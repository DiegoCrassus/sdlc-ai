"""Stooq CSV download provider."""

from __future__ import annotations

import csv
import io
import time
from datetime import UTC, datetime, timedelta

import httpx

from app.backend.src.config import MarketDataConfig
from app.backend.src.market_data.base import MarketDataProvider
from app.backend.src.market_data.provenance import make_provenance
from app.backend.src.market_data.tracker import ProviderRequestTracker
from app.shared.types.market_data import (
    AssetMetadata,
    AssetSearchResult,
    AssetType,
    ConfidenceLevel,
    CurrentPrice,
    HistoricalPrices,
    MarketSummary,
    PriceInterval,
    PricePoint,
    PriceRange,
    ProviderHealth,
    SourceType,
)

_STOOQ_CSV_BASE = "https://stooq.com/q/d/l/"


def _to_stooq_symbol(symbol: str, asset_type: AssetType) -> str:
    sym = symbol.lower().replace(".", "")
    if asset_type == AssetType.STOCK and "." not in symbol.lower():
        if symbol.upper().endswith(".SA"):
            return symbol.lower().replace(".sa", ".sa")
        return f"{sym}.us"
    if asset_type == AssetType.INDEX and not symbol.startswith("^"):
        return f"^{sym}"
    return symbol.lower()


class CsvMarketDataProvider(MarketDataProvider):
    def __init__(self, config: MarketDataConfig, tracker: ProviderRequestTracker | None = None) -> None:
        self._config = config
        self._tracker = tracker
        self._client = httpx.AsyncClient(timeout=30.0, headers={"User-Agent": config.user_agent})
        self._daily_downloads = 0

    @property
    def provider_name(self) -> str:
        return "csv_stooq"

    async def close(self) -> None:
        await self._client.aclose()

    async def _download_csv(
        self,
        stooq_symbol: str,
        start: datetime,
        end: datetime,
        *,
        symbol: str,
        asset_type: AssetType,
    ) -> str | None:
        if self._daily_downloads >= 30:
            return None
        url = (
            f"{_STOOQ_CSV_BASE}?s={stooq_symbol}&d1={start.strftime('%Y%m%d')}"
            f"&d2={end.strftime('%Y%m%d')}&i=d"
        )
        start_ts = time.perf_counter()
        status = "success"
        http_status: int | None = None
        error_message: str | None = None
        text: str | None = None
        try:
            response = await self._client.get(url)
            http_status = response.status_code
            response.raise_for_status()
            text = response.text
            if "Exceeded the daily hits limit" in text or not text.strip():
                status = "rate_limited"
                return None
            self._daily_downloads += 1
            return text
        except Exception as exc:
            status = "error"
            error_message = str(exc)
            return None
        finally:
            if self._tracker:
                await self._tracker.log(
                    provider_name=self.provider_name,
                    source_type=SourceType.CSV,
                    endpoint_or_url=url,
                    symbol=symbol,
                    asset_type=asset_type,
                    status=status,
                    http_status=http_status,
                    response_time_ms=int((time.perf_counter() - start_ts) * 1000),
                    error_message=error_message,
                )

    def _parse_csv(self, csv_text: str) -> list[PricePoint]:
        reader = csv.DictReader(io.StringIO(csv_text))
        points: list[PricePoint] = []
        for row in reader:
            try:
                points.append(
                    PricePoint(
                        timestamp=datetime.strptime(row["Date"], "%Y-%m-%d").replace(tzinfo=UTC),
                        open=float(row["Open"]) if row.get("Open") else None,
                        high=float(row["High"]) if row.get("High") else None,
                        low=float(row["Low"]) if row.get("Low") else None,
                        close=float(row["Close"]),
                        volume=float(row["Volume"]) if row.get("Volume") else None,
                    )
                )
            except (KeyError, ValueError):
                continue
        return points

    def _range_dates(self, range: PriceRange) -> tuple[datetime, datetime]:
        end = datetime.now(UTC)
        days = {
            PriceRange.DAY: 5,
            PriceRange.WEEK: 14,
            PriceRange.MONTH: 45,
            PriceRange.THREE_MONTHS: 120,
            PriceRange.SIX_MONTHS: 200,
            PriceRange.YEAR: 400,
            PriceRange.FIVE_YEARS: 365 * 6,
            PriceRange.MAX: 365 * 15,
        }[range]
        return end - timedelta(days=days), end

    async def search_assets(self, query: str, asset_type: AssetType | None = None) -> list[AssetSearchResult]:
        return []

    async def get_current_price(self, symbol: str, asset_type: AssetType) -> CurrentPrice | None:
        history = await self.get_historical_prices(
            symbol, asset_type, PriceRange.WEEK, PriceInterval.DAY
        )
        if not history or not history.points:
            return None
        last = history.points[-1]
        return CurrentPrice(
            symbol=symbol.upper(),
            asset_type=asset_type,
            price=last.close,
            currency="USD" if not symbol.upper().endswith(".SA") else "BRL",
            provenance=make_provenance(
                provider_name=self.provider_name,
                source_type=SourceType.CSV,
                source_url=_STOOQ_CSV_BASE,
                is_delayed=True,
                confidence_level=ConfidenceLevel.MEDIUM,
                warning="End-of-day CSV data — may be delayed",
            ),
        )

    async def get_historical_prices(
        self,
        symbol: str,
        asset_type: AssetType,
        range: PriceRange,
        interval: PriceInterval,
    ) -> HistoricalPrices | None:
        if interval != PriceInterval.DAY:
            return None
        stooq_symbol = _to_stooq_symbol(symbol, asset_type)
        start, end = self._range_dates(range)
        csv_text = await self._download_csv(
            stooq_symbol, start, end, symbol=symbol, asset_type=asset_type
        )
        if not csv_text:
            return None
        points = self._parse_csv(csv_text)
        if not points:
            return None
        return HistoricalPrices(
            symbol=symbol.upper(),
            asset_type=asset_type,
            range=range,
            interval=interval,
            points=points,
            provenance=make_provenance(
                provider_name=self.provider_name,
                source_type=SourceType.CSV,
                source_url=f"{_STOOQ_CSV_BASE}?s={stooq_symbol}",
                is_delayed=True,
                confidence_level=ConfidenceLevel.MEDIUM,
            ),
        )

    async def get_asset_metadata(self, symbol: str, asset_type: AssetType) -> AssetMetadata | None:
        return AssetMetadata(
            symbol=symbol.upper(),
            asset_type=asset_type,
            name=symbol.upper(),
            provenance=make_provenance(
                provider_name=self.provider_name,
                source_type=SourceType.CSV,
                source_url=_STOOQ_CSV_BASE,
                confidence_level=ConfidenceLevel.LOW,
                warning="Minimal metadata from CSV provider",
            ),
        )

    async def get_market_summary(self) -> MarketSummary | None:
        return None

    async def get_provider_health(self) -> ProviderHealth:
        return ProviderHealth(
            provider_name=self.provider_name,
            healthy=True,
            message=f"CSV provider ready — {self._daily_downloads}/30 daily downloads used",
            checked_at=datetime.now(UTC),
        )
