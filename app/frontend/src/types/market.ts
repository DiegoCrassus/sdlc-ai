import type { AssetClass as SharedAssetClass } from "@shared/types/allocation";
import type { SourceMeta } from "@shared/types/forecast";

export type AssetClass = SharedAssetClass;

export interface Quote {
  asset_id: string;
  symbol: string;
  name: string;
  asset_class: AssetClass;
  price: number;
  change: number;
  change_percent: number;
  volume_24h?: number | null;
  market_cap?: number | null;
  currency: string;
}

export interface IndexSnapshot {
  asset_id: string;
  name: string;
  value: number;
  change_percent: number;
}

export interface MarketMover {
  symbol: string;
  name: string;
  price: number;
  change_percent: number;
}

export interface MarketOverview {
  total_market_cap_usd: number;
  total_volume_24h_usd: number;
  btc_dominance_percent: number;
  fear_greed_index: number;
  active_assets: number;
  indices: IndexSnapshot[];
  top_gainers: MarketMover[];
  top_losers: MarketMover[];
}

export interface PricePoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface PriceHistory {
  asset_id: string;
  interval: string;
  points: PricePoint[];
}

export type {
  AssetProjection,
  DataSource,
  ProjectionPoint,
  ProjectionScenario,
  SourceMeta,
  TechnicalIndicators,
  TrendDirection,
} from "@shared/types/forecast";
export type {
  AllocationStatus,
  DriftBand,
  RebalanceSummary,
  WatchlistAllocationSummary,
  WatchlistItem,
  WatchlistResponse as Watchlist,
} from "@shared/types/allocation";

export interface SearchHit {
  asset_id: string;
  symbol: string;
  name: string;
  asset_class: AssetClass;
}

export interface ComparePoint {
  date: string;
  normalized_close: number;
  open: number;
  high: number;
  low: number;
  volume: number;
}

export interface CompareSeries {
  symbol: string;
  asset_id: string;
  points: ComparePoint[];
}

export interface CompareCorrelation {
  symbols: string[];
  values: number[][];
}

export interface CompareMetric {
  symbol: string;
  volatility: number;
  max_drawdown: number;
}

export interface CompareDateRange {
  start: string;
  end: string;
  aligned_points: number;
}

export interface CompareResponse {
  symbols: string[];
  days: number;
  series: CompareSeries[];
  correlation: CompareCorrelation;
  metrics: CompareMetric[];
  date_range: CompareDateRange;
  meta: SourceMeta;
}
