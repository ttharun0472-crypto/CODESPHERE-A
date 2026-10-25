from typing import Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.mcq_interview_schema import MCQAttemptCreate, MCQAttemptSubmit
from app.services.mcq_interview_service import (
    create_attempt,
    get_active_attempt,
    get_attempt_history,
    get_attempt_progress,
    get_owned_attempt_response,
    submit_attempt,
)
from app.services.mcq_question_provider import (
    DIFFICULTIES,
    QUESTION_COUNTS,
    rule_based_provider,
)

router = APIRouter(
    prefix="/interview/mcq",
    tags=["MCQ Interviews"],
)


@router.get("/options", dependencies=[Depends(get_current_user)])
def mcq_options() -> dict[str, Any]:
    return {
        "subjects": rule_based_provider.subjects(),
        "difficulties": list(DIFFICULTIES),
        "question_counts": list(QUESTION_COUNTS),
    }


@router.get("/attempts/active")
def active_mcq_attempt(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any] | None:
    return get_active_attempt(current_user.id, db)


@router.post(
    "/attempts",
    status_code=status.HTTP_201_CREATED,
)
def start_mcq_attempt(
    request: MCQAttemptCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return create_attempt(current_user.id, request, db)


@router.get("/history")
def mcq_interview_history(
    limit: int = Query(default=50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> list[dict[str, Any]]:
    return get_attempt_history(current_user.id, db, limit)


@router.get("/progress")
def mcq_interview_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return get_attempt_progress(current_user.id, db)


@router.get("/attempts/{attempt_id}")
def mcq_attempt(
    attempt_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return get_owned_attempt_response(attempt_id, current_user.id, db)


@router.post("/attempts/{attempt_id}/submit")
def submit_mcq_attempt(
    attempt_id: int,
    request: MCQAttemptSubmit,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict[str, Any]:
    return submit_attempt(attempt_id, current_user.id, request, db)
