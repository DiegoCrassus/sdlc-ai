import { sessionHeaders } from "./session";

export interface WorkspaceSummary {
  id: string;
  name: string;
  description: string;
  master_name: string;
  version: string;
  max_members: number;
  sheet_source: "file" | "json" | "text";
  template_status: "draft" | "published";
  template_version: number;
  is_example: boolean;
  template_image_url: string | null;
  created_at: string;
}

export interface WorkspaceDetail extends WorkspaceSummary {
  invite_count: number;
  pending_invites: number;
}

export interface Invite {
  id: string;
  email: string;
  role: string;
  status: string;
  created_at: string;
}

export interface CanvasRegion {
  id: string;
  title: string;
  order: number;
  columns?: number;
  presentation: "field_grid" | "stat_row" | "rich_text";
  fields: string[];
}

export interface CanvasSpec {
  version: number;
  layout: string;
  regions: CanvasRegion[];
  styling?: { density?: string; show_labels?: boolean };
}

export interface SchemaField {
  type: string;
  label: string;
  required?: boolean;
  min?: number;
  max?: number;
}

export interface SheetSchema {
  version: number;
  fields: Record<string, SchemaField>;
}

export interface ExampleSheet {
  label: string;
  schema_data: SheetSchema;
  canvas_spec: CanvasSpec;
  data: Record<string, string | number>;
  template_image_url: string | null;
  editable_fields?: Record<string, boolean>;
  role?: string;
  revision?: number;
  updated_at?: string;
  missing_required?: string[];
}

export interface CharacterSummary {
  id: string;
  name: string;
  player_email: string;
  sheet_id: string | null;
  revision: number | null;
  updated_at: string | null;
  missing_required: string[];
  incomplete: boolean;
}

export interface WorkspaceDashboard {
  workspace_id: string;
  template_status: string;
  template_version: number;
  character_count: number;
  incomplete_count: number;
  characters: CharacterSummary[];
}

export type SheetSource = "file" | "json" | "text";

export interface TemplateAnalysis {
  template_status: string;
  template_version: number;
  published_at: string | null;
  analysis: {
    steps: Array<{ id: string; label: string; finding: string; fields?: unknown[] }>;
    warnings?: string[];
    confidence?: string;
  } | null;
  schema_data: SheetSchema;
  canvas_spec: CanvasSpec;
  warnings: string[];
  confidence: string | null;
  template_image_url: string | null;
}

export interface CreateWorkspaceInput {
  name: string;
  master_name: string;
  description: string;
  version: string;
  max_members: number;
  sheet_source: SheetSource;
  template_image?: File | null;
  sheet_json?: string;
  sheet_text?: string;
}

export interface CreateInviteInput {
  email: string;
  role: "player" | "gm";
}

const API = "/v1";

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    const detail = body.detail;
    if (typeof detail === "string") return detail;
    if (Array.isArray(detail)) {
      return detail
        .map((d) => (typeof d === "string" ? d : (d as { msg?: string }).msg ?? ""))
        .filter(Boolean)
        .join("; ");
    }
    return res.statusText;
  } catch {
    return res.statusText;
  }
}

async function apiFetch(url: string, init?: RequestInit): Promise<Response> {
  const headers = new Headers(init?.headers);
  const session = sessionHeaders();
  Object.entries(session).forEach(([k, v]) => headers.set(k, v));
  return fetch(url, { ...init, headers });
}

export async function listWorkspaces(): Promise<WorkspaceSummary[]> {
  const res = await fetch(`${API}/workspaces`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function createWorkspace(input: CreateWorkspaceInput): Promise<WorkspaceDetail> {
  const form = new FormData();
  form.append("name", input.name);
  form.append("master_name", input.master_name);
  form.append("description", input.description);
  form.append("version", input.version);
  form.append("max_members", String(input.max_members));
  form.append("sheet_source", input.sheet_source);
  form.append("sheet_json", input.sheet_json ?? "");
  form.append("sheet_text", input.sheet_text ?? "");
  if (input.template_image) {
    form.append("template_image", input.template_image);
  }

  const res = await fetch(`${API}/workspaces`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getWorkspace(id: string): Promise<WorkspaceDetail> {
  const res = await fetch(`${API}/workspaces/${id}`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function listInvites(workspaceId: string): Promise<Invite[]> {
  const res = await fetch(`${API}/workspaces/${workspaceId}/invites`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function createInvite(workspaceId: string, input: CreateInviteInput): Promise<Invite> {
  const res = await fetch(`${API}/workspaces/${workspaceId}/invites`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getExampleSheet(workspaceId: string): Promise<ExampleSheet> {
  const res = await fetch(`${API}/workspaces/${workspaceId}/example-sheet`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getTemplateAnalysis(workspaceId: string): Promise<TemplateAnalysis> {
  const res = await fetch(`${API}/workspaces/${workspaceId}/template/analysis`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function analyzeTemplate(workspaceId: string): Promise<TemplateAnalysis> {
  const res = await fetch(`${API}/workspaces/${workspaceId}/template/analyze`, { method: "POST" });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function publishTemplate(workspaceId: string): Promise<TemplateAnalysis> {
  const res = await fetch(`${API}/workspaces/${workspaceId}/template/publish`, { method: "POST" });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export interface TemplateExtendInput {
  description?: string;
  field_key?: string;
  field_label?: string;
  field_type?: string;
  region_id?: string;
  region_title?: string;
  create_region?: boolean;
}

export async function extendTemplate(
  workspaceId: string,
  input: TemplateExtendInput
): Promise<TemplateAnalysis> {
  const res = await apiFetch(`${API}/workspaces/${workspaceId}/template/extend`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export interface RemoveFieldPreview {
  field_key: string;
  affected_sheets: number;
  needs_confirm: boolean;
}

export async function previewRemoveField(
  workspaceId: string,
  fieldKey: string
): Promise<RemoveFieldPreview> {
  const res = await apiFetch(
    `${API}/workspaces/${workspaceId}/template/remove-field/${encodeURIComponent(fieldKey)}/preview`
  );
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function removeTemplateField(
  workspaceId: string,
  fieldKey: string,
  confirm = false
): Promise<TemplateAnalysis> {
  const res = await apiFetch(`${API}/workspaces/${workspaceId}/template/remove-field`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ field_key: fieldKey, confirm }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getWorkspaceDashboard(workspaceId: string): Promise<WorkspaceDashboard> {
  const res = await apiFetch(`${API}/workspaces/${workspaceId}/dashboard`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function listCharacters(workspaceId: string): Promise<CharacterSummary[]> {
  const res = await apiFetch(`${API}/workspaces/${workspaceId}/characters`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function createCharacter(
  workspaceId: string,
  input: { name: string; player_email: string }
): Promise<CharacterSummary> {
  const res = await apiFetch(`${API}/workspaces/${workspaceId}/characters`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getSheet(sheetId: string): Promise<ExampleSheet> {
  const res = await apiFetch(`${API}/sheets/${sheetId}`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function updateSheet(
  sheetId: string,
  data: Record<string, string | number>
): Promise<ExampleSheet> {
  const res = await apiFetch(`${API}/sheets/${sheetId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ data }),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export function modifier(score: number): string {
  const mod = Math.floor((score - 10) / 2);
  return mod >= 0 ? `+${mod}` : String(mod);
}
