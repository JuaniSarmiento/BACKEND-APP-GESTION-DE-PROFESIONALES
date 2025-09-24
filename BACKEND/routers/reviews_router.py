# routers/reviews_router.py
from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase

from database.databaseMongo import get_db
from schemas.review_schema import ReviewIn, ReviewOut
from schemas.user_schemas import UserOut
from services import review_service, professional_service
from utils.auth_service import get_current_user

router = APIRouter(prefix="/reviews", tags=["Reviews"])

@router.post("/", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def add_review(
    review_in: ReviewIn, 
    db: AsyncIOMotorDatabase = Depends(get_db), 
    current_user: UserOut = Depends(get_current_user)
):
    # Verificar que el profesional exista
    professional = await professional_service.get_professional_by_id(db, review_in.professional_id)
    if not professional:
        raise HTTPException(status_code=404, detail="Professional not found")

    new_review = await review_service.add_review(db, review_in, str(current_user.id))
    return ReviewOut(**new_review)

@router.get("/{professional_id}", response_model=List[ReviewOut])
async def get_reviews_for_professional(
    professional_id: str, 
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    reviews = await review_service.get_reviews_for_professional(db, professional_id)
    return [ReviewOut(**review) for review in reviews]