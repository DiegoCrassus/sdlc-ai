"""Test helpers for auth flows."""

from __future__ import annotations

from httpx import AsyncClient


async def identify_as(client: AsyncClient, email: str = "user@example.com") -> dict:
    """POST identify and return response JSON (cookies stored on client)."""
    response = await client.post("/api/v1/auth/identify", json={"email": email})
    assert response.status_code == 200
    return response.json()
