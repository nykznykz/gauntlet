"""Trading engine for order execution"""
from decimal import Decimal
from typing import Optional, Tuple
from sqlalchemy.orm import Session
from uuid import UUID
from app.models.order import Order
from app.models.trade import Trade
from app.models.participant import Participant
from app.models.portfolio import Portfolio
from app.models.position import Position
from app.models.competition import Competition
from app.services.cfd_engine import CFDEngine
from app.services.portfolio_manager import PortfolioManager
from app.services.market_data_service import market_data_service
from app.utils.calculations import calculate_notional_value, calculate_margin_required


class TradingEngine:
    """Engine for order validation and execution"""

    def __init__(self, db: Session):
        self.db = db
        self.cfd_engine = CFDEngine(db)
        self.portfolio_manager = PortfolioManager(db)

    def validate_order(
        self,
        participant: Participant,
        competition: Competition,
        portfolio: Portfolio,
        symbol: str,
        side: str,
        quantity: Decimal,
        leverage: Decimal,
        action: str,
        position_id: Optional[UUID] = None
    ) -> Tuple[bool, Optional[str]]:
        """Validate an order before execution"""

        # Check participant status
        if participant.status != "active":
            return False, f"Participant is {participant.status}"

        # Check leverage limit
        if leverage > competition.max_leverage:
            return False, f"Leverage {leverage} exceeds max {competition.max_leverage}"

        # For opening new positions, check margin and position size
        if action == "open":
            # Get current price
            price = market_data_service.get_price(symbol, "crypto")
            if price is None:
                return False, f"Could not fetch price for {symbol}"

            # Calculate required margin
            notional_value = calculate_notional_value(quantity, price)
            margin_required = calculate_margin_required(notional_value, leverage)

            # Check margin available
            if margin_required > portfolio.margin_available:
                return False, f"Insufficient margin. Required: {margin_required}, Available: {portfolio.margin_available}"

        # For closing/modifying positions, check position exists
        elif action in ["close", "increase", "decrease"]:
            if position_id is None:
                return False, "Position ID required for close/increase/decrease"

            position = self.db.query(Position).filter(Position.id == position_id).first()
            if not position:
                return False, f"Position {position_id} not found"

            if position.participant_id != participant.id:
                return False, "Position does not belong to this participant"

        return True, None

    def execute_order(
        self,
        order: Order,
        action: str,
        position_id: Optional[UUID] = None,
        exit_plan: Optional[dict] = None
    ) -> Optional[Trade]:
        """Execute an order and create a trade"""

        participant = self.db.query(Participant).filter(Participant.id == order.participant_id).first()
        portfolio = self.db.query(Portfolio).filter(Portfolio.participant_id == order.participant_id).first()
        competition = self.db.query(Competition).filter(Competition.id == order.competition_id).first()

        # Get current market price
        execution_price = market_data_service.get_price(order.symbol, order.asset_class)
        if execution_price is None:
            order.status = "rejected"
            order.rejection_reason = "Could not fetch market price"
            self.db.add(order)
            self.db.commit()
            return None

        order.executed_price = execution_price

        # Execute based on action
        if action == "open":
            return self._execute_open(order, participant, portfolio, competition, execution_price, exit_plan)
        elif action == "close":
            return self._execute_close(order, participant, portfolio, execution_price, position_id)
        else:
            order.status = "rejected"
            order.rejection_reason = f"Action {action} not yet implemented"
            self.db.add(order)
            self.db.commit()
            return None

    def _execute_open(
        self,
        order: Order,
        participant: Participant,
        portfolio: Portfolio,
        competition: Competition,
        price: Decimal,
        exit_plan: Optional[dict] = None
    ) -> Trade:
        """Execute opening a new position"""

        # Determine position side from order side
        position_side = "long" if order.side == "buy" else "short"

        # Calculate metrics
        notional_value = calculate_notional_value(order.quantity, price)
        margin_required = calculate_margin_required(notional_value, order.leverage)

        # Allocate margin
        self.portfolio_manager.allocate_margin(portfolio, margin_required)

        # Open position with exit plan
        position = self.cfd_engine.open_position(
            portfolio=portfolio,
            symbol=order.symbol,
            asset_class=order.asset_class,
            side=position_side,
            quantity=order.quantity,
            entry_price=price,
            leverage=order.leverage,
            exit_plan=exit_plan,
        )

        # Create trade record
        trade = Trade(
            order_id=order.id,
            participant_id=participant.id,
            position_id=position.id,
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=price,
            action="open",
            leverage=order.leverage,
            notional_value=notional_value,
            margin_impact=margin_required,
            realized_pnl=None,
            realized_pnl_pct=None,
        )

        order.status = "executed"
        self.db.add(order)
        self.db.add(trade)
        self.db.commit()
        self.db.refresh(trade)

        # Update portfolio and participant equity
        portfolio = self.portfolio_manager.update_portfolio(portfolio)
        self.portfolio_manager.update_participant_equity(participant, portfolio.equity)

        return trade

    def _execute_close(
        self,
        order: Order,
        participant: Participant,
        portfolio: Portfolio,
        price: Decimal,
        position_id: Optional[UUID] = None
    ) -> Trade:
        """Execute closing a position"""

        # Find the position - use position_id if provided (preferred), otherwise fall back to symbol
        if position_id:
            position = self.db.query(Position).filter(Position.id == position_id).first()
        else:
            # Fallback: Find by symbol (less reliable if multiple positions exist)
            position = self.db.query(Position).filter(
                Position.participant_id == participant.id,
                Position.symbol == order.symbol
            ).first()

        if not position:
            order.status = "rejected"
            order.rejection_reason = "Position not found"
            self.db.add(order)
            self.db.commit()
            return None

        # Close position and get realized P&L
        close_result = self.cfd_engine.close_position(position, price)

        # Release margin and add realized P&L to cash
        self.portfolio_manager.release_margin(
            portfolio,
            close_result["margin_released"],
            close_result["realized_pnl"]
        )

        # Calculate notional and margin impact
        notional_value = calculate_notional_value(order.quantity, price)

        # Create trade record
        # Note: position_id is set to None because the position is being deleted in this transaction
        # The FK constraint has ondelete="SET NULL" so this avoids FK constraint violations
        trade = Trade(
            order_id=order.id,
            participant_id=participant.id,
            position_id=None,  # Position is being deleted, so don't reference it
            symbol=order.symbol,
            side=order.side,
            quantity=order.quantity,
            price=price,
            action="close",
            leverage=position.leverage,
            notional_value=notional_value,
            margin_impact=-close_result["margin_released"],  # Negative because margin is released
            realized_pnl=close_result["realized_pnl"],
            realized_pnl_pct=close_result["realized_pnl_pct"],
        )

        order.status = "executed"
        self.db.add(order)
        self.db.add(trade)

        # Update participant stats
        participant.total_trades += 1
        if close_result["realized_pnl"] > Decimal("0"):
            participant.winning_trades += 1
        elif close_result["realized_pnl"] < Decimal("0"):
            participant.losing_trades += 1
        # else: breakeven trades (PnL == 0) don't count as wins or losses

        self.db.add(participant)
        self.db.commit()
        self.db.refresh(trade)

        # Update portfolio and participant equity
        portfolio = self.portfolio_manager.update_portfolio(portfolio)
        self.portfolio_manager.update_participant_equity(participant, portfolio.equity)

        return trade
