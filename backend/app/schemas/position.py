"""Position schemas"""
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import List


class PositionResponse(BaseModel):
    """Schema for position response"""
    id: UUID
    symbol: str
    asset_class: str
    side: str
    quantity: Decimal
    entry_price: Decimal
    current_price: Decimal
    leverage: Decimal
    margin_required: Decimal
    notional_value: Decimal
    unrealized_pnl: Decimal
    unrealized_pnl_pct: Decimal
    opened_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PositionList(BaseModel):
    """Schema for position list response"""
    positions: List[PositionResponse]
