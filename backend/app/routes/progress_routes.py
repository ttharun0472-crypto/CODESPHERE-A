from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies import get_current_user
from app.models import User

from app.schemas.progress_schema import (
    ProgressCreate,
    ProgressResponse
)

from app.services.progress_service import (
    update_progress,
    get_user_progress,
    get_lesson_progress,
    get_completed_courses_for_interview,
)


router = APIRouter(
    prefix="/progress",
    tags=["Progress"]
)


# =========================
# UPDATE PROGRESS
# =========================

@router.post(
    "",
    response_model=ProgressResponse
)
def update_lesson_progress(
    progress: ProgressCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return update_progress(
        current_user.id,
        progress.lesson_id,
        progress.completion_percentage,
        db
    )


# =========================
# GET ALL PROGRESS
# =========================

@router.get("/completed-courses")
def completed_courses_for_interview(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_completed_courses_for_interview(current_user.id, db)


@router.get(
    "",
    response_model=list[ProgressResponse]
)
def get_progress(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_user_progress(
        current_user.id,
        db
    )


# =========================
# GET LESSON PROGRESS
# =========================

@router.get(
    "/lesson/{lesson_id}",
    response_model=ProgressResponse
)
def get_lesson_progress_api(
    lesson_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return get_lesson_progress(
        current_user.id,
        lesson_id,
        db
    )