from fastapi import APIRouter, Depends, HTTPException, status
from bson import ObjectId
from datetime import datetime

from schemas.review_schema import ReviewCreate, ReviewOut
from utils.auth_service import get_current_user_id
from database.databaseMongo import review_collection, job_collection, professional_collection

router = APIRouter(prefix="/reviews", tags=["Reviews"])

def review_helper(review) -> dict:
    return {
        "id": str(review["_id"]),
        "job_id": str(review["job_id"]),
        "client_id": str(review["client_id"]),
        "professional_id": str(review["professional_id"]),
        "rating": review["rating"],
        "comment": review["comment"],
        "created_at": review["created_at"],
    }

async def update_professional_rating(professional_id: ObjectId):
    """Calcula y actualiza el rating promedio y total de un profesional."""
    pipeline = [
        {"$match": {"professional_id": professional_id}},
        {"$group": {
            "_id": "$professional_id",
            "avg_rating": {"$avg": "$rating"},
            "total_reviews": {"$sum": 1}
        }}
    ]
    
    result = await review_collection.aggregate(pipeline).to_list(1)
    
    if result:
        update_data = result[0]
        await professional_collection.update_one(
            {"user_id": professional_id},
            {"$set": {
                "avg_rating": round(update_data["avg_rating"], 2),
                "total_reviews": update_data["total_reviews"]
            }}
        )

@router.post("/job/{job_id}", response_model=ReviewOut, status_code=status.HTTP_201_CREATED)
async def create_review_for_job(
    job_id: str, 
    review_data: ReviewCreate, 
    user_id: str = Depends(get_current_user_id)
):
    """Crea una reseña para un trabajo completado."""
    job = await job_collection.find_one({"_id": ObjectId(job_id)})
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado.")

    # Verificaciones de seguridad y lógica de negocio
    if str(job["client_id"]) != user_id:
        raise HTTPException(status_code=403, detail="No puedes dejar una reseña en un trabajo que no creaste.")
    if job["status"] != "completed":
        raise HTTPException(status_code=409, detail="Solo se pueden reseñar trabajos completados.")
    
    existing_review = await review_collection.find_one({"job_id": ObjectId(job_id)})
    if existing_review:
        raise HTTPException(status_code=409, detail="Este trabajo ya tiene una reseña.")

    # Creamos la reseña
    review_dict = review_data.model_dump()
    review_dict.update({
        "job_id": ObjectId(job_id),
        "client_id": ObjectId(user_id),
        "professional_id": job["professional_id"],
        "created_at": datetime.utcnow()
    })

    result = await review_collection.insert_one(review_dict)
    new_review = await review_collection.find_one({"_id": result.inserted_id})

    # Actualizamos el rating del profesional
    await update_professional_rating(job["professional_id"])

    return review_helper(new_review)