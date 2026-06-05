import type { AllocationStatus, RebalanceSummary } from "../types/market";

interface Props {
  rebalanceSummary?: RebalanceSummary;
  allocationStatus?: AllocationStatus;
}

export function RebalanceSummaryPanel({ rebalanceSummary, allocationStatus }: Props) {
  const summary = rebalanceSummary ?? { total_invested: 0, suggestions_ready: false };
  const copy = getRebalanceCopy(summary, allocationStatus);

  return (
    <div
      className={`rounded-lg border px-4 py-3 text-sm ${copy.className}`}
      role="status"
      aria-label="Portfolio rebalance summary"
    >
      <p className="font-medium">Total invested: {formatCurrency(summary.total_invested)}</p>
      {summary.max_drift_percent != null && (
        <p className="mt-1">Max drift: {formatSignedPercent(summary.max_drift_percent)}</p>
      )}
      <p className="mt-1">{copy.message}</p>
    </div>
  );
}

function getRebalanceCopy(
  summary: RebalanceSummary,
  allocationStatus?: AllocationStatus,
): { className: string; message: string } {
  if (summary.total_invested === 0) {
    return {
      className: "border-slate-600/60 bg-slate-800/40 text-slate-300",
      message: "Enter invested amounts to see current weights and drift.",
    };
  }

  if (allocationStatus !== "balanced") {
    return {
      className: "border-amber-500/40 bg-amber-500/10 text-amber-300",
      message: "Balance target allocations to 100% before rebalance suggestions appear.",
    };
  }

  if (summary.suggestions_ready) {
    return {
      className: "border-emerald-500/40 bg-emerald-500/10 text-emerald-300",
      message: "Rebalance suggestions are ready. Review drift and suggested buy/sell amounts.",
    };
  }

  return {
    className: "border-slate-600/60 bg-slate-800/40 text-slate-300",
    message: "Portfolio weights are shown; suggestions will appear when targets are balanced.",
  };
}

function formatCurrency(amount: number) {
  return `$${amount.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function formatSignedPercent(value: number) {
  const sign = value >= 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}
