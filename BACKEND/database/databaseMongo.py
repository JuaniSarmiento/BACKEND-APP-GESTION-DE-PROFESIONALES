import motor.motor_asyncio
from core.config import settings

client = motor.motor_asyncio.AsyncIOMotorClient(settings.DATABASE_URL)
db = client[settings.DB_NAME]

# Definimos las colecciones que vamos a usar
user_collection = db.get_collection("users")
professional_collection = db.get_collection("professionals")
job_collection = db.get_collection("jobs")
review_collection = db.get_collection("reviews")

# (Agregá más colecciones a medida que las necesites)