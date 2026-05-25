"""Resolve field editability from canvas role_overrides."""

from __future__ import annotations

from typing import Any


def readonly_fields_for_role(canvas_spec: dict[str, Any], role: str) -> set[str]:
    overrides = canvas_spec.get("role_overrides") or {}
    role_cfg = overrides.get(role) or {}
    readonly = role_cfg.get("readonly_fields") or []
    return set(readonly)


def field_permissions(
    canvas_spec: dict[str, Any],
    role: str,
    schema_fields: dict[str, Any],
) -> dict[str, bool]:
    readonly = readonly_fields_for_role(canvas_spec, role)
    if role == "gm":
        return {key: True for key in schema_fields}
    return {key: key not in readonly for key in schema_fields}
