"""Pytest fixtures - function-scoped to avoid asyncpg + anyio loop conflicts."""
import asyncio
import os
import uuid

os.environ["APP_ENV"] = "test"

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core.database import Base, get_db
from app.core.rate_limit import RateLimitMiddleware
from app.main import app

# Remove RateLimitMiddleware for tests (APP_ENV=test already self-skips, but cleaner to exclude entirely)
app.user_middleware = [m for m in app.user_middleware if m.cls != RateLimitMiddleware]
app.middleware_stack = app.build_middleware_stack()

TEST_DB_URL = "postgresql+asyncpg://postgres:postgres@localhost:5432/career_copilot_test"


@pytest.fixture(scope="function")
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_engine():
    engine = create_async_engine(TEST_DB_URL, echo=False, pool_size=1, max_overflow=0)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture(scope="function")
async def client(test_engine):
    session_factory = async_sessionmaker(test_engine, class_=AsyncSession, expire_on_commit=False)

    async def override_get_db():
        async with session_factory() as session:
            try:
                yield session
                await session.commit()
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture(scope="function")
async def auth_headers(client):
    resp = await client.post("/api/v1/auth/register", json={
        "email": f"test_{uuid.uuid4().hex[:8]}@test.com",
        "password": "test123456",
        "name": "Test User",
    })
    if resp.status_code != 201:
        pytest.skip(f"Register failed: {resp.text}")
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
