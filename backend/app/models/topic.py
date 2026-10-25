from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.config.database import Base


class Topic(Base):

    __tablename__ = "topics"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    lesson_id = Column(
        Integer,
        ForeignKey("lessons.id", ondelete="CASCADE"),
        nullable=False
    )

    title = Column(
        String(150),
        nullable=False
    )

    description = Column(
        Text,
        nullable=True
    )

    topic_number = Column(
        Integer,
        default=1,
        nullable=False
    )

    # Relationships
    lesson = relationship(
        "Lesson",
        back_populates="topics"
    )

    questions = relationship(
        "Question",
        back_populates="topic",
        cascade="all, delete-orphan",
        order_by="Question.question_number"
    )
