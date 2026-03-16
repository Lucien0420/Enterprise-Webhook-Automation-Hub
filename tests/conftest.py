"""Pytest shared fixtures."""
import asyncio
import os

import pytest
from fastapi.testclient import TestClient

os.environ["API_KEY"] = "test-api-key"
os.environ["DISCORD_WEBHOOK_URL"] = "https://discord.com/api/webhooks/test/fake"
os.environ["DATABASE_URL"] = "sqlite:///./data/test.db"


@pytest.fixture
def client():
    """FastAPI test client. Ensures DB tables exist."""
    from main import app
    from app.db.database import init_db

    async def _init():
        await init_db()

    asyncio.run(_init())
    return TestClient(app)


@pytest.fixture
def api_headers():
    return {"X-API-KEY": "test-api-key", "Content-Type": "application/json"}
