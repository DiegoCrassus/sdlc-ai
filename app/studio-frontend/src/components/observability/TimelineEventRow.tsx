import { formatEventTimestamp, payloadSummary } from "../../api/obsQuery";
import type { StudioEvent } from "../../types/observability";

const CATEGORY_STYLES: Record<StudioEvent["category"], string> = {
  gateway: "border-sky-500/40 bg-sky-500/10 text-sky-200",
  obs: "border-emerald-500/40 bg-emerald-500/10 text-emerald-200",
  handoff: "border-violet-500/40 bg-violet-500/10 text-violet-200",
  gate: "border-amber-500/40 bg-amber-500/10 text-amber-200",
};

type TimelineEventRowProps = {
  event: StudioEvent;
  selected: boolean;
  onSelect: () => void;
};

export function TimelineEventRow({ event, selected, onSelect }: TimelineEventRowProps) {
  const categoryClass = CATEGORY_STYLES[event.category];

  return (
    <button
      type="button"
      onClick={onSelect}
      className={[
        "w-full rounded-lg border px-4 py-3 text-left transition-colors",
        selected
          ? "border-studio-accent/60 bg-studio-accent/10"
          : "border-slate-800 bg-surface-card/80 hover:border-slate-600",
      ].join(" ")}
    >
      <div className="flex flex-wrap items-center gap-2">
        <span className="font-mono text-xs text-slate-500">{formatEventTimestamp(event.timestamp)}</span>
        <span className={`rounded px-1.5 py-0.5 text-[10px] uppercase tracking-wide ${categoryClass}`}>
          {event.category}
        </span>
        <span className="font-mono text-xs text-studio-accent">{event.event_type}</span>
      </div>
      <p className="mt-1 text-sm text-slate-300">{payloadSummary(event)}</p>
      {event.correlation_id ? (
        <p className="mt-1 truncate font-mono text-[11px] text-slate-500">{event.correlation_id}</p>
      ) : null}
    </button>
  );
}
