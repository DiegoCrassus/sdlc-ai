import {
  Area,
  AreaChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { PricePoint } from "../types/market";

interface Props {
  symbol: string;
  points: PricePoint[];
  isLoading: boolean;
}

export function PriceChart({ symbol, points, isLoading }: Props) {
  if (isLoading) {
    return <div className="h-80 animate-pulse rounded-xl bg-surface-card" />;
  }

  const data = points.map((point) => ({
    date: new Date(point.timestamp).toLocaleDateString(undefined, { month: "short", day: "numeric" }),
    close: point.close,
  }));

  return (
    <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
      <header className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">{symbol} Price Chart</h2>
        <span className="text-xs text-slate-500">Daily OHLCV · 90d</span>
      </header>
      <div className="h-80">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data}>
            <defs>
              <linearGradient id="priceFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#34d399" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
              </linearGradient>
            </defs>
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
            />
            <Area type="monotone" dataKey="close" stroke="#34d399" fill="url(#priceFill)" strokeWidth={2} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
