"""Participant model"""
from sqlalchemy import Column, String, Text, Integer, Numeric, TIMESTAMP, ForeignKey, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class Participant(Base):
    """LLM participant in a competition"""
    __tablename__ = "participants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)

    # Identity
    name = Column(String(255), nullable=False)
    llm_provider = Column(String(50), nullable=False)  # anthropic, openai, custom
    llm_model = Column(String(100), nullable=False)
    llm_config = Column(JSONB)

    # Status
    status = Column(String(50), nullable=False, default="active")  # active, liquidated, disqualified
    joined_at = Column(TIMESTAMP(timezone=True), server_default=func.now())

    # Performance Tracking
    current_equity = Column(Numeric(20, 2), nullable=False)
    initial_capital = Column(Numeric(20, 2), nullable=False)
    peak_equity = Column(Numeric(20, 2), nullable=False)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)

    # API Configuration
    endpoint_url = Column(Text)
    api_key_encrypted = Column(Text)
    timeout_seconds = Column(Integer, default=30)

    created_at = Column(TIMESTAMP(timezone=True), server_default=func.now())
    updated_at = Column(TIMESTAMP(timezone=True), server_default=func.now(), onupdate=func.now())

    # Relationships
    competition = relationship("Competition", back_populates="participants")
    portfolio = relationship("Portfolio", back_populates="participant", uselist=False, cascade="all, delete-orphan")
    positions = relationship("Position", back_populates="participant", cascade="all, delete-orphan")
    orders = relationship("Order", back_populates="participant", cascade="all, delete-orphan")
    trades = relationship("Trade", back_populates="participant", cascade="all, delete-orphan")
    invocations = relationship("LLMInvocation", back_populates="participant", cascade="all, delete-orphan")

    __table_args__ = (
        UniqueConstraint("competition_id", "name", name="unique_participant_name"),
    )
