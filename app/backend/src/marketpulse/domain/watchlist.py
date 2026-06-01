"""Watchlist membership for MarketPulse MVP."""

from __future__ import annotations

DEFAULT_WATCHLIST: tuple[str, ...] = (
    "AAPL",
    "MSFT",
    "NVDA",
    "BTC",
    "ETH",
    "SOL",
    "EUR/USD",
)


def is_watchlist_symbol(symbol: str) -> bool:
    """Return True when symbol is on the default watchlist."""
    return symbol.upper() in DEFAULT_WATCHLIST
