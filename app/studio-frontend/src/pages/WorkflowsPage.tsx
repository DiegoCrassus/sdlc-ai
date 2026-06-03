import { useMemo, useState } from "react";
import { Link } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { DerivedBanner } from "../components/common/DerivedBanner";
import { CanvasFiltersBar } from "../components/canvas/CanvasFiltersBar";
import { CanvasLegendPanel } from "../components/canvas/CanvasLegendPanel";
import { NodeInspector } from "../components/canvas/NodeInspector";
import { WorkflowCanvas } from "../components/canvas/WorkflowCanvas";
import {
  DEFAULT_VALIDATION_VISIBILITY,
  toggleValidationVisibility,
} from "../components/canvas/validationVisibility";
import type { CanvasFilterParams, ValidationStatus } from "../types/canvas";

function builderHref(selectedNodeId: string | null): string {
  if (!selectedNodeId) {
    return "/builder";
  }
  return `/builder?node=${encodeURIComponent(selectedNodeId)}`;
}

export function WorkflowsPage() {
  const [filters, setFilters] = useState<CanvasFilterParams>({});
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);
  const [visibleValidationStatuses, setVisibleValidationStatuses] = useState(
    DEFAULT_VALIDATION_VISIBILITY,
  );

  const canvasQuery = useQuery({
    queryKey: ["studio", "canvas", "full", filters],
    queryFn: () => studioApi.canvasFull(filters),
    refetchInterval: 60_000,
  });

  const nodeDetailQuery = useQuery({
    queryKey: ["studio", "canvas", "node", selectedNodeId],
    queryFn: () => studioApi.canvasNode(selectedNodeId!),
    enabled: Boolean(selectedNodeId),
  });

  const authority = canvasQuery.data?.canvas.authority ?? "derived_non_authoritative";

  const filterKey = useMemo(() => JSON.stringify(filters), [filters]);

  const onToggleValidationStatus = (status: ValidationStatus) => {
    setVisibleValidationStatuses((current) => toggleValidationVisibility(current, status));
  };

  if (canvasQuery.isError) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <DerivedBanner authority={authority} />
        <div className="rounded-lg border border-studio-fail/40 bg-red-950/40 p-4 text-red-200">
          <p className="font-medium">Cannot load workflow canvas</p>
          <p className="mt-1 text-sm">
            Start the backend with <code className="text-red-100">make studio-dev</code>, then
            refresh.
          </p>
          <p className="mt-2 text-xs text-red-300/80">{canvasQuery.error.message}</p>
        </div>
      </div>
    );
  }

  const data = canvasQuery.data;

  return (
    <div className="mx-auto flex max-w-[1600px] flex-col gap-4">
      <DerivedBanner authority={authority} />
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <h1 className="text-2xl font-bold text-white">Workflows</h1>
          <p className="mt-1 text-sm text-slate-400">
            Read-only SDLC graph from <code className="text-slate-300">GET /studio/canvas/full</code>
            {data?.canvas.name ? ` · ${data.canvas.name}` : ""}
          </p>
        </div>
        <Link
          to={builderHref(selectedNodeId)}
          className="rounded-md border border-studio-accent/50 bg-studio-accent/10 px-4 py-2 text-sm font-medium text-studio-accent hover:bg-studio-accent/20"
        >
          Propose change
        </Link>
      </div>

      <CanvasFiltersBar
        legend={data?.legend}
        filters={filters}
        meta={data?.meta}
        onChange={setFilters}
        onReset={() => {
          setFilters({});
          setSelectedNodeId(null);
        }}
      />

      {canvasQuery.isLoading ? (
        <p className="text-slate-400">Loading canvas…</p>
      ) : (
        <div className="grid min-h-[520px] gap-4 lg:grid-cols-[1fr_auto] lg:grid-rows-[1fr_auto]">
          <div className="h-[calc(100vh-18rem)] min-h-[420px] lg:row-span-2">
            <WorkflowCanvas
              key={filterKey}
              nodes={data?.nodes ?? []}
              edges={data?.edges ?? []}
              selectedNodeId={selectedNodeId}
              visibleValidationStatuses={visibleValidationStatuses}
              onSelectNode={setSelectedNodeId}
            />
          </div>
          {selectedNodeId ? (
            <NodeInspector
              detail={nodeDetailQuery.data}
              loading={nodeDetailQuery.isLoading}
              onClose={() => setSelectedNodeId(null)}
            />
          ) : (
            <CanvasLegendPanel
              legend={data?.legend}
              visibleStatuses={visibleValidationStatuses}
              onToggleStatus={onToggleValidationStatus}
            />
          )}
        </div>
      )}
    </div>
  );
}
