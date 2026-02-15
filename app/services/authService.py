from fastapi import HTTPException, Request, Response, status, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Dict, Any

from app.models.interview import InterviewSession
from app.models.users import User, Profile
from app.db.session import get_db
from app.schemas.auth import UserCreate
from app.utils.security import (
    create_access_token,
    create_refresh_token,
    verify_access_token,
)

# Shared cookie configuration
COOKIE_SETTINGS = {
    "httponly": True,
    "samesite": "lax",
    "secure": False,  # Set to True in production (HTTPS)
    "path": "/",
}


def _generate_auth_response(user: User, response: Response,imgurl:str) -> Dict[str, Any]:
    """Sets cookies and returns basic user info."""
    access_token = create_access_token(
        data={"sub": user.email, "id": str(user.id), "type": "user"}
    )
    refresh_token = create_refresh_token(user_id=str(user.id))

    response.set_cookie(
        key="access_token", value=access_token, **COOKIE_SETTINGS, max_age=3600
    )
    response.set_cookie(
        key="refresh_token", value=refresh_token, **COOKIE_SETTINGS, max_age=604800
    )

    return {
        "status": "success",
        "username": user.username,
        "email": user.email,
        "imgUrl" : imgurl
    }


def register_user(user_schema: UserCreate, db: Session):
    existing = db.query(User).filter(User.email == user_schema.email).first()
    if existing:
        raise HTTPException(status.HTTP_409_CONFLICT, "Email already registered.")

    new_user = User(
        email=user_schema.email, 
        username=user_schema.username,
        role="user"  
    )
    new_user.hash_password(user_schema.password)

    db.add(new_user)
    db.flush() 

  
    db.add(Profile(user_id=new_user.id))
    db.commit()
    db.refresh(new_user)
    return new_user


def login_user(email: str, password: str, response: Response, db: Session):
    user = db.query(User).filter(User.email == email).first()
    if not user or not user.verify_password(password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")

    return _generate_auth_response(user, response)


def authenticate_google_user(google_data: dict, response: Response, db: Session):
    """
    google_data should contain 'sub' (the unique Google ID), 'email', and 'name'.
    """
    img_url = google_data.get("picture")
    google_id = str(google_data.get("sub"))
    email = google_data.get("email")

  
    user = db.query(User).filter(User.google_id == google_id).first()

    if not user:
      
        user = db.query(User).filter(User.email == email).first()
        
        if user:
           
            user.google_id = google_id
            db.commit()
        else:
          
            user = User(
                email=email,
                username=google_data.get("name", email),
                google_id=google_id,
                role="user"
            )
            
            db.add(user)
            db.flush()
            db.add(Profile(user_id=user.id))
            db.commit()
            db.refresh(user)

    return _generate_auth_response(user, response,img_url)


def get_current_user(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("access_token")
    
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Authentication required")

    payload = verify_access_token(token)
    if not payload or payload.get("type") != "user":
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid session")

   
    user = db.query(User).filter(User.id == payload.get("id")).first()
    if not user:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User no longer exists")

    return user

def get_profile_data(db: Session, user_id: UUID):
    result = (
        db.query(
            User,
            Profile,
            func.count(InterviewSession.id).label("total_interviews")
        )
        .join(Profile, User.id == Profile.user_id)
        .outerjoin(InterviewSession, User.id == InterviewSession.user_id)
        .filter(User.id == user_id)
        .group_by(User.id, Profile.id)
        .first()
    )

    if not result:
        return None

    user, profile, total_interviews = result
    
    # Combine data into a clean dictionary
    return {
        "user_info": {
            "username": user.username,
            "email": user.email,
        },
        "profile_info": {
            "bio": profile.interview_credits, # Add your actual profile fields here
            "interview_credits": profile.interview_credits,
        },
        "stats": {
            "total_interviews": total_interviews
        }
    }