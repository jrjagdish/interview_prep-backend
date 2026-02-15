from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import RedirectResponse
import httpx
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.authService import (
    register_user,
    login_user,
    get_current_user,
    authenticate_google_user,
    get_profile_data
)
from app.schemas.auth import UserCreate, UserLogin
from app.models.users import User
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["Authentication"])


COOKIE_PARAMS = {
    "httponly": True,
    "samesite": "lax",
    "secure": settings.ENVIRONMENT == "production",
}

@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, db: Session = Depends(get_db)):
    register_user(user, db)
    return {"message": "User registered successfully"}

@router.post("/login")
def login(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    return login_user(user.email, user.password, response, db)

@router.get("/google/login")
def google_login():
   
    google_auth_url = (
        f"https://accounts.google.com/o/oauth2/v2/auth?"
        f"client_id={settings.GOOGLE_CLIENT_ID}&"
        f"redirect_uri={settings.GOOGLE_REDIRECT_URI}&"
        f"response_type=code&"
        f"scope=openid%20email%20profile"
    )
    return {"auth_url": google_auth_url}

@router.get("/callback")
async def auth_callback(code: str, response: Response, db: Session = Depends(get_db)):
    """Step 2: Google sends the user here with a 'code'"""
    
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code",
    }

    async with httpx.AsyncClient() as client:
       
        token_res = await client.post(token_url, data=data)
        if token_res.status_code != 200:
            raise HTTPException(400, "Failed to exchange code for token")
        
        token_data = token_res.json()
        access_token = token_data.get("access_token")

      
        user_info_res = await client.get(
            "https://www.googleapis.com/oauth2/v3/userinfo",
            headers={"Authorization": f"Bearer {access_token}"},
        )
        user_info = user_info_res.json()

       
        auth_data = authenticate_google_user(user_info, response, db)
        
    
    return auth_data 

@router.get("/me")
def read_users_me(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    
    user_with_profile = get_profile_data(db, current_user.id)
    return user_with_profile

@router.post("/logout")
def logout(response: Response):
    response.delete_cookie(key="access_token", path="/", **COOKIE_PARAMS)
    response.delete_cookie(key="refresh_token", path="/", **COOKIE_PARAMS)
    return {"message": "Logged out successfully"}