# services/job_service.py
from typing import List, Optional
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime

from schemas.job_schema import JobIn, JobUpdate, JobStatus

async def create_job(db: AsyncIOMotorDatabase, job_in: JobIn, user_id: str) -> dict:
    job_dict = job_in.model_dump()
    job_dict["client_id"] = ObjectId(user_id)
    job_dict["professional_id"] = ObjectId(job_in.professional_id)
    job_dict["created_at"] = datetime.utcnow()
    job_dict["status"] = JobStatus.POSTED.value
    
    result = await db["jobs"].insert_one(job_dict)
    created_job = await db["jobs"].find_one({"_id": result.inserted_id})
    return created_job

async def get_all_jobs(db: AsyncIOMotorDatabase) -> List[dict]:
    jobs_cursor = db["jobs"].find()
    return await jobs_cursor.to_list(length=None)

async def get_job_by_id(db: AsyncIOMotorDatabase, job_id: str) -> Optional[dict]:
    return await db["jobs"].find_one({"_id": ObjectId(job_id)})

async def update_job(db: AsyncIOMotorDatabase, job_id: str, job_update: JobUpdate) -> Optional[dict]:
    update_data = {k: v for k, v in job_update.model_dump(exclude_unset=True).items() if v is not None}
    if not update_data:
        return None
    if 'status' in update_data and isinstance(update_data['status'], JobStatus):
        update_data['status'] = update_data['status'].value

    await db["jobs"].update_one(
        {"_id": ObjectId(job_id)},
        {"$set": update_data}
    )
    return await db["jobs"].find_one({"_id": ObjectId(job_id)})

async def delete_job(db: AsyncIOMotorDatabase, job_id: str) -> bool:
    result = await db["jobs"].delete_one({"_id": ObjectId(job_id)})
    return result.deleted_count > 0