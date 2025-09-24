from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from schemas import user_schemas
from database.databaseMongo import get_db
from utils.security import hash_password
from utils.auth_service import get_current_user # Para proteger rutas de usuario

# Simulación de un servicio de envío de emails
def send_welcome_email(email: str, name: str):
    """
    Simula el envío de un correo electrónico de bienvenida.
    En un proyecto real, esta función estaría en 'utils/email_service.py'
    y usaría una librería como 'fastapi-mail'.
    """
    print("--- TAREA EN SEGUNDO PLANO INICIADA ---")
    print(f"Enviando email de bienvenida a {name} a la dirección {email}...")
    # Simula un tiempo de envío
    import time
    time.sleep(3) 
    print(f"--- EMAIL ENVIADO a {email} ---")

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.post("/register", response_model=user_schemas.UserOut, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_in: user_schemas.UserIn, 
    background_tasks: BackgroundTasks, # Inyectamos las tareas de fondo
    db: AsyncIOMotorDatabase = Depends(get_db)
):
    """
    Registra un nuevo usuario en la base de datos.
    """
    existing_user = await db.users.find_one({"email": user_in.email})
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El email ya está registrado")

    user_doc = user_in.model_dump()
    user_doc["password"] = hash_password(user_doc["password"])
    
    result = await db.users.insert_one(user_doc)
    created_user = await db.users.find_one({"_id": result.inserted_id})

    # Agregamos la tarea a la cola para que se ejecute en segundo plano
    background_tasks.add_task(send_welcome_email, created_user["email"], created_user["first_name"])
    
    return created_user

# Endpoint de ejemplo para ver los datos del usuario logueado
@router.get("/me", response_model=user_schemas.UserOut)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    """
    Obtiene los datos del usuario actualmente autenticado.
    """
    return current_user