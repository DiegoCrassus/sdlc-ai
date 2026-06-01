import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import type { CreateAlertRequest } from "@shared/types/alerts";

import { api } from "../api/client";

const REFETCH_MS = 30_000;

export function useAlerts(symbol?: string) {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: ["alerts", symbol ?? "all"],
    queryFn: () => api.alerts.list(symbol),
    refetchInterval: REFETCH_MS,
  });

  const createMutation = useMutation({
    mutationFn: (payload: CreateAlertRequest) => api.alerts.create(payload),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  const deleteMutation = useMutation({
    mutationFn: (alertId: string) => api.alerts.delete(alertId),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["alerts"] });
    },
  });

  return {
    alerts: query.data?.items ?? [],
    isLoading: query.isLoading,
    isError: query.isError,
    error: query.error,
    refetch: query.refetch,
    createAlert: createMutation.mutateAsync,
    isCreating: createMutation.isPending,
    createError: createMutation.error,
    deleteAlert: deleteMutation.mutateAsync,
    isDeleting: deleteMutation.isPending,
    deleteError: deleteMutation.error,
  };
}
