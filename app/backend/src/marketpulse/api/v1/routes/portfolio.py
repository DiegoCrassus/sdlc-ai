"""Portfolio snapshot and history routes (INVES-118)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from marketpulse.api.errors import AlertApiError
from marketpulse.db.session import get_db_session
from marketpulse.deps import get_current_user, get_market_provider_dep
from marketpulse.domain.auth import CurrentUser
from marketpulse.domain.models import CreateSnapshotResponse, HistoryDays, PortfolioHistoryResponse
from marketpulse.providers.base import MarketDataProvider
from marketpulse.services import portfolio_snapshots as snapshot_service
from marketpulse.services import watchlist_allocations as allocation_service

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

_VALID_HISTORY_DAYS: set[int] = {30, 90, 365}


def _validation_error(message: str, details: dict[str, object] | None = None) -> AlertApiError:
    return AlertApiError(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="VALIDATION_ERROR",
        message=message,
        details=details,
    )


@router.post("/snapshots", response_model=CreateSnapshotResponse)
async def create_snapshot(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    provider: Annotated[MarketDataProvider, Depends(get_market_provider_dep)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> CreateSnapshotResponse:
    invested_cents_by_symbol = await allocation_service.list_invested(session, current_user.id)
    return await snapshot_service.record_snapshot(
        session,
        current_user.id,
        provider,
        invested_cents_by_symbol,
        upsert=True,
    )


@router.get("/history", response_model=PortfolioHistoryResponse)
async def get_portfolio_history(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    days: Annotated[int, Query()] = 30,
) -> PortfolioHistoryResponse:
    if days not in _VALID_HISTORY_DAYS:
        raise _validation_error(
            "days must be one of 30, 90, or 365",
            details={"days": days},
        )
    history_days: HistoryDays = days  # type: ignore[assignment]
    return await snapshot_service.get_history(session, current_user.id, days=history_days)
