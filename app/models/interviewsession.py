from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from app.db.base import Base
from datetime import datetime

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    guest_user_id = Column(String, ForeignKey("guest_users.id"), nullable=True)
    scheduled_at = Column(DateTime, default=datetime.utcnow)
    status = Column(String, default="scheduled")
    current_question_index = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)

    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    user = relationship("User", back_populates="interview_sessions")
    guest_user = relationship("GuestUser", back_populates="interview_sessions")
    questions = relationship("InterviewQuestion", back_populates="session")
    answers = relationship("InterviewAnswer", back_populates="session")
    evaluation = relationship(
        "InterviewEvaluation",
        back_populates="session",
        uselist=False
    ) 