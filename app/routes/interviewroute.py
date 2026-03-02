from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.ai.run import evaluate
from app.db.session import get_db
from app.models.users import User
from app.models.interview import InterviewQA, InterviewSession
from app.schemas.interview import StartInterviewRequest
from app.services.authService import get_current_user

router = APIRouter(prefix="/interview", tags=["Interview Session"])

@router.post("/start")
def start_user_interview(
    payload: StartInterviewRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # 1. Create Session
    new_session = InterviewSession(
        user_id=current_user.id,
        admin_id=current_user.id, 
        title=f"{payload.level} {payload.role} Interview",
        status="IN_PROGRESS",
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)

    # 2. Initialize QA Record for storing history
    new_qa = InterviewQA(
        session_id=new_session.id,
        chat_history=[] # Initialize empty list
    )
    db.add(new_qa)
    db.commit()

    return {
        "session_id": new_session.id,
        "message": "Session started, connect to /ws/interview/{session_id}",
    }

@router.get("/history")
def get_interview_history(
    current_user: User = Depends(get_current_user), db: Session = Depends(get_db)
):
    data = db.query(InterviewSession).filter(InterviewSession.user_id == current_user.id).all()
    return data

@router.get('/score/{session_id}')
def score_evaluation(session_id:UUID,current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    answer = db.query(InterviewQA).filter(InterviewQA.session_id == session_id).first()
    
    if not answer:
        raise HTTPException(status_code=404, detail="Interview session not found.")
        
    result,feedback= evaluate(answer.chat_history)
    answer.score = int(result.score)
    answer.ai_feedback = feedback
    try:
        db.commit()
        db.refresh(answer)
    except:
        db.rollback()
        raise HTTPException(status_code=500, detail="Database update failed.")

    return {
        "session_id": session_id,
        "score": answer.score,
        "feedback": answer.ai_feedback
    }