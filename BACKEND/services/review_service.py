# services/review_service.py
# CORRECCIÓN: Actualizamos los campos de rating en inglés.
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from schemas.review_schema import ReviewIn

async def add_review(db: AsyncIOMotorDatabase, review_in: ReviewIn, user_id: str) -> dict:
    review_dict = review_in.model_dump()
    review_dict["client_id"] = ObjectId(user_id)
    review_dict["professional_id"] = ObjectId(review_in.professional_id)
    review_dict["created_at"] = datetime.utcnow()
    
    result = await db["reviews"].insert_one(review_dict)
    
    professional_id = ObjectId(review_in.professional_id)
    pipeline = [
        {"$match": {"professional_id": professional_id}},
        {"$group": {
            "_id": "$professional_id",
            "avg_rating": {"$avg": "$rating"},
            "count": {"$sum": 1}
        }}
    ]
    
    stats_cursor = db["reviews"].aggregate(pipeline)
    stats = await stats_cursor.to_list(length=1)
    
    if stats:
        avg_rating = stats[0]['avg_rating']
        count = stats[0]['count']
        await db["professionals"].update_one(
            {"_id": professional_id},
            {"$set": {"avg_rating": avg_rating, "total_reviews": count}}
        )
        
    new_review = await db["reviews"].find_one({"_id": result.inserted_id})
    return new_review

async def get_reviews_for_professional(db: AsyncIOMotorDatabase, professional_id: str) -> List[dict]:
    reviews_cursor = db["reviews"].find({"professional_id": ObjectId(professional_id)})
    return await reviews_cursor.to_list(length=None)