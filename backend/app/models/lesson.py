from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.config.database import Base


class Lesson(Base):

    __tablename__ = "lessons"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    course_id = Column(
        Integer,
        ForeignKey("courses.id"),
        nullable=False
    )

    title = Column(
        String(150),
        nullable=False
    )

    notes = Column(
        Text,
        nullable=True
    )

    important_concepts = Column(
        Text,
        nullable=True
    )

    youtube_url = Column(
        String(500),
        nullable=True
    )

    lesson_order = Column(
        Integer,
        default=1,
        nullable=False
    )

    course = relationship(
        "Course",
        back_populates="lessons"
    )

    topics = relationship(
        "Topic",
        back_populates="lesson",
        cascade="all, delete-orphan",
        order_by="Topic.topic_number"
    )