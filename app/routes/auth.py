from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.authService import (
    create_refresh_token,
    get_profile_data,
    register_user,
    login_user,
    get_current_user,
)
from app.schemas.auth import UserCreate, UserLogin, UserResponse
from app.models.users import User
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])

# Helper for consistent cookie settings across routes
COOKIE_PARAMS = {
    "httponly": True,
    "samesite": "lax",
    "secure": settings.ENVIRONMENT == "production",
}

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    Impact: Logic moved to service, router handles response status.
    """
    register_user(user, db)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    """
    Impact: Sets both Access and Refresh cookies inside the login_user service.
    """
    return login_user(user.email, user.password, response, db)

@router.post("/refresh")
def refresh(
    request: Request,
    response: Response,
    db: Session = Depends(get_db),
):
    """
    Impact: Automatically rotates the access token cookie. 
    Crucial for B2B security to keep the session alive without re-login.
    """
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired. Please login again.")

    new_access_token = create_refresh_token(db, refresh_token)

    # Re-set the access_token cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        max_age=3600,  # 1 hour
        **COOKIE_PARAMS
    )

    return {"message": "Token refreshed"}

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user),db: Session = Depends(get_db)):
    """
    Impact: Returns the current user profile. 
    Frontend uses this to populate the dashboard and check roles.
    """
    user_data = get_profile_data(db,current_user.id)
    print(user_data.profile.interview_credits)
    return user_data

@router.post("/logout")
def logout(response: Response):
    """
    Impact: Wipes both cookies. 
    Explicitly setting path="/" ensures cookies are deleted across all sub-routes.
    """
    response.delete_cookie(key="access_token", path="/", **COOKIE_PARAMS)
    response.delete_cookie(key="refresh_token", path="/", **COOKIE_PARAMS)
    return {"message": "Logged out successfully"}