"""Provenance helpers."""

from __future__ import annotations

from datetime import UTC, datetime

from app.shared.types.market_data import ConfidenceLevel, DataProvenance, SourceType


def make_provenance(
    *,
    provider_name: str,
    source_type: SourceType,
    source_url: str | None = None,
    is_realtime: bool = False,
    is_delayed: bool = False,
    confidence_level: ConfidenceLevel = ConfidenceLevel.HIGH,
    warning: str | None = None,
    fetched_at: datetime | None = None,
    cached_at: datetime | None = None,
) -> DataProvenance:
    return DataProvenance(
        provider_name=provider_name,
        source_type=source_type,
        source_url=source_url,
        fetched_at=fetched_at or datetime.now(UTC),
        cached_at=cached_at,
        is_realtime=is_realtime,
        is_delayed=is_delayed,
        confidence_level=confidence_level,
        warning=warning,
    )
