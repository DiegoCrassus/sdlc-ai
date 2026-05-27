"""Tests for mock and composite providers."""

import pytest

from app.backend.src.config import MarketDataConfig
from app.backend.src.market_data.cache import MarketDataCache
from app.backend.src.market_data.composite import CompositeMarketDataProvider
from app.backend.src.market_data.mock import MockMarketDataProvider
from app.shared.types.market_data import AssetType, ConfidenceLevel, SourceType


@pytest.fixture
def composite() -> CompositeMarketDataProvider:
    mock = MockMarketDataProvider()
    cache = MarketDataCache(MarketDataConfig(mode="mock"))
    return CompositeMarketDataProvider(
        cache=cache,
        api=mock,
        csv=mock,
        scraping=mock,
        mock=mock,
    )


@pytest.mark.asyncio
async def test_mock_current_price() -> None:
    provider = MockMarketDataProvider()
    price = await provider.get_current_price("AAPL", AssetType.STOCK)
    assert price is not None
    assert price.price == 189.50
    assert price.provenance.source_type == SourceType.MOCK
    assert price.provenance.confidence_level == ConfidenceLevel.LOW


@pytest.mark.asyncio
async def test_composite_falls_back_to_mock(composite: CompositeMarketDataProvider) -> None:
    price = await composite.get_current_price("AAPL", AssetType.STOCK)
    assert price is not None
    assert price.provenance.provider_name == "mock"


@pytest.mark.asyncio
async def test_composite_search(composite: CompositeMarketDataProvider) -> None:
    results = await composite.search_assets("apple", AssetType.STOCK)
    assert len(results) >= 1
    assert results[0].symbol == "AAPL"


@pytest.mark.asyncio
async def test_composite_health(composite: CompositeMarketDataProvider) -> None:
    health = await composite.get_provider_health()
    assert health.healthy is True
