"""Non-authoritative Studio compiler core.

The compiler reads known SDLC and Cursor source indexes and returns derived
records in memory. It intentionally does not execute workflows, call tools, or
persist generated outputs.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml

REQUIRED_SOURCE_PATHS: tuple[str, ...] = (
    "studio/compiler-validator-boundaries.md",
    "studio/graph-ir-contract.md",
    "studio/validation-result-ir-contract.md",
    "studio/schemas/graph.schema.yaml",
    "studio/schemas/workflow.schema.yaml",
    "studio/schemas/validation-result.schema.yaml",
    ".sdlc/registry/index.yaml",
    ".sdlc/registry/sdlc-artifacts.yaml",
    ".sdlc/registry/cursor-artifacts.yaml",
    ".sdlc/registry/relationships.yaml",
    ".sdlc/sdlc.yaml",
    ".sdlc/stages/lifecycle.yaml",
    ".sdlc/workflows/transitions.yaml",
    ".sdlc/gates/paths.yaml",
    ".sdlc/process/master-workflow.md",
    ".sdlc/process/change-lifecycle.md",
)

GRAPH_NON_GOALS: tuple[str, ...] = (
    "Does not replace .sdlc/, .cursor/, Plane, GitHub, or .sdlc/registry/.",
    "Does not execute workflows, commands, gates, agents, validators, or compilers.",
    "Does not store local tickets, backlog, specs, generated outputs, or durable evidence.",
    "Does not define UI, backend, frontend, API, database, deployment, or AI orchestration behavior.",
)

REPORT_NON_GOALS: tuple[str, ...] = (
    "No CLI surface, stdout UX, command runner, workflow runner, validator engine, or generated output persistence.",
    "No copied agent prompts, skill bodies, rule bodies, hook logic, templates, lifecycle prose, CI logs, or evidence.",
    "No replacement behavior for .sdlc/, .cursor/, .sdlc/registry/, Plane, or GitHub.",
)

EXCLUDED_SOURCE_AREAS: tuple[str, ...] = (
    "app/",
    "studio/examples/",
    "studio/generated/",
    "specs/",
    "local tickets",
    "local backlog",
    "local evidence files",
    "generated Graph IR, Workflow IR, reports, validation, snapshots, and command outputs",
)

_GRAPH_NODE_TYPES = {
    "workflow",
    "stage",
    "agent",
    "skill",
    "command",
    "gate",
    "policy",
    "template",
    "hook",
    "rule",
    "module",
    "registry_entity",
    "registry_relationship",
    "validation",
    "artifact",
    "external_authority",
}

_KIND_TO_NODE_TYPE = {
    "agent": "agent",
    "command": "command",
    "doctor": "validation",
    "gate": "gate",
    "gateway_policy": "policy",
    "hook": "hook",
    "module": "module",
    "rule": "rule",
    "script": "command",
    "skill": "skill",
    "stage": "stage",
    "template": "template",
    "workflow": "workflow",
    "workboard_policy": "policy",
}

_WORKFLOW_RECOVERY_TRANSITIONS = {"incident_to_autofix"}


@dataclass(frozen=True)
class CompilerResult:
    """In-memory compiler result."""

    graph_ir: dict[str, Any]
    workflow_ir: dict[str, Any]
    report: dict[str, Any]


class CompilerInputError(RuntimeError):
    """Raised when required compiler inputs are missing or unreadable."""

    def __init__(
        self,
        *,
        missing_paths: list[str] | None = None,
        unreadable_yaml: dict[str, str] | None = None,
        unreadable_paths: dict[str, str] | None = None,
    ) -> None:
        self.missing_paths = sorted(missing_paths or [])
        self.unreadable_yaml = dict(sorted((unreadable_yaml or {}).items()))
        self.unreadable_paths = dict(sorted((unreadable_paths or {}).items()))
        super().__init__(self._message())

    def _message(self) -> str:
        parts: list[str] = []
        if self.missing_paths:
            parts.append(
                "Missing required compiler inputs: " + ", ".join(self.missing_paths)
            )
        if self.unreadable_yaml:
            details = ", ".join(
                f"{path} ({error})" for path, error in self.unreadable_yaml.items()
            )
            parts.append("Unreadable required YAML: " + details)
        if self.unreadable_paths:
            details = ", ".join(
                f"{path} ({error})" for path, error in self.unreadable_paths.items()
            )
            parts.append("Unreadable required compiler inputs: " + details)
        return "; ".join(parts) or "Invalid compiler inputs"


def compile_studio_sources(root: Path | str) -> CompilerResult:
    """Compile Studio Graph IR, Workflow IR, and report records in memory."""

    repository_root = Path(root)
    required_paths = _validate_required_inputs(repository_root)
    yaml_inputs = _load_required_yaml(repository_root, required_paths)

    sdlc_artifacts = _as_list(
        yaml_inputs[".sdlc/registry/sdlc-artifacts.yaml"].get("artifacts")
    )
    cursor_artifacts = _as_list(
        yaml_inputs[".sdlc/registry/cursor-artifacts.yaml"].get("artifacts")
    )
    relationships = _as_list(
        yaml_inputs[".sdlc/registry/relationships.yaml"].get("relationships")
    )
    stages = _as_list(yaml_inputs[".sdlc/stages/lifecycle.yaml"].get("stages"))
    transitions = _as_list(
        yaml_inputs[".sdlc/workflows/transitions.yaml"].get("workflows")
    )

    graph_ir = _build_graph_ir(sdlc_artifacts, cursor_artifacts, relationships)
    workflow_ir = _build_workflow_ir(stages, transitions)
    report = _build_report(
        repository_root,
        required_paths,
        sdlc_artifacts,
        cursor_artifacts,
        relationships,
        stages,
        transitions,
    )
    return CompilerResult(graph_ir=graph_ir, workflow_ir=workflow_ir, report=report)


def _validate_required_inputs(root: Path) -> tuple[str, ...]:
    missing = [path for path in REQUIRED_SOURCE_PATHS if not (root / path).is_file()]
    if missing:
        raise CompilerInputError(missing_paths=missing)

    unreadable: dict[str, str] = {}
    for path in REQUIRED_SOURCE_PATHS:
        try:
            (root / path).read_text(encoding="utf-8")
        except OSError as exc:
            unreadable[path] = exc.strerror or exc.__class__.__name__
        except UnicodeError as exc:
            unreadable[path] = exc.__class__.__name__
    if unreadable:
        raise CompilerInputError(unreadable_paths=unreadable)
    return tuple(REQUIRED_SOURCE_PATHS)


def _load_required_yaml(root: Path, required_paths: tuple[str, ...]) -> dict[str, Any]:
    unreadable: dict[str, str] = {}
    loaded: dict[str, Any] = {}
    for path in required_paths:
        if not path.endswith((".yaml", ".yml")):
            continue
        try:
            parsed = yaml.safe_load((root / path).read_text(encoding="utf-8"))
        except (OSError, UnicodeError, yaml.YAMLError) as exc:
            unreadable[path] = str(exc).splitlines()[0]
            continue
        loaded[path] = parsed if isinstance(parsed, dict) else {}

    if unreadable:
        raise CompilerInputError(unreadable_yaml=unreadable)
    return loaded


def _build_graph_ir(
    sdlc_artifacts: list[dict[str, Any]],
    cursor_artifacts: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
) -> dict[str, Any]:
    artifacts = sorted(
        [*sdlc_artifacts, *cursor_artifacts], key=lambda artifact: str(artifact.get("id", ""))
    )
    nodes = [_artifact_to_node(artifact) for artifact in artifacts]
    known_node_ids = {node["registry_ref"]: node["id"] for node in nodes}

    edges = [
        _relationship_to_edge(relationship, known_node_ids)
        for relationship in sorted(
            relationships, key=lambda relationship: str(relationship.get("id", ""))
        )
        if relationship.get("from") in known_node_ids
        and relationship.get("to") in known_node_ids
    ]

    return {
        "graph": {
            "id": "graph.sdlc_studio.registry",
            "name": "SDLC Studio Registry Graph",
            "description": "Derived, non-executable graph over SDLC and Cursor registry records.",
            "version": "0.1.0",
            "source_refs": [
                _source_ref(".sdlc/registry/sdlc-artifacts.yaml", "SDLC registry nodes"),
                _source_ref(".sdlc/registry/cursor-artifacts.yaml", "Cursor registry nodes"),
                _source_ref(".sdlc/registry/relationships.yaml", "Registry graph edges"),
                _source_ref("studio/schemas/graph.schema.yaml", "Graph IR schema"),
                _source_ref("studio/graph-ir-contract.md", "Graph IR contract"),
            ],
            "annotations": [
                {
                    "kind": "note",
                    "text": "Derived records are referential and non-authoritative.",
                    "source_refs": [
                        _source_ref(
                            "studio/compiler-validator-boundaries.md",
                            "Compiler boundary source",
                        )
                    ],
                }
            ],
            "non_goals": list(GRAPH_NON_GOALS),
        },
        "nodes": nodes,
        "edges": edges,
    }


def _artifact_to_node(artifact: dict[str, Any]) -> dict[str, Any]:
    artifact_id = str(artifact.get("id", "unknown"))
    kind = str(artifact.get("kind", "artifact"))
    node_type = _KIND_TO_NODE_TYPE.get(kind, kind if kind in _GRAPH_NODE_TYPES else "artifact")
    source_system = str(artifact.get("source_system", "derived"))
    category = source_system if source_system in {"sdlc", "cursor"} else "derived"
    path = str(artifact.get("path", ""))
    node: dict[str, Any] = {
        "id": f"node.{artifact_id}",
        "type": node_type,
        "category": category,
        "label": _trim(str(artifact.get("name", artifact_id)), 120),
        "registry_ref": artifact_id,
        "entity_ref": artifact_id,
        "source_refs": [_source_ref(path, _trim(str(artifact.get("summary", "")), 180))],
    }
    summary = str(artifact.get("summary", "")).strip()
    if summary:
        node["annotations"] = [{"kind": "note", "text": _trim(summary, 500)}]
    return node


def _relationship_to_edge(
    relationship: dict[str, Any], known_node_ids: dict[str, str]
) -> dict[str, Any]:
    relationship_id = str(relationship.get("id", "unknown"))
    source_refs = [
        _source_ref(str(path), "Registry relationship source")
        for path in _as_list(relationship.get("source_refs"))
    ]
    edge: dict[str, Any] = {
        "id": f"edge.{relationship_id}",
        "from": known_node_ids[str(relationship["from"])],
        "to": known_node_ids[str(relationship["to"])],
        "relation": str(relationship.get("relation", "references")),
        "source_refs": source_refs,
    }
    summary = str(relationship.get("summary", "")).strip()
    if summary:
        edge["summary"] = _trim(summary, 180)
    return edge


def _build_workflow_ir(
    stages: list[dict[str, Any]], transitions: list[dict[str, Any]]
) -> dict[str, Any]:
    stage_records = [_stage_to_workflow_record(stage) for stage in sorted(stages, key=_stage_key)]
    transition_records = [
        _transition_to_workflow_record(transition)
        for transition in sorted(transitions, key=lambda item: str(item.get("id", "")))
    ]

    return {
        "workflow": {
            "id": "workflow.sdlc.lifecycle",
            "name": "SDLC Lifecycle Workflow",
            "description": "Derived, non-executable workflow view assembled from SDLC lifecycle and transition sources.",
            "source_refs": [
                ".sdlc/stages/lifecycle.yaml",
                ".sdlc/workflows/transitions.yaml",
                ".sdlc/gates/paths.yaml",
                ".sdlc/process/master-workflow.md",
                ".sdlc/process/change-lifecycle.md",
                "studio/schemas/workflow.schema.yaml",
            ],
            "stages": stage_records,
            "transitions": transition_records,
            "non_goals": [
                "This workflow view does not execute stages, agents, commands, gates, or transitions.",
                "This workflow view does not update Plane, GitHub, .sdlc/, .cursor/, or registry state.",
                "This workflow view does not store local tickets, backlog, generated outputs, or durable evidence.",
            ],
        }
    }


def _stage_to_workflow_record(stage: dict[str, Any]) -> dict[str, Any]:
    stage_id = str(stage.get("id", "unknown"))
    return {
        "id": f"stage.{stage_id}",
        "name": _trim(str(stage.get("name", stage_id)), 120),
        "stage_ref": f"sdlc.stage.lifecycle#{stage_id}",
        "description": _trim(str(stage.get("description", "")), 240),
        "order": stage.get("order"),
        "source_refs": [".sdlc/stages/lifecycle.yaml"],
    }


def _transition_to_workflow_record(transition: dict[str, Any]) -> dict[str, Any]:
    transition_id = str(transition.get("id", "unknown"))
    from_stage = str(transition.get("from_stage", ""))
    to_stage = str(transition.get("to_stage", ""))
    record: dict[str, Any] = {
        "id": f"transition.{transition_id}",
        "name": _trim(str(transition.get("name", transition_id)), 120),
        "from": f"stage.{from_stage}",
        "to": f"stage.{to_stage}",
        "relation": _workflow_relation(transition_id),
        "source_refs": [".sdlc/workflows/transitions.yaml"],
    }
    agent = transition.get("agent")
    skill = transition.get("skill")
    if agent:
        record["agent_ref"] = f"cursor.agent.{str(agent).replace('-', '_')}"
    if skill:
        record["skill_refs"] = [f"cursor.skill.{str(skill).replace('-', '_')}"]
    description = str(transition.get("description", "")).strip()
    if description:
        record["description"] = _trim(description, 240)
    return record


def _build_report(
    root: Path,
    required_paths: tuple[str, ...],
    sdlc_artifacts: list[dict[str, Any]],
    cursor_artifacts: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
    stages: list[dict[str, Any]],
    transitions: list[dict[str, Any]],
) -> dict[str, Any]:
    artifacts = [*sdlc_artifacts, *cursor_artifacts]
    registry_ids = {str(artifact.get("id")) for artifact in artifacts}
    unresolved_relationships = sorted(
        str(relationship.get("id", "unknown"))
        for relationship in relationships
        if relationship.get("from") not in registry_ids
        or relationship.get("to") not in registry_ids
    )

    return {
        "id": "report.studio.compiler_core",
        "status": "pass" if not unresolved_relationships else "warn",
        "authority": "derived_non_authoritative",
        "source_refs": list(required_paths),
        "coverage": {
            "required_inputs": len(required_paths),
            "registry_nodes": len(artifacts),
            "registry_edges": len(relationships),
            "workflow_stages": len(stages),
            "workflow_transitions": len(transitions),
            "unresolved_relationships": unresolved_relationships,
        },
        "missing_optional_source_paths": _missing_optional_source_paths(
            root, required_paths, artifacts, relationships
        ),
        "excluded_source_areas": list(EXCLUDED_SOURCE_AREAS),
        "non_goals": list(REPORT_NON_GOALS),
        "suggested_next_actions": [
            "QA should run focused compiler tests and SDLC validation commands for INVES-61.",
            "Future cards may add CLI, validator, or UI consumers without changing these authority boundaries.",
        ],
    }


def _missing_optional_source_paths(
    root: Path,
    required_paths: tuple[str, ...],
    artifacts: list[dict[str, Any]],
    relationships: list[dict[str, Any]],
) -> list[str]:
    required = set(required_paths)
    referenced_paths = {
        str(artifact.get("path", ""))
        for artifact in artifacts
        if str(artifact.get("path", "")).strip()
    }
    for relationship in relationships:
        referenced_paths.update(str(path) for path in _as_list(relationship.get("source_refs")))

    return sorted(
        path
        for path in referenced_paths
        if path not in required and path and not (root / path).exists()
    )


def _workflow_relation(transition_id: str) -> str:
    if transition_id in _WORKFLOW_RECOVERY_TRANSITIONS:
        return "recovery"
    return "next"


def _source_ref(ref: str, summary: str = "") -> dict[str, str]:
    source_ref = {"ref_type": "path", "ref": ref}
    if summary:
        source_ref["summary"] = _trim(summary, 180)
    return source_ref


def _stage_key(stage: dict[str, Any]) -> tuple[int, str]:
    order = stage.get("order")
    if isinstance(order, int):
        return (order, str(stage.get("id", "")))
    return (10_000, str(stage.get("id", "")))


def _as_list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _trim(value: str, limit: int) -> str:
    value = " ".join(value.split())
    if len(value) <= limit:
        return value
    return value[: limit - 1].rstrip() + "..."
