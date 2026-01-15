from fastapi.security import OAuth2PasswordBearer
from app.models.users import User
from app.db.session import get_db
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status, Depends
from app.utils.security import create_access_token,verify_access_token
from app.schemas.auth import UserCreate
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")


def register_user(user:UserCreate,db:Session=Depends(get_db)):
    
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise ValueError("User with this email already exists.")
    db_user=User(
        email=user.email,
    )
    db_user.hash_password(user.password)
    try:
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
       
    
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )  
    return db_user

def login_user(email:str,password:str,db:Session=Depends(get_db)):
    user=db.query(User).filter(User.email==email).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    if not user.verify_password(password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    access_token = create_access_token(data={"sub": user.email})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(token:str = Depends(oauth2_scheme),db:Session=Depends(get_db)):
    payload=verify_access_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    email: str = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    user=db.query(User).filter(User.email==email).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user