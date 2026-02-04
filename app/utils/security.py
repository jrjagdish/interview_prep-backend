from fastapi import HTTPException
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from app.core.config import settings

# Helper for consistent timezone-aware "now"
def get_now():
    return datetime.now(timezone.utc)

def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Standard Access Token. 
    Impact: Explicitly sets type='user' and includes 'role' from data.
    """
    to_encode = data.copy()
    expire = get_now() + (expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES))
    
    # Ensure type is set to prevent token-swapping attacks
    to_encode.update({"exp": expire, "type": "user"})
    
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_refresh_token(user_id: str) -> str:
    """
    Refresh Token for rotating sessions.
    Impact: Longer expiry, strictly type='refresh'.
    """
    payload = {
        "sub": str(user_id),
        "type": "refresh",
        "exp": get_now() + timedelta(days=7),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_guest_token(data: dict) -> str:
    """
    Impact: Changed to accept a dict to allow 'admin_id' and 'guest_id' 
    to be stored inside the token for better session validation.
    """
    to_encode = data.copy()
    expire = get_now() + timedelta(hours=4) # Guests usually need more than 30 mins
    to_encode.update({"exp": expire, "type": "guest"})

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def create_invite_token(admin_id: str) -> str:
    """
    Token used in the 'Invite Link' URL.
    """
    payload = {
        "admin_id": str(admin_id),
        "type": "invite",
        "exp": get_now() + timedelta(hours=24),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def verify_token(token: str, expected_type: str):
    """
    Central verifier that checks signature AND the 'type' claim.
    """
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        # This is the critical security check
        if payload.get("type") != expected_type:
            return None
            
        return payload
    except JWTError:
        return None

# Use these in your dependencies (get_current_user, get_current_guest, etc.)
def verify_access_token(token: str):
    return verify_token(token, expected_type="user")

def verify_guest_token(token: str):
    return verify_token(token, expected_type="guest")

def verify_invite_token(token: str):
    return verify_token(token, expected_type="invite")

def verify_refresh_token(token: str):
    return verify_token(token, expected_type="refresh")