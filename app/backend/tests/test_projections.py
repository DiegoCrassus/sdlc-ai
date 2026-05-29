"""Projection endpoint tests."""

from __future__ import annotations

import json
from pathlib import Path

import jsonschema
from httpx import AsyncClient

FORECAST_SCHEMA_PATH = (
    Path(__file__).resolve().parents[2] / "shared" / "contracts" / "forecast.schema.json"
)


def _load_forecast_schema() -> dict:
    return json.loads(FORECAST_SCHEMA_PATH.read_text(encoding="utf-8"))


async def test_projection_returns_7d_horizon(client: AsyncClient) -> None:
    response = await client.get("/api/v1/projections/BTC", params={"horizon_days": 7})
    assert response.status_code == 200
    payload = response.json()
    assert payload["asset_id"] == "BTC"
    assert payload["horizon_days"] == 7
    assert len(payload["scenarios"]) == 1
    assert len(payload["scenarios"][0]["points"]) == 7


async def test_projection_includes_indicators_and_meta(client: AsyncClient) -> None:
    response = await client.get("/api/v1/projections/BTC", params={"horizon_days": 7})
    assert response.status_code == 200
    payload = response.json()

    indicators = payload["indicators"]
    assert set(indicators) == {
        "rsi_14",
        "macd",
        "macd_signal",
        "sma_20",
        "sma_50",
        "bollinger_upper",
        "bollinger_lower",
    }

    meta = payload["meta"]
    assert meta["source"] in {"mock", "live", "fallback"}
    assert isinstance(meta["provider"], str)
    assert isinstance(meta["fetched_at"], str)


async def test_projection_matches_forecast_schema(client: AsyncClient) -> None:
    response = await client.get("/api/v1/projections/BTC", params={"horizon_days": 7})
    assert response.status_code == 200
    jsonschema.validate(instance=response.json(), schema=_load_forecast_schema())
