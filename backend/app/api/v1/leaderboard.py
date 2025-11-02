"""Leaderboard API endpoints"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from pydantic import BaseModel
from decimal import Decimal
from app.db.session import get_db
from app.models.participant import Participant
from app.models.competition import Competition
from app.utils.calculations import calculate_win_rate

router = APIRouter(prefix="/leaderboard", tags=["leaderboard"])


class LeaderboardEntry(BaseModel):
    rank: int
    participant_id: UUID
    name: str
    equity: Decimal
    total_pnl: Decimal
    total_pnl_pct: Decimal
    total_trades: int
    win_rate: Decimal
    status: str


class LeaderboardResponse(BaseModel):
    leaderboard: List[LeaderboardEntry]


@router.get("/competitions/{competition_id}/leaderboard", response_model=LeaderboardResponse)
def get_competition_leaderboard(
    competition_id: UUID,
    metric: str = "equity",
    limit: int = 10,
    db: Session = Depends(get_db)
):
    """Get competition leaderboard"""
    # Verify competition exists
    competition = db.query(Competition).filter(Competition.id == competition_id).first()
    if not competition:
        raise HTTPException(status_code=404, detail="Competition not found")

    # Get participants ordered by selected metric
    if metric == "equity":
        participants = (
            db.query(Participant)
            .filter(Participant.competition_id == competition_id)
            .order_by(Participant.current_equity.desc())
            .limit(limit)
            .all()
        )
    else:
        # Default to equity
        participants = (
            db.query(Participant)
            .filter(Participant.competition_id == competition_id)
            .order_by(Participant.current_equity.desc())
            .limit(limit)
            .all()
        )

    # Build leaderboard
    leaderboard = []
    for rank, p in enumerate(participants, 1):
        total_pnl = p.current_equity - p.initial_capital
        total_pnl_pct = (total_pnl / p.initial_capital * 100) if p.initial_capital > 0 else Decimal("0")
        win_rate = calculate_win_rate(p.winning_trades, p.total_trades)

        leaderboard.append(
            LeaderboardEntry(
                rank=rank,
                participant_id=p.id,
                name=p.name,
                equity=p.current_equity,
                total_pnl=total_pnl,
                total_pnl_pct=total_pnl_pct,
                total_trades=p.total_trades,
                win_rate=win_rate,
                status=p.status,
            )
        )

    return {"leaderboard": leaderboard}
