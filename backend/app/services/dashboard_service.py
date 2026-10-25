from sqlalchemy.orm import Session

from app.models import (
    User,
    Course,
    Lesson,
    Progress,
    Resume,
    Placement,
    Interview
)


def get_dashboard(
    user_id: int,
    db: Session
):

    # Get current user
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if user is None:
        return {
            "message": "User not found"
        }

    # Available courses and lessons are counted from their actual tables,
    # without joining through user progress or other related records.
    total_courses = db.query(Course.id).count()
    total_lessons = db.query(Lesson.id).count()

    # User progress is isolated to the authenticated student.
    progress_records = db.query(Progress).filter(
        Progress.user_id == user_id
    ).all()

    normalized_progress = []
    for progress in progress_records:
        completion = float(progress.completion_percentage or 0)
        normalized_progress.append(max(0, min(completion, 100)))

    lessons_started = len(progress_records)
    lessons_completed = sum(
        1 for completion in normalized_progress if completion >= 100
    )
    average_progress = (
        sum(normalized_progress) / len(normalized_progress)
        if normalized_progress else 0
    )

    # Resume
    resume = db.query(Resume).filter(
        Resume.user_id == user_id
    ).first()

    # Placements
    total_placements = db.query(
        Placement
    ).count()

    # Interview questions
    total_interview_questions = db.query(
        Interview
    ).count()

    return {
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "is_admin": user.is_admin
        },

        "courses": {
            "total_courses": total_courses,
            "total_lessons": total_lessons
        },

        "learning_progress": {
            "lessons_started": lessons_started,
            "lessons_completed": lessons_completed,
            "average_progress": round(
                average_progress,
                2
            )
        },

        "resume": {
            "created": resume is not None,
            "resume_id": (
                resume.id
                if resume
                else None
            )
        },

        "placements": {
            "total": total_placements
        },

        "interview_preparation": {
            "total_questions": total_interview_questions
        }
    }