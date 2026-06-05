import { useState } from "react";

import { PortfolioChart } from "../components/PortfolioChart";
import { PnlSummaryCards } from "../components/PnlSummaryCards";
import { usePortfolioHistory } from "../hooks/usePortfolio";

import type { HistoryDays } from "@shared/types/portfolio";

const DAY_OPTIONS: HistoryDays[] = [30, 90, 365];

export function PortfolioPage() {
  const [days, setDays] = useState<HistoryDays>(30);
  const historyQuery = usePortfolioHistory(days);

  return (
    <main className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 lg:px-6">
      <header className="flex flex-col gap-4 sm:flex-row sm:items-end sm:justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white">Portfólio</h1>
          <p className="mt-1 text-sm text-slate-400">Histórico de valor total da watchlist</p>
        </div>
        <div className="flex gap-2" role="group" aria-label="Período do histórico">
          {DAY_OPTIONS.map((option) => (
            <button
              key={option}
              type="button"
              onClick={() => setDays(option)}
              className={[
                "rounded-lg px-3 py-1.5 text-sm font-medium transition-colors",
                days === option
                  ? "bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/40"
                  : "border border-slate-700 text-slate-400 hover:bg-slate-800 hover:text-white",
              ].join(" ")}
            >
              {option}d
            </button>
          ))}
        </div>
      </header>

      <PnlSummaryCards summary={historyQuery.data?.summary} isLoading={historyQuery.isLoading} />

      {historyQuery.isError && (
        <p className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-300">
          Failed to load portfolio history. Sign in and try again.
        </p>
      )}

      <PortfolioChart
        points={historyQuery.data?.points ?? []}
        isLoading={historyQuery.isLoading}
        days={days}
      />
    </main>
  );
}
