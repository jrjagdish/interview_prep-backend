from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.admin import AdminSessionScoreOut, GuestCandidateOut
from app.services.adminservice import (
    delete_guest_candidate,
    delete_guest_session,
    get_session_score,
    list_guest_candidates,
)
from app.utils.getadmin import admin_only

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get(
    "/guest-candidates/",
    response_model=list[GuestCandidateOut],
    dependencies=[Depends(admin_only)],
)
def get_guest_candidates(db: Session = Depends(get_db)):
    return list_guest_candidates(db)


@router.get(
    "/sessions/{session_id}/score",
    response_model=AdminSessionScoreOut,
    dependencies=[Depends(admin_only)],
)
def get_session_score_view(session_id: int, db: Session = Depends(get_db)):
    eval_result = get_session_score(db, session_id)

    if not eval_result:
        raise HTTPException(status_code=404, detail="Score not found")
    

    # construct dict matching AdminSessionScoreOut
    response = {
        "guest_username": getattr(eval_result, "username", None),
        "guest_email": getattr(eval_result, "email", None),
        "total_score": float(
            getattr(eval_result, "total_score", 0.0)
        ),  # convert to float
        "already_evaluated": getattr(eval_result, "already_evaluated", False),
    }

    return response


@router.delete("/sessions/{session_id}", dependencies=[Depends(admin_only)])
def remove_guest_session(session_id: int, db: Session = Depends(get_db)):
    if not delete_guest_session(db, session_id):
        raise HTTPException(status_code=404, detail="Guest session not found")

    return {"message": "Guest session deleted successfully"}


@router.delete("/guest-users/{guest_user_id}", dependencies=[Depends(admin_only)])
def remove_guest_user(guest_user_id, db: Session = Depends(get_db)):
    if not delete_guest_candidate(db, guest_user_id):
        raise HTTPException(status_code=404, detail="Guest user not found")

    return {"message": "Guest user and all sessions deleted"}
