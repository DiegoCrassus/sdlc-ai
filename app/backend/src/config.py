"""Backend configuration from environment variables."""

from __future__ import annotations

import os
from dataclasses import dataclass


def _env_bool(name: str, default: bool = False) -> bool:
    value = os.getenv(name, str(default)).lower()
    return value in ("1", "true", "yes", "on")


@dataclass(frozen=True)
class MarketDataConfig:
    mode: str = "live"
    scraping_enabled: bool = False
    redis_url: str = "redis://localhost:6379/0"
    database_url: str = "sqlite+aiosqlite:///./data/market_data.db"
    twelve_data_api_key: str | None = None
    finnhub_api_key: str | None = None
    brapi_api_key: str | None = None
    coingecko_api_key: str | None = None
    alpha_vantage_api_key: str | None = None
    user_agent: str = "SDLC-Invest/1.0 (+https://github.com/DiegoCrassus/sdlc-ai; market-data-research)"
    cache_ttl_crypto_price: int = 60
    cache_ttl_stock_price: int = 600
    cache_ttl_historical: int = 43200
    cache_ttl_metadata: int = 86400
    cache_ttl_search: int = 7200
    cache_ttl_scraped: int = 1800


def load_config() -> MarketDataConfig:
    return MarketDataConfig(
        mode=os.getenv("MARKET_DATA_MODE", "live"),
        scraping_enabled=_env_bool("MARKET_DATA_SCRAPING_ENABLED", False),
        redis_url=os.getenv("REDIS_URL", "redis://localhost:6379/0"),
        database_url=os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./data/market_data.db"),
        twelve_data_api_key=os.getenv("TWELVE_DATA_API_KEY"),
        finnhub_api_key=os.getenv("FINNHUB_API_KEY"),
        brapi_api_key=os.getenv("BRAPI_API_KEY"),
        coingecko_api_key=os.getenv("COINGECKO_API_KEY"),
        alpha_vantage_api_key=os.getenv("ALPHA_VANTAGE_API_KEY"),
        user_agent=os.getenv(
            "MARKET_DATA_USER_AGENT",
            "SDLC-Invest/1.0 (+https://github.com/DiegoCrassus/sdlc-ai; market-data-research)",
        ),
    )
