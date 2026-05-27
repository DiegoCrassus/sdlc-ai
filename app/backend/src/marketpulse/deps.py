"""FastAPI dependency factories."""

from __future__ import annotations

from functools import lru_cache

from marketpulse.config import Settings, get_settings
from marketpulse.providers.base import MarketDataProvider, NotConfiguredError
from marketpulse.providers.mock import MockMarketDataProvider
from marketpulse.providers.twelve_data import TwelveDataProvider


@lru_cache
def _build_provider(provider_name: str, seed: int) -> MarketDataProvider:
    if provider_name == "mock":
        return MockMarketDataProvider(seed=seed)
    if provider_name == "twelve_data":
        return TwelveDataProvider()
    raise ValueError(f"Unsupported market data provider: {provider_name}")


def get_market_provider(settings: Settings | None = None) -> MarketDataProvider:
    """Return configured market data provider."""
    resolved = settings or get_settings()
    try:
        return _build_provider(resolved.market_data_provider, resolved.mock_seed)
    except NotConfiguredError:
        raise


def get_market_provider_dep() -> MarketDataProvider:
    """FastAPI Depends wrapper."""
    return get_market_provider()
