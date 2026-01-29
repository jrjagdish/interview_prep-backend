from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, DateTime, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    google_id = Column(String, unique=True, nullable=True) # For OAuth
    role = Column(String, default="user") # user, admin, b2b_manager
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime, server_default=func.now())

    # Relationships
    profile = relationship("Profile", back_populates="user", uselist=False, cascade="all, delete-orphan")
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

class Profile(Base):
    __tablename__ = "profiles"

    id = Column(Integer, primary_key=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    skills = Column(Text, nullable=True) # Store as comma-separated or JSON
    is_paid_user = Column(Boolean, default=False)
    interview_credits = Column(Integer, default=3) # B2C monetization
    resume_url = Column(String, nullable=True)
    
    user = relationship("User", back_populates="profile")

class GuestUser(Base):
    __tablename__ = "guest_users"
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String, nullable=False)
    email = Column(String, index=True, nullable=False)
    pdf_url = Column(String, nullable=False)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    joined_at = Column(DateTime, server_default=func.now())

    interview_sessions = relationship("InterviewSession", back_populates="guest_user")