from datetime import datetime, timezone

from sqlalchemy import (
    Column,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import relationship

from app.config.database import Base


class StudentInterviewSkill(Base):
    __tablename__ = "student_interview_skills"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    skill_name = Column(String(100), nullable=False)

    created_at = Column(
        DateTime,
        default=lambda: datetime.now(timezone.utc).replace(tzinfo=None),
        nullable=False,
    )

    user = relationship("User")

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "skill_name",
            name="uq_student_interview_skill",
        ),
    )