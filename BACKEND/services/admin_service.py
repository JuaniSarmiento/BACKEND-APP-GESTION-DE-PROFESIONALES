# services/admin_service.py
from motor.motor_asyncio import AsyncIOMotorDatabase

async def get_total_users(db: AsyncIOMotorDatabase) -> int:
    return await db["users"].count_documents({})

async def get_total_professionals(db: AsyncIOMotorDatabase) -> int:
    return await db["professionals"].count_documents({})

async def get_total_jobs(db: AsyncIOMotorDatabase) -> int:
    return await db["jobs"].count_documents({})

async def get_jobs_by_state(db: AsyncIOMotorDatabase) -> list:
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    cursor = db["jobs"].aggregate(pipeline)
    return await cursor.to_list(length=None)

async def get_professionals_by_category(db: AsyncIOMotorDatabase) -> list:
    pipeline = [
        {"$group": {"_id": "$categories", "count": {"$sum": 1}}} # Corregido a 'categories' que es una lista
    ]
    cursor = db["professionals"].aggregate(pipeline)
    return await cursor.to_list(length=None)