"""Shared pytest fixtures."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from marketpulse.main import app


@pytest.fixture
async def client() -> AsyncClient:
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as async_client:
        yield async_client
