"""Async engine and session factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy import inspect, text
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from marketpulse.config import Settings, get_settings
from marketpulse.db import models as _models  # noqa: F401 — register metadata
from marketpulse.db.base import Base
from marketpulse.db.models import (
    PriceAlertRow,
    WatchlistAllocationTargetRow,
    WatchlistInvestedAmountRow,
)

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None

_USER_DATA_TABLES = (
    PriceAlertRow.__table__,
    WatchlistAllocationTargetRow.__table__,
    WatchlistInvestedAmountRow.__table__,
)


def _build_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, echo=False)


def configure_engine(database_url: str) -> None:
    """Configure global engine and session factory (used in tests)."""
    global _engine, _session_factory
    if _engine is not None:
        raise RuntimeError("Database engine already configured")
    _engine = _build_engine(database_url)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


def _migrate_auth_schema_sync(connection) -> None:
    """Destructive one-time migration from legacy global user-data tables."""
    inspector = inspect(connection)
    tables = set(inspector.get_table_names())
    if "price_alerts" not in tables:
        return

    columns = {column["name"] for column in inspector.get_columns("price_alerts")}
    if "user_id" in columns:
        return

    for table in _USER_DATA_TABLES:
        if table.name in tables:
            connection.execute(text(f"DELETE FROM {table.name}"))
            connection.execute(text(f"DROP TABLE {table.name}"))

    Base.metadata.create_all(connection, tables=list(_USER_DATA_TABLES))


async def migrate_auth_schema() -> None:
    """Apply idempotent auth schema migration when legacy tables lack user_id."""
    if _engine is None:
        return
    async with _engine.begin() as conn:
        await conn.run_sync(_migrate_auth_schema_sync)


async def init_db(settings: Settings | None = None) -> None:
    """Create tables if missing and migrate legacy user-data schema."""
    resolved = settings or get_settings()
    global _engine, _session_factory
    if _engine is None:
        _engine = _build_engine(resolved.database_url)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    await migrate_auth_schema()


async def dispose_engine() -> None:
    """Dispose engine (tests / shutdown)."""
    global _engine, _session_factory
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_factory = None


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    if _session_factory is None:
        raise RuntimeError("Database not initialized; call init_db() first")
    return _session_factory


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Yield an async DB session with commit/rollback."""
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
