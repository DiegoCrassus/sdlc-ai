import { useEffect, useMemo, useState } from "react";

import type { PriceAlert } from "@shared/types/alerts";
import type { DriftBand } from "@shared/types/allocation";

import { AlertModal } from "./AlertModal";
import { RebalanceSummaryPanel } from "./RebalanceSummaryPanel";
import type {
  RebalanceSummary,
  WatchlistAllocationSummary,
  WatchlistItem,
} from "../types/market";

interface Props {
  items: WatchlistItem[];
  allocationSummary?: WatchlistAllocationSummary;
  rebalanceSummary?: RebalanceSummary;
  selectedSymbol: string;
  onSelect: (symbol: string) => void;
  isLoading: boolean;
  onUpdateAllocation: (payload: {
    symbol: string;
    target_percent: number | null;
  }) => Promise<unknown>;
  isUpdatingAllocation: boolean;
  updateAllocationError: Error | null;
  onUpdateInvested: (payload: {
    symbol: string;
    invested_amount: number | null;
  }) => Promise<unknown>;
  isUpdatingInvested: boolean;
  updateInvestedError: Error | null;
  alerts: PriceAlert[];
  onCreateAlert: (payload: {
    symbol: string;
    direction: "above" | "below";
    target_price: number;
  }) => Promise<void>;
  isCreatingAlert: boolean;
  createAlertError: Error | null;
}

export function WatchlistTable({
  items,
  allocationSummary,
  rebalanceSummary,
  selectedSymbol,
  onSelect,
  isLoading,
  onUpdateAllocation,
  isUpdatingAllocation,
  updateAllocationError,
  onUpdateInvested,
  isUpdatingInvested,
  updateInvestedError,
  alerts,
  onCreateAlert,
  isCreatingAlert,
  createAlertError,
}: Props) {
  const [modalSymbol, setModalSymbol] = useState<string | null>(null);
  const [draftTargets, setDraftTargets] = useState<Record<string, string>>({});
  const [draftInvested, setDraftInvested] = useState<Record<string, string>>({});
  const [savingTargetSymbol, setSavingTargetSymbol] = useState<string | null>(null);
  const [savingInvestedSymbol, setSavingInvestedSymbol] = useState<string | null>(null);
  const [allocationError, setAllocationError] = useState<string | null>(null);
  const [investedError, setInvestedError] = useState<string | null>(null);

  useEffect(() => {
    const nextTargets: Record<string, string> = {};
    const nextInvested: Record<string, string> = {};
    for (const item of items) {
      nextTargets[item.symbol] =
        item.target_percent === null || item.target_percent === undefined
          ? ""
          : formatDecimalInput(item.target_percent);
      nextInvested[item.symbol] =
        item.invested_amount === null || item.invested_amount === undefined
          ? ""
          : formatDecimalInput(item.invested_amount);
    }
    setDraftTargets(nextTargets);
    setDraftInvested(nextInvested);
  }, [items]);

  const triggeredSymbols = useMemo(() => {
    const set = new Set<string>();
    for (const alert of alerts) {
      if (alert.triggered_at !== null) {
        set.add(alert.symbol);
      }
    }
    return set;
  }, [alerts]);

  const modalItem = items.find((item) => item.symbol === modalSymbol);
  const summary = allocationSummary ?? buildFallbackAllocationSummary(items);
  const summaryCopy = getAllocationSummaryCopy(summary);
  const displayedAllocationError =
    allocationError ?? updateAllocationError?.message ?? null;
  const displayedInvestedError = investedError ?? updateInvestedError?.message ?? null;
  const isMutating = isUpdatingAllocation || isUpdatingInvested;

  async function saveAllocation(item: WatchlistItem) {
    const rawTarget = draftTargets[item.symbol]?.trim() ?? "";
    const target_percent = parseTargetPercent(rawTarget);

    if (target_percent === "invalid") {
      setAllocationError("Enter a target between 0.01% and 100%, or clear it.");
      return;
    }

    setAllocationError(null);
    setSavingTargetSymbol(item.symbol);
    try {
      await onUpdateAllocation({ symbol: item.symbol, target_percent });
    } catch (error) {
      setAllocationError(error instanceof Error ? error.message : "Unable to update allocation.");
    } finally {
      setSavingTargetSymbol(null);
    }
  }

  async function clearAllocation(item: WatchlistItem) {
    setDraftTargets((current) => ({ ...current, [item.symbol]: "" }));
    setAllocationError(null);
    setSavingTargetSymbol(item.symbol);
    try {
      await onUpdateAllocation({ symbol: item.symbol, target_percent: null });
    } catch (error) {
      setAllocationError(error instanceof Error ? error.message : "Unable to clear allocation.");
    } finally {
      setSavingTargetSymbol(null);
    }
  }

  async function saveInvested(item: WatchlistItem) {
    const rawInvested = draftInvested[item.symbol]?.trim() ?? "";
    const invested_amount = parseInvestedAmount(rawInvested);

    if (invested_amount === "invalid") {
      setInvestedError("Enter a non-negative amount with up to 2 decimals, or clear it.");
      return;
    }

    setInvestedError(null);
    setSavingInvestedSymbol(item.symbol);
    try {
      await onUpdateInvested({ symbol: item.symbol, invested_amount });
    } catch (error) {
      setInvestedError(error instanceof Error ? error.message : "Unable to update invested amount.");
    } finally {
      setSavingInvestedSymbol(null);
    }
  }

  async function clearInvested(item: WatchlistItem) {
    setDraftInvested((current) => ({ ...current, [item.symbol]: "" }));
    setInvestedError(null);
    setSavingInvestedSymbol(item.symbol);
    try {
      await onUpdateInvested({ symbol: item.symbol, invested_amount: null });
    } catch (error) {
      setInvestedError(error instanceof Error ? error.message : "Unable to clear invested amount.");
    } finally {
      setSavingInvestedSymbol(null);
    }
  }

  if (isLoading) {
    return <div className="h-64 animate-pulse rounded-xl bg-surface-card" />;
  }

  return (
    <>
      <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
        <div className="mb-4 flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <h2 className="text-lg font-semibold text-white">Watchlist</h2>
            <p className="mt-1 text-sm text-slate-400">
              Set target allocations and invested amounts to track drift and rebalance suggestions.
            </p>
          </div>
          <div className="flex flex-col gap-3 sm:flex-row">
            <div
              className={`rounded-lg border px-4 py-3 text-sm ${summaryCopy.className}`}
              role={summary.status === "over_allocated" ? "alert" : "status"}
            >
              <p className="font-medium">
                Total allocated: {formatPercent(summary.target_percent_total)}
              </p>
              <p className="mt-1">{summaryCopy.message}</p>
            </div>
            <RebalanceSummaryPanel
              rebalanceSummary={rebalanceSummary}
              allocationStatus={summary.status}
            />
          </div>
        </div>
        {displayedAllocationError && (
          <div className="mb-3 rounded-lg border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-sm text-rose-300">
            {displayedAllocationError}
          </div>
        )}
        {displayedInvestedError && (
          <div className="mb-3 rounded-lg border border-rose-500/40 bg-rose-500/10 px-3 py-2 text-sm text-rose-300">
            {displayedInvestedError}
          </div>
        )}
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="pb-2 pr-4">Symbol</th>
                <th className="pb-2 pr-4">Name</th>
                <th className="pb-2 pr-4">Price</th>
                <th className="pb-2 pr-4">Change</th>
                <th className="pb-2 pr-4">Target</th>
                <th className="pb-2 pr-4">Invested</th>
                <th className="pb-2 pr-4">Weight</th>
                <th className="pb-2 pr-4">Drift</th>
                <th className="pb-2 pr-4">Suggestion</th>
                <th className="pb-2 pr-4">Status</th>
                <th className="pb-2">Alert</th>
              </tr>
            </thead>
            <tbody>
              {items.map((item) => {
                const active = item.symbol === selectedSymbol;
                const positive = item.change_percent >= 0;
                const hasTriggered = triggeredSymbols.has(item.symbol);
                const isSavingTarget = savingTargetSymbol === item.symbol;
                const isSavingInvested = savingInvestedSymbol === item.symbol;
                return (
                  <tr
                    key={item.symbol}
                    className={`border-t border-slate-700/40 ${active ? "bg-slate-800/60" : "hover:bg-slate-800/30"}`}
                  >
                    <td
                      className="cursor-pointer py-2 pr-4 font-medium text-white"
                      onClick={() => onSelect(item.symbol)}
                    >
                      <span className="inline-flex items-center gap-2">
                        {item.symbol}
                        {hasTriggered && (
                          <span className="rounded-full bg-amber-500/20 px-2 py-0.5 text-xs font-medium text-amber-400">
                            Alert triggered
                          </span>
                        )}
                      </span>
                    </td>
                    <td
                      className="cursor-pointer py-2 pr-4 text-slate-300"
                      onClick={() => onSelect(item.symbol)}
                    >
                      {item.name}
                    </td>
                    <td
                      className="cursor-pointer py-2 pr-4 text-slate-200"
                      onClick={() => onSelect(item.symbol)}
                    >
                      ${item.price.toLocaleString()}
                    </td>
                    <td
                      className={`cursor-pointer py-2 pr-4 ${positive ? "text-emerald-400" : "text-rose-400"}`}
                      onClick={() => onSelect(item.symbol)}
                    >
                      {positive ? "+" : ""}
                      {item.change_percent.toFixed(2)}%
                    </td>
                    <td className="py-2 pr-4">
                      <form
                        className="flex min-w-56 flex-wrap items-center gap-2"
                        onSubmit={(event) => {
                          event.preventDefault();
                          void saveAllocation(item);
                        }}
                      >
                        <div className="relative">
                          <input
                            aria-label={`Target allocation for ${item.symbol}`}
                            type="number"
                            min="0.01"
                            max="100"
                            step="0.01"
                            inputMode="decimal"
                            placeholder="0.00"
                            value={draftTargets[item.symbol] ?? ""}
                            disabled={isMutating}
                            onChange={(event) => {
                              setDraftTargets((current) => ({
                                ...current,
                                [item.symbol]: event.target.value,
                              }));
                            }}
                            className="w-24 rounded-lg border border-slate-600 bg-slate-950/60 px-3 py-1 pr-7 text-sm text-slate-100 outline-none transition-colors placeholder:text-slate-600 focus:border-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
                          />
                          <span className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-xs text-slate-500">
                            %
                          </span>
                        </div>
                        <button
                          type="submit"
                          disabled={isMutating}
                          className="rounded-lg border border-emerald-500/40 px-3 py-1 text-xs font-medium text-emerald-400 transition-colors hover:bg-emerald-500/10 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          {isSavingTarget ? "Saving..." : "Save"}
                        </button>
                        <button
                          type="button"
                          disabled={isMutating}
                          onClick={() => {
                            void clearAllocation(item);
                          }}
                          className="rounded-lg border border-slate-600 px-3 py-1 text-xs text-slate-300 transition-colors hover:border-rose-500/50 hover:text-rose-300 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          Clear
                        </button>
                      </form>
                    </td>
                    <td className="py-2 pr-4">
                      <form
                        className="flex min-w-56 flex-wrap items-center gap-2"
                        onSubmit={(event) => {
                          event.preventDefault();
                          void saveInvested(item);
                        }}
                      >
                        <div className="relative">
                          <input
                            aria-label={`Invested amount for ${item.symbol}`}
                            type="number"
                            min="0"
                            step="0.01"
                            inputMode="decimal"
                            placeholder="0.00"
                            value={draftInvested[item.symbol] ?? ""}
                            disabled={isMutating}
                            onChange={(event) => {
                              setDraftInvested((current) => ({
                                ...current,
                                [item.symbol]: event.target.value,
                              }));
                            }}
                            className="w-28 rounded-lg border border-slate-600 bg-slate-950/60 px-3 py-1 pr-7 text-sm text-slate-100 outline-none transition-colors placeholder:text-slate-600 focus:border-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
                          />
                          <span className="pointer-events-none absolute right-2 top-1/2 -translate-y-1/2 text-xs text-slate-500">
                            $
                          </span>
                        </div>
                        <button
                          type="submit"
                          disabled={isMutating}
                          className="rounded-lg border border-emerald-500/40 px-3 py-1 text-xs font-medium text-emerald-400 transition-colors hover:bg-emerald-500/10 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          {isSavingInvested ? "Saving..." : "Save"}
                        </button>
                        <button
                          type="button"
                          disabled={isMutating}
                          onClick={() => {
                            void clearInvested(item);
                          }}
                          className="rounded-lg border border-slate-600 px-3 py-1 text-xs text-slate-300 transition-colors hover:border-rose-500/50 hover:text-rose-300 disabled:cursor-not-allowed disabled:opacity-60"
                        >
                          Clear
                        </button>
                      </form>
                    </td>
                    <td className="py-2 pr-4 text-slate-300">
                      {formatNullablePercent(item.current_weight_percent)}
                    </td>
                    <td className="py-2 pr-4 text-slate-300">
                      {formatNullableSignedPercent(item.drift_percent)}
                    </td>
                    <td className="py-2 pr-4">
                      {formatSuggestion(item.suggestion_amount)}
                    </td>
                    <td className="py-2 pr-4">
                      <DriftBandBadge band={item.drift_band} />
                    </td>
                    <td className="py-2">
                      <button
                        type="button"
                        onClick={() => setModalSymbol(item.symbol)}
                        className="rounded-lg border border-slate-600 px-3 py-1 text-xs text-slate-300 hover:border-emerald-500/50 hover:text-emerald-400"
                      >
                        Set alert
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </section>

      {modalItem && (
        <AlertModal
          symbol={modalItem.symbol}
          currentPrice={modalItem.price}
          isOpen={modalSymbol !== null}
          onClose={() => setModalSymbol(null)}
          onSubmit={async (payload) => {
            await onCreateAlert({ symbol: modalItem.symbol, ...payload });
          }}
          isSubmitting={isCreatingAlert}
          error={createAlertError}
        />
      )}
    </>
  );
}

function DriftBandBadge({ band }: { band?: DriftBand | null }) {
  if (band == null) {
    return <span className="text-slate-500">—</span>;
  }

  const styles: Record<DriftBand, { className: string; label: string }> = {
    on_target: {
      className: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
      label: "On target",
    },
    warning: {
      className: "border-amber-500/40 bg-amber-500/10 text-amber-300",
      label: "Warning",
    },
    off_target: {
      className: "border-rose-500/40 bg-rose-500/10 text-rose-300",
      label: "Off target",
    },
  };

  const style = styles[band];
  return (
    <span
      className={`inline-flex rounded-full border px-2 py-0.5 text-xs font-medium ${style.className}`}
    >
      {style.label}
    </span>
  );
}

function parseTargetPercent(rawTarget: string): number | null | "invalid" {
  if (rawTarget === "") {
    return null;
  }

  const target = Number(rawTarget);
  if (!Number.isFinite(target) || target <= 0 || target > 100) {
    return "invalid";
  }

  if (!hasAtMostTwoDecimals(rawTarget)) {
    return "invalid";
  }

  return Math.round(target * 100) / 100;
}

function parseInvestedAmount(rawInvested: string): number | null | "invalid" {
  if (rawInvested === "") {
    return null;
  }

  const amount = Number(rawInvested);
  if (!Number.isFinite(amount) || amount < 0) {
    return "invalid";
  }

  if (!hasAtMostTwoDecimals(rawInvested)) {
    return "invalid";
  }

  return Math.round(amount * 100) / 100;
}

function hasAtMostTwoDecimals(raw: string) {
  const trimmed = raw.trim();
  const parts = trimmed.split(".");
  if (parts.length === 1) {
    return true;
  }
  return parts[1]?.length <= 2;
}

function formatDecimalInput(value: number) {
  return value.toFixed(2).replace(/\.?0+$/, "");
}

function formatPercent(target: number) {
  return `${target.toFixed(2)}%`;
}

function formatNullablePercent(value?: number | null) {
  if (value == null) {
    return "—";
  }
  return formatPercent(value);
}

function formatNullableSignedPercent(value?: number | null) {
  if (value == null) {
    return "—";
  }
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

function formatSuggestion(value?: number | null) {
  if (value == null) {
    return <span className="text-slate-500">—</span>;
  }

  const positive = value >= 0;
  const sign = positive ? "+" : "";
  const className = positive ? "text-emerald-400" : "text-rose-400";
  return (
    <span className={className}>
      {sign}${Math.abs(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
    </span>
  );
}

function buildFallbackAllocationSummary(items: WatchlistItem[]): WatchlistAllocationSummary {
  const target_percent_total = Math.round(
    items.reduce((total, item) => total + (item.target_percent ?? 0), 0) * 100,
  ) / 100;

  return {
    target_percent_total,
    status:
      target_percent_total === 100
        ? "balanced"
        : target_percent_total < 100
          ? "under_allocated"
          : "over_allocated",
  };
}

function getAllocationSummaryCopy(summary: WatchlistAllocationSummary) {
  if (summary.status === "balanced") {
    return {
      className: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
      message: "Balanced at exactly 100%.",
    };
  }

  if (summary.status === "under_allocated") {
    return {
      className: "border-amber-500/40 bg-amber-500/10 text-amber-300",
      message: `${formatPercent(100 - summary.target_percent_total)} left to allocate.`,
    };
  }

  return {
    className: "border-rose-500/40 bg-rose-500/10 text-rose-300",
    message: `${formatPercent(summary.target_percent_total - 100)} over target allocation.`,
  };
}
