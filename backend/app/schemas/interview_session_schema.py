from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


InterviewCategory = Literal["technical", "hr", "communication", "mixed"]
InterviewDifficulty = Literal["easy", "medium", "hard"]


class InterviewSessionCreate(BaseModel):
    category: InterviewCategory = "technical"
    course_id: int | None = Field(default=None, gt=0)
    difficulty: InterviewDifficulty = "medium"
    number_of_questions: int = Field(default=5, ge=1, le=20)
    duration_minutes: int | None = Field(default=None, ge=5, le=180)

    @model_validator(mode="after")
    def require_course_for_technical_interviews(self):
        if self.category in {"technical", "mixed"} and self.course_id is None:
            raise ValueError("Select a learning course for technical or mixed interviews.")
        return self


class InterviewAnswerCreate(BaseModel):
    answer: str = Field(min_length=1, max_length=10000)

    @field_validator("answer")
    @classmethod
    def clean_answer(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Answer cannot be empty.")
        return cleaned


class InterviewEvaluation(BaseModel):
    score: float = Field(ge=0, le=100)
    strengths: list[str] = Field(min_length=1, max_length=8)
    missing_concepts: list[str] = Field(max_length=8)
    areas_for_improvement: list[str] = Field(min_length=1, max_length=8)
    model_answer: str = Field(min_length=1, max_length=5000)
    next_attempt_suggestion: str = Field(min_length=1, max_length=1000)
    criterion_scores: dict[str, float] = Field(min_length=1, max_length=6)

    @field_validator("criterion_scores")
    @classmethod
    def validate_criterion_scores(
        cls, value: dict[str, float]
    ) -> dict[str, float]:
        if any(not 0 <= score <= 100 for score in value.values()):
            raise ValueError("Criterion scores must be between 0 and 100.")
        return value


class InterviewQuestionResult(BaseModel):
    question_index: int
    course_id: int | None = None
    question: str
    category: str
    difficulty: str
    answer: str | None = None
    evaluation: InterviewEvaluation | None = None
    expected_answer: str | None = None


class InterviewSessionResponse(BaseModel):
    id: int
    category: str
    course_id: int | None = None
    course_title: str | None = None
    skill: str | None
    difficulty: str
    duration_minutes: int | None
    total_questions: int
    questions: list[InterviewQuestionResult]
    status: Literal["in_progress", "completed"]
    question_source: Literal["ai", "default"] = "default"
    overall_score: float | None
    created_at: datetime
    completed_at: datetime | None

    model_config = ConfigDict(from_attributes=True)


class InterviewSessionSummary(BaseModel):
    total_completed: int
    average_score: float | None
    recent_sessions: list[InterviewSessionResponse]
