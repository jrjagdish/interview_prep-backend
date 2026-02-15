from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, CheckConstraint, Text, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
import uuid
from sqlalchemy import CheckConstraint

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=True)
    guest_user_id = Column(UUID(as_uuid=True), ForeignKey("guest_users.id", ondelete="CASCADE"), nullable=True)
    admin_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)

    title = Column(String, nullable=False) # e.g. "React Developer Mock Interview"
    status = Column(String, default="IN_PROGRESS") # IN_PROGRESS, COMPLETED, CANCELLED
    current_question_index = Column(Integer, default=0)
    
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "(user_id IS NOT NULL AND guest_user_id IS NULL) OR (user_id IS NULL AND guest_user_id IS NOT NULL)",
            name="check_single_owner",
        ),
    )

    # Relationships
    user = relationship("User", foreign_keys=[user_id], back_populates="interview_sessions")
    admin = relationship("User", foreign_keys=[admin_id], back_populates="admin_sessions")
    guest_user = relationship("GuestUser", back_populates="interview_sessions")
    
    # The actual Q&A loop
    qa_history = relationship("InterviewQA", back_populates="session", cascade="all, delete-orphan")

class InterviewQA(Base):
    __tablename__ = "interview_qa"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(UUID(as_uuid=True), ForeignKey("interview_sessions.id", ondelete="CASCADE"))
    
    chat_history = Column(Text,nullable=False)
    ai_feedback = Column(Text, nullable=True) 
    score = Column(Integer, nullable=True) # 1-10 scale
    question_index = Column(Integer, nullable=False)
    
    created_at = Column(DateTime, server_default=func.now())

    session = relationship("InterviewSession", back_populates="qa_history")