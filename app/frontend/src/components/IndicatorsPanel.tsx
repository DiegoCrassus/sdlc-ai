import type { TechnicalIndicators } from "@shared/types/forecast";

interface Props {
  indicators?: TechnicalIndicators;
  isLoading: boolean;
}

function Metric({ label, value, format = "number" }: { label: string; value: number; format?: "number" | "price" }) {
  const display =
    format === "price" ? `$${value.toLocaleString(undefined, { maximumFractionDigits: 2 })}` : value.toFixed(2);

  return (
    <div className="rounded-lg border border-slate-700/50 bg-slate-900/50 px-3 py-2">
      <dt className="text-xs uppercase tracking-wide text-slate-500">{label}</dt>
      <dd className="mt-1 text-lg font-semibold text-white">{display}</dd>
    </div>
  );
}

export function IndicatorsPanel({ indicators, isLoading }: Props) {
  if (isLoading || !indicators) {
    return <div className="h-48 animate-pulse rounded-xl bg-surface-card" />;
  }

  return (
    <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
      <header className="mb-4">
        <h2 className="text-lg font-semibold text-white">Technical Indicators</h2>
        <p className="text-xs text-slate-500">From projection response · RSI, MACD, SMA, Bollinger</p>
      </header>
      <dl className="grid gap-3 sm:grid-cols-2 lg:grid-cols-3">
        <Metric label="RSI (14)" value={indicators.rsi_14} />
        <Metric label="MACD" value={indicators.macd} />
        <Metric label="MACD Signal" value={indicators.macd_signal} />
        <Metric label="SMA 20" value={indicators.sma_20} format="price" />
        <Metric label="SMA 50" value={indicators.sma_50} format="price" />
        <Metric label="Bollinger Upper" value={indicators.bollinger_upper} format="price" />
        <Metric label="Bollinger Lower" value={indicators.bollinger_lower} format="price" />
      </dl>
    </section>
  );
}
