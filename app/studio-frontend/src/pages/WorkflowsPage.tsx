import { useMemo, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import { studioApi } from "../api/client";
import { DerivedBanner } from "../components/common/DerivedBanner";
import { CanvasFiltersBar } from "../components/canvas/CanvasFiltersBar";
import { CanvasLegendPanel } from "../components/canvas/CanvasLegendPanel";
import { NodeInspector } from "../components/canvas/NodeInspector";
import { WorkflowCanvas } from "../components/canvas/WorkflowCanvas";
import type { CanvasFilterParams } from "../types/canvas";

export function WorkflowsPage() {
  const [filters, setFilters] = useState<CanvasFilterParams>({});
  const [selectedNodeId, setSelectedNodeId] = useState<string | null>(null);

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
      <div>
        <h1 className="text-2xl font-bold text-white">Workflows</h1>
        <p className="mt-1 text-sm text-slate-400">
          Read-only SDLC graph from <code className="text-slate-300">GET /studio/canvas/full</code>
          {data?.canvas.name ? ` · ${data.canvas.name}` : ""}
        </p>
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
            <CanvasLegendPanel legend={data?.legend} />
          )}
        </div>
      )}
    </div>
  );
}
