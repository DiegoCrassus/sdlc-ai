"""Finnhub free API adapter — primary US stocks/indexes."""

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

_FINNHUB_BASE = "https://finnhub.io/api/v1"

_INDEX_SYMBOL_MAP = {
    "SPX": "^GSPC",
    "GSPC": "^GSPC",
    "NDX": "^NDX",
    "DJI": "^DJI",
    "IXIC": "^IXIC",
}


def finnhub_symbol(symbol: str, asset_type: AssetType) -> str:
    upper = symbol.upper()
    if asset_type == AssetType.INDEX:
        return _INDEX_SYMBOL_MAP.get(upper, upper if upper.startswith("^") else f"^{upper}")
    return upper


def finnhub_resolution(interval: PriceInterval) -> str:
    return "D" if interval == PriceInterval.DAY else "60"


def finnhub_range_timestamps(range: PriceRange) -> tuple[int, int]:
    now = int(datetime.now(UTC).timestamp())
    days = {
        PriceRange.DAY: 2,
        PriceRange.WEEK: 10,
        PriceRange.MONTH: 35,
        PriceRange.THREE_MONTHS: 100,
        PriceRange.SIX_MONTHS: 200,
        PriceRange.YEAR: 400,
        PriceRange.FIVE_YEARS: 365 * 6,
        PriceRange.MAX: 365 * 15,
    }[range]
    return now - days * 86400, now


RequestFn = Callable[..., Coroutine[Any, Any, tuple[int, Any | None]]]


class FinnhubAdapter:
    def __init__(self, api_key: str | None, request: RequestFn) -> None:
        self._api_key = api_key
        self._request = request

    @property
    def available(self) -> bool:
        return bool(self._api_key)

    async def search(self, query: str) -> list[AssetSearchResult]:
        if not self._api_key:
            return []
        _, data = await self._request(
            url=f"{_FINNHUB_BASE}/search",
            params={"q": query, "token": self._api_key},
            sub_provider="finnhub",
        )
        if not data or not data.get("result"):
            return []
        results: list[AssetSearchResult] = []
        for item in data["result"][:10]:
            at = AssetType.STOCK
            if item.get("type") == "ETP":
                at = AssetType.ETF
            results.append(
                AssetSearchResult(
                    symbol=item.get("symbol", ""),
                    name=item.get("description", ""),
                    asset_type=at,
                    provenance=make_provenance(
                        provider_name="finnhub",
                        source_type=SourceType.API,
                        source_url=f"{_FINNHUB_BASE}/search",
                        is_realtime=True,
                        confidence_level=ConfidenceLevel.HIGH,
                    ),
                )
            )
        return results

    async def quote(self, symbol: str, asset_type: AssetType) -> CurrentPrice | None:
        if not self._api_key:
            return None
        fh_symbol = finnhub_symbol(symbol, asset_type)
        _, data = await self._request(
            url=f"{_FINNHUB_BASE}/quote",
            params={"symbol": fh_symbol, "token": self._api_key},
            symbol=symbol,
            asset_type=asset_type,
            sub_provider="finnhub",
        )
        if not data or data.get("c") in (None, 0):
            return None
        change_pct = None
        if data.get("pc"):
            change_pct = ((float(data["c"]) - float(data["pc"])) / float(data["pc"])) * 100
        return CurrentPrice(
            symbol=symbol.upper(),
            asset_type=asset_type,
            price=float(data["c"]),
            currency="USD",
            change=float(data["c"]) - float(data["pc"]) if data.get("pc") else None,
            change_percent=change_pct,
            provenance=make_provenance(
                provider_name="finnhub",
                source_type=SourceType.API,
                source_url=f"{_FINNHUB_BASE}/quote",
                is_realtime=True,
                confidence_level=ConfidenceLevel.HIGH,
            ),
        )

    async def history(
        self,
        symbol: str,
        asset_type: AssetType,
        range: PriceRange,
        interval: PriceInterval,
    ) -> HistoricalPrices | None:
        if not self._api_key:
            return None
        fh_symbol = finnhub_symbol(symbol, asset_type)
        start, end = finnhub_range_timestamps(range)
        _, data = await self._request(
            url=f"{_FINNHUB_BASE}/stock/candle",
            params={
                "symbol": fh_symbol,
                "resolution": finnhub_resolution(interval),
                "from": start,
                "to": end,
                "token": self._api_key,
            },
            symbol=symbol,
            asset_type=asset_type,
            sub_provider="finnhub",
        )
        if not data or data.get("s") != "ok":
            return None
        points: list[PricePoint] = []
        for i, ts in enumerate(data.get("t", [])):
            points.append(
                PricePoint(
                    timestamp=datetime.fromtimestamp(ts, tz=UTC),
                    open=float(data["o"][i]) if data.get("o") else None,
                    high=float(data["h"][i]) if data.get("h") else None,
                    low=float(data["l"][i]) if data.get("l") else None,
                    close=float(data["c"][i]),
                    volume=float(data["v"][i]) if data.get("v") else None,
                )
            )
        return HistoricalPrices(
            symbol=symbol.upper(),
            asset_type=asset_type,
            range=range,
            interval=interval,
            points=points,
            provenance=make_provenance(
                provider_name="finnhub",
                source_type=SourceType.API,
                source_url=f"{_FINNHUB_BASE}/stock/candle",
                is_delayed=False,
                confidence_level=ConfidenceLevel.HIGH,
            ),
        )

    async def profile(self, symbol: str, asset_type: AssetType) -> AssetMetadata | None:
        if not self._api_key:
            return None
        _, data = await self._request(
            url=f"{_FINNHUB_BASE}/stock/profile2",
            params={"symbol": symbol.upper(), "token": self._api_key},
            symbol=symbol,
            asset_type=asset_type,
            sub_provider="finnhub",
        )
        if not data or not data.get("name"):
            return None
        return AssetMetadata(
            symbol=symbol.upper(),
            asset_type=asset_type,
            name=data.get("name", symbol),
            sector=data.get("finnhubIndustry"),
            currency=data.get("currency"),
            exchange=data.get("exchange"),
            website=data.get("weburl"),
            market_cap=float(data["marketCapitalization"]) * 1_000_000 if data.get("marketCapitalization") else None,
            extra={"country": data.get("country"), "ipo": data.get("ipo")},
            provenance=make_provenance(
                provider_name="finnhub",
                source_type=SourceType.API,
                source_url=f"{_FINNHUB_BASE}/stock/profile2",
                confidence_level=ConfidenceLevel.HIGH,
            ),
        )
