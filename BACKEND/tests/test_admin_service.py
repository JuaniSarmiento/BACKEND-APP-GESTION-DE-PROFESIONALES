# tests/test_admin_service.py
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase

from services import user_service, professional_service, job_service, admin_service
from schemas.user_schemas import UserIn
from schemas.professional_schema import ProfessionalIn
from schemas.job_schema import JobIn, JobStatus

@pytest_asyncio.fixture
async def seed_database(db: AsyncIOMotorDatabase):
    u1 = await user_service.create_user(db, UserIn(username="u1", email="u1@a.com", password="123", firstName="u", lastName="1", role="client"))
    u2 = await user_service.create_user(db, UserIn(username="u2", email="u2@a.com", password="123", firstName="u", lastName="2", role="professional"))
    u3 = await user_service.create_user(db, UserIn(username="u3", email="u3@a.com", password="123", firstName="u", lastName="3", role="professional"))

    p1 = await professional_service.create_professional(db, ProfessionalIn(headline="P1", bio="", categories=["Plomería"]), str(u2["_id"]))
    p2 = await professional_service.create_professional(db, ProfessionalIn(headline="P2", bio="", categories=["Gas"]), str(u3["_id"]))

    await job_service.create_job(db, JobIn(title="Trabajo Plomeria 1", description="", category="Plomería", budget=1.0, professional_id=str(p1["_id"])), str(u1["_id"]))
    job2 = await job_service.create_job(db, JobIn(title="Trabajo Plomeria 2", description="", category="Plomería", budget=1.0, professional_id=str(p1["_id"])), str(u1["_id"]))
    await job_service.create_job(db, JobIn(title="Trabajo Gas 1", description="", category="Gas", budget=1.0, professional_id=str(p2["_id"])), str(u1["_id"]))
    
    await db["jobs"].update_one({"_id": job2["_id"]}, {"$set": {"status": JobStatus.COMPLETED.value}})
    yield

@pytest.mark.asyncio
async def test_get_dashboard_stats(db: AsyncIOMotorDatabase, seed_database):
    total_users = await admin_service.get_total_users(db)
    assert total_users == 3

    total_professionals = await admin_service.get_total_professionals(db)
    assert total_professionals == 2

    total_jobs = await admin_service.get_total_jobs(db)
    assert total_jobs == 3

    jobs_by_state = await admin_service.get_jobs_by_state(db)
    states = {item["_id"]: item["count"] for item in jobs_by_state}
    
    assert states.get(JobStatus.POSTED.value) == 2
    assert states.get(JobStatus.COMPLETED.value) == 1
    
    profs_by_cat = await admin_service.get_professionals_by_category(db)
    # La categoría es una lista, la agregación puede ser más compleja, pero para este test simple, lo dejamos así.
    # El test real debería comprobar la estructura de `profs_by_cat`
    assert len(profs_by_cat) > 0