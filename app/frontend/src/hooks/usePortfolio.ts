import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { HistoryDays } from "@shared/types/portfolio";

import { api } from "../api/client";

const PORTFOLIO_HISTORY_KEY = "portfolio-history";

export function portfolioHistoryQueryKey(days: HistoryDays) {
  return [PORTFOLIO_HISTORY_KEY, days] as const;
}

export function usePortfolioHistory(days: HistoryDays = 30) {
  return useQuery({
    queryKey: portfolioHistoryQueryKey(days),
    queryFn: () => api.portfolio.history(days),
  });
}

export function useCreatePortfolioSnapshot() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: () => api.portfolio.createSnapshot(),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: [PORTFOLIO_HISTORY_KEY] });
    },
  });
}
