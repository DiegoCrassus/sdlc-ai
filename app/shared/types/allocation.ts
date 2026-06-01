/**
 * Watchlist allocation types — canonical contract for allocation targets.
 *
 * Endpoints:
 * - GET `/api/v1/watchlist` → 200 WatchlistResponse
 * - PATCH `/api/v1/watchlist/items/{symbol}/allocation` — body UpdateWatchlistAllocationRequest
 *   → 200 UpdateWatchlistAllocationResponse
 *
 * `target_percent` is the public decimal percentage with up to two fractional digits.
 * Send `null` to clear a target while keeping the asset in the watchlist.
 */

export type AssetClass = "stock" | "crypto" | "index" | "forex" | "commodity";

export type AllocationStatus = "under_allocated" | "balanced" | "over_allocated";

export interface WatchlistItem {
  symbol: string;
  name: string;
  asset_class: AssetClass;
  price: number;
  change_percent: number;
  target_percent?: number | null;
}

/** Overall allocation state computed canonically by the backend. */
export interface WatchlistAllocationSummary {
  target_percent_total: number;
  status: AllocationStatus;
}

/** GET /api/v1/watchlist — 200 response body. */
export interface WatchlistResponse {
  items: WatchlistItem[];
  allocation_summary: WatchlistAllocationSummary;
}

/** PATCH /api/v1/watchlist/items/{symbol}/allocation request body. */
export interface UpdateWatchlistAllocationRequest {
  target_percent: number | null;
}

/** PATCH /api/v1/watchlist/items/{symbol}/allocation — 200 response body. */
export interface UpdateWatchlistAllocationResponse {
  item: WatchlistItem;
  allocation_summary: WatchlistAllocationSummary;
}

export const WATCHLIST_API_PATHS = {
  list: "/api/v1/watchlist",
  itemAllocation: (symbol: string) => `/api/v1/watchlist/items/${symbol}/allocation`,
} as const;
