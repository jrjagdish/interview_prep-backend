from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.authService import (
    refresh_access_token,
    register_user,
    login_user,
    get_current_user,
)
from app.services.guestauthService import create_guest_user
from app.schemas.auth import UserCreate, UserLogin
from app.models.users import User, GuestUser

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = register_user(user, db)
        return {"message": "registered"}
    except ValueError as ve:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))


@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    return login_user(user.email, user.password, response, db)


@router.post("/refresh")
def refresh(
    request: Request,
    response: Response,  # Add Response here
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(401, "Refresh token missing")

    new_access_token = refresh_access_token(db, refresh_token)

    # Update the access_token cookie
    response.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesite="lax",
        secure=False,
        max_age=3600,
    )

    return {"message": "Token refreshed"}


@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    # current_user is provided by the dependency we wrote earlier
    name = current_user.email.split("@")[0]
    return {
        "email": current_user.email,
        "full_name": name,
        "role": current_user.role,
        "id": current_user.id,
        # You can add logic here to fetch real stats from other tables
        "stats": {"total_interviews": 12, "success_rate": 78, "skills_count": 5},
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    response.delete_cookie(
        key="access_token",
        httponly=True,
        samesite="lax",
    )
    return {"message": "Logged out"}
