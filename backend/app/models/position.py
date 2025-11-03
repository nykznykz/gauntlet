"""Position model"""
from sqlalchemy import Column, String, Numeric, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Position(Base):
    """CFD position held by a participant"""
    __tablename__ = "positions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    portfolio_id = Column(UUID(as_uuid=True), ForeignKey("portfolios.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)

    # Asset
    symbol = Column(String(50), nullable=False)
    asset_class = Column(String(50), nullable=False)  # crypto, stocks, indices, commodities

    # Position Details
    side = Column(String(10), nullable=False)  # long, short
    quantity = Column(Numeric(20, 8), nullable=False)
    entry_price = Column(Numeric(20, 8), nullable=False)
    current_price = Column(Numeric(20, 8), nullable=False)

    # CFD Specifics
    leverage = Column(Numeric(5, 2), nullable=False)
    margin_required = Column(Numeric(20, 2), nullable=False)
    notional_value = Column(Numeric(20, 2), nullable=False)

    # P&L
    unrealized_pnl = Column(Numeric(20, 2), nullable=False)
    unrealized_pnl_pct = Column(Numeric(10, 4), nullable=False)

    # LLM Strategy Context
    exit_plan = Column(JSON, nullable=True)  # Stores LLM's original exit plan: {profit_target, stop_loss, invalidation}

    # Timestamps
    opened_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    portfolio = relationship("Portfolio", back_populates="positions")
    participant = relationship("Participant", back_populates="positions")
    trades = relationship("Trade", back_populates="position")

    __table_args__ = (
        CheckConstraint("side IN ('long', 'short')", name="valid_side"),
        CheckConstraint("quantity > 0", name="positive_quantity"),
        CheckConstraint("leverage > 0", name="positive_leverage"),
    )
