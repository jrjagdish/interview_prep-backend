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
def login(user: UserLogin,response: Response, db: Session = Depends(get_db)):
    return login_user(user.email, user.password,response, db)


@router.post("/refresh")
def refresh(
    request: Request,
    db: Session = Depends(get_db),
):
    refresh_token = request.cookies.get("refresh_token")
    if not refresh_token:
        raise HTTPException(401, "Refresh token missing")

    new_access_token = refresh_access_token(db, refresh_token)

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
    }


@router.post("/logout")
def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}
