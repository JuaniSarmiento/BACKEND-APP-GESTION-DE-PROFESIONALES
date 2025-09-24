# tests/conftest.py
import asyncio
import pytest
import pytest_asyncio # <--- 1. AGREGAMOS ESTE IMPORT
from httpx import AsyncClient
from motor.motor_asyncio import AsyncIOMotorClient
import sys
import os

# Esto le dice a Python que la carpeta raíz del proyecto existe
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from main import app
from database.databaseMongo import get_db

TEST_MONGO_URL = "mongodb://localhost:27017"
TEST_DB_NAME = "test_db_profesionales"

@pytest.fixture(scope="session")
def event_loop():
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
    yield loop
    loop.close()

# 2. CAMBIAMOS EL DECORADOR ACÁ
@pytest_asyncio.fixture(scope="function")
async def db():
    client = AsyncIOMotorClient(TEST_MONGO_URL)
    db_instance = client[TEST_DB_NAME]
    yield db_instance
    await client.drop_database(TEST_DB_NAME)
    client.close()

# 3. Y LO CAMBIAMOS ACÁ TAMBIÉN POR CONSISTENCIA
@pytest_asyncio.fixture(scope="function")
async def client(db):
    async def override_get_db():
        return db

    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as async_client:
        yield async_client
        
    app.dependency_overrides.clear()