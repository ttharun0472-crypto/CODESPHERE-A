from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.models.student_interview_skill import StudentInterviewSkill

from app.schemas.student_interview_skill_schema import (
    StudentInterviewSkillCreate,
    StudentInterviewSkillResponse,
)

router = APIRouter(
    prefix="/interview/skills",
    tags=["Interview Skills"],
)


# ADD A SKILL
@router.post(
    "/",
    response_model=StudentInterviewSkillResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_interview_skill(
    skill_data: StudentInterviewSkillCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skill_name = skill_data.skill_name.strip()

    if not skill_name:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Skill name cannot be empty.",
        )

    db.query(User).filter(User.id == current_user.id).with_for_update().first()
    existing_skill = (
        db.query(StudentInterviewSkill)
        .filter(
            StudentInterviewSkill.user_id == current_user.id,
            StudentInterviewSkill.skill_name.ilike(skill_name),
        )
        .first()
    )

    if existing_skill:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already added this skill.",
        )

    skill = StudentInterviewSkill(
        user_id=current_user.id,
        skill_name=skill_name,
    )

    try:
        db.add(skill)
        db.commit()
        db.refresh(skill)
        return skill
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="You have already added this skill.",
        ) from exc
    except Exception:
        db.rollback()
        raise


# GET ALL SKILLS FOR THE LOGGED-IN USER
@router.get(
    "/",
    response_model=list[StudentInterviewSkillResponse],
)
def get_interview_skills(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return (
        db.query(StudentInterviewSkill)
        .filter(StudentInterviewSkill.user_id == current_user.id)
        .order_by(StudentInterviewSkill.id.desc())
        .all()
    )


# DELETE A SKILL
@router.delete("/{skill_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview_skill(
    skill_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    skill = (
        db.query(StudentInterviewSkill)
        .filter(
            StudentInterviewSkill.id == skill_id,
            StudentInterviewSkill.user_id == current_user.id,
        )
        .first()
    )

    if skill is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Skill not found.",
        )

    db.delete(skill)
    db.commit()

    return None