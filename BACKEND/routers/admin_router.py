from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId

from utils.auth_service import get_current_user_id
from database.databaseMongo import professional_collection, user_collection
from schemas.professional_schema import ProfessionalProfileOut, VerificationStatus
from .professionals_router import profile_helper # Reutilizamos el helper

# --- Dependencia de Admin ---
async def require_admin(user_id: str = Depends(get_current_user_id)):
    """Dependencia que verifica si el usuario tiene el rol de 'admin'."""
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user or user.get("role") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere rol de administrador."
        )
    return user_id

# --- Router de Admin ---
router = APIRouter(
    prefix="/admin", 
    tags=["Admin"],
    dependencies=[Depends(require_admin)] # ¡Protegemos todas las rutas de este router!
)

@router.get("/verifications/pending", response_model=List[ProfessionalProfileOut])
async def get_pending_verifications():
    """Obtiene todos los perfiles de profesionales pendientes de verificación."""
    profiles = []
    query = {"verification_status": VerificationStatus.PENDING}
    async for profile in professional_collection.find(query):
        user = await user_collection.find_one({"_id": profile["user_id"]})
        if user:
            profiles.append(profile_helper(profile, user))
    return profiles

@router.patch("/verifications/{prof_user_id}/approve", status_code=status.HTTP_204_NO_CONTENT)
async def approve_verification(prof_user_id: str):
    """Aprueba la verificación de un profesional."""
    await professional_collection.update_one(
        {"user_id": ObjectId(prof_user_id)},
        {"$set": {"verification_status": VerificationStatus.VERIFIED}}
    )
    # 204 significa "OK, lo hice, pero no te devuelvo nada en el cuerpo"
    return

@router.patch("/verifications/{prof_user_id}/reject", status_code=status.HTTP_204_NO_CONTENT)
async def reject_verification(prof_user_id: str):
    """Rechaza la verificación de un profesional."""
    await professional_collection.update_one(
        {"user_id": ObjectId(prof_user_id)},
        {"$set": {"verification_status": VerificationStatus.REJECTED}}
    )
    return