"""Mock market data provider with seeded realistic data."""

from __future__ import annotations

import hashlib
import random
from datetime import UTC, datetime, timedelta

from marketpulse.domain.enums import AssetClass, DataSource, Interval
from marketpulse.domain.models import (
    AssetProjection,
    IndexSnapshot,
    MarketMover,
    MarketOverview,
    PriceHistory,
    PricePoint,
    Quote,
    SearchHit,
    SourceMeta,
)
from marketpulse.providers.base import MarketDataProvider
from marketpulse.services.projection import build_projection

ASSET_CATALOG: dict[str, dict[str, object]] = {
    "AAPL": {
        "name": "Apple Inc.",
        "asset_class": AssetClass.STOCK,
        "base_price": 189.50,
        "volume": 52_000_000,
        "market_cap": 2_900_000_000_000,
    },
    "MSFT": {
        "name": "Microsoft Corp.",
        "asset_class": AssetClass.STOCK,
        "base_price": 415.20,
        "volume": 22_000_000,
        "market_cap": 3_100_000_000_000,
    },
    "NVDA": {
        "name": "NVIDIA Corp.",
        "asset_class": AssetClass.STOCK,
        "base_price": 875.40,
        "volume": 48_000_000,
        "market_cap": 2_150_000_000_000,
    },
    "BTC": {
        "name": "Bitcoin",
        "asset_class": AssetClass.CRYPTO,
        "base_price": 67_250.0,
        "volume": 28_000_000_000,
        "market_cap": 1_320_000_000_000,
    },
    "ETH": {
        "name": "Ethereum",
        "asset_class": AssetClass.CRYPTO,
        "base_price": 3_420.0,
        "volume": 14_000_000_000,
        "market_cap": 410_000_000_000,
    },
    "SOL": {
        "name": "Solana",
        "asset_class": AssetClass.CRYPTO,
        "base_price": 148.75,
        "volume": 2_800_000_000,
        "market_cap": 68_000_000_000,
    },
    "EUR/USD": {
        "name": "Euro / US Dollar",
        "asset_class": AssetClass.FOREX,
        "base_price": 1.0842,
        "volume": None,
        "market_cap": None,
    },
    "SPX": {
        "name": "S&P 500",
        "asset_class": AssetClass.INDEX,
        "base_price": 5_280.0,
        "volume": None,
        "market_cap": None,
    },
    "NDX": {
        "name": "NASDAQ 100",
        "asset_class": AssetClass.INDEX,
        "base_price": 18_650.0,
        "volume": None,
        "market_cap": None,
    },
}


class MockMarketDataProvider(MarketDataProvider):
    """Deterministic mock provider for local development and tests."""

    def __init__(self, seed: int = 42) -> None:
        self._seed = seed

    @property
    def provider_name(self) -> str:
        return "mock"

    def _rng(self, symbol: str) -> random.Random:
        digest = hashlib.sha256(f"{self._seed}:{symbol}".encode()).hexdigest()
        return random.Random(int(digest[:8], 16))

    def _meta(self) -> SourceMeta:
        return SourceMeta(
            source=DataSource.MOCK,
            provider=self.provider_name,
            fetched_at=datetime.now(tz=UTC),
            latency_ms=0.5,
        )

    def _price_state(self, symbol: str) -> tuple[float, float, float]:
        catalog = ASSET_CATALOG[symbol.upper()]
        rng = self._rng(symbol)
        base = float(catalog["base_price"])
        drift = rng.uniform(-0.025, 0.035)
        price = base * (1 + drift)
        change_percent = rng.uniform(-4.5, 4.5)
        change = price * change_percent / 100
        return price, change, change_percent

    async def get_overview(self) -> MarketOverview:
        quotes = [await self.get_quote(symbol) for symbol in ("BTC", "ETH", "AAPL", "MSFT", "NVDA")]
        sorted_quotes = sorted(quotes, key=lambda quote: quote.change_percent, reverse=True)
        indices = [
            IndexSnapshot(
                asset_id="SPX",
                name="S&P 500",
                value=5280.42,
                change_percent=0.62,
            ),
            IndexSnapshot(
                asset_id="NDX",
                name="NASDAQ 100",
                value=18654.11,
                change_percent=0.88,
            ),
            IndexSnapshot(
                asset_id="BTC",
                name="Bitcoin",
                value=67250.0,
                change_percent=sorted_quotes[0].change_percent,
            ),
        ]
        movers = [
            MarketMover(
                asset_id=quote.asset_id,
                symbol=quote.symbol,
                name=quote.name,
                asset_class=quote.asset_class,
                price=quote.price,
                change_percent=quote.change_percent,
            )
            for quote in quotes
        ]
        gainers = sorted(movers, key=lambda item: item.change_percent, reverse=True)[:3]
        losers = sorted(movers, key=lambda item: item.change_percent)[:3]
        return MarketOverview(
            total_market_cap_usd=3_200_000_000_000,
            total_volume_24h_usd=98_500_000_000,
            btc_dominance_percent=52.4,
            fear_greed_index=68,
            active_assets=len(ASSET_CATALOG),
            indices=indices,
            top_gainers=gainers,
            top_losers=losers,
            meta=self._meta(),
        )

    async def get_quote(self, symbol: str) -> Quote:
        key = symbol.upper()
        if key not in ASSET_CATALOG:
            raise KeyError(f"Unknown symbol: {symbol}")
        catalog = ASSET_CATALOG[key]
        price, change, change_percent = self._price_state(key)
        rng = self._rng(key)
        high = price * (1 + abs(rng.uniform(0.005, 0.02)))
        low = price * (1 - abs(rng.uniform(0.005, 0.02)))
        return Quote(
            asset_id=key,
            symbol=key,
            name=str(catalog["name"]),
            asset_class=AssetClass(catalog["asset_class"]),
            price=round(price, 4),
            change=round(change, 4),
            change_percent=round(change_percent, 2),
            volume_24h=catalog["volume"],  # type: ignore[arg-type]
            market_cap=catalog["market_cap"],  # type: ignore[arg-type]
            high_24h=round(high, 4),
            low_24h=round(low, 4),
            currency="USD",
            meta=self._meta(),
        )

    async def get_ohlcv(self, symbol: str, interval: Interval, limit: int) -> PriceHistory:
        key = symbol.upper()
        if key not in ASSET_CATALOG:
            raise KeyError(f"Unknown symbol: {symbol}")
        quote = await self.get_quote(key)
        rng = self._rng(f"{key}:ohlcv")
        points: list[PricePoint] = []
        price = quote.price
        step = timedelta(days=1) if interval == Interval.DAY_1 else timedelta(hours=1)
        now = datetime.now(tz=UTC)
        for index in range(limit, 0, -1):
            timestamp = now - step * index
            drift = rng.uniform(-0.02, 0.02)
            open_price = price
            close_price = price * (1 + drift)
            high = max(open_price, close_price) * (1 + rng.uniform(0, 0.01))
            low = min(open_price, close_price) * (1 - rng.uniform(0, 0.01))
            volume = rng.uniform(1_000_000, 50_000_000)
            points.append(
                PricePoint(
                    timestamp=timestamp,
                    open=round(open_price, 4),
                    high=round(high, 4),
                    low=round(low, 4),
                    close=round(close_price, 4),
                    volume=round(volume, 2),
                )
            )
            price = close_price
        return PriceHistory(
            asset_id=key,
            interval=interval,
            points=points,
            meta=self._meta(),
        )

    async def search(self, query: str) -> list[SearchHit]:
        needle = query.strip().lower()
        if not needle:
            return []
        hits: list[SearchHit] = []
        for symbol, catalog in ASSET_CATALOG.items():
            name = str(catalog["name"]).lower()
            if needle in symbol.lower() or needle in name:
                hits.append(
                    SearchHit(
                        asset_id=symbol,
                        symbol=symbol,
                        name=str(catalog["name"]),
                        asset_class=AssetClass(catalog["asset_class"]),
                        exchange="MOCK" if catalog["asset_class"] != AssetClass.CRYPTO else "CRYPTO",
                    )
                )
        return hits[:10]

    async def get_projection(self, symbol: str, horizon_days: int) -> AssetProjection:
        key = symbol.upper()
        history = await self.get_ohlcv(key, Interval.DAY_1, 90)
        quote = await self.get_quote(key)
        return build_projection(
            asset_id=key,
            symbol=key,
            current_price=quote.price,
            points=history.points,
            horizon_days=horizon_days,
            provider=self.provider_name,
        )
