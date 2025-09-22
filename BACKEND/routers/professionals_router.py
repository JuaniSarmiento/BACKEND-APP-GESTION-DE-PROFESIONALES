from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from bson import ObjectId
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from schemas.professional_schema import ProfessionalProfileCreate, ProfessionalProfileOut
from utils.auth_service import get_current_user_id
from database.databaseMongo import professional_collection, user_collection
from .auth_router import user_helper # Reutilizamos el helper de usuarios
from schemas.dashboard_schema import DashboardOut
from database.databaseMongo import job_collection, review_collection
router = APIRouter(prefix="/professionals", tags=["Professionals"])

def profile_helper(profile_data, user_data) -> dict:
    """Combina datos del perfil y del usuario para la respuesta."""
    return {
        "user_id": str(user_data["_id"]),
        "headline": profile_data.get("headline"),
        "bio": profile_data.get("bio"),
        "categories": profile_data.get("categories", []),
        # ... acá podrías agregar más datos del usuario si quisieras
    }

@router.put("/me/profile", response_model=ProfessionalProfileOut)
async def create_or_update_my_profile(
    profile_data: ProfessionalProfileCreate, 
    user_id: str = Depends(get_current_user_id)
):
    """Crea o actualiza el perfil del profesional autenticado."""
    # 1. Verificamos que el usuario sea realmente un profesional
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user or user.get("role") != "professional":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Acción no permitida. Se requiere rol de profesional."
        )

    # 2. Creamos o actualizamos el perfil usando 'upsert=True'
    # Esta es la magia de Mongo: si no encuentra un doc para actualizar, lo crea.
    profile_dict = profile_data.model_dump()
    profile_dict["user_id"] = ObjectId(user_id)

    await professional_collection.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": profile_dict},
        upsert=True
    )
    
    # Devolvemos el perfil combinado con datos del usuario
    return profile_helper(profile_dict, user)


@router.get("/", response_model=List[ProfessionalProfileOut])
async def get_all_professionals():
    """Obtiene una lista de todos los perfiles de profesionales (ruta pública)."""
    profiles = []
    # Usamos un cursor para iterar sobre los resultados de la base de datos
    async for profile in professional_collection.find().limit(100):
        user = await user_collection.find_one({"_id": profile["user_id"]})
        if user:
            profiles.append(profile_helper(profile, user))
    return profiles

@router.get("/", response_model=List[ProfessionalProfileOut])
async def get_all_professionals(
    category: Optional[str] = Query(None, description="Filtrar por categoría de servicio"),
    sort_by: Optional[str] = Query(None, description="Ordenar por 'rating_desc' o 'rating_asc'")
):
    """
    Obtiene una lista de todos los perfiles de profesionales,
    con opciones de filtrado y ordenamiento.
    """
    query = {}
    sort_options = []

    # 1. Construimos el filtro dinámicamente
    if category:
        # Buscamos que la categoría esté DENTRO del array 'categories' del profesional
        query["categories"] = category.lower()

    # 2. Construimos el ordenamiento dinámicamente
    if sort_by:
        if sort_by == "rating_desc":
            sort_options.append(("avg_rating", -1)) # -1 para descendente
        elif sort_by == "rating_asc":
            sort_options.append(("avg_rating", 1)) # 1 para ascendente
    
    # 3. Ejecutamos la consulta
    profiles_cursor = professional_collection.find(query)
    if sort_options:
        profiles_cursor = profiles_cursor.sort(sort_options)

    # 4. Procesamos y devolvemos los resultados
    profiles = []
    async for profile in profiles_cursor.limit(100):
        user = await user_collection.find_one({"_id": profile["user_id"]})
        if user and user.get("role") == "professional":
            # Para la respuesta, necesitamos los datos del perfil y del usuario
            full_profile_data = profile.copy()
            full_profile_data.update(user)
            full_profile_data["user_id"] = str(user["_id"])
            profiles.append(profile_helper(profile, user)) # Usamos el helper que ya teníamos
            
    return profiles
@router.get("/{professional_user_id}", response_model=ProfessionalProfileOut)
async def get_professional_by_id(professional_user_id: str):
    """Obtiene el perfil público de un profesional específico por su ID de usuario."""
    try:
        user_obj_id = ObjectId(professional_user_id)
    except Exception:
        raise HTTPException(status_code=400, detail="ID de usuario inválido.")

    user = await user_collection.find_one({"_id": user_obj_id})
    profile = await professional_collection.find_one({"user_id": user_obj_id})

    if user and profile and user.get("role") == "professional":
        return profile_helper(profile, user)
    
    raise HTTPException(status_code=404, detail="Profesional no encontrado.")

@router.get("/me/dashboard", response_model=DashboardOut)
async def get_professional_dashboard(user_id: str = Depends(get_current_user_id)):
    """
    Calcula y devuelve las métricas de negocio para el profesional autenticado.
    """
    professional_obj_id = ObjectId(user_id)

    # --- Pipeline para calcular métricas de Trabajos ---
    jobs_pipeline = [
        # 1. Filtrar solo los trabajos del profesional actual
        {"$match": {"professional_id": professional_obj_id}},
        # 2. Agrupar por estado y calcular
        {"$group": {
            "_id": "$status", # Agrupamos por el campo 'status'
            "count": {"$sum": 1}, # Contamos cuántos trabajos hay en cada estado
            "total_budget": {"$sum": "$budget"} # Sumamos el presupuesto
        }}
    ]
    
    # --- Pipeline para calcular métricas de Reseñas ---
    reviews_pipeline = [
        {"$match": {"professional_id": professional_obj_id}},
        {"$sort": {"created_at": -1}}, # Ordenamos de más nueva a más vieja
        {"$group": {
            "_id": "$professional_id",
            "rating_promedio": {"$avg": "$rating"},
            "total_resenas": {"$sum": 1},
            # Guardamos las 3 últimas reseñas en un array
            "ultimas_resenas": {"$push": {"rating": "$rating", "comment": "$comment"}}
        }},
        {"$project": { # Con project, limpiamos la salida
            "rating_promedio": 1,
            "total_resenas": 1,
            "ultimas_resenas": {"$slice": ["$ultimas_resenas", 3]} # Nos quedamos solo con 3
        }}
    ]

    # Ejecutamos las pipelines
    jobs_result = await job_collection.aggregate(jobs_pipeline).to_list(length=None)
    reviews_result = await review_collection.aggregate(reviews_pipeline).to_list(length=1)

    # Procesamos los resultados para armar la respuesta final
    dashboard_data = {
        "total_ingresos": 0,
        "trabajos_completados": 0,
        "trabajos_en_progreso": 0,
        "rating_promedio": 0,
        "total_resenas": 0,
        "ultimas_resenas": []
    }

    for res in jobs_result:
        if res["_id"] == "completed":
            dashboard_data["trabajos_completados"] = res["count"]
            dashboard_data["total_ingresos"] = res.get("total_budget", 0)
        elif res["_id"] == "in_progress":
            dashboard_data["trabajos_en_progreso"] = res["count"]

    if reviews_result:
        review_data = reviews_result[0]
        dashboard_data["rating_promedio"] = round(review_data.get("rating_promedio", 0), 2)
        dashboard_data["total_resenas"] = review_data.get("total_resenas", 0)
        dashboard_data["ultimas_resenas"] = review_data.get("ultimas_resenas", [])

    return dashboard_data
@router.post("/me/documents", status_code=status.HTTP_202_ACCEPTED)
async def upload_verification_documents(
    files: List[UploadFile] = File(...),
    user_id: str = Depends(get_current_user_id)
):
    """
    Permite a un profesional subir sus documentos para verificación.
    SIMULACIÓN: No guarda los archivos, solo actualiza el estado.
    """
    # 1. Verificamos que sea un profesional
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user or user.get("role") != "professional":
        raise HTTPException(status_code=403, detail="Acción no permitida.")

    # --- SIMULACIÓN DE SUBIDA DE ARCHIVOS ---
    # En un proyecto real, acá iría la lógica para subir cada 'file' a AWS S3
    # y obtener la URL de cada uno.
    # Por ahora, simulamos las URLs.
    simulated_urls = [f"https://fake-storage.com/{user_id}/{file.filename}" for file in files]
    
    # 2. Actualizamos el perfil del profesional
    await professional_collection.update_one(
        {"user_id": ObjectId(user_id)},
        {"$set": {
            "document_urls": simulated_urls,
            "verification_status": VerificationStatus.PENDING
        }},
        upsert=True # Lo crea si no existe un perfil para este usuario
    )

    return {"message": "Documentos recibidos, pendientes de revisión."}