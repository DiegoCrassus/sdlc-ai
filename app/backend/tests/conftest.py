"""Shared pytest fixtures."""

from __future__ import annotations

from collections.abc import AsyncIterator

import pytest
from auth_helpers import identify_as
from httpx import ASGITransport, AsyncClient
from marketpulse.config import Settings, get_settings
from marketpulse.db.session import dispose_engine, init_db
from marketpulse.main import app


@pytest.fixture
async def client(monkeypatch: pytest.MonkeyPatch) -> AsyncIterator[AsyncClient]:
    test_settings = Settings(database_url="sqlite+aiosqlite:///:memory:", debug=True)
    get_settings.cache_clear()
    monkeypatch.setattr("marketpulse.config.get_settings", lambda: test_settings)
    monkeypatch.setattr("marketpulse.deps.get_settings", lambda: test_settings)
    monkeypatch.setattr("marketpulse.services.auth.get_settings", lambda: test_settings)
    monkeypatch.setattr("marketpulse.api.v1.routes.auth.get_settings", lambda: test_settings)
    await dispose_engine()
    await init_db(test_settings)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client

    await dispose_engine()
    get_settings.cache_clear()


@pytest.fixture
async def authed_client(client: AsyncClient) -> AsyncClient:
    await identify_as(client)
    return client
