"""Trade schemas"""
from pydantic import BaseModel, Field
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
    pnl: Optional[Decimal] = Field(default=None, alias="realized_pnl", serialization_alias="pnl")
    realized_pnl_pct: Optional[Decimal] = None
    timestamp: datetime = Field(alias="executed_at", serialization_alias="timestamp")
    llm_reasoning: Optional[str] = None
    participant_id: UUID

    class Config:
        from_attributes = True
        populate_by_name = True


class TradeList(BaseModel):
    """Schema for trade list response"""
    trades: List[TradeResponse]
    total: int
    limit: int
    offset: int
