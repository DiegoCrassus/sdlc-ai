export type AssetClass = "stock" | "crypto" | "index" | "forex" | "commodity";

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

export interface WatchlistItem {
  symbol: string;
  name: string;
  asset_class: AssetClass;
  price: number;
  change_percent: number;
}

export interface Watchlist {
  items: WatchlistItem[];
}

export interface SearchHit {
  asset_id: string;
  symbol: string;
  name: string;
  asset_class: AssetClass;
}
