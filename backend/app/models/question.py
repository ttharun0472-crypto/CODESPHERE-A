from sqlalchemy import Column, Integer, String, Text, ForeignKey
from sqlalchemy.orm import relationship

from app.config.database import Base


class Question(Base):

    __tablename__ = "questions"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    topic_id = Column(
        Integer,
        ForeignKey("topics.id", ondelete="CASCADE"),
        nullable=False
    )

    # Question title / stem
    question = Column(
        String(500),
        nullable=False
    )

    # Quick one-line answer
    quick_answer = Column(
        Text,
        nullable=True
    )

    # Full detailed explanation
    explanation = Column(
        Text,
        nullable=True
    )

    # Real-world usage example (text)
    real_world_example = Column(
        Text,
        nullable=True
    )

    # Code snippet
    code_example = Column(
        Text,
        nullable=True
    )

    # Expected output of code_example
    expected_output = Column(
        Text,
        nullable=True
    )

    # Optional flowchart / diagram (plain-text ASCII or description)
    flowchart = Column(
        Text,
        nullable=True
    )

    # Bullet-point key facts (newline-separated)
    key_points = Column(
        Text,
        nullable=True
    )

    # Short "remember this" summary
    remember_this = Column(
        Text,
        nullable=True
    )

    # Sort order within the topic
    question_number = Column(
        Integer,
        default=1,
        nullable=False
    )

    # Relationships
    topic = relationship(
        "Topic",
        back_populates="questions"
    )

    progress_records = relationship(
        "QuestionProgress",
        back_populates="question",
        cascade="all, delete-orphan"
    )
