from uuid import UUID
from sqlalchemy.orm import Session
from app.models.users import GuestUser
from app.models.interviewsession import InterviewSession
from app.models.interviewevaluation import InterviewEvaluation
from app.models.interviewanswer import InterviewAnswer
from sqlalchemy.orm import selectinload


def list_guest_candidates(db: Session, admin_id: UUID):
    guests = (
        db.query(GuestUser)
        .options(selectinload(GuestUser.interview_sessions))
        .filter(GuestUser.admin_id == admin_id)
        .order_by(GuestUser.joined_at.desc())
        .all()
    )

    # now you can loop if needed
    result = [
        {
            "id": str(guest.id),
            "username": guest.username,
            "email": guest.email,
            "sessions": [
                {"session_id": str(s.id), "status": s.status}
                for s in guest.interview_sessions
            ],
        }
        for guest in guests
    ]

    return result


# guests will be a list of tuples: (GuestUser, InterviewSession)


def delete_guest_candidate(db: Session, guest_id):
    guest = db.query(GuestUser).filter(GuestUser.id == guest_id).first()
    if guest:
        db.delete(guest)
        db.commit()
    return guest


def get_session_score(db: Session, session_id: UUID, admin_id: UUID):
    return (
        db.query(
            InterviewSession.id.label("session_id"),
            GuestUser.username,
            GuestUser.email,
            InterviewEvaluation.total_score,
            InterviewEvaluation.feedback,
        )
        .join(GuestUser, InterviewSession.guest_user_id == GuestUser.id)
        .join(
            InterviewEvaluation, InterviewEvaluation.session_id == InterviewSession.id
        )
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.admin_id
            == admin_id,  # ensures admin sees only their guests
        )
        .first()
    )


def delete_guest_session(db: Session, session_id: UUID) -> bool:
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.id == session_id,
            InterviewSession.guest_user_id.isnot(None),
        )
        .first()
    )

    if not session:
        return False

    db.delete(session)
    db.commit()
    return True
