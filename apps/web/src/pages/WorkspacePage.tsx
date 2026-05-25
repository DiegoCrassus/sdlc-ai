import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  createInvite,
  getCampaign,
  getExampleSheet,
  getSheet,
  listSheetRevisions,
  listCampaignSheets,
  listInvites,
  publishTemplate,
  updateSheet,
  uploadTemplateSource,
  extendTemplate,
  type CampaignDetail,
  type ExampleSheet,
  type Invite,
  type SheetRevision,
  type SheetDetail,
  type SheetSummary,
  type TemplateAnalysis,
} from "../api";
import { SheetCanvas } from "../components/SheetCanvas";

export function WorkspacePage() {
  const { id } = useParams<{ id: string }>();
  const [campaign, setCampaign] = useState<CampaignDetail | null>(null);
  const [invites, setInvites] = useState<Invite[]>([]);
  const [exampleSheet, setExampleSheet] = useState<ExampleSheet | null>(null);
  const [sheets, setSheets] = useState<SheetSummary[]>([]);
  const [activeSheet, setActiveSheet] = useState<SheetDetail | null>(null);
  const [revisions, setRevisions] = useState<SheetRevision[]>([]);
  const [analysis, setAnalysis] = useState<TemplateAnalysis | null>(null);
  const [templateFile, setTemplateFile] = useState<File | null>(null);
  const [templateStatus, setTemplateStatus] = useState<string | null>(null);
  const [newFieldLabel, setNewFieldLabel] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<"player" | "gm">("player");
  const [error, setError] = useState<string | null>(null);
  const [inviteError, setInviteError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function reload(campaignId: string) {
    const [c, inv, sheet, sheetList] = await Promise.all([
      getCampaign(campaignId),
      listInvites(campaignId),
      getExampleSheet(campaignId),
      listCampaignSheets(campaignId),
    ]);
    setCampaign(c);
    setInvites(inv);
    setExampleSheet(sheet);
    setSheets(sheetList.sheets);
    if (sheetList.sheets[0]) {
      const detail = await getSheet(sheetList.sheets[0].id);
      setActiveSheet(detail);
      setRevisions(await listSheetRevisions(detail.id));
    }
  }

  useEffect(() => {
    if (!id) return;
    reload(id)
      .catch((e) => setError(e instanceof Error ? e.message : "Erro ao carregar workspace"))
      .finally(() => setLoading(false));
  }, [id]);

  async function onInvite(e: FormEvent) {
    e.preventDefault();
    if (!id) return;
    setInviteError(null);
    try {
      await createInvite(id, { email, role });
      setEmail("");
      await reload(id);
    } catch (err) {
      setInviteError(err instanceof Error ? err.message : "Falha ao convidar");
    }
  }

  async function onSaveSheet(data: Record<string, string | number>) {
    if (!activeSheet) return;
    const saved = await updateSheet(activeSheet.id, data);
    setActiveSheet(saved);
    setRevisions(await listSheetRevisions(saved.id));
    if (id) await reload(id);
  }

  async function onSelectSheet(sheetId: string) {
    const detail = await getSheet(sheetId);
    setActiveSheet(detail);
    setRevisions(await listSheetRevisions(sheetId));
  }

  async function onUploadTemplate(e: FormEvent) {
    e.preventDefault();
    if (!id || !templateFile) return;
    setTemplateStatus(null);
    try {
      const result = await uploadTemplateSource(id, templateFile);
      setAnalysis(result);
      setTemplateStatus("Draft analisado. Revise e publique quando estiver pronto.");
    } catch (err) {
      setTemplateStatus(err instanceof Error ? err.message : "Falha ao analisar template");
    }
  }

  async function onPublishTemplate() {
    if (!id) return;
    try {
      await publishTemplate(id);
      setTemplateStatus("Template publicado.");
      await reload(id);
    } catch (err) {
      setTemplateStatus(err instanceof Error ? err.message : "Falha ao publicar template");
    }
  }

  async function onExtendTemplate(e: FormEvent) {
    e.preventDefault();
    if (!id || !newFieldLabel.trim()) return;
    const fieldKey = newFieldLabel
      .trim()
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .replace(/[^a-z0-9]+/g, "_")
      .replace(/^_|_$/g, "");
    try {
      await extendTemplate(id, {
        section_title: "Extensões",
        field_key: fieldKey,
        field_label: newFieldLabel.trim(),
        field_type: "text",
      });
      setNewFieldLabel("");
      setTemplateStatus("Campo append-only adicionado ao template.");
      await reload(id);
    } catch (err) {
      setTemplateStatus(err instanceof Error ? err.message : "Falha ao estender template");
    }
  }

  if (loading) {
    return (
      <div className="page">
        <p className="muted">Carregando workspace…</p>
      </div>
    );
  }

  if (error || !campaign) {
    return (
      <div className="page">
        <p className="error">{error ?? "Sandbox não encontrado"}</p>
        <Link to="/">Voltar</Link>
      </div>
    );
  }

  const slotsLeft = campaign.max_members - campaign.invite_count;

  return (
    <div className="page">
      <header className="page-header workspace-header">
        <div>
          <Link to="/" className="back-link">
            ← Sandboxes
          </Link>
          <h1>{campaign.name}</h1>
          <p className="lead">{campaign.description || "Sem descrição"}</p>
          <div className="workspace-meta">
            <span>Versão {campaign.version}</span>
            <span>
              Membros: {campaign.invite_count}/{campaign.max_members}
            </span>
            {campaign.pending_invites > 0 && (
              <span>{campaign.pending_invites} convite(s) pendente(s)</span>
            )}
          </div>
        </div>
      </header>

      <div className="workspace-grid">
        <section className="panel">
          <h2>Convidar membros</h2>
          <p className="muted section-desc">
            Envie convites por e-mail. Restam {Math.max(slotsLeft, 0)} vaga(s) neste sandbox.
          </p>
          <form className="invite-form" onSubmit={onInvite}>
            <input
              type="email"
              required
              placeholder="email@exemplo.com"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              disabled={slotsLeft <= 0}
            />
            <select value={role} onChange={(e) => setRole(e.target.value as "player" | "gm")}>
              <option value="player">Jogador</option>
              <option value="gm">Mestre</option>
            </select>
            <button type="submit" className="btn btn-primary" disabled={slotsLeft <= 0}>
              Convidar
            </button>
          </form>
          {inviteError && <p className="error">{inviteError}</p>}
          {invites.length > 0 && (
            <ul className="invite-list">
              {invites.map((inv) => (
                <li key={inv.id}>
                  <span>{inv.email}</span>
                  <span className="invite-role">{inv.role}</span>
                  <span className={`invite-status status-${inv.status}`}>{inv.status}</span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="panel panel-wide">
          <h2>Dashboard do mestre</h2>
          <p className="muted section-desc">
            Acompanhe as fichas da campanha, versão do template e campos obrigatórios pendentes.
          </p>
          {sheets.length > 0 && (
            <ul className="sheet-list">
              {sheets.map((sheet) => (
                <li key={sheet.id}>
                  <button type="button" onClick={() => onSelectSheet(sheet.id)}>
                    {sheet.character.name}
                  </button>
                  <span>Template v{sheet.template_version}</span>
                  <span>Rev. {sheet.revision}</span>
                  <span>
                    {sheet.incomplete_fields.length
                      ? `${sheet.incomplete_fields.length} pendente(s)`
                      : "Completa"}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </section>

        <section className="panel panel-wide">
          <h2>Template HITL</h2>
          <p className="muted section-desc">
            Faça upload de um modelo, revise a análise determinística e publique somente após confirmação.
          </p>
          <form className="template-form" onSubmit={onUploadTemplate}>
            <input
              type="file"
              accept="image/*,application/pdf"
              onChange={(event) => setTemplateFile(event.target.files?.[0] ?? null)}
            />
            <button type="submit" className="btn btn-primary" disabled={!templateFile}>
              Analisar
            </button>
            <button
              type="button"
              className="btn btn-ghost"
              onClick={onPublishTemplate}
              disabled={!analysis}
            >
              Publicar draft
            </button>
          </form>
          {templateStatus && <p className="muted">{templateStatus}</p>}
          {analysis && (
            <div className="analysis-box">
              <strong>{analysis.template.name}</strong>
              <span> v{analysis.template.version}</span>
              <ul>
                {analysis.warnings.map((warning) => (
                  <li key={warning}>{warning}</li>
                ))}
              </ul>
            </div>
          )}
          <form className="template-form" onSubmit={onExtendTemplate}>
            <input
              type="text"
              placeholder="Novo campo append-only"
              value={newFieldLabel}
              onChange={(event) => setNewFieldLabel(event.target.value)}
            />
            <button type="submit" className="btn btn-ghost">
              Adicionar campo
            </button>
          </form>
        </section>

        <section className="panel panel-wide">
          <h2>Ficha do jogador</h2>
          <p className="muted section-desc">
            Edite os campos permitidos e salve pelo BFF com validação contra o schema do template.
          </p>
          {activeSheet ? (
            <>
              <SheetCanvas sheet={activeSheet} editable onSave={onSaveSheet} />
              {revisions.length > 0 && (
                <div className="revision-strip">
                  Histórico: {revisions.map((revision) => `rev.${revision.revision}`).join(" · ")}
                </div>
              )}
            </>
          ) : (
            exampleSheet && <SheetCanvas sheet={exampleSheet} />
          )}
        </section>
      </div>
    </div>
  );
}
