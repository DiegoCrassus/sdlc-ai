import type { CanvasSpec, ExampleSheet, SchemaField } from "../api";
import { modifier } from "../api";
import "./SheetCanvas.css";

interface Props {
  sheet: ExampleSheet;
}

function fieldLabel(schema: Record<string, SchemaField>, key: string): string {
  return schema[key]?.label ?? key;
}

function FieldGrid({
  fields,
  data,
  schema,
  columns = 2,
}: {
  fields: string[];
  data: Record<string, string | number>;
  schema: Record<string, SchemaField>;
  columns?: number;
}) {
  return (
    <div className="field-grid" style={{ gridTemplateColumns: `repeat(${columns}, minmax(0, 1fr))` }}>
      {fields.map((key) => (
        <div key={key} className="field-cell">
          <span className="field-label">{fieldLabel(schema, key)}</span>
          <span className="field-value">{data[key] ?? "—"}</span>
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
}: {
  fieldKey: string;
  data: Record<string, string | number>;
  schema: Record<string, SchemaField>;
}) {
  return (
    <div className="rich-text-block">
      <span className="field-label">{fieldLabel(schema, fieldKey)}</span>
      <p>{data[fieldKey] ?? "—"}</p>
    </div>
  );
}

function RegionBody({
  region,
  schema,
  data,
}: {
  region: CanvasSpec["regions"][0];
  schema: Record<string, SchemaField>;
  data: Record<string, string | number>;
}) {
  switch (region.presentation) {
    case "stat_row":
      return <StatRow fields={region.fields} data={data} schema={schema} />;
    case "rich_text":
      return region.fields.map((key) => (
        <RichText key={key} fieldKey={key} data={data} schema={schema} />
      ));
    default:
      return (
        <FieldGrid
          fields={region.fields}
          data={data}
          schema={schema}
          columns={region.columns ?? 2}
        />
      );
  }
}

export function SheetCanvas({ sheet }: Props) {
  const regions = [...sheet.canvas_spec.regions].sort((a, b) => a.order - b.order);
  const schema = sheet.schema_data.fields;

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
            <p className="sheet-canvas-sub">Preview com valores de demonstração</p>
          </div>
          <span className="mock-badge">Mock</span>
        </header>
        {regions.map((region) => (
          <section key={region.id} className="canvas-region">
            <h3>{region.title}</h3>
            <RegionBody region={region} schema={schema} data={sheet.data} />
          </section>
        ))}
      </article>
    </div>
  );
}
