"""Order schemas"""
from pydantic import BaseModel
from decimal import Decimal
from typing import Optional
from uuid import UUID


class OrderCreate(BaseModel):
    """Schema for creating an order from LLM response"""
    action: str  # open, close, increase, decrease
    symbol: str
    side: str  # buy, sell
    quantity: Decimal
    leverage: Decimal = Decimal("1.0")
    position_id: Optional[UUID] = None  # Required for close/increase/decrease
