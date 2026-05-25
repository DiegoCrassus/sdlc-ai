"""Derive sheet schema, canvas spec and mock data from workspace ficha input."""

import json
from typing import Any

from fastapi import HTTPException

from app.fixtures.default_template import DEFAULT_CANVAS_SPEC, DEFAULT_SCHEMA, MOCK_SHEET_DATA


def _empty_defaults(schema: dict[str, Any]) -> dict[str, Any]:
    data: dict[str, Any] = {}
    for key, field in schema.get("fields", {}).items():
        ftype = field.get("type", "string")
        if ftype == "integer":
            data[key] = field.get("min", 0)
        elif ftype == "boolean":
            data[key] = False
        else:
            data[key] = ""
    return data


def empty_defaults(schema: dict[str, Any]) -> dict[str, Any]:
    return _empty_defaults(schema)


def _canvas_from_schema(schema: dict[str, Any]) -> dict[str, Any]:
    fields = list(schema.get("fields", {}).keys())
    if not fields:
        raise HTTPException(status_code=400, detail="Schema JSON precisa conter ao menos um campo.")

    header_fields = fields[: min(4, len(fields))]
    remaining = fields[len(header_fields) :]

    regions: list[dict[str, Any]] = [
        {
            "id": "main",
            "title": "Campos",
            "order": 0,
            "columns": 2,
            "presentation": "field_grid",
            "fields": header_fields,
        }
    ]
    if remaining:
        regions.append(
            {
                "id": "extra",
                "title": "Demais campos",
                "order": 1,
                "columns": 2,
                "presentation": "field_grid",
                "fields": remaining,
            }
        )

    return {
        "version": schema.get("version", 1),
        "layout": "regions",
        "regions": regions,
        "styling": {"density": "compact", "show_labels": True},
        "role_overrides": {
            "player": {"readonly_fields": []},
            "gm": {"readonly_fields": []},
        },
    }


def provision_from_json(sheet_json: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    try:
        payload = json.loads(sheet_json)
    except json.JSONDecodeError as exc:
        raise HTTPException(status_code=400, detail=f"JSON inválido: {exc.msg}") from exc

    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="JSON da ficha deve ser um objeto.")

    if "schema" in payload and "canvas_spec" in payload:
        schema = payload["schema"]
        canvas = payload["canvas_spec"]
        data = payload.get("data") or _empty_defaults(schema)
    elif "fields" in payload:
        schema = payload
        canvas = _canvas_from_schema(schema)
        data = _empty_defaults(schema)
    else:
        raise HTTPException(
            status_code=400,
            detail=("JSON deve conter 'schema' + 'canvas_spec', ou um objeto schema com 'fields'."),
        )

    if not isinstance(schema, dict) or "fields" not in schema:
        raise HTTPException(status_code=400, detail="Schema inválido: falta 'fields'.")

    return schema, canvas, data


def provision_from_text(sheet_text: str) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    text = sheet_text.strip()
    if len(text) < 10:
        raise HTTPException(
            status_code=400,
            detail="Descreva a ficha com ao menos 10 caracteres.",
        )
    return DEFAULT_SCHEMA, DEFAULT_CANVAS_SPEC, MOCK_SHEET_DATA


def provision_from_file() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return DEFAULT_SCHEMA, DEFAULT_CANVAS_SPEC, MOCK_SHEET_DATA


def provision_dnd5e_example() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return DEFAULT_SCHEMA, DEFAULT_CANVAS_SPEC, MOCK_SHEET_DATA
