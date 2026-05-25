"""DPA Agent — template analysis (MVP2 stub; LLM integration in follow-up)."""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, Field

from app.fixtures.default_template import DEFAULT_CANVAS_SPEC, DEFAULT_SCHEMA
from app.services.provisioning import provision_from_json, provision_from_text


class AnalysisStep(BaseModel):
    id: str
    label: str
    finding: str
    fields: list[dict[str, Any]] = Field(default_factory=list)


class TemplateAnalysisResult(BaseModel):
    steps: list[AnalysisStep]
    sheet_schema: dict[str, Any]
    canvas_spec: dict[str, Any]
    warnings: list[str] = Field(default_factory=list)
    confidence: Literal["high", "medium", "low"] = "medium"


def analyze_template(
    *,
    sheet_source: str,
    sheet_input_raw: str | None,
    has_image: bool,
) -> TemplateAnalysisResult:
    """Deterministic analysis stub until LLM multimodal is wired."""
    warnings: list[str] = []

    if sheet_source == "json" and sheet_input_raw:
        schema, canvas, _ = provision_from_json(sheet_input_raw)
        steps = [
            AnalysisStep(
                id="step-1",
                label="Validar JSON estruturado",
                finding="Schema e canvas fornecidos pelo mestre via JSON.",
            ),
            AnalysisStep(
                id="step-2",
                label="Confirmar campos",
                finding=f"Detectados {len(schema.get('fields', {}))} campos no schema.",
                fields=[{"key": k, **v} for k, v in schema.get("fields", {}).items()],
            ),
        ]
        confidence: Literal["high", "medium", "low"] = "high"
    elif sheet_source == "text" and sheet_input_raw:
        schema, canvas, _ = provision_from_text(sheet_input_raw)
        steps = [
            AnalysisStep(
                id="step-1",
                label="Interpretar descrição textual",
                finding="Descrição recebida; template provisório D&D 5e aplicado como base.",
            ),
            AnalysisStep(
                id="step-2",
                label="Mapear campos sugeridos",
                finding=f"{len(schema.get('fields', {}))} campos inferidos a partir da descrição.",
            ),
        ]
        warnings.append("Análise textual usa heurística MVP2; revise campos antes de publicar.")
        confidence = "medium"
    elif has_image or sheet_source == "file":
        schema = DEFAULT_SCHEMA
        canvas = DEFAULT_CANVAS_SPEC
        steps = [
            AnalysisStep(
                id="step-1",
                label="Identificar regiões da ficha",
                finding="Cabeçalho, bloco de atributos, combate e anotações detectados (heurística).",
            ),
            AnalysisStep(
                id="step-2",
                label="Extrair campos visíveis",
                finding=f"{len(schema.get('fields', {}))} campos mapeados no layout D&D 5e de referência.",
                fields=[{"key": k, **v} for k, v in schema.get("fields", {}).items()],
            ),
            AnalysisStep(
                id="step-3",
                label="Montar canvas_spec",
                finding=f"{len(canvas.get('regions', []))} regiões propostas para apresentação.",
            ),
        ]
        warnings.append(
            "Análise de imagem usa fixture D&D 5e até integração multimodal do DPA Agent."
        )
        confidence = "low" if has_image else "medium"
    else:
        schema = DEFAULT_SCHEMA
        canvas = DEFAULT_CANVAS_SPEC
        steps = [
            AnalysisStep(
                id="step-1",
                label="Template padrão",
                finding="Nenhuma ficha fonte encontrada; aplicado template D&D 5e de referência.",
            )
        ]
        warnings.append("Envie uma ficha (imagem/PDF) antes de publicar.")
        confidence = "low"

    return TemplateAnalysisResult(
        steps=steps,
        sheet_schema=schema,
        canvas_spec=canvas,
        warnings=warnings,
        confidence=confidence,
    )


class ExtendStep(BaseModel):
    id: str
    label: str
    finding: str
    patch: dict[str, Any] = Field(default_factory=dict)


def extend_template_analysis(
    schema: dict[str, Any],
    canvas: dict[str, Any],
    patch: dict[str, Any],
    *,
    description: str = "",
) -> TemplateAnalysisResult:
    """Build analysis result for extend mode without re-running full analysis."""
    action = patch.get("action", "append_field")
    field_key = patch.get("field_key", "")
    steps = [
        AnalysisStep(
            id="extend-1",
            label="Modo extend — patch append-only",
            finding=f"Ação: {action}. Campo alvo: {field_key or '—'}.",
            fields=[{"key": field_key, **(schema.get("fields", {}).get(field_key, {}))}]
            if field_key
            else [],
        ),
        AnalysisStep(
            id="extend-2",
            label="Preview do canvas",
            finding=f"{len(canvas.get('regions', []))} regiões após extensão.",
        ),
    ]
    if description:
        steps.insert(
            0,
            AnalysisStep(
                id="extend-0",
                label="Pedido do mestre",
                finding=description[:500],
            ),
        )

    existing = schema.get("fields") or {}
    warnings: list[str] = [
        "Extensão em rascunho — publique para aplicar defaults nas fichas existentes."
    ]
    confidence: Literal["high", "medium", "low"] = "high" if field_key in existing else "medium"

    return TemplateAnalysisResult(
        steps=steps,
        sheet_schema=schema,
        canvas_spec=canvas,
        warnings=warnings,
        confidence=confidence,
    )
