import type {
  ApiErrorBody,
  Asset,
  HistoryResponse,
  PaginatedAssets,
  PaginatedHoldings,
  PaginatedTransactions,
  PaginatedWatchlist,
  Portfolio,
  Quote,
  TransactionCreate,
  TransactionResponse,
  WatchlistItem,
  WatchlistItemCreate,
} from "./types";

const BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000/api/v1";

export class ApiClientError extends Error {
  readonly status: number;
  readonly code: string;
  readonly details?: Record<string, unknown>;

  constructor(
    status: number,
    code: string,
    message: string,
    details?: Record<string, unknown>,
  ) {
    super(message);
    this.name = "ApiClientError";
    this.status = status;
    this.code = code;
    this.details = details;
  }
}

async function parseError(response: Response): Promise<ApiClientError> {
  let code = "UNKNOWN";
  let message = response.statusText || "Request failed";
  let details: Record<string, unknown> | undefined;

  try {
    const body = (await response.json()) as ApiErrorBody;
    if (body.error) {
      code = body.error.code;
      message = body.error.message;
      details = body.error.details;
    }
  } catch {
    /* non-JSON body */
  }

  return new ApiClientError(response.status, code, message, details);
}

async function request<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const url = `${BASE_URL.replace(/\/$/, "")}${path.startsWith("/") ? path : `/${path}`}`;
  const response = await fetch(url, {
    ...init,
    headers: {
      "Content-Type": "application/json",
      ...init?.headers,
    },
  });

  if (!response.ok) {
    throw await parseError(response);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  return (await response.json()) as T;
}

export function encodeAssetId(assetId: string): string {
  return encodeURIComponent(assetId);
}

export const api = {
  health: () =>
    request<{ status: string; version: string; database: string }>("/health"),

  searchAssets: (q: string, assetClass?: string, limit = 20) => {
    const params = new URLSearchParams({ q, limit: String(limit) });
    if (assetClass) params.set("class", assetClass);
    return request<PaginatedAssets>(`/assets/search?${params}`);
  },

  getAsset: (assetId: string) =>
    request<Asset>(`/assets/${encodeAssetId(assetId)}`),

  getQuote: (assetId: string) =>
    request<Quote>(`/quotes/${encodeAssetId(assetId)}`),

  getHistory: (assetId: string, interval = "1d") =>
    request<HistoryResponse>(
      `/history/${encodeAssetId(assetId)}?interval=${interval}`,
    ),

  getWatchlist: () => request<PaginatedWatchlist>("/watchlist"),

  addWatchlistItem: (body: WatchlistItemCreate) =>
    request<WatchlistItem>("/watchlist/items", {
      method: "POST",
      body: JSON.stringify(body),
    }),

  removeWatchlistItem: (assetId: string) =>
    request<void>(`/watchlist/items/${encodeAssetId(assetId)}`, {
      method: "DELETE",
    }),

  getPortfolio: () => request<Portfolio>("/portfolio"),

  getHoldings: () => request<PaginatedHoldings>("/portfolio/holdings"),

  getTransactions: (limit = 50) =>
    request<PaginatedTransactions>(
      `/portfolio/transactions?limit=${limit}`,
    ),

  createTransaction: (body: TransactionCreate) =>
    request<TransactionResponse>("/portfolio/transactions", {
      method: "POST",
      body: JSON.stringify(body),
    }),
};
