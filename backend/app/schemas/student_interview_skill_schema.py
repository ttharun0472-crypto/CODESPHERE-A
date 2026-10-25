from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class StudentInterviewSkillCreate(BaseModel):
    skill_name: str = Field(
        ...,
        min_length=1,
        max_length=100,
        description="Additional skill selected by the student",
    )


class StudentInterviewSkillResponse(BaseModel):
    id: int
    user_id: int
    skill_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)