"""Integration tests for market data HTTP API."""

from __future__ import annotations

import os

import pytest
from fastapi.testclient import TestClient

os.environ.setdefault("MARKET_DATA_MODE", "mock")
os.environ.setdefault("DATABASE_URL", "sqlite+aiosqlite:///./data/test_market_api.db")

from app.backend.src.main import create_app


@pytest.fixture
def client() -> TestClient:
    with TestClient(create_app()) as test_client:
        yield test_client


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_search_mock(client: TestClient) -> None:
    response = client.get("/api/v1/market/search", params={"q": "apple", "asset_type": "stock"})
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["symbol"] == "AAPL"


def test_current_price_mock(client: TestClient) -> None:
    response = client.get("/api/v1/market/price/AAPL", params={"asset_type": "stock"})
    assert response.status_code == 200
    body = response.json()
    assert body["price"] == 189.5
    assert body["provenance"]["source_type"] == "mock"


def test_history_mock(client: TestClient) -> None:
    response = client.get(
        "/api/v1/market/history/AAPL",
        params={"asset_type": "stock", "range": "1mo", "interval": "1d"},
    )
    assert response.status_code == 200
    assert len(response.json()["points"]) >= 1


def test_metadata_mock(client: TestClient) -> None:
    response = client.get("/api/v1/market/metadata/AAPL", params={"asset_type": "stock"})
    assert response.status_code == 200
    assert response.json()["name"] == "Apple Inc."


def test_summary_mock(client: TestClient) -> None:
    response = client.get("/api/v1/market/summary")
    assert response.status_code == 200
    assert len(response.json()["indexes"]) >= 1


def test_provider_health_mock(client: TestClient) -> None:
    response = client.get("/api/v1/market/providers/health")
    assert response.status_code == 200
    assert response.json()["healthy"] is True
