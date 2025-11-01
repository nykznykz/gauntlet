"""LLM Invocation schemas"""
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import List, Optional, Dict, Any


class LLMInvocationResponse(BaseModel):
    """Schema for LLM invocation response"""
    id: UUID
    participant_id: UUID
    competition_id: UUID

    # Request
    prompt_text: str
    prompt_tokens: Optional[int] = None
    market_data_snapshot: Optional[Dict[str, Any]] = None
    portfolio_snapshot: Optional[Dict[str, Any]] = None

    # Response
    response_text: Optional[str] = None
    response_tokens: Optional[int] = None
    parsed_decision: Optional[Dict[str, Any]] = None
    execution_results: Optional[List[Dict[str, Any]]] = None

    # Metadata
    invocation_time: datetime
    response_time_ms: Optional[int] = None
    status: str  # success, timeout, error, invalid_response
    error_message: Optional[str] = None

    # Cost Tracking
    estimated_cost: Optional[Decimal] = None

    class Config:
        from_attributes = True


class LLMInvocationList(BaseModel):
    """Schema for LLM invocation list response"""
    invocations: List[LLMInvocationResponse]
    total: int
    limit: int
    offset: int
