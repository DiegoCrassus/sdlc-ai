"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from httpx import ASGITransport, AsyncClient
from marketpulse.config import Settings, get_settings
from marketpulse.db.session import dispose_engine, init_db
from marketpulse.main import app


@pytest.fixture
async def client() -> AsyncIterator[AsyncClient]:
    test_settings = Settings(database_url="sqlite+aiosqlite:///:memory:")
    get_settings.cache_clear()
    await dispose_engine()
    await init_db(test_settings)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    await dispose_engine()
    get_settings.cache_clear()
