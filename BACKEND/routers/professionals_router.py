from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from schemas import professional_schema
from database.databaseMongo import get_db
from utils.auth_service import get_current_user

router = APIRouter(
    prefix="/professionals",
    tags=["Professionals"],
    dependencies=[Depends(get_current_user)]
)

@router.get("/all", response_model=List[professional_schema.ProfessionalOut])
async def get_all_professionals(
    db: AsyncIOMotorDatabase = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de profesionales a saltear"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de profesionales por página")
):
    """
    Obtiene una lista paginada de todos los profesionales.
    """
    professionals_cursor = db.professionals.find().skip(skip).limit(limit)
    professionals_list = await professionals_cursor.to_list(length=limit)
    return professionals_list

@router.get("/search", response_model=List[professional_schema.ProfessionalOut])
async def search_professionals_with_filters(
    db: AsyncIOMotorDatabase = Depends(get_db),
    profession: Optional[str] = Query(None, description="Filtrar por profesión (ej: Plomero)"),
    city: Optional[str] = Query(None, description="Filtrar por ciudad (ej: Mendoza)"),
    min_rating: Optional[float] = Query(None, ge=0, le=5, description="Filtrar por calificación mínima (0 a 5)"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100)
):
    """
    Busca profesionales aplicando filtros avanzados y paginación.
    """
    search_query = {}
    if profession:
        search_query["profession"] = {"$regex": profession, "$options": "i"}
    if city:
        search_query["city"] = {"$regex": city, "$options": "i"}
    if min_rating is not None:
        search_query["rating"] = {"$gte": min_rating}

    professionals_cursor = db.professionals.find(search_query).skip(skip).limit(limit)
    professionals_list = await professionals_cursor.to_list(length=limit)
    
    if not professionals_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se encontraron profesionales con esos filtros")
        
    return professionals_list

@router.get("/{professional_id}", response_model=professional_schema.ProfessionalOut)
async def get_professional_by_id(professional_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    if not ObjectId.is_valid(professional_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de profesional inválido")
    professional = await db.professionals.find_one({"_id": ObjectId(professional_id)})
    if professional:
        return professional
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profesional no encontrado")