from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from datetime import datetime

from schemas.job_schema import JobCreate, JobOut, JobStatus
from utils.auth_service import get_current_user_id
from database.databaseMongo import job_collection, user_collection

router = APIRouter(prefix="/jobs", tags=["Jobs"])

def job_helper(job) -> dict:
    """Formatea la respuesta de un trabajo."""
    return {
        "id": str(job["_id"]),
        "client_id": str(job["client_id"]),
        "title": job["title"],
        "description": job["description"],
        "category": job["category"],
        "budget": job["budget"],
        "status": job["status"],
        "created_at": job["created_at"],
    }

@router.post("/", response_model=JobOut, status_code=status.HTTP_201_CREATED)
async def create_job(
    job_data: JobCreate, 
    user_id: str = Depends(get_current_user_id)
):
    """Crea una nueva solicitud de trabajo (solo para clientes)."""
    # 1. Verificamos que el usuario sea un cliente
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user or user.get("role") != "client":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acción no permitida. Se requiere rol de cliente."
        )

    # 2. Creamos el diccionario del trabajo para la DB
    job_dict = job_data.model_dump()
    job_dict["client_id"] = ObjectId(user_id)
    job_dict["status"] = JobStatus.POSTED  # Estado inicial
    job_dict["created_at"] = datetime.utcnow()

    # 3. Insertamos y devolvemos el trabajo creado
    result = await job_collection.insert_one(job_dict)
    new_job = await job_collection.find_one({"_id": result.inserted_id})
    
    return job_helper(new_job)

@router.get("/my-jobs", response_model=List[JobOut])
async def get_my_posted_jobs(user_id: str = Depends(get_current_user_id)):
    """Obtiene todos los trabajos publicados por el cliente autenticado."""
    jobs = []
    async for job in job_collection.find({"client_id": ObjectId(user_id)}):
        jobs.append(job_helper(job))
    return jobs

@router.get("/{job_id}", response_model=JobOut)
async def get_job_by_id(job_id: str, user_id: str = Depends(get_current_user_id)):
    """Obtiene un trabajo específico por su ID."""
    try:
        job_obj_id = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de trabajo inválido.")

    job = await job_collection.find_one({"_id": job_obj_id})
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado.")
    
    # (Acá podríamos agregar lógica de permisos, por ahora cualquiera logueado puede ver)
    return job_helper(job)
@router.get("/available/", response_model=List[JobOut])
async def get_available_jobs(user_id: str = Depends(get_current_user_id)):
    """
    Obtiene todos los trabajos con estado 'posted'.
    Ruta protegida solo para profesionales.
    """
    # 1. Verificamos que el usuario sea un profesional
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user or user.get("role") != "professional":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acción no permitida. Se requiere rol de profesional."
        )

    # 2. Buscamos todos los trabajos que esperan ser aceptados
    available_jobs = []
    query = {"status": JobStatus.POSTED}
    async for job in job_collection.find(query):
        available_jobs.append(job_helper(job))
        
    return available_jobs
@router.patch("/{job_id}/accept", response_model=JobOut)
async def accept_job(job_id: str, user_id: str = Depends(get_current_user_id)):
    """
    Permite a un profesional aceptar un trabajo.
    Cambia el estado del trabajo a 'accepted' y le asigna el profesional.
    """
    # 1. Verificamos que el usuario sea un profesional
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user or user.get("role") != "professional":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Se requiere rol de profesional."
        )

    try:
        job_obj_id = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de trabajo inválido.")
        
    # 2. Buscamos el trabajo y chequeamos que se pueda aceptar
    job = await job_collection.find_one({"_id": job_obj_id})
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado.")
    if job["status"] != JobStatus.POSTED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, # 'Conflict' es ideal para este caso
            detail=f"No se puede aceptar el trabajo, su estado actual es '{job['status']}'."
        )

    # 3. Actualizamos el trabajo en la base de datos
    update_data = {
        "$set": {
            "professional_id": ObjectId(user_id),
            "status": JobStatus.ACCEPTED
        }
    }
    result = await job_collection.update_one({"_id": job_obj_id}, update_data)
    
    if result.modified_count == 1:
        updated_job = await job_collection.find_one({"_id": job_obj_id})
        return job_helper(updated_job)
    

    raise HTTPException(status_code=500, detail="No se pudo actualizar el trabajo.")

# ... (al final del archivo, dentro del router de jobs) ...

@router.patch("/{job_id}/start", response_model=JobOut)
async def start_job_progress(job_id: str, user_id: str = Depends(get_current_user_id)):
    """El profesional asignado marca el trabajo como 'en progreso'."""
    try:
        job_obj_id = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de trabajo inválido.")

    job = await job_collection.find_one({"_id": job_obj_id})
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado.")

    # Verificamos que quien lo inicia es el profesional asignado
    if str(job.get("professional_id")) != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para iniciar este trabajo.")
    
    if job["status"] != JobStatus.ACCEPTED:
        raise HTTPException(status_code=409, detail=f"El trabajo no puede iniciarse, su estado es '{job['status']}'.")

    await job_collection.update_one({"_id": job_obj_id}, {"$set": {"status": JobStatus.IN_PROGRESS}})
    updated_job = await job_collection.find_one({"_id": job_obj_id})
    return job_helper(updated_job)


@router.patch("/{job_id}/complete", response_model=JobOut)
async def complete_job(job_id: str, user_id: str = Depends(get_current_user_id)):
    """El cliente marca el trabajo como 'completado'."""
    try:
        job_obj_id = ObjectId(job_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de trabajo inválido.")

    job = await job_collection.find_one({"_id": job_obj_id})
    if not job:
        raise HTTPException(status_code=404, detail="Trabajo no encontrado.")

    # Verificamos que quien lo completa es el cliente que lo creó
    if str(job.get("client_id")) != user_id:
        raise HTTPException(status_code=403, detail="No tienes permiso para completar este trabajo.")

    if job["status"] != JobStatus.IN_PROGRESS:
        raise HTTPException(status_code=409, detail=f"El trabajo no puede completarse, su estado es '{job['status']}'.")

    await job_collection.update_one({"_id": job_obj_id}, {"$set": {"status": JobStatus.COMPLETED}})
    updated_job = await job_collection.find_one({"_id": job_obj_id})
    return job_helper(updated_job)