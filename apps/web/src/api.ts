export interface CampaignSummary {
  id: string;
  name: string;
  description: string;
  version: string;
  max_members: number;
  template_image_url: string | null;
  created_at: string;
}

export interface CampaignDetail extends CampaignSummary {
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
}

export interface CreateCampaignInput {
  name: string;
  description: string;
  version: string;
  max_members: number;
  template_image: File;
}

export interface CreateInviteInput {
  email: string;
  role: "player" | "gm";
}

const API = "/v1";

async function parseError(res: Response): Promise<string> {
  try {
    const body = await res.json();
    return body.detail ?? res.statusText;
  } catch {
    return res.statusText;
  }
}

export async function listCampaigns(): Promise<CampaignSummary[]> {
  const res = await fetch(`${API}/campaigns`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function createCampaign(input: CreateCampaignInput): Promise<CampaignDetail> {
  const form = new FormData();
  form.append("name", input.name);
  form.append("description", input.description);
  form.append("version", input.version);
  form.append("max_members", String(input.max_members));
  form.append("template_image", input.template_image);

  const res = await fetch(`${API}/campaigns`, { method: "POST", body: form });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getCampaign(id: string): Promise<CampaignDetail> {
  const res = await fetch(`${API}/campaigns/${id}`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function listInvites(campaignId: string): Promise<Invite[]> {
  const res = await fetch(`${API}/campaigns/${campaignId}/invites`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function createInvite(campaignId: string, input: CreateInviteInput): Promise<Invite> {
  const res = await fetch(`${API}/campaigns/${campaignId}/invites`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export async function getExampleSheet(campaignId: string): Promise<ExampleSheet> {
  const res = await fetch(`${API}/campaigns/${campaignId}/example-sheet`);
  if (!res.ok) throw new Error(await parseError(res));
  return res.json();
}

export function modifier(score: number): string {
  const mod = Math.floor((score - 10) / 2);
  return mod >= 0 ? `+${mod}` : String(mod);
}
