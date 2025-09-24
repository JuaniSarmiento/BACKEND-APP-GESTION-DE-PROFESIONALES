# database/databaseMongo.py
import os
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

# Cargamos las variables de entorno
load_dotenv()

MONGO_URL = os.getenv("MONGO_URL")
MONGO_DATABASE = os.getenv("MONGO_DATABASE")

if not MONGO_URL or not MONGO_DATABASE:
    raise ValueError("MONGO_URL y MONGO_DATABASE deben estar definidos en el .env")

# --- Creamos el cliente y la conexión a la base de datos ---
client = AsyncIOMotorClient(MONGO_URL)
database = client[MONGO_DATABASE]

# --- ¡¡ACÁ ESTÁ LA FUNCIÓN QUE FALTABA!! ---
# Esta es la función que FastAPI usa como dependencia para "inyectar" la DB
async def get_db():
    """
    Dependencia de FastAPI para obtener la instancia de la base de datos.
    """
    return database