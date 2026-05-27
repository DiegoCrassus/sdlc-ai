import type { MarketOverview } from "../types/market";

interface Props {
  overview?: MarketOverview;
  isLoading: boolean;
}

function formatUsd(value: number): string {
  if (value >= 1_000_000_000_000) {
    return `$${(value / 1_000_000_000_000).toFixed(2)}T`;
  }
  if (value >= 1_000_000_000) {
    return `$${(value / 1_000_000_000).toFixed(2)}B`;
  }
  return `$${value.toLocaleString()}`;
}

export function MarketOverviewCards({ overview, isLoading }: Props) {
  if (isLoading || !overview) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-28 animate-pulse rounded-xl bg-surface-card" />
        ))}
      </div>
    );
  }

  const cards = [
    {
      label: "Market Cap",
      value: formatUsd(overview.total_market_cap_usd),
      hint: "Global aggregate",
    },
    {
      label: "24h Volume",
      value: formatUsd(overview.total_volume_24h_usd),
      hint: "Across tracked assets",
    },
    {
      label: "BTC Dominance",
      value: `${overview.btc_dominance_percent.toFixed(1)}%`,
      hint: "Crypto market share",
    },
    {
      label: "Fear & Greed",
      value: String(overview.fear_greed_index),
      hint: overview.fear_greed_index >= 55 ? "Greed zone" : "Neutral / fear",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <article
          key={card.label}
          className="rounded-xl border border-slate-700/60 bg-surface-card p-4 shadow-lg shadow-black/20"
        >
          <p className="text-sm text-slate-400">{card.label}</p>
          <p className="mt-2 text-2xl font-semibold text-white">{card.value}</p>
          <p className="mt-1 text-xs text-slate-500">{card.hint}</p>
        </article>
      ))}
    </div>
  );
}
