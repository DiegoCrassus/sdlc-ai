"""Projection endpoint tests."""

from __future__ import annotations

from httpx import AsyncClient


async def test_projection_returns_7d_horizon(client: AsyncClient) -> None:
    response = await client.get("/api/v1/projections/BTC", params={"horizon_days": 7})
    assert response.status_code == 200
    payload = response.json()
    assert payload["asset_id"] == "BTC"
    assert payload["horizon_days"] == 7
    assert len(payload["scenarios"]) == 1
    assert len(payload["scenarios"][0]["points"]) == 7
