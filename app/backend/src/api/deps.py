"""FastAPI dependencies."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request

from app.backend.src.market_data.composite import CompositeMarketDataProvider


def get_market_provider(request: Request) -> CompositeMarketDataProvider:
    provider: CompositeMarketDataProvider = request.app.state.market_provider
    return provider


MarketProviderDep = Annotated[CompositeMarketDataProvider, Depends(get_market_provider)]
