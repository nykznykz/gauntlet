"""CFD Engine for position management"""
from decimal import Decimal
from typing import Literal
from sqlalchemy.orm import Session
from app.models.position import Position
from app.models.portfolio import Portfolio
from app.utils.calculations import (
    calculate_notional_value,
    calculate_margin_required,
    calculate_unrealized_pnl,
    calculate_pnl_percentage,
)


class CFDEngine:
    """Engine for CFD position calculations and management"""

    def __init__(self, db: Session):
        self.db = db

    def calculate_position_metrics(
        self,
        side: Literal["long", "short"],
        quantity: Decimal,
        entry_price: Decimal,
        current_price: Decimal,
        leverage: Decimal,
    ) -> dict:
        """Calculate all metrics for a position"""
        notional_value = calculate_notional_value(quantity, current_price)
        margin_required = calculate_margin_required(
            calculate_notional_value(quantity, entry_price),
            leverage
        )
        unrealized_pnl = calculate_unrealized_pnl(
            side, quantity, entry_price, current_price
        )
        entry_value = calculate_notional_value(quantity, entry_price)
        unrealized_pnl_pct = calculate_pnl_percentage(unrealized_pnl, entry_value)

        return {
            "notional_value": notional_value,
            "margin_required": margin_required,
            "unrealized_pnl": unrealized_pnl,
            "unrealized_pnl_pct": unrealized_pnl_pct,
        }

    def update_position_price(
        self,
        position: Position,
        new_price: Decimal
    ) -> Position:
        """Update position with new market price"""
        metrics = self.calculate_position_metrics(
            side=position.side,
            quantity=position.quantity,
            entry_price=position.entry_price,
            current_price=new_price,
            leverage=position.leverage,
        )

        position.current_price = new_price
        position.notional_value = metrics["notional_value"]
        position.unrealized_pnl = metrics["unrealized_pnl"]
        position.unrealized_pnl_pct = metrics["unrealized_pnl_pct"]

        self.db.add(position)
        self.db.commit()
        self.db.refresh(position)

        return position

    def close_position(
        self,
        position: Position,
        closing_price: Decimal
    ) -> dict:
        """Close a position and calculate realized P&L"""
        # Update position with final price (but don't commit yet)
        metrics = self.calculate_position_metrics(
            side=position.side,
            quantity=position.quantity,
            entry_price=position.entry_price,
            current_price=closing_price,
            leverage=position.leverage,
        )

        position.current_price = closing_price
        position.notional_value = metrics["notional_value"]
        position.unrealized_pnl = metrics["unrealized_pnl"]
        position.unrealized_pnl_pct = metrics["unrealized_pnl_pct"]

        realized_pnl = position.unrealized_pnl
        realized_pnl_pct = position.unrealized_pnl_pct
        margin_released = position.margin_required

        # Delete position (but don't commit - let caller handle transaction)
        self.db.delete(position)

        return {
            "realized_pnl": realized_pnl,
            "realized_pnl_pct": realized_pnl_pct,
            "margin_released": margin_released,
        }

    def open_position(
        self,
        portfolio: Portfolio,
        symbol: str,
        asset_class: str,
        side: Literal["long", "short"],
        quantity: Decimal,
        entry_price: Decimal,
        leverage: Decimal,
    ) -> Position:
        """Open a new CFD position"""
        metrics = self.calculate_position_metrics(
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            leverage=leverage,
        )

        position = Position(
            portfolio_id=portfolio.id,
            participant_id=portfolio.participant_id,
            symbol=symbol,
            asset_class=asset_class,
            side=side,
            quantity=quantity,
            entry_price=entry_price,
            current_price=entry_price,
            leverage=leverage,
            margin_required=metrics["margin_required"],
            notional_value=metrics["notional_value"],
            unrealized_pnl=Decimal("0"),
            unrealized_pnl_pct=Decimal("0"),
        )

        self.db.add(position)
        self.db.commit()
        self.db.refresh(position)

        return position
