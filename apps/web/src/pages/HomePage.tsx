import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listCampaigns, type CampaignSummary } from "../api";

export function HomePage() {
  const [campaigns, setCampaigns] = useState<CampaignSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listCampaigns()
      .then(setCampaigns)
      .catch((e) => setError(e instanceof Error ? e.message : "Erro ao carregar"))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>RPG-OP</h1>
          <p className="lead">Sandboxes de mesa — fichas digitais a partir do modelo do mestre.</p>
        </div>
        <Link to="/create" className="btn btn-primary">
          Criar sandbox RPG
        </Link>
      </header>

      <section className="panel">
        <h2>Seus sandboxes</h2>
        {loading && <p className="muted">Carregando…</p>}
        {error && <p className="error">{error}</p>}
        {!loading && !error && campaigns.length === 0 && (
          <p className="muted">Nenhum sandbox ainda. Crie o primeiro para começar.</p>
        )}
        <ul className="campaign-list">
          {campaigns.map((c) => (
            <li key={c.id}>
              <Link to={`/workspace/${c.id}`} className="campaign-card">
                <div className="campaign-card-main">
                  <strong>{c.name}</strong>
                  <span className="muted">v{c.version}</span>
                </div>
                <p>{c.description || "Sem descrição"}</p>
                <span className="campaign-meta">Até {c.max_members} membros</span>
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
