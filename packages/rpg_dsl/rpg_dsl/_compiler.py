"""Compiler — emits artefacts from registered specs."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

from ._models import ApiSpec, CanvasSpec, EvalSpec, FieldSpec, RouteSpec, SheetSpec, SubAgentSpec
from ._registry import get_all

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_PY_TYPES: dict[str, str] = {
    "string": "str",
    "integer": "int",
    "float": "float",
    "boolean": "bool",
    "text": "str",
}

_JSON_TYPES: dict[str, dict[str, str]] = {
    "string": {"type": "string"},
    "integer": {"type": "integer"},
    "float": {"type": "number"},
    "boolean": {"type": "boolean"},
    "text": {"type": "string"},
}

_TS_TYPES: dict[str, str] = {
    "string": "string",
    "integer": "number",
    "float": "number",
    "boolean": "boolean",
    "text": "string",
}


def _py_type(field: FieldSpec) -> str:
    base = _PY_TYPES.get(field.type, "Any")
    if not field.required:
        return f"{base} | None"
    return base


def _default_expr(field: FieldSpec) -> str:
    if field.required:
        return f'Field(..., title="{field.label}")'
    if field.default is not None:
        d = repr(field.default)
        return f'Field({d}, title="{field.label}")'
    return f'Field(None, title="{field.label}")'


# ---------------------------------------------------------------------------
# Target: pydantic
# ---------------------------------------------------------------------------


def emit_pydantic(out_dir: Path) -> list[Path]:
    sheets: list[SheetSpec] = get_all("sheet")
    if not sheets:
        return []

    target = out_dir / "pydantic" / "sheets"
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for spec in sheets:
        class_name = spec.source_class.__name__ if spec.source_class else spec.name
        snake = _to_snake(class_name)
        file_path = target / f"{snake}_v{spec.version}.py"

        imports = {"from pydantic import BaseModel, Field"}
        if any(_py_type(f) == "Any" for f in spec.fields):
            imports.add("from typing import Any")

        field_lines: list[str] = []
        for f in spec.fields:
            py_type = _py_type(f)
            default = _default_expr(f)
            field_lines.append(f"    {f.key}: {py_type} = {default}")

        body = "\n".join(field_lines) or "    pass"
        content = "\n".join(sorted(imports)) + "\n\n\n"
        content += f"class {class_name}V{spec.version}(BaseModel):\n{body}\n"

        file_path.write_text(content, encoding="utf-8")
        written.append(file_path)

    return written


# ---------------------------------------------------------------------------
# Target: jsonschema
# ---------------------------------------------------------------------------


def emit_jsonschema(out_dir: Path) -> list[Path]:
    sheets: list[SheetSpec] = get_all("sheet")
    if not sheets:
        return []

    target = out_dir / "schemas"
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    for spec in sheets:
        class_name = spec.source_class.__name__ if spec.source_class else spec.name
        snake = _to_snake(class_name)
        file_path = target / f"{snake}_v{spec.version}.json"

        properties: dict[str, Any] = {}
        required_keys: list[str] = []
        for f in spec.fields:
            prop: dict[str, Any] = {"title": f.label}
            if f.type in ("string", "text"):
                prop["type"] = "string"
            elif f.type == "integer":
                prop["type"] = "integer"
                if f.min is not None:
                    prop["minimum"] = f.min
                if f.max is not None:
                    prop["maximum"] = f.max
            elif f.type == "float":
                prop["type"] = "number"
            elif f.type == "boolean":
                prop["type"] = "boolean"
            properties[f.key] = prop
            if f.required:
                required_keys.append(f.key)

        schema: dict[str, Any] = {
            "$schema": "https://json-schema.org/draft/2020-12/schema",
            "title": class_name,
            "version": spec.version,
            "type": "object",
            "properties": properties,
        }
        if required_keys:
            schema["required"] = required_keys

        file_path.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(file_path)

    return written


# ---------------------------------------------------------------------------
# Target: typescript
# ---------------------------------------------------------------------------


def emit_typescript(out_dir: Path) -> list[Path]:
    sheets: list[SheetSpec] = get_all("sheet")
    canvases: list[CanvasSpec] = get_all("canvas")
    apis: list[ApiSpec] = get_all("api")
    if not sheets and not canvases and not apis:
        return []

    target = out_dir / "typescript"
    target.mkdir(parents=True, exist_ok=True)
    file_path = target / "api.ts"

    lines: list[str] = [
        "/* Auto-generated from specs/. Do not edit manually. */",
        "",
    ]

    for spec in sheets:
        class_name = spec.source_class.__name__ if spec.source_class else spec.name
        interface_name = f"{class_name}V{spec.version}"
        lines.append(f"export interface {interface_name} {{")
        for field in spec.fields:
            optional = "" if field.required else "?"
            lines.append(f"  {field.key}{optional}: {_ts_type(field)};")
        lines.append("}")
        lines.append("")

    if canvases:
        lines.extend(
            [
                'export type PresentationType = "field_grid" | "stat_row" | "rich_text";',
                "",
                "export interface CanvasRegion {",
                "  id: string;",
                "  title: string;",
                "  order: number;",
                "  presentation: PresentationType;",
                "  fields: string[];",
                "  columns: number;",
                "}",
                "",
                "export interface CanvasSpec {",
                "  name: string;",
                "  version: number;",
                "  regions: CanvasRegion[];",
                "}",
                "",
            ]
        )
        for canvas in canvases:
            const_name = _to_const_name(canvas.name)
            payload = {
                "name": canvas.name,
                "version": canvas.version,
                "regions": [
                    {
                        "id": region.id,
                        "title": region.title,
                        "order": region.order,
                        "presentation": region.presentation.value,
                        "fields": region.fields,
                        "columns": region.columns,
                    }
                    for region in canvas.regions
                ],
            }
            lines.append(
                f"export const {const_name}: CanvasSpec = {json.dumps(payload, indent=2, ensure_ascii=False)};"
            )
            lines.append("")

    for api in apis:
        const_name = _to_const_name(
            f"{api.source_class.__name__ if api.source_class else api.tag}Routes"
        )
        route_payload = [
            {
                "method": route.method,
                "path": f"{api.prefix}{route.path}",
                "tag": api.tag,
                "response": route.response,
                "body": route.body,
                "stream": route.stream,
            }
            for route in api.routes
        ]
        lines.append(
            f"export const {const_name} = {json.dumps(route_payload, indent=2, ensure_ascii=False)} as const;"
        )
        lines.append("")

    file_path.write_text("\n".join(lines), encoding="utf-8")
    return [file_path]


# ---------------------------------------------------------------------------
# Target: openapi
# ---------------------------------------------------------------------------


def emit_openapi(out_dir: Path) -> list[Path]:
    apis: list[ApiSpec] = get_all("api")
    sheets: list[SheetSpec] = get_all("sheet")
    if not apis:
        return []

    target = out_dir / "openapi"
    target.mkdir(parents=True, exist_ok=True)
    file_path = target / "bff_v1.yaml"

    components: dict[str, Any] = {"schemas": {}}
    for spec in sheets:
        class_name = spec.source_class.__name__ if spec.source_class else spec.name
        components["schemas"][f"{class_name}V{spec.version}"] = _sheet_json_schema(spec, class_name)

    route_dtos = {route.response for api in apis for route in api.routes if route.response} | {
        route.body for api in apis for route in api.routes if route.body
    }
    for dto in sorted(route_dtos):
        components["schemas"].setdefault(dto, _placeholder_schema(dto))

    paths: dict[str, Any] = {}
    for api in apis:
        for route in api.routes:
            full_path = f"{api.prefix}{route.path}"
            path_item = paths.setdefault(full_path, {})
            operation: dict[str, Any] = {
                "tags": [api.tag],
                "operationId": _operation_id(route),
                "responses": {
                    "200": {
                        "description": "Successful response",
                    }
                },
            }
            parameters = _path_parameters(full_path)
            if parameters:
                operation["parameters"] = parameters
            if route.response:
                operation["responses"]["200"]["content"] = {
                    "application/json": {
                        "schema": {"$ref": f"#/components/schemas/{route.response}"}
                    }
                }
            if route.body:
                operation["requestBody"] = {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {"$ref": f"#/components/schemas/{route.body}"}
                        }
                    },
                }
            if route.stream:
                operation["x-streaming"] = True
            path_item[route.method.lower()] = operation

    document = {
        "openapi": "3.1.0",
        "info": {
            "title": "RPG-OP BFF API",
            "version": "1.0.0",
        },
        "paths": paths,
        "components": components,
    }
    file_path.write_text(json.dumps(document, indent=2, ensure_ascii=False), encoding="utf-8")
    return [file_path]


# ---------------------------------------------------------------------------
# Target: agent_manifest
# ---------------------------------------------------------------------------


def emit_agent_manifest(out_dir: Path) -> list[Path]:
    subagents: list[SubAgentSpec] = get_all("subagent")
    canvases: list[CanvasSpec] = get_all("canvas")
    sheets: list[SheetSpec] = get_all("sheet")

    target = out_dir / "agent_manifest"
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    manifest: dict[str, Any] = {
        "version": 1,
        "subagents": [
            {
                "name": s.name,
                "response_model": s.response_model,
                "skills": s.skills,
            }
            for s in subagents
        ],
        "canvas_specs": [c.name for c in canvases],
        "sheet_specs": [f"{s.name}_v{s.version}" for s in sheets],
    }

    manifest_path = target / "orchestrator.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    written.append(manifest_path)

    permissions: dict[str, Any] = {
        "allow": ["specs/**", "backend/**", "apps/**", "services/**"],
        "deny": ["generated/**"],
    }
    perms_path = target / "permissions.json"
    perms_path.write_text(json.dumps(permissions, indent=2, ensure_ascii=False), encoding="utf-8")
    written.append(perms_path)

    return written


# ---------------------------------------------------------------------------
# Target: evals
# ---------------------------------------------------------------------------


def emit_evals(out_dir: Path) -> list[Path]:
    evals: list[EvalSpec] = get_all("eval")
    if not evals:
        return []

    target = out_dir / "evals"
    target.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []

    by_suite: dict[str, list[dict]] = {}
    for spec in evals:
        entry = {
            "name": spec.source_class.__name__ if spec.source_class else spec.suite,
            "fixture": spec.fixture,
            "user_message": spec.user_message,
            "assertions": [{"type": a.type, "value": a.value} for a in spec.assertions],
        }
        by_suite.setdefault(spec.suite, []).append(entry)

    for suite_name, cases in by_suite.items():
        snake = suite_name.replace("-", "_")
        file_path = target / f"{snake}.json"
        payload = {"suite": suite_name, "cases": cases}
        file_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        written.append(file_path)

    return written


# ---------------------------------------------------------------------------
# Target: registry
# ---------------------------------------------------------------------------


def emit_registry(out_dir: Path) -> list[Path]:
    target = out_dir / "registry"
    target.mkdir(parents=True, exist_ok=True)

    sheets: list[SheetSpec] = get_all("sheet")
    canvases: list[CanvasSpec] = get_all("canvas")
    subagents: list[SubAgentSpec] = get_all("subagent")
    evals: list[EvalSpec] = get_all("eval")
    apis: list[ApiSpec] = get_all("api")

    manifest: dict[str, Any] = {
        "sheets": [{"name": s.name, "version": s.version} for s in sheets],
        "canvases": [
            {"name": c.name, "version": c.version, "regions": len(c.regions)} for c in canvases
        ],
        "subagents": [{"name": s.name} for s in subagents],
        "apis": [
            {
                "prefix": api.prefix,
                "tag": api.tag,
                "routes": len(api.routes),
            }
            for api in apis
        ],
        "evals": list({e.suite for e in evals}),
    }

    file_path = target / "manifest.json"
    file_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    return [file_path]


# ---------------------------------------------------------------------------
# Target: skills
# ---------------------------------------------------------------------------


def emit_skills(out_dir: Path) -> list[Path]:
    subagents: list[SubAgentSpec] = get_all("subagent")
    if not subagents:
        return []

    written: list[Path] = []
    for spec in subagents:
        skill_dir = out_dir / "skills" / spec.name
        skill_dir.mkdir(parents=True, exist_ok=True)
        skill_path = skill_dir / "SKILL.md"
        content = textwrap.dedent(f"""\
            ---
            name: {spec.name}
            generated: true
            response_model: {spec.response_model}
            ---

            # {spec.name}

            > Auto-generated from `specs/agents/`. Do not edit manually — run `rpg compile`.

            ## Response model

            `{spec.response_model}`

            ## Skills referenced

            {chr(10).join(f"- `{s}`" for s in spec.skills) or "- (none)"}
            """)
        skill_path.write_text(content, encoding="utf-8")
        written.append(skill_path)

    return written


# ---------------------------------------------------------------------------
# Dispatcher
# ---------------------------------------------------------------------------

TARGETS = {
    "pydantic": emit_pydantic,
    "jsonschema": emit_jsonschema,
    "typescript": emit_typescript,
    "openapi": emit_openapi,
    "agent_manifest": emit_agent_manifest,
    "evals": emit_evals,
    "registry": emit_registry,
    "skills": emit_skills,
}


def compile_all(out_dir: Path, targets: list[str] | None = None) -> dict[str, list[Path]]:
    selected = targets or list(TARGETS)
    results: dict[str, list[Path]] = {}
    for t in selected:
        if t not in TARGETS:
            raise ValueError(f"Unknown target: {t!r}. Available: {list(TARGETS)}")
        results[t] = TARGETS[t](out_dir)
    return results


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _to_snake(name: str) -> str:
    import re

    s1 = re.sub(r"(.)([A-Z][a-z]+)", r"\1_\2", name)
    return re.sub(r"([a-z0-9])([A-Z])", r"\1_\2", s1).lower()


def _to_const_name(name: str) -> str:
    snake = _to_snake(name)
    parts = [p for p in snake.split("_") if p]
    return parts[0] + "".join(p.capitalize() for p in parts[1:]) if parts else "value"


def _ts_type(field: FieldSpec) -> str:
    return _TS_TYPES.get(field.type, "unknown")


def _sheet_json_schema(spec: SheetSpec, title: str) -> dict[str, Any]:
    properties: dict[str, Any] = {}
    required: list[str] = []
    for field in spec.fields:
        prop = {"title": field.label, **_JSON_TYPES.get(field.type, {"type": "string"})}
        if field.type == "integer":
            if field.min is not None:
                prop["minimum"] = field.min
            if field.max is not None:
                prop["maximum"] = field.max
        properties[field.key] = prop
        if field.required:
            required.append(field.key)

    schema: dict[str, Any] = {
        "title": title,
        "type": "object",
        "properties": properties,
    }
    if required:
        schema["required"] = required
    return schema


def _placeholder_schema(name: str) -> dict[str, Any]:
    return {
        "title": name,
        "type": "object",
        "additionalProperties": True,
    }


def _operation_id(route: RouteSpec) -> str:
    cleaned = route.path.strip("/").replace("{", "").replace("}", "")
    parts = [route.method.lower(), *[p for p in cleaned.replace("-", "_").split("/") if p]]
    return "_".join(parts) if parts else route.method.lower()


def _path_parameters(path: str) -> list[dict[str, Any]]:
    import re

    return [
        {
            "name": match,
            "in": "path",
            "required": True,
            "schema": {"type": "string"},
        }
        for match in re.findall(r"{([^}]+)}", path)
    ]
