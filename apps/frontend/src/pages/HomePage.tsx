import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { listWorkspaces, type WorkspaceSummary } from "../api";

export function HomePage() {
  const [workspaces, setWorkspaces] = useState<WorkspaceSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    listWorkspaces()
      .then(setWorkspaces)
      .catch((e) => setError(e instanceof Error ? e.message : "Erro ao carregar"))
      .finally(() => setLoading(false));
  }, []);

  const example = workspaces.find((w) => w.is_example);
  const userWorkspaces = workspaces.filter((w) => !w.is_example);

  return (
    <div className="page">
      <header className="page-header">
        <div>
          <h1>RPG-OP</h1>
          <p className="lead">
            Plataforma agnóstica de RPG — cada workspace é uma mesa com ficha customizada.
          </p>
        </div>
        <Link to="/create" className="btn btn-primary">
          Criar workspace
        </Link>
      </header>

      {example && (
        <section className="panel panel-highlight">
          <div className="panel-highlight-header">
            <h2>Workspace de exemplo</h2>
            <span className="badge badge-example">D&D 5e</span>
          </div>
          <p className="muted section-desc">
            Explore a mesa mockada com ficha D&D 5ª edição antes de criar a sua.
          </p>
          <Link to={`/workspace/${example.id}`} className="workspace-card workspace-card-featured">
            <div className="workspace-card-main">
              <strong>{example.name}</strong>
              <span className="muted">Mestre: {example.master_name}</span>
            </div>
            <p>{example.description}</p>
          </Link>
        </section>
      )}

      <section className="panel">
        <h2>Seus workspaces</h2>
        {loading && <p className="muted">Carregando…</p>}
        {error && <p className="error">{error}</p>}
        {!loading && !error && userWorkspaces.length === 0 && (
          <p className="muted">Nenhum workspace criado ainda. Comece pelo botão acima.</p>
        )}
        <ul className="workspace-list">
          {userWorkspaces.map((w) => (
            <li key={w.id}>
              <Link to={`/workspace/${w.id}`} className="workspace-card">
                <div className="workspace-card-main">
                  <strong>{w.name}</strong>
                  <span className="muted">v{w.version}</span>
                </div>
                <p className="workspace-card-meta">
                  Mestre: {w.master_name} · Ficha via {w.sheet_source}
                </p>
                {w.description && <p>{w.description}</p>}
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
