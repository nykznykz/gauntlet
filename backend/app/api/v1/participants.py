"""Participant API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from app.api.dependencies import verify_api_key
from app.db.session import get_db
from app.models.participant import Participant
from app.models.competition import Competition
from app.models.portfolio import Portfolio
from app.models.position import Position
from app.models.trade import Trade
from app.models.portfolio_history import PortfolioHistory
from app.models.llm_invocation import LLMInvocation
from app.schemas.participant import ParticipantCreate, ParticipantResponse, ParticipantPerformance
from app.schemas.portfolio import PortfolioResponse
from app.schemas.position import PositionList, PositionResponse
from app.schemas.trade import TradeList, TradeResponse
from app.schemas.portfolio_history import PortfolioHistoryResponse, PortfolioHistoryPoint
from app.schemas.llm_invocation import LLMInvocationResponse, LLMInvocationList
from app.services.portfolio_manager import PortfolioManager
from app.utils.calculations import calculate_win_rate

router = APIRouter(prefix="/participants", tags=["participants"])


@router.post("/competitions/{competition_id}/participants", response_model=ParticipantResponse, status_code=201)
def create_participant(
    competition_id: UUID,
    participant_data: ParticipantCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Register a participant in a competition"""
    # Verify competition exists
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    # Check if competition is full
    participant_count = db.query(Participant).filter(Participant.competition_id == competition_id).count()
    if participant_count >= competition.max_participants:
        raise HTTPException(status_code=400, detail="Competition is full")

    # Create participant
    participant = Participant(
        competition_id=competition_id,
        name=participant_data.name,
        llm_provider=participant_data.llm_provider,
        llm_model=participant_data.llm_model,
        llm_config=participant_data.llm_config,
        endpoint_url=participant_data.endpoint_url,
        timeout_seconds=participant_data.timeout_seconds,
        initial_capital=competition.initial_capital,
        current_equity=competition.initial_capital,
        peak_equity=competition.initial_capital,
        status="active",
    )

    db.add(participant)
    db.commit()
    db.refresh(participant)

    # Create portfolio
    portfolio_manager = PortfolioManager(db)
    portfolio_manager.create_portfolio(participant.id, competition.initial_capital)

    return participant


@router.get("/{participant_id}", response_model=ParticipantResponse)
def get_participant(
    participant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get participant details"""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    return participant


@router.get("/{participant_id}/portfolio", response_model=PortfolioResponse)
def get_participant_portfolio(
    participant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get participant's portfolio"""
    portfolio = db.query(Portfolio).filter(Portfolio.participant_id == participant_id).first()

    if not portfolio:
        raise HTTPException(status_code=404, detail="Portfolio not found")

    return portfolio


@router.get("/{participant_id}/positions", response_model=PositionList)
def get_participant_positions(
    participant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get participant's current positions"""
    positions = db.query(Position).filter(Position.participant_id == participant_id).all()

    return {"positions": positions}


@router.get("/{participant_id}/trades", response_model=TradeList)
def get_participant_trades(
    participant_id: UUID,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Get participant's trade history"""
    query = db.query(Trade).filter(Trade.participant_id == participant_id).order_by(Trade.executed_at.desc())

    total = query.count()
    trades = query.offset(offset).limit(limit).all()

    return {
        "trades": trades,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{participant_id}/performance", response_model=ParticipantPerformance)
def get_participant_performance(
    participant_id: UUID,
    db: Session = Depends(get_db)
):
    """Get participant's performance metrics"""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    total_pnl = participant.current_equity - participant.initial_capital
    total_pnl_pct = (total_pnl / participant.initial_capital) * 100 if participant.initial_capital > 0 else 0
    win_rate = calculate_win_rate(participant.winning_trades, participant.total_trades)

    return {
        "initial_capital": participant.initial_capital,
        "current_equity": participant.current_equity,
        "peak_equity": participant.peak_equity,
        "total_pnl": total_pnl,
        "total_pnl_pct": total_pnl_pct,
        "total_trades": participant.total_trades,
        "winning_trades": participant.winning_trades,
        "losing_trades": participant.losing_trades,
        "win_rate": win_rate,
    }


@router.get("/{participant_id}/history", response_model=PortfolioHistoryResponse)
def get_participant_history(
    participant_id: UUID,
    limit: int = 500,
    db: Session = Depends(get_db)
):
    """Get participant's portfolio history for equity curve"""
    participant = db.query(Participant).filter(Participant.id == participant_id).first()

    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    # Get portfolio history ordered by time
    history = (
        db.query(PortfolioHistory)
        .filter(PortfolioHistory.participant_id == participant_id)
        .order_by(PortfolioHistory.recorded_at.asc())
        .limit(limit)
        .all()
    )

    return {
        "participant_id": participant.id,
        "participant_name": participant.name,
        "history": history
    }


@router.get("/competitions/{competition_id}/all", response_model=List[ParticipantResponse])
def list_competition_participants(
    competition_id: UUID,
    db: Session = Depends(get_db)
):
    """List all participants in a competition"""
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    participants = (
        db.query(Participant)
        .filter(Participant.competition_id == competition_id)
        .all()
    )

    return participants


@router.get("/{participant_id}/invocations", response_model=LLMInvocationList)
def get_participant_invocations(
    participant_id: UUID,
    limit: int = 50,
    offset: int = 0,
    status: str = None,
    db: Session = Depends(get_db)
):
    """Get participant's LLM invocation logs with optional status filtering"""
    # Verify participant exists
    participant = db.query(Participant).filter(Participant.id == participant_id).first()
    if not participant:
        raise HTTPException(status_code=404, detail="Participant not found")

    # Build query
    query = db.query(LLMInvocation).filter(LLMInvocation.participant_id == participant_id)

    # Apply status filter if provided
    if status:
        query = query.filter(LLMInvocation.status == status)

    # Order by most recent first
    query = query.order_by(LLMInvocation.invocation_time.desc())

    total = query.count()
    invocations = query.offset(offset).limit(limit).all()

    return {
        "invocations": invocations,
        "total": total,
        "limit": limit,
        "offset": offset,
    }
