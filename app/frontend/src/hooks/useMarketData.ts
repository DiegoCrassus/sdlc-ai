import { useQuery } from "@tanstack/react-query";

import type { AssetProjection } from "@shared/types/forecast";

import { api } from "../api/client";

const REFETCH_MS = 30_000;

export function useMarketOverview() {
  return useQuery({
    queryKey: ["overview"],
    queryFn: api.overview,
    refetchInterval: REFETCH_MS,
  });
}

export function useTickerQuotes(symbols: string[]) {
  return useQuery({
    queryKey: ["quotes", symbols.join(",")],
    queryFn: () => api.quotes(symbols),
    refetchInterval: REFETCH_MS,
  });
}

export function useOhlcv(symbol: string) {
  return useQuery({
    queryKey: ["ohlcv", symbol],
    queryFn: () => api.ohlcv(symbol),
    refetchInterval: REFETCH_MS,
  });
}

export function useProjection(symbol: string, horizonDays = 7) {
  return useQuery<AssetProjection>({
    queryKey: ["projection", symbol, horizonDays],
    queryFn: () => api.projection(symbol, horizonDays),
    refetchInterval: REFETCH_MS,
  });
}

export function useWatchlist() {
  return useQuery({
    queryKey: ["watchlist"],
    queryFn: api.watchlist,
    refetchInterval: REFETCH_MS,
  });
}

export function useAssetSearch(query: string) {
  return useQuery({
    queryKey: ["search", query],
    queryFn: () => api.search(query),
    enabled: query.trim().length >= 2,
  });
}
