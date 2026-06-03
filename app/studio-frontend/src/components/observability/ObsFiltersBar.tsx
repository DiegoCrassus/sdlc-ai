import type { EventCategory, ObsFilterParams } from "../../types/observability";

const CATEGORIES: { value: EventCategory; label: string }[] = [
  { value: "gateway", label: "Gateway" },
  { value: "obs", label: "Runs (obs)" },
  { value: "handoff", label: "Handoff" },
  { value: "gate", label: "Gate" },
];

type ObsFiltersBarProps = {
  filters: ObsFilterParams;
  onChange: (next: ObsFilterParams) => void;
  onReset: () => void;
};

export function ObsFiltersBar({ filters, onChange, onReset }: ObsFiltersBarProps) {
  const hasActive =
    Boolean(filters.category) ||
    Boolean(filters.card?.trim()) ||
    Boolean(filters.run_id?.trim()) ||
    Boolean(filters.event_type?.trim());

  return (
    <div className="flex flex-wrap items-end gap-3 rounded-xl border border-slate-800 bg-surface-card p-4">
      <label className="flex min-w-[140px] flex-col gap-1 text-xs text-slate-400">
        Category
        <select
          className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 text-sm text-white"
          value={filters.category ?? ""}
          onChange={(e) =>
            onChange({
              ...filters,
              category: (e.target.value as EventCategory) || undefined,
            })
          }
        >
          <option value="">All categories</option>
          {CATEGORIES.map((cat) => (
            <option key={cat.value} value={cat.value}>
              {cat.label}
            </option>
          ))}
        </select>
      </label>

      <label className="flex min-w-[120px] flex-col gap-1 text-xs text-slate-400">
        Card
        <input
          type="text"
          placeholder="INVES-83"
          className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 font-mono text-sm text-white placeholder:text-slate-600"
          value={filters.card ?? ""}
          onChange={(e) => onChange({ ...filters, card: e.target.value || undefined })}
        />
      </label>

      <label className="flex min-w-[140px] flex-col gap-1 text-xs text-slate-400">
        Run ID
        <input
          type="text"
          placeholder="run_…"
          className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 font-mono text-sm text-white placeholder:text-slate-600"
          value={filters.run_id ?? ""}
          onChange={(e) => onChange({ ...filters, run_id: e.target.value || undefined })}
        />
      </label>

      <label className="flex min-w-[160px] flex-1 flex-col gap-1 text-xs text-slate-400">
        Event type
        <input
          type="text"
          placeholder="gateway.shell_denied"
          className="rounded-md border border-slate-700 bg-slate-900 px-2 py-1.5 font-mono text-sm text-white placeholder:text-slate-600"
          value={filters.event_type ?? ""}
          onChange={(e) => onChange({ ...filters, event_type: e.target.value || undefined })}
        />
      </label>

      <div className="flex gap-2 pb-0.5">
        <button
          type="button"
          className="rounded-md border border-slate-600 px-3 py-1.5 text-xs text-slate-300 hover:bg-slate-800 disabled:opacity-40"
          disabled={!hasActive}
          onClick={onReset}
        >
          Reset filters
        </button>
      </div>
    </div>
  );
}
