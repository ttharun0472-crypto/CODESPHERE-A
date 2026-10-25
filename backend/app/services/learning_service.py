from fastapi import HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models import Course, Lesson
from app.schemas import (
    CourseCreate,
    CourseUpdate,
    LessonCreate,
    LessonUpdate
)


# =========================
# COURSE
# =========================

def create_course(
    course_data: CourseCreate,
    db: Session
):
    title = course_data.title.strip()
    existing_course = db.query(Course).filter(
        func.lower(func.trim(Course.title)) == title.lower()
    ).first()
    if existing_course is not None:
        return existing_course

    course = Course(
        title=title,
        description=course_data.description
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


def get_courses(db: Session):
    return db.query(Course).all()


def get_course(
    course_id: int,
    db: Session
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return course


def update_course(
    course_id: int,
    course_data: CourseUpdate,
    db: Session
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    title = course_data.title.strip()
    duplicate = db.query(Course).filter(
        Course.id != course.id,
        func.lower(func.trim(Course.title)) == title.lower()
    ).first()
    if duplicate is not None:
        raise HTTPException(
            status_code=409,
            detail="A course with this title already exists"
        )

    course.title = title
    course.description = course_data.description

    db.commit()
    db.refresh(course)

    return course


def delete_course(
    course_id: int,
    db: Session
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    db.delete(course)
    db.commit()

    return {
        "message": "Course deleted successfully"
    }


# =========================
# LESSON
# =========================

def _lessons_for_course(
    db: Session,
    course_id: int,
    exclude_lesson_id: int | None = None
) -> list[Lesson]:
    query = db.query(Lesson).filter(Lesson.course_id == course_id)
    if exclude_lesson_id is not None:
        query = query.filter(Lesson.id != exclude_lesson_id)
    return query.order_by(Lesson.lesson_order, Lesson.id).all()


def _assign_lesson_order(lessons: list[Lesson]) -> None:
    for order, lesson in enumerate(lessons, start=1):
        lesson.lesson_order = order


def create_lesson(
    lesson_data: LessonCreate,
    db: Session
):
    course = db.query(Course).filter(
        Course.id == lesson_data.course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    title = lesson_data.title.strip()
    existing_lesson = db.query(Lesson).filter(
        Lesson.course_id == lesson_data.course_id,
        func.lower(func.trim(Lesson.title)) == title.lower()
    ).first()
    if existing_lesson is not None:
        return existing_lesson

    lessons = _lessons_for_course(db, course.id)
    requested_order = lesson_data.lesson_order
    insert_at = (
        len(lessons)
        if requested_order is None
        else min(requested_order - 1, len(lessons))
    )

    lesson = Lesson(
        course_id=lesson_data.course_id,
        title=title,
        notes=lesson_data.notes,
        important_concepts=lesson_data.important_concepts,
        youtube_url=lesson_data.youtube_url
    )

    lessons.insert(insert_at, lesson)
    db.add(lesson)
    _assign_lesson_order(lessons)
    db.commit()
    db.refresh(lesson)

    return lesson


def get_lessons(
    course_id: int,
    db: Session
):
    course = db.query(Course).filter(
        Course.id == course_id
    ).first()

    if course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    return db.query(Lesson).filter(
        Lesson.course_id == course_id
    ).order_by(
        Lesson.lesson_order,
        Lesson.id
    ).all()


def get_lesson(
    lesson_id: int,
    db: Session
):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    return lesson


def update_lesson(
    lesson_id: int,
    lesson_data: LessonUpdate,
    db: Session
):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    target_course_id = (
        lesson_data.course_id
        if lesson_data.course_id is not None
        else lesson.course_id
    )
    target_course = db.query(Course).filter(
        Course.id == target_course_id
    ).first()
    if target_course is None:
        raise HTTPException(
            status_code=404,
            detail="Course not found"
        )

    title = lesson_data.title.strip()
    duplicate = db.query(Lesson).filter(
        Lesson.course_id == target_course_id,
        Lesson.id != lesson.id,
        func.lower(func.trim(Lesson.title)) == title.lower()
    ).first()
    if duplicate is not None:
        raise HTTPException(
            status_code=409,
            detail="A lesson with this title already exists in the course"
        )

    source_course_id = lesson.course_id
    order_changed = (
        target_course_id != source_course_id
        or lesson_data.lesson_order is not None
    )
    if order_changed:
        source_lessons = _lessons_for_course(
            db,
            source_course_id,
            exclude_lesson_id=lesson.id
        )
        if target_course_id == source_course_id:
            target_lessons = source_lessons
        else:
            _assign_lesson_order(source_lessons)
            target_lessons = _lessons_for_course(db, target_course_id)

        requested_order = lesson_data.lesson_order
        if requested_order is None:
            insert_at = len(target_lessons)
        else:
            insert_at = min(requested_order - 1, len(target_lessons))
        target_lessons.insert(insert_at, lesson)
        lesson.course_id = target_course_id
        _assign_lesson_order(target_lessons)

    lesson.title = title
    lesson.notes = lesson_data.notes
    lesson.important_concepts = lesson_data.important_concepts
    lesson.youtube_url = lesson_data.youtube_url

    db.commit()
    db.refresh(lesson)

    return lesson


def delete_lesson(
    lesson_id: int,
    db: Session
):
    lesson = db.query(Lesson).filter(
        Lesson.id == lesson_id
    ).first()

    if lesson is None:
        raise HTTPException(
            status_code=404,
            detail="Lesson not found"
        )

    db.delete(lesson)
    db.commit()

    return {
        "message": "Lesson deleted successfully"
    }