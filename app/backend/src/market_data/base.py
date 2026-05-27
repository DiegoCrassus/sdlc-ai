"""Abstract market data provider contract."""

from __future__ import annotations

from abc import ABC, abstractmethod

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
)


class MarketDataProvider(ABC):
    """Contract for all market data providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable provider identifier."""

    @abstractmethod
    async def search_assets(self, query: str, asset_type: AssetType | None = None) -> list[AssetSearchResult]:
        ...

    @abstractmethod
    async def get_current_price(self, symbol: str, asset_type: AssetType) -> CurrentPrice | None:
        ...

    @abstractmethod
    async def get_historical_prices(
        self,
        symbol: str,
        asset_type: AssetType,
        range: PriceRange,
        interval: PriceInterval,
    ) -> HistoricalPrices | None:
        ...

    @abstractmethod
    async def get_asset_metadata(self, symbol: str, asset_type: AssetType) -> AssetMetadata | None:
        ...

    @abstractmethod
    async def get_market_summary(self) -> MarketSummary | None:
        ...

    @abstractmethod
    async def get_provider_health(self) -> ProviderHealth:
        ...
