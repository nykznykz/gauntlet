"""Participant schemas"""
from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict, Any
from uuid import UUID


class ParticipantBase(BaseModel):
    """Base participant schema"""
    name: str = Field(..., max_length=255)
    llm_provider: str = Field(..., max_length=50)  # anthropic, openai, custom
    llm_model: str = Field(..., max_length=100)
    llm_config: Optional[Dict[str, Any]] = None
    endpoint_url: Optional[str] = None
    timeout_seconds: int = 30


class ParticipantCreate(ParticipantBase):
    """Schema for creating a participant"""
    api_key: Optional[str] = None  # Will be encrypted


class ParticipantResponse(BaseModel):
    """Schema for participant response"""
    id: UUID
    competition_id: UUID
    name: str
    llm_provider: str
    llm_model: str
    status: str
    initial_capital: Decimal
    current_equity: Decimal
    peak_equity: Decimal
    total_trades: int
    winning_trades: int
    losing_trades: int
    joined_at: datetime

    class Config:
        from_attributes = True


class ParticipantPerformance(BaseModel):
    """Schema for participant performance metrics"""
    initial_capital: Decimal
    current_equity: Decimal
    peak_equity: Decimal
    total_pnl: Decimal
    total_pnl_pct: Decimal
    total_trades: int
    winning_trades: int
    losing_trades: int
    win_rate: Decimal
