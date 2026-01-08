from fastapi import Depends
from app.models.users import User
from app.db.session import get_db
from sqlalchemy.orm import Session

from app.schemas.auth import UserCreate


def register_user(user:UserCreate,db:Session=Depends(get_db)):
    pass
