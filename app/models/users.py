from sqlalchemy import Integer, String, Boolean,Column
from sqlalchemy.ext.declarative import declarative_base
import uuid
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

Base = declarative_base()
class User(Base):
    __tablename__ = "users"
    id = Column(uuid,primary_key=True, default=uuid.uuid4, unique=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=True)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    joined_at = Column(default=datetime.now(), nullable=False)

    def hash_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)
    
    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)