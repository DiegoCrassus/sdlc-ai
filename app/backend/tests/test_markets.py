"""Market data endpoint tests."""

from __future__ import annotations

from httpx import AsyncClient


async def test_overview_returns_mock_data(client: AsyncClient) -> None:
    response = await client.get("/api/v1/markets/overview")
    assert response.status_code == 200
    payload = response.json()
    assert payload["btc_dominance_percent"] > 0
    assert len(payload["indices"]) >= 1
    assert len(payload["top_gainers"]) >= 1
    assert payload["meta"]["provider"] == "mock"


async def test_quotes_returns_requested_symbols(client: AsyncClient) -> None:
    response = await client.get("/api/v1/markets/quotes", params={"symbols": "AAPL,BTC"})
    assert response.status_code == 200
    payload = response.json()
    assert len(payload) == 2
    symbols = {item["symbol"] for item in payload}
    assert symbols == {"AAPL", "BTC"}


async def test_ohlcv_returns_series(client: AsyncClient) -> None:
    response = await client.get("/api/v1/markets/AAPL/ohlcv", params={"interval": "1d", "limit": 30})
    assert response.status_code == 200
    payload = response.json()
    assert payload["asset_id"] == "AAPL"
    assert len(payload["points"]) == 30
    first = payload["points"][0]
    assert {"timestamp", "open", "high", "low", "close", "volume"} <= set(first.keys())


async def test_search_returns_hits(client: AsyncClient) -> None:
    response = await client.get("/api/v1/markets/search", params={"q": "bit"})
    assert response.status_code == 200
    payload = response.json()
    assert any(item["symbol"] == "BTC" for item in payload)
