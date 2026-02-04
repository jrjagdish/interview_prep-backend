from uuid import UUID
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from fastapi import HTTPException

from app.models.users import GuestUser
from app.models.interview import InterviewSession, InterviewQA

def list_guest_candidates(db: Session, admin_id: UUID):
    """
    Fetches all guests for an admin, including their session summaries.
    Impact: Uses selectinload to prevent the 'N+1' problem. 
    One query for guests + One query for all their sessions.
    """
    guests = (
        db.query(GuestUser)
        .options(selectinload(GuestUser.interview_sessions))
        .filter(GuestUser.admin_id == admin_id)
        .order_by(GuestUser.joined_at.desc())
        .all()
    )

    return [
        {
            "id": str(guest.id),
            "username": guest.username,
            "email": guest.email,
            "joined_at": guest.joined_at,
            "sessions": [
                {
                    "session_id": str(s.id), 
                    "status": s.status,
                    "created_at": s.created_at
                } for s in guest.interview_sessions
            ],
        } for guest in guests
    ]

def delete_guest_candidate(db: Session, guest_id: UUID, admin_id: UUID):
    """
    Impact: Added admin_id check. 
    Without this, an attacker could delete ANY guest by guessing a UUID.
    """
    guest = db.query(GuestUser).filter(
        GuestUser.id == guest_id, 
        GuestUser.admin_id == admin_id
    ).first()
    
    if not guest:
        raise HTTPException(status_code=404, detail="Guest not found or unauthorized")

    db.delete(guest)
    db.commit()
    return True

def get_session_report(db: Session, session_id: UUID, admin_id: UUID):
    """
    Impact: Updated to use the unified InterviewQA table.
    Instead of a static evaluation table, we calculate the score dynamically 
    from individual question scores.
    """
    # 1. Get the session and guest info
    session_data = (
        db.query(InterviewSession, GuestUser)
        .join(GuestUser, InterviewSession.guest_user_id == GuestUser.id)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.admin_id == admin_id
        )
        .first()
    )

    if not session_data:
        raise HTTPException(status_code=404, detail="Session not found")

    session, guest = session_data

    # 2. Aggregate the score from the QA table
    stats = (
        db.query(
            func.avg(InterviewQA.score).label("avg_score"),
            func.count(InterviewQA.id).label("total_q")
        )
        .filter(InterviewQA.session_id == session_id)
        .first()
    )

    # 3. Fetch the full QA transcript
    transcript = (
        db.query(InterviewQA)
        .filter(InterviewQA.session_id == session_id)
        .order_by(InterviewQA.created_at.asc())
        .all()
    )

    return {
        "candidate": guest.username,
        "email": guest.email,
        "status": session.status,
        "average_score": round(stats.avg_score, 2) if stats.avg_score else 0,
        "transcript": [
            {
                "question": qa.question_text,
                "answer": qa.user_answer,
                "score": qa.score,
                "feedback": qa.ai_feedback
            } for qa in transcript
        ]
    }

def delete_guest_session(db: Session, session_id: UUID, admin_id: UUID):
    """
    Impact: Added admin_id check to prevent unauthorized deletions.
    """
    session = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.admin_id == admin_id
    ).first()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found or unauthorized")

    db.delete(session)
    db.commit()
    return True