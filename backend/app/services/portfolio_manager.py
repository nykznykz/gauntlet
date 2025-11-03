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
        """Allocate margin for a new position (reserves margin without deducting from cash)"""
        # Model 1: Reserve margin - cash stays in account, margin is reserved
        # Cash balance remains unchanged
        # NOTE: Don't manually adjust margin_used here - update_portfolio will
        # recalculate it from all positions
        # margin_available will be recalculated in update_portfolio as (equity - margin_used)

        # No need to commit here, just let update_portfolio handle it
        return self.update_portfolio(portfolio)

    def release_margin(
        self,
        portfolio: Portfolio,
        margin_amount: Decimal,
        realized_pnl: Decimal
    ) -> Portfolio:
        """Release margin from a closed position"""
        # Model 1: Margin was never deducted from cash, so only add realized P&L
        portfolio.cash_balance += realized_pnl
        # NOTE: Don't manually adjust margin_used here - update_portfolio will
        # recalculate it from all remaining positions (the closed position has been deleted)
        # This prevents double-subtraction of margin
        portfolio.realized_pnl += realized_pnl

        self.db.add(portfolio)
        # Don't commit here - let caller handle transaction atomicity

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

    def check_and_liquidate(
        self,
        participant: Participant,
        portfolio: Portfolio,
        competition: "Competition"
    ) -> bool:
        """
        Check if participant should be liquidated and liquidate if necessary.

        Returns:
            True if participant was liquidated, False otherwise
        """
        from app.utils.calculations import check_liquidation

        # Skip if already liquidated or not active
        if participant.status != "active":
            return False

        # Skip check if no margin used (no positions)
        if portfolio.margin_used <= 0:
            return False

        # Calculate margin level
        if portfolio.margin_used > 0:
            margin_level = (portfolio.equity / portfolio.margin_used) * Decimal("100")
        else:
            return False

        # Calculate liquidation threshold
        initial_margin_pct = Decimal("100") / competition.max_leverage
        should_liquidate = check_liquidation(
            margin_level,
            competition.maintenance_margin_pct,
            initial_margin_pct
        )

        if not should_liquidate:
            return False

        # Liquidate all positions
        positions = list(
            self.db.execute(
                select(Position).where(Position.portfolio_id == portfolio.id)
            )
            .scalars()
            .all()
        )

        if not positions:
            return False

        # Import here to avoid circular dependency
        from app.services.cfd_engine import CFDEngine
        from app.services.market_data_service import market_data_service

        cfd_engine = CFDEngine(self.db)
        total_realized_pnl = Decimal("0")
        total_margin_released = Decimal("0")

        # Close all positions
        for position in positions:
            try:
                # Get current price
                current_price = market_data_service.get_price(position.symbol, position.asset_class)
                if not current_price:
                    continue

                # Close position
                close_result = cfd_engine.close_position(position, current_price)
                total_realized_pnl += close_result["realized_pnl"]
                total_margin_released += close_result["margin_released"]

            except Exception as e:
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error closing position {position.id} during liquidation: {e}")

        # Update portfolio with realized P&L
        portfolio.cash_balance += total_realized_pnl
        portfolio.realized_pnl += total_realized_pnl
        self.db.add(portfolio)

        # Update portfolio metrics (will recalculate margin_used from remaining positions)
        self.update_portfolio(portfolio)

        # Mark participant as liquidated
        participant.status = "liquidated"
        self.db.add(participant)
        self.db.commit()

        return True
