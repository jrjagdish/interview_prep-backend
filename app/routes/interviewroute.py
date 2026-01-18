from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.interview import AnswerRequest, StartInterviewRequest

from app.services.interviewservice import InterviewService
from app.db.session import get_db
from app.services.getuserorguest import get_user_or_guest

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post("/start")
def start_interview(
    payload: StartInterviewRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_user_or_guest),
):
    service = InterviewService(db)
    if current_user["type"] == "user":
        user = current_user["data"]
        user_id = user.id
        guest_id = None

    elif current_user["type"] == "guest":
        user_id = None
        guest_id = current_user["data"]["guest_id"]

    else:
        raise HTTPException(401, "Invalid authentication")

    result = service.start_interview_session(
        role=payload.role,
        level=payload.level,
        guest_id=guest_id,
        user_id=user_id,
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
    result = service.evaluate_interview(session_id)
    return {
        "score": f"{result['total_score']}/5",
        "numeric_score": result["total_score"],
        "feedback": result["feedback"],
        "already_evaluated": result["already_evaluated"],
    }
