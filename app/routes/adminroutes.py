from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.admin import AdminSessionScoreOut
from app.services.adminservice import (
    delete_guest_candidate,
    delete_guest_session,
    get_session_score,
    list_guest_candidates,
)
from app.services.authService import get_current_user
from app.utils.getadmin import admin_only
from app.utils.security import create_invite_token

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.post("/invite-link", dependencies=[Depends(admin_only)])
def create_invite_link(admin=Depends(admin_only)):
    token = create_invite_token(str(admin.id))

    invite_url = f"https://yourfrontend.com/guest/upload?token={token}"

    return {
        "invite_link": invite_url,
        "expires_in": "24 hours",
    }


@router.get(
    "/guest-candidates/",
    dependencies=[Depends(admin_only)],
)
def get_guest_candidates(db: Session = Depends(get_db),current_admin=Depends(get_current_user)):
    admin_id = current_admin.id
    return list_guest_candidates(db,admin_id)


@router.get(
    "/sessions/{session_id}/score",
    response_model=AdminSessionScoreOut,
    dependencies=[Depends(admin_only)],
)
def get_session_score_view(session_id: UUID , db: Session = Depends(get_db),current_admin=Depends(get_current_user)):
    admin_id = current_admin.id
    eval_result = get_session_score(db, session_id,admin_id)

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
def remove_guest_session(session_id: UUID , db: Session = Depends(get_db)):
    if not delete_guest_session(db, session_id):
        raise HTTPException(status_code=404, detail="Guest session not found")

    return {"message": "Guest session deleted successfully"}


@router.delete("/guest-users/{guest_user_id}", dependencies=[Depends(admin_only)])
def remove_guest_user(guest_user_id, db: Session = Depends(get_db)):
    if not delete_guest_candidate(db, guest_user_id):
        raise HTTPException(status_code=404, detail="Guest user not found")

    return {"message": "Guest user and all sessions deleted"}
