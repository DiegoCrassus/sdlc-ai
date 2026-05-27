"""Fallback catalog when live APIs fail."""

from __future__ import annotations

import hashlib
import random
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta

from app.backend.schemas import Asset, DataSource
from app.backend.utils.asset_id import AssetClass, format_asset_id


@dataclass(frozen=True)
class CatalogEntry:
    symbol: str
    asset_type: AssetClass
    name: str
    base_price: float
    change_pct_24h: float
    currency: str = "USD"
    exchange: str | None = None
    coingecko_id: str | None = None


STOCKS = [
    CatalogEntry("AAPL", "stock", "Apple Inc.", 198.5, 1.2, exchange="NASDAQ"),
    CatalogEntry("MSFT", "stock", "Microsoft", 425.3, 0.8, exchange="NASDAQ"),
    CatalogEntry("NVDA", "stock", "NVIDIA", 118.9, 2.3, exchange="NASDAQ"),
]
CRYPTOS = [
    CatalogEntry("BTC", "crypto", "Bitcoin", 67200.0, 2.1, exchange="CRYPTO", coingecko_id="bitcoin"),
    CatalogEntry("ETH", "crypto", "Ethereum", 3450.0, 1.8, exchange="CRYPTO", coingecko_id="ethereum"),
    CatalogEntry("SOL", "crypto", "Solana", 168.5, 3.2, exchange="CRYPTO", coingecko_id="solana"),
]
CATALOG = {(e.symbol, e.asset_type): e for e in STOCKS + CRYPTOS}


def search_catalog(
    query: str,
    limit: int = 20,
    offset: int = 0,
    asset_class: AssetClass | None = None,
) -> tuple[list[CatalogEntry], int]:
    q = query.strip().lower()
    pool = STOCKS + CRYPTOS
    if asset_class == "stock":
        pool = STOCKS
    elif asset_class == "crypto":
        pool = CRYPTOS
    if q:
        pool = [e for e in pool if q in f"{e.symbol} {e.name}".lower()]
    total = len(pool)
    return pool[offset : offset + limit], total


def get_catalog_entry(symbol: str, asset_type: AssetClass) -> CatalogEntry | None:
    return CATALOG.get((symbol.upper(), asset_type))


def catalog_entry_to_asset(entry: CatalogEntry, source: DataSource = "fallback") -> Asset:
    return Asset.model_validate(
        {
            "id": format_asset_id(entry.asset_type, entry.symbol),
            "class": entry.asset_type,
            "symbol": entry.symbol,
            "name": entry.name,
            "currency": entry.currency,
            "exchange": entry.exchange,
            "source": source,
        }
    )


def synthetic_entry(symbol: str, asset_type: AssetClass) -> CatalogEntry:
    return CatalogEntry(
        symbol.upper(),
        asset_type,
        f"{symbol.upper()} demo",
        50.0 + hash(symbol) % 200,
        0.0,
        exchange="CRYPTO" if asset_type == "crypto" else None,
    )


@dataclass(frozen=True)
class OhlcvPoint:
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None


def generate_fallback_history(
    symbol: str,
    asset_type: AssetClass,
    base: float,
    from_date: date,
    to_date: date,
) -> list[OhlcvPoint]:
    rng = random.Random(int(hashlib.sha256(f"{symbol}:{asset_type}".encode()).hexdigest()[:16], 16))
    days = max((to_date - from_date).days + 1, 1)
    price = base * 0.95
    points: list[OhlcvPoint] = []
    for i in range(days):
        day = from_date + timedelta(days=i)
        ts = datetime(day.year, day.month, day.day, tzinfo=UTC)
        drift = rng.gauss(0, 0.008)
        open_p = price
        close_p = max(price * (1 + drift), base * 0.5)
        high_p = max(open_p, close_p) * (1 + abs(rng.gauss(0, 0.004)))
        low_p = min(open_p, close_p) * (1 - abs(rng.gauss(0, 0.004)))
        vol = rng.randint(1_000_000, 50_000_000) if asset_type == "stock" else None
        points.append(
            OhlcvPoint(
                timestamp=ts,
                open=round(open_p, 2),
                high=round(high_p, 2),
                low=round(low_p, 2),
                close=round(close_p, 2),
                volume=float(vol) if vol is not None else None,
            )
        )
        price = close_p
    if points:
        last = points[-1]
        points[-1] = OhlcvPoint(
            timestamp=last.timestamp,
            open=last.open,
            high=last.high,
            low=last.low,
            close=base,
            volume=last.volume,
        )
    return points
