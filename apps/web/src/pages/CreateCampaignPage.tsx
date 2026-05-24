import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { createCampaign } from "../api";

export function CreateCampaignPage() {
  const navigate = useNavigate();
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [version, setVersion] = useState("1.0.0");
  const [maxMembers, setMaxMembers] = useState(4);
  const [file, setFile] = useState<File | null>(null);
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
    if (!file) {
      setError("Selecione uma imagem do modelo de ficha (PNG ou JPG).");
      return;
    }
    setError(null);
    setSubmitting(true);
    try {
      const campaign = await createCampaign({
        name,
        description,
        version,
        max_members: maxMembers,
        template_image: file,
      });
      navigate(`/workspace/${campaign.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Falha ao criar sandbox");
    } finally {
      setSubmitting(false);
    }
  }

  return (
    <div className="page page-narrow">
      <header className="page-header">
        <div>
          <h1>Novo sandbox RPG</h1>
          <p className="lead">Descreva a mesa e envie o modelo visual da ficha que vocês usam.</p>
        </div>
      </header>

      <form className="panel form-panel" onSubmit={onSubmit}>
        <label>
          Nome da mesa / campanha
          <input
            required
            value={name}
            onChange={(e) => setName(e.target.value)}
            placeholder="Ex.: Crônicas de Ardenfall"
          />
        </label>

        <label>
          Descrição inicial
          <textarea
            rows={4}
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
            Número máximo de membros
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

        <label>
          Modelo de ficha (PNG ou JPG)
          <input
            type="file"
            accept="image/png,image/jpeg,image/webp,image/gif"
            required
            onChange={(e) => onFileChange(e.target.files?.[0] ?? null)}
          />
        </label>

        {preview && (
          <div className="image-preview">
            <img src={preview} alt="Prévia do modelo" />
          </div>
        )}

        {error && <p className="error">{error}</p>}

        <div className="form-actions">
          <button type="button" className="btn btn-ghost" onClick={() => navigate("/")}>
            Cancelar
          </button>
          <button type="submit" className="btn btn-primary" disabled={submitting}>
            {submitting ? "Criando…" : "Criar sandbox"}
          </button>
        </div>
      </form>
    </div>
  );
}
