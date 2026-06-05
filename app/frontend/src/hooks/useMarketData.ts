import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { AssetProjection } from "@shared/types/forecast";

import { api } from "../api/client";

const REFETCH_MS = 30_000;
const WATCHLIST_QUERY_KEY = ["watchlist"] as const;

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
    queryKey: WATCHLIST_QUERY_KEY,
    queryFn: api.watchlist,
    refetchInterval: REFETCH_MS,
  });
}

export function useUpdateWatchlistAllocation() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      symbol,
      target_percent,
    }: {
      symbol: string;
      target_percent: number | null;
    }) => api.updateWatchlistAllocation(symbol, { target_percent }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: WATCHLIST_QUERY_KEY });
    },
  });
}

export function useUpdateWatchlistInvested() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: ({
      symbol,
      invested_amount,
    }: {
      symbol: string;
      invested_amount: number | null;
    }) => api.updateWatchlistInvested(symbol, { invested_amount }),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: WATCHLIST_QUERY_KEY });
    },
  });
}

export function useAssetSearch(query: string) {
  return useQuery({
    queryKey: ["search", query],
    queryFn: () => api.search(query),
    enabled: query.trim().length >= 2,
  });
}
