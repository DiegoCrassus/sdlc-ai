/** Forecast projection types — mirror of backend Pydantic models (ADR-009). */

export type TrendDirection = "bullish" | "bearish" | "neutral";

export type DataSource = "mock" | "live" | "fallback";

export interface TechnicalIndicators {
  rsi_14: number;
  macd: number;
  macd_signal: number;
  sma_20: number;
  sma_50: number;
  bollinger_upper: number;
  bollinger_lower: number;
}

export interface SourceMeta {
  source: DataSource;
  provider: string;
  fetched_at: string;
  latency_ms?: number | null;
}

export interface ProjectionPoint {
  timestamp: string;
  price: number;
  lower_bound: number;
  upper_bound: number;
}

export interface ProjectionScenario {
  name: string;
  direction: TrendDirection;
  confidence: number;
  points: ProjectionPoint[];
}

export interface AssetProjection {
  asset_id: string;
  horizon_days: number;
  current_price: number;
  indicators: TechnicalIndicators;
  scenarios: ProjectionScenario[];
  disclaimer: string;
  meta: SourceMeta;
}
