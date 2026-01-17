from sqlalchemy import (
    Column,
    Integer,
    String,
    ForeignKey,
    DateTime,
    CheckConstraint
)
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import Base
from datetime import datetime
import uuid

class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)

    # Registered user (optional)
    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=True
    )

    # Guest user (optional)
    guest_user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("guest_users.id", ondelete="CASCADE"),
        nullable=True
    )

    status = Column(String, default="IN_PROGRESS")
    current_question_index = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)

    scheduled_at = Column(DateTime, default=datetime.utcnow)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    # 🔒 Ensure only ONE owner exists
    __table_args__ = (
        CheckConstraint(
            "(user_id IS NOT NULL AND guest_user_id IS NULL) OR "
            "(user_id IS NULL AND guest_user_id IS NOT NULL)",
            name="check_single_owner"
        ),
    )

    # Relationships
    user = relationship(
        "User",
        back_populates="interview_sessions",
        passive_deletes=True
    )

    guest_user = relationship(
        "GuestUser",
        back_populates="interview_sessions",
        passive_deletes=True
    )

    questions = relationship(
        "InterviewQuestion",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    answers = relationship(
        "InterviewAnswer",
        back_populates="session",
        cascade="all, delete-orphan"
    )

    evaluation = relationship(
        "InterviewEvaluation",
        back_populates="session",
        uselist=False,
        cascade="all, delete-orphan"
    )
