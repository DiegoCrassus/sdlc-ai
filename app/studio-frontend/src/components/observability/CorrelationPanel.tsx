import type { StudioEvent } from "../../types/observability";

type CorrelationPanelProps = {
  event: StudioEvent;
};

export function CorrelationPanel({ event }: CorrelationPanelProps) {
  const corr = event.correlation;
  const entries = [
    ["correlation_id", event.correlation_id],
    ["card", corr.card],
    ["run_id", corr.run_id],
    ["branch", corr.branch],
    ["session_id", corr.session_id],
  ].filter(([, value]) => value);

  return (
    <div
      className="flex min-h-0 flex-1 flex-col gap-4 overflow-y-auto rounded-xl border border-slate-800 bg-surface-card p-4"
      data-testid="obs-detail-panel"
    >
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-500">Selected event</p>
        <p className="mt-1 font-mono text-sm leading-relaxed text-studio-accent">{event.event_type}</p>
        <p className="mt-1 break-all font-mono text-xs leading-relaxed text-slate-500">
          {event.event_id}
        </p>
      </div>
      {entries.length > 0 ? (
        <dl className="space-y-3 text-sm">
          {entries.map(([key, value]) => (
            <div key={key}>
              <dt className="text-xs uppercase text-slate-500">{key}</dt>
              <dd className="mt-0.5 break-all font-mono text-sm leading-relaxed text-slate-200">
                {String(value)}
              </dd>
            </div>
          ))}
        </dl>
      ) : (
        <p className="text-sm leading-relaxed text-slate-500">No correlation fields on this event.</p>
      )}
      <div className="min-h-0 flex-1">
        <p className="text-xs uppercase tracking-wide text-slate-500">Payload</p>
        <pre className="mt-2 max-h-72 overflow-auto rounded-md border border-slate-700 bg-slate-900 p-3 font-mono text-xs leading-relaxed text-slate-300">
          {JSON.stringify(event.payload, null, 2)}
        </pre>
      </div>
      <p className="shrink-0 text-sm leading-relaxed text-slate-500">
        Continue orchestration in Cursor — Studio does not embed chat. Source:{" "}
        <span className="font-mono text-slate-400">{event.source}</span>
      </p>
    </div>
  );
}
