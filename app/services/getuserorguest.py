from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError,jwt
from app.models.users import User
from app.db.session import get_db
from sqlalchemy.orm import Session
from fastapi import HTTPException,Depends
from app.core.config import settings

bearer_scheme = HTTPBearer(auto_error=True)


def get_user_or_guest(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    token = credentials.credentials

    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
    except JWTError:
        raise HTTPException(401, "Invalid token")

    # USER
    if payload.get("type") == "user":
        user = db.query(User).filter(User.email == payload.get("sub")).first()
        if not user:
            raise HTTPException(401, "User not found")

        return {
            "type": "user",
            "data": user,
        }

    # GUEST
    if payload.get("type") == "guest":
        return {
            "type": "guest",
            "data": {
                "guest_id": payload["guest_id"],
            },
        }

    raise HTTPException(401, "Unknown token type")
