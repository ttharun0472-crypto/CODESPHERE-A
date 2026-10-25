from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import MCQInterviewAttempt
from app.schemas.mcq_interview_schema import MCQAttemptCreate, MCQAttemptSubmit
from app.services.mcq_question_provider import rule_based_provider

ATTEMPT_TTL = timedelta(hours=2)
GRADE_THRESHOLDS = ((80, "A"), (60, "B"), (40, "C"))


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def grade_percentage(percentage: float) -> str:
    """Grade raw percentage: A >= 80, B >= 60, C >= 40, and D below 40."""
    for threshold, grade in GRADE_THRESHOLDS:
        if percentage >= threshold:
            return grade
    return "D"


def serialize_attempt(attempt: MCQInterviewAttempt) -> dict[str, Any]:
    response: dict[str, Any] = {
        "id": attempt.id,
        "subject": attempt.subject,
        "topic": attempt.topic,
        "difficulty": attempt.difficulty,
        "total_questions": attempt.total_questions,
        "status": attempt.status,
        "created_at": attempt.created_at,
        "expires_at": (
            attempt.created_at + ATTEMPT_TTL
            if attempt.status == "in_progress"
            else None
        ),
        "completed_at": attempt.completed_at,
    }
    if attempt.status == "completed":
        response["result"] = attempt.result
    else:
        response["questions"] = [
            {
                "id": question["id"],
                "subject": question["subject"],
                "topic": question["topic"],
                "difficulty": question["difficulty"],
                "question": question["question"],
                "options": question["options"],
            }
            for question in attempt.questions
        ]
    return response


def get_attempt(
    attempt_id: int, user_id: int, db: Session, *, lock: bool = False
) -> MCQInterviewAttempt:
    query = db.query(MCQInterviewAttempt).filter(
        MCQInterviewAttempt.id == attempt_id,
        MCQInterviewAttempt.user_id == user_id,
    )
    if lock:
        query = query.with_for_update()
    attempt = query.first()
    if attempt is None:
        raise HTTPException(status_code=404, detail="MCQ interview attempt not found.")
    return attempt


def create_attempt(
    user_id: int, request: MCQAttemptCreate, db: Session
) -> dict[str, Any]:
    questions = rule_based_provider.get_questions(
        request.subject,
        request.topic,
        request.difficulty,
        request.number_of_questions,
    )
    active = (
        db.query(MCQInterviewAttempt)
        .filter(
            MCQInterviewAttempt.user_id == user_id,
            MCQInterviewAttempt.status == "in_progress",
        )
        .first()
    )
    if active is not None:
        if _now() >= active.created_at + ATTEMPT_TTL:
            active.status = "expired"
            db.commit()
        else:
            raise HTTPException(
                status_code=409,
                detail="Resume or submit your active MCQ interview before starting another.",
            )

    attempt = MCQInterviewAttempt(
        user_id=user_id,
        subject=request.subject,
        topic=request.topic,
        difficulty=request.difficulty,
        total_questions=len(questions),
        questions=questions,
        status="in_progress",
    )
    try:
        db.add(attempt)
        db.commit()
        db.refresh(attempt)
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=409,
            detail="An MCQ interview was started in another request. Resume that attempt.",
        ) from exc
    return serialize_attempt(attempt)


def get_active_attempt(user_id: int, db: Session) -> dict[str, Any] | None:
    attempt = (
        db.query(MCQInterviewAttempt)
        .filter(
            MCQInterviewAttempt.user_id == user_id,
            MCQInterviewAttempt.status == "in_progress",
        )
        .order_by(MCQInterviewAttempt.created_at.desc())
        .first()
    )
    if attempt is None:
        return None
    if _now() >= attempt.created_at + ATTEMPT_TTL:
        attempt.status = "expired"
        db.commit()
        return None
    return serialize_attempt(attempt)


def get_owned_attempt_response(
    attempt_id: int, user_id: int, db: Session
) -> dict[str, Any]:
    attempt = get_attempt(attempt_id, user_id, db)
    if (
        attempt.status == "in_progress"
        and _now() >= attempt.created_at + ATTEMPT_TTL
    ):
        attempt.status = "expired"
        db.commit()
        raise HTTPException(
            status_code=410,
            detail="This MCQ interview has expired. Start a new interview.",
        )
    if attempt.status == "expired":
        raise HTTPException(
            status_code=410,
            detail="This MCQ interview has expired. Start a new interview.",
        )
    return serialize_attempt(attempt)


def submit_attempt(
    attempt_id: int,
    user_id: int,
    request: MCQAttemptSubmit,
    db: Session,
) -> dict[str, Any]:
    attempt = get_attempt(attempt_id, user_id, db, lock=True)
    if attempt.status == "completed":
        raise HTTPException(
            status_code=409,
            detail="This MCQ interview has already been submitted.",
        )
    if attempt.status == "expired" or _now() >= attempt.created_at + ATTEMPT_TTL:
        attempt.status = "expired"
        db.commit()
        raise HTTPException(
            status_code=410,
            detail="This MCQ interview has expired. Start a new interview.",
        )

    question_by_id = {question["id"]: question for question in attempt.questions}
    submitted_by_id: dict[str, str] = {}
    for answer in request.answers:
        if answer.question_id in submitted_by_id:
            raise HTTPException(
                status_code=422,
                detail="Each question may have at most one submitted answer.",
            )
        question = question_by_id.get(answer.question_id)
        if question is None:
            raise HTTPException(
                status_code=422,
                detail="An answer references a question outside this interview.",
            )
        valid_option_ids = {option["id"] for option in question["options"]}
        if answer.option_id not in valid_option_ids:
            raise HTTPException(
                status_code=422,
                detail="An answer references an invalid option for its question.",
            )
        submitted_by_id[answer.question_id] = answer.option_id

    reviewed_questions: list[dict[str, Any]] = []
    correct_answers = 0
    for question in attempt.questions:
        selected_option_id = submitted_by_id.get(question["id"])
        is_correct = (
            selected_option_id is not None
            and selected_option_id == question["correct_option_id"]
        )
        correct_answers += int(is_correct)
        selected_option = next(
            (
                option["text"]
                for option in question["options"]
                if option["id"] == selected_option_id
            ),
            None,
        )
        reviewed_questions.append(
            {
                "id": question["id"],
                "subject": question["subject"],
                "topic": question["topic"],
                "difficulty": question["difficulty"],
                "question": question["question"],
                "options": question["options"],
                "selected_option_id": selected_option_id,
                "selected_answer": selected_option,
                "correct_option_id": question["correct_option_id"],
                "correct_answer": question["correct_answer"],
                "status": (
                    "unanswered"
                    if selected_option_id is None
                    else "correct"
                    if is_correct
                    else "wrong"
                ),
                "explanation": question["explanation"],
            }
        )

    total_questions = len(attempt.questions)
    answered_questions = len(submitted_by_id)
    wrong_answers = answered_questions - correct_answers
    unanswered_questions = total_questions - answered_questions
    percentage = correct_answers / total_questions * 100
    attempt.result = {
        "total_questions": total_questions,
        "answered_questions": answered_questions,
        "correct_answers": correct_answers,
        "wrong_answers": wrong_answers,
        "unanswered_questions": unanswered_questions,
        "score": f"{correct_answers}/{total_questions}",
        "percentage": round(percentage, 2),
        "grade": grade_percentage(percentage),
        "questions": reviewed_questions,
    }
    attempt.status = "completed"
    attempt.completed_at = _now()
    try:
        db.commit()
        db.refresh(attempt)
    except Exception:
        db.rollback()
        raise
    return serialize_attempt(attempt)


def get_attempt_history(
    user_id: int, db: Session, limit: int = 50
) -> list[dict[str, Any]]:
    attempts = (
        db.query(MCQInterviewAttempt)
        .filter(
            MCQInterviewAttempt.user_id == user_id,
            MCQInterviewAttempt.status == "completed",
        )
        .order_by(MCQInterviewAttempt.completed_at.desc())
        .limit(limit)
        .all()
    )
    return [serialize_attempt(attempt) for attempt in attempts]


def get_attempt_progress(user_id: int, db: Session) -> dict[str, Any]:
    attempts = (
        db.query(MCQInterviewAttempt)
        .filter(
            MCQInterviewAttempt.user_id == user_id,
            MCQInterviewAttempt.status == "completed",
        )
        .order_by(MCQInterviewAttempt.completed_at.desc())
        .all()
    )
    total_questions = sum(attempt.result["total_questions"] for attempt in attempts)
    total_answered = sum(attempt.result["answered_questions"] for attempt in attempts)
    total_correct = sum(attempt.result["correct_answers"] for attempt in attempts)
    percentages = [float(attempt.result["percentage"]) for attempt in attempts]
    topic_stats: dict[tuple[str, str], dict[str, int]] = {}
    for attempt in attempts:
        key = (attempt.subject, attempt.topic)
        stats = topic_stats.setdefault(
            key, {"attempts": 0, "questions": 0, "answered": 0, "correct": 0}
        )
        stats["attempts"] += 1
        stats["questions"] += attempt.result["total_questions"]
        stats["answered"] += attempt.result["answered_questions"]
        stats["correct"] += attempt.result["correct_answers"]
    return {
        "total_completed": len(attempts),
        "total_questions": total_questions,
        "total_answered": total_answered,
        "correct_answers": total_correct,
        "overall_accuracy": (
            round(total_correct / total_answered * 100, 2)
            if total_answered
            else None
        ),
        "average_percentage": (
            round(sum(percentages) / len(percentages), 2) if percentages else None
        ),
        "best_percentage": max(percentages) if percentages else None,
        "topic_performance": [
            {
                "subject": subject,
                "topic": topic,
                **stats,
                "accuracy": (
                    round(stats["correct"] / stats["answered"] * 100, 2)
                    if stats["answered"]
                    else None
                ),
            }
            for (subject, topic), stats in sorted(topic_stats.items())
        ],
        "recent_attempts": [serialize_attempt(attempt) for attempt in attempts[:5]],
    }
