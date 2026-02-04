from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.admin import AdminSessionScoreOut
from app.services.adminservice import (
    delete_guest_candidate,
    get_session_report, 
    delete_guest_session,
    list_guest_candidates,
)
from app.utils.getadmin import admin_only
from app.utils.security import create_invite_token
from app.core.config import settings

router = APIRouter(prefix="/admin", tags=["Admin Management"])

@router.post("/invite-link")
def create_invite_link(admin=Depends(admin_only)):
    """
    Impact: Generates a secure token for guests to register under this admin.
    The str(admin.id) ensures the UUID is JWT-compatible.
    """
    token = create_invite_token(str(admin.id))
    
    # We use a setting for the base URL to make switching between localhost and prod easy
    invite_url = f"{settings.FRONTEND_URL}/guest/register?token={token}"

    return {
        "invite_link": invite_url,
        "expires_in": "24 hours",
    }

@router.get("/guest-candidates")
def get_candidates(
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Impact: Fetches all guests specifically belonging to the logged-in admin.
    """
    return list_guest_candidates(db, admin.id)

@router.get("/sessions/{session_id}/report")
def get_session_full_report(
    session_id: UUID, 
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Impact: Switched to get_session_report to return the detailed 
    QA transcript and dynamic average score.
    """
    report = get_session_report(db, session_id, admin.id)
    return report

@router.delete("/sessions/{session_id}")
def remove_guest_session(
    session_id: UUID, 
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Impact: Now passes admin.id to the service to ensure an admin 
    cannot delete a session belonging to another admin's guest.
    """
    if not delete_guest_session(db, session_id, admin.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Session not found or unauthorized"
        )
    return {"message": "Guest session deleted successfully"}

@router.delete("/guest-users/{guest_user_id}")
def remove_guest_user(
    guest_user_id: UUID, 
    db: Session = Depends(get_db),
    admin=Depends(admin_only)
):
    """
    Impact: Cascade deletes everything related to the guest safely.
    """
    if not delete_guest_candidate(db, guest_user_id, admin.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Guest user not found or unauthorized"
        )
    return {"message": "Guest candidate and all related data deleted"}