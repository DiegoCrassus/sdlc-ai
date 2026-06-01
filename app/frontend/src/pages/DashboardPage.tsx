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
  useWatchlist,
} from "../hooks/useMarketData";

const TICKER_SYMBOLS = ["AAPL", "MSFT", "NVDA", "BTC", "ETH", "SOL", "EUR/USD"];

export function DashboardPage() {
  const [selectedSymbol, setSelectedSymbol] = useState("BTC");
  const overviewQuery = useMarketOverview();
  const tickerQuery = useTickerQuotes(TICKER_SYMBOLS);
  const watchlistQuery = useWatchlist();
  const alertsQuery = useAlerts();
  const ohlcvQuery = useOhlcv(selectedSymbol);
  const projectionQuery = useProjection(selectedSymbol, 7);

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
          selectedSymbol={selectedSymbol}
          onSelect={setSelectedSymbol}
          isLoading={watchlistQuery.isLoading}
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
