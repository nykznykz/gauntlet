"""Portfolio schemas"""
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import Optional


class PortfolioResponse(BaseModel):
    """Schema for portfolio response"""
    id: UUID
    participant_id: UUID
    cash_balance: Decimal
    equity: Decimal
    margin_used: Decimal
    margin_available: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    total_pnl: Decimal
    current_leverage: Decimal
    margin_level: Optional[Decimal] = None
    updated_at: datetime

    class Config:
        from_attributes = True
