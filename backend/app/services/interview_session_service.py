from datetime import datetime, timedelta, timezone

from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import InterviewSession, User
from app.schemas.interview_session_schema import (
    InterviewEvaluation,
    InterviewSessionCreate,
    InterviewSessionResponse,
)
from app.services.interview_ai_service import (
    evaluate_interview_answer,
    generate_interview_questions,
)
from app.services.interview_question_bank import get_course


def _as_utc(value: datetime | None) -> datetime | None:
    if value is None:
        return None
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def serialize_session(session: InterviewSession) -> InterviewSessionResponse:
    completed = session.status == "completed"
    questions = []
    for index, item in enumerate(session.questions):
        questions.append(
            {
                "question_index": index,
                "course_id": item.get("course_id"),
                "question": item["question"],
                "category": item["category"],
                "difficulty": item["difficulty"],
                "answer": item.get("answer"),
                "evaluation": item.get("evaluation"),
                "expected_answer": (
                    item.get("expected_answer") if completed else None
                ),
            }
        )
    return InterviewSessionResponse(
        id=session.id,
        category=session.category,
        course_id=session.course_id,
        course_title=session.course_title,
        skill=session.skill,
        difficulty=session.difficulty,
        duration_minutes=session.duration_minutes,
        total_questions=session.total_questions,
        questions=questions,
        status=session.status,
        question_source=(
            session.questions[0].get("question_source", "default")
            if session.questions
            else "default"
        ),
        overall_score=session.overall_score,
        created_at=_as_utc(session.created_at),
        completed_at=_as_utc(session.completed_at),
    )


def get_owned_session(
    session_id: int,
    user_id: int,
    db: Session,
    lock: bool = False,
) -> InterviewSession:
    query = db.query(InterviewSession).filter(
        InterviewSession.id == session_id,
        InterviewSession.user_id == user_id,
    )
    if lock:
        query = query.with_for_update()
    session = query.first()
    if session is None:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return session


def create_session(
    user_id: int,
    request: InterviewSessionCreate,
    db: Session,
) -> InterviewSessionResponse:
    active_session = (
        db.query(InterviewSession.id)
        .filter(
            InterviewSession.user_id == user_id,
            InterviewSession.status == "in_progress",
        )
        .first()
    )
    if active_session:
        raise HTTPException(
            status_code=409,
            detail="Finish or resume your active interview before starting another.",
        )

    course = get_course(request.course_id, db) if request.course_id else None
    questions = generate_interview_questions(request, course)
    user = db.query(User).filter(User.id == user_id).with_for_update().first()
    if user is None:
        raise HTTPException(status_code=404, detail="User not found.")
    active_session = (
        db.query(InterviewSession.id)
        .filter(
            InterviewSession.user_id == user_id,
            InterviewSession.status == "in_progress",
        )
        .first()
    )
    if active_session:
        raise HTTPException(
            status_code=409,
            detail="Finish or resume your active interview before starting another.",
        )

    session = InterviewSession(
        user_id=user_id,
        category=request.category,
        course_id=course.id if course else None,
        course_title=course.title if course else None,
        skill=None,
        difficulty=request.difficulty,
        duration_minutes=request.duration_minutes,
        total_questions=len(questions),
        questions=[
            {**question, "answer": None, "evaluation": None}
            for question in questions
        ],
    )
    try:
        db.add(session)
        db.commit()
        db.refresh(session)
    except Exception:
        db.rollback()
        raise
    return serialize_session(session)


def submit_answer(
    session_id: int,
    question_index: int,
    user_id: int,
    answer: str,
    db: Session,
) -> InterviewSessionResponse:
    session = get_owned_session(session_id, user_id, db, lock=True)
    if session.status != "in_progress":
        raise HTTPException(
            status_code=409,
            detail="This interview has already been completed.",
        )
    if question_index < 0 or question_index >= len(session.questions):
        raise HTTPException(status_code=404, detail="Interview question not found.")
    question = session.questions[question_index]
    if question.get("evaluation") is not None:
        raise HTTPException(
            status_code=409,
            detail="An answer has already been submitted for this question.",
        )
    if not answer.strip():
        raise HTTPException(status_code=422, detail="Answer cannot be empty.")
    if (
        session.duration_minutes is not None
        and datetime.now(timezone.utc).replace(tzinfo=None)
        >= session.created_at + timedelta(minutes=session.duration_minutes)
    ):
        raise HTTPException(
            status_code=409,
            detail="The interview time limit has elapsed. Finish the interview to review your results.",
        )

    evaluation: InterviewEvaluation = evaluate_interview_answer(
        question,
        answer,
        session.category,
    )
    questions = [dict(item) for item in session.questions]
    questions[question_index]["answer"] = answer.strip()
    questions[question_index]["evaluation"] = evaluation.model_dump()
    session.questions = questions
    try:
        db.commit()
        db.refresh(session)
    except Exception:
        db.rollback()
        raise
    return serialize_session(session)


def complete_session(
    session_id: int,
    user_id: int,
    db: Session,
) -> InterviewSessionResponse:
    session = get_owned_session(session_id, user_id, db, lock=True)
    if session.status == "completed":
        return serialize_session(session)

    scores = [
        item["evaluation"]["score"]
        for item in session.questions
        if item.get("evaluation") is not None
    ]
    session.overall_score = round(sum(scores) / len(scores), 1) if scores else None
    session.status = "completed"
    session.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    try:
        db.commit()
        db.refresh(session)
    except Exception:
        db.rollback()
        raise
    return serialize_session(session)


def get_completed_sessions(
    user_id: int,
    db: Session,
    limit: int = 20,
) -> list[InterviewSessionResponse]:
    sessions = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.user_id == user_id,
            InterviewSession.status == "completed",
        )
        .order_by(InterviewSession.completed_at.desc())
        .limit(limit)
        .all()
    )
    return [serialize_session(session) for session in sessions]


def get_session_summary(user_id: int, db: Session) -> dict:
    query = db.query(
        func.count(InterviewSession.id),
        func.avg(InterviewSession.overall_score),
    ).filter(
        InterviewSession.user_id == user_id,
        InterviewSession.status == "completed",
    )
    total_completed, average_score = query.one()
    return {
        "total_completed": total_completed,
        "average_score": (
            round(float(average_score), 1) if average_score is not None else None
        ),
        "recent_sessions": get_completed_sessions(user_id, db, limit=5),
    }


def get_active_session(
    user_id: int,
    db: Session,
) -> InterviewSessionResponse | None:
    session = (
        db.query(InterviewSession)
        .filter(
            InterviewSession.user_id == user_id,
            InterviewSession.status == "in_progress",
        )
        .order_by(InterviewSession.created_at.desc())
        .first()
    )
    return serialize_session(session) if session else None
