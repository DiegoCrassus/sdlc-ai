"""Fallback catalog when live APIs fail."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from app.backend.schemas import AssetType, HistoryRange


@dataclass(frozen=True)
class CatalogEntry:
    symbol: str
    asset_type: AssetType
    name: str
    base_price: float
    change_pct_24h: float
    market_cap: float | None = None
    description: str = ""
    exchange_or_network: str | None = None
    coingecko_id: str | None = None


STOCKS = [
    CatalogEntry("AAPL", "stock", "Apple Inc.", 198.5, 1.2, exchange_or_network="NASDAQ"),
    CatalogEntry("MSFT", "stock", "Microsoft", 425.3, 0.8, exchange_or_network="NASDAQ"),
    CatalogEntry("NVDA", "stock", "NVIDIA", 118.9, 2.3, exchange_or_network="NASDAQ"),
]
CRYPTOS = [
    CatalogEntry("BTC", "crypto", "Bitcoin", 67200.0, 2.1, coingecko_id="bitcoin"),
    CatalogEntry("ETH", "crypto", "Ethereum", 3450.0, 1.8, coingecko_id="ethereum"),
    CatalogEntry("SOL", "crypto", "Solana", 168.5, 3.2, coingecko_id="solana"),
]
CATALOG = {(e.symbol, e.asset_type): e for e in STOCKS + CRYPTOS}


def search_catalog(query: str, limit: int = 20) -> list[CatalogEntry]:
    q = query.strip().lower()
    pool = STOCKS + CRYPTOS
    if not q:
        return pool[:limit]
    return [e for e in pool if q in f"{e.symbol} {e.name}".lower()][:limit]


def get_catalog_entry(symbol: str, asset_type: AssetType) -> CatalogEntry | None:
    return CATALOG.get((symbol.upper(), asset_type))


def generate_fallback_history(symbol: str, asset_type: AssetType, base: float, range_key: HistoryRange):
    rng = random.Random(int(hashlib.sha256(f"{symbol}:{asset_type}".encode()).hexdigest()[:16], 16))
    count = {"1d": 24, "7d": 168, "30d": 30, "90d": 90}[range_key]
    step = 1 if range_key in ("1d", "7d") else 24
    now = datetime.now(UTC).replace(minute=0, second=0, microsecond=0)
    start = now - timedelta(hours=step * (count - 1))
    price = base * 0.95
    series = []
    for i in range(count):
        ts = start + timedelta(hours=step * i)
        price = max(price * (1 + rng.gauss(0, 0.008)), base * 0.5)
        series.append((ts, round(price, 2)))
    series[-1] = (series[-1][0], base)
    return series
