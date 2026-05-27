"""API schemas aligned with investment-radar-api.md."""

from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field

AssetClass = Literal["stock", "crypto"]
DataSource = Literal["live", "fallback"]
HistoryInterval = Literal["1d", "1h"]


class Asset(BaseModel):
    id: str
    asset_class: str = Field(alias="class")
    symbol: str
    name: str
    currency: str
    exchange: str | None = None
    source: DataSource | None = None

    model_config = {"populate_by_name": True}


class Quote(BaseModel):
    asset_id: str
    price: float
    change: float | None = None
    change_percent: float | None = None
    currency: str
    timestamp: datetime
    source: DataSource


class PricePoint(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float | None = None


class PaginatedAssets(BaseModel):
    items: list[Asset]
    total: int
    limit: int
    offset: int


class BatchQuotes(BaseModel):
    items: list[Quote]
    missing: list[str]


class HistoryResponse(BaseModel):
    asset_id: str
    interval: HistoryInterval
    source: DataSource
    points: list[PricePoint]


class WatchlistItem(BaseModel):
    asset_id: str
    asset: Asset | None = None
    quote: Quote | None = None
    notes: str | None = None
    sort_order: int = 0
    added_at: datetime


class PaginatedWatchlist(BaseModel):
    items: list[WatchlistItem]
    total: int
    limit: int
    offset: int


class WatchlistItemCreate(BaseModel):
    asset_id: str
    notes: str | None = Field(None, max_length=500)
    sort_order: int = 0


class WatchlistItemUpdate(BaseModel):
    notes: str | None = Field(None, max_length=500)
    sort_order: int | None = None
