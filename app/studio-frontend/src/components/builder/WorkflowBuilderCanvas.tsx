import { useCallback, useMemo } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ReactFlow,
  type Connection,
  type Edge,
  type Node,
  type OnSelectionChangeParams,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";

import type { CanvasNode } from "../../types/canvas";
import type { WorkflowTransitionDraft } from "../../types/builder";
import { StudioNode } from "../canvas/StudioNode";
import { mapCanvasEdge, mapCanvasNode, type StudioNodeData } from "../canvas/mapViewModel";
import { applyDagreLayout } from "../canvas/mapViewModel";
import { draftsToCanvasEdges, stageNodesFromCanvas } from "./workflowDraft";

const nodeTypes = { studioNode: StudioNode };

type WorkflowBuilderCanvasProps = {
  nodes: CanvasNode[];
  drafts: WorkflowTransitionDraft[];
  selectedEdgeId: string | null;
  highlightedNodeId: string | null;
  onSelectEdge: (edgeDisplayId: string | null) => void;
  onConnectStages: (sourceDisplayId: string, targetDisplayId: string) => void;
  onRemoveEdge: (edgeDisplayId: string) => void;
};

export function WorkflowBuilderCanvas({
  nodes,
  drafts,
  selectedEdgeId,
  highlightedNodeId,
  onSelectEdge,
  onConnectStages,
  onRemoveEdge,
}: WorkflowBuilderCanvasProps) {
  const stageNodes = useMemo(() => stageNodesFromCanvas(nodes), [nodes]);
  const draftEdges = useMemo(() => draftsToCanvasEdges(drafts), [drafts]);

  const { nodes: flowNodes, edges: flowEdges } = useMemo(() => {
    const mappedNodes = stageNodes.map((node) => mapCanvasNode(node));
    const mappedEdges = draftEdges.map((edge) => mapCanvasEdge(edge));
    return applyDagreLayout(mappedNodes, mappedEdges);
  }, [stageNodes, draftEdges]);

  const styledNodes = useMemo(
    () =>
      flowNodes.map((node) => ({
        ...node,
        selected: node.id === highlightedNodeId,
        data: {
          ...node.data,
          validationBorderVisible: false,
        },
      })),
    [flowNodes, highlightedNodeId],
  );

  const styledEdges = useMemo(
    () =>
      flowEdges.map((edge) => ({
        ...edge,
        selected: edge.id === selectedEdgeId,
        style: edge.id === selectedEdgeId ? { stroke: "#38bdf8", strokeWidth: 2 } : undefined,
      })),
    [flowEdges, selectedEdgeId],
  );

  const onConnect = useCallback(
    (connection: Connection) => {
      if (connection.source && connection.target) {
        onConnectStages(connection.source, connection.target);
      }
    },
    [onConnectStages],
  );

  const onSelectionChange = useCallback(
    ({ edges: selectedEdges }: OnSelectionChangeParams<Node<StudioNodeData>, Edge>) => {
      onSelectEdge(selectedEdges[0]?.id ?? null);
    },
    [onSelectEdge],
  );

  const onEdgesDelete = useCallback(
    (deleted: Edge[]) => {
      for (const edge of deleted) {
        onRemoveEdge(edge.id);
      }
    },
    [onRemoveEdge],
  );

  if (stageNodes.length === 0) {
    return (
      <div className="flex h-full min-h-[420px] items-center justify-center rounded-xl border border-dashed border-slate-700 bg-surface-card/40 text-sm text-slate-500">
        No stage nodes available in the canvas payload.
      </div>
    );
  }

  return (
    <div className="h-full min-h-[420px] overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
      <ReactFlow
        nodes={styledNodes}
        edges={styledEdges}
        nodeTypes={nodeTypes}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        minZoom={0.2}
        maxZoom={1.5}
        nodesConnectable
        elementsSelectable
        deleteKeyCode={["Backspace", "Delete"]}
        onConnect={onConnect}
        onSelectionChange={onSelectionChange}
        onEdgesDelete={onEdgesDelete}
        proOptions={{ hideAttribution: true }}
      >
        <Background gap={16} color="#334155" />
        <Controls className="!border-slate-700 !bg-surface-card !shadow-lg [&>button]:!border-slate-600 [&>button]:!bg-slate-800 [&>button]:!text-slate-200" />
        <MiniMap
          className="!border-slate-700 !bg-surface-card"
          nodeColor={() => "#64748b"}
          maskColor="rgb(15 23 42 / 0.75)"
        />
      </ReactFlow>
    </div>
  );
}
