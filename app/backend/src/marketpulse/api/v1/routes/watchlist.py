"""Watchlist routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from marketpulse.api.errors import AlertApiError
from marketpulse.db.session import get_db_session
from marketpulse.deps import get_market_provider_dep
from marketpulse.domain.models import (
    UpdateWatchlistAllocationRequest,
    UpdateWatchlistAllocationResponse,
    Watchlist,
    WatchlistItem,
)
from marketpulse.domain.watchlist import DEFAULT_WATCHLIST, is_watchlist_symbol
from marketpulse.providers.base import MarketDataProvider
from marketpulse.services import watchlist_allocations as allocation_service

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


def _validation_error(message: str, details: dict[str, object] | None = None) -> AlertApiError:
    return AlertApiError(
        status_code=status.HTTP_400_BAD_REQUEST,
        code="VALIDATION_ERROR",
        message=message,
        details=details,
    )


def _not_found_error(message: str) -> AlertApiError:
    return AlertApiError(
        status_code=status.HTTP_404_NOT_FOUND,
        code="NOT_FOUND",
        message=message,
    )


def _normalize_symbol(symbol: str) -> str:
    return symbol.strip().upper()


async def _build_watchlist_item(
    provider: MarketDataProvider,
    symbol: str,
    targets_by_symbol: dict[str, int],
) -> WatchlistItem:
    try:
        quote = await provider.get_quote(symbol)
    except KeyError as exc:
        raise _not_found_error(f"Symbol '{symbol}' not found") from exc
    target_bps = targets_by_symbol.get(symbol)
    return WatchlistItem(
        symbol=quote.symbol,
        name=quote.name,
        asset_class=quote.asset_class,
        price=quote.price,
        change_percent=quote.change_percent,
        target_percent=(
            allocation_service.bps_to_target_percent(target_bps)
            if target_bps is not None
            else None
        ),
    )


@router.get("", response_model=Watchlist)
async def get_watchlist(
    provider: Annotated[MarketDataProvider, Depends(get_market_provider_dep)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Watchlist:
    targets_by_symbol = await allocation_service.list_targets(session)
    items = [
        await _build_watchlist_item(provider, symbol, targets_by_symbol)
        for symbol in DEFAULT_WATCHLIST
    ]
    return Watchlist(
        items=items,
        allocation_summary=allocation_service.build_allocation_summary(targets_by_symbol),
    )


@router.patch(
    "/items/{symbol:path}/allocation",
    response_model=UpdateWatchlistAllocationResponse,
)
async def update_watchlist_allocation(
    symbol: str,
    payload: UpdateWatchlistAllocationRequest,
    provider: Annotated[MarketDataProvider, Depends(get_market_provider_dep)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UpdateWatchlistAllocationResponse:
    normalized = _normalize_symbol(symbol)
    if not is_watchlist_symbol(normalized):
        raise _validation_error(
            f"Symbol '{normalized}' is not on the watchlist",
            details={"symbol": normalized},
        )

    target_bps = (
        allocation_service.target_percent_to_bps(payload.target_percent)
        if payload.target_percent is not None
        else None
    )
    targets_by_symbol = await allocation_service.set_target(
        session,
        symbol=normalized,
        target_bps=target_bps,
    )
    return UpdateWatchlistAllocationResponse(
        item=await _build_watchlist_item(provider, normalized, targets_by_symbol),
        allocation_summary=allocation_service.build_allocation_summary(targets_by_symbol),
    )
