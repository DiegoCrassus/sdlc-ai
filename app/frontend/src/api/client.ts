import type {
  AlertListResponse,
  CreateAlertRequest,
  PriceAlert,
} from "@shared/types/alerts";
import type {
  UpdateWatchlistAllocationRequest,
  UpdateWatchlistAllocationResponse,
  UpdateWatchlistInvestedRequest,
  UpdateWatchlistInvestedResponse,
} from "@shared/types/allocation";
import type {
  AuthMeResponse,
  IdentifyRequest,
  IdentifyResponse,
  User,
} from "@shared/types/auth";
import type {
  CreateSnapshotResponse,
  HistoryDays,
  PortfolioHistoryResponse,
} from "@shared/types/portfolio";
import type {
  AssetProjection,
  MarketOverview,
  PriceHistory,
  Quote,
  SearchHit,
  Watchlist,
} from "../types/market";

const API_BASE = import.meta.env.VITE_API_BASE ?? "/api/v1";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    credentials: "include",
    ...init,
  });
  if (!response.ok) {
    throw new Error(`API ${response.status}: ${response.statusText}`);
  }
  if (response.status === 204) {
    return undefined as T;
  }
  return response.json() as Promise<T>;
}

export const api = {
  auth: {
    me: async (): Promise<User | null> => {
      const response = await fetch(`${API_BASE}/auth/me`, { credentials: "include" });
      if (response.status === 401) {
        return null;
      }
      if (!response.ok) {
        throw new Error(`API ${response.status}: ${response.statusText}`);
      }
      const data = (await response.json()) as AuthMeResponse;
      return data.user;
    },
    identify: (email: string) =>
      request<IdentifyResponse>("/auth/identify", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email } satisfies IdentifyRequest),
      }),
    logout: () => request<void>("/auth/logout", { method: "POST" }),
  },
  health: () => request<{ status: string; provider: string }>("/health"),
  overview: () => request<MarketOverview>("/markets/overview"),
  quotes: (symbols: string[]) =>
    request<Quote[]>(`/markets/quotes?symbols=${encodeURIComponent(symbols.join(","))}`),
  ohlcv: (symbol: string, interval = "1d", limit = 90) =>
    request<PriceHistory>(
      `/markets/${encodeURIComponent(symbol)}/ohlcv?interval=${interval}&limit=${limit}`,
    ),
  search: (query: string) =>
    request<SearchHit[]>(`/markets/search?q=${encodeURIComponent(query)}`),
  projection: (symbol: string, horizonDays = 7) =>
    request<AssetProjection>(
      `/projections/${encodeURIComponent(symbol)}?horizon_days=${horizonDays}`,
    ),
  watchlist: () => request<Watchlist>("/watchlist"),
  updateWatchlistAllocation: (
    symbol: string,
    payload: UpdateWatchlistAllocationRequest,
  ) =>
    request<UpdateWatchlistAllocationResponse>(
      `/watchlist/items/${encodeURIComponent(symbol)}/allocation`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
    ),
  updateWatchlistInvested: (
    symbol: string,
    payload: UpdateWatchlistInvestedRequest,
  ) =>
    request<UpdateWatchlistInvestedResponse>(
      `/watchlist/items/${encodeURIComponent(symbol)}/invested`,
      {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      },
    ),
  portfolio: {
    history: (days: HistoryDays = 30) =>
      request<PortfolioHistoryResponse>(`/portfolio/history?days=${days}`),
    createSnapshot: () =>
      request<CreateSnapshotResponse>("/portfolio/snapshots", { method: "POST" }),
  },
  alerts: {
    list: (symbol?: string) => {
      const query = symbol ? `?symbol=${encodeURIComponent(symbol)}` : "";
      return request<AlertListResponse>(`/alerts${query}`);
    },
    create: (payload: CreateAlertRequest) =>
      request<PriceAlert>("/alerts", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
      }),
    delete: (alertId: string) =>
      request<void>(`/alerts/${encodeURIComponent(alertId)}`, { method: "DELETE" }),
  },
};
