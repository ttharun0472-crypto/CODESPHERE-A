from typing import Optional
from pydantic import BaseModel, Field


# =========================
# CREATE
# =========================

class QuestionCreate(BaseModel):
    topic_id: int
    question: str = Field(min_length=2, max_length=500)
    quick_answer: Optional[str] = None
    explanation: Optional[str] = None
    real_world_example: Optional[str] = None
    code_example: Optional[str] = None
    expected_output: Optional[str] = None
    flowchart: Optional[str] = None
    key_points: Optional[str] = None
    remember_this: Optional[str] = None
    question_number: Optional[int] = Field(default=None, ge=1)


# =========================
# UPDATE
# =========================

class QuestionUpdate(BaseModel):
    question: str = Field(min_length=2, max_length=500)
    quick_answer: Optional[str] = None
    explanation: Optional[str] = None
    real_world_example: Optional[str] = None
    code_example: Optional[str] = None
    expected_output: Optional[str] = None
    flowchart: Optional[str] = None
    key_points: Optional[str] = None
    remember_this: Optional[str] = None
    question_number: Optional[int] = Field(default=None, ge=1)


# =========================
# RESPONSE
# =========================

class QuestionResponse(BaseModel):
    id: int
    topic_id: int
    question: str
    quick_answer: Optional[str]
    explanation: Optional[str]
    real_world_example: Optional[str]
    code_example: Optional[str]
    expected_output: Optional[str]
    flowchart: Optional[str]
    key_points: Optional[str]
    remember_this: Optional[str]
    question_number: int

    class Config:
        from_attributes = True


# =========================
# PROGRESS
# =========================

class QuestionProgressCreate(BaseModel):
    question_id: int


class QuestionProgressResponse(BaseModel):
    id: int
    user_id: int
    question_id: int
    completed: bool

    class Config:
        from_attributes = True


# =========================
# TOPIC COMPLETION
# =========================

class TopicCompletionResponse(BaseModel):
    topic_id: int
    total_questions: int
    completed_questions: int
    completion_percentage: float
    is_complete: bool


class LessonCompletionResponse(BaseModel):
    lesson_id: int
    total_questions: int
    completed_questions: int
    completion_percentage: float
    is_complete: bool
    completed_topic_ids: list[int]
    total_topics: int
    completed_topics: int
