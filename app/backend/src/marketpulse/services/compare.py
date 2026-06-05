"""Multi-asset compare: alignment, normalization, correlation, and metrics."""

from __future__ import annotations

import math
from datetime import UTC, date, datetime

from marketpulse.domain.enums import Interval
from marketpulse.domain.models import (
    CompareCorrelation,
    CompareDateRange,
    CompareMetric,
    ComparePoint,
    CompareResponse,
    CompareSeries,
    PriceHistory,
    PricePoint,
    SourceMeta,
)
from marketpulse.providers.base import MarketDataProvider


class InsufficientAlignedDataError(Exception):
    """Raised when inner-join yields fewer than two aligned calendar dates."""


def parse_compare_symbols(raw: str) -> list[str]:
    """Parse comma-separated symbols; preserve order, uppercase, dedupe."""
    seen: set[str] = set()
    symbols: list[str] = []
    for part in raw.split(","):
        symbol = part.strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        symbols.append(symbol)
    return symbols


def utc_calendar_date(timestamp: datetime) -> date:
    """Extract UTC calendar date from a timestamp."""
    if timestamp.tzinfo is None:
        return timestamp.date()
    return timestamp.astimezone(UTC).date()


def align_price_histories(
    histories: dict[str, PriceHistory],
) -> tuple[list[date], dict[str, dict[date, PricePoint]]]:
    """Inner-join OHLCV points by UTC calendar date across all symbols."""
    by_symbol: dict[str, dict[date, PricePoint]] = {}
    date_sets: list[set[date]] = []

    for symbol, history in histories.items():
        points_by_date: dict[date, PricePoint] = {}
        for point in history.points:
            day = utc_calendar_date(point.timestamp)
            points_by_date[day] = point
        by_symbol[symbol] = points_by_date
        date_sets.append(set(points_by_date))

    if not date_sets:
        return [], by_symbol

    aligned_dates = sorted(set.intersection(*date_sets))
    return aligned_dates, by_symbol


def normalize_points(closes: list[float], base: float = 100.0) -> list[float]:
    """Scale closes so the first value equals ``base`` (default 100)."""
    if not closes:
        return []
    first = closes[0]
    if first == 0:
        return [base] * len(closes)
    factor = base / first
    return [close * factor for close in closes]


def daily_simple_returns(closes: list[float]) -> list[float]:
    """Consecutive simple returns from aligned close prices."""
    returns: list[float] = []
    for index in range(1, len(closes)):
        previous = closes[index - 1]
        if previous == 0:
            continue
        returns.append((closes[index] - previous) / previous)
    return returns


def pearson_correlation(x: list[float], y: list[float]) -> float:
    """Pearson correlation coefficient for two equal-length series."""
    if len(x) != len(y) or len(x) < 2:
        return 0.0

    n = len(x)
    mean_x = sum(x) / n
    mean_y = sum(y) / n

    cov = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
    var_x = sum((value - mean_x) ** 2 for value in x)
    var_y = sum((value - mean_y) ** 2 for value in y)

    denominator = math.sqrt(var_x * var_y)
    if denominator == 0:
        return 0.0
    return cov / denominator


def compute_volatility(closes: list[float]) -> float:
    """Annualized volatility from daily log-return standard deviation × √252."""
    if len(closes) < 2:
        return 0.0

    log_returns = [
        math.log(closes[index] / closes[index - 1])
        for index in range(1, len(closes))
        if closes[index - 1] > 0 and closes[index] > 0
    ]
    if len(log_returns) < 2:
        return 0.0

    mean = sum(log_returns) / len(log_returns)
    variance = sum((value - mean) ** 2 for value in log_returns) / (len(log_returns) - 1)
    daily_std = math.sqrt(variance)
    return daily_std * math.sqrt(252)


def compute_max_drawdown(closes: list[float]) -> float:
    """Peak-to-trough drawdown on raw closes, expressed as a positive percentage."""
    if not closes:
        return 0.0

    peak = closes[0]
    max_drawdown = 0.0
    for close in closes:
        if close > peak:
            peak = close
        if peak > 0:
            drawdown = (peak - close) / peak * 100
            if drawdown > max_drawdown:
                max_drawdown = drawdown
    return max_drawdown


def build_correlation_matrix(
    symbols: list[str],
    closes_by_symbol: dict[str, list[float]],
) -> CompareCorrelation:
    """Build an N×N Pearson correlation matrix on aligned daily simple returns."""
    returns_by_symbol = {
        symbol: daily_simple_returns(closes_by_symbol[symbol]) for symbol in symbols
    }
    values: list[list[float]] = []

    for row_symbol in symbols:
        row: list[float] = []
        row_returns = returns_by_symbol[row_symbol]
        for col_symbol in symbols:
            if row_symbol == col_symbol:
                row.append(1.0)
            else:
                row.append(pearson_correlation(row_returns, returns_by_symbol[col_symbol]))
        values.append(row)

    return CompareCorrelation(symbols=symbols, values=values)


async def build_compare_response(
    provider: MarketDataProvider,
    symbols: list[str],
    days: int,
) -> CompareResponse:
    """Fetch OHLCV, align dates, and assemble the compare response."""
    histories: dict[str, PriceHistory] = {}
    for symbol in symbols:
        histories[symbol] = await provider.get_ohlcv(symbol, Interval.DAY_1, days)

    aligned_dates, points_by_symbol = align_price_histories(histories)
    if len(aligned_dates) < 2:
        raise InsufficientAlignedDataError()

    series: list[CompareSeries] = []
    closes_by_symbol: dict[str, list[float]] = {}
    metrics: list[CompareMetric] = []

    for symbol in symbols:
        raw_points = [points_by_symbol[symbol][day] for day in aligned_dates]
        closes = [point.close for point in raw_points]
        closes_by_symbol[symbol] = closes
        normalized = normalize_points(closes)

        compare_points = [
            ComparePoint(
                date=day,
                normalized_close=round(normalized[index], 4),
                open=raw_points[index].open,
                high=raw_points[index].high,
                low=raw_points[index].low,
                volume=raw_points[index].volume,
            )
            for index, day in enumerate(aligned_dates)
        ]
        series.append(
            CompareSeries(
                symbol=symbol,
                asset_id=histories[symbol].asset_id,
                points=compare_points,
            )
        )
        metrics.append(
            CompareMetric(
                symbol=symbol,
                volatility=round(compute_volatility(closes), 4),
                max_drawdown=round(compute_max_drawdown(closes), 4),
            )
        )

    meta: SourceMeta = histories[symbols[0]].meta

    return CompareResponse(
        symbols=symbols,
        days=days,
        series=series,
        correlation=build_correlation_matrix(symbols, closes_by_symbol),
        metrics=metrics,
        date_range=CompareDateRange(
            start=aligned_dates[0],
            end=aligned_dates[-1],
            aligned_points=len(aligned_dates),
        ),
        meta=meta,
    )
