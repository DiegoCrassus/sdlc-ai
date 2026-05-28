import { useMemo, useState } from "react";
import { useSearchParams } from "react-router-dom";

import { AssetSearch } from "../components/AssetSearch";
import { ForecastChart } from "../components/ForecastChart";
import { IndicatorsPanel } from "../components/IndicatorsPanel";
import { useOhlcv, useProjection, useWatchlist } from "../hooks/useMarketData";

const HORIZON_OPTIONS = [7, 30, 90] as const;
type HorizonDays = (typeof HORIZON_OPTIONS)[number];

function parseHorizon(value: string | null): HorizonDays {
  const parsed = Number(value);
  if (parsed === 30 || parsed === 90) return parsed;
  return 7;
}

export function ForecastPage() {
  const [searchParams, setSearchParams] = useSearchParams();
  const initialSymbol = searchParams.get("symbol") ?? "BTC";
  const [selectedSymbol, setSelectedSymbol] = useState(initialSymbol);
  const [horizonDays, setHorizonDays] = useState<HorizonDays>(parseHorizon(searchParams.get("horizon")));

  const watchlistQuery = useWatchlist();
  const ohlcvQuery = useOhlcv(selectedSymbol);
  const projectionQuery = useProjection(selectedSymbol, horizonDays);

  const watchlistItems = watchlistQuery.data?.items ?? [];

  const scenario = useMemo(
    () => projectionQuery.data?.scenarios[0],
    [projectionQuery.data],
  );

  const updateSymbol = (symbol: string) => {
    setSelectedSymbol(symbol);
    setSearchParams({ symbol, horizon: String(horizonDays) }, { replace: true });
  };

  const updateHorizon = (days: HorizonDays) => {
    setHorizonDays(days);
    setSearchParams({ symbol: selectedSymbol, horizon: String(days) }, { replace: true });
  };

  return (
    <main className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 lg:px-6">
      <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-end lg:justify-between">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
            <div>
              <label htmlFor="watchlist-select" className="mb-2 block text-sm text-slate-400">
                Asset (watchlist)
              </label>
              <select
                id="watchlist-select"
                value={selectedSymbol}
                onChange={(event) => updateSymbol(event.target.value)}
                className="w-full min-w-[10rem] rounded-lg border border-slate-600 bg-slate-900 px-3 py-2 text-sm text-white outline-none ring-emerald-500 focus:ring-2 sm:w-auto"
              >
                {watchlistItems.map((item) => (
                  <option key={item.symbol} value={item.symbol}>
                    {item.symbol} — {item.name}
                  </option>
                ))}
                {!watchlistItems.some((item) => item.symbol === selectedSymbol) && (
                  <option value={selectedSymbol}>{selectedSymbol}</option>
                )}
              </select>
            </div>
            <div>
              <p className="mb-2 text-sm text-slate-400">Horizon</p>
              <div className="flex gap-2">
                {HORIZON_OPTIONS.map((days) => (
                  <button
                    key={days}
                    type="button"
                    onClick={() => updateHorizon(days)}
                    className={[
                      "rounded-lg px-3 py-2 text-sm font-medium transition-colors",
                      horizonDays === days
                        ? "bg-emerald-500/20 text-emerald-400 ring-1 ring-emerald-500/40"
                        : "border border-slate-600 text-slate-300 hover:bg-slate-800",
                    ].join(" ")}
                  >
                    {days}d
                  </button>
                ))}
              </div>
            </div>
          </div>
          <div className="min-w-[16rem] flex-1 lg:max-w-sm">
            <AssetSearch onSelect={updateSymbol} />
          </div>
        </div>
      </section>

      <ForecastChart
        symbol={selectedSymbol}
        historical={ohlcvQuery.data?.points ?? []}
        projection={projectionQuery.data}
        isLoading={ohlcvQuery.isLoading || projectionQuery.isLoading}
        horizonDays={horizonDays}
      />

      <div className="grid gap-6 xl:grid-cols-[2fr_1fr]">
        <IndicatorsPanel
          indicators={projectionQuery.data?.indicators}
          isLoading={projectionQuery.isLoading}
        />
        <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
          <h2 className="mb-3 text-lg font-semibold text-white">Projection Summary</h2>
          {projectionQuery.isLoading || !projectionQuery.data ? (
            <div className="h-32 animate-pulse rounded-lg bg-slate-800/50" />
          ) : (
            <dl className="grid gap-3">
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">Current price</dt>
                <dd className="text-xl font-semibold text-white">
                  ${projectionQuery.data.current_price.toLocaleString()}
                </dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">Trend</dt>
                <dd className="capitalize text-slate-200">{scenario?.direction ?? "neutral"}</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">Confidence</dt>
                <dd className="text-slate-200">{((scenario?.confidence ?? 0) * 100).toFixed(0)}%</dd>
              </div>
              <div>
                <dt className="text-xs uppercase tracking-wide text-slate-500">Data source</dt>
                <dd className="text-sm capitalize text-slate-300">
                  {projectionQuery.data.meta.source} · {projectionQuery.data.meta.provider}
                </dd>
              </div>
            </dl>
          )}
        </section>
      </div>

      {projectionQuery.data?.disclaimer && (
        <p className="text-center text-xs text-slate-500">{projectionQuery.data.disclaimer}</p>
      )}
    </main>
  );
}
