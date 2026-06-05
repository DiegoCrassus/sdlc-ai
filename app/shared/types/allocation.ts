/**
 * Watchlist allocation types — canonical contract for allocation targets.
 *
 * Endpoints:
 * - GET `/api/v1/watchlist` → 200 WatchlistResponse
 * - PATCH `/api/v1/watchlist/items/{symbol}/allocation` — body UpdateWatchlistAllocationRequest
 *   → 200 UpdateWatchlistAllocationResponse
 * - PATCH `/api/v1/watchlist/items/{symbol}/invested` — body UpdateWatchlistInvestedRequest
 *   → 200 UpdateWatchlistInvestedResponse
 *
 * `target_percent` is the public decimal percentage with up to two fractional digits.
 * Send `null` to clear a target while keeping the asset in the watchlist.
 *
 * `invested_amount` is the manual position in base currency with up to two fractional digits.
 * Send `null` to clear invested value while keeping the asset in the watchlist.
 */

export type AssetClass = "stock" | "crypto" | "index" | "forex" | "commodity";

export type AllocationStatus = "under_allocated" | "balanced" | "over_allocated";

export type DriftBand = "on_target" | "warning" | "off_target";

export interface WatchlistItem {
  symbol: string;
  name: string;
  asset_class: AssetClass;
  price: number;
  change_percent: number;
  target_percent?: number | null;
  invested_amount?: number | null;
  current_weight_percent?: number | null;
  drift_percent?: number | null;
  suggestion_amount?: number | null;
  drift_band?: DriftBand | null;
}

/** Overall allocation state computed canonically by the backend. */
export interface WatchlistAllocationSummary {
  target_percent_total: number;
  status: AllocationStatus;
}

/** Portfolio rebalance summary computed canonically by the backend. */
export interface RebalanceSummary {
  total_invested: number;
  suggestions_ready: boolean;
  max_drift_percent?: number | null;
}

/** GET /api/v1/watchlist — 200 response body. */
export interface WatchlistResponse {
  items: WatchlistItem[];
  allocation_summary: WatchlistAllocationSummary;
  rebalance_summary: RebalanceSummary;
}

/** PATCH /api/v1/watchlist/items/{symbol}/allocation request body. */
export interface UpdateWatchlistAllocationRequest {
  target_percent: number | null;
}

/** PATCH /api/v1/watchlist/items/{symbol}/allocation — 200 response body. */
export interface UpdateWatchlistAllocationResponse {
  item: WatchlistItem;
  allocation_summary: WatchlistAllocationSummary;
  rebalance_summary: RebalanceSummary;
}

/** PATCH /api/v1/watchlist/items/{symbol}/invested request body. */
export interface UpdateWatchlistInvestedRequest {
  invested_amount: number | null;
}

/** PATCH /api/v1/watchlist/items/{symbol}/invested — 200 response body. */
export interface UpdateWatchlistInvestedResponse {
  item: WatchlistItem;
  allocation_summary: WatchlistAllocationSummary;
  rebalance_summary: RebalanceSummary;
}

export const WATCHLIST_API_PATHS = {
  list: "/api/v1/watchlist",
  itemAllocation: (symbol: string) => `/api/v1/watchlist/items/${encodeURIComponent(symbol)}/allocation`,
  itemInvested: (symbol: string) => `/api/v1/watchlist/items/${encodeURIComponent(symbol)}/invested`,
} as const;
