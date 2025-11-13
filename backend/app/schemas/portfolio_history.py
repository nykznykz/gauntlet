"""Portfolio history schemas"""
from pydantic import BaseModel
from decimal import Decimal
from datetime import datetime
from uuid import UUID
from typing import List, Optional


class PortfolioHistoryPoint(BaseModel):
    """Single portfolio history data point"""
    recorded_at: datetime
    equity: Decimal
    cash_balance: Decimal
    margin_used: Decimal
    realized_pnl: Decimal
    unrealized_pnl: Decimal
    total_pnl: Decimal

    class Config:
        from_attributes = True


class DownsamplingMetadata(BaseModel):
    """Metadata about downsampling applied to history data"""
    original_count: int
    downsampled_count: int
    interval_minutes: int


class PortfolioHistoryResponse(BaseModel):
    """Portfolio history response"""
    participant_id: UUID
    participant_name: str
    history: List[PortfolioHistoryPoint]
    metadata: Optional[DownsamplingMetadata] = None


class MultiParticipantHistoryResponse(BaseModel):
    """Multi-participant equity history for charts"""
    participants: List[PortfolioHistoryResponse]
