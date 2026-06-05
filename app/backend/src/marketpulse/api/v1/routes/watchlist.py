"""Watchlist routes."""

from __future__ import annotations

import logging
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from marketpulse.api.errors import AlertApiError
from marketpulse.db.session import get_db_session
from marketpulse.deps import get_current_user, get_market_provider_dep
from marketpulse.domain.auth import CurrentUser
from marketpulse.domain.models import (
    RebalanceSummary,
    UpdateWatchlistAllocationRequest,
    UpdateWatchlistAllocationResponse,
    UpdateWatchlistInvestedRequest,
    UpdateWatchlistInvestedResponse,
    Watchlist,
    WatchlistItem,
)
from marketpulse.domain.watchlist import DEFAULT_WATCHLIST, is_watchlist_symbol
from marketpulse.providers.base import MarketDataProvider
from marketpulse.services import portfolio_snapshots as snapshot_service
from marketpulse.services import watchlist_allocations as allocation_service
from marketpulse.services import watchlist_rebalance as rebalance_service

logger = logging.getLogger(__name__)

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
    invested_cents_by_symbol: dict[str, int],
    rebalance_fields: rebalance_service.ItemRebalanceFields,
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
        invested_amount=rebalance_fields.invested_amount,
        current_weight_percent=rebalance_fields.current_weight_percent,
        drift_percent=rebalance_fields.drift_percent,
        suggestion_amount=rebalance_fields.suggestion_amount,
        drift_band=rebalance_fields.drift_band,
    )


async def _load_rebalance_context(
    session: AsyncSession,
    user_id: str,
) -> tuple[
    dict[str, int],
    dict[str, int],
    dict[str, rebalance_service.ItemRebalanceFields],
    RebalanceSummary,
]:
    targets_by_symbol = await allocation_service.list_targets(session, user_id)
    invested_cents_by_symbol = await allocation_service.list_invested(session, user_id)
    allocation_summary = allocation_service.build_allocation_summary(targets_by_symbol)
    item_rebalances, rebalance_summary = rebalance_service.compute_all_item_rebalances(
        symbols=list(DEFAULT_WATCHLIST),
        targets_by_symbol=targets_by_symbol,
        invested_cents_by_symbol=invested_cents_by_symbol,
        allocation_summary=allocation_summary,
    )
    return targets_by_symbol, invested_cents_by_symbol, item_rebalances, rebalance_summary


@router.get("", response_model=Watchlist)
async def get_watchlist(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    provider: Annotated[MarketDataProvider, Depends(get_market_provider_dep)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Watchlist:
    targets_by_symbol, invested_cents_by_symbol, item_rebalances, rebalance_summary = (
        await _load_rebalance_context(session, current_user.id)
    )
    try:
        await snapshot_service.ensure_daily_snapshot(
            session,
            current_user.id,
            provider,
            invested_cents_by_symbol,
        )
    except Exception:
        logger.exception("Failed to record daily portfolio snapshot for user %s", current_user.id)
    allocation_summary = allocation_service.build_allocation_summary(targets_by_symbol)
    items = [
        await _build_watchlist_item(
            provider,
            symbol,
            targets_by_symbol,
            invested_cents_by_symbol,
            item_rebalances[symbol],
        )
        for symbol in DEFAULT_WATCHLIST
    ]
    return Watchlist(
        items=items,
        allocation_summary=allocation_summary,
        rebalance_summary=rebalance_summary,
    )


@router.patch(
    "/items/{symbol:path}/allocation",
    response_model=UpdateWatchlistAllocationResponse,
)
async def update_watchlist_allocation(
    symbol: str,
    payload: UpdateWatchlistAllocationRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
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
        user_id=current_user.id,
        symbol=normalized,
        target_bps=target_bps,
    )
    invested_cents_by_symbol = await allocation_service.list_invested(session, current_user.id)
    allocation_summary = allocation_service.build_allocation_summary(targets_by_symbol)
    item_rebalances, rebalance_summary = rebalance_service.compute_all_item_rebalances(
        symbols=list(DEFAULT_WATCHLIST),
        targets_by_symbol=targets_by_symbol,
        invested_cents_by_symbol=invested_cents_by_symbol,
        allocation_summary=allocation_summary,
    )
    return UpdateWatchlistAllocationResponse(
        item=await _build_watchlist_item(
            provider,
            normalized,
            targets_by_symbol,
            invested_cents_by_symbol,
            item_rebalances[normalized],
        ),
        allocation_summary=allocation_summary,
        rebalance_summary=rebalance_summary,
    )


@router.patch(
    "/items/{symbol:path}/invested",
    response_model=UpdateWatchlistInvestedResponse,
)
async def update_watchlist_invested(
    symbol: str,
    payload: UpdateWatchlistInvestedRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    provider: Annotated[MarketDataProvider, Depends(get_market_provider_dep)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> UpdateWatchlistInvestedResponse:
    normalized = _normalize_symbol(symbol)
    if not is_watchlist_symbol(normalized):
        raise _validation_error(
            f"Symbol '{normalized}' is not on the watchlist",
            details={"symbol": normalized},
        )

    amount_cents = (
        allocation_service.invested_amount_to_cents(payload.invested_amount)
        if payload.invested_amount is not None
        else None
    )
    invested_cents_by_symbol = await allocation_service.set_invested(
        session,
        user_id=current_user.id,
        symbol=normalized,
        amount_cents=amount_cents,
    )
    targets_by_symbol = await allocation_service.list_targets(session, current_user.id)
    allocation_summary = allocation_service.build_allocation_summary(targets_by_symbol)
    item_rebalances, rebalance_summary = rebalance_service.compute_all_item_rebalances(
        symbols=list(DEFAULT_WATCHLIST),
        targets_by_symbol=targets_by_symbol,
        invested_cents_by_symbol=invested_cents_by_symbol,
        allocation_summary=allocation_summary,
    )
    return UpdateWatchlistInvestedResponse(
        item=await _build_watchlist_item(
            provider,
            normalized,
            targets_by_symbol,
            invested_cents_by_symbol,
            item_rebalances[normalized],
        ),
        allocation_summary=allocation_summary,
        rebalance_summary=rebalance_summary,
    )
