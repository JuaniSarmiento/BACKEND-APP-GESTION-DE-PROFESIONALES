# tests/test_professional_service.py
import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase
from services import user_service, professional_service
from schemas.user_schemas import UserIn
from schemas.professional_schema import ProfessionalIn, ProfessionalUpdate

@pytest.fixture
async def setup_user(db: AsyncIOMotorDatabase):
    user_data = UserIn(
        username="prof_user", 
        email="prof@user.com", 
        password="123", 
        firstName="Profesional", 
        lastName="De Prueba", 
        role="professional"
    )
    user = await user_service.create_user(db, user_data)
    return user

@pytest.mark.asyncio
async def test_create_professional(db: AsyncIOMotorDatabase, setup_user):
    user = await setup_user
    prof_data = ProfessionalIn(
        headline="El mejor plomero de la zona oeste.",
        bio="Reparaciones e instalaciones de todo tipo. Matriculado.",
        categories=["Plomería", "Gas"]
    )
    
    created_prof = await professional_service.create_professional(db, prof_data, str(user["_id"]))
    
    assert created_prof is not None
    assert created_prof["categories"] == ["Plomería", "Gas"]
    assert created_prof["user_id"] == user["_id"]
    assert created_prof["avg_rating"] == 0.0
    assert created_prof["total_reviews"] == 0

@pytest.mark.asyncio
async def test_update_professional(db: AsyncIOMotorDatabase, setup_user):
    user = await setup_user
    prof_data = ProfessionalIn(
        headline="Gasista Matriculado", 
        bio="Instalaciones y arreglos.", 
        categories=["Gas"]
    )
    created_prof = await professional_service.create_professional(db, prof_data, str(user["_id"]))
    prof_id = str(created_prof["_id"])
    
    update_data = ProfessionalUpdate(bio="El mejor gasista, matriculado y con garantía.")
    
    updated_prof = await professional_service.update_professional(db, prof_id, update_data)
    
    assert updated_prof is not None
    assert updated_prof["bio"] == "El mejor gasista, matriculado y con garantía."
    assert updated_prof["headline"] == "Gasista Matriculado"