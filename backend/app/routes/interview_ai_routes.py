from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.schemas.interview_session_schema import InterviewSessionCreate
from app.services.interview_ai_service import generate_interview_questions
from app.services.interview_question_bank import get_course

router = APIRouter(
    prefix="/interview/ai",
    tags=["AI Interview"],
)


@router.post("/generate-questions")
def generate_questions(
    request: InterviewSessionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    course = get_course(request.course_id, db) if request.course_id else None
    questions = generate_interview_questions(request, course)
    return {
        "user_id": current_user.id,
        "course_id": course.id if course else None,
        "course_title": course.title if course else None,
        "category": request.category,
        "difficulty": request.difficulty,
        "total_questions": len(questions),
        "questions": questions,
    }