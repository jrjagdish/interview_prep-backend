from fastapi import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta
from app.core.config import settings

def create_invite_token(admin_id: str) -> str:
    payload = {
        "admin_id": admin_id,
        "type": "invite",
        "exp": datetime.utcnow() + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
def decode_invite_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "invite":
            raise HTTPException(401, "Invalid invite token")
        return payload["admin_id"]
    except JWTError:
        raise HTTPException(401, "Invite link expired or invalid")
    
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    to_encode["type"] = "user"
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt


def verify_access_token(token: str):
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


from app.core.config import settings


def create_guest_token(guest_id: str) -> str:
    payload = {
        "type": "guest",
        "guest_id": guest_id,
        "exp": datetime.utcnow() + timedelta(minutes=30),
    }

    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )
