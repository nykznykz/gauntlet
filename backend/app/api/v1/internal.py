"""Internal/Admin API endpoints"""
from fastapi import APIRouter, Depends, BackgroundTasks, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from pydantic import BaseModel
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from app.api.dependencies import get_db_session
from app.models.participant import Participant
from app.models.competition import Competition
from app.models.portfolio import Portfolio
from app.models.portfolio_history import PortfolioHistory
from app.models.position import Position
from app.models.trade import Trade
from app.models.llm_invocation import LLMInvocation
from app.services.llm_invoker import LLMInvoker

router = APIRouter(prefix="/internal", tags=["internal"])


class InvokeParticipantsRequest(BaseModel):
    competition_id: UUID


class InvokeParticipantsResponse(BaseModel):
    invocations_triggered: int
    participants: List[UUID]


@router.post("/invoke-participants", response_model=InvokeParticipantsResponse)
def invoke_participants(
    request: InvokeParticipantsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """Trigger LLM invocations for all active participants in a competition"""

    # Get all active participants in the competition
    participants = (
        db.query(Participant)
        .filter(
            Participant.competition_id == request.competition_id,
            Participant.status == "active"
        )
        .all()
    )

    participant_ids = [p.id for p in participants]

    # Invoke each participant in the background
    for participant_id in participant_ids:
        background_tasks.add_task(_invoke_participant_task, participant_id)

    return {
        "invocations_triggered": len(participant_ids),
        "participants": participant_ids,
    }


def _invoke_participant_task(participant_id: UUID):
    """Background task to invoke a participant"""
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        invoker = LLMInvoker(db)
        invoker.invoke_participant(participant_id)
    finally:
        db.close()


@router.post("/trigger-invocation/{participant_id}")
def trigger_single_invocation(
    participant_id: UUID,
    db: Session = Depends(get_db_session)
):
    """Manually trigger a single LLM invocation (for testing)"""
    invoker = LLMInvoker(db)
    invocation = invoker.invoke_participant(participant_id)

    if invocation:
        return {
            "invocation_id": invocation.id,
            "status": invocation.status,
            "response_time_ms": invocation.response_time_ms,
        }
    else:
        return {"error": "Failed to invoke participant"}


# Competition configuration for reset
COMPETITION_CONFIG = {
    "name": "LLM Trading Competition - Battle Royale",
    "description": "A competitive trading simulation where different LLM agents compete to maximize returns using CFD trading strategies.",
    "initial_capital": Decimal("10000.00"),
    "max_leverage": Decimal("40.0"),
    "maintenance_margin_pct": Decimal("1.25"),
    "allowed_asset_classes": ["crypto"],
    "max_participants": 20,
    "invocation_interval_minutes": 5,
    "market_hours_only": False,
    "duration_days": 7,
}

PARTICIPANTS_CONFIG = [
    {
        "name": "claude-sonnet-4.5",
        "llm_provider": "anthropic",
        "llm_model": "claude-3-5-sonnet-20250110",
        "llm_config": {
            "temperature": 0.7,
            "max_tokens": 2000,
        }
    },
    {
        "name": "gpt4o",
        "llm_provider": "azure_openai",
        "llm_model": "gpt-4o",
        "llm_config": {
            "model": "gpt-4o",
            "temperature": 0.7,
            "max_tokens": 2000,
        }
    },
    {
        "name": "gpt4o-mini",
        "llm_provider": "azure_openai",
        "llm_model": "gpt-4o-mini",
        "llm_config": {
            "model": "gpt-4o-mini",
            "temperature": 0.7,
            "max_tokens": 2000,
        }
    },
    {
        "name": "deepseek-chat",
        "llm_provider": "deepseek",
        "llm_model": "deepseek-chat",
        "llm_config": {
            "temperature": 0.7,
            "max_tokens": 8000,
        }
    },
]


class ResetCompetitionResponse(BaseModel):
    success: bool
    message: str
    deleted_records: dict
    new_competition_id: UUID
    participants_created: int


@router.post("/reset-competition", response_model=ResetCompetitionResponse)
def reset_competition(db: Session = Depends(get_db_session)):
    """
    Reset the competition: delete all data and recreate fresh competition
    WARNING: This deletes ALL competition data!
    """
    try:
        # Step 1: Delete all existing data
        deleted_counts = {}

        # Delete in correct order to respect foreign key constraints
        deleted_counts['invocations'] = db.query(LLMInvocation).delete()
        deleted_counts['portfolio_history'] = db.query(PortfolioHistory).delete()
        deleted_counts['trades'] = db.query(Trade).delete()
        deleted_counts['positions'] = db.query(Position).delete()
        deleted_counts['portfolios'] = db.query(Portfolio).delete()
        deleted_counts['participants'] = db.query(Participant).delete()
        deleted_counts['competitions'] = db.query(Competition).delete()

        db.commit()

        # Step 2: Create new competition
        now = datetime.now(timezone.utc)
        config = COMPETITION_CONFIG

        competition = Competition(
            name=config["name"],
            description=config["description"],
            status="active",
            start_time=now,
            end_time=now + timedelta(days=config["duration_days"]),
            initial_capital=config["initial_capital"],
            max_leverage=config["max_leverage"],
            maintenance_margin_pct=config["maintenance_margin_pct"],
            allowed_asset_classes=config["allowed_asset_classes"],
            max_participants=config["max_participants"],
            invocation_interval_minutes=config["invocation_interval_minutes"],
            market_hours_only=config["market_hours_only"],
        )

        db.add(competition)
        db.commit()
        db.refresh(competition)

        # Step 3: Create participants
        participants = []
        for p_config in PARTICIPANTS_CONFIG:
            participant = Participant(
                competition_id=competition.id,
                name=p_config["name"],
                llm_provider=p_config["llm_provider"],
                llm_model=p_config["llm_model"],
                llm_config=p_config["llm_config"],
                initial_capital=competition.initial_capital,
                current_equity=competition.initial_capital,
                peak_equity=competition.initial_capital,
                status="active",
                total_trades=0,
                winning_trades=0,
                losing_trades=0,
            )

            db.add(participant)
            db.flush()

            # Create portfolio
            portfolio = Portfolio(
                participant_id=participant.id,
                cash_balance=competition.initial_capital,
                equity=competition.initial_capital,
                margin_used=Decimal("0.0"),
                margin_available=competition.initial_capital,
                unrealized_pnl=Decimal("0.0"),
                realized_pnl=Decimal("0.0"),
                total_pnl=Decimal("0.0"),
            )

            db.add(portfolio)

            # Initial history entry
            history = PortfolioHistory(
                participant_id=participant.id,
                equity=competition.initial_capital,
                cash_balance=competition.initial_capital,
                margin_used=Decimal("0.0"),
                realized_pnl=Decimal("0.0"),
                unrealized_pnl=Decimal("0.0"),
                total_pnl=Decimal("0.0"),
            )

            db.add(history)
            participants.append(participant)

        db.commit()

        return ResetCompetitionResponse(
            success=True,
            message="Competition reset successfully",
            deleted_records=deleted_counts,
            new_competition_id=competition.id,
            participants_created=len(participants)
        )

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to reset competition: {str(e)}")
