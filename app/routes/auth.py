from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.authService import register_user, login_user, get_current_user
from app.services.guestauthService import create_guest_user
from app.schemas.auth import UserCreate, UserLogin
from app.models.users import User, GuestUser

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserCreate)
def register(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = register_user(user, db)
        return db_user
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(ve)
        )
    
@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    return login_user(user.email, user.password, db)

   