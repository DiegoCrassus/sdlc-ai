import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { CompareSeries } from "../types/market";

const LINE_COLORS = ["#34d399", "#60a5fa", "#f472b6", "#fbbf24"];

interface Props {
  series: CompareSeries[];
  isLoading: boolean;
  days: number;
}

interface ChartPoint {
  date: string;
  [symbol: string]: string | number;
}

function formatAxisDate(date: string): string {
  return new Date(date).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function buildChartData(series: CompareSeries[]): ChartPoint[] {
  const byDate = new Map<string, ChartPoint>();

  for (const entry of series) {
    for (const point of entry.points) {
      const existing = byDate.get(point.date) ?? { date: point.date };
      existing[entry.symbol] = point.normalized_close;
      byDate.set(point.date, existing);
    }
  }

  return [...byDate.values()].sort(
    (left, right) => new Date(left.date).getTime() - new Date(right.date).getTime(),
  );
}

export function CompareChart({ series, isLoading, days }: Props) {
  if (isLoading) {
    return <div className="h-96 animate-pulse rounded-xl bg-surface-card" />;
  }

  const points = buildChartData(series);

  if (points.length === 0) {
    return (
      <section className="flex h-96 items-center justify-center rounded-xl border border-slate-700/60 bg-surface-card">
        <p className="text-sm text-slate-500">No aligned compare data available</p>
      </section>
    );
  }

  const symbols = series.map((entry) => entry.symbol);

  return (
    <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
      <header className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">Normalized overlay (base 100)</h2>
        <span className="text-xs text-slate-500">{days}-day aligned window</span>
      </header>
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <LineChart data={points}>
            <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
            <XAxis
              dataKey="date"
              tick={{ fill: "#94a3b8", fontSize: 12 }}
              tickFormatter={formatAxisDate}
              minTickGap={32}
            />
            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 12 }}
              domain={["auto", "auto"]}
              tickFormatter={(value: number) => value.toFixed(0)}
            />
            <Tooltip
              contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
              labelStyle={{ color: "#e2e8f0" }}
              labelFormatter={(label) => formatAxisDate(String(label))}
              formatter={(value: number, name: string) => [value.toFixed(2), name]}
            />
            <Legend />
            {symbols.map((symbol, index) => (
              <Line
                key={symbol}
                type="monotone"
                dataKey={symbol}
                name={symbol}
                stroke={LINE_COLORS[index % LINE_COLORS.length]}
                strokeWidth={2}
                dot={false}
                connectNulls
                isAnimationActive={false}
              />
            ))}
          </LineChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
