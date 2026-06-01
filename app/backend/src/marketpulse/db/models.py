"""ORM models for MarketPulse persistence."""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from marketpulse.db.base import Base


class PriceAlertRow(Base):
    """Persisted price alert (ADR-011)."""

    __tablename__ = "price_alerts"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    symbol: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    direction: Mapped[str] = mapped_column(String(8), nullable=False)
    target_price: Mapped[float] = mapped_column(Float, nullable=False)
    triggered_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)


class WatchlistAllocationTargetRow(Base):
    """Persisted allocation target keyed by normalized watchlist symbol."""

    __tablename__ = "watchlist_allocation_targets"

    symbol: Mapped[str] = mapped_column(String(32), primary_key=True)
    target_bps: Mapped[int] = mapped_column(Integer, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
