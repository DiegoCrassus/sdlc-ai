import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createWorkspace, type SheetSource } from "../api";

const JSON_PLACEHOLDER = `{
  "schema": {
    "version": 1,
    "fields": {
      "character_name": { "type": "string", "label": "Nome", "required": true },
      "level": { "type": "integer", "label": "Nível", "min": 1 }
    }
  },
  "canvas_spec": {
    "version": 1,
    "layout": "regions",
    "regions": [
      {
        "id": "main",
        "title": "Personagem",
        "order": 0,
        "columns": 2,
        "presentation": "field_grid",
        "fields": ["character_name", "level"]
      }
    ]
  }
}`;

export function CreateWorkspacePage() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [masterName, setMasterName] = useState("");
  const [description, setDescription] = useState("");
  const [version, setVersion] = useState("1.0.0");
  const [maxMembers, setMaxMembers] = useState(4);
  const [sheetSource, setSheetSource] = useState<SheetSource>("file");
  const [file, setFile] = useState<File | null>(null);
  const [sheetJson, setSheetJson] = useState("");
  const [sheetText, setSheetText] = useState("");
  const [preview, setPreview] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [submitting, setSubmitting] = useState(false);

  function onFileChange(f: File | null) {
    setFile(f);
    if (preview) URL.revokeObjectURL(preview);
    setPreview(f ? URL.createObjectURL(f) : null);
  }

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);

    if (sheetSource === "file" && !file) {
      setError("Selecione uma imagem da ficha ou use JSON/descrição.");
      return;
    }
    if (sheetSource === "json" && !sheetJson.trim()) {
      setError("Informe o JSON da ficha.");
      return;
    }
    if (sheetSource === "text" && sheetText.trim().length < 10) {
      setError("Descreva a ficha com ao menos 10 caracteres.");
      return;
    }

    setSubmitting(true);
    try {
      const workspace = await createWorkspace({
        name,
        master_name: masterName,
        description,
        version,
        max_members: maxMembers,
        sheet_source: sheetSource,
        template_image: sheetSource === "file" ? file : null,
        sheet_json: sheetSource === "json" ? sheetJson : undefined,
        sheet_text: sheetSource === "text" ? sheetText : undefined,
      });
      navigate(`/workspace/${workspace.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao criar workspace");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page page-narrow">
      <header className="page-header">
        <div>
          <h1>Novo workspace</h1>
          <p className="lead">
            Cada workspace é uma mesa de RPG. Informe o mestre e como é a ficha — o sistema
            provisiona schema e canvas automaticamente.
          </p>
        </div>
      </header>

      <form className="panel form-panel" onSubmit={onSubmit}>
        <label>
          Nome da mesa
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ex.: Crônicas de Ardenfall"
          />
        </label>

        <label>
          Mestre
          <input
            required
            value={masterName}
            onChange={(e) => setMasterName(e.target.value)}
            placeholder="Nome do mestre responsável"
          />
        </label>

        <label>
          Descrição (opcional)
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Premissa, tom, sistema houserule…"
          />
        </label>

        <div className="form-row">
          <label>
            Versão
            <input
              required
              value={version}
              onChange={(e) => setVersion(e.target.value)}
              placeholder="1.0.0"
            />
          </label>
          <label>
            Máx. membros
            <input
              type="number"
              min={1}
              max={20}
              required
              value={maxMembers}
              onChange={(e) => setMaxMembers(Number(e.target.value))}
            />
          </label>
        </div>

        <fieldset className="sheet-source-fieldset">
          <legend>Ficha de RPG (obrigatório)</legend>
          <div className="sheet-source-tabs">
            {(["file", "json", "text"] as SheetSource[]).map((mode) => (
              <button
                key={mode}
                type="button"
                className={`tab-btn ${sheetSource === mode ? "tab-btn-active" : ""}`}
                onClick={() => setSheetSource(mode)}
              >
                {mode === "file" ? "Arquivo" : mode === "json" ? "JSON" : "Descrição"}
              </button>
            ))}
          </div>

          {sheetSource === "file" && (
            <label>
              Imagem da ficha (PNG, JPG ou WEBP)
              <input
                type="file"
                accept="image/png,image/jpeg,image/webp,image/gif"
                onChange={(e) => onFileChange(e.target.files?.[0] ?? null)}
              />
            </label>
          )}

          {sheetSource === "json" && (
            <label>
              JSON da ficha
              <textarea
                rows={12}
                value={sheetJson}
                onChange={(e) => setSheetJson(e.target.value)}
                placeholder={JSON_PLACEHOLDER}
                className="code-input"
              />
            </label>
          )}

          {sheetSource === "text" && (
            <label>
              Descreva a ficha
              <textarea
                rows={6}
                value={sheetText}
                onChange={(e) => setSheetText(e.target.value)}
                placeholder="Ex.: Ficha com nome, classe, nível, seis atributos (FOR/DES/CON/INT/SAB/CAR), CA, PV e anotações livres."
              />
            </label>
          )}
        </fieldset>

        {preview && sheetSource === "file" && (
          <div className="image-preview">
            <img src={preview} alt="Prévia da ficha" />
          </div>
        )}

        {error && <p className="error">{error}</p>}

        <div className="form-actions">
          <button type="button" className="btn btn-ghost" onClick={() => navigate("/")}>
            Cancelar
          </button>
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? "Provisionando…" : "Criar workspace"}
          </button>
        </div>
      </form>
    </div>
  );
}
