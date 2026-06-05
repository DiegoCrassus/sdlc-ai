import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { PortfolioHistoryPoint } from "@shared/types/portfolio";

interface Props {
  points: PortfolioHistoryPoint[];
  isLoading: boolean;
  days: number;
}

function formatAxisDate(snapshotDate: string): string {
  return new Date(`${snapshotDate}T00:00:00Z`).toLocaleDateString(undefined, {
    month: "short",
    day: "numeric",
  });
}

function formatUsd(value: number): string {
  return `$${value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
}

export function PortfolioChart({ points, isLoading, days }: Props) {
  if (isLoading) {
    return <div className="h-80 animate-pulse rounded-xl bg-surface-card" data-testid="portfolio-chart-loading" />;
  }

  if (points.length === 0) {
    return (
      <section
        className="flex h-80 items-center justify-center rounded-xl border border-slate-700/60 bg-surface-card"
        data-testid="portfolio-chart-empty"
      >
        <p className="text-sm text-slate-500">No portfolio history yet — register a snapshot to begin.</p>
      </section>
    );
  }

  const data = points.map((point) => ({
    date: formatAxisDate(point.snapshot_date),
    total_value: point.total_value,
    cumulative_return_pct: point.cumulative_return_pct,
  }));

  return (
    <section
      className="rounded-xl border border-slate-700/60 bg-surface-card p-4"
      data-testid="portfolio-chart"
    >
      <header className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Portfolio Value</h2>
        <span className="text-xs text-slate-500">Daily snapshots · {days}d</span>
      </header>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={data}>
            <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
            <XAxis dataKey="date" tick={{ fill: "#94a3b8", fontSize: 12 }} minTickGap={24} />
            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 12 }}
              domain={["auto", "auto"]}
              tickFormatter={(value: number) => `$${value.toLocaleString()}`}
            />
            <Tooltip
              contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
              labelStyle={{ color: "#e2e8f0" }}
              formatter={(value: number, name: string) => {
                if (name === "total_value") {
                  return [formatUsd(value), "Total value"];
                }
                return [`${value.toFixed(2)}%`, "Cumulative return"];
              }}
            />
            <Line
              type="monotone"
              dataKey="total_value"
              stroke="#34d399"
              strokeWidth={2}
              dot={points.length <= 14}
              isAnimationActive={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
