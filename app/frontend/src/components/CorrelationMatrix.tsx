import type { CompareCorrelation } from "../types/market";

interface Props {
  correlation?: CompareCorrelation;
  isLoading: boolean;
}

function correlationColor(value: number): string {
  const clamped = Math.max(-1, Math.min(1, value));
  if (clamped >= 0) {
    const intensity = Math.round(clamped * 180);
    return `rgb(16, ${80 + intensity}, ${120 + Math.round(intensity * 0.4)})`;
  }
  const intensity = Math.round(Math.abs(clamped) * 180);
  return `rgb(${120 + intensity}, ${60 + Math.round(intensity * 0.3)}, 80)`;
}

export function CorrelationMatrix({ correlation, isLoading }: Props) {
  if (isLoading) {
    return <div className="h-64 animate-pulse rounded-xl bg-surface-card" />;
  }

  if (!correlation || correlation.symbols.length === 0) {
    return (
      <section className="flex h-64 items-center justify-center rounded-xl border border-slate-700/60 bg-surface-card">
        <p className="text-sm text-slate-500">Correlation matrix unavailable</p>
      </section>
    );
  }

  const { symbols, values } = correlation;

  return (
    <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
      <header className="mb-4">
        <h2 className="text-lg font-semibold text-white">Correlation matrix</h2>
        <p className="text-xs text-slate-500">Pearson correlation on aligned daily returns</p>
      </header>
      <div className="overflow-x-auto">
        <table className="w-full min-w-[16rem] border-collapse text-sm">
          <thead>
            <tr>
              <th className="p-2 text-left text-xs uppercase tracking-wide text-slate-500" />
              {symbols.map((symbol) => (
                <th
                  key={symbol}
                  className="p-2 text-center text-xs font-semibold uppercase tracking-wide text-slate-300"
                >
                  {symbol}
                </th>
              ))}
            </tr>
          </thead>
          <tbody>
            {symbols.map((rowSymbol, rowIndex) => (
              <tr key={rowSymbol}>
                <th className="p-2 text-left text-xs font-semibold uppercase tracking-wide text-slate-300">
                  {rowSymbol}
                </th>
                {values[rowIndex]?.map((value, colIndex) => (
                  <td
                    key={`${rowSymbol}-${symbols[colIndex]}`}
                    className="p-2 text-center font-medium text-white"
                    style={{ backgroundColor: correlationColor(value) }}
                    title={`${rowSymbol} vs ${symbols[colIndex]}: ${value.toFixed(3)}`}
                  >
                    {value.toFixed(2)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
