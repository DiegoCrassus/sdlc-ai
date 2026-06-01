"""Domain enumerations."""

from enum import StrEnum


class AssetClass(StrEnum):
    STOCK = "stock"
    CRYPTO = "crypto"
    INDEX = "index"
    FOREX = "forex"
    COMMODITY = "commodity"


class DataSource(StrEnum):
    MOCK = "mock"
    LIVE = "live"
    FALLBACK = "fallback"


class TrendDirection(StrEnum):
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


class Interval(StrEnum):
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    HOUR_1 = "1h"
    DAY_1 = "1d"
    WEEK_1 = "1w"


class AlertDirection(StrEnum):
    ABOVE = "above"
    BELOW = "below"
