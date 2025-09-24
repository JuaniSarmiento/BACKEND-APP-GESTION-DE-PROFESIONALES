from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from schemas import job_schema
from database.databaseMongo import get_db
from utils.auth_service import get_current_user

router = APIRouter(
    prefix="/jobs",
    tags=["Jobs"],
    dependencies=[Depends(get_current_user)]
)

@router.post("/", response_model=job_schema.JobOut, status_code=status.HTTP_201_CREATED)
async def create_job(job_data: job_schema.JobIn, db: AsyncIOMotorDatabase = Depends(get_db)):
    job_doc = job_data.model_dump()
    result = await db.jobs.insert_one(job_doc)
    created_job = await db.jobs.find_one({"_id": result.inserted_id})
    return created_job

# --- ENDPOINT MEJORADO ---
@router.get("/all", response_model=List[job_schema.JobOut])
async def get_all_jobs(
    db: AsyncIOMotorDatabase = Depends(get_db),
    skip: int = Query(0, ge=0, description="Número de trabajos a saltear"),
    limit: int = Query(20, ge=1, le=100, description="Máximo de trabajos por página")
):
    """
    Obtiene una lista paginada de todos los trabajos.
    """
    jobs_cursor = db.jobs.find().skip(skip).limit(limit)
    jobs_list = await jobs_cursor.to_list(length=limit)
    return jobs_list

@router.get("/{job_id}", response_model=job_schema.JobOut)
async def get_job_by_id(job_id: str, db: AsyncIOMotorDatabase = Depends(get_db)):
    if not ObjectId.is_valid(job_id):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="ID de trabajo inválido")
    job = await db.jobs.find_one({"_id": ObjectId(job_id)})
    if job:
        return job
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Trabajo no encontrado")