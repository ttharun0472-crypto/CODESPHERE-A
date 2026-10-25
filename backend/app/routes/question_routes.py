from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies import get_current_user
from app.middleware.admin_middleware import get_current_admin
from app.models import User

from app.schemas.question_schema import (
    QuestionCreate,
    QuestionUpdate,
    QuestionResponse,
    QuestionProgressCreate,
    QuestionProgressResponse,
    TopicCompletionResponse,
    LessonCompletionResponse
)

from app.services.question_service import (
    create_question,
    get_question,
    get_questions_for_topic,
    get_question_in_topic,
    update_question,
    delete_question,
    mark_question_complete,
    get_completed_question_ids_in_topic,
    get_topic_completion,
    get_lesson_completion
)


router = APIRouter(
    prefix="/questions",
    tags=["Questions"]
)


# =========================
# GET QUESTIONS FOR TOPIC (Student)
# =========================

@router.get(
    "/topic/{topic_id}",
    response_model=list[QuestionResponse]
)
def list_questions_for_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_questions_for_topic(topic_id, db)


# =========================
# GET SINGLE QUESTION (Student)
# =========================

@router.get(
    "/{question_id}",
    response_model=QuestionResponse
)
def single_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_question(question_id, db)


# =========================
# MARK QUESTION COMPLETE (Student)
# =========================

@router.post("/progress/complete")
def complete_question(
    body: QuestionProgressCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return mark_question_complete(current_user.id, body.question_id, db)


# =========================
# GET COMPLETED QUESTION IDs IN TOPIC (Student)
# =========================

@router.get("/progress/topic/{topic_id}")
def completed_in_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    ids = get_completed_question_ids_in_topic(current_user.id, topic_id, db)
    return {"completed_question_ids": ids}


# =========================
# GET TOPIC COMPLETION (Student)
# =========================

@router.get(
    "/completion/topic/{topic_id}",
    response_model=TopicCompletionResponse
)
def topic_completion(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_topic_completion(current_user.id, topic_id, db)


# =========================
# GET LESSON COMPLETION (Student)
# =========================

@router.get(
    "/completion/lesson/{lesson_id}",
    response_model=LessonCompletionResponse
)
def lesson_completion(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_lesson_completion(current_user.id, lesson_id, db)


# =========================
# CREATE QUESTION (Admin)
# =========================

@router.post(
    "",
    response_model=QuestionResponse
)
def add_question(
    question: QuestionCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return create_question(question, db)


# =========================
# UPDATE QUESTION (Admin)
# =========================

@router.put(
    "/{question_id}",
    response_model=QuestionResponse
)
def edit_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return update_question(question_id, question_data, db)


# =========================
# DELETE QUESTION (Admin)
# =========================

@router.delete("/{question_id}")
def remove_question(
    question_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return delete_question(question_id, db)
