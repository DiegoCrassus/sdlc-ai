import pytest


@pytest.mark.asyncio
async def test_search_fallback_catalog(client):
    response = await client.get("/api/v1/assets/search", params={"q": "apple"})
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert body["total"] >= 1
    assert any(item["symbol"] == "AAPL" for item in body["items"])
    assert body["items"][0]["source"] == "fallback"


@pytest.mark.asyncio
async def test_quote_fallback_known_symbol(client):
    response = await client.get("/api/v1/quotes/crypto:BTC")
    assert response.status_code == 200
    body = response.json()
    assert body["asset_id"] == "crypto:BTC"
    assert body["source"] == "fallback"
    assert body["price"] > 0


@pytest.mark.asyncio
async def test_invalid_asset_id_returns_400(client):
    response = await client.get("/api/v1/assets/invalid-id")
    assert response.status_code == 400
    err = response.json()["error"]
    assert err["code"] == "VALIDATION_ERROR"


@pytest.mark.asyncio
async def test_unknown_asset_returns_404(client):
    response = await client.get("/api/v1/assets/stock:ZZZZ")
    assert response.status_code == 404
    err = response.json()["error"]
    assert err["code"] == "NOT_FOUND"


@pytest.mark.asyncio
async def test_history_returns_ohlcv_with_source(client):
    response = await client.get("/api/v1/history/stock:AAPL")
    assert response.status_code == 200
    body = response.json()
    assert body["asset_id"] == "stock:AAPL"
    assert body["source"] == "fallback"
    assert body["interval"] == "1d"
    assert len(body["points"]) >= 1
    point = body["points"][0]
    for field in ("timestamp", "open", "high", "low", "close"):
        assert field in point


@pytest.mark.asyncio
async def test_batch_quotes_with_missing(client):
    response = await client.get(
        "/api/v1/quotes",
        params={"ids": "crypto:BTC,stock:ZZZZ"},
    )
    assert response.status_code == 200
    body = response.json()
    assert len(body["items"]) == 1
    assert body["items"][0]["asset_id"] == "crypto:BTC"
    assert "stock:ZZZZ" in body["missing"]


@pytest.mark.asyncio
async def test_get_asset_by_id(client):
    response = await client.get("/api/v1/assets/stock:AAPL")
    assert response.status_code == 200
    body = response.json()
    assert body["id"] == "stock:AAPL"
    assert body["class"] == "stock"
    assert body["symbol"] == "AAPL"
