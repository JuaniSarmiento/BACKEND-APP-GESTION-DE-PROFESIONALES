from fastapi import APIRouter, Depends, HTTPException
from bson import ObjectId

from schemas.user_schemas import UserOut
from utils.auth_service import get_current_user_id
from database.databaseMongo import user_collection
from .auth_router import user_helper # Reutilizamos el helper

router = APIRouter(prefix="/users", tags=["Users"])

@router.get("/me", response_model=UserOut)
async def get_current_user_data(user_id: str = Depends(get_current_user_id)):
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if user:
        return user_helper(user)
    raise HTTPException(status_code=404, detail="Usuario no encontrado")