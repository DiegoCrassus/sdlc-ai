"""Shared market data types used by backend and frontend contract generation."""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class AssetType(str, Enum):
    STOCK = "stock"
    CRYPTO = "crypto"
    INDEX = "index"
    FX = "fx"
    ETF = "etf"


class SourceType(str, Enum):
    API = "api"
    CSV = "csv"
    SCRAPING = "scraping"
    MOCK = "mock"
    CACHE = "cache"


class ConfidenceLevel(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class PriceRange(str, Enum):
    DAY = "1d"
    WEEK = "1w"
    MONTH = "1mo"
    THREE_MONTHS = "3mo"
    SIX_MONTHS = "6mo"
    YEAR = "1y"
    FIVE_YEARS = "5y"
    MAX = "max"


class PriceInterval(str, Enum):
    MINUTE = "1m"
    HOUR = "1h"
    DAY = "1d"
    WEEK = "1wk"


class DataProvenance(BaseModel):
    provider_name: str
    source_type: SourceType
    source_url: str | None = None
    fetched_at: datetime
    cached_at: datetime | None = None
    is_realtime: bool = False
    is_delayed: bool = False
    confidence_level: ConfidenceLevel = ConfidenceLevel.HIGH
    warning: str | None = None


class AssetSearchResult(BaseModel):
    symbol: str
    name: str
    asset_type: AssetType
    exchange: str | None = None
    currency: str | None = None
    provenance: DataProvenance


class PricePoint(BaseModel):
    timestamp: datetime
    open: float | None = None
    high: float | None = None
    low: float | None = None
    close: float
    volume: float | None = None


class CurrentPrice(BaseModel):
    symbol: str
    asset_type: AssetType
    price: float
    currency: str
    change: float | None = None
    change_percent: float | None = None
    provenance: DataProvenance


class HistoricalPrices(BaseModel):
    symbol: str
    asset_type: AssetType
    range: PriceRange
    interval: PriceInterval
    points: list[PricePoint]
    provenance: DataProvenance


class AssetMetadata(BaseModel):
    symbol: str
    asset_type: AssetType
    name: str
    description: str | None = None
    sector: str | None = None
    industry: str | None = None
    market_cap: float | None = None
    currency: str | None = None
    exchange: str | None = None
    website: str | None = None
    extra: dict[str, Any] = Field(default_factory=dict)
    provenance: DataProvenance


class MarketIndexSummary(BaseModel):
    symbol: str
    name: str
    price: float
    change_percent: float | None = None


class MarketSummary(BaseModel):
    indexes: list[MarketIndexSummary]
    updated_at: datetime
    provenance: DataProvenance


class ProviderHealth(BaseModel):
    provider_name: str
    healthy: bool
    latency_ms: float | None = None
    message: str | None = None
    checked_at: datetime
