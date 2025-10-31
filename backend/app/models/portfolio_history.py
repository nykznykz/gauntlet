"""Portfolio history model for tracking equity over time"""
from sqlalchemy import Column, Numeric, TIMESTAMP, ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class PortfolioHistory(Base):
    """Snapshot of portfolio state at a point in time"""
    __tablename__ = "portfolio_history"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)

    # Portfolio state snapshot
    equity = Column(Numeric(20, 2), nullable=False)
    cash_balance = Column(Numeric(20, 2), nullable=False)
    margin_used = Column(Numeric(20, 2), nullable=False)
    realized_pnl = Column(Numeric(20, 2), nullable=False)
    unrealized_pnl = Column(Numeric(20, 2), nullable=False)
    total_pnl = Column(Numeric(20, 2), nullable=False)

    # Timestamp
    recorded_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), nullable=False)

    # Relationships
    participant = relationship("Participant")

    __table_args__ = (
        Index("idx_portfolio_history_participant_time", "participant_id", "recorded_at"),
    )
