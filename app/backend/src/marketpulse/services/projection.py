"""Simple linear trend projection from recent OHLCV data."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from marketpulse.domain.enums import TrendDirection
from marketpulse.domain.models import (
    AssetProjection,
    PricePoint,
    ProjectionPoint,
    ProjectionScenario,
    SourceMeta,
    TechnicalIndicators,
)
from marketpulse.domain.enums import DataSource


def _compute_indicators(points: list[PricePoint]) -> TechnicalIndicators:
    closes = [point.close for point in points]
    last = closes[-1]
    sma_20 = sum(closes[-20:]) / min(len(closes), 20)
    sma_50 = sum(closes[-50:]) / min(len(closes), 50)
    gains = [max(closes[i] - closes[i - 1], 0.0) for i in range(1, len(closes))]
    losses = [max(closes[i - 1] - closes[i], 0.0) for i in range(1, len(closes))]
    avg_gain = sum(gains[-14:]) / max(len(gains[-14:]), 1)
    avg_loss = sum(losses[-14:]) / max(len(losses[-14:]), 1)
    rs = avg_gain / avg_loss if avg_loss else 100.0
    rsi = 100.0 - (100.0 / (1.0 + rs))
    ema_12 = sum(closes[-12:]) / min(len(closes), 12)
    ema_26 = sum(closes[-26:]) / min(len(closes), 26)
    macd = ema_12 - ema_26
    return TechnicalIndicators(
        rsi_14=round(rsi, 2),
        macd=round(macd, 4),
        macd_signal=round(macd * 0.9, 4),
        sma_20=round(sma_20, 2),
        sma_50=round(sma_50, 2),
        bollinger_upper=round(last * 1.02, 2),
        bollinger_lower=round(last * 0.98, 2),
    )


def build_projection(
    *,
    asset_id: str,
    symbol: str,
    current_price: float,
    points: list[PricePoint],
    horizon_days: int,
    provider: str,
) -> AssetProjection:
    """Build a linear trend projection with confidence bands."""
    window = points[-min(len(points), 30) :]
    if len(window) < 2:
        slope = 0.0
    else:
        first_close = window[0].close
        last_close = window[-1].close
        slope = (last_close - first_close) / len(window)

    volatility = 0.0
    if len(window) > 1:
        returns = [
            abs(window[i].close - window[i - 1].close) / window[i - 1].close
            for i in range(1, len(window))
        ]
        volatility = sum(returns) / len(returns)

    direction = (
        TrendDirection.BULLISH
        if slope > 0
        else TrendDirection.BEARISH
        if slope < 0
        else TrendDirection.NEUTRAL
    )
    confidence = min(0.95, max(0.35, 0.55 + abs(slope) / max(current_price, 1.0) * 10))

    now = datetime.now(tz=UTC)
    projection_points: list[ProjectionPoint] = []
    for day in range(1, horizon_days + 1):
        projected = current_price + slope * day
        band = projected * volatility * 2
        projection_points.append(
            ProjectionPoint(
                timestamp=now + timedelta(days=day),
                price=round(projected, 4),
                lower_bound=round(projected - band, 4),
                upper_bound=round(projected + band, 4),
            )
        )

    indicators = _compute_indicators(points)
    return AssetProjection(
        asset_id=asset_id,
        horizon_days=horizon_days,
        current_price=current_price,
        indicators=indicators,
        scenarios=[
            ProjectionScenario(
                name="linear_trend",
                direction=direction,
                confidence=round(confidence, 2),
                points=projection_points,
            )
        ],
        disclaimer=(
            "Projections are illustrative only and based on a simple linear trend "
            "from recent price history. Not financial advice."
        ),
        meta=SourceMeta(
            source=DataSource.MOCK,
            provider=provider,
            fetched_at=now,
            latency_ms=1.0,
        ),
    )
