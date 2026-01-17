from sqlalchemy.orm import Session
from app.models.users import GuestUser
from app.models.interviewsession import InterviewSession
from app.models.interviewevaluation import InterviewEvaluation
from app.models.interviewanswer import InterviewAnswer



def list_guest_candidates(db: Session):
    return db.query(GuestUser).order_by(GuestUser.joined_at.desc()).all()

def delete_guest_candidate(db: Session, guest_id):
    guest = db.query(GuestUser).filter(GuestUser.id == guest_id).first()
    if guest:
        db.delete(guest)
        db.commit()
    return guest

def get_session_score(db: Session, session_id: int):
    return (
        db.query(
            InterviewSession.id.label("session_id"),
            GuestUser.username,
            GuestUser.email,
            InterviewEvaluation.total_score,
           
            InterviewEvaluation.feedback,
        )
        .join(GuestUser, InterviewSession.guest_user_id == GuestUser.id)
        .join(InterviewEvaluation, InterviewEvaluation.session_id == InterviewSession.id)
        .filter(InterviewSession.id == session_id)
        .first()
    )

def delete_guest_session(db: Session, session_id: int) -> bool:
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.guest_user_id.isnot(None)
        )
        .first()
    )

    if not session:
        return False

    db.delete(session)
    db.commit()
    return True
