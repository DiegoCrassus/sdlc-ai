"""FastAPI dependency factories."""

from __future__ import annotations

from functools import lru_cache
from typing import Annotated

from fastapi import Depends, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from marketpulse.api.errors import AlertApiError
from marketpulse.config import Settings, get_settings
from marketpulse.db.session import get_db_session
from marketpulse.domain.auth import CurrentUser
from marketpulse.providers.base import MarketDataProvider, NotConfiguredError
from marketpulse.providers.mock import MockMarketDataProvider
from marketpulse.providers.twelve_data import TwelveDataProvider
from marketpulse.services import auth as auth_service


@lru_cache
def _build_provider(provider_name: str, seed: int) -> MarketDataProvider:
    if provider_name == "mock":
        return MockMarketDataProvider(seed=seed)
    if provider_name == "twelve_data":
        return TwelveDataProvider()
    raise ValueError(f"Unsupported market data provider: {provider_name}")


def get_market_provider(settings: Settings | None = None) -> MarketDataProvider:
    """Return configured market data provider."""
    resolved = settings or get_settings()
    try:
        return _build_provider(resolved.market_data_provider, resolved.mock_seed)
    except NotConfiguredError:
        raise


def get_market_provider_dep() -> MarketDataProvider:
    """FastAPI Depends wrapper."""
    return get_market_provider()


def _unauthorized_error() -> AlertApiError:
    return AlertApiError(
        status_code=status.HTTP_401_UNAUTHORIZED,
        code="UNAUTHORIZED",
        message="Valid session required",
    )


async def get_current_user(
    request: Request,
    session: Annotated[AsyncSession, Depends(get_db_session)],
    settings: Annotated[Settings, Depends(get_settings)],
) -> CurrentUser:
    """Resolve authenticated user from HttpOnly session cookie."""
    token = request.cookies.get(settings.session_cookie_name)
    if not token:
        raise _unauthorized_error()
    user = await auth_service.resolve_session(session, token)
    if user is None:
        raise _unauthorized_error()
    return user
