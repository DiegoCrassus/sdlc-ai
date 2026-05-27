"""Asset ID parsing utilities."""

from __future__ import annotations

from typing import Literal

AssetClass = Literal["stock", "crypto"]

VALID_CLASSES: frozenset[str] = frozenset({"stock", "crypto"})


class AssetIdError(ValueError):
    """Raised when an asset ID cannot be parsed."""


def format_asset_id(asset_class: AssetClass, symbol: str) -> str:
    """Build canonical asset ID `{class}:{symbol}`."""
    return f"{asset_class}:{symbol.upper()}"


def parse_asset_id(asset_id: str) -> tuple[AssetClass, str]:
    """Parse `{class}:{symbol}` into class and uppercase symbol."""
    if not asset_id or ":" not in asset_id:
        raise AssetIdError("Asset ID must use format '{class}:{symbol}'")

    asset_class, _, symbol = asset_id.partition(":")
    asset_class = asset_class.strip().lower()
    symbol = symbol.strip().upper()

    if asset_class not in VALID_CLASSES:
        raise AssetIdError(f"Invalid asset class '{asset_class}'; expected stock or crypto")
    if not symbol:
        raise AssetIdError("Asset symbol is required")

    return asset_class, symbol  # type: ignore[return-value]
