"""SQLAlchemy ORM models."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.backend.database import Base

DEFAULT_PORTFOLIO_CASH = 100_000.0
DEFAULT_PORTFOLIO_CURRENCY = "USD"
DEFAULT_PORTFOLIO_NAME = "My Portfolio"


class WatchlistItemRow(Base):
    """Persisted watchlist entry (single implicit watchlist)."""

    __tablename__ = "watchlist_items"

    asset_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    sort_order: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class PortfolioRow(Base):
    """Single default simulated portfolio."""

    __tablename__ = "portfolios"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(128), nullable=False)
    base_currency: Mapped[str] = mapped_column(String(3), nullable=False)
    cash_balance: Mapped[float] = mapped_column(Float, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
        nullable=False,
    )


class HoldingRow(Base):
    """Position in the default portfolio."""

    __tablename__ = "holdings"

    portfolio_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("portfolios.id"), primary_key=True
    )
    asset_id: Mapped[str] = mapped_column(String(64), primary_key=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    avg_cost: Mapped[float] = mapped_column(Float, nullable=False)


class TransactionRow(Base):
    """Simulated buy/sell record."""

    __tablename__ = "transactions"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    portfolio_id: Mapped[str] = mapped_column(
        String(36), ForeignKey("portfolios.id"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(String(4), nullable=False)
    asset_id: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    quantity: Mapped[float] = mapped_column(Float, nullable=False)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    total: Mapped[float] = mapped_column(Float, nullable=False)
    source: Mapped[str] = mapped_column(String(16), nullable=False)
    executed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
