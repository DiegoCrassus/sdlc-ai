/**
 * Price alert types — canonical contract for watchlist-scoped alerts (ADR-011).
 *
 * Endpoints (prefix `/api/v1`):
 * - POST `/alerts` — body CreateAlertRequest → 201 PriceAlert
 * - GET `/alerts` — optional `?symbol=` → 200 AlertListResponse (evaluates pending alerts first)
 * - DELETE `/alerts/{alert_id}` → 204 No Content; 404 AlertError if missing
 *
 * Trigger semantics: `above` → price >= target_price; `below` → price <= target_price (inclusive).
 * `triggered_at` is a one-shot latch until DELETE.
 */

export type AlertDirection = "above" | "below";

export interface PriceAlert {
  id: string;
  symbol: string;
  direction: AlertDirection;
  target_price: number;
  triggered_at: string | null;
  created_at: string;
}

/** POST /api/v1/alerts request body. Symbol must be on the watchlist (server-validated). */
export interface CreateAlertRequest {
  symbol: string;
  direction: AlertDirection;
  target_price: number;
}

/** GET /api/v1/alerts — 200 response body. */
export interface AlertListResponse {
  items: PriceAlert[];
}

export type AlertErrorCode = "VALIDATION_ERROR" | "NOT_FOUND";

export interface ApiErrorBody {
  code: AlertErrorCode;
  message: string;
  details?: Record<string, unknown>;
}

/** 400 / 404 alert error envelope (`{ error: { code, message, details? } }`). */
export interface AlertError {
  error: ApiErrorBody;
}

export const ALERTS_API_PATHS = {
  list: "/api/v1/alerts",
  detail: (alertId: string) => `/api/v1/alerts/${alertId}`,
} as const;
