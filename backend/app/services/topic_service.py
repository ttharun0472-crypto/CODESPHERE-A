from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.topic import Topic
from app.models.lesson import Lesson
from app.models.question import Question
from app.models.question_progress import QuestionProgress
from app.schemas.topic_schema import TopicCreate, TopicUpdate


# =========================
# CREATE TOPIC
# =========================

def _topics_for_lesson(
    db: Session,
    lesson_id: int,
    exclude_topic_id: int | None = None
) -> list[Topic]:
    query = db.query(Topic).filter(Topic.lesson_id == lesson_id)
    if exclude_topic_id is not None:
        query = query.filter(Topic.id != exclude_topic_id)
    return query.order_by(Topic.topic_number, Topic.id).all()


def _assign_topic_order(topics: list[Topic]) -> None:
    for number, topic in enumerate(topics, start=1):
        topic.topic_number = number


def create_topic(topic_data: TopicCreate, db: Session) -> Topic:
    lesson = db.query(Lesson).filter(Lesson.id == topic_data.lesson_id).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    title = topic_data.title.strip()
    existing_topic = db.query(Topic).filter(
        Topic.lesson_id == lesson.id,
        func.lower(func.trim(Topic.title)) == title.lower()
    ).first()
    if existing_topic is not None:
        return existing_topic

    topics = _topics_for_lesson(db, lesson.id)
    requested_number = topic_data.topic_number
    insert_at = (
        len(topics)
        if requested_number is None
        else min(requested_number - 1, len(topics))
    )

    topic = Topic(
        lesson_id=topic_data.lesson_id,
        title=title,
        description=topic_data.description,
    )
    topics.insert(insert_at, topic)
    db.add(topic)
    _assign_topic_order(topics)
    db.commit()
    db.refresh(topic)
    return topic


# =========================
# GET TOPICS FOR A LESSON
# =========================

def get_topics_for_lesson(lesson_id: int, db: Session) -> list[Topic]:
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    return (
        db.query(Topic)
        .filter(Topic.lesson_id == lesson_id)
        .order_by(Topic.topic_number, Topic.id)
        .all()
    )


# =========================
# GET SINGLE TOPIC
# =========================

def get_topic(topic_id: int, db: Session) -> Topic:
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")
    return topic


# =========================
# GET TOPIC WITH COUNTS FOR A USER
# =========================

def get_topics_with_counts(lesson_id: int, user_id: int, db: Session) -> list[dict]:
    topics = get_topics_for_lesson(lesson_id, db)
    result = []

    for topic in topics:
        total_q = (
            db.query(Question)
            .filter(Question.topic_id == topic.id)
            .count()
        )

        completed_q = (
            db.query(QuestionProgress)
            .join(Question, QuestionProgress.question_id == Question.id)
            .filter(
                Question.topic_id == topic.id,
                QuestionProgress.user_id == user_id,
                QuestionProgress.completed == True
            )
            .count()
        )

        result.append({
            "id": topic.id,
            "lesson_id": topic.lesson_id,
            "title": topic.title,
            "description": topic.description,
            "topic_number": topic.topic_number,
            "total_questions": total_q,
            "completed_questions": completed_q
        })

    return result


# =========================
# UPDATE TOPIC
# =========================

def update_topic(topic_id: int, topic_data: TopicUpdate, db: Session) -> Topic:
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    title = topic_data.title.strip()
    duplicate = db.query(Topic).filter(
        Topic.lesson_id == topic.lesson_id,
        Topic.id != topic.id,
        func.lower(func.trim(Topic.title)) == title.lower()
    ).first()
    if duplicate is not None:
        raise HTTPException(
            status_code=409,
            detail="A topic with this title already exists in the lesson"
        )

    if topic_data.topic_number is not None:
        topics = _topics_for_lesson(
            db,
            topic.lesson_id,
            exclude_topic_id=topic.id
        )
        insert_at = min(topic_data.topic_number - 1, len(topics))
        topics.insert(insert_at, topic)
        _assign_topic_order(topics)

    topic.title = title
    topic.description = topic_data.description

    db.commit()
    db.refresh(topic)
    return topic


# =========================
# DELETE TOPIC
# =========================

def delete_topic(topic_id: int, db: Session) -> dict:
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    db.delete(topic)
    db.commit()
    return {"message": "Topic deleted successfully"}


# =========================
# GET NEXT TOPIC IN LESSON
# =========================

def get_next_topic(topic_id: int, db: Session) -> Topic | None:
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    next_topic = (
        db.query(Topic)
        .filter(
            Topic.lesson_id == topic.lesson_id,
            Topic.topic_number > topic.topic_number
        )
        .order_by(Topic.topic_number, Topic.id)
        .first()
    )

    return next_topic


# =========================
# GET LESSON TOPIC COMPLETION
# =========================

def get_lesson_topic_completion(lesson_id: int, user_id: int, db: Session) -> dict:
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    topics = (
        db.query(Topic)
        .filter(Topic.lesson_id == lesson_id)
        .order_by(Topic.topic_number, Topic.id)
        .all()
    )

    total_topics = len(topics)
    completed_topic_ids = []

    for topic in topics:
        total_q = (
            db.query(Question)
            .filter(Question.topic_id == topic.id)
            .count()
        )

        if total_q == 0:
            continue

        completed_q = (
            db.query(QuestionProgress)
            .join(Question, QuestionProgress.question_id == Question.id)
            .filter(
                Question.topic_id == topic.id,
                QuestionProgress.user_id == user_id,
                QuestionProgress.completed == True
            )
            .count()
        )

        if completed_q >= total_q:
            completed_topic_ids.append(topic.id)

    return {
        "lesson_id": lesson_id,
        "total_topics": total_topics,
        "completed_topics": len(completed_topic_ids),
        "completed_topic_ids": completed_topic_ids,
        "is_complete": total_topics > 0 and len(completed_topic_ids) == total_topics
    }
