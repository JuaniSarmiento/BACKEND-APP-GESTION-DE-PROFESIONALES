# services/user_service.py
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from schemas.user_schemas import UserIn, UserOut
from utils.security import hash_password


async def get_user_by_id(db: AsyncIOMotorDatabase, user_id: str) -> Optional[dict]:
    """Busca un usuario por su ID."""
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    return user

async def get_user_by_email(db: AsyncIOMotorDatabase, email: str) -> Optional[dict]:
    """Busca un usuario por su email."""
    user = await db["users"].find_one({"email": email})
    return user

async def get_user_by_username(db: AsyncIOMotorDatabase, username: str) -> Optional[dict]:
    """Busca un usuario por su username."""
    user = await db["users"].find_one({"username": username})
    return user

async def get_all_users(db: AsyncIOMotorDatabase) -> List[UserOut]:
    """Obtiene todos los usuarios de la base de datos."""
    users_cursor = db["users"].find()
    users = await users_cursor.to_list(length=None)
    return [UserOut(**user) for user in users]

async def create_user(db: AsyncIOMotorDatabase, user_in: UserIn) -> dict:
    """Crea un nuevo usuario en la base de datos."""
    hashed_password = hash_password(user_in.password)
    user_dict = user_in.model_dump()
    user_dict["password"] = hashed_password
    
    result = await db["users"].insert_one(user_dict)
    created_user = await db["users"].find_one({"_id": result.inserted_id})
    return created_user

async def delete_user(db: AsyncIOMotorDatabase, user_id: str) -> bool:
    """Elimina un usuario por su ID."""
    result = await db["users"].delete_one({"_id": ObjectId(user_id)})
    return result.deleted_count > 0