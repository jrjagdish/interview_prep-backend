from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from app.models.users import User
from app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, Request, Response, status, Depends
from app.utils.security import (
    create_access_token,
    verify_access_token,
    create_refresh_token,
)
from app.schemas.auth import UserCreate
from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=True)

bearer_guest = HTTPBearer(auto_error=True)


def register_user(user: UserCreate, db: Session = Depends(get_db)):
    is_company_email = user.email.endswith("@company.com")
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError("User with this email already exists.")
    if user.role == "admin" and not is_company_email:
        raise HTTPException(
            status_code=400,
            detail="Admin registration requires a company email. Use user registration instead.",
        )
    if user.role == "user" and is_company_email:
        raise HTTPException(
            status_code=400,
            detail="Company email detected. Please use admin registration.",
        )
    db_user = User(
        email=user.email,
        role=user.role,
    )
    db_user.hash_password(user.password)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )
    return db_user


def login_user(
    email: str, password: str, response: Response, db: Session = Depends(get_db)
):
    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    if not user.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect password"
        )
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        max_age=3600 * 24,
        samesite="none",
        secure=True,
    )

    refresh_token = create_refresh_token(str(user.id))

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=False,  # MUST match access_token (False for http)
        samesite="lax",
        max_age=7 * 24 * 60 * 60,
    )
    return {"access_token": access_token, "token_type": "bearer"}


def refresh_access_token(db: Session, refresh_token: str) -> str:
    try:
        payload = jwt.decode(
            refresh_token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "refresh":
            raise HTTPException(401, "Invalid token type")

        user_id = payload["sub"]

    except JWTError:
        raise HTTPException(401, "Invalid or expired refresh token")

    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()

    if not user:
        raise HTTPException(401, "User not found")

    return create_access_token(data={"sub": user.email, "role": user.role})


def get_current_user(request: Request, db: Session = Depends(get_db)):
    print(f"DEBUG: All Cookies: {request.cookies}")
    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication cookie missing",
        )
    print(f"DEBUG: Token: {token}")
    payload = verify_access_token(token)
    print(f"DEBUG: Payload: {payload}")
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )
    email: str = payload.get("sub")
    print(f"DEBUG: Sub: {email}, Type: {payload.get('type')}")

    if email is None or payload.get("type") != "user":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload"
        )
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )
    return user


def get_current_guest(request: Request):
    token = request.cookies.get("guest_token")

    if not token:
        raise HTTPException(status_code=401, detail="Guest session missing")
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )

        if payload.get("type") != "guest":
            raise HTTPException(401, "Invalid token type")

        return {
            "guest_id": payload["guest_id"],
        }

    except JWTError:
        raise HTTPException(401, "Invalid or expired guest token")
