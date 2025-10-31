"""Trade model"""
from sqlalchemy import Column, String, Numeric, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Trade(Base):
    """Executed trade"""
    __tablename__ = "trades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    order_id = Column(UUID(as_uuid=True), ForeignKey("orders.id", ondelete="CASCADE"), nullable=False)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    position_id = Column(UUID(as_uuid=True), ForeignKey("positions.id", ondelete="SET NULL"))

    # Trade Details
    symbol = Column(String(50), nullable=False)
    side = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(Numeric(20, 8), nullable=False)
    price = Column(Numeric(20, 8), nullable=False)

    # Position Action
    action = Column(String(20), nullable=False)  # open, close, increase, decrease

    # CFD Details
    leverage = Column(Numeric(5, 2), nullable=False)
    notional_value = Column(Numeric(20, 2), nullable=False)
    margin_impact = Column(Numeric(20, 2), nullable=False)

    # P&L (for closing trades)
    realized_pnl = Column(Numeric(20, 2))
    realized_pnl_pct = Column(Numeric(10, 4))

    executed_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Relationships
    order = relationship("Order", back_populates="trades")
    participant = relationship("Participant", back_populates="trades")
    position = relationship("Position", back_populates="trades")

    __table_args__ = (
        CheckConstraint("action IN ('open', 'close', 'increase', 'decrease')", name="valid_action"),
    )
