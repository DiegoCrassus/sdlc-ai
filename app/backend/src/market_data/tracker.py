"""Track external provider requests for observability."""

from __future__ import annotations

import os
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from app.backend.src.config import MarketDataConfig
from app.shared.types.market_data import AssetType, SourceType


class Base(DeclarativeBase):
    pass


class ProviderRequest(Base):
    __tablename__ = "provider_requests"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    provider_name: Mapped[str] = mapped_column(String(64), nullable=False)
    source_type: Mapped[str] = mapped_column(String(16), nullable=False)
    endpoint_or_url: Mapped[str | None] = mapped_column(String(512))
    symbol: Mapped[str | None] = mapped_column(String(64))
    asset_type: Mapped[str | None] = mapped_column(String(16))
    status: Mapped[str] = mapped_column(String(32), nullable=False)
    http_status: Mapped[int | None] = mapped_column(Integer)
    response_time_ms: Mapped[int | None] = mapped_column(Integer)
    cache_hit: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    error_message: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        nullable=False,
    )


class ProviderRequestTracker:
    def __init__(self, config: MarketDataConfig) -> None:
        self._ensure_sqlite_dir(config.database_url)
        self._engine = create_async_engine(config.database_url, echo=False)
        self._session_factory = async_sessionmaker(self._engine, expire_on_commit=False)

    @staticmethod
    def _ensure_sqlite_dir(database_url: str) -> None:
        if database_url.startswith("sqlite"):
            path_part = database_url.split("///", 1)[-1]
            db_path = Path(path_part)
            if db_path.parent and str(db_path.parent) not in (".", ""):
                os.makedirs(db_path.parent, exist_ok=True)

    async def init_db(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async def log(
        self,
        *,
        provider_name: str,
        source_type: SourceType,
        endpoint_or_url: str | None,
        symbol: str | None = None,
        asset_type: AssetType | None = None,
        status: str,
        http_status: int | None = None,
        response_time_ms: int | None = None,
        cache_hit: bool = False,
        error_message: str | None = None,
    ) -> None:
        record = ProviderRequest(
            provider_name=provider_name,
            source_type=source_type.value,
            endpoint_or_url=endpoint_or_url,
            symbol=symbol,
            asset_type=asset_type.value if asset_type else None,
            status=status,
            http_status=http_status,
            response_time_ms=response_time_ms,
            cache_hit=cache_hit,
            error_message=error_message,
        )
        async with self._session_factory() as session:
            session.add(record)
            await session.commit()

    async def dispose(self) -> None:
        await self._engine.dispose()

    @property
    def session_factory(self) -> async_sessionmaker[AsyncSession]:
        return self._session_factory
