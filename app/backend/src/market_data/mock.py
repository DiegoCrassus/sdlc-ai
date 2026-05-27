"""Deterministic mock market data for dev, CI, and outage fallback."""

from __future__ import annotations

from builtins import range as builtin_range
from datetime import UTC, datetime, timedelta

from app.backend.src.market_data.base import MarketDataProvider
from app.backend.src.market_data.provenance import make_provenance
from app.shared.types.market_data import (
    AssetMetadata,
    AssetSearchResult,
    AssetType,
    ConfidenceLevel,
    CurrentPrice,
    DataProvenance,
    HistoricalPrices,
    MarketIndexSummary,
    MarketSummary,
    PriceInterval,
    PricePoint,
    PriceRange,
    ProviderHealth,
    SourceType,
)

_MOCK_CATALOG: dict[str, dict] = {
    "AAPL": {
        "name": "Apple Inc.",
        "asset_type": AssetType.STOCK,
        "price": 189.50,
        "currency": "USD",
        "exchange": "NASDAQ",
        "sector": "Technology",
    },
    "BTC": {
        "name": "Bitcoin",
        "asset_type": AssetType.CRYPTO,
        "price": 67500.0,
        "currency": "USD",
        "exchange": "GLOBAL",
    },
    "PETR4.SA": {
        "name": "Petrobras PN",
        "asset_type": AssetType.STOCK,
        "price": 38.20,
        "currency": "BRL",
        "exchange": "B3",
        "sector": "Energy",
    },
    "USD/BRL": {
        "name": "US Dollar / Brazilian Real",
        "asset_type": AssetType.FX,
        "price": 5.12,
        "currency": "BRL",
        "exchange": "BCB PTAX",
    },
    "SPX": {
        "name": "S&P 500",
        "asset_type": AssetType.INDEX,
        "price": 5280.0,
        "currency": "USD",
        "exchange": "INDEX",
    },
}


class MockMarketDataProvider(MarketDataProvider):
    def __init__(self, *, warning: str | None = None) -> None:
        self._warning = warning or "Simulated data — for development and testing only"

    @property
    def provider_name(self) -> str:
        return "mock"

    def _provenance(self) -> DataProvenance:
        return make_provenance(
            provider_name=self.provider_name,
            source_type=SourceType.MOCK,
            confidence_level=ConfidenceLevel.LOW,
            warning=self._warning,
        )

    async def search_assets(self, query: str, asset_type: AssetType | None = None) -> list[AssetSearchResult]:
        query_upper = query.upper()
        results: list[AssetSearchResult] = []
        for symbol, info in _MOCK_CATALOG.items():
            if asset_type and info["asset_type"] != asset_type:
                continue
            if query_upper in symbol.upper() or query.lower() in info["name"].lower():
                results.append(
                    AssetSearchResult(
                        symbol=symbol,
                        name=info["name"],
                        asset_type=info["asset_type"],
                        exchange=info.get("exchange"),
                        currency=info.get("currency"),
                        provenance=self._provenance(),
                    )
                )
        return results

    async def get_current_price(self, symbol: str, asset_type: AssetType) -> CurrentPrice | None:
        info = _MOCK_CATALOG.get(symbol.upper()) or _MOCK_CATALOG.get(symbol)
        if info is None or info["asset_type"] != asset_type:
            return None
        return CurrentPrice(
            symbol=symbol.upper(),
            asset_type=asset_type,
            price=info["price"],
            currency=info["currency"],
            change=info["price"] * 0.002,
            change_percent=0.2,
            provenance=self._provenance(),
        )

    async def get_historical_prices(
        self,
        symbol: str,
        asset_type: AssetType,
        range: PriceRange,
        interval: PriceInterval,
    ) -> HistoricalPrices | None:
        info = _MOCK_CATALOG.get(symbol.upper()) or _MOCK_CATALOG.get(symbol)
        if info is None or info["asset_type"] != asset_type:
            return None

        days = {"1d": 1, "1w": 7, "1mo": 30, "3mo": 90, "6mo": 180, "1y": 365, "5y": 365 * 5, "max": 365 * 10}[
            range.value
        ]
        base = info["price"]
        now = datetime.now(UTC)
        points: list[PricePoint] = []
        for i in builtin_range(days):
            ts = now - timedelta(days=days - i)
            close = base * (1 + 0.001 * (i - days / 2))
            points.append(
                PricePoint(
                    timestamp=ts,
                    open=close * 0.998,
                    high=close * 1.005,
                    low=close * 0.995,
                    close=close,
                    volume=1_000_000 + i * 1000,
                )
            )
        return HistoricalPrices(
            symbol=symbol.upper(),
            asset_type=asset_type,
            range=range,
            interval=interval,
            points=points,
            provenance=self._provenance(),
        )

    async def get_asset_metadata(self, symbol: str, asset_type: AssetType) -> AssetMetadata | None:
        info = _MOCK_CATALOG.get(symbol.upper()) or _MOCK_CATALOG.get(symbol)
        if info is None or info["asset_type"] != asset_type:
            return None
        return AssetMetadata(
            symbol=symbol.upper(),
            asset_type=asset_type,
            name=info["name"],
            sector=info.get("sector"),
            currency=info.get("currency"),
            exchange=info.get("exchange"),
            provenance=self._provenance(),
        )

    async def get_market_summary(self) -> MarketSummary | None:
        indexes = [
            MarketIndexSummary(symbol="SPX", name="S&P 500", price=5280.0, change_percent=0.35),
            MarketIndexSummary(symbol="NDX", name="Nasdaq 100", price=18500.0, change_percent=0.52),
        ]
        return MarketSummary(
            indexes=indexes,
            updated_at=datetime.now(UTC),
            provenance=self._provenance(),
        )

    async def get_provider_health(self) -> ProviderHealth:
        return ProviderHealth(
            provider_name=self.provider_name,
            healthy=True,
            latency_ms=0.1,
            message="Mock provider always available",
            checked_at=datetime.now(UTC),
        )
