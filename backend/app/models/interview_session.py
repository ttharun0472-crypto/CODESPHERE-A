from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String,
)

from app.config.database import Base


class InterviewSession(Base):
    __tablename__ = "interview_sessions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    category = Column(String(30), nullable=False)
    course_id = Column(
        Integer,
        ForeignKey("courses.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    course_title = Column(String(150), nullable=True)
    skill = Column(String(100), nullable=True)
    difficulty = Column(String(20), nullable=False)
    duration_minutes = Column(Integer, nullable=True)
    total_questions = Column(Integer, nullable=False)
    questions = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="in_progress")
    overall_score = Column(Float, nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
    )
    completed_at = Column(DateTime, nullable=True)
