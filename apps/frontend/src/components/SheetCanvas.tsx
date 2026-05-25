import { useCallback, useState } from "react";
import type { CanvasSpec, ExampleSheet, SchemaField } from "../api";
import { modifier } from "../api";
import "./SheetCanvas.css";

interface Props {
  sheet: ExampleSheet;
  editable?: boolean;
  onSave?: (data: Record<string, string | number>) => Promise<void>;
}

function fieldLabel(schema: Record<string, SchemaField>, key: string): string {
  return schema[key]?.label ?? key;
}

function isEditable(key: string, editable?: boolean, perms?: Record<string, boolean>): boolean {
  if (!editable) return false;
  if (!perms) return true;
  return perms[key] !== false;
}

function FieldInput({
  fieldKey,
  value,
  schema,
  editable,
  onChange,
}: {
  fieldKey: string;
  value: string | number | undefined;
  schema: Record<string, SchemaField>;
  editable: boolean;
  onChange: (key: string, val: string | number) => void;
}) {
  const spec = schema[fieldKey];
  const ftype = spec?.type ?? "string";

  if (!editable) {
    return <span className="field-value">{value ?? "—"}</span>;
  }

  if (ftype === "integer") {
    return (
      <input
        type="number"
        className="field-input"
        value={value ?? ""}
        min={spec?.min}
        max={spec?.max}
        onChange={(e) => onChange(fieldKey, e.target.value === "" ? 0 : Number(e.target.value))}
      />
    );
  }

  if (ftype === "text") {
    return (
      <textarea
        className="field-input field-textarea"
        rows={4}
        value={String(value ?? "")}
        onChange={(e) => onChange(fieldKey, e.target.value)}
      />
    );
  }

  return (
    <input
      type="text"
      className="field-input"
      value={String(value ?? "")}
      onChange={(e) => onChange(fieldKey, e.target.value)}
    />
  );
}

function FieldGrid({
  fields,
  data,
  schema,
  columns = 2,
  editable,
  editableFields,
  onChange,
}: {
  fields: string[];
  data: Record<string, string | number>;
  schema: Record<string, SchemaField>;
  columns?: number;
  editable?: boolean;
  editableFields?: Record<string, boolean>;
  onChange: (key: string, val: string | number) => void;
}) {
  return (
    <div className="field-grid" style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}>
      {fields.map((key) => {
        const canEdit = isEditable(key, editable, editableFields);
        return (
          <div key={key} className={`field-cell ${canEdit ? "" : "field-readonly"}`}>
            <span className="field-label">{fieldLabel(schema, key)}</span>
            <FieldInput
              fieldKey={key}
              value={data[key]}
              schema={schema}
              editable={canEdit}
              onChange={onChange}
            />
          </div>
        );
      })}
    </div>
  );
}

function StatRow({
  fields,
  data,
  schema,
  editable,
  editableFields,
  onChange,
}: {
  fields: string[];
  data: Record<string, string | number>;
  schema: Record<string, SchemaField>;
  editable?: boolean;
  editableFields?: Record<string, boolean>;
  onChange: (key: string, val: string | number) => void;
}) {
  return (
    <div className="stat-row">
      {fields.map((key) => {
        const value = data[key];
        const num = typeof value === "number" ? value : Number(value);
        const mod = Number.isFinite(num) ? modifier(num) : "";
        const canEdit = isEditable(key, editable, editableFields);
        return (
          <div key={key} className={`stat-cell ${canEdit ? "" : "field-readonly"}`}>
            <span className="stat-abbr">{fieldLabel(schema, key)}</span>
            {canEdit ? (
              <input
                type="number"
                className="field-input stat-input"
                value={value ?? ""}
                onChange={(e) =>
                  onChange(key, e.target.value === "" ? 0 : Number(e.target.value))
                }
              />
            ) : (
              <span className="stat-score">{value ?? "—"}</span>
            )}
            {mod && <span className="stat-mod">{mod}</span>}
          </div>
        );
      })}
    </div>
  );
}

function RegionBody({
  region,
  schema,
  data,
  editable,
  editableFields,
  onChange,
}: {
  region: CanvasSpec["regions"][0];
  schema: Record<string, SchemaField>;
  data: Record<string, string | number>;
  editable?: boolean;
  editableFields?: Record<string, boolean>;
  onChange: (key: string, val: string | number) => void;
}) {
  switch (region.presentation) {
    case "stat_row":
      return (
        <StatRow
          fields={region.fields}
          data={data}
          schema={schema}
          editable={editable}
          editableFields={editableFields}
          onChange={onChange}
        />
      );
    case "rich_text":
      return region.fields.map((key) => (
        <div key={key} className="rich-text-block">
          <span className="field-label">{fieldLabel(schema, key)}</span>
          <FieldInput
            fieldKey={key}
            value={data[key]}
            schema={schema}
            editable={isEditable(key, editable, editableFields)}
            onChange={onChange}
          />
        </div>
      ));
    default:
      return (
        <FieldGrid
          fields={region.fields}
          data={data}
          schema={schema}
          columns={region.columns ?? 2}
          editable={editable}
          editableFields={editableFields}
          onChange={onChange}
        />
      );
  }
}

export function SheetCanvas({ sheet, editable = false, onSave }: Props) {
  const regions = [...sheet.canvas_spec.regions].sort((a, b) => a.order - b.order);
  const schema = sheet.schema_data.fields;
  const [data, setData] = useState(sheet.data);
  const [saving, setSaving] = useState(false);
  const [saveError, setSaveError] = useState<string | null>(null);
  const [dirty, setDirty] = useState(false);

  const onChange = useCallback((key: string, val: string | number) => {
    setData((prev) => ({ ...prev, [key]: val }));
    setDirty(true);
    setSaveError(null);
  }, []);

  async function handleSave() {
    if (!onSave) return;
    setSaving(true);
    setSaveError(null);
    try {
      await onSave(data);
      setDirty(false);
    } catch (e) {
      setSaveError(e instanceof Error ? e.message : "Falha ao salvar");
    } finally {
      setSaving(false);
    }
  }

  const isLive = editable && !!onSave;

  return (
    <div className="sheet-canvas-wrapper">
      {sheet.template_image_url && (
        <aside className="template-reference">
          <h3>Modelo enviado pelo mestre</h3>
          <img src={sheet.template_image_url} alt="Modelo de ficha" />
        </aside>
      )}
      <article className="sheet-canvas">
        <header className="sheet-canvas-header">
          <div>
            <h2>{sheet.label}</h2>
            <p className="sheet-canvas-sub">
              {isLive
                ? `Edição como ${sheet.role === "gm" ? "mestre" : "jogador"}`
                : "Visualização"}
              {sheet.revision != null && ` · rev. ${sheet.revision}`}
            </p>
          </div>
          <div className="sheet-canvas-actions">
            {sheet.missing_required && sheet.missing_required.length > 0 && (
              <span className="badge badge-incomplete">
                {sheet.missing_required.length} campo(s) faltando
              </span>
            )}
            {isLive && (
              <button
                type="button"
                className="btn btn-primary btn-sm"
                disabled={!dirty || saving}
                onClick={handleSave}
              >
                {saving ? "Salvando…" : "Salvar ficha"}
              </button>
            )}
            {!isLive && !editable && <span className="mock-badge">Preview</span>}
          </div>
        </header>
        {saveError && <p className="error sheet-save-error">{saveError}</p>}
        {regions.map((region) => (
          <section key={region.id} className="canvas-region">
            <h3>{region.title}</h3>
            <RegionBody
              region={region}
              schema={schema}
              data={data}
              editable={editable}
              editableFields={sheet.editable_fields}
              onChange={onChange}
            />
          </section>
        ))}
      </article>
    </div>
  );
}
