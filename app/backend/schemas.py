"""API schemas."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel

AssetType = Literal["stock", "crypto"]
HistoryRange = Literal["1d", "7d", "30d", "90d"]
DataSourceStatus = Literal["live", "fallback", "unavailable"]


class PricePoint(BaseModel):
    timestamp: datetime
    price: float


class AssetQuote(BaseModel):
    symbol: str
    asset_type: AssetType
    name: str
    currency: str = "USD"
    price: float
    change_24h: float | None = None
    change_pct_24h: float | None = None
    market_cap: float | None = None
    volume_24h: float | None = None
    source: DataSourceStatus
    as_of: datetime


class AssetSearchResult(BaseModel):
    symbol: str
    asset_type: AssetType
    name: str
    exchange_or_network: str | None = None


class AssetDetail(AssetQuote):
    description: str | None = None
    high_52w: float | None = None
    low_52w: float | None = None


class PriceHistory(BaseModel):
    symbol: str
    asset_type: AssetType
    range: HistoryRange
    points: list[PricePoint]
    source: DataSourceStatus
