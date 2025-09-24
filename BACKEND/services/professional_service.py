# services/professional_service.py
# CORRECCIÓN: Inicializamos los campos de rating en inglés.
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.professional_schema import ProfessionalIn, ProfessionalUpdate

async def create_professional(db: AsyncIOMotorDatabase, professional_in: ProfessionalIn, user_id: str) -> dict:
    professional_dict = professional_in.model_dump()
    professional_dict["user_id"] = ObjectId(user_id)
    professional_dict["avg_rating"] = 0.0
    professional_dict["total_reviews"] = 0
    
    result = await db["professionals"].insert_one(professional_dict)
    created_professional = await db["professionals"].find_one({"_id": result.inserted_id})
    return created_professional

# ... (el resto del archivo queda igual)
async def get_all_professionals(db: AsyncIOMotorDatabase) -> List[dict]:
    professionals_cursor = db["professionals"].find()
    return await professionals_cursor.to_list(length=None)

async def get_professional_by_id(db: AsyncIOMotorDatabase, professional_id: str) -> Optional[dict]:
    return await db["professionals"].find_one({"_id": ObjectId(professional_id)})
    
async def get_professional_by_user_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[dict]:
    return await db["professionals"].find_one({"user_id": ObjectId(user_id)})

async def update_professional(db: AsyncIOMotorDatabase, professional_id: str, professional_update: ProfessionalUpdate) -> Optional[dict]:
    update_data = {k: v for k, v in professional_update.model_dump(exclude_unset=True).items() if v is not None}
    if not update_data:
        return None

    await db["professionals"].update_one(
        {"_id": ObjectId(professional_id)},
        {"$set": update_data}
    )
    return await db["professionals"].find_one({"_id": ObjectId(professional_id)})

async def delete_professional(db: AsyncIOMotorDatabase, professional_id: str) -> bool:
    result = await db["professionals"].delete_one({"_id": ObjectId(professional_id)})
    return result.deleted_count > 0