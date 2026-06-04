import { BaseEdge, getSmoothStepPath, type EdgeProps } from "@xyflow/react";

export function TransitionEdge({
  id,
  sourceX,
  sourceY,
  targetX,
  targetY,
  sourcePosition,
  targetPosition,
  style,
  markerEnd,
  selected,
}: EdgeProps) {
  const [edgePath] = getSmoothStepPath({
    sourceX,
    sourceY,
    targetX,
    targetY,
    sourcePosition,
    targetPosition,
  });

  return (
    <g data-testid="transition-edge" data-edge-id={id} className={selected ? "selected" : undefined}>
      <BaseEdge path={edgePath} markerEnd={markerEnd} style={style} interactionWidth={20} />
    </g>
  );
}
