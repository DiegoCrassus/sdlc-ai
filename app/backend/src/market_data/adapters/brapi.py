"""brapi.dev free API adapter — Brazilian equities (B3)."""

from __future__ import annotations

from collections.abc import Callable, Coroutine
from datetime import UTC, datetime
from typing import Any

from app.backend.src.market_data.provenance import make_provenance
from app.shared.types.market_data import (
    AssetMetadata,
    AssetSearchResult,
    AssetType,
    ConfidenceLevel,
    CurrentPrice,
    HistoricalPrices,
    PriceInterval,
    PricePoint,
    PriceRange,
    SourceType,
)

_BRAPI_BASE = "https://brapi.dev/api"
_BRAPI_TEST_TICKERS = frozenset({"PETR4", "MGLU3", "VALE3", "ITUB4"})


def is_brazilian_symbol(symbol: str) -> bool:
    """Detect B3 tickers (PETR4, PETR4.SA) vs US tickers."""
    s = symbol.upper().removesuffix(".SA")
    return len(s) >= 5 and s[-1].isdigit() and s[-2].isalpha()


def brapi_ticker(symbol: str) -> str:
    return symbol.upper().removesuffix(".SA")


def brapi_range_param(range: PriceRange) -> str:
    mapping = {
        PriceRange.DAY: "1d",
        PriceRange.WEEK: "5d",
        PriceRange.MONTH: "1mo",
        PriceRange.THREE_MONTHS: "3mo",
        PriceRange.SIX_MONTHS: "6mo",
        PriceRange.YEAR: "1y",
        PriceRange.FIVE_YEARS: "5y",
        PriceRange.MAX: "max",
    }
    return mapping[range]


RequestFn = Callable[..., Coroutine[Any, Any, tuple[int, Any | None]]]


class BrapiAdapter:
    """Free tier: 15k req/month; PETR4/MGLU3/VALE3/ITUB4 work without token."""

    def __init__(self, api_key: str | None, request: RequestFn) -> None:
        self._api_key = api_key
        self._request = request

    def _auth_params(self, ticker: str) -> dict[str, str]:
        if self._api_key and ticker not in _BRAPI_TEST_TICKERS:
            return {"token": self._api_key}
        if self._api_key:
            return {"token": self._api_key}
        return {}

    def _auth_headers(self, ticker: str) -> dict[str, str]:
        if self._api_key:
            return {"Authorization": f"Bearer {self._api_key}"}
        if ticker in _BRAPI_TEST_TICKERS:
            return {}
        return {}

    async def search(self, query: str) -> list[AssetSearchResult]:
        ticker = brapi_ticker(query) if is_brazilian_symbol(query) else query.upper()
        if ticker not in _BRAPI_TEST_TICKERS and not self._api_key:
            return []
        _, data = await self._quote_payload(ticker)
        if not data or not data.get("results"):
            return []
        item = data["results"][0]
        return [
            AssetSearchResult(
                symbol=item.get("symbol", ticker),
                name=item.get("longName") or item.get("shortName", ticker),
                asset_type=AssetType.STOCK,
                exchange="B3",
                currency="BRL",
                provenance=make_provenance(
                    provider_name="brapi",
                    source_type=SourceType.API,
                    source_url=f"{_BRAPI_BASE}/quote/{ticker}",
                    is_delayed=True,
                    confidence_level=ConfidenceLevel.HIGH,
                ),
            )
        ]

    async def _quote_payload(self, ticker: str) -> tuple[int, Any | None]:
        params = {"range": "1d", "interval": "1d", **self._auth_params(ticker)}
        return await self._request(
            url=f"{_BRAPI_BASE}/quote/{ticker}",
            params=params,
            headers=self._auth_headers(ticker),
            symbol=ticker,
            asset_type=AssetType.STOCK,
            sub_provider="brapi",
        )

    async def quote(self, symbol: str, asset_type: AssetType) -> CurrentPrice | None:
        ticker = brapi_ticker(symbol)
        if ticker not in _BRAPI_TEST_TICKERS and not self._api_key:
            return None
        _, data = await self._quote_payload(ticker)
        if not data or not data.get("results"):
            return None
        item = data["results"][0]
        price = item.get("regularMarketPrice")
        if price is None:
            return None
        return CurrentPrice(
            symbol=ticker,
            asset_type=asset_type,
            price=float(price),
            currency="BRL",
            change=float(item["regularMarketChange"]) if item.get("regularMarketChange") is not None else None,
            change_percent=float(item["regularMarketChangePercent"])
            if item.get("regularMarketChangePercent") is not None
            else None,
            provenance=make_provenance(
                provider_name="brapi",
                source_type=SourceType.API,
                source_url=f"{_BRAPI_BASE}/quote/{ticker}",
                is_delayed=True,
                confidence_level=ConfidenceLevel.HIGH,
                warning="B3 data updated every ~30 min on free tier",
            ),
        )

    async def history(
        self,
        symbol: str,
        asset_type: AssetType,
        range: PriceRange,
        interval: PriceInterval,
    ) -> HistoricalPrices | None:
        if interval not in (PriceInterval.DAY, PriceInterval.WEEK):
            return None
        ticker = brapi_ticker(symbol)
        if ticker not in _BRAPI_TEST_TICKERS and not self._api_key:
            return None
        params = {
            "range": brapi_range_param(range),
            "interval": "1d",
            **self._auth_params(ticker),
        }
        _, data = await self._request(
            url=f"{_BRAPI_BASE}/quote/{ticker}",
            params=params,
            headers=self._auth_headers(ticker),
            symbol=ticker,
            asset_type=asset_type,
            sub_provider="brapi",
        )
        if not data or not data.get("results"):
            return None
        item = data["results"][0]
        hist = item.get("historicalDataPrice") or []
        points = [
            PricePoint(
                timestamp=datetime.fromtimestamp(row["date"], tz=UTC),
                open=float(row["open"]) if row.get("open") is not None else None,
                high=float(row["high"]) if row.get("high") is not None else None,
                low=float(row["low"]) if row.get("low") is not None else None,
                close=float(row["close"]),
                volume=float(row["volume"]) if row.get("volume") is not None else None,
            )
            for row in hist
        ]
        if not points:
            return None
        return HistoricalPrices(
            symbol=ticker,
            asset_type=asset_type,
            range=range,
            interval=interval,
            points=points,
            provenance=make_provenance(
                provider_name="brapi",
                source_type=SourceType.API,
                source_url=f"{_BRAPI_BASE}/quote/{ticker}",
                is_delayed=True,
                confidence_level=ConfidenceLevel.HIGH,
            ),
        )

    async def profile(self, symbol: str, asset_type: AssetType) -> AssetMetadata | None:
        ticker = brapi_ticker(symbol)
        if ticker not in _BRAPI_TEST_TICKERS and not self._api_key:
            return None
        params = {"modules": "summaryProfile", **self._auth_params(ticker)}
        _, data = await self._request(
            url=f"{_BRAPI_BASE}/quote/{ticker}",
            params=params,
            headers=self._auth_headers(ticker),
            symbol=ticker,
            asset_type=asset_type,
            sub_provider="brapi",
        )
        if not data or not data.get("results"):
            return None
        item = data["results"][0]
        summary = item.get("summaryProfile") or {}
        return AssetMetadata(
            symbol=ticker,
            asset_type=asset_type,
            name=item.get("longName") or item.get("shortName", ticker),
            description=summary.get("longBusinessSummary"),
            sector=summary.get("sectorDisp") or summary.get("sector"),
            industry=summary.get("industryDisp") or summary.get("industry"),
            currency="BRL",
            exchange="B3",
            website=summary.get("website"),
            provenance=make_provenance(
                provider_name="brapi",
                source_type=SourceType.API,
                source_url=f"{_BRAPI_BASE}/quote/{ticker}",
                confidence_level=ConfidenceLevel.HIGH,
            ),
        )
