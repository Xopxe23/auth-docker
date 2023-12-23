import asyncio
import json

import pytest
from httpx import AsyncClient
from sqlalchemy import NullPool, insert
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.auth.models import User
from app.config import settings
from app.database import Base, get_async_session
from app.main import app as fastapi_app

DB_URL = settings.TEST_DB_URL
engine = create_async_engine(DB_URL, poolclass=NullPool)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def override_get_async_session() -> AsyncSession | None:
    async with async_session_maker() as session:
        yield session

fastapi_app.dependency_overrides[get_async_session] = override_get_async_session


@pytest.fixture(scope="session", autouse=True)
async def prepare_database():

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    def open_mock_json(model: str):
        with open(f'tests/mocks/{model}.json', "r") as file:
            return json.load(file)

    users = open_mock_json("users")

    async with async_session_maker() as session:
        add_users = insert(User).values(users)
        await session.execute(add_users)
        await session.commit()


@pytest.fixture(scope="session")
def event_loop(request):
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="function")
async def async_client():
    async with AsyncClient(app=fastapi_app, base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="function")
async def authenticated_async_client():
    async with AsyncClient(app=fastapi_app, base_url="http://test") as async_client:
        await async_client.post("/auth/login", json={
            "email": "georgeduday@gmail.com",
            "password": "Geo95RGe"
        })
        yield async_client


@pytest.fixture(scope="function")
async def superuser_async_client():
    async with AsyncClient(app=fastapi_app, base_url="http://test") as async_client:
        await async_client.post("/auth/login", json={
            "email": "admin@admin.com",
            "password": "Admin123"
        })
        yield async_client
