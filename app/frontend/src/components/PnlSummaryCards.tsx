import type { PortfolioHistorySummary } from "@shared/types/portfolio";

interface Props {
  summary?: PortfolioHistorySummary;
  isLoading: boolean;
}

function formatPnl(value: number | undefined): string {
  if (value === undefined) {
    return "—";
  }
  const sign = value >= 0 ? "+" : "";
  return `${sign}$${Math.abs(value).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

function pnlColor(value: number | undefined): string {
  if (value === undefined) {
    return "text-slate-400";
  }
  if (value > 0) {
    return "text-emerald-400";
  }
  if (value < 0) {
    return "text-rose-400";
  }
  return "text-slate-300";
}

export function PnlSummaryCards({ summary, isLoading }: Props) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <div key={index} className="h-24 animate-pulse rounded-xl bg-surface-card" />
        ))}
      </div>
    );
  }

  const cards = [
    { label: "Hoje", value: summary?.pnl_today },
    { label: "7 dias", value: summary?.pnl_7d },
    { label: "30 dias", value: summary?.pnl_30d },
    { label: "YTD", value: summary?.pnl_ytd },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => (
        <article
          key={card.label}
          className="rounded-xl border border-slate-700/60 bg-surface-card p-4 shadow-lg shadow-black/20"
        >
          <p className="text-sm text-slate-400">{card.label}</p>
          <p className={`mt-2 text-2xl font-semibold ${pnlColor(card.value)}`}>{formatPnl(card.value)}</p>
        </article>
      ))}
    </div>
  );
}
