"""Portfolio model"""
from sqlalchemy import Column, Numeric, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Portfolio(Base):
    """Portfolio state for a participant"""
    __tablename__ = "portfolios"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)

    # Capital
    cash_balance = Column(Numeric(20, 2), nullable=False)
    equity = Column(Numeric(20, 2), nullable=False)
    margin_used = Column(Numeric(20, 2), nullable=False, default=0)
    margin_available = Column(Numeric(20, 2), nullable=False)

    # P&L
    realized_pnl = Column(Numeric(20, 2), default=0)
    unrealized_pnl = Column(Numeric(20, 2), default=0)
    total_pnl = Column(Numeric(20, 2), default=0)

    # Risk Metrics
    current_leverage = Column(Numeric(10, 4), default=0)
    margin_level = Column(Numeric(10, 4))  # Equity / Margin Used * 100

    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    participant = relationship("Participant", back_populates="portfolio")
    positions = relationship("Position", back_populates="portfolio", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("participant_id", name="unique_participant_portfolio"),
    )
