"""Watchlist routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from marketpulse.deps import get_market_provider_dep
from marketpulse.domain.models import Watchlist, WatchlistItem
from marketpulse.providers.base import MarketDataProvider

DEFAULT_WATCHLIST = ("AAPL", "MSFT", "NVDA", "BTC", "ETH", "SOL", "EUR/USD")

router = APIRouter(prefix="/watchlist", tags=["watchlist"])


@router.get("", response_model=Watchlist)
async def get_watchlist(
    provider: MarketDataProvider = Depends(get_market_provider_dep),
) -> Watchlist:
    items: list[WatchlistItem] = []
    for symbol in DEFAULT_WATCHLIST:
        try:
            quote = await provider.get_quote(symbol)
        except KeyError as exc:
            raise HTTPException(status_code=404, detail=str(exc)) from exc
        items.append(
            WatchlistItem(
                symbol=quote.symbol,
                name=quote.name,
                asset_class=quote.asset_class,
                price=quote.price,
                change_percent=quote.change_percent,
            )
        )
    return Watchlist(items=items)
