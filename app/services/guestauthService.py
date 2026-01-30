from uuid import UUID
from fastapi import HTTPException, Request, status, Response,Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.users import GuestUser
from app.utils.security import create_guest_token, verify_access_token
from app.core.config import settings

def create_guest_user(
    username: str, 
    email: str, 
    pdf_url: str, 
    cloudinary_public_id: str, 
    admin_id: UUID, 
    response: Response, # Added response to set cookie
    db: Session
):
    """
    Creates a guest and sets a secure HttpOnly cookie.
    """
    # 1. Conflict Check (Optimized)
    # We check by email to prevent duplicate candidate entries for the same admin
    existing_user = db.query(GuestUser).filter(GuestUser.email == email).first()
    
    if existing_user:
        # Instead of just erroring, we return the existing user 
        # or raise conflict based on your preference. 
        # Here we follow your conflict logic:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A candidate with this email is already registered."
        )

    # 2. Create Guest
    guest_user = GuestUser(
        username=username,
        email=email,
        pdf_url=pdf_url,
        cloudinary_public_id=cloudinary_public_id,
        admin_id=admin_id,
    )
    
    db.add(guest_user)
    db.commit()
    db.refresh(guest_user)

    # 3. Secure Token Generation
    # We pass 'guest' as the type to differentiate from full users in the middleware
    token = create_guest_token(data={
        "guest_id": str(guest_user.id),
        "type": "guest",
        "admin_id": str(admin_id)
    })

    # 4. Set HttpOnly Cookie
    response.set_cookie(
        key="guest_token",
        value=token,
        httponly=True,
        samesite="lax",
        secure=settings.ENVIRONMENT == "production",
        max_age=3600 * 4 # 4 hours for an interview session
    )

    return {
        "message": "Guest session started",
        "guest_id": guest_user.id,
        "username": guest_user.username
    }

def get_current_guest(request: Request, db: Session = Depends(get_db)):
    """
    Retrieves the current guest user based on the guest_token cookie.
    """
    guest_token = request.cookies.get("guest_token")
    if not guest_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Guest session not found. Please upload your resume again.")

    payload = verify_access_token(guest_token)
    guest_id = payload.get("guest_id")

    guest_user = db.query(GuestUser).filter(GuestUser.id == guest_id).first()
    if not guest_user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Guest user not found.")

    return guest_user