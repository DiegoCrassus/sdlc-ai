import { useCallback, useEffect, useMemo, useRef } from "react";
import {
  Background,
  Controls,
  MiniMap,
  ConnectionMode,
  ReactFlow,
  useEdgesState,
  useNodesState,
  type Connection,
  type Edge,
  type FinalConnectionState,
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
import { TransitionEdge } from "./TransitionEdge";

const nodeTypes = { studioNode: StudioNode };
const edgeTypes = { transitionEdge: TransitionEdge };

type WorkflowBuilderCanvasProps = {
  nodes: CanvasNode[];
  drafts: WorkflowTransitionDraft[];
  selectedEdgeId: string | null;
  highlightedNodeId: string | null;
  connectOnClick: boolean;
  onConnectOnClickChange: (enabled: boolean) => void;
  onSelectEdge: (edgeDisplayId: string | null) => void;
  onConnectStages: (sourceDisplayId: string, targetDisplayId: string) => void;
  onRemoveEdge: (edgeDisplayId: string) => void;
  onSelectNode?: (nodeId: string | null) => void;
  onConnectionFailed: (message: string) => void;
};

function mergeNodeData(
  current: Node<StudioNodeData>[],
  mapped: Node<StudioNodeData>[],
): Node<StudioNodeData>[] {
  return mapped.map((node) => {
    const existing = current.find((item) => item.id === node.id);
    if (!existing) {
      return node;
    }
    return {
      ...node,
      position: existing.position,
    };
  });
}

export function WorkflowBuilderCanvas({
  nodes,
  drafts,
  selectedEdgeId,
  highlightedNodeId,
  connectOnClick,
  onConnectOnClickChange,
  onSelectEdge,
  onConnectStages,
  onRemoveEdge,
  onSelectNode,
  onConnectionFailed,
}: WorkflowBuilderCanvasProps) {
  const stageNodes = useMemo(() => stageNodesFromCanvas(nodes), [nodes]);
  const mappedNodes = useMemo(
    () => stageNodes.map((node) => mapCanvasNode(node)),
    [stageNodes],
  );
  const draftEdges = useMemo(() => draftsToCanvasEdges(drafts), [drafts]);

  const layoutAppliedRef = useRef(false);
  const [flowNodes, setFlowNodes, onNodesChange] = useNodesState<Node<StudioNodeData>>([]);
  const flowEdgesStatic = useMemo(
    () =>
      draftEdges.map((edge) => ({
        ...mapCanvasEdge(edge),
        type: "transitionEdge" as const,
      })),
    [draftEdges],
  );
  const [flowEdges, setFlowEdges, onEdgesChange] = useEdgesState<Edge>(flowEdgesStatic);

  useEffect(() => {
    if (mappedNodes.length === 0) {
      setFlowNodes([]);
      layoutAppliedRef.current = false;
      return;
    }

    if (!layoutAppliedRef.current) {
      const { nodes: positioned } = applyDagreLayout(mappedNodes, flowEdgesStatic);
      setFlowNodes(positioned);
      layoutAppliedRef.current = true;
      return;
    }

    setFlowNodes((current) => mergeNodeData(current, mappedNodes));
  }, [mappedNodes, flowEdgesStatic, setFlowNodes]);

  useEffect(() => {
    setFlowEdges(
      flowEdgesStatic.map((edge) => ({
        ...edge,
        selected: edge.id === selectedEdgeId,
        style: edge.id === selectedEdgeId ? { stroke: "#38bdf8", strokeWidth: 2 } : undefined,
      })),
    );
  }, [flowEdgesStatic, selectedEdgeId, setFlowEdges]);

  const runAutoLayout = useCallback(() => {
    setFlowNodes((current) => {
      const { nodes: positioned } = applyDagreLayout(current, flowEdgesStatic);
      return positioned;
    });
  }, [flowEdgesStatic, setFlowNodes]);

  const styledNodes = useMemo(
    () =>
      flowNodes.map((node) => ({
        ...node,
        selected: node.id === highlightedNodeId,
        connectable: true,
        data: {
          ...node.data,
          validationBorderVisible: false,
        },
      })),
    [flowNodes, highlightedNodeId],
  );

  const onConnect = useCallback(
    (connection: Connection) => {
      if (!connection.source || !connection.target) {
        onConnectionFailed("Could not connect: missing source or target handle.");
        return;
      }
      if (connection.source === connection.target) {
        onConnectionFailed("Cannot connect a stage to itself.");
        return;
      }
      onConnectStages(connection.source, connection.target);
    },
    [onConnectStages, onConnectionFailed],
  );

  const onConnectEnd = useCallback(
    (_event: MouseEvent | TouchEvent, connectionState: FinalConnectionState) => {
      if (connectionState.isValid) {
        return;
      }
      const { fromNode, toNode, fromHandle } = connectionState;
      if (fromNode?.id && toNode?.id && fromNode.id === toNode.id) {
        onConnectionFailed("Cannot connect a stage to itself.");
        return;
      }
      if (fromNode && !toNode && !fromHandle) {
        onConnectionFailed("Could not connect: pick a source handle first.");
        return;
      }
      if (fromNode && toNode) {
        onConnectionFailed("Could not connect these stages. Use bottom → top handles.");
        return;
      }
      if (fromNode && !toNode) {
        onConnectionFailed("Connection cancelled or invalid target.");
      }
    },
    [onConnectionFailed],
  );

  const onSelectionChange = useCallback(
    ({ edges: selectedEdges, nodes: selectedNodes }: OnSelectionChangeParams<Node<StudioNodeData>, Edge>) => {
      onSelectEdge(selectedEdges[0]?.id ?? null);
      onSelectNode?.(selectedNodes[0]?.id ?? null);
    },
    [onSelectEdge, onSelectNode],
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
      <div
        data-testid="builder-canvas-empty"
        className="flex h-full min-h-[420px] items-center justify-center rounded-xl border border-dashed border-slate-700 bg-surface-card/40 text-sm text-slate-500"
      >
        Drag stages from the toolbox when WB-2 ships. No lifecycle stages from API.
      </div>
    );
  }

  return (
    <div className="flex h-full min-h-[420px] flex-col gap-2 overflow-hidden">
      <div className="flex flex-wrap items-center gap-2">
        <button
          type="button"
          data-testid="builder-auto-layout"
          onClick={runAutoLayout}
          className="rounded-md border border-slate-700 bg-slate-900 px-3 py-1.5 text-xs text-slate-200 hover:bg-slate-800"
        >
          Auto-layout
        </button>
        <label className="flex cursor-pointer items-center gap-2 text-xs text-slate-400">
          <input
            type="checkbox"
            data-testid="builder-connect-on-click"
            checked={connectOnClick}
            onChange={(event) => onConnectOnClickChange(event.target.checked)}
            className="rounded border-slate-600"
          />
          Connect on click
        </label>
        <span className="text-xs text-slate-500">
          Drag <span className="text-slate-300">bottom → top</span> handles, or enable click mode.
        </span>
      </div>

      <div className="min-h-0 flex-1 overflow-hidden rounded-xl border border-slate-800 bg-slate-950">
        <ReactFlow
          nodes={styledNodes}
          edges={flowEdges}
          nodeTypes={nodeTypes}
          edgeTypes={edgeTypes}
          onNodesChange={onNodesChange}
          onEdgesChange={onEdgesChange}
          fitView
          fitViewOptions={{ padding: 0.2 }}
          minZoom={0.15}
          maxZoom={1.5}
          nodesConnectable
          elementsSelectable
          connectionMode={ConnectionMode.Loose}
          connectOnClick={connectOnClick}
          deleteKeyCode={["Backspace", "Delete"]}
          onConnect={onConnect}
          onConnectEnd={onConnectEnd}
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
    </div>
  );
}
