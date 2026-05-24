import { FormEvent, useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import {
  createInvite,
  getCampaign,
  getExampleSheet,
  listInvites,
  type CampaignDetail,
  type ExampleSheet,
  type Invite,
} from "../api";
import { SheetCanvas } from "../components/SheetCanvas";

export function WorkspacePage() {
  const { id } = useParams<{ id: string }>();
  const [campaign, setCampaign] = useState<CampaignDetail | null>(null);
  const [invites, setInvites] = useState<Invite[]>([]);
  const [exampleSheet, setExampleSheet] = useState<ExampleSheet | null>(null);
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<"player" | "gm">("player");
  const [error, setError] = useState<string | null>(null);
  const [inviteError, setInviteError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  async function reload(campaignId: string) {
    const [c, inv, sheet] = await Promise.all([
      getCampaign(campaignId),
      listInvites(campaignId),
      getExampleSheet(campaignId),
    ]);
    setCampaign(c);
    setInvites(inv);
    setExampleSheet(sheet);
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
          <h2>Ficha de exemplo</h2>
          <p className="muted section-desc">
            Valores mockados para entender o canvas. O agente substituirá isso após analisar o
            modelo enviado.
          </p>
          {exampleSheet && <SheetCanvas sheet={exampleSheet} />}
        </section>
      </div>
    </div>
  );
}
