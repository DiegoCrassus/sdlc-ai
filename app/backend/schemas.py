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


TransactionType = Literal["buy", "sell"]


class Portfolio(BaseModel):
    id: str
    name: str
    base_currency: str
    cash_balance: float
    total_value: float
    total_cost_basis: float
    unrealized_pnl: float
    updated_at: datetime


class Holding(BaseModel):
    asset_id: str
    asset: Asset | None = None
    quantity: float
    avg_cost: float
    market_price: float
    market_value: float
    cost_basis: float
    unrealized_pnl: float
    source: DataSource


class Transaction(BaseModel):
    id: str
    type: TransactionType
    asset_id: str
    quantity: float
    price: float
    total: float
    source: DataSource
    executed_at: datetime
    note: str | None = None


class PaginatedHoldings(BaseModel):
    items: list[Holding]
    total: int
    limit: int
    offset: int


class PaginatedTransactions(BaseModel):
    items: list[Transaction]
    total: int
    limit: int
    offset: int


class TransactionCreate(BaseModel):
    type: TransactionType
    asset_id: str
    quantity: float = Field(gt=0)
    note: str | None = Field(None, max_length=500)


class TransactionResponse(BaseModel):
    transaction: Transaction
    portfolio: Portfolio
    holding: Holding | None = None
