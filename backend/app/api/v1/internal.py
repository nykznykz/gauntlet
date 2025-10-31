"""Internal/Admin API endpoints"""
from fastapi import APIRouter, Depends, BackgroundTasks
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List
from pydantic import BaseModel
from app.api.dependencies import get_db_session
from app.models.participant import Participant
from app.models.competition import Competition
from app.services.llm_invoker import LLMInvoker

router = APIRouter(prefix="/internal", tags=["internal"])


class InvokeParticipantsRequest(BaseModel):
    competition_id: UUID


class InvokeParticipantsResponse(BaseModel):
    invocations_triggered: int
    participants: List[UUID]


@router.post("/invoke-participants", response_model=InvokeParticipantsResponse)
def invoke_participants(
    request: InvokeParticipantsRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db_session)
):
    """Trigger LLM invocations for all active participants in a competition"""

    # Get all active participants in the competition
    participants = (
        db.query(Participant)
        .filter(
            Participant.competition_id == request.competition_id,
            Participant.status == "active"
        )
        .all()
    )

    participant_ids = [p.id for p in participants]

    # Invoke each participant in the background
    for participant_id in participant_ids:
        background_tasks.add_task(_invoke_participant_task, participant_id)

    return {
        "invocations_triggered": len(participant_ids),
        "participants": participant_ids,
    }


def _invoke_participant_task(participant_id: UUID):
    """Background task to invoke a participant"""
    from app.db.session import SessionLocal

    db = SessionLocal()
    try:
        invoker = LLMInvoker(db)
        invoker.invoke_participant(participant_id)
    finally:
        db.close()


@router.post("/trigger-invocation/{participant_id}")
def trigger_single_invocation(
    participant_id: UUID,
    db: Session = Depends(get_db_session)
):
    """Manually trigger a single LLM invocation (for testing)"""
    invoker = LLMInvoker(db)
    invocation = invoker.invoke_participant(participant_id)

    if invocation:
        return {
            "invocation_id": invocation.id,
            "status": invocation.status,
            "response_time_ms": invocation.response_time_ms,
        }
    else:
        return {"error": "Failed to invoke participant"}
