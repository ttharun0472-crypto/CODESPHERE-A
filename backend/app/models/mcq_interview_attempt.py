from datetime import datetime, timezone

from sqlalchemy import (
    JSON,
    Column,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    String,
    text,
)

from app.config.database import Base


class MCQInterviewAttempt(Base):
    __tablename__ = "mcq_interview_attempts"
    __table_args__ = (
        CheckConstraint("total_questions > 0", name="ck_mcq_attempt_positive_question_count"),
        Index(
            "uq_mcq_interview_attempts_one_active_per_user",
            "user_id",
            unique=True,
            postgresql_where=text("status = 'in_progress'"),
            sqlite_where=text("status = 'in_progress'"),
        ),
        Index("ix_mcq_interview_attempts_user_completed", "user_id", "completed_at"),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    subject = Column(String(60), nullable=False)
    topic = Column(String(150), nullable=False)
    difficulty = Column(String(20), nullable=False)
    total_questions = Column(Integer, nullable=False)
    questions = Column(JSON, nullable=False)
    status = Column(String(20), nullable=False, default="in_progress", index=True)
    result = Column(JSON, nullable=True)
    created_at = Column(
        DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        server_default=text("CURRENT_TIMESTAMP"),
    )
    completed_at = Column(DateTime, nullable=True)
