from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.users import GuestUser, User
from app.schemas.interview import (
    AnswerRequest,
    StartInterviewRequest,
    InterviewEvaluationOut,
)
from app.services.authService import get_current_user
from app.services.guestauthService import get_current_guest
from app.services.interviewservice import InterviewService

router = APIRouter(prefix="/interview", tags=["Interview Session"])


@router.post("/start")
def start_user_interview(
    payload: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service = InterviewService(db)
    return service.start_interview_session(
        role=payload.role,
        level=payload.level,
        admin_id=current_user.id,
        user_id=current_user.id,
        guest_id=None,
    )


@router.post("/guest/start",response_model=None)
def start_guest_interview(
    payload: StartInterviewRequest,
    current_guest: GuestUser = Depends(get_current_guest),
    db: Session = Depends(get_db),
):
    service = InterviewService(db)
    return service.start_interview_session(
        role=payload.role,
        level=payload.level,
        admin_id=current_guest.admin_id,
        user_id=None,
        guest_id=current_guest.id,
    )


@router.get("/{session_id}/current")
def get_current_question(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    service = InterviewService(db)
    index, question = service.get_current_question(session_id)
    return {"question_index": index, "question": question}


@router.post("/{session_id}/answer")
def submit_answer(
    session_id: UUID,
    payload: AnswerRequest,
    db: Session = Depends(get_db),
):
    service = InterviewService(db)
    result = service.submit_answer(session_id, payload.answer)

    return {
        **result,
        "next_step": "evaluate" if result.get("completed") else "next_question",
    }



