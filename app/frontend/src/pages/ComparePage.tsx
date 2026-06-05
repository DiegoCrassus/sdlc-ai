import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { CompareAssetPicker } from "../components/CompareAssetPicker";
import { CompareChart } from "../components/CompareChart";
import { CorrelationMatrix } from "../components/CorrelationMatrix";
import { useCompare, useWatchlist } from "../hooks/useMarketData";
import {
  isValidCompareSelection,
  parseCompareSymbols,
  serializeCompareSymbols,
} from "../utils/compareQueryParams";

const DAYS_OPTIONS = [30, 90, 180, 365] as const;
const MAX_SYMBOLS = 4;

function parseDays(value: string | null): number {
  const parsed = Number(value);
  if (DAYS_OPTIONS.includes(parsed as (typeof DAYS_OPTIONS)[number])) {
    return parsed;
  }
  return 90;
}

export function ComparePage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialSymbols = parseCompareSymbols(searchParams.get("symbols"));
  const [selectedSymbols, setSelectedSymbols] = useState<string[]>(
    initialSymbols.length > 0 ? initialSymbols : ["BTC", "ETH"],
  );
  const [days, setDays] = useState(parseDays(searchParams.get("days")));

  const watchlistQuery = useWatchlist();
  const compareQuery = useCompare(selectedSymbols, days);

  const watchlistItems = watchlistQuery.data?.items ?? [];
  const isSelectionValid = isValidCompareSelection(selectedSymbols);

  const metricsBySymbol = useMemo(() => {
    const map = new Map<string, { volatility: number; max_drawdown: number }>();
    for (const metric of compareQuery.data?.metrics ?? []) {
      map.set(metric.symbol, {
        volatility: metric.volatility,
        max_drawdown: metric.max_drawdown,
      });
    }
    return map;
  }, [compareQuery.data?.metrics]);

  const syncUrl = (symbols: string[], nextDays: number) => {
    const params: Record<string, string> = { days: String(nextDays) };
    const serialized = serializeCompareSymbols(symbols);
    if (serialized) {
      params.symbols = serialized;
    }
    setSearchParams(params, { replace: true });
  };

  const updateSymbols = (symbols: string[]) => {
    const normalized = parseCompareSymbols(serializeCompareSymbols(symbols));
    setSelectedSymbols(normalized);
    syncUrl(normalized, days);
  };

  const addSymbol = (symbol: string) => {
    if (selectedSymbols.length >= MAX_SYMBOLS || selectedSymbols.includes(symbol)) {
      return;
    }
    updateSymbols([...selectedSymbols, symbol]);
  };

  const removeSymbol = (symbol: string) => {
    updateSymbols(selectedSymbols.filter((entry) => entry !== symbol));
  };

  const addFromWatchlist = (symbol: string) => {
    addSymbol(symbol.toUpperCase());
  };

  const updateDays = (nextDays: number) => {
    setDays(nextDays);
    syncUrl(selectedSymbols, nextDays);
  };

  return (
    <main className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 lg:px-6">
      <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div className="flex flex-col gap-3">
            <div>
              <label htmlFor="watchlist-compare" className="mb-2 block text-sm text-slate-400">
                Quick add from watchlist
              </label>
              <select
                id="watchlist-compare"
                defaultValue=""
                onChange={(event) => {
                  const symbol = event.target.value;
                  if (symbol) {
                    addFromWatchlist(symbol);
                    event.target.value = "";
                  }
                }}
                disabled={selectedSymbols.length >= MAX_SYMBOLS}
                className="w-full min-w-[12rem] rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-sm text-white outline-none ring-emerald-500 focus:ring-2 disabled:cursor-not-allowed disabled:opacity-60 sm:w-auto"
              >
                <option value="">Select asset…</option>
                {watchlistItems.map((item) => (
                  <option
                    key={item.symbol}
                    value={item.symbol}
                    disabled={selectedSymbols.includes(item.symbol.toUpperCase())}
                  >
                    {item.symbol} — {item.name}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <p className="mb-2 text-sm text-slate-400">Lookback window</p>
              <div className="flex flex-wrap gap-2">
                {DAYS_OPTIONS.map((option) => (
                  <button
                    key={option}
                    type="button"
                    onClick={() => updateDays(option)}
                    className={[
                      "rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      days === option
                        ? "bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/40"
                        : "border border-slate-600 text-slate-300 hover:bg-slate-800",
                    ].join(" ")}
                  >
                    {option}d
                  </button>
                ))}
              </div>
            </div>
          </div>
          <div className="min-w-[16rem] flex-1 lg:max-w-md">
            <CompareAssetPicker
              selectedSymbols={selectedSymbols}
              onAdd={addSymbol}
              onRemove={removeSymbol}
            />
          </div>
        </div>
      </section>

      {!isSelectionValid && (
        <p
          className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-3 text-sm text-amber-200"
          data-testid="compare-validation"
        >
          Select at least 2 and at most 4 unique symbols to load the compare chart and correlation
          matrix.
        </p>
      )}

      {compareQuery.isError && isSelectionValid && (
        <p className="rounded-lg border border-rose-500/30 bg-rose-500/10 px-4 py-3 text-sm text-rose-200">
          Failed to load compare data. Check that all symbols are valid and have enough aligned
          history.
        </p>
      )}

      <CompareChart
        series={compareQuery.data?.series ?? []}
        isLoading={isSelectionValid && compareQuery.isLoading}
        days={days}
      />

      <div className="grid gap-6 xl:grid-cols-[1fr_1fr]">
        <CorrelationMatrix
          correlation={compareQuery.data?.correlation}
          isLoading={isSelectionValid && compareQuery.isLoading}
        />

        <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
          <h2 className="mb-3 text-lg font-semibold text-white">Risk metrics</h2>
          {!isSelectionValid ? (
            <p className="text-sm text-slate-500">Metrics appear once 2+ symbols are selected.</p>
          ) : compareQuery.isLoading ? (
            <div className="h-32 animate-pulse rounded-lg bg-slate-800/50" />
          ) : (
            <ul className="space-y-3">
              {selectedSymbols.map((symbol) => {
                const metric = metricsBySymbol.get(symbol);
                return (
                  <li
                    key={symbol}
                    className="flex items-center justify-between rounded-lg border border-slate-700/60 px-3 py-2 text-sm"
                  >
                    <span className="font-medium text-white">{symbol}</span>
                    <div className="text-right text-slate-300">
                      <p>Volatility: {metric ? `${(metric.volatility * 100).toFixed(1)}%` : "—"}</p>
                      <p>
                        Max drawdown:{" "}
                        {metric ? `${(metric.max_drawdown * 100).toFixed(1)}%` : "—"}
                      </p>
                    </div>
                  </li>
                );
              })}
            </ul>
          )}
        </section>
      </div>

      {compareQuery.data?.date_range && isSelectionValid && !compareQuery.isLoading && (
        <p className="text-center text-xs text-slate-500">
          Aligned {compareQuery.data.date_range.aligned_points} trading days ·{" "}
          {compareQuery.data.date_range.start} → {compareQuery.data.date_range.end} ·{" "}
          {compareQuery.data.meta.source} · {compareQuery.data.meta.provider}
        </p>
      )}
    </main>
  );
}
