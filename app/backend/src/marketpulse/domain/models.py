"""Pydantic domain models for MarketPulse."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Literal

from marketpulse.domain.enums import (
    AlertDirection,
    AssetClass,
    DataSource,
    Interval,
    TrendDirection,
)
from pydantic import BaseModel, Field, field_validator


class SourceMeta(BaseModel):
    source: DataSource
    provider: str
    fetched_at: datetime
    latency_ms: float | None = None


class Quote(BaseModel):
    asset_id: str
    symbol: str
    name: str
    asset_class: AssetClass
    price: float
    change: float
    change_percent: float
    volume_24h: float | None = None
    market_cap: float | None = None
    high_24h: float | None = None
    low_24h: float | None = None
    currency: str = "USD"
    meta: SourceMeta


class PricePoint(BaseModel):
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float


class PriceHistory(BaseModel):
    asset_id: str
    interval: Interval
    points: list[PricePoint]
    meta: SourceMeta


class SearchHit(BaseModel):
    asset_id: str
    symbol: str
    name: str
    asset_class: AssetClass
    exchange: str | None = None


class IndexSnapshot(BaseModel):
    asset_id: str
    name: str
    value: float
    change_percent: float


class MarketMover(BaseModel):
    asset_id: str
    symbol: str
    name: str
    asset_class: AssetClass
    price: float
    change_percent: float


class MarketOverview(BaseModel):
    total_market_cap_usd: float
    total_volume_24h_usd: float
    btc_dominance_percent: float
    fear_greed_index: int = Field(ge=0, le=100)
    active_assets: int
    indices: list[IndexSnapshot]
    top_gainers: list[MarketMover]
    top_losers: list[MarketMover]
    meta: SourceMeta


class TechnicalIndicators(BaseModel):
    rsi_14: float
    macd: float
    macd_signal: float
    sma_20: float
    sma_50: float
    bollinger_upper: float
    bollinger_lower: float


class ProjectionPoint(BaseModel):
    timestamp: datetime
    price: float
    lower_bound: float
    upper_bound: float


class ProjectionScenario(BaseModel):
    name: str
    direction: TrendDirection
    confidence: float = Field(ge=0, le=1)
    points: list[ProjectionPoint]


class AssetProjection(BaseModel):
    asset_id: str
    horizon_days: int
    current_price: float
    indicators: TechnicalIndicators
    scenarios: list[ProjectionScenario]
    disclaimer: str
    meta: SourceMeta


class AssetDetail(BaseModel):
    asset_id: str
    symbol: str
    name: str
    asset_class: AssetClass
    description: str
    quote: Quote
    history_preview: list[PricePoint]
    indicators: TechnicalIndicators


class WatchlistItem(BaseModel):
    symbol: str
    name: str
    asset_class: AssetClass
    price: float
    change_percent: float
    target_percent: float | None = None


class WatchlistAllocationSummary(BaseModel):
    target_percent_total: float
    status: Literal["under_allocated", "balanced", "over_allocated"]


class Watchlist(BaseModel):
    items: list[WatchlistItem]
    allocation_summary: WatchlistAllocationSummary


class UpdateWatchlistAllocationRequest(BaseModel):
    target_percent: Decimal | None

    @field_validator("target_percent", mode="before")
    @classmethod
    def validate_target_percent(cls, value: object) -> Decimal | None:
        if value is None:
            return None
        if isinstance(value, bool):
            raise ValueError("target_percent must be a decimal percent")
        try:
            decimal_value = Decimal(str(value))
        except (InvalidOperation, ValueError) as exc:
            raise ValueError("target_percent must be a decimal percent") from exc
        if not decimal_value.is_finite():
            raise ValueError("target_percent must be finite")
        if decimal_value <= 0 or decimal_value > 100:
            raise ValueError("target_percent must be > 0 and <= 100")
        if decimal_value.as_tuple().exponent < -2:
            raise ValueError("target_percent must have at most two decimal places")
        return decimal_value


class UpdateWatchlistAllocationResponse(BaseModel):
    item: WatchlistItem
    allocation_summary: WatchlistAllocationSummary


class HealthResponse(BaseModel):
    status: str
    provider: str


class CreateAlertRequest(BaseModel):
    symbol: str = Field(min_length=1)
    direction: AlertDirection
    target_price: float = Field(gt=0)


class PriceAlert(BaseModel):
    id: str
    symbol: str
    direction: AlertDirection
    target_price: float = Field(gt=0)
    triggered_at: datetime | None
    created_at: datetime


class AlertListResponse(BaseModel):
    items: list[PriceAlert]


class ApiErrorBody(BaseModel):
    code: str
    message: str
    details: dict[str, object] | None = None


class AlertErrorResponse(BaseModel):
    error: ApiErrorBody
