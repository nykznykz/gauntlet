"""LLM Invocation model"""
from sqlalchemy import Column, String, Text, Integer, Numeric, TIMESTAMP, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from app.db.base import Base


class LLMInvocation(Base):
    """Record of LLM invocation"""
    __tablename__ = "llm_invocations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    participant_id = Column(UUID(as_uuid=True), ForeignKey("participants.id", ondelete="CASCADE"), nullable=False)
    competition_id = Column(UUID(as_uuid=True), ForeignKey("competitions.id", ondelete="CASCADE"), nullable=False)

    # Request
    prompt_text = Column(Text, nullable=False)
    prompt_tokens = Column(Integer)
    market_data_snapshot = Column(JSONB)
    portfolio_snapshot = Column(JSONB)

    # Response
    response_text = Column(Text)
    response_tokens = Column(Integer)
    parsed_decision = Column(JSONB)
    execution_results = Column(JSONB)  # Array of order execution results with validation/rejection details

    # Metadata
    invocation_time = Column(TIMESTAMP(timezone=True), server_default=func.now())
    response_time_ms = Column(Integer)
    status = Column(String(50), nullable=False)  # success, timeout, error, invalid_response
    error_message = Column(Text)

    # Cost Tracking
    estimated_cost = Column(Numeric(10, 6))

    # Relationships
    participant = relationship("Participant", back_populates="invocations")
