from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.orm import relationship
from app.db.base import Base

class InterviewQuestion(Base):
    __tablename__ = "interview_questions"

    id = Column(Integer, primary_key=True, index=True)

    session_id = Column(Integer, ForeignKey("interview_sessions.id"), nullable=False)

    question_index = Column(Integer, nullable=False)  # 0..N
    question_text = Column(Text, nullable=False)

    session = relationship("InterviewSession", back_populates="questions")
    answers = relationship("InterviewAnswer", back_populates="question")
