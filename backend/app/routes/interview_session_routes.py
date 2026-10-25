from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.interview_session_schema import (
    InterviewAnswerCreate,
    InterviewCategory,
    InterviewDifficulty,
    InterviewSessionCreate,
    InterviewSessionResponse,
    InterviewSessionSummary,
)
from app.services.interview_session_service import (
    complete_session,
    create_session,
    get_active_session,
    get_completed_sessions,
    get_owned_session,
    get_session_summary,
    serialize_session,
    submit_answer,
)
from app.services.interview_question_bank import get_available_questions

router = APIRouter(
    prefix="/interview/sessions",
    tags=["Interview Sessions"],
)


@router.post(
    "",
    response_model=InterviewSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
def start_interview(
    request: InterviewSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return create_session(current_user.id, request, db)


@router.get(
    "/summary",
    response_model=InterviewSessionSummary,
)
def interview_summary(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_session_summary(current_user.id, db)


@router.get("/available-questions")
def available_interview_questions(
    course_id: int | None = Query(default=None, gt=0),
    category: InterviewCategory = "technical",
    difficulty: InterviewDifficulty = "medium",
    _current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_available_questions(course_id, category, difficulty, db)


@router.get(
    "/active",
    response_model=InterviewSessionResponse | None,
)
def active_interview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_active_session(current_user.id, db)


@router.get(
    "",
    response_model=list[InterviewSessionResponse],
)
def interview_history(
    limit: int = Query(default=20, ge=1, le=50),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return get_completed_sessions(current_user.id, db, limit=limit)


@router.get(
    "/{session_id}",
    response_model=InterviewSessionResponse,
)
def interview_result(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    session = get_owned_session(session_id, current_user.id, db)
    return serialize_session(session)


@router.post(
    "/{session_id}/answers/{question_index}",
    response_model=InterviewSessionResponse,
)
def submit_interview_answer(
    session_id: int,
    question_index: int,
    request: InterviewAnswerCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return submit_answer(
        session_id=session_id,
        question_index=question_index,
        user_id=current_user.id,
        answer=request.answer,
        db=db,
    )


@router.post(
    "/{session_id}/complete",
    response_model=InterviewSessionResponse,
)
def finish_interview(
    session_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return complete_session(session_id, current_user.id, db)
