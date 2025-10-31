"""Portfolio Manager for P&L and equity calculations"""
from decimal import Decimal
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import select
from app.models.portfolio import Portfolio
from app.models.position import Position
from app.models.participant import Participant
from app.models.portfolio_history import PortfolioHistory
from app.utils.calculations import (
    calculate_equity,
    calculate_margin_level,
    calculate_current_leverage,
)


class PortfolioManager:
    """Manager for portfolio calculations and updates"""

    def __init__(self, db: Session):
        self.db = db

    def create_portfolio(
        self,
        participant_id: str,
        initial_capital: Decimal
    ) -> Portfolio:
        """Create initial portfolio for a participant"""
        portfolio = Portfolio(
            participant_id=participant_id,
            cash_balance=initial_capital,
            equity=initial_capital,
            margin_used=Decimal("0"),
            margin_available=initial_capital,
            realized_pnl=Decimal("0"),
            unrealized_pnl=Decimal("0"),
            total_pnl=Decimal("0"),
            current_leverage=Decimal("0"),
            margin_level=None,
        )

        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)

        # Record initial portfolio history
        self.record_portfolio_history(portfolio)

        return portfolio

    def update_portfolio(self, portfolio: Portfolio) -> Portfolio:
        """Recalculate all portfolio metrics"""
        # Get all positions
        positions: List[Position] = (
            self.db.execute(
                select(Position).where(Position.portfolio_id == portfolio.id)
            )
            .scalars()
            .all()
        )

        # Calculate aggregated metrics
        total_margin_used = sum(p.margin_required for p in positions)
        total_unrealized_pnl = sum(p.unrealized_pnl for p in positions)
        total_notional_value = sum(p.notional_value for p in positions)

        # Calculate equity
        equity = calculate_equity(portfolio.cash_balance, total_unrealized_pnl)

        # Calculate margin available
        margin_available = equity - total_margin_used

        # Calculate total P&L
        total_pnl = portfolio.realized_pnl + total_unrealized_pnl

        # Calculate margin level
        if total_margin_used > 0:
            margin_level = calculate_margin_level(equity, total_margin_used)
        else:
            margin_level = None

        # Calculate current leverage
        current_leverage = calculate_current_leverage(total_notional_value, equity)

        # Update portfolio
        portfolio.equity = equity
        portfolio.margin_used = total_margin_used
        portfolio.margin_available = margin_available
        portfolio.unrealized_pnl = total_unrealized_pnl
        portfolio.total_pnl = total_pnl
        portfolio.margin_level = margin_level
        portfolio.current_leverage = current_leverage

        self.db.add(portfolio)
        self.db.commit()
        self.db.refresh(portfolio)

        # Record portfolio history snapshot
        self.record_portfolio_history(portfolio)

        return portfolio

    def record_portfolio_history(self, portfolio: Portfolio) -> None:
        """Record a snapshot of the portfolio state"""
        history_entry = PortfolioHistory(
            participant_id=portfolio.participant_id,
            equity=portfolio.equity,
            cash_balance=portfolio.cash_balance,
            margin_used=portfolio.margin_used,
            realized_pnl=portfolio.realized_pnl,
            unrealized_pnl=portfolio.unrealized_pnl,
            total_pnl=portfolio.total_pnl,
        )
        self.db.add(history_entry)
        self.db.commit()

    def allocate_margin(
        self,
        portfolio: Portfolio,
        margin_amount: Decimal
    ) -> Portfolio:
        """Allocate margin for a new position"""
        portfolio.cash_balance -= margin_amount
        portfolio.margin_used += margin_amount
        portfolio.margin_available -= margin_amount

        self.db.add(portfolio)
        self.db.commit()

        return self.update_portfolio(portfolio)

    def release_margin(
        self,
        portfolio: Portfolio,
        margin_amount: Decimal,
        realized_pnl: Decimal
    ) -> Portfolio:
        """Release margin from a closed position"""
        # Return margin + realized P&L to cash balance
        portfolio.cash_balance += (margin_amount + realized_pnl)
        portfolio.margin_used -= margin_amount
        portfolio.realized_pnl += realized_pnl

        self.db.add(portfolio)
        self.db.commit()

        return self.update_portfolio(portfolio)

    def update_participant_equity(
        self,
        participant: Participant,
        new_equity: Decimal
    ) -> Participant:
        """Update participant's current equity and peak equity"""
        participant.current_equity = new_equity

        if new_equity > participant.peak_equity:
            participant.peak_equity = new_equity

        self.db.add(participant)
        self.db.commit()
        self.db.refresh(participant)

        return participant
