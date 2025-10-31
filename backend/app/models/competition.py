"""Competition model"""
from sqlalchemy import Column, String, Text, Integer, Numeric, TIMESTAMP, ARRAY, Boolean, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Competition(Base):
    """Trading competition model"""
    __tablename__ = "competitions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    status = Column(String(50), nullable=False, default="pending")  # pending, active, completed, cancelled

    # Timing
    start_time = Column(TIMESTAMP(timezone=True), nullable=False)
    end_time = Column(TIMESTAMP(timezone=True), nullable=False)
    invocation_interval_minutes = Column(Integer, nullable=False, default=15)
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Trading Rules
    initial_capital = Column(Numeric(20, 2), nullable=False, default=100000.00)
    max_leverage = Column(Numeric(5, 2), nullable=False, default=10.00)
    max_position_size_pct = Column(Numeric(5, 2), default=20.00)
    allowed_asset_classes = Column(ARRAY(Text), default=["crypto", "stocks", "indices", "commodities"])

    # CFD Configuration
    margin_requirement_pct = Column(Numeric(5, 2), nullable=False, default=10.00)
    maintenance_margin_pct = Column(Numeric(5, 2), nullable=False, default=5.00)

    # Competition Settings
    max_participants = Column(Integer, default=5)
    market_hours_only = Column(Boolean, default=True)

    # Relationships
    participants = relationship("Participant", back_populates="competition", cascade="all, delete-orphan")

    # Constraints
    __table_args__ = (
        CheckConstraint("end_time > start_time", name="valid_dates"),
        CheckConstraint("max_leverage >= 1.0 AND max_leverage <= 100.0", name="valid_leverage"),
        CheckConstraint("maintenance_margin_pct < margin_requirement_pct", name="valid_margin"),
    )
