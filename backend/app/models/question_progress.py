from datetime import datetime

from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from app.config.database import Base


class QuestionProgress(Base):

    __tablename__ = "question_progress"

    __table_args__ = (
        # Each student can have at most one progress record per question
        UniqueConstraint(
            "user_id",
            "question_id",
            name="uq_user_question"
        ),
    )

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )

    question_id = Column(
        Integer,
        ForeignKey("questions.id", ondelete="CASCADE"),
        nullable=False
    )

    completed = Column(
        Boolean,
        default=False,
        nullable=False
    )

    completed_at = Column(
        DateTime,
        nullable=True
    )

    # Relationships
    user = relationship("User")

    question = relationship(
        "Question",
        back_populates="progress_records"
    )
