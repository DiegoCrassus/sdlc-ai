"""Compiler — emits artefacts from registered specs."""

from __future__ import annotations

import json
import textwrap
from pathlib import Path
from typing import Any

from ._models import CanvasSpec, EvalSpec, FieldSpec, SheetSpec, SubAgentSpec
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

    manifest: dict[str, Any] = {
        "sheets": [{"name": s.name, "version": s.version} for s in sheets],
        "canvases": [{"name": c.name, "version": c.version, "regions": len(c.regions)} for c in canvases],
        "subagents": [{"name": s.name} for s in subagents],
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

            {chr(10).join(f'- `{s}`' for s in spec.skills) or '- (none)'}
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
