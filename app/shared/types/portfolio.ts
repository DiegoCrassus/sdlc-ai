/**
 * Portfolio snapshot types — canonical contract for daily value history (INVES-117).
 *
 * Endpoints (prefix `/api/v1`):
 * - POST `/portfolio/snapshots` → 200 CreateSnapshotResponse (upsert today UTC)
 * - GET `/portfolio/history?days=30|90|365` → 200 PortfolioHistoryResponse (default 30)
 *
 * `total_value` is the public decimal amount with up to two fractional digits.
 * Return percentages are computed at read time; first point in a series is always 0%.
 */

export type HistoryDays = 30 | 90 | 365;

export interface PortfolioSnapshot {
  snapshot_date: string;
  total_value: number;
  created_at: string;
  updated_at: string;
}

export interface PortfolioHistoryPoint {
  snapshot_date: string;
  total_value: number;
  daily_change_pct: number;
  cumulative_return_pct: number;
}

/** Optional headline PnL cards for dashboard UI. */
export interface PortfolioHistorySummary {
  pnl_today?: number;
  pnl_7d?: number;
  pnl_30d?: number;
  pnl_ytd?: number;
}

/** GET /api/v1/portfolio/history — 200 response body. */
export interface PortfolioHistoryResponse {
  days: HistoryDays;
  points: PortfolioHistoryPoint[];
  summary?: PortfolioHistorySummary;
}

/** POST /api/v1/portfolio/snapshots — 200 response body. */
export interface CreateSnapshotResponse {
  snapshot: PortfolioSnapshot;
  /** True when a new row was inserted; false when today's snapshot was upserted. */
  created: boolean;
}

export const PORTFOLIO_API_PATHS = {
  snapshots: "/api/v1/portfolio/snapshots",
  history: (days: HistoryDays = 30) =>
    `/api/v1/portfolio/history?days=${days}`,
} as const;
