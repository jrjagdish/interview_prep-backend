from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models.users import GuestUser
from app.schemas.interview import AnswerRequest, StartInterviewRequest
from app.services.authService import get_current_guest, get_current_user
from app.services.interviewservice import InterviewService
from app.db.session import get_db
from app.services.getuserorguest import get_user_or_guest

router = APIRouter(prefix="/interview", tags=["Interview"])


@router.post("/interview/start")
def start_interview(
    payload: StartInterviewRequest,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    service = InterviewService(db)

    if hasattr(current_user, "role") and current_user.role == "user":
        user_id = current_user.id
        guest_id = None
        admin_id = current_user.id

    elif hasattr(current_user, "guest_id"):  # for guest token
        user_id = None
        guest_id = current_user.guest_id

    else:
        raise HTTPException(401, "Invalid authentication")

    result = service.start_interview_session(
        role=payload.role,
        level=payload.level,
        guest_id=guest_id,
        user_id=user_id,
        admin_id=admin_id
    )

    return result

@router.post("/guest/start")
def guest_start_interview(
    payload: StartInterviewRequest,
    current_guest=Depends(get_current_guest),
    db: Session = Depends(get_db),
):
    guest_id = current_guest["guest_id"]

    guest = db.query(GuestUser).filter(GuestUser.id == guest_id).first()
    if not guest:
        raise HTTPException(404, "Guest not found")

    admin_id = guest.admin_id

    service = InterviewService(db)
    result = service.start_interview_session(
        role=payload.role,
        level=payload.level,
        admin_id=admin_id,
        guest_id=guest.id,
        user_id=None,
    )

    return {
        "session_id": result["session_id"],
        "question_index": result["question_index"],
        "question": result["question"],
    }






@router.get("/{session_id}/current")
def get_current_question(
    session_id: UUID,
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
    session_id: UUID,
    payload: AnswerRequest,
    db: Session = Depends(get_db),
):
    service = InterviewService(db)
    completed = service.submit_answer(session_id, payload.answer)

    return {
        **completed,
        "next_step": "evaluate" if completed["completed"] else "next_question",
    }


@router.post("/{session_id}/evaluate")
def evaluate_interview(
    session_id: UUID,
    db: Session = Depends(get_db),
):
    service = InterviewService(db)
    result = service.evaluate_interview(session_id)
    return {
        "score": f"{result['total_score']}/5",
        "numeric_score": result["total_score"],
        "feedback": result["feedback"],
        "already_evaluated": result.get("already_evaluated", False),
    }
