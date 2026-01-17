from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.services.interviewservice import InterviewService
from app.db.session import get_db
router = APIRouter(prefix="/interview", tags=["Interview"])

@router.post("/start")
def start_interview(
    role: str,
    level: str,
    guest_id: int | None = None,
    user_id: int | None = None,
    db: Session = Depends(get_db)
):
    service = InterviewService(db)
    session_id, first_question = service.start_interview_session(
        role=role,
        level=level,
        guest_id=guest_id,
        user_id=user_id
    )
    return {"session_id": session_id, "first_question": first_question}

@router.get("/{session_id}/current")
def get_current_question(
    session_id: int,
    db: Session = Depends(get_db)
):
    service = InterviewService(db)
    index, question = service.get_current_question(session_id)

    return {
        "index": index,
        "question": question
    }

@router.post("/{session_id}/answer")
def submit_answer(
    session_id: int,
    answer: str,
    db: Session = Depends(get_db)
):
    service = InterviewService(db)
    completed = service.submit_answer(session_id, answer)

    return {"completed": completed}

@router.post("/{session_id}/evaluate")
def evaluate_interview(
    session_id: int,
    db: Session = Depends(get_db)
):
    service = InterviewService(db)
    return service.evaluate_interview(session_id)

