from pydantic import BaseModel, Field


class LessonCreate(BaseModel):
    course_id: int
    title: str = Field(min_length=2, max_length=150)
    notes: str | None = None
    important_concepts: str | None = None
    lesson_order: int | None = Field(default=None, ge=1)
    youtube_url: str | None = Field(
        default=None,
        max_length=500
    )


class LessonUpdate(BaseModel):
    course_id: int | None = Field(default=None, ge=1)
    title: str = Field(min_length=2, max_length=150)
    notes: str | None = None
    important_concepts: str | None = None
    lesson_order: int | None = Field(default=None, ge=1)
    youtube_url: str | None = Field(
        default=None,
        max_length=500
    )


class LessonResponse(BaseModel):
    id: int
    course_id: int
    title: str
    notes: str | None
    important_concepts: str | None
    youtube_url: str | None
    lesson_order: int

    class Config:
        from_attributes = True