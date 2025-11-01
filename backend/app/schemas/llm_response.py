"""LLM response schemas"""
from pydantic import BaseModel, Field
from typing import List, Literal


class LLMOrderDecision(BaseModel):
    """Schema for LLM order decision"""
    action: Literal["open", "close", "increase", "decrease"]
    symbol: str
    side: Literal["buy", "sell"] | None = None  # Optional for close actions
    quantity: float | None = None  # Optional for close actions
    leverage: float = 1.0
    position_id: str | None = None


class LLMResponse(BaseModel):
    """Schema for LLM trading response"""
    decision: Literal["trade", "hold"]
    reasoning: str = Field(..., max_length=500)
    orders: List[LLMOrderDecision] = []
