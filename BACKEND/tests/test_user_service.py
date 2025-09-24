# tests/test_user_service.py
import pytest
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from services import user_service
from schemas.user_schemas import UserIn
from utils.security import verify_password

@pytest.mark.asyncio
async def test_create_user(db: AsyncIOMotorDatabase):
    user_data = UserIn(
        username="testjuani",
        email="test@juani.com",
        password="password123",
        firstName="Juan Ignacio",
        lastName="Sarmiento",
        role="client"
    )
    
    created_user = await user_service.create_user(db, user_data)
    
    assert created_user is not None
    assert created_user["email"] == user_data.email
    assert created_user["username"] == user_data.username
    assert "_id" in created_user
    assert created_user["password"] != user_data.password
    assert verify_password(user_data.password, created_user["password"])

@pytest.mark.asyncio
async def test_get_user_by_email(db: AsyncIOMotorDatabase):
    user_data = UserIn(
        username="testjuani2",
        email="test2@juani.com",
        password="password123",
        firstName="Juan",
        lastName="Sarmiento",
        role="professional"
    )
    await user_service.create_user(db, user_data)
    
    found_user = await user_service.get_user_by_email(db, "test2@juani.com")
    assert found_user is not None
    assert found_user["username"] == "testjuani2"

@pytest.mark.asyncio
async def test_get_user_by_id(db: AsyncIOMotorDatabase):
    user_data = UserIn(
        username="testjuani3",
        email="test3@juani.com",
        password="password123",
        firstName="Juan",
        lastName="Sarmiento",
        role="client"
    )
    created_user = await user_service.create_user(db, user_data)
    user_id = str(created_user["_id"])
    
    found_user = await user_service.get_user_by_id(db, user_id)
    assert found_user is not None
    assert found_user["email"] == "test3@juani.com"

@pytest.mark.asyncio
async def test_delete_user(db: AsyncIOMotorDatabase):
    user_data = UserIn(
        username="todelete",
        email="delete@me.com",
        password="password123",
        firstName="Delete",
        lastName="Me",
        role="client"
    )
    created_user = await user_service.create_user(db, user_data)
    user_id = str(created_user["_id"])

    deleted = await user_service.delete_user(db, user_id)
    assert deleted is True
    
    found_user = await user_service.get_user_by_id(db, user_id)
    assert found_user is None