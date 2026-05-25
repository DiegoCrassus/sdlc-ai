import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  analyzeTemplate,
  createCharacter,
  createInvite,
  extendTemplate,
  getExampleSheet,
  getTemplateAnalysis,
  getWorkspace,
  getWorkspaceDashboard,
  listCharacters,
  listInvites,
  previewRemoveField,
  publishTemplate,
  removeTemplateField,
  type CharacterSummary,
  type ExampleSheet,
  type Invite,
  type TemplateAnalysis,
  type WorkspaceDashboard,
  type WorkspaceDetail,
} from "../api";
import { SheetCanvas } from "../components/SheetCanvas";
import { getSession } from "../session";

export function WorkspacePage() {
  const { id } = useParams<{ id: string }>();
  const [workspace, setWorkspace] = useState<WorkspaceDetail | null>(null);
  const [invites, setInvites] = useState<Invite[]>([]);
  const [exampleSheet, setExampleSheet] = useState<ExampleSheet | null>(null);
  const [templateAnalysis, setTemplateAnalysis] = useState<TemplateAnalysis | null>(null);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<"player" | "gm">("player");
  const [error, setError] = useState<string | null>(null);
  const [inviteError, setInviteError] = useState<string | null>(null);
  const [templateError, setTemplateError] = useState<string | null>(null);
  const [templateBusy, setTemplateBusy] = useState(false);
  const [loading, setLoading] = useState(true);
  const [dashboard, setDashboard] = useState<WorkspaceDashboard | null>(null);
  const [myCharacters, setMyCharacters] = useState<CharacterSummary[]>([]);
  const [charName, setCharName] = useState("");
  const [charEmail, setCharEmail] = useState("");
  const [charError, setCharError] = useState<string | null>(null);
  const [extendLabel, setExtendLabel] = useState("");
  const [extendKey, setExtendKey] = useState("");
  const [extendType, setExtendType] = useState("string");
  const [extendDesc, setExtendDesc] = useState("");
  const [removeKey, setRemoveKey] = useState("");
  const [removeConfirm, setRemoveConfirm] = useState<string | null>(null);

  const session = getSession();
  const isGm = session.role === "gm";

  async function reload(workspaceId: string) {
    const s = getSession();
    const [w, inv, sheet, analysis] = await Promise.all([
      getWorkspace(workspaceId),
      listInvites(workspaceId),
      getExampleSheet(workspaceId),
      getTemplateAnalysis(workspaceId),
    ]);
    setWorkspace(w);
    setInvites(inv);
    setExampleSheet(sheet);
    setTemplateAnalysis(analysis);

    if (s.role === "gm") {
      setDashboard(await getWorkspaceDashboard(workspaceId));
    } else {
      setDashboard(null);
      setMyCharacters(await listCharacters(workspaceId));
    }
  }

  useEffect(() => {
    if (!id) return;
    reload(id)
      .catch((e) => setError(e instanceof Error ? e.message : "Erro ao carregar workspace"))
      .finally(() => setLoading(false));

    const onSession = () => {
      setLoading(true);
      reload(id)
        .catch((e) => setError(e instanceof Error ? e.message : "Erro ao carregar"))
        .finally(() => setLoading(false));
    };
    window.addEventListener("rpg-op-session", onSession);
    return () => window.removeEventListener("rpg-op-session", onSession);
  }, [id]);

  async function onCreateCharacter(e: FormEvent) {
    e.preventDefault();
    if (!id) return;
    setCharError(null);
    try {
      await createCharacter(id, { name: charName, player_email: charEmail });
      setCharName("");
      setCharEmail("");
      await reload(id);
    } catch (err) {
      setCharError(err instanceof Error ? err.message : "Falha ao criar personagem");
    }
  }

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

  async function onAnalyze() {
    if (!id) return;
    setTemplateError(null);
    setTemplateBusy(true);
    try {
      const analysis = await analyzeTemplate(id);
      setTemplateAnalysis(analysis);
      await reload(id);
    } catch (err) {
      setTemplateError(err instanceof Error ? err.message : "Falha na análise");
    } finally {
      setTemplateBusy(false);
    }
  }

  async function onPublish() {
    if (!id) return;
    setTemplateError(null);
    setTemplateBusy(true);
    try {
      await publishTemplate(id);
      await reload(id);
    } catch (err) {
      setTemplateError(err instanceof Error ? err.message : "Falha ao publicar");
    } finally {
      setTemplateBusy(false);
    }
  }

  async function onExtend(e: FormEvent) {
    e.preventDefault();
    if (!id) return;
    setTemplateError(null);
    setTemplateBusy(true);
    try {
      const analysis = await extendTemplate(id, {
        field_key: extendKey || undefined,
        field_label: extendLabel || undefined,
        field_type: extendType,
        description: extendDesc || extendLabel,
        create_region: true,
        region_id: "extensions",
        region_title: "Extensões",
      });
      setTemplateAnalysis(analysis);
      await reload(id);
      setExtendLabel("");
      setExtendKey("");
      setExtendDesc("");
    } catch (err) {
      setTemplateError(err instanceof Error ? err.message : "Falha ao estender template");
    } finally {
      setTemplateBusy(false);
    }
  }

  async function onRemoveField() {
    if (!id || !removeKey) return;
    setTemplateError(null);
    setTemplateBusy(true);
    try {
      const preview = await previewRemoveField(id, removeKey);
      if (preview.needs_confirm && removeConfirm !== removeKey) {
        setRemoveConfirm(removeKey);
        setTemplateError(
          `Campo "${removeKey}" tem dados em ${preview.affected_sheets} ficha(s). Clique remover novamente para confirmar.`
        );
        return;
      }
      await removeTemplateField(id, removeKey, preview.needs_confirm);
      setRemoveConfirm(null);
      setRemoveKey("");
      await reload(id);
    } catch (err) {
      setTemplateError(err instanceof Error ? err.message : "Falha ao remover campo");
    } finally {
      setTemplateBusy(false);
    }
  }

  if (loading) {
    return (
      <div className="page">
        <p className="muted">Carregando workspace…</p>
      </div>
    );
  }

  if (error || !workspace) {
    return (
      <div className="page">
        <p className="error">{error ?? "Workspace não encontrado"}</p>
        <Link to="/">Voltar</Link>
      </div>
    );
  }

  const slotsLeft = workspace.max_members - workspace.invite_count;
  const isDraft = workspace.template_status === "draft";
  const steps = templateAnalysis?.analysis?.steps ?? [];
  const schemaFields = templateAnalysis?.schema_data?.fields ?? {};
  const fieldKeys = Object.keys(schemaFields);

  return (
    <div className="page">
      <header className="page-header workspace-header">
        <div>
          <Link to="/" className="back-link">
            ← Workspaces
          </Link>
          <div className="workspace-title-row">
            <h1>{workspace.name}</h1>
            {workspace.is_example && <span className="badge badge-example">Exemplo D&D 5e</span>}
            {isDraft && <span className="badge badge-draft">Template rascunho</span>}
            {!isDraft && !workspace.is_example && (
              <span className="badge badge-published">Publicado v{workspace.template_version}</span>
            )}
          </div>
          <p className="lead">{workspace.description || "Sem descrição"}</p>
          <div className="workspace-meta">
            <span>Mestre: {workspace.master_name}</span>
            <span>Versão {workspace.version}</span>
            <span>Ficha: {workspace.sheet_source}</span>
            <span>
              Membros: {workspace.invite_count}/{workspace.max_members}
            </span>
          </div>
        </div>
      </header>

      <div className="workspace-grid">
        {isGm && dashboard && (
          <section className="panel panel-wide">
            <div className="dashboard-header">
              <h2>Personagens da mesa</h2>
              <div className="dashboard-stats">
                <span>Template v{dashboard.template_version}</span>
                <span>{dashboard.character_count} personagem(ns)</span>
                {dashboard.incomplete_count > 0 && (
                  <span className="stat-warn">{dashboard.incomplete_count} incompleto(s)</span>
                )}
              </div>
            </div>
            <table className="char-table">
              <thead>
                <tr>
                  <th>Personagem</th>
                  <th>Jogador</th>
                  <th>Rev.</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {dashboard.characters.map((c) => (
                  <tr key={c.id} className={c.incomplete ? "row-incomplete" : ""}>
                    <td>{c.name}</td>
                    <td>{c.player_email}</td>
                    <td>{c.revision ?? "—"}</td>
                    <td>
                      {c.incomplete ? (
                        <span className="badge badge-incomplete">Incompleta</span>
                      ) : (
                        <span className="badge badge-published">OK</span>
                      )}
                    </td>
                    <td>
                      {c.sheet_id && (
                        <Link to={`/workspace/${id}/sheet/${c.sheet_id}`} className="btn btn-ghost btn-sm">
                          Abrir ficha
                        </Link>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
            {!workspace.is_example && workspace.template_status === "published" && (
              <form className="char-create-form" onSubmit={onCreateCharacter}>
                <input
                  required
                  placeholder="Nome do personagem"
                  value={charName}
                  onChange={(e) => setCharName(e.target.value)}
                />
                <input
                  required
                  type="email"
                  placeholder="email@jogador.dev"
                  value={charEmail}
                  onChange={(e) => setCharEmail(e.target.value)}
                />
                <button type="submit" className="btn btn-primary">
                  Adicionar personagem
                </button>
              </form>
            )}
            {charError && <p className="error">{charError}</p>}
          </section>
        )}

        {!isGm && myCharacters.length > 0 && (
          <section className="panel">
            <h2>Minhas fichas</h2>
            <ul className="my-chars-list">
              {myCharacters.map((c) => (
                <li key={c.id}>
                  <div>
                    <strong>{c.name}</strong>
                    {c.incomplete && (
                      <span className="badge badge-incomplete">Incompleta</span>
                    )}
                  </div>
                  {c.sheet_id && (
                    <Link to={`/workspace/${id}/sheet/${c.sheet_id}`} className="btn btn-primary btn-sm">
                      Editar ficha
                    </Link>
                  )}
                </li>
              ))}
            </ul>
          </section>
        )}

        {(isGm || !workspace.is_example) && (
          <section className="panel">
            <h2>Template — DPA Agent</h2>
            <p className="muted section-desc">
              Analise a ficha, revise os passos e publique quando estiver satisfeito.
            </p>
            <div className="template-actions">
              <button
                type="button"
                className="btn btn-ghost"
                disabled={templateBusy}
                onClick={onAnalyze}
              >
                {templateBusy ? "Processando…" : "Reanalisar ficha"}
              </button>
              {isDraft && (
                <button
                  type="button"
                  className="btn btn-primary"
                  disabled={templateBusy}
                  onClick={onPublish}
                >
                  Publicar template v{workspace.template_version + 1}
                </button>
              )}
            </div>
            {templateError && <p className="error">{templateError}</p>}
            {templateAnalysis?.warnings && templateAnalysis.warnings.length > 0 && (
              <ul className="analysis-warnings">
                {templateAnalysis.warnings.map((w) => (
                  <li key={w}>{w}</li>
                ))}
              </ul>
            )}
            {steps.length > 0 && (
              <ol className="analysis-steps">
                {steps.map((step) => (
                  <li key={step.id}>
                    <strong>{step.label}</strong>
                    <p>{step.finding}</p>
                  </li>
                ))}
              </ol>
            )}
          </section>
        )}

        {isGm && (workspace.template_status === "published" || isDraft) && (
          <section className="panel">
            <h2>Estender template</h2>
            <p className="muted section-desc">
              Adicione campos ou seções sem reenviar a ficha original. Preview abaixo; publique para
              aplicar nas fichas existentes.
            </p>
            <form className="extend-form" onSubmit={onExtend}>
              <input
                placeholder="Rótulo do campo (ex: Montaria)"
                value={extendLabel}
                onChange={(e) => setExtendLabel(e.target.value)}
                required
              />
              <input
                placeholder="Chave (opcional, ex: mount)"
                value={extendKey}
                onChange={(e) => setExtendKey(e.target.value)}
              />
              <select value={extendType} onChange={(e) => setExtendType(e.target.value)}>
                <option value="string">Texto curto</option>
                <option value="text">Texto longo</option>
                <option value="integer">Número</option>
              </select>
              <input
                placeholder="Descrição livre (opcional)"
                value={extendDesc}
                onChange={(e) => setExtendDesc(e.target.value)}
              />
              <button type="submit" className="btn btn-primary" disabled={templateBusy}>
                {templateBusy ? "Gerando patch…" : "Adicionar campo"}
              </button>
            </form>
            {fieldKeys.length > 0 && (
              <div className="remove-field-row">
                <select value={removeKey} onChange={(e) => setRemoveKey(e.target.value)}>
                  <option value="">Remover campo…</option>
                  {fieldKeys.map((k) => (
                    <option key={k} value={k}>
                      {schemaFields[k]?.label ?? k}
                    </option>
                  ))}
                </select>
                <button
                  type="button"
                  className="btn btn-ghost"
                  disabled={!removeKey || templateBusy}
                  onClick={onRemoveField}
                >
                  {removeConfirm === removeKey ? "Confirmar remoção" : "Remover"}
                </button>
              </div>
            )}
          </section>
        )}

        <section className="panel">
          <h2>Convidar membros</h2>
          <p className="muted section-desc">
            Envie convites por e-mail. Restam {Math.max(slotsLeft, 0)} vaga(s) neste workspace.
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
          <h2>Ficha de exemplo</h2>
          <p className="muted section-desc">
            {isDraft
              ? "Preview do rascunho — publique o template para fixar a versão."
              : "Canvas do template publicado."}
          </p>
          {exampleSheet && <SheetCanvas sheet={exampleSheet} />}
        </section>
      </div>
    </div>
  );
}
