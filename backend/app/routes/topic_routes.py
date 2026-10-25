from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies import get_current_user
from app.middleware.admin_middleware import get_current_admin
from app.models import User

from app.schemas.topic_schema import (
    TopicCreate,
    TopicUpdate,
    TopicResponse,
    TopicWithCountResponse
)

from app.services.topic_service import (
    create_topic,
    get_topic,
    get_topics_for_lesson,
    get_topics_with_counts,
    update_topic,
    delete_topic,
    get_next_topic,
    get_lesson_topic_completion
)


router = APIRouter(
    prefix="/topics",
    tags=["Topics"]
)


# =========================
# GET TOPICS FOR A LESSON (Student)
# Returns topics with completion counts for the authenticated student
# =========================

@router.get(
    "/lesson/{lesson_id}",
    response_model=list[TopicWithCountResponse]
)
def list_topics_for_lesson(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_topics_with_counts(lesson_id, current_user.id, db)


# =========================
# GET TOPICS FOR A LESSON (Admin — plain list)
# =========================

@router.get(
    "/admin/lesson/{lesson_id}",
    response_model=list[TopicResponse]
)
def admin_list_topics(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return get_topics_for_lesson(lesson_id, db)


# =========================
# GET SINGLE TOPIC
# =========================

@router.get(
    "/{topic_id}",
    response_model=TopicResponse
)
def single_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_topic(topic_id, db)


# =========================
# GET NEXT TOPIC IN LESSON
# =========================

@router.get(
    "/{topic_id}/next",
    response_model=TopicResponse | None
)
def next_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_next_topic(topic_id, db)


# =========================
# GET LESSON TOPIC COMPLETION (Student)
# =========================

@router.get(
    "/lesson/{lesson_id}/completion"
)
def lesson_topic_completion(
    lesson_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    return get_lesson_topic_completion(lesson_id, current_user.id, db)


# =========================
# CREATE TOPIC (Admin)
# =========================

@router.post(
    "",
    response_model=TopicResponse
)
def add_topic(
    topic: TopicCreate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return create_topic(topic, db)


# =========================
# UPDATE TOPIC (Admin)
# =========================

@router.put(
    "/{topic_id}",
    response_model=TopicResponse
)
def edit_topic(
    topic_id: int,
    topic_data: TopicUpdate,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return update_topic(topic_id, topic_data, db)


# =========================
# DELETE TOPIC (Admin)
# =========================

@router.delete("/{topic_id}")
def remove_topic(
    topic_id: int,
    db: Session = Depends(get_db),
    current_admin: User = Depends(get_current_admin)
):
    return delete_topic(topic_id, db)
