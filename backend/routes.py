import os
import uuid
from datetime import datetime, timedelta, timezone

import jwt
import sentry_sdk
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
import bcrypt
from pydantic import BaseModel, EmailStr
from sqlalchemy.orm import Session
import cloudinary.uploader
from db import get_db
from models import Profile, User
import config

router = APIRouter()
security = HTTPBearer()


JWT_SECRET = os.getenv("JWT_SECRET", "change-me-in-production")
JWT_ALGORITHM = "HS256"
JWT_EXPIRE_DAYS = 7

filename = f"{uuid.uuid4()}.pdf"


# ── Pydantic schemas ──────────────────────────────────────────────────────────


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_id: str
    email: str
    username: str | None


# ── Helpers ───────────────────────────────────────────────────────────────────


def _hash_password(plain: str) -> str:
    pwd_bytes = plain.encode("utf-8")
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_bytes.decode("utf-8")


def _verify_password(plain: str, hashed: str) -> bool:
    try:
        pwd_bytes = plain.encode("utf-8")
        hashed_bytes = hashed.encode("utf-8")
        return bcrypt.checkpw(pwd_bytes, hashed_bytes)
    except Exception:
        return False


def _create_token(user_id: uuid.UUID) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=JWT_EXPIRE_DAYS)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire}, JWT_SECRET, algorithm=JWT_ALGORITHM
    )


# ── Auth dependency ───────────────────────────────────────────────────────────


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    try:
        payload = jwt.decode(
            credentials.credentials, JWT_SECRET, algorithms=[JWT_ALGORITHM]
        )
        user_id: str = payload.get("sub")
        if not user_id:
            raise ValueError("missing sub")
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Token expired"
        )
    except Exception as e:
        sentry_sdk.capture_exception(e)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        )

    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found"
        )
    return user


# ── Routes ────────────────────────────────────────────────────────────────────


@router.post(
    "/api/auth/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(body: RegisterRequest, db: Session = Depends(get_db)):
    if db.query(User).filter(User.email == body.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already registered"
        )

    user = User(
        username=body.username,
        email=body.email,
        hashed_password=_hash_password(body.password),
    )
    db.add(user)
    db.flush()

    profile = Profile(user_id=user.id)
    db.add(profile)
    db.commit()
    db.refresh(user)

    return AuthResponse(
        access_token=_create_token(user.id),
        user_id=str(user.id),
        email=user.email,
        username=user.username,
    )


@router.post("/api/auth/login", response_model=AuthResponse)
def login(body: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == body.email).first()
    if not user or not _verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password"
        )

    return AuthResponse(
        access_token=_create_token(user.id),
        user_id=str(user.id),
        email=user.email,
        username=user.username,
    )


@router.get("/api/users/me")
def me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "username": current_user.username,
        "image_url": current_user.image_url,
        "is_verified": current_user.is_verified,
        "created_at": current_user.created_at,
    }


@router.post("/api/upload")
def upload_file(
    file: UploadFile,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="File not found"
        )
    result = cloudinary.uploader.upload(file.file, resource_type="image", folder="pdfs")
    profile = db.query(Profile).filter(Profile.user_id == current_user.id).first()

    if profile is None:
        raise HTTPException(status_code=404, detail="Profile not found")

    profile.resume_pdf_url = result["secure_url"]

    db.commit()
    db.refresh(profile)

    return {"Message": "Successful"}
