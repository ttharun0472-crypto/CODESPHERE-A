from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models import Progress, Lesson, Course, Topic


# ==========================================
# UPDATE LESSON PROGRESS
# ==========================================

def update_progress(
    user_id: int,
    lesson_id: int,
    completion_percentage: float,
    db: Session
):
    # Validate completion percentage
    if not 0 <= completion_percentage <= 100:
        raise HTTPException(
            status_code=400,
            detail="Completion percentage must be between 0 and 100"
        )

    # Check whether lesson exists
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    # Find existing progress
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.lesson_id == lesson_id
    ).first()

    try:
        if progress:
            progress.completion_percentage = completion_percentage

        else:
            progress = Progress(
                user_id=user_id,
                lesson_id=lesson_id,
                completion_percentage=completion_percentage
            )

            db.add(progress)

        db.commit()
        db.refresh(progress)

        return progress

    except Exception:
        db.rollback()
        raise


# ==========================================
# GET ALL USER PROGRESS
# ==========================================

def get_user_progress(
    user_id: int,
    db: Session
):
    return db.query(Progress).filter(
        Progress.user_id == user_id
    ).all()


# ==========================================
# GET PROGRESS FOR A PARTICULAR LESSON
# ==========================================

def get_lesson_progress(
    user_id: int,
    lesson_id: int,
    db: Session
):
    progress = db.query(Progress).filter(
        Progress.user_id == user_id,
        Progress.lesson_id == lesson_id
    ).first()

    if progress is None:
        raise HTTPException(
            status_code=404,
            detail="Progress not found"
        )

    return progress


# ==========================================
# GET COMPLETED COURSES FOR INTERVIEW
# ==========================================

def get_completed_courses_for_interview(
    user_id: int,
    db: Session
):
    # Get all courses
    courses = db.query(Course).all()

    # Get progress belonging to the current user
    user_progress = db.query(Progress).filter(
        Progress.user_id == user_id
    ).all()

    # Map lesson IDs to their completion percentages
    progress_map = {
        item.lesson_id: item.completion_percentage
        for item in user_progress
    }

    completed_courses = []

    for course in courses:

        # Get lessons belonging to this course
        lessons = db.query(Lesson).filter(
            Lesson.course_id == course.id
        ).order_by(
            Lesson.lesson_order
        ).all()

        # Skip courses without lessons
        if not lessons:
            continue

        total_lessons = len(lessons)

        # Count lessons completed by this user
        completed_lessons = sum(
            1
            for lesson in lessons
            if progress_map.get(lesson.id, 0) >= 100
        )

        # Calculate completion percentage
        completion_percentage = round(
            (completed_lessons / total_lessons) * 100,
            2
        )

        # Include only fully completed courses
        if completed_lessons != total_lessons:
            continue

        lesson_details = []

        for lesson in lessons:

            # Get topics belonging to the lesson
            topics = db.query(Topic).filter(
                Topic.lesson_id == lesson.id
            ).order_by(
                Topic.topic_number
            ).all()

            lesson_details.append({
                "lesson_id": lesson.id,
                "title": lesson.title,
                "topics": [
                    {
                        "topic_id": topic.id,
                        "title": topic.title,
                        "description": topic.description
                    }
                    for topic in topics
                ]
            })

        # Add completed course information
        completed_courses.append({
            "course_id": course.id,
            "course_title": course.title,
            "course_level": course.level,
            "course_category": course.category,
            "completion_percentage": completion_percentage,
            "total_lessons": total_lessons,
            "completed_lessons": completed_lessons,
            "lessons": lesson_details
        })

    # Return completed course information
    return {
        "user_id": user_id,
        "total_completed_courses": len(completed_courses),
        "completed_courses": completed_courses
    }