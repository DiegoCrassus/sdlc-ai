export type DataSource = "live" | "fallback";
export type AssetClass = "stock" | "crypto";
export type TransactionType = "buy" | "sell";

export interface ApiErrorBody {
  error: {
    code: string;
    message: string;
    details?: Record<string, unknown>;
  };
}

export interface Asset {
  id: string;
  class: AssetClass;
  symbol: string;
  name: string;
  currency: string;
  exchange?: string | null;
  source?: DataSource | null;
}

export interface Quote {
  asset_id: string;
  price: number;
  change?: number | null;
  change_percent?: number | null;
  currency: string;
  timestamp: string;
  source: DataSource;
}

export interface PricePoint {
  timestamp: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume?: number | null;
}

export interface PaginatedAssets {
  items: Asset[];
  total: number;
  limit: number;
  offset: number;
}

export interface HistoryResponse {
  asset_id: string;
  interval: string;
  source: DataSource;
  points: PricePoint[];
}

export interface WatchlistItem {
  asset_id: string;
  asset?: Asset | null;
  quote?: Quote | null;
  notes?: string | null;
  sort_order: number;
  added_at: string;
}

export interface PaginatedWatchlist {
  items: WatchlistItem[];
  total: number;
  limit: number;
  offset: number;
}

export interface Portfolio {
  id: string;
  name: string;
  base_currency: string;
  cash_balance: number;
  total_value: number;
  total_cost_basis: number;
  unrealized_pnl: number;
  updated_at: string;
}

export interface Holding {
  asset_id: string;
  asset?: Asset | null;
  quantity: number;
  avg_cost: number;
  market_price: number;
  market_value: number;
  cost_basis: number;
  unrealized_pnl: number;
  source: DataSource;
}

export interface Transaction {
  id: string;
  type: TransactionType;
  asset_id: string;
  quantity: number;
  price: number;
  total: number;
  source: DataSource;
  executed_at: string;
  note?: string | null;
}

export interface PaginatedHoldings {
  items: Holding[];
  total: number;
  limit: number;
  offset: number;
}

export interface PaginatedTransactions {
  items: Transaction[];
  total: number;
  limit: number;
  offset: number;
}

export interface TransactionResponse {
  transaction: Transaction;
  portfolio: Portfolio;
  holding: Holding | null;
}

export interface WatchlistItemCreate {
  asset_id: string;
  notes?: string | null;
  sort_order?: number;
}

export interface TransactionCreate {
  type: TransactionType;
  asset_id: string;
  quantity: number;
  note?: string | null;
}
