import { useEffect, useState } from "react";
import { Link, useParams } from "react-router-dom";
import { getSheet, updateSheet, type ExampleSheet } from "../api";
import { SheetCanvas } from "../components/SheetCanvas";

export function CharacterSheetPage() {
  const { workspaceId, sheetId } = useParams<{ workspaceId: string; sheetId: string }>();
  const [sheet, setSheet] = useState<ExampleSheet | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sheetId) return;
    const reload = () =>
      getSheet(sheetId)
        .then(setSheet)
        .catch((e) => setError(e instanceof Error ? e.message : "Erro ao carregar ficha"));

    reload().finally(() => setLoading(false));

    const onSession = () => {
      setLoading(true);
      reload().finally(() => setLoading(false));
    };
    window.addEventListener("rpg-op-session", onSession);
    return () => window.removeEventListener("rpg-op-session", onSession);
  }, [sheetId]);

  async function onSave(data: Record<string, string | number>) {
    if (!sheetId) return;
    const updated = await updateSheet(sheetId, data);
    setSheet(updated);
  }

  if (loading) {
    return (
      <div className="page">
        <p className="muted">Carregando ficha…</p>
      </div>
    );
  }

  if (error || !sheet) {
    return (
      <div className="page">
        <p className="error">{error ?? "Ficha não encontrada"}</p>
        {workspaceId && (
          <Link to={`/workspace/${workspaceId}`}>Voltar ao workspace</Link>
        )}
      </div>
    );
  }

  return (
    <div className="page">
      <header className="page-header workspace-header">
        <Link to={`/workspace/${workspaceId}`} className="back-link">
          ← Workspace
        </Link>
        <h1>{sheet.label}</h1>
        {sheet.updated_at && (
          <p className="muted">Última atualização: {new Date(sheet.updated_at).toLocaleString()}</p>
        )}
      </header>
      <SheetCanvas sheet={sheet} editable onSave={onSave} />
    </div>
  );
}
