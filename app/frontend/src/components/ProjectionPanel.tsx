import type { AssetProjection } from "../types/market";

interface Props {
  projection?: AssetProjection;
  isLoading: boolean;
}

export function ProjectionPanel({ projection, isLoading }: Props) {
  if (isLoading || !projection) {
    return <div className="h-64 animate-pulse rounded-xl bg-surface-card" />;
  }

  const scenario = projection.scenarios[0];
  const lastPoint = scenario?.points[scenario.points.length - 1];

  return (
    <section className="rounded-xl border border-slate-700/60 bg-surface-card p-4">
      <header className="mb-3">
        <h2 className="text-lg font-semibold text-white">7-Day Projection</h2>
        <p className="text-xs text-slate-500">{projection.disclaimer}</p>
      </header>
      <dl className="grid gap-3 sm:grid-cols-2">
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Current</dt>
          <dd className="text-xl font-semibold text-white">${projection.current_price.toLocaleString()}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Projected (D+7)</dt>
          <dd className="text-xl font-semibold text-emerald-400">
            ${lastPoint ? lastPoint.price.toLocaleString() : "—"}
          </dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Trend</dt>
          <dd className="capitalize text-slate-200">{scenario?.direction ?? "neutral"}</dd>
        </div>
        <div>
          <dt className="text-xs uppercase tracking-wide text-slate-500">Confidence</dt>
          <dd className="text-slate-200">{((scenario?.confidence ?? 0) * 100).toFixed(0)}%</dd>
        </div>
      </dl>
      {lastPoint && (
        <p className="mt-4 text-sm text-slate-400">
          Band: ${lastPoint.lower_bound.toLocaleString()} – ${lastPoint.upper_bound.toLocaleString()}
        </p>
      )}
    </section>
  );
}
