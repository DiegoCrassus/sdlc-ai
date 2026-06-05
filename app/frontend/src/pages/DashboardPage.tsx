import { useMemo, useState } from "react";
import { Link } from "react-router-dom";

import { AssetSearch } from "../components/AssetSearch";
import { MarketOverviewCards } from "../components/MarketOverview";
import { PriceChart } from "../components/PriceChart";
import { ProjectionPanel } from "../components/ProjectionPanel";
import { TickerTape } from "../components/TickerTape";
import { WatchlistTable } from "../components/WatchlistTable";
import { useAlerts } from "../hooks/useAlerts";
import {
  useMarketOverview,
  useOhlcv,
  useProjection,
  useTickerQuotes,
  useUpdateWatchlistAllocation,
  useUpdateWatchlistInvested,
  useWatchlist,
} from "../hooks/useMarketData";
import { useCreatePortfolioSnapshot } from "../hooks/usePortfolio";

const TICKER_SYMBOLS = ["AAPL", "MSFT", "NVDA", "BTC", "ETH", "SOL", "EUR/USD"];

export function DashboardPage() {
  const [selectedSymbol, setSelectedSymbol] = useState("BTC");
  const overviewQuery = useMarketOverview();
  const tickerQuery = useTickerQuotes(TICKER_SYMBOLS);
  const watchlistQuery = useWatchlist();
  const updateAllocationMutation = useUpdateWatchlistAllocation();
  const updateInvestedMutation = useUpdateWatchlistInvested();
  const alertsQuery = useAlerts();
  const ohlcvQuery = useOhlcv(selectedSymbol);
  const projectionQuery = useProjection(selectedSymbol, 7);
  const snapshotMutation = useCreatePortfolioSnapshot();

  const gainersLosers = useMemo(() => {
    const overview = overviewQuery.data;
    if (!overview) return null;
    return { gainers: overview.top_gainers, losers: overview.top_losers };
  }, [overviewQuery.data]);

  return (
    <>
      <TickerTape quotes={tickerQuery.data ?? []} />

      <main className="mx-auto flex max-w-7xl flex-col gap-6 px-4 py-6 lg:px-6">
        <MarketOverviewCards overview={overviewQuery.data} isLoading={overviewQuery.isLoading} />

        <section className="flex flex-col gap-3 rounded-xl border border-slate-700/60 bg-surface-card p-4 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <h2 className="text-sm font-semibold text-white">Snapshot diário</h2>
            <p className="text-xs text-slate-500">
              Registra o valor total da watchlist para o histórico do portfólio.
            </p>
          </div>
          <div className="flex flex-col items-start gap-2 sm:items-end">
            <button
              type="button"
              onClick={() => snapshotMutation.mutate()}
              disabled={snapshotMutation.isPending}
              className="rounded-lg bg-emerald-600 px-4 py-2 text-sm font-medium text-white hover:bg-emerald-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {snapshotMutation.isPending ? "Registrando…" : "Registrar snapshot agora"}
            </button>
            {snapshotMutation.isSuccess && (
              <p className="text-xs text-emerald-400" data-testid="snapshot-success">
                Snapshot registrado — $
                {snapshotMutation.data.snapshot.total_value.toLocaleString(undefined, {
                  minimumFractionDigits: 2,
                  maximumFractionDigits: 2,
                })}
                {snapshotMutation.data.created ? " (novo)" : " (atualizado)"}
              </p>
            )}
            {snapshotMutation.isError && (
              <p className="text-xs text-rose-400" data-testid="snapshot-error">
                Falha ao registrar snapshot. Verifique se está autenticado.
              </p>
            )}
          </div>
        </section>

        {gainersLosers && (
          <div className="grid gap-4 lg:grid-cols-2">
            <MoverList title="Top Gainers" items={gainersLosers.gainers} positive />
            <MoverList title="Top Losers" items={gainersLosers.losers} positive={false} />
          </div>
        )}

        <div className="grid gap-6 xl:grid-cols-[2fr_1fr]">
          <PriceChart
            symbol={selectedSymbol}
            points={ohlcvQuery.data?.points ?? []}
            isLoading={ohlcvQuery.isLoading}
          />
          <div className="flex flex-col gap-6">
            <AssetSearch onSelect={setSelectedSymbol} />
            <ProjectionPanel projection={projectionQuery.data} isLoading={projectionQuery.isLoading} />
            <Link
              to={`/forecast?symbol=${encodeURIComponent(selectedSymbol)}`}
              className="rounded-lg border border-emerald-500/30 bg-emerald-500/10 px-4 py-3 text-center text-sm font-medium text-emerald-400 transition-colors hover:bg-emerald-500/20"
            >
              Open full forecast chart →
            </Link>
          </div>
        </div>

        <WatchlistTable
          items={watchlistQuery.data?.items ?? []}
          allocationSummary={watchlistQuery.data?.allocation_summary}
          rebalanceSummary={watchlistQuery.data?.rebalance_summary}
          selectedSymbol={selectedSymbol}
          onSelect={setSelectedSymbol}
          isLoading={watchlistQuery.isLoading}
          onUpdateAllocation={updateAllocationMutation.mutateAsync}
          isUpdatingAllocation={updateAllocationMutation.isPending}
          updateAllocationError={updateAllocationMutation.error}
          onUpdateInvested={updateInvestedMutation.mutateAsync}
          isUpdatingInvested={updateInvestedMutation.isPending}
          updateInvestedError={updateInvestedMutation.error}
          alerts={alertsQuery.alerts}
          onCreateAlert={async (payload) => {
            await alertsQuery.createAlert(payload);
          }}
          isCreatingAlert={alertsQuery.isCreating}
          createAlertError={alertsQuery.createError}
        />
      </main>
    </>
  );
}

interface MoverListProps {
  title: string;
  items: Array<{ symbol: string; name: string; price: number; change_percent: number }>;
  positive: boolean;
}

function MoverList({ title, items, positive }: MoverListProps) {
  return (
    <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
      <h2 className="mb-3 text-lg font-semibold text-white">{title}</h2>
      <ul className="space-y-2">
        {items.map((item) => (
          <li key={item.symbol} className="flex items-center justify-between text-sm">
            <div>
              <p className="font-medium text-white">{item.symbol}</p>
              <p className="text-slate-500">{item.name}</p>
            </div>
            <div className="text-right">
              <p className="text-slate-200">${item.price.toLocaleString()}</p>
              <p className={positive ? "text-emerald-400" : "text-rose-400"}>
                {item.change_percent >= 0 ? "+" : ""}
                {item.change_percent.toFixed(2)}%
              </p>
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
