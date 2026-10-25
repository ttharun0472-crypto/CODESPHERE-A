from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.question import Question
from app.models.question_progress import QuestionProgress
from app.models.topic import Topic
from app.models.progress import Progress
from app.models.lesson import Lesson
from app.schemas.question_schema import QuestionCreate, QuestionUpdate


# =========================
# CREATE QUESTION
# =========================

def _questions_for_topic(
    db: Session,
    topic_id: int,
    exclude_question_id: int | None = None
) -> list[Question]:
    query = db.query(Question).filter(Question.topic_id == topic_id)
    if exclude_question_id is not None:
        query = query.filter(Question.id != exclude_question_id)
    return query.order_by(Question.question_number, Question.id).all()


def _assign_question_order(questions: list[Question]) -> None:
    for number, question in enumerate(questions, start=1):
        question.question_number = number


def create_question(question_data: QuestionCreate, db: Session) -> Question:
    topic = db.query(Topic).filter(Topic.id == question_data.topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    question_text = question_data.question.strip()
    existing_question = db.query(Question).filter(
        Question.topic_id == topic.id,
        func.lower(func.trim(Question.question)) == question_text.lower()
    ).first()
    if existing_question is not None:
        return existing_question

    questions = _questions_for_topic(db, topic.id)
    requested_number = question_data.question_number
    insert_at = (
        len(questions)
        if requested_number is None
        else min(requested_number - 1, len(questions))
    )

    question = Question(
        topic_id=question_data.topic_id,
        question=question_text,
        quick_answer=question_data.quick_answer,
        explanation=question_data.explanation,
        real_world_example=question_data.real_world_example,
        code_example=question_data.code_example,
        expected_output=question_data.expected_output,
        flowchart=question_data.flowchart,
        key_points=question_data.key_points,
        remember_this=question_data.remember_this,
    )
    questions.insert(insert_at, question)
    db.add(question)
    _assign_question_order(questions)
    db.commit()
    db.refresh(question)
    return question


# =========================
# GET QUESTIONS FOR TOPIC
# =========================

def get_questions_for_topic(topic_id: int, db: Session) -> list[Question]:
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    return (
        db.query(Question)
        .filter(Question.topic_id == topic_id)
        .order_by(Question.question_number, Question.id)
        .all()
    )


# =========================
# GET SINGLE QUESTION
# =========================

def get_question(question_id: int, db: Session) -> Question:
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")
    return question


# =========================
# GET QUESTION WITH TOPIC VALIDATION
# =========================

def get_question_in_topic(question_id: int, topic_id: int, db: Session) -> Question:
    question = db.query(Question).filter(
        Question.id == question_id,
        Question.topic_id == topic_id
    ).first()
    if question is None:
        raise HTTPException(
            status_code=404,
            detail="Question not found in the specified topic"
        )
    return question


# =========================
# UPDATE QUESTION
# =========================

def update_question(question_id: int, question_data: QuestionUpdate, db: Session) -> Question:
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    question_text = question_data.question.strip()
    duplicate = db.query(Question).filter(
        Question.topic_id == question.topic_id,
        Question.id != question.id,
        func.lower(func.trim(Question.question)) == question_text.lower()
    ).first()
    if duplicate is not None:
        raise HTTPException(
            status_code=409,
            detail="This question already exists in the topic"
        )

    if question_data.question_number is not None:
        questions = _questions_for_topic(
            db,
            question.topic_id,
            exclude_question_id=question.id
        )
        insert_at = min(question_data.question_number - 1, len(questions))
        questions.insert(insert_at, question)
        _assign_question_order(questions)

    question.question = question_text
    question.quick_answer = question_data.quick_answer
    question.explanation = question_data.explanation
    question.real_world_example = question_data.real_world_example
    question.code_example = question_data.code_example
    question.expected_output = question_data.expected_output
    question.flowchart = question_data.flowchart
    question.key_points = question_data.key_points
    question.remember_this = question_data.remember_this

    db.commit()
    db.refresh(question)
    return question


# =========================
# DELETE QUESTION
# =========================

def delete_question(question_id: int, db: Session) -> dict:
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    db.delete(question)
    db.commit()
    return {"message": "Question deleted successfully"}


# =========================
# MARK QUESTION COMPLETE
# =========================

def mark_question_complete(user_id: int, question_id: int, db: Session) -> dict:
    # Validate question exists
    question = db.query(Question).filter(Question.id == question_id).first()
    if question is None:
        raise HTTPException(status_code=404, detail="Question not found")

    # Upsert question progress
    existing = db.query(QuestionProgress).filter(
        QuestionProgress.user_id == user_id,
        QuestionProgress.question_id == question_id
    ).first()

    if existing:
        if not existing.completed:
            existing.completed = True
            existing.completed_at = datetime.now(timezone.utc)
            db.commit()
            db.refresh(existing)
        return {
            "id": existing.id,
            "user_id": existing.user_id,
            "question_id": existing.question_id,
            "completed": existing.completed
        }
    else:
        record = QuestionProgress(
            user_id=user_id,
            question_id=question_id,
            completed=True,
            completed_at=datetime.now(timezone.utc)
        )
        db.add(record)
        db.commit()
        db.refresh(record)

        # Auto-sync lesson-level Progress table
        _sync_lesson_progress(user_id, question.topic_id, db)

        return {
            "id": record.id,
            "user_id": record.user_id,
            "question_id": record.question_id,
            "completed": record.completed
        }


# =========================
# GET COMPLETED QUESTIONS IN TOPIC
# =========================

def get_completed_question_ids_in_topic(user_id: int, topic_id: int, db: Session) -> list[int]:
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    records = (
        db.query(QuestionProgress)
        .join(Question, QuestionProgress.question_id == Question.id)
        .filter(
            Question.topic_id == topic_id,
            QuestionProgress.user_id == user_id,
            QuestionProgress.completed == True
        )
        .all()
    )

    return [r.question_id for r in records]


# =========================
# GET TOPIC COMPLETION
# =========================

def get_topic_completion(user_id: int, topic_id: int, db: Session) -> dict:
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        raise HTTPException(status_code=404, detail="Topic not found")

    total_q = (
        db.query(Question)
        .filter(Question.topic_id == topic_id)
        .count()
    )

    completed_q = (
        db.query(QuestionProgress)
        .join(Question, QuestionProgress.question_id == Question.id)
        .filter(
            Question.topic_id == topic_id,
            QuestionProgress.user_id == user_id,
            QuestionProgress.completed == True
        )
        .count()
    )

    percentage = (completed_q / total_q * 100) if total_q > 0 else 0.0

    return {
        "topic_id": topic_id,
        "total_questions": total_q,
        "completed_questions": completed_q,
        "completion_percentage": round(percentage, 2),
        "is_complete": total_q > 0 and completed_q >= total_q
    }


# =========================
# GET LESSON COMPLETION
# =========================

def get_lesson_completion(user_id: int, lesson_id: int, db: Session) -> dict:
    lesson = db.query(Lesson).filter(Lesson.id == lesson_id).first()
    if lesson is None:
        raise HTTPException(status_code=404, detail="Lesson not found")

    topics = (
        db.query(Topic)
        .filter(Topic.lesson_id == lesson_id)
        .all()
    )

    topic_ids = [t.id for t in topics]

    if not topic_ids:
        return {
            "lesson_id": lesson_id,
            "total_questions": 0,
            "completed_questions": 0,
            "completion_percentage": 0.0,
            "is_complete": False,
            "completed_topic_ids": [],
            "total_topics": 0,
            "completed_topics": 0
        }

    total_q = (
        db.query(Question)
        .filter(Question.topic_id.in_(topic_ids))
        .count()
    )

    completed_q = (
        db.query(QuestionProgress)
        .join(Question, QuestionProgress.question_id == Question.id)
        .filter(
            Question.topic_id.in_(topic_ids),
            QuestionProgress.user_id == user_id,
            QuestionProgress.completed == True
        )
        .count()
    )

    percentage = (completed_q / total_q * 100) if total_q > 0 else 0.0

    # Which topics are fully completed?
    completed_topic_ids = []
    for topic in topics:
        total_tq = (
            db.query(Question)
            .filter(Question.topic_id == topic.id)
            .count()
        )

        if total_tq == 0:
            continue

        completed_tq = (
            db.query(QuestionProgress)
            .join(Question, QuestionProgress.question_id == Question.id)
            .filter(
                Question.topic_id == topic.id,
                QuestionProgress.user_id == user_id,
                QuestionProgress.completed == True
            )
            .count()
        )

        if completed_tq >= total_tq:
            completed_topic_ids.append(topic.id)

    return {
        "lesson_id": lesson_id,
        "total_questions": total_q,
        "completed_questions": completed_q,
        "completion_percentage": round(percentage, 2),
        "is_complete": total_q > 0 and completed_q >= total_q,
        "completed_topic_ids": completed_topic_ids,
        "total_topics": len(topics),
        "completed_topics": len(completed_topic_ids)
    }


# =========================
# PRIVATE: SYNC LESSON PROGRESS
# =========================

def _sync_lesson_progress(user_id: int, topic_id: int, db: Session):
    """
    After a question is marked complete, recalculate and update the
    existing lesson-level Progress record so existing analytics stay accurate.
    """
    topic = db.query(Topic).filter(Topic.id == topic_id).first()
    if topic is None:
        return

    lesson_id = topic.lesson_id

    topics = db.query(Topic).filter(Topic.lesson_id == lesson_id).all()
    topic_ids = [t.id for t in topics]

    if not topic_ids:
        return

    total_q = (
        db.query(Question)
        .filter(Question.topic_id.in_(topic_ids))
        .count()
    )

    completed_q = (
        db.query(QuestionProgress)
        .join(Question, QuestionProgress.question_id == Question.id)
        .filter(
            Question.topic_id.in_(topic_ids),
            QuestionProgress.user_id == user_id,
            QuestionProgress.completed == True
        )
        .count()
    )

    percentage = (completed_q / total_q * 100) if total_q > 0 else 0.0

    # Upsert into existing progress table
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.lesson_id == lesson_id
    ).first()

    if progress:
        progress.completion_percentage = round(percentage, 2)
    else:
        progress = Progress(
            user_id=user_id,
            lesson_id=lesson_id,
            completion_percentage=round(percentage, 2)
        )
        db.add(progress)

    db.commit()
