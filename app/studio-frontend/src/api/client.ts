import type {
  CanvasFilterParams,
  CanvasFullResponse,
  CanvasNodeDetailResponse,
} from "../types/canvas";
import type {
  DashboardSummary,
  ReadinessResponse,
  SessionGateResponse,
  StudioHealth,
} from "../types/studio";

/** Browser dev uses Vite proxy (`/studio`); override for direct API access. */
export function studioApiBase(): string {
  const configured = import.meta.env.VITE_STUDIO_API_URL?.replace(/\/$/, "");
  if (configured) {
    return `${configured}/studio`;
  }
  return "/studio";
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${studioApiBase()}${path}`, init);
  if (!response.ok) {
    const detail = await response.text().catch(() => "");
    throw new Error(
      `Studio API ${response.status}: ${response.statusText}${detail ? ` — ${detail.slice(0, 120)}` : ""}`,
    );
  }
  return response.json() as Promise<T>;
}

function canvasQueryString(filters: CanvasFilterParams = {}): string {
  const params = new URLSearchParams();
  if (filters.section) params.set("section", filters.section);
  if (filters.validation_status) params.set("validation_status", filters.validation_status);
  if (filters.entity_type) params.set("entity_type", filters.entity_type);
  if (filters.q) params.set("q", filters.q);
  const qs = params.toString();
  return qs ? `?${qs}` : "";
}

export const studioApi = {
  health: () => request<StudioHealth>("/health"),
  readiness: () => request<ReadinessResponse>("/readiness"),
  sessionGate: () => request<SessionGateResponse>("/session/gate"),
  dashboardSummary: () => request<DashboardSummary>("/dashboard/summary"),
  canvasFull: (filters?: CanvasFilterParams) =>
    request<CanvasFullResponse>(`/canvas/full${canvasQueryString(filters)}`),
  canvasNode: (displayId: string) =>
    request<CanvasNodeDetailResponse>(`/canvas/nodes/${encodeURIComponent(displayId)}`),
};
