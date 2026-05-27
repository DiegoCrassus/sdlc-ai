"""Tests for Finnhub and brapi adapters."""

from __future__ import annotations

import pytest

from app.backend.src.market_data.adapters.brapi import BrapiAdapter, brapi_ticker, is_brazilian_symbol
from app.backend.src.market_data.adapters.finnhub import FinnhubAdapter, finnhub_symbol
from app.shared.types.market_data import AssetType, PriceInterval, PriceRange


@pytest.mark.parametrize(
    "symbol,expected",
    [
        ("PETR4", True),
        ("PETR4.SA", True),
        ("AAPL", False),
        ("VALE3", True),
    ],
)
def test_is_brazilian_symbol(symbol: str, expected: bool) -> None:
    assert is_brazilian_symbol(symbol) is expected


def test_brapi_ticker_normalizes_sa_suffix() -> None:
    assert brapi_ticker("PETR4.SA") == "PETR4"


def test_finnhub_index_symbol_mapping() -> None:
    assert finnhub_symbol("SPX", AssetType.INDEX) == "^GSPC"


@pytest.mark.asyncio
async def test_finnhub_quote_parses_response() -> None:
    async def mock_request(**kwargs):
        return 200, {"c": 150.0, "pc": 148.0, "h": 151.0, "l": 147.0}

    adapter = FinnhubAdapter("test-key", mock_request)
    price = await adapter.quote("AAPL", AssetType.STOCK)
    assert price is not None
    assert price.price == 150.0
    assert price.provenance.provider_name == "finnhub"


@pytest.mark.asyncio
async def test_brapi_quote_parses_response() -> None:
    async def mock_request(**kwargs):
        return 200, {
            "results": [
                {
                    "symbol": "PETR4",
                    "regularMarketPrice": 38.5,
                    "regularMarketChange": 0.5,
                    "regularMarketChangePercent": 1.3,
                }
            ]
        }

    adapter = BrapiAdapter(None, mock_request)
    price = await adapter.quote("PETR4", AssetType.STOCK)
    assert price is not None
    assert price.price == 38.5
    assert price.currency == "BRL"
    assert price.provenance.provider_name == "brapi"


@pytest.mark.asyncio
async def test_finnhub_history_parses_candles() -> None:
    async def mock_request(**kwargs):
        return 200, {
            "s": "ok",
            "t": [1_700_000_000, 1_700_086_400],
            "o": [100.0, 101.0],
            "h": [102.0, 103.0],
            "l": [99.0, 100.0],
            "c": [101.0, 102.0],
            "v": [1_000_000, 1_100_000],
        }

    adapter = FinnhubAdapter("test-key", mock_request)
    hist = await adapter.history("AAPL", AssetType.STOCK, PriceRange.WEEK, PriceInterval.DAY)
    assert hist is not None
    assert len(hist.points) == 2
    assert hist.points[0].close == 101.0
