"""Market data service."""

from __future__ import annotations

import logging
from datetime import UTC, datetime

import httpx

from app.backend.config import settings
from app.backend.schemas import (
    AssetDetail,
    AssetQuote,
    AssetSearchResult,
    AssetType,
    DataSourceStatus,
    HistoryRange,
    PriceHistory,
    PricePoint,
)
from app.backend.services.fallback_catalog import (
    CatalogEntry,
    generate_fallback_history,
    get_catalog_entry,
    search_catalog,
)

logger = logging.getLogger(__name__)


async def search_assets(query: str, limit: int = 20) -> list[AssetSearchResult]:
    seen: set[tuple[str, str]] = set()
    out: list[AssetSearchResult] = []
    if settings.enable_live_market_data:
        try:
            async with httpx.AsyncClient(timeout=settings.market_request_timeout) as client:
                resp = await client.get(
                    f"{settings.coingecko_base_url}/search",
                    params={"query": query or "bitcoin"},
                )
                if resp.status_code == 200:
                    for c in resp.json().get("coins", [])[: limit // 2]:
                        sym = c.get("symbol", "").upper()
                        key = (sym, "crypto")
                        if key not in seen:
                            seen.add(key)
                            out.append(
                                AssetSearchResult(
                                    symbol=sym,
                                    asset_type="crypto",
                                    name=c.get("name", sym),
                                    exchange_or_network="CoinGecko",
                                )
                            )
        except Exception as exc:
            logger.warning("CoinGecko search: %s", exc)
    for e in search_catalog(query, limit):
        key = (e.symbol, e.asset_type)
        if key not in seen:
            seen.add(key)
            out.append(
                AssetSearchResult(
                    symbol=e.symbol,
                    asset_type=e.asset_type,
                    name=e.name,
                    exchange_or_network=e.exchange_or_network,
                )
            )
    return out[:limit]


async def get_quote(symbol: str, asset_type: AssetType) -> AssetQuote:
    if settings.enable_live_market_data:
        live = await _live_quote(symbol, asset_type)
        if live:
            return live
    entry = get_catalog_entry(symbol, asset_type) or _synthetic(symbol, asset_type)
    return _from_catalog(entry, "fallback")


async def get_asset_detail(symbol: str, asset_type: AssetType) -> AssetDetail:
    q = await get_quote(symbol, asset_type)
    entry = get_catalog_entry(symbol, asset_type)
    return AssetDetail(
        **q.model_dump(),
        description=entry.description if entry else "Demo asset",
        high_52w=q.price * 1.15,
        low_52w=q.price * 0.85,
    )


async def get_price_history(symbol: str, asset_type: AssetType, range_key: HistoryRange) -> PriceHistory:
    entry = get_catalog_entry(symbol, asset_type)
    base = entry.base_price if entry else 100.0
    if settings.enable_live_market_data and entry and entry.coingecko_id and asset_type == "crypto":
        hist = await _crypto_history(symbol, asset_type, range_key, entry)
        if hist and hist.points:
            return hist
    if not entry:
        entry = _synthetic(symbol, asset_type)
        base = entry.base_price
    raw = generate_fallback_history(symbol, asset_type, base, range_key)
    return PriceHistory(
        symbol=symbol.upper(),
        asset_type=asset_type,
        range=range_key,
        points=[PricePoint(timestamp=t, price=p) for t, p in raw],
        source="fallback",
    )


async def _crypto_history(symbol: str, asset_type: AssetType, range_key: HistoryRange, entry: CatalogEntry):
    days = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}[range_key]
    try:
        async with httpx.AsyncClient(timeout=settings.market_request_timeout) as client:
            resp = await client.get(
                f"{settings.coingecko_base_url}/coins/{entry.coingecko_id}/market_chart",
                params={"vs_currency": "usd", "days": days},
            )
            if resp.status_code != 200:
                return None
            prices = resp.json().get("prices", [])
            if not prices:
                return None
            return PriceHistory(
                symbol=symbol.upper(),
                asset_type=asset_type,
                range=range_key,
                points=[
                    PricePoint(
                        timestamp=datetime.fromtimestamp(ts / 1000, tz=UTC),
                        price=round(p, 4 if p < 10 else 2),
                    )
                    for ts, p in prices
                ],
                source="live",
            )
    except Exception as exc:
        logger.warning("CoinGecko history: %s", exc)
        return None


async def _live_quote(symbol: str, asset_type: AssetType) -> AssetQuote | None:
    sym = symbol.upper()
    if asset_type == "crypto":
        entry = get_catalog_entry(sym, "crypto")
        coin_id = entry.coingecko_id if entry else sym.lower()
        try:
            async with httpx.AsyncClient(timeout=settings.market_request_timeout) as client:
                resp = await client.get(
                    f"{settings.coingecko_base_url}/simple/price",
                    params={"ids": coin_id, "vs_currencies": "usd", "include_24hr_change": "true"},
                )
                if resp.status_code != 200:
                    return None
                data = resp.json().get(coin_id)
                if not data:
                    return None
                price = float(data["usd"])
                pct = float(data.get("usd_24h_change") or 0)
                return AssetQuote(
                    symbol=sym,
                    asset_type="crypto",
                    name=entry.name if entry else sym,
                    price=price,
                    change_pct_24h=pct,
                    change_24h=price * pct / 100,
                    source="live",
                    as_of=datetime.now(UTC),
                )
        except Exception as exc:
            logger.warning("CoinGecko quote: %s", exc)
        return None
    try:
        import yfinance as yf

        hist = yf.Ticker(sym).history(period="2d")
        if hist.empty:
            return None
        price = float(hist["Close"].iloc[-1])
        prev = float(hist["Close"].iloc[-2]) if len(hist) > 1 else price
        entry = get_catalog_entry(sym, "stock")
        return AssetQuote(
            symbol=sym,
            asset_type="stock",
            name=entry.name if entry else sym,
            price=round(price, 2),
            change_24h=round(price - prev, 2),
            change_pct_24h=round((price - prev) / prev * 100, 2) if prev else 0,
            source="live",
            as_of=datetime.now(UTC),
        )
    except Exception as exc:
        logger.warning("yfinance: %s", exc)
        return None


def _from_catalog(entry: CatalogEntry, source: DataSourceStatus) -> AssetQuote:
    ch = entry.base_price * entry.change_pct_24h / 100
    return AssetQuote(
        symbol=entry.symbol,
        asset_type=entry.asset_type,
        name=entry.name,
        price=entry.base_price,
        change_24h=round(ch, 4),
        change_pct_24h=entry.change_pct_24h,
        source=source,
        as_of=datetime.now(UTC),
    )


def _synthetic(symbol: str, asset_type: AssetType) -> CatalogEntry:
    return CatalogEntry(symbol.upper(), asset_type, f"{symbol.upper()} demo", 50.0 + hash(symbol) % 200, 0.0)
