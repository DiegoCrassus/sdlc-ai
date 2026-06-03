import { useCallback, useEffect, useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { mergeTimelineEvents } from "../api/obsQuery";
import { DerivedBanner } from "../components/common/DerivedBanner";
import { ObsFiltersBar } from "../components/observability/ObsFiltersBar";
import { TimelineEventRow } from "../components/observability/TimelineEventRow";
import { useStudioObsStream } from "../hooks/useStudioObsStream";
import type { ObsFilterParams, ObsStreamStatus, StudioEvent } from "../types/observability";

const DEFAULT_LIMIT = 100;

const STREAM_LABEL: Record<ObsStreamStatus, string> = {
  idle: "SSE idle",
  connecting: "Connecting…",
  open: "Live",
  error: "SSE error — retry by refreshing",
  closed: "Disconnected",
};

function streamBadgeClass(status: ObsStreamStatus): string {
  if (status === "open") return "border-emerald-500/50 bg-emerald-500/10 text-emerald-200";
  if (status === "error") return "border-studio-fail/50 bg-red-950/40 text-red-200";
  if (status === "connecting") return "border-studio-accent/40 bg-studio-accent/10 text-sky-200";
  return "border-slate-600 bg-slate-800/60 text-slate-400";
}

function CorrelationPanel({ event }: { event: StudioEvent }) {
  const corr = event.correlation;
  const entries = [
    ["correlation_id", event.correlation_id],
    ["card", corr.card],
    ["run_id", corr.run_id],
    ["branch", corr.branch],
    ["session_id", corr.session_id],
  ].filter(([, value]) => value);

  return (
    <div className="space-y-4 rounded-xl border border-slate-800 bg-surface-card p-4">
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-500">Selected event</p>
        <p className="mt-1 font-mono text-sm text-studio-accent">{event.event_type}</p>
        <p className="mt-1 font-mono text-xs text-slate-500">{event.event_id}</p>
      </div>
      {entries.length > 0 ? (
        <dl className="space-y-2 text-sm">
          {entries.map(([key, value]) => (
            <div key={key}>
              <dt className="text-xs uppercase text-slate-500">{key}</dt>
              <dd className="mt-0.5 font-mono text-xs text-slate-200">{String(value)}</dd>
            </div>
          ))}
        </dl>
      ) : (
        <p className="text-xs text-slate-500">No correlation fields on this event.</p>
      )}
      <div>
        <p className="text-xs uppercase tracking-wide text-slate-500">Payload</p>
        <pre className="mt-2 max-h-64 overflow-auto rounded-md border border-slate-700 bg-slate-900 p-3 font-mono text-[11px] text-slate-300">
          {JSON.stringify(event.payload, null, 2)}
        </pre>
      </div>
      <p className="text-xs text-slate-500">
        Continue orchestration in Cursor — Studio does not embed chat. Source:{" "}
        <span className="font-mono text-slate-400">{event.source}</span>
      </p>
    </div>
  );
}

export function ObservabilityPage() {
  const [filters, setFilters] = useState<ObsFilterParams>({ limit: DEFAULT_LIMIT });
  const [events, setEvents] = useState<StudioEvent[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const filterKey = useMemo(() => JSON.stringify(filters), [filters]);

  const timelineQuery = useQuery({
    queryKey: ["studio", "obs", "timeline", filters],
    queryFn: () => studioApi.obsTimeline(filters),
    refetchInterval: 60_000,
  });

  useEffect(() => {
    if (timelineQuery.data?.events) {
      setEvents(timelineQuery.data.events);
      setSelectedId((current) => {
        if (current && timelineQuery.data!.events.some((e) => e.event_id === current)) {
          return current;
        }
        const list = timelineQuery.data!.events;
        const last = list[list.length - 1];
        return last?.event_id ?? null;
      });
    }
  }, [timelineQuery.data]);

  const onStreamEvent = useCallback((event: StudioEvent) => {
    setEvents((prev) => mergeTimelineEvents(prev, [event]));
    setSelectedId((current) => current ?? event.event_id);
  }, []);

  const [sseSince, setSseSince] = useState<string | null>(null);

  useEffect(() => {
    setSseSince(null);
  }, [filterKey]);

  useEffect(() => {
    const list = timelineQuery.data?.events;
    const last = list?.[list.length - 1];
    if (last) {
      setSseSince((prev) => prev ?? last.timestamp);
    }
  }, [timelineQuery.data]);

  const streamStatus = useStudioObsStream({
    enabled: !timelineQuery.isError && !timelineQuery.isLoading,
    filters,
    since: sseSince,
    onEvent: onStreamEvent,
  });

  const selectedEvent = useMemo(
    () => events.find((e) => e.event_id === selectedId) ?? null,
    [events, selectedId],
  );

  if (timelineQuery.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <DerivedBanner />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load observability timeline</p>
          <p className="mt-1 text-sm">
            Start the backend with <code className="text-red-100">make studio-dev</code>, then refresh.
          </p>
          <p className="mt-2 text-xs text-red-300/80">{timelineQuery.error.message}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <DerivedBanner />
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white">Observability</h1>
          <p className="mt-1 text-sm text-slate-400">
            Unified timeline from gateway, handoff, gate, and obs runs · SSE{" "}
            <code className="text-slate-500">/studio/obs/events</code>
          </p>
        </div>
        <span
          className={`rounded-full border px-3 py-1 text-xs font-medium ${streamBadgeClass(streamStatus)}`}
        >
          {STREAM_LABEL[streamStatus]}
        </span>
      </div>

      <ObsFiltersBar
        filters={filters}
        onChange={(next) => setFilters({ limit: DEFAULT_LIMIT, ...next })}
        onReset={() => setFilters({ limit: DEFAULT_LIMIT })}
      />

      <div className="grid gap-6 lg:grid-cols-[1fr_280px]">
        <section className="space-y-2" key={filterKey}>
          <div className="flex items-center justify-between text-xs text-slate-500">
            <span>
              {timelineQuery.isLoading ? "Loading…" : `${events.length} event(s)`}
              {timelineQuery.data?.count != null && !timelineQuery.isLoading
                ? ` · API count ${timelineQuery.data.count}`
                : null}
            </span>
          </div>
          {timelineQuery.isLoading && events.length === 0 ? (
            <p className="text-slate-400">Loading timeline…</p>
          ) : events.length === 0 ? (
            <div className="rounded-xl border border-dashed border-slate-700 p-8 text-center text-sm text-slate-500">
              No events match the current filters. Trigger gateway or handoff activity, then refresh.
            </div>
          ) : (
            <ul className="space-y-2">
              {[...events].reverse().map((event) => (
                <li key={event.event_id}>
                  <TimelineEventRow
                    event={event}
                    selected={event.event_id === selectedId}
                    onSelect={() => setSelectedId(event.event_id)}
                  />
                </li>
              ))}
            </ul>
          )}
        </section>

        <aside>
          {selectedEvent ? (
            <CorrelationPanel event={selectedEvent} />
          ) : (
            <div className="rounded-xl border border-dashed border-slate-700 p-6 text-center text-sm text-slate-500">
              Select an event to inspect correlation and payload.
            </div>
          )}
        </aside>
      </div>
    </div>
  );
}
