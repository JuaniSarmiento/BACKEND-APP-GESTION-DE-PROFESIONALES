# routers/admin_router.py
from fastapi import APIRouter, Depends
from motor.motor_asyncio import AsyncIOMotorDatabase

from database.databaseMongo import get_db
from schemas.dashboard_schema import DashboardStats
from services import admin_service

router = APIRouter(prefix="/admin", tags=["Admin"])

@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(db: AsyncIOMotorDatabase = Depends(get_db)):
    total_users = await admin_service.get_total_users(db)
    total_professionals = await admin_service.get_total_professionals(db)
    total_jobs = await admin_service.get_total_jobs(db)
    jobs_by_state = await admin_service.get_jobs_by_state(db)
    professionals_by_category = await admin_service.get_professionals_by_category(db)
    
    return DashboardStats(
        total_users=total_users,
        total_professionals=total_professionals,
        total_jobs=total_jobs,
        jobs_by_state=jobs_by_state,
        professionals_by_category=professionals_by_category,
    )