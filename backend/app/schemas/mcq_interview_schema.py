from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


MCQDifficulty = Literal["Beginner", "Intermediate", "Advanced"]
MCQQuestionCount = Literal[5, 10, 15, 20]


class MCQAttemptCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    subject: str = Field(min_length=1, max_length=60)
    topic: str = Field(min_length=1, max_length=150)
    difficulty: MCQDifficulty
    number_of_questions: MCQQuestionCount


class MCQAnswerSubmission(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question_id: str = Field(min_length=1, max_length=200)
    option_id: str = Field(min_length=1, max_length=200)


class MCQAttemptSubmit(BaseModel):
    model_config = ConfigDict(extra="forbid")

    answers: list[MCQAnswerSubmission] = Field(max_length=20)
