from sqlalchemy import Column, Integer, Text, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from datetime import datetime
from app.db.base import Base

class InterviewEvaluation(Base):
    __tablename__ = "interview_evaluations"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(
        Integer,
        ForeignKey("interview_sessions.id"),
        unique=True
    )

    total_score = Column(Float)  # e.g. 7.5 / 10
    feedback = Column(Text)      # AI analysis of thinking

    created_at = Column(DateTime, default=datetime.utcnow)

    session = relationship("InterviewSession", back_populates="evaluation")
