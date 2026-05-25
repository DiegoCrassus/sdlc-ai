import { useEffect, useState } from "react";
import type { CanvasSpec, ExampleSheet, SchemaField } from "../api";
import { modifier } from "../api";
import "./SheetCanvas.css";

interface Props {
  sheet: ExampleSheet;
  editable?: boolean;
  onSave?: (data: Record<string, string | number>) => Promise<void>;
}

type SheetValue = string | number;

function fieldLabel(schema: Record<string, SchemaField>, key: string): string {
  return schema[key]?.label ?? key;
}

function FieldGrid({
  fields,
  data,
  schema,
  editable,
  onChange,
  columns = 2,
}: {
  fields: string[];
  data: Record<string, SheetValue>;
  schema: Record<string, SchemaField>;
  editable: boolean;
  onChange: (key: string, value: SheetValue) => void;
  columns?: number;
}) {
  return (
    <div className="field-grid" style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}>
      {fields.map((key) => (
        <div key={key} className="field-cell">
          <span className="field-label">{fieldLabel(schema, key)}</span>
          {editable ? (
            <FieldInput fieldKey={key} schema={schema[key]} value={data[key]} onChange={onChange} />
          ) : (
            <span className="field-value">{data[key] ?? "—"}</span>
          )}
        </div>
      ))}
    </div>
  );
}

function StatRow({
  fields,
  data,
  schema,
}: {
  fields: string[];
  data: Record<string, string | number>;
  schema: Record<string, SchemaField>;
}) {
  return (
    <div className="stat-row">
      {fields.map((key) => {
        const value = data[key];
        const num = typeof value === "number" ? value : Number(value);
        const mod = Number.isFinite(num) ? modifier(num) : "";
        return (
          <div key={key} className="stat-cell">
            <span className="stat-abbr">{fieldLabel(schema, key)}</span>
            <span className="stat-score">{value ?? "—"}</span>
            {mod && <span className="stat-mod">{mod}</span>}
          </div>
        );
      })}
    </div>
  );
}

function RichText({
  fieldKey,
  data,
  schema,
  editable,
  onChange,
}: {
  fieldKey: string;
  data: Record<string, SheetValue>;
  schema: Record<string, SchemaField>;
  editable: boolean;
  onChange: (key: string, value: SheetValue) => void;
}) {
  return (
    <div className="rich-text-block">
      <span className="field-label">{fieldLabel(schema, fieldKey)}</span>
      {editable ? (
        <textarea
          value={String(data[fieldKey] ?? "")}
          onChange={(event) => onChange(fieldKey, event.target.value)}
          rows={4}
        />
      ) : (
        <p>{data[fieldKey] ?? "—"}</p>
      )}
    </div>
  );
}

function FieldInput({
  fieldKey,
  schema,
  value,
  onChange,
}: {
  fieldKey: string;
  schema?: SchemaField;
  value: SheetValue | undefined;
  onChange: (key: string, value: SheetValue) => void;
}) {
  const isNumber = schema?.type === "integer" || schema?.type === "float";
  return (
    <input
      className="sheet-input"
      type={isNumber ? "number" : "text"}
      value={value ?? ""}
      onChange={(event) => {
        const next = event.target.value;
        onChange(fieldKey, isNumber ? Number(next) : next);
      }}
    />
  );
}

function RegionBody({
  region,
  schema,
  data,
  editable,
  onChange,
}: {
  region: CanvasSpec["regions"][0];
  schema: Record<string, SchemaField>;
  data: Record<string, SheetValue>;
  editable: boolean;
  onChange: (key: string, value: SheetValue) => void;
}) {
  switch (region.presentation) {
    case "stat_row":
      return <StatRow fields={region.fields} data={data} schema={schema} />;
    case "rich_text":
      return region.fields.map((key) => (
        <RichText
          key={key}
          fieldKey={key}
          data={data}
          schema={schema}
          editable={editable}
          onChange={onChange}
        />
      ));
    default:
      return (
        <FieldGrid
          fields={region.fields}
          data={data}
          schema={schema}
          editable={editable}
          onChange={onChange}
          columns={region.columns ?? 2}
        />
      );
  }
}

export function SheetCanvas({ sheet, editable = false, onSave }: Props) {
  const [draft, setDraft] = useState<Record<string, SheetValue>>(sheet.data);
  const [saving, setSaving] = useState(false);
  const regions = [...sheet.canvas_spec.regions].sort((a, b) => a.order - b.order);
  const schema = sheet.schema_data.fields;

  useEffect(() => {
    setDraft(sheet.data);
  }, [sheet]);

  function onChange(key: string, value: SheetValue) {
    setDraft((current) => ({ ...current, [key]: value }));
  }

  async function save() {
    if (!onSave) return;
    setSaving(true);
    try {
      await onSave(draft);
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="sheet-canvas-wrapper">
      {sheet.template_image_url && (
        <aside className="template-reference">
          <h3>Modelo enviado pelo mestre</h3>
          <img src={sheet.template_image_url} alt="Modelo de ficha" />
          <p className="template-hint">Referência visual — dados mockados ao lado.</p>
        </aside>
      )}
      <article className="sheet-canvas">
        <header className="sheet-canvas-header">
          <div>
            <h2>{sheet.label}</h2>
            <p className="sheet-canvas-sub">
              {editable ? "Ficha editável do jogador" : "Preview com valores de demonstração"}
            </p>
          </div>
          <span className="mock-badge">{editable ? "Editável" : "Mock"}</span>
        </header>
        {regions.map((region) => (
          <section key={region.id} className="canvas-region">
            <h3>{region.title}</h3>
            <RegionBody
              region={region}
              schema={schema}
              data={draft}
              editable={editable}
              onChange={onChange}
            />
          </section>
        ))}
        {editable && (
          <footer className="sheet-actions">
            <button className="btn btn-primary" type="button" onClick={save} disabled={saving}>
              {saving ? "Salvando..." : "Salvar ficha"}
            </button>
          </footer>
        )}
      </article>
    </div>
  );
}
