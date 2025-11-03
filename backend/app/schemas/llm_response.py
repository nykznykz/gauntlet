"""LLM response schemas"""
from pydantic import BaseModel, Field
from typing import List, Literal, Optional


class ExitPlan(BaseModel):
    """Schema for exit plan (optional)"""
    profit_target: Optional[float] = None
    stop_loss: Optional[float] = None
    invalidation: Optional[str] = None


class LLMOrderDecision(BaseModel):
    """Schema for LLM order decision"""
    action: Literal["open", "close", "increase", "decrease"]
    symbol: str
    side: Literal["buy", "sell"] | None = None  # Optional for close actions
    quantity: float | None = None  # Optional for close actions
    leverage: float = 1.0
    position_id: str | None = None
    exit_plan: Optional[ExitPlan] = None  # Optional: explicit exit conditions


class LLMResponse(BaseModel):
    """Schema for LLM trading response"""
    decision: Literal["trade", "hold"]
    reasoning: str = Field(..., max_length=500)
    confidence: Optional[float] = Field(None, ge=0.0, le=1.0)  # Optional: confidence score [0.0-1.0]
    orders: List[LLMOrderDecision] = []
