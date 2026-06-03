import { Handle, Position, type Node, type NodeProps } from "@xyflow/react";

import { validationStatusColor, type StudioNodeData } from "./mapViewModel";

export function StudioNode({ data, selected }: NodeProps<Node<StudioNodeData>>) {
  const borderColor = validationStatusColor(data.validationStatus);

  return (
    <div
      className={[
        "rounded-lg border-2 bg-surface-card px-3 py-2 shadow-lg transition-shadow",
        selected ? "ring-2 ring-studio-accent/60" : "",
      ].join(" ")}
      style={{ borderColor, minWidth: 180, maxWidth: 220 }}
    >
      <Handle type="target" position={Position.Top} className="!bg-slate-500" />
      <p className="truncate text-xs uppercase tracking-wide text-slate-500">{data.category}</p>
      <p className="mt-0.5 truncate text-sm font-semibold text-white">{data.label}</p>
      <p className="mt-1 truncate font-mono text-[10px] text-slate-400">{data.entityType}</p>
      <Handle type="source" position={Position.Bottom} className="!bg-slate-500" />
    </div>
  );
}
