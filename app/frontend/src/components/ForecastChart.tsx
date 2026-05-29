import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type { AssetProjection, PricePoint } from "../types/market";

interface Props {
  symbol: string;
  historical: PricePoint[];
  projection?: AssetProjection;
  isLoading: boolean;
  horizonDays: number;
}

interface ChartPoint {
  timestamp: string;
  historicalClose?: number;
  projectedPrice?: number;
  upperBound?: number;
  lowerBound?: number;
}

function formatAxisDate(timestamp: string): string {
  return new Date(timestamp).toLocaleDateString(undefined, { month: "short", day: "numeric" });
}

function buildChartData(
  historical: PricePoint[],
  projection?: AssetProjection,
): { points: ChartPoint[]; lastHistoricalTimestamp: string | null } {
  if (historical.length === 0) {
    return { points: [], lastHistoricalTimestamp: null };
  }

  const lastHistorical = historical[historical.length - 1];
  const lastHistoricalTimestamp = lastHistorical.timestamp;
  const scenario = projection?.scenarios[0];

  const points: ChartPoint[] = historical.map((point) => ({
    timestamp: point.timestamp,
    historicalClose: point.close,
  }));

  if (!scenario || scenario.points.length === 0) {
    return { points, lastHistoricalTimestamp };
  }

  const bridge: ChartPoint = {
    timestamp: lastHistoricalTimestamp,
    historicalClose: lastHistorical.close,
    projectedPrice: lastHistorical.close,
    upperBound: lastHistorical.close,
    lowerBound: lastHistorical.close,
  };

  const firstProjected = scenario.points[0];
  const needsBridge = firstProjected.timestamp !== lastHistoricalTimestamp;

  if (needsBridge) {
    points.push(bridge);
  } else {
    const lastIndex = points.length - 1;
    points[lastIndex] = {
      ...points[lastIndex],
      projectedPrice: lastHistorical.close,
      upperBound: lastHistorical.close,
      lowerBound: lastHistorical.close,
    };
  }

  for (const point of scenario.points) {
    if (point.timestamp === lastHistoricalTimestamp && !needsBridge) {
      points[points.length - 1] = {
        ...points[points.length - 1],
        projectedPrice: point.price,
        upperBound: point.upper_bound,
        lowerBound: point.lower_bound,
      };
      continue;
    }

    points.push({
      timestamp: point.timestamp,
      projectedPrice: point.price,
      upperBound: point.upper_bound,
      lowerBound: point.lower_bound,
    });
  }

  return { points, lastHistoricalTimestamp };
}

export function ForecastChart({ symbol, historical, projection, isLoading, horizonDays }: Props) {
  if (isLoading) {
    return <div className="h-96 animate-pulse rounded-xl bg-surface-card" />;
  }

  const { points, lastHistoricalTimestamp } = buildChartData(historical, projection);

  if (points.length === 0) {
    return (
      <section className="flex h-96 items-center justify-center rounded-xl border border-slate-700/60 bg-surface-card">
        <p className="text-sm text-slate-500">No chart data for {symbol}</p>
      </section>
    );
  }

  return (
    <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
      <header className="mb-4 flex items-center justify-between">
        <h2 className="text-lg font-semibold text-white">{symbol} Forecast</h2>
        <span className="text-xs text-slate-500">
          Historical OHLCV + {horizonDays}-day projection
        </span>
      </header>
      <div className="h-96">
        <ResponsiveContainer width="100%" height="100%">
          <ComposedChart data={points}>
            <defs>
              <linearGradient id="historicalFill" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#34d399" stopOpacity={0.35} />
                <stop offset="95%" stopColor="#34d399" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid stroke="#334155" strokeDasharray="3 3" />
            <XAxis
              dataKey="timestamp"
              tick={{ fill: "#94a3b8", fontSize: 12 }}
              tickFormatter={formatAxisDate}
              minTickGap={32}
            />
            <YAxis
              tick={{ fill: "#94a3b8", fontSize: 12 }}
              domain={["auto", "auto"]}
              tickFormatter={(value: number) => `$${value.toLocaleString()}`}
            />
            <Tooltip
              contentStyle={{ background: "#1e293b", border: "1px solid #334155", borderRadius: 8 }}
              labelStyle={{ color: "#e2e8f0" }}
              labelFormatter={(label) => formatAxisDate(String(label))}
              formatter={(value: number, name: string) => {
                const labels: Record<string, string> = {
                  historicalClose: "Historical close",
                  projectedPrice: "Projected",
                  upperBound: "Upper bound",
                  lowerBound: "Lower bound",
                };
                return [`$${value.toLocaleString()}`, labels[name] ?? name];
              }}
            />
            <Area
              type="monotone"
              dataKey="upperBound"
              stroke="none"
              fill="#34d399"
              fillOpacity={0.12}
              connectNulls
              isAnimationActive={false}
            />
            <Area
              type="monotone"
              dataKey="lowerBound"
              stroke="none"
              fill="#1e293b"
              fillOpacity={1}
              connectNulls
              isAnimationActive={false}
            />
            <Area
              type="monotone"
              dataKey="historicalClose"
              stroke="#34d399"
              fill="url(#historicalFill)"
              strokeWidth={2}
              connectNulls={false}
              isAnimationActive={false}
            />
            <Line
              type="monotone"
              dataKey="projectedPrice"
              stroke="#60a5fa"
              strokeWidth={2}
              strokeDasharray="6 4"
              dot={false}
              connectNulls
              isAnimationActive={false}
            />
            {lastHistoricalTimestamp && (
              <ReferenceLine
                x={lastHistoricalTimestamp}
                stroke="#94a3b8"
                strokeDasharray="4 4"
                label={{ value: "Now", position: "insideTopRight", fill: "#94a3b8", fontSize: 11 }}
              />
            )}
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </section>
  );
}
