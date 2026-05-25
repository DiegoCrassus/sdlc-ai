"""Validate sheet data against published template schema."""

from __future__ import annotations

from typing import Any


class SheetValidationError(ValueError):
    def __init__(self, errors: list[str]) -> None:
        super().__init__("; ".join(errors))
        self.errors = errors


def validate_sheet_data(schema: dict[str, Any], data: dict[str, Any]) -> dict[str, Any]:
    fields = schema.get("fields", {})
    if not isinstance(fields, dict):
        raise SheetValidationError(["Schema inválido: fields ausente"])

    errors: list[str] = []
    normalized: dict[str, Any] = {}

    for key, spec in fields.items():
        if not isinstance(spec, dict):
            continue
        raw = data.get(key)
        required = spec.get("required", False)
        ftype = spec.get("type", "string")

        if raw is None or raw == "":
            if required:
                errors.append(f"Campo obrigatório: {spec.get('label', key)}")
            normalized[key] = _default_for_type(ftype, spec)
            continue

        try:
            normalized[key] = _coerce_value(raw, ftype, spec, key, errors)
        except ValueError:
            pass

    return normalized if not errors else (_raise(errors))


def _default_for_type(ftype: str, spec: dict[str, Any]) -> Any:
    if ftype == "integer":
        return spec.get("min", 0)
    if ftype == "boolean":
        return False
    return ""


def _coerce_value(
    raw: Any, ftype: str, spec: dict[str, Any], key: str, errors: list[str]
) -> Any:
    label = spec.get("label", key)
    if ftype == "integer":
        try:
            val = int(raw)
        except (TypeError, ValueError):
            errors.append(f"{label}: valor inteiro inválido")
            return spec.get("min", 0)
        min_v = spec.get("min")
        max_v = spec.get("max")
        if min_v is not None and val < min_v:
            errors.append(f"{label}: mínimo {min_v}")
        if max_v is not None and val > max_v:
            errors.append(f"{label}: máximo {max_v}")
        return val
    if ftype == "boolean":
        if isinstance(raw, bool):
            return raw
        return str(raw).lower() in {"1", "true", "yes", "sim"}
    return str(raw)


def _raise(errors: list[str]) -> dict[str, Any]:
    raise SheetValidationError(errors)


def missing_required_fields(schema: dict[str, Any], data: dict[str, Any]) -> list[str]:
    missing: list[str] = []
    for key, spec in schema.get("fields", {}).items():
        if not isinstance(spec, dict):
            continue
        if not spec.get("required"):
            continue
        val = data.get(key)
        if val is None or val == "":
            missing.append(spec.get("label", key))
    return missing
