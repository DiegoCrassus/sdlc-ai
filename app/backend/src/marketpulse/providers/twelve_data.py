"""Twelve Data provider stub — requires TWELVE_DATA_API_KEY."""

from __future__ import annotations

from marketpulse.config import get_settings
from marketpulse.domain.enums import Interval
from marketpulse.domain.models import AssetProjection, MarketOverview, PriceHistory, Quote, SearchHit
from marketpulse.providers.base import MarketDataProvider, NotConfiguredError


class TwelveDataProvider(MarketDataProvider):
    """Stub for Twelve Data integration."""

    def __init__(self) -> None:
        settings = get_settings()
        self._api_key = settings.twelve_data_api_key

    def _ensure_configured(self) -> None:
        if not self._api_key:
            raise NotConfiguredError(
                "Twelve Data provider is not configured. Set TWELVE_DATA_API_KEY."
            )

    @property
    def provider_name(self) -> str:
        return "twelve_data"

    async def get_overview(self) -> MarketOverview:
        self._ensure_configured()
        raise NotImplementedError("Twelve Data overview not implemented yet.")

    async def get_quote(self, symbol: str) -> Quote:
        self._ensure_configured()
        raise NotImplementedError("Twelve Data quote not implemented yet.")

    async def get_ohlcv(self, symbol: str, interval: Interval, limit: int) -> PriceHistory:
        self._ensure_configured()
        raise NotImplementedError("Twelve Data OHLCV not implemented yet.")

    async def search(self, query: str) -> list[SearchHit]:
        self._ensure_configured()
        raise NotImplementedError("Twelve Data search not implemented yet.")

    async def get_projection(self, symbol: str, horizon_days: int) -> AssetProjection:
        self._ensure_configured()
        raise NotImplementedError("Twelve Data projection not implemented yet.")
