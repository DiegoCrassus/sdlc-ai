"""Market data provider protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod

from marketpulse.domain.enums import Interval
from marketpulse.domain.models import (
    AssetProjection,
    MarketOverview,
    PriceHistory,
    Quote,
    SearchHit,
)


class NotConfiguredError(RuntimeError):
    """Raised when a live provider is selected without required credentials."""


class MarketDataProvider(ABC):
    """Abstract market data provider."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider identifier returned by health checks."""

    @abstractmethod
    async def get_overview(self) -> MarketOverview:
        """Return aggregated market overview."""

    @abstractmethod
    async def get_quote(self, symbol: str) -> Quote:
        """Return a single asset quote."""

    @abstractmethod
    async def get_ohlcv(self, symbol: str, interval: Interval, limit: int) -> PriceHistory:
        """Return OHLCV time series."""

    @abstractmethod
    async def search(self, query: str) -> list[SearchHit]:
        """Search assets by symbol or name."""

    @abstractmethod
    async def get_projection(self, symbol: str, horizon_days: int) -> AssetProjection:
        """Return price projection for the given horizon."""
