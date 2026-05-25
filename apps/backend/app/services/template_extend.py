"""Append-only template extensions and controlled field removal."""

from __future__ import annotations

import re
import uuid
from typing import Any

from app.services.provisioning import empty_defaults


class TemplateExtendError(ValueError):
    def __init__(self, message: str, *, needs_confirm: bool = False) -> None:
        super().__init__(message)
        self.needs_confirm = needs_confirm


def slugify_key(label: str) -> str:
    key = re.sub(r"[^a-zA-Z0-9]+", "_", label.strip().lower()).strip("_")
    return key or f"field_{uuid.uuid4().hex[:8]}"


def extend_template(
    schema: dict[str, Any],
    canvas: dict[str, Any],
    *,
    field_key: str,
    field_label: str,
    field_type: str = "string",
    region_id: str | None = None,
    region_title: str | None = None,
    create_region: bool = False,
    description: str = "",
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Return updated schema, canvas, and patch metadata (append-only)."""
    fields = dict(schema.get("fields") or {})
    key = slugify_key(field_key) if not re.match(r"^[a-z][a-z0-9_]*$", field_key) else field_key

    if key in fields:
        raise TemplateExtendError(f"Campo '{key}' já existe no template.")

    field_spec: dict[str, Any] = {"type": field_type, "label": field_label}
    if field_type == "integer":
        field_spec["min"] = 0

    fields[key] = field_spec
    new_schema = {**schema, "version": schema.get("version", 1), "fields": fields}

    regions = [dict(r) for r in canvas.get("regions") or []]
    target_region_id = region_id or "extensions"

    if create_region or not any(r.get("id") == target_region_id for r in regions):
        title = region_title or "Extensões"
        regions.append(
            {
                "id": target_region_id,
                "title": title,
                "order": max((r.get("order", 0) for r in regions), default=-1) + 1,
                "columns": 2,
                "presentation": "field_grid",
                "fields": [key],
            }
        )
    else:
        for region in regions:
            if region.get("id") == target_region_id:
                region_fields = list(region.get("fields") or [])
                if key not in region_fields:
                    region_fields.append(key)
                region["fields"] = region_fields
                break

    new_canvas = {**canvas, "version": canvas.get("version", 1), "regions": regions}

    patch = {
        "action": "append_field",
        "field_key": key,
        "field_label": field_label,
        "field_type": field_type,
        "region_id": target_region_id,
        "description": description,
    }
    return new_schema, new_canvas, patch


def extend_from_description(
    schema: dict[str, Any],
    canvas: dict[str, Any],
    description: str,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    """Parse simple natural-language extend requests."""
    text = description.strip()
    if len(text) < 3:
        raise TemplateExtendError("Descreva o campo ou seção a adicionar.")

    # Patterns: "campo Montaria string", "seção Recursos com campo guilda_rank integer"
    field_match = re.search(
        r"(?:campo|field)\s+([a-zA-Z0-9_\s]+?)(?:\s+(string|integer|text|boolean))?$",
        text,
        re.I,
    )
    section_match = re.search(
        r"(?:seção|secao|section)\s+([a-zA-Z0-9_\s]+?)(?:\s+com\s+campo\s+([a-zA-Z0-9_\s]+?)(?:\s+(string|integer|text))?)?$",
        text,
        re.I,
    )

    if section_match:
        section_title = section_match.group(1).strip()
        field_name = (section_match.group(2) or section_title).strip()
        ftype = (section_match.group(3) or "string").lower()
        region_id = slugify_key(section_title)
        return extend_template(
            schema,
            canvas,
            field_key=slugify_key(field_name),
            field_label=field_name.replace("_", " ").title(),
            field_type=ftype,
            region_id=region_id,
            region_title=section_title,
            create_region=True,
            description=text,
        )

    if field_match:
        label = field_match.group(1).strip()
        ftype = (field_match.group(2) or "string").lower()
        return extend_template(
            schema,
            canvas,
            field_key=slugify_key(label),
            field_label=label,
            field_type=ftype,
            region_id="extensions",
            region_title="Extensões",
            create_region=not any(r.get("id") == "extensions" for r in canvas.get("regions") or []),
            description=text,
        )

    # Fallback: use whole description as label
    return extend_template(
        schema,
        canvas,
        field_key=slugify_key(text[:40]),
        field_label=text[:80],
        field_type="string",
        region_id="extensions",
        region_title="Extensões",
        create_region=not any(r.get("id") == "extensions" for r in canvas.get("regions") or []),
        description=text,
    )


def field_has_data(data: dict[str, Any], field_key: str) -> bool:
    val = data.get(field_key)
    if val is None:
        return False
    if val == "" or val == 0:
        return False
    return True


def remove_field(
    schema: dict[str, Any],
    canvas: dict[str, Any],
    field_key: str,
    all_sheet_data: list[dict[str, Any]],
    *,
    confirm: bool = False,
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    fields = dict(schema.get("fields") or {})
    if field_key not in fields:
        raise TemplateExtendError(f"Campo '{field_key}' não existe.")

    affected = sum(1 for data in all_sheet_data if field_has_data(data, field_key))
    if affected > 0 and not confirm:
        raise TemplateExtendError(
            f"Campo '{field_key}' possui dados em {affected} ficha(s). "
            "Envie confirm=true para remover.",
            needs_confirm=True,
        )

    del fields[field_key]
    new_schema = {**schema, "fields": fields}

    regions = []
    for region in canvas.get("regions") or []:
        region = dict(region)
        region["fields"] = [f for f in region.get("fields") or [] if f != field_key]
        if region["fields"]:
            regions.append(region)
    new_canvas = {**canvas, "regions": regions}

    patch = {"action": "remove_field", "field_key": field_key, "affected_sheets": affected}
    return new_schema, new_canvas, patch


def merge_new_fields_into_sheet(
    sheet_data: dict[str, Any],
    schema: dict[str, Any],
    previous_field_keys: set[str],
) -> dict[str, Any]:
    current_keys = set((schema.get("fields") or {}).keys())
    new_keys = current_keys - previous_field_keys
    if not new_keys:
        return sheet_data

    partial_schema = {"fields": {k: schema["fields"][k] for k in new_keys}}
    defaults = empty_defaults(partial_schema)
    merged = dict(sheet_data)
    for key in new_keys:
        if key not in merged or merged[key] in ("", None):
            merged[key] = defaults.get(key, "")
    return merged
