# tests/test_job_service.py
import pytest
import pytest_asyncio
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from services import user_service, professional_service, job_service
from schemas.user_schemas import UserIn
from schemas.professional_schema import ProfessionalIn
from schemas.job_schema import JobIn, JobUpdate, JobStatus

@pytest_asyncio.fixture
async def setup_users_and_prof(db: AsyncIOMotorDatabase):
    client_user = await user_service.create_user(db, UserIn(username="client", email="client@a.com", password="123", firstName="Cliente", lastName="Final", role="client"))
    prof_user = await user_service.create_user(db, UserIn(username="prof", email="prof@a.com", password="123", firstName="Pro", lastName="Fesional", role="professional"))
    prof_profile = await professional_service.create_professional(
        db, 
        ProfessionalIn(headline="Electricista de Confianza", bio="220v y 380v.", categories=["Electricidad"]), 
        str(prof_user["_id"])
    )
    return {"client": client_user, "professional": prof_profile}

@pytest.mark.asyncio
async def test_create_job(db: AsyncIOMotorDatabase, setup_users_and_prof):
    # CORRECCIÓN ACÁ: Sacamos el 'await'
    data = setup_users_and_prof
    client_id = str(data["client"]["_id"])
    prof_id = str(data["professional"]["_id"])

    job_data = JobIn(
        title="Arreglar enchufe",
        description="El enchufe de la cocina tiró chispas.",
        category="Electricidad",
        budget=1500.50,
        professional_id=prof_id
    )
    
    created_job = await job_service.create_job(db, job_data, client_id)
    
    assert created_job is not None
    assert created_job["title"] == "Arreglar enchufe"
    assert created_job["client_id"] == ObjectId(client_id)
    assert created_job["professional_id"] == ObjectId(prof_id)
    assert created_job["status"] == JobStatus.POSTED

@pytest.mark.asyncio
async def test_update_job_status(db: AsyncIOMotorDatabase, setup_users_and_prof):
    # CORRECCIÓN ACÁ: Sacamos el 'await'
    data = setup_users_and_prof
    client_id = str(data["client"]["_id"])
    prof_id = str(data["professional"]["_id"])
    job_data = JobIn(title="Cambiar térmica", description="Saltó y no levantó más.", category="Electricidad", budget=3000.0, professional_id=prof_id)
    created_job = await job_service.create_job(db, job_data, client_id)
    job_id = str(created_job["_id"])

    update_data = JobUpdate(status=JobStatus.COMPLETED)
    updated_job = await job_service.update_job(db, job_id, update_data)

    assert updated_job is not None
    assert updated_job["status"] == JobStatus.COMPLETED