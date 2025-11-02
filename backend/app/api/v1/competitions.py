"""Competition API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from uuid import UUID
from app.api.dependencies import verify_api_key
from app.db.session import get_db
from app.models.competition import Competition
from app.models.participant import Participant
from app.models.portfolio_history import PortfolioHistory
from app.schemas.competition import CompetitionCreate, CompetitionResponse, CompetitionList
from app.schemas.portfolio_history import MultiParticipantHistoryResponse, PortfolioHistoryResponse

router = APIRouter(prefix="/competitions", tags=["competitions"])


@router.post("", response_model=CompetitionResponse, status_code=201)
def create_competition(
    competition_data: CompetitionCreate,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Create a new competition"""
    competition = Competition(**competition_data.model_dump())
    competition.status = "pending"

    db.add(competition)
    db.commit()
    db.refresh(competition)

    return competition


@router.get("", response_model=CompetitionList)
def list_competitions(
    status: Optional[str] = None,
    limit: int = 20,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List all competitions"""
    query = db.query(Competition)

    if status:
        query = query.filter(Competition.status == status)

    total = query.count()
    competitions = query.offset(offset).limit(limit).all()

    return {
        "competitions": competitions,
        "total": total,
        "limit": limit,
        "offset": offset,
    }


@router.get("/{competition_id}", response_model=CompetitionResponse)
def get_competition(
    competition_id: UUID,
    db: Session = Depends(get_db)
):
    """Get competition details"""
    competition = db.query(Competition).filter(Competition.id == competition_id).first()

    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    return competition


@router.post("/{competition_id}/start")
def start_competition(
    competition_id: UUID,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Start a competition"""
    competition = db.query(Competition).filter(Competition.id == competition_id).first()

    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    if competition.status != "pending":
        raise HTTPException(status_code=400, detail=f"Cannot start competition with status {competition.status}")

    competition.status = "active"
    db.add(competition)
    db.commit()
    db.refresh(competition)

    return {"id": competition.id, "status": competition.status}


@router.post("/{competition_id}/stop")
def stop_competition(
    competition_id: UUID,
    db: Session = Depends(get_db),
    api_key: str = Depends(verify_api_key)
):
    """Stop a competition"""
    competition = db.query(Competition).filter(Competition.id == competition_id).first()

    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    if competition.status != "active":
        raise HTTPException(status_code=400, detail=f"Cannot stop competition with status {competition.status}")

    competition.status = "completed"
    db.add(competition)
    db.commit()
    db.refresh(competition)

    return {"id": competition.id, "status": competition.status}


@router.get("/{competition_id}/history", response_model=MultiParticipantHistoryResponse)
def get_competition_history(
    competition_id: UUID,
    limit_per_participant: int = 500,
    db: Session = Depends(get_db)
):
    """Get portfolio history for all participants in a competition (for multi-trader equity chart)"""
    competition = db.query(Competition).filter(Competition.id == competition_id).first()

    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    # Get all participants in the competition
    participants = (
        db.query(Participant)
        .filter(Participant.competition_id == competition_id)
        .all()
    )

    # Get history for each participant
    participants_history = []
    for participant in participants:
        history = (
            db.query(PortfolioHistory)
            .filter(PortfolioHistory.participant_id == participant.id)
            .order_by(PortfolioHistory.recorded_at.asc())
            .limit(limit_per_participant)
            .all()
        )

        participants_history.append({
            "participant_id": participant.id,
            "participant_name": participant.name,
            "history": history
        })

    return {"participants": participants_history}
