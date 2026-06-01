"""Async engine and session factory."""

from __future__ import annotations

from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from marketpulse.config import Settings, get_settings
from marketpulse.db import models as _models  # noqa: F401 — register metadata
from marketpulse.db.base import Base

_engine: AsyncEngine | None = None
_session_factory: async_sessionmaker[AsyncSession] | None = None


def _build_engine(database_url: str) -> AsyncEngine:
    return create_async_engine(database_url, echo=False)


def configure_engine(database_url: str) -> None:
    """Configure global engine and session factory (used in tests)."""
    global _engine, _session_factory
    if _engine is not None:
        raise RuntimeError("Database engine already configured")
    _engine = _build_engine(database_url)
    _session_factory = async_sessionmaker(_engine, expire_on_commit=False)


async def init_db(settings: Settings | None = None) -> None:
    """Create tables if missing."""
    resolved = settings or get_settings()
    global _engine, _session_factory
    if _engine is None:
        _engine = _build_engine(resolved.database_url)
        _session_factory = async_sessionmaker(_engine, expire_on_commit=False)
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


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
