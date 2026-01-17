from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.interview import AnswerRequest, StartInterviewRequest
from app.services.authService import get_current_user,get_current_guest
from app.services.interviewservice import InterviewService
from app.db.session import get_db

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post("/start")
def start_interview(
    payload: StartInterviewRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
    guest_user = Depends(get_current_guest)
):
    service = InterviewService(db)

    result = service.start_interview_session(
        role=payload.role,
        level=payload.level,
        guest_id=guest_user.id,
        user_id=current_user.id,
    )

    return {
        "session_id": result["session_id"],
        "question_index": result["question_index"],
        "question": result["question"],
    }


@router.get("/{session_id}/current")
def get_current_question(
    session_id: int,
    db: Session = Depends(get_db),
):
    service = InterviewService(db)
    index, question = service.get_current_question(session_id)

    return {
        "question_index": index,
        "question": question,
    }


@router.post("/{session_id}/answer")
def submit_answer(
    session_id: int,
    payload: AnswerRequest,
    db: Session = Depends(get_db),
):
    service = InterviewService(db)
    completed = service.submit_answer(session_id, payload.answer)

    return {
        "completed": completed,
        "next_step": "evaluate" if completed else "next_question",
    }


@router.post("/{session_id}/evaluate")
def evaluate_interview(
    session_id: int,
    db: Session = Depends(get_db),
):
    service = InterviewService(db)
    return service.evaluate_interview(session_id)
