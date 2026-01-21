from sqlalchemy import DateTime, ForeignKey, Integer, String, Boolean, Column
from app.db.base import Base
import uuid
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from passlib.context import CryptContext
from datetime import datetime

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String,nullable=True)
    hashed_password = Column(String, nullable=True)
    role = Column(String, default="user")
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    interview_sessions = relationship(
        "InterviewSession",
        foreign_keys="InterviewSession.user_id",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    admin_sessions = relationship(
        "InterviewSession",
        foreign_keys="InterviewSession.admin_id",
        back_populates="admin",
        cascade="all, delete-orphan",
    )

    def hash_password(self, password: str):
        self.hashed_password = pwd_context.hash(password)

    def verify_password(self, password: str) -> bool:
        return pwd_context.verify(password, self.hashed_password)


class GuestUser(Base):
    __tablename__ = "guest_users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    pdf_url = Column(String, nullable=False)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    cloudinary_public_id = Column(String, nullable=True)
    joined_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    interview_sessions = relationship(
        "InterviewSession",
        back_populates="guest_user",
        cascade="all, delete-orphan",
    )

    admin = relationship(
        "User",
        foreign_keys=[admin_id],
    )

    def __str__(self):
        return f"GuestUser(username={self.username}, email={self.email})"
