"""Competition schemas"""
from pydantic import BaseModel, Field, computed_field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from uuid import UUID


class CompetitionBase(BaseModel):
    """Base competition schema"""
    name: str = Field(..., max_length=255)
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    invocation_interval_minutes: int = 15
    initial_capital: Decimal = Decimal("100000.00")
    max_leverage: Decimal = Decimal("10.00")
    allowed_asset_classes: List[str] = ["crypto"]
    maintenance_margin_pct: Decimal = Decimal("5.00")
    max_participants: int = 5
    market_hours_only: bool = True

    @computed_field
    @property
    def margin_requirement_pct(self) -> Decimal:
        """Calculate margin requirement from max leverage: margin_pct = 100 / leverage"""
        return Decimal("100") / self.max_leverage


class CompetitionCreate(CompetitionBase):
    """Schema for creating a competition"""
    pass


class CompetitionUpdate(BaseModel):
    """Schema for updating a competition"""
    name: Optional[str] = None
    description: Optional[str] = None
    max_participants: Optional[int] = None


class CompetitionResponse(CompetitionBase):
    """Schema for competition response"""
    id: UUID
    status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class CompetitionList(BaseModel):
    """Schema for competition list response"""
    competitions: List[CompetitionResponse]
    total: int
    limit: int
    offset: int
