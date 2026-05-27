"""Controlled scraping fallback — Stooq pages only, disabled by default."""

from __future__ import annotations

import asyncio
import logging
import time
from datetime import UTC, datetime
from urllib.parse import quote
from urllib.robotparser import RobotFileParser

import httpx

from app.backend.src.config import MarketDataConfig
from app.backend.src.market_data.base import MarketDataProvider
from app.backend.src.market_data.provenance import make_provenance
from app.backend.src.market_data.scraping.stooq_parser import parse_stooq_quote_page
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
    PriceRange,
    ProviderHealth,
    SourceType,
)

logger = logging.getLogger(__name__)

_STOOQ_DOMAIN = "https://stooq.com"
_MIN_REQUEST_INTERVAL_SEC = 30.0


class ScrapingMarketDataProvider(MarketDataProvider):
    """Scraping adapter — optional, rate-limited, low confidence."""

    def __init__(self, config: MarketDataConfig, tracker: ProviderRequestTracker | None = None) -> None:
        self._config = config
        self._tracker = tracker
        self._client = httpx.AsyncClient(
            timeout=20.0,
            headers={"User-Agent": config.user_agent},
            follow_redirects=True,
        )
        self._last_request_at: datetime | None = None
        self._robots = RobotFileParser()
        self._robots_loaded = False

    @property
    def provider_name(self) -> str:
        return "scraping_stooq"

    async def close(self) -> None:
        await self._client.aclose()

    async def _ensure_robots(self) -> None:
        if self._robots_loaded:
            return
        try:
            self._robots.set_url(f"{_STOOQ_DOMAIN}/robots.txt")
            self._robots.read()
        except Exception as exc:
            logger.warning("Could not load robots.txt for Stooq: %s", exc)
        self._robots_loaded = True

    async def _rate_limit(self) -> None:
        if self._last_request_at is None:
            return
        elapsed = (datetime.now(UTC) - self._last_request_at).total_seconds()
        if elapsed < _MIN_REQUEST_INTERVAL_SEC:
            await asyncio.sleep(_MIN_REQUEST_INTERVAL_SEC - elapsed)

    async def _fetch_page(self, path: str, *, symbol: str, asset_type: AssetType) -> str | None:
        if not self._config.scraping_enabled:
            return None
        await self._ensure_robots()
        url = f"{_STOOQ_DOMAIN}{path}"
        if self._robots_loaded and not self._robots.can_fetch(self._config.user_agent, url):
            logger.info("robots.txt disallows fetch: %s", url)
            return None

        await self._rate_limit()
        start = time.perf_counter()
        status_label = "success"
        http_status: int | None = None
        error_message: str | None = None
        html: str | None = None
        try:
            response = await self._client.get(url)
            http_status = response.status_code
            self._last_request_at = datetime.now(UTC)
            if response.status_code == 429:
                status_label = "rate_limited"
                return None
            response.raise_for_status()
            html = response.text
            return html
        except Exception as exc:
            status_label = "error"
            error_message = str(exc)
            logger.warning("Scraping failed for %s: %s", url, exc)
            return None
        finally:
            if self._tracker:
                await self._tracker.log(
                    provider_name=self.provider_name,
                    source_type=SourceType.SCRAPING,
                    endpoint_or_url=url,
                    symbol=symbol,
                    asset_type=asset_type,
                    status=status_label,
                    http_status=http_status,
                    response_time_ms=int((time.perf_counter() - start) * 1000),
                    error_message=error_message,
                )

    async def search_assets(self, query: str, asset_type: AssetType | None = None) -> list[AssetSearchResult]:
        return []

    async def get_current_price(self, symbol: str, asset_type: AssetType) -> CurrentPrice | None:
        stooq_sym = symbol.lower().replace(".sa", ".sa")
        if asset_type == AssetType.STOCK and ".sa" not in stooq_sym:
            stooq_sym = f"{stooq_sym}.us"
        path = f"/q/?s={quote(stooq_sym)}"
        html = await self._fetch_page(path, symbol=symbol, asset_type=asset_type)
        if not html:
            return None
        quote_data = parse_stooq_quote_page(html, symbol=symbol, source_url=f"{_STOOQ_DOMAIN}{path}")
        if not quote_data:
            return None
        return CurrentPrice(
            symbol=quote_data.symbol,
            asset_type=asset_type,
            price=quote_data.price,
            currency="BRL" if symbol.upper().endswith(".SA") else "USD",
            change_percent=quote_data.change_percent,
            provenance=make_provenance(
                provider_name=self.provider_name,
                source_type=SourceType.SCRAPING,
                source_url=quote_data.source_url,
                fetched_at=quote_data.fetched_at,
                is_delayed=True,
                confidence_level=ConfidenceLevel.LOW,
                warning="Data from scraped public page · May be delayed",
            ),
        )

    async def get_historical_prices(
        self,
        symbol: str,
        asset_type: AssetType,
        range: PriceRange,
        interval: PriceInterval,
    ) -> HistoricalPrices | None:
        return None

    async def get_asset_metadata(self, symbol: str, asset_type: AssetType) -> AssetMetadata | None:
        return None

    async def get_market_summary(self) -> MarketSummary | None:
        return None

    async def get_provider_health(self) -> ProviderHealth:
        enabled = self._config.scraping_enabled
        return ProviderHealth(
            provider_name=self.provider_name,
            healthy=enabled,
            message="Scraping enabled" if enabled else "Scraping disabled (MARKET_DATA_SCRAPING_ENABLED=false)",
            checked_at=datetime.now(UTC),
        )
