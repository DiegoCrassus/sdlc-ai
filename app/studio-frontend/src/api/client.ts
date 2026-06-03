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

export const studioApi = {
  health: () => request<StudioHealth>("/health"),
  readiness: () => request<ReadinessResponse>("/readiness"),
  sessionGate: () => request<SessionGateResponse>("/session/gate"),
  dashboardSummary: () => request<DashboardSummary>("/dashboard/summary"),
};
