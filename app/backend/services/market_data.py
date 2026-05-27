"""Market data service — live providers with fallback catalog."""

from __future__ import annotations

import logging
from datetime import UTC, date, datetime, timedelta

import httpx

from app.backend.config import settings
from app.backend.errors import AppError
from app.backend.schemas import (
    Asset,
    BatchQuotes,
    DataSource,
    HistoryInterval,
    HistoryResponse,
    PaginatedAssets,
    PricePoint,
    Quote,
)
from app.backend.services.fallback_catalog import (
    CatalogEntry,
    OhlcvPoint,
    catalog_entry_to_asset,
    generate_fallback_history,
    get_catalog_entry,
    search_catalog,
    synthetic_entry,
)
from app.backend.utils.asset_id import AssetClass, format_asset_id, parse_asset_id

logger = logging.getLogger(__name__)

MAX_BATCH_QUOTES = 20


async def search_assets(
    query: str,
    limit: int = 20,
    offset: int = 0,
    asset_class: AssetClass | None = None,
) -> PaginatedAssets:
    seen: set[str] = set()
    items: list[Asset] = []

    if settings.enable_live_market_data:
        live_items = await _live_search(query, asset_class, limit + offset)
        for asset in live_items:
            if asset.id not in seen:
                seen.add(asset.id)
                items.append(asset)

    catalog_entries, _ = search_catalog(query, limit=limit + offset, offset=0, asset_class=asset_class)
    for entry in catalog_entries:
        aid = format_asset_id(entry.asset_type, entry.symbol)
        if aid not in seen:
            seen.add(aid)
            items.append(catalog_entry_to_asset(entry, "fallback"))

    total = len(items)
    page = items[offset : offset + limit]
    return PaginatedAssets(items=page, total=total, limit=limit, offset=offset)


async def get_asset(asset_id: str) -> Asset:
    asset_class, symbol = parse_asset_id(asset_id)
    if settings.enable_live_market_data:
        live = await _live_asset(asset_class, symbol)
        if live:
            return live
    entry = get_catalog_entry(symbol, asset_class)
    if entry:
        return catalog_entry_to_asset(entry, "fallback")
    raise AppError("NOT_FOUND", f"Asset not found: {asset_id}", status_code=404)


async def get_quote(asset_id: str, *, allow_synthetic: bool = True) -> Quote:
    asset_class, symbol = parse_asset_id(asset_id)
    if settings.enable_live_market_data:
        live = await _live_quote(asset_class, symbol)
        if live:
            return live
    entry = get_catalog_entry(symbol, asset_class)
    if not entry:
        if not allow_synthetic:
            raise AppError("NOT_FOUND", f"Asset not found: {asset_id}", status_code=404)
        entry = synthetic_entry(symbol, asset_class)
    return _quote_from_catalog(asset_id, entry, "fallback")


async def get_quotes(asset_ids: list[str]) -> BatchQuotes:
    if len(asset_ids) > MAX_BATCH_QUOTES:
        raise AppError(
            "VALIDATION_ERROR",
            f"Maximum {MAX_BATCH_QUOTES} asset IDs per request",
            details={"max": MAX_BATCH_QUOTES},
        )
    items: list[Quote] = []
    missing: list[str] = []
    for aid in asset_ids:
        aid = aid.strip()
        if not aid:
            continue
        try:
            parse_asset_id(aid)
        except Exception:
            missing.append(aid)
            continue
        try:
            items.append(await get_quote(aid, allow_synthetic=False))
        except AppError as exc:
            if exc.code == "NOT_FOUND":
                missing.append(aid)
            else:
                raise
    return BatchQuotes(items=items, missing=missing)


async def get_history(
    asset_id: str,
    interval: HistoryInterval = "1d",
    from_date: date | None = None,
    to_date: date | None = None,
) -> HistoryResponse:
    asset_class, symbol = parse_asset_id(asset_id)
    today = date.today()
    to_d = to_date or today
    from_d = from_date or (to_d - timedelta(days=90))

    if settings.enable_live_market_data:
        live_points = await _live_history(asset_class, symbol, interval, from_d, to_d)
        if live_points:
            return HistoryResponse(
                asset_id=asset_id,
                interval=interval,
                source="live",
                points=[_ohlcv_to_price_point(p) for p in live_points],
            )

    entry = get_catalog_entry(symbol, asset_class) or synthetic_entry(symbol, asset_class)
    raw = generate_fallback_history(symbol, asset_class, entry.base_price, from_d, to_d)
    return HistoryResponse(
        asset_id=asset_id,
        interval=interval,
        source="fallback",
        points=[_ohlcv_to_price_point(p) for p in raw],
    )


def _ohlcv_to_price_point(point: OhlcvPoint) -> PricePoint:
    return PricePoint(
        timestamp=point.timestamp,
        open=point.open,
        high=point.high,
        low=point.low,
        close=point.close,
        volume=point.volume,
    )


def _quote_from_catalog(asset_id: str, entry: CatalogEntry, source: DataSource) -> Quote:
    change_pct = entry.change_pct_24h
    change = round(entry.base_price * change_pct / 100, 4)
    return Quote(
        asset_id=asset_id,
        price=entry.base_price,
        change=change,
        change_percent=change_pct,
        currency=entry.currency,
        timestamp=datetime.now(UTC),
        source=source,
    )


async def _live_search(
    query: str,
    asset_class: AssetClass | None,
    limit: int,
) -> list[Asset]:
    items: list[Asset] = []
    try:
        async with httpx.AsyncClient(timeout=settings.market_request_timeout) as client:
            if asset_class in (None, "stock") and settings.finnhub_api_key:
                items.extend(await _finnhub_search(client, query, limit))
            if asset_class in (None, "crypto"):
                items.extend(await _coingecko_search(client, query, limit))
    except Exception as exc:
        logger.warning("live search failed: %s", exc)
    return items[:limit]


async def _finnhub_search(client: httpx.AsyncClient, query: str, limit: int) -> list[Asset]:
    resp = await client.get(
        f"{settings.finnhub_base_url}/search",
        params={"q": query, "token": settings.finnhub_api_key},
    )
    if resp.status_code != 200:
        return []
    out: list[Asset] = []
    for row in resp.json().get("result", [])[:limit]:
        sym = (row.get("symbol") or "").upper()
        if not sym:
            continue
        out.append(
            Asset.model_validate(
                {
                    "id": format_asset_id("stock", sym),
                    "class": "stock",
                    "symbol": sym,
                    "name": row.get("description") or sym,
                    "currency": "USD",
                    "exchange": row.get("type"),
                    "source": "live",
                }
            )
        )
    return out


async def _coingecko_search(client: httpx.AsyncClient, query: str, limit: int) -> list[Asset]:
    resp = await client.get(
        f"{settings.coingecko_base_url}/search",
        params={"query": query or "bitcoin"},
    )
    if resp.status_code != 200:
        return []
    out: list[Asset] = []
    for coin in resp.json().get("coins", [])[:limit]:
        sym = (coin.get("symbol") or "").upper()
        if not sym:
            continue
        out.append(
            Asset.model_validate(
                {
                    "id": format_asset_id("crypto", sym),
                    "class": "crypto",
                    "symbol": sym,
                    "name": coin.get("name") or sym,
                    "currency": "USD",
                    "exchange": "CRYPTO",
                    "source": "live",
                }
            )
        )
    return out


async def _live_asset(asset_class: AssetClass, symbol: str) -> Asset | None:
    entry = get_catalog_entry(symbol, asset_class)
    if asset_class == "crypto":
        quote = await _coingecko_quote(symbol, entry)
        if quote:
            return Asset.model_validate(
                {
                    "id": format_asset_id("crypto", symbol),
                    "class": "crypto",
                    "symbol": symbol.upper(),
                    "name": entry.name if entry else symbol.upper(),
                    "currency": "USD",
                    "exchange": "CRYPTO",
                    "source": "live",
                }
            )
    elif settings.finnhub_api_key:
        quote = await _finnhub_quote(symbol)
        if quote:
            entry = entry or get_catalog_entry(symbol, "stock")
            return Asset.model_validate(
                {
                    "id": format_asset_id("stock", symbol),
                    "class": "stock",
                    "symbol": symbol.upper(),
                    "name": entry.name if entry else symbol.upper(),
                    "currency": "USD",
                    "exchange": entry.exchange if entry else None,
                    "source": "live",
                }
            )
    return None


async def _live_quote(asset_class: AssetClass, symbol: str) -> Quote | None:
    sym = symbol.upper()
    asset_id = format_asset_id(asset_class, sym)
    entry = get_catalog_entry(sym, asset_class)

    if asset_class == "crypto":
        return await _coingecko_quote(sym, entry, asset_id)

    if settings.finnhub_api_key:
        q = await _finnhub_quote(sym, asset_id)
        if q:
            return q
    if settings.alpha_vantage_api_key:
        return await _alpha_vantage_quote(sym, asset_id)
    return None


async def _finnhub_quote(symbol: str, asset_id: str | None = None) -> Quote | None:
    if not settings.finnhub_api_key:
        return None
    aid = asset_id or format_asset_id("stock", symbol)
    try:
        async with httpx.AsyncClient(timeout=settings.market_request_timeout) as client:
            resp = await client.get(
                f"{settings.finnhub_base_url}/quote",
                params={"symbol": symbol, "token": settings.finnhub_api_key},
            )
            if resp.status_code != 200:
                return None
            data = resp.json()
            price = data.get("c")
            if price is None or price == 0:
                return None
            ts = datetime.fromtimestamp(data.get("t", 0), tz=UTC)
            return Quote(
                asset_id=aid,
                price=float(price),
                change=float(data.get("d") or 0),
                change_percent=float(data.get("dp") or 0),
                currency="USD",
                timestamp=ts,
                source="live",
            )
    except Exception as exc:
        logger.warning("Finnhub quote: %s", exc)
    return None


async def _alpha_vantage_quote(symbol: str, asset_id: str) -> Quote | None:
    if not settings.alpha_vantage_api_key:
        return None
    try:
        async with httpx.AsyncClient(timeout=settings.market_request_timeout) as client:
            resp = await client.get(
                settings.alpha_vantage_base_url,
                params={
                    "function": "GLOBAL_QUOTE",
                    "symbol": symbol,
                    "apikey": settings.alpha_vantage_api_key,
                },
            )
            if resp.status_code != 200:
                return None
            gq = resp.json().get("Global Quote") or {}
            price_raw = gq.get("05. price")
            if not price_raw:
                return None
            price = float(price_raw)
            change = float(gq.get("09. change") or 0)
            pct_raw = (gq.get("10. change percent") or "0").replace("%", "")
            return Quote(
                asset_id=asset_id,
                price=price,
                change=change,
                change_percent=float(pct_raw),
                currency="USD",
                timestamp=datetime.now(UTC),
                source="live",
            )
    except Exception as exc:
        logger.warning("Alpha Vantage quote: %s", exc)
    return None


async def _coingecko_quote(
    symbol: str,
    entry: CatalogEntry | None,
    asset_id: str | None = None,
) -> Quote | None:
    coin_id = entry.coingecko_id if entry else symbol.lower()
    aid = asset_id or format_asset_id("crypto", symbol)
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
            return Quote(
                asset_id=aid,
                price=price,
                change=round(price * pct / 100, 4),
                change_percent=pct,
                currency="USD",
                timestamp=datetime.now(UTC),
                source="live",
            )
    except Exception as exc:
        logger.warning("CoinGecko quote: %s", exc)
    return None


async def _live_history(
    asset_class: AssetClass,
    symbol: str,
    interval: HistoryInterval,
    from_d: date,
    to_d: date,
) -> list[OhlcvPoint] | None:
    if interval != "1d":
        return None
    if asset_class == "crypto":
        return await _coingecko_history(symbol, from_d, to_d)
    if settings.finnhub_api_key:
        return await _finnhub_candles(symbol, from_d, to_d)
    return None


async def _finnhub_candles(symbol: str, from_d: date, to_d: date) -> list[OhlcvPoint] | None:
    from_ts = int(datetime(from_d.year, from_d.month, from_d.day, tzinfo=UTC).timestamp())
    to_ts = int(datetime(to_d.year, to_d.month, to_d.day, 23, 59, tzinfo=UTC).timestamp())
    try:
        async with httpx.AsyncClient(timeout=settings.market_request_timeout) as client:
            resp = await client.get(
                f"{settings.finnhub_base_url}/stock/candle",
                params={
                    "symbol": symbol,
                    "resolution": "D",
                    "from": from_ts,
                    "to": to_ts,
                    "token": settings.finnhub_api_key,
                },
            )
            if resp.status_code != 200 or resp.json().get("s") != "ok":
                return None
            payload = resp.json()
            times = payload.get("t") or []
            if not times:
                return None
            return [
                OhlcvPoint(
                    timestamp=datetime.fromtimestamp(t, tz=UTC),
                    open=float(payload["o"][i]),
                    high=float(payload["h"][i]),
                    low=float(payload["l"][i]),
                    close=float(payload["c"][i]),
                    volume=float(payload["v"][i]) if payload.get("v") else None,
                )
                for i, t in enumerate(times)
            ]
    except Exception as exc:
        logger.warning("Finnhub candles: %s", exc)
    return None


async def _coingecko_history(symbol: str, from_d: date, to_d: date) -> list[OhlcvPoint] | None:
    entry = get_catalog_entry(symbol, "crypto")
    coin_id = entry.coingecko_id if entry else symbol.lower()
    days = max((to_d - from_d).days, 1)
    try:
        async with httpx.AsyncClient(timeout=settings.market_request_timeout) as client:
            resp = await client.get(
                f"{settings.coingecko_base_url}/coins/{coin_id}/market_chart",
                params={"vs_currency": "usd", "days": min(days, 90)},
            )
            if resp.status_code != 200:
                return None
            prices = resp.json().get("prices", [])
            if not prices:
                return None
            points: list[OhlcvPoint] = []
            for ts_ms, close in prices:
                ts = datetime.fromtimestamp(ts_ms / 1000, tz=UTC)
                c = round(float(close), 4 if close < 10 else 2)
                points.append(
                    OhlcvPoint(timestamp=ts, open=c, high=c, low=c, close=c, volume=None)
                )
            return points
    except Exception as exc:
        logger.warning("CoinGecko history: %s", exc)
    return None
