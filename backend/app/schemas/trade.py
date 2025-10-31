"""Trade schemas"""
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import List, Optional


class TradeResponse(BaseModel):
    """Schema for trade response"""
    id: UUID
    symbol: str
    side: str
    quantity: Decimal
    price: Decimal
    action: str
    leverage: Decimal
    notional_value: Decimal
    margin_impact: Decimal
    realized_pnl: Optional[Decimal] = None
    realized_pnl_pct: Optional[Decimal] = None
    executed_at: datetime

    class Config:
        from_attributes = True


class TradeList(BaseModel):
    """Schema for trade list response"""
    trades: List[TradeResponse]
    total: int
    limit: int
    offset: int
