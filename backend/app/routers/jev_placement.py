from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Body
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.dependencies import get_current_user
from app.models import User
from app.services.jev_placement_service import calculate_placement_recommendations


router = APIRouter(
    prefix="/api/jev/placement",
    tags=["Jev Placement Recommendation"]
)


class PlacementRecommendRequest(BaseModel):
    career_goal: Optional[str] = None
    preferred_location: Optional[str] = None
    job_type: Optional[str] = None


@router.post("/recommend")
def recommend_placements_post(
    request: Optional[PlacementRecommendRequest] = Body(default=None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Generate AI-powered placement recommendations by combining:
    - CodeSphere student profile
    - Generated Resume Builder data
    - LMS course completions and progress
    - Database placement company requirements
    Evaluated via Jev AI decision engine.
    """
    try:
        career_filter = request.career_goal if request else None
        recommendations = calculate_placement_recommendations(
            user_id=current_user.id,
            db=db,
            career_filter=career_filter
        )
        return recommendations
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate placement recommendations: {str(e)}"
        )


@router.get("/recommend")
def recommend_placements_get(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Convenience GET endpoint to fetch placement recommendations for the authenticated student.
    """
    try:
        return calculate_placement_recommendations(
            user_id=current_user.id,
            db=db
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to generate placement recommendations: {str(e)}"
        )
