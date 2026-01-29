from fastapi import HTTPException, Request, Response, status, Depends
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from datetime import timedelta
from uuid import UUID

from app.models.users import User, Profile # Import Profile
from app.db.session import get_db
from app.schemas.auth import UserCreate
from app.utils.security import create_access_token, verify_access_token, create_refresh_token
from app.core.config import settings

# --- FIXING CORS/COOKIE ISSUES ---
# If frontend is on :3000 and backend on :8000, 
# SameSite must be 'Lax' or 'None' (if using HTTPS)
COOKIE_SETTINGS = {
    "httponly": True,
    "samesite": "lax", 
    "secure": settings.ENVIRONMENT == "production", # False for localhost
}

def register_user(user_schema:UserCreate, db: Session):
    # 1. Validation Logic
    is_company = user_schema.email.endswith("@company.com")
    if user_schema.role == "admin" and not is_company:
        raise HTTPException(400, "Admins must use company emails.")
    
    existing = db.query(User).filter(User.email == user_schema.email).first()
    if existing:
        raise HTTPException(409, "Email already registered.")

    # 2. Create User
    new_user = User(
        email=user_schema.email,
        role=user_schema.role,
        username=user_schema.username
    )
    new_user.hash_password(user_schema.password)
    
    db.add(new_user)
    db.flush() # Get ID for profile

    # 3. Create Profile (New requirement)
    new_profile = Profile(user_id=new_user.id)
    db.add(new_profile)
    
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(email: str, password: str, response: Response, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.verify_password(password):
        raise HTTPException(401, "Invalid credentials")

    # 4. Generate Tokens with Role & ID
    access_token = create_access_token(data={
        "sub": user.email, 
        "id": str(user.id), 
        "role": user.role,
        "type": "user" 
    })
    
    refresh_token = create_refresh_token(data={
        "sub": str(user.id),
        "type": "refresh"
    })

    # 5. Set HttpOnly Cookies
    response.set_cookie(key="access_token", value=access_token, **COOKIE_SETTINGS, max_age=3600)
    response.set_cookie(key="refresh_token", value=refresh_token, **COOKIE_SETTINGS, max_age=604800)

    return {"message": "Logged in successfully", "role": user.role}

def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(401, "Authentication required")

    payload = verify_access_token(token)
    if not payload or payload.get("type") != "user":
        raise HTTPException(401, "Invalid session")

    user = db.query(User).filter(User.email == payload.get("sub")).first()
    if not user:
        raise HTTPException(404, "User no longer exists")
    
    return user