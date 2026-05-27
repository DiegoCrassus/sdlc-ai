"""Factory to wire market data providers."""

from __future__ import annotations

from app.backend.src.config import MarketDataConfig, load_config
from app.backend.src.market_data.api import ApiMarketDataProvider
from app.backend.src.market_data.cache import MarketDataCache
from app.backend.src.market_data.composite import CompositeMarketDataProvider
from app.backend.src.market_data.csv import CsvMarketDataProvider
from app.backend.src.market_data.mock import MockMarketDataProvider
from app.backend.src.market_data.scraping.provider import ScrapingMarketDataProvider
from app.backend.src.market_data.tracker import ProviderRequestTracker


async def build_market_data_provider(
    config: MarketDataConfig | None = None,
) -> CompositeMarketDataProvider:
    cfg = config or load_config()
    tracker = ProviderRequestTracker(cfg)
    await tracker.init_db()

    cache = MarketDataCache(cfg)
    await cache.connect()

    if cfg.mode == "mock":
        mock = MockMarketDataProvider()
        return CompositeMarketDataProvider(
            cache=cache,
            api=mock,
            csv=mock,
            scraping=mock,
            mock=mock,
            tracker=tracker,
        )

    api = ApiMarketDataProvider(cfg, tracker)
    csv = CsvMarketDataProvider(cfg, tracker)
    scraping = ScrapingMarketDataProvider(cfg, tracker)
    mock = MockMarketDataProvider(
        warning="Simulated data — external sources unavailable",
    )

    return CompositeMarketDataProvider(
        cache=cache,
        api=api,
        csv=csv,
        scraping=scraping,
        mock=mock,
        tracker=tracker,
    )
