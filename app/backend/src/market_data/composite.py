"""Composite provider with cache-first priority chain."""

from __future__ import annotations

import hashlib
from collections.abc import Callable
from datetime import UTC, datetime
from typing import TypeVar

from app.backend.src.market_data.base import MarketDataProvider
from app.backend.src.market_data.cache import MarketDataCache
from app.backend.src.market_data.tracker import ProviderRequestTracker
from app.shared.types.market_data import (
    AssetMetadata,
    AssetSearchResult,
    AssetType,
    CurrentPrice,
    HistoricalPrices,
    MarketSummary,
    PriceInterval,
    PriceRange,
    ProviderHealth,
    SourceType,
)

T = TypeVar("T")


class CompositeMarketDataProvider(MarketDataProvider):
    """
    Priority:
      1. Cached data
      2. Official API provider
      3. CSV provider
      4. Scraping provider
      5. Mock provider
    """

    def __init__(
        self,
        *,
        cache: MarketDataCache,
        api: MarketDataProvider,
        csv: MarketDataProvider,
        scraping: MarketDataProvider,
        mock: MarketDataProvider,
        tracker: ProviderRequestTracker | None = None,
    ) -> None:
        self._cache = cache
        self._api = api
        self._csv = csv
        self._scraping = scraping
        self._mock = mock
        self._tracker = tracker

    @property
    def provider_name(self) -> str:
        return "composite"

    def _apply_cache_provenance(self, model: T) -> T:
        prov = model.provenance  # type: ignore[attr-defined]
        model.provenance = prov.model_copy(  # type: ignore[attr-defined]
            update={
                "source_type": SourceType.CACHE,
                "cached_at": datetime.now(UTC),
            }
        )
        return model

    async def _cached_or_fetch(
        self,
        cache_key: str,
        model_type: type,
        fetchers: list[tuple[MarketDataProvider, Callable]],
    ):
        cached = await self._cache.get(cache_key, model_type)
        if cached is not None:
            if self._tracker:
                await self._tracker.log(
                    provider_name="cache",
                    source_type=SourceType.CACHE,
                    endpoint_or_url=cache_key,
                    status="success",
                    cache_hit=True,
                )
            return self._apply_cache_provenance(cached)

        for provider, fetch in fetchers:
            result = await fetch(provider)
            if result is not None:
                await self._cache.set(cache_key, result)
                return result
        return None

    async def search_assets(self, query: str, asset_type: AssetType | None = None) -> list[AssetSearchResult]:
        key = self._cache.cache_key(
            "search",
            asset_type.value if asset_type else "all",
            hashlib.sha256(query.lower().encode()).hexdigest()[:16],
        )
        cached = await self._cache.get_list(key, AssetSearchResult)
        if cached is not None:
            return [self._apply_cache_provenance(r) for r in cached]

        for provider in (self._api, self._mock):
            results = await provider.search_assets(query, asset_type)
            if results:
                await self._cache.set(key, results)
                return results
        return []

    async def get_current_price(self, symbol: str, asset_type: AssetType) -> CurrentPrice | None:
        prefix = "crypto" if asset_type == AssetType.CRYPTO else "stock"
        key = self._cache.cache_key(prefix, "price", symbol.upper())

        async def _fetch(p: MarketDataProvider) -> CurrentPrice | None:
            return await p.get_current_price(symbol, asset_type)

        result = await self._cached_or_fetch(
            key,
            CurrentPrice,
            [
                (self._api, _fetch),
                (self._csv, _fetch),
                (self._scraping, _fetch),
                (self._mock, _fetch),
            ],
        )
        if result is None:
            return await self._mock.get_current_price(symbol, asset_type)
        return result

    async def get_historical_prices(
        self,
        symbol: str,
        asset_type: AssetType,
        range: PriceRange,
        interval: PriceInterval,
    ) -> HistoricalPrices | None:
        key = self._cache.cache_key(
            "hist", asset_type.value, symbol.upper(), range.value, interval.value
        )

        async def _fetch(p: MarketDataProvider) -> HistoricalPrices | None:
            return await p.get_historical_prices(symbol, asset_type, range, interval)

        result = await self._cached_or_fetch(
            key,
            HistoricalPrices,
            [
                (self._api, _fetch),
                (self._csv, _fetch),
                (self._mock, _fetch),
            ],
        )
        return result

    async def get_asset_metadata(self, symbol: str, asset_type: AssetType) -> AssetMetadata | None:
        key = self._cache.cache_key("meta", asset_type.value, symbol.upper())

        async def _fetch(p: MarketDataProvider) -> AssetMetadata | None:
            return await p.get_asset_metadata(symbol, asset_type)

        return await self._cached_or_fetch(
            key,
            AssetMetadata,
            [
                (self._api, _fetch),
                (self._csv, _fetch),
                (self._mock, _fetch),
            ],
        )

    async def get_market_summary(self) -> MarketSummary | None:
        key = self._cache.cache_key("summary", "market")

        async def _fetch(p: MarketDataProvider) -> MarketSummary | None:
            return await p.get_market_summary()

        return await self._cached_or_fetch(
            key,
            MarketSummary,
            [
                (self._api, _fetch),
                (self._mock, _fetch),
            ],
        )

    async def get_provider_health(self) -> ProviderHealth:
        checks = await asyncio_gather_health(
            self._api,
            self._csv,
            self._scraping,
            self._mock,
        )
        healthy = any(c.healthy for c in checks)
        return ProviderHealth(
            provider_name=self.provider_name,
            healthy=healthy,
            message="; ".join(f"{c.provider_name}={'ok' if c.healthy else 'down'}" for c in checks),
            checked_at=datetime.now(UTC),
        )


async def asyncio_gather_health(*providers: MarketDataProvider) -> list[ProviderHealth]:
    import asyncio

    return list(await asyncio.gather(*(p.get_provider_health() for p in providers)))
