"""Order model"""
from sqlalchemy import Column, String, Text, Numeric, TIMESTAMP, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Order(Base):
    """Trading order placed by a participant"""
    __tablename__ = "orders"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)

    # Order Details
    symbol = Column(String(50), nullable=False)
    asset_class = Column(String(50), nullable=False)
    order_type = Column(String(20), nullable=False, default="market")  # market, limit
    side = Column(String(10), nullable=False)  # buy, sell
    quantity = Column(Numeric(20, 8), nullable=False)

    # Pricing
    requested_price = Column(Numeric(20, 8))
    executed_price = Column(Numeric(20, 8))

    # CFD
    leverage = Column(Numeric(5, 2), nullable=False, default=1.0)

    # Status
    status = Column(String(50), nullable=False)  # pending, executed, rejected, cancelled
    rejection_reason = Column(Text)

    # Timestamps
    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    executed_at = Column(TIMESTAMP(timezone=True))

    # LLM Context
    llm_invocation_id = Column(UUID(as_uuid=True), ForeignKey("llm_invocations.id", ondelete="SET NULL"))

    # Relationships
    participant = relationship("Participant", back_populates="orders")
    trades = relationship("Trade", back_populates="order")

    __table_args__ = (
        CheckConstraint("order_type IN ('market', 'limit')", name="valid_order_type"),
        CheckConstraint("side IN ('buy', 'sell')", name="valid_side"),
        CheckConstraint("quantity > 0", name="positive_quantity"),
    )
