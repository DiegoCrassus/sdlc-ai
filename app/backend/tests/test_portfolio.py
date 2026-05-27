import pytest
from sqlalchemy import delete

from app.backend.database import SessionLocal
from app.backend.models import HoldingRow, PortfolioRow, TransactionRow
from app.backend.services.fallback_catalog import get_catalog_entry


@pytest.fixture(autouse=True)
async def clear_portfolio_tables():
    async with SessionLocal() as session:
        await session.execute(delete(TransactionRow))
        await session.execute(delete(HoldingRow))
        await session.execute(delete(PortfolioRow))
        await session.commit()
    yield
    async with SessionLocal() as session:
        await session.execute(delete(TransactionRow))
        await session.execute(delete(HoldingRow))
        await session.execute(delete(PortfolioRow))
        await session.commit()


@pytest.mark.asyncio
async def test_seed_portfolio_on_first_get(client):
    response = await client.get("/api/v1/portfolio")
    assert response.status_code == 200
    body = response.json()
    assert body["name"] == "My Portfolio"
    assert body["base_currency"] == "USD"
    assert body["cash_balance"] == 100_000.0
    assert body["total_value"] == 100_000.0
    assert body["total_cost_basis"] == 0.0
    assert body["unrealized_pnl"] == 0.0
    assert body["id"]


@pytest.mark.asyncio
async def test_buy_reduces_cash_creates_holding(client):
    entry = get_catalog_entry("BTC", "crypto")
    assert entry is not None
    qty = 1.0
    cost = qty * entry.base_price

    buy = await client.post(
        "/api/v1/portfolio/transactions",
        json={"type": "buy", "asset_id": "crypto:BTC", "quantity": qty},
    )
    assert buy.status_code == 201
    payload = buy.json()
    assert payload["transaction"]["type"] == "buy"
    assert payload["transaction"]["asset_id"] == "crypto:BTC"
    assert payload["transaction"]["quantity"] == qty
    assert payload["transaction"]["price"] == entry.base_price
    assert payload["transaction"]["source"] == "fallback"
    assert payload["holding"]["quantity"] == qty
    assert payload["portfolio"]["cash_balance"] == pytest.approx(100_000.0 - cost, rel=1e-2)

    holdings = await client.get("/api/v1/portfolio/holdings")
    assert holdings.status_code == 200
    assert holdings.json()["total"] == 1
    item = holdings.json()["items"][0]
    assert item["asset_id"] == "crypto:BTC"
    assert item["quantity"] == qty
    assert item["asset"]["id"] == "crypto:BTC"
    assert item["market_price"] == entry.base_price


@pytest.mark.asyncio
async def test_sell_increases_cash_reduces_holding(client):
    entry = get_catalog_entry("AAPL", "stock")
    assert entry is not None
    buy_qty = 10.0
    sell_qty = 4.0

    await client.post(
        "/api/v1/portfolio/transactions",
        json={"type": "buy", "asset_id": "stock:AAPL", "quantity": buy_qty},
    )

    sell = await client.post(
        "/api/v1/portfolio/transactions",
        json={"type": "sell", "asset_id": "stock:AAPL", "quantity": sell_qty},
    )
    assert sell.status_code == 201
    payload = sell.json()
    proceeds = sell_qty * entry.base_price
    assert payload["transaction"]["type"] == "sell"
    assert payload["holding"]["quantity"] == pytest.approx(buy_qty - sell_qty)
    expected_cash = 100_000.0 - buy_qty * entry.base_price + proceeds
    assert payload["portfolio"]["cash_balance"] == pytest.approx(expected_cash, rel=1e-2)


@pytest.mark.asyncio
async def test_sell_more_than_held_returns_422(client):
    await client.post(
        "/api/v1/portfolio/transactions",
        json={"type": "buy", "asset_id": "crypto:ETH", "quantity": 1.0},
    )

    response = await client.post(
        "/api/v1/portfolio/transactions",
        json={"type": "sell", "asset_id": "crypto:ETH", "quantity": 2.0},
    )
    assert response.status_code == 422
    err = response.json()["error"]
    assert err["code"] == "UNPROCESSABLE"


@pytest.mark.asyncio
async def test_buy_insufficient_cash_returns_422(client):
    response = await client.post(
        "/api/v1/portfolio/transactions",
        json={"type": "buy", "asset_id": "crypto:BTC", "quantity": 2.0},
    )
    assert response.status_code == 422
    err = response.json()["error"]
    assert err["code"] == "UNPROCESSABLE"


@pytest.mark.asyncio
async def test_list_transactions_after_trades(client):
    await client.post(
        "/api/v1/portfolio/transactions",
        json={"type": "buy", "asset_id": "crypto:SOL", "quantity": 1.0},
    )
    await client.post(
        "/api/v1/portfolio/transactions",
        json={"type": "sell", "asset_id": "crypto:SOL", "quantity": 0.5},
    )

    listing = await client.get("/api/v1/portfolio/transactions")
    assert listing.status_code == 200
    body = listing.json()
    assert body["total"] == 2
    assert len(body["items"]) == 2
    types = {item["type"] for item in body["items"]}
    assert types == {"buy", "sell"}


@pytest.mark.asyncio
async def test_post_unknown_asset_returns_404(client):
    response = await client.post(
        "/api/v1/portfolio/transactions",
        json={"type": "buy", "asset_id": "stock:ZZZZ", "quantity": 1},
    )
    assert response.status_code == 404
    err = response.json()["error"]
    assert err["code"] == "NOT_FOUND"
