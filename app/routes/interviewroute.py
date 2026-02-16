from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
import requests
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import GuestUser, User
from app.models.interview import InterviewSession
from app.schemas.interview import (
    AnswerRequest,
    StartInterviewRequest,
    InterviewEvaluationOut,
)
from app.services.authService import get_current_user
from app.services.interviewservice import create_token_for_room

router = APIRouter(prefix="/interview", tags=["Interview Session"])


@router.post("/start")
def start_user_interview(
    payload: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    new_session = InterviewSession(
        user_id=current_user.id,
        admin_id=current_user.id,  # Assigning user as their own admin for now
        title=f"{payload.level} {payload.role} Interview",
        status="IN_PROGRESS",
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    token_str = create_token_for_room(
        role=payload.role,
        user_id=str(current_user.id),
        user_name=current_user.username,
        session_id=str(new_session.id),
    )
    return {
        "token": token_str,
        "session_id": new_session.id,
        "room_name": f"room_{new_session.id}",
    }


@router.get("/history")
def get_interview_history(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    data = db.query(InterviewSession).filter(InterviewSession.user_id == current_user.id).all()
    return data


