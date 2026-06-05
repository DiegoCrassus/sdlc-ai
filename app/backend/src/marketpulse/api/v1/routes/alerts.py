"""Price alert routes (ADR-011)."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from marketpulse.api.errors import AlertApiError
from marketpulse.db.session import get_db_session
from marketpulse.deps import get_current_user, get_market_provider_dep
from marketpulse.domain.auth import CurrentUser
from marketpulse.domain.models import (
    AlertListResponse,
    CreateAlertRequest,
    PriceAlert,
)
from marketpulse.domain.watchlist import is_watchlist_symbol
from marketpulse.providers.base import MarketDataProvider
from marketpulse.services import alerts as alert_service

router = APIRouter(prefix="/alerts", tags=["alerts"])


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


@router.post("", response_model=PriceAlert, status_code=status.HTTP_201_CREATED)
async def create_alert(
    payload: CreateAlertRequest,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> PriceAlert:
    symbol = payload.symbol.upper()
    if not is_watchlist_symbol(symbol):
        raise _validation_error(
            f"Symbol '{symbol}' is not on the watchlist",
            details={"symbol": symbol},
        )
    normalized = CreateAlertRequest(
        symbol=symbol,
        direction=payload.direction,
        target_price=payload.target_price,
    )
    return await alert_service.create_alert(session, current_user.id, normalized)


@router.get("", response_model=AlertListResponse)
async def list_alerts(
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
    provider: Annotated[MarketDataProvider, Depends(get_market_provider_dep)],
    symbol: Annotated[str | None, Query()] = None,
) -> AlertListResponse:
    if symbol is not None and not is_watchlist_symbol(symbol):
        raise _validation_error(
            f"Symbol '{symbol.upper()}' is not on the watchlist",
            details={"symbol": symbol.upper()},
        )
    filter_symbol = symbol.upper() if symbol is not None else None
    await alert_service.evaluate_pending_alerts(
        session,
        current_user.id,
        provider,
        symbol=filter_symbol,
    )
    items = await alert_service.list_alerts(session, current_user.id, symbol=filter_symbol)
    return AlertListResponse(items=items)


@router.delete("/{alert_id}", status_code=status.HTTP_204_NO_CONTENT, response_class=Response)
async def delete_alert(
    alert_id: str,
    current_user: Annotated[CurrentUser, Depends(get_current_user)],
    session: Annotated[AsyncSession, Depends(get_db_session)],
) -> Response:
    deleted = await alert_service.delete_alert(session, current_user.id, alert_id)
    if not deleted:
        raise _not_found_error(f"Alert '{alert_id}' not found")
    return Response(status_code=status.HTTP_204_NO_CONTENT)
