import { useCallback, useMemo } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type Node,
  type OnSelectionChangeParams,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { CanvasEdge, CanvasNode } from "../../types/canvas";
import { mapCanvasToFlow, type StudioNodeData } from "./mapViewModel";
import { StudioNode } from "./StudioNode";

const nodeTypes = { studioNode: StudioNode };

type WorkflowCanvasProps = {
  nodes: CanvasNode[];
  edges: CanvasEdge[];
  selectedNodeId: string | null;
  onSelectNode: (nodeId: string | null) => void;
};

export function WorkflowCanvas({
  nodes,
  edges,
  selectedNodeId,
  onSelectNode,
}: WorkflowCanvasProps) {
  const { nodes: flowNodes, edges: flowEdges } = useMemo(
    () => mapCanvasToFlow(nodes, edges),
    [nodes, edges],
  );

  const styledNodes = useMemo(
    () =>
      flowNodes.map((node) => ({
        ...node,
        selected: node.id === selectedNodeId,
      })),
    [flowNodes, selectedNodeId],
  );

  const onSelectionChange = useCallback(
    ({ nodes: selected }: OnSelectionChangeParams<Node<StudioNodeData>>) => {
      onSelectNode(selected[0]?.id ?? null);
    },
    [onSelectNode],
  );

  const onPaneClick = useCallback(() => {
    onSelectNode(null);
  }, [onSelectNode]);

  if (nodes.length === 0) {
    return (
      <div className="flex h-full min-h-[420px] items-center justify-center rounded-xl border border-dashed border-slate-700 bg-surface-card/40 text-sm text-slate-500">
        No nodes match the current filters.
      </div>
    );
  }

  return (
    <div className="h-full min-h-[420px] overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
      <ReactFlow
        nodes={styledNodes}
        edges={flowEdges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.2}
        maxZoom={1.5}
        onSelectionChange={onSelectionChange}
        onPaneClick={onPaneClick}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={16} color="#334155" />
        <Controls className="!border-slate-700 !bg-surface-card !shadow-lg [&>button]:!border-slate-600 [&>button]:!bg-slate-800 [&>button]:!text-slate-200" />
        <MiniMap
          className="!border-slate-700 !bg-surface-card"
          nodeColor={(node) => {
            const status = (node.data as StudioNodeData | undefined)?.validationStatus;
            if (status === "pass") return "#34d399";
            if (status === "warn") return "#fbbf24";
            if (status === "fail") return "#f87171";
            return "#64748b";
          }}
          maskColor="rgb(15 23 42 / 0.75)"
        />
      </ReactFlow>
    </div>
  );
}
