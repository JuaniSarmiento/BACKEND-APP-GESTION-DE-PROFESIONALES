# tests/test_review_service.py
import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase

from services import user_service, professional_service, review_service
from schemas.user_schemas import UserIn
from schemas.professional_schema import ProfessionalIn
from schemas.review_schema import ReviewIn

@pytest.fixture
async def setup_data(db: AsyncIOMotorDatabase):
    """Crea un cliente, un profesional y su perfil."""
    client_user = await user_service.create_user(db, UserIn(username="test_client", email="client@test.com", password="123", firstName="Test", lastName="Client", role="client"))
    prof_user = await user_service.create_user(db, UserIn(username="test_prof", email="prof@test.com", password="123", firstName="Test", lastName="Professional", role="professional"))
    prof_profile = await professional_service.create_professional(
        db,
        ProfessionalIn(headline="Review Pro", bio="Awaiting reviews", categories=["Testing"]),
        str(prof_user["_id"])
    )
    return {"client": client_user, "professional_profile": prof_profile}

@pytest.mark.asyncio
async def test_add_review_and_update_average(db: AsyncIOMotorDatabase, setup_data):
    data = await setup_data
    client_id = str(data["client"]["_id"])
    prof_id = str(data["professional_profile"]["_id"])

    # Primera reseña
    review1_data = ReviewIn(professional_id=prof_id, rating=5, comment="Excelente!")
    await review_service.add_review(db, review1_data, client_id)
    
    prof = await professional_service.get_professional_by_id(db, prof_id)
    assert prof["avg_rating"] == 5.0
    assert prof["total_reviews"] == 1

    # Segunda reseña
    review2_data = ReviewIn(professional_id=prof_id, rating=3, comment="Bueno.")
    await review_service.add_review(db, review2_data, client_id)

    prof = await professional_service.get_professional_by_id(db, prof_id)
    assert prof["avg_rating"] == 4.0  # (5+3)/2
    assert prof["total_reviews"] == 2