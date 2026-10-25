from typing import Optional
from pydantic import BaseModel, Field


# =========================
# CREATE
# =========================

class TopicCreate(BaseModel):
    lesson_id: int
    title: str = Field(min_length=2, max_length=150)
    description: Optional[str] = None
    topic_number: Optional[int] = Field(default=None, ge=1)


# =========================
# UPDATE
# =========================

class TopicUpdate(BaseModel):
    title: str = Field(min_length=2, max_length=150)
    description: Optional[str] = None
    topic_number: Optional[int] = Field(default=None, ge=1)


# =========================
# RESPONSE
# =========================

class TopicResponse(BaseModel):
    id: int
    lesson_id: int
    title: str
    description: Optional[str]
    topic_number: int

    class Config:
        from_attributes = True


# =========================
# TOPIC WITH QUESTION COUNT
# =========================

class TopicWithCountResponse(BaseModel):
    id: int
    lesson_id: int
    title: str
    description: Optional[str]
    topic_number: int
    total_questions: int
    completed_questions: int

    class Config:
        from_attributes = True
