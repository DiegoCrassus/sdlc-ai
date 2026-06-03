from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from studio import CompilerInputError, compile_studio_sources, compiler_core

REPO_ROOT = Path(__file__).resolve().parents[1]


def test_compile_studio_sources_is_deterministic_and_schema_shaped() -> None:
    first = compile_studio_sources(REPO_ROOT)
    second = compile_studio_sources(REPO_ROOT)

    assert first == second
    _assert_graph_schema_shape(first.graph_ir)
    _assert_workflow_schema_shape(first.workflow_ir)

    node_ids = [node["id"] for node in first.graph_ir["nodes"]]
    edge_ids = [edge["id"] for edge in first.graph_ir["edges"]]
    transition_ids = [
        transition["id"] for transition in first.workflow_ir["workflow"]["transitions"]
    ]

    assert node_ids == sorted(node_ids)
    assert edge_ids == sorted(edge_ids)
    assert transition_ids == sorted(transition_ids)
    assert [
        stage["id"] for stage in first.workflow_ir["workflow"]["stages"]
    ] == [
        "stage.ticket",
        "stage.requirements",
        "stage.architecture",
        "stage.implementation",
        "stage.validation",
        "stage.review",
        "stage.deployment",
        "stage.observability",
        "stage.incident",
        "stage.autofix",
    ]


def test_compile_studio_sources_preserves_source_references_without_source_bodies() -> None:
    result = compile_studio_sources(REPO_ROOT)

    assert result.graph_ir["graph"]["source_refs"]
    assert all(node["source_refs"] for node in result.graph_ir["nodes"])
    assert all(edge["source_refs"] for edge in result.graph_ir["edges"])
    assert all(
        stage["source_refs"] for stage in result.workflow_ir["workflow"]["stages"]
    )
    assert all(
        transition["source_refs"]
        for transition in result.workflow_ir["workflow"]["transitions"]
    )
    assert any(
        node["registry_ref"].startswith("cursor.")
        and node["source_refs"][0]["ref"].startswith(".cursor/")
        for node in result.graph_ir["nodes"]
    )
    assert result.report["authority"] == "derived_non_authoritative"
    assert "studio/generated/" in result.report["excluded_source_areas"]
    _assert_forbidden_body_keys_absent(result.graph_ir)
    _assert_forbidden_body_keys_absent(result.workflow_ir)
    _assert_forbidden_body_keys_absent(result.report)


def test_compile_studio_sources_reports_missing_required_inputs(tmp_path: Path) -> None:
    with pytest.raises(CompilerInputError) as exc_info:
        compile_studio_sources(tmp_path)

    error = exc_info.value
    assert ".sdlc/registry/sdlc-artifacts.yaml" in error.missing_paths
    assert "Missing required compiler inputs" in str(error)


def test_compile_studio_sources_reports_unreadable_required_yaml(tmp_path: Path) -> None:
    _write_minimal_required_inputs(tmp_path)
    bad_yaml = tmp_path / ".sdlc/registry/relationships.yaml"
    bad_yaml.write_text("relationships: [\n", encoding="utf-8")

    with pytest.raises(CompilerInputError) as exc_info:
        compile_studio_sources(tmp_path)

    error = exc_info.value
    assert ".sdlc/registry/relationships.yaml" in error.unreadable_yaml
    assert "Unreadable required YAML" in str(error)


def test_compile_studio_sources_does_not_persist_generated_outputs() -> None:
    forbidden_paths = [
        REPO_ROOT / "studio/generated",
        REPO_ROOT / "studio/examples",
        REPO_ROOT / "specs",
    ]
    before_exists = {path: path.exists() for path in forbidden_paths}
    before_mtime = {
        source_path: (REPO_ROOT / source_path).stat().st_mtime_ns
        for source_path in compiler_core.REQUIRED_SOURCE_PATHS
    }

    compile_studio_sources(REPO_ROOT)

    after_exists = {path: path.exists() for path in forbidden_paths}
    after_mtime = {
        source_path: (REPO_ROOT / source_path).stat().st_mtime_ns
        for source_path in compiler_core.REQUIRED_SOURCE_PATHS
    }
    assert after_exists == before_exists
    assert after_mtime == before_mtime


def _assert_graph_schema_shape(graph_ir: dict[str, Any]) -> None:
    schema = _load_schema("graph.schema.yaml")
    graph_schema = schema["properties"]["graph"]
    node_schema = schema["properties"]["nodes"]["items"]
    edge_schema = schema["properties"]["edges"]["items"]

    assert set(schema["required"]).issubset(graph_ir)
    assert set(graph_schema["required"]).issubset(graph_ir["graph"])
    assert re.match(graph_schema["properties"]["id"]["pattern"], graph_ir["graph"]["id"])
    assert graph_ir["graph"]["non_goals"]
    _assert_source_ref_objects(graph_ir["graph"]["source_refs"])

    allowed_node_types = set(node_schema["properties"]["type"]["enum"])
    allowed_categories = set(node_schema["properties"]["category"]["enum"])
    for node in graph_ir["nodes"]:
        assert set(node_schema["required"]).issubset(node)
        assert re.match(node_schema["properties"]["id"]["pattern"], node["id"])
        assert node["type"] in allowed_node_types
        assert node["category"] in allowed_categories
        _assert_source_ref_objects(node["source_refs"])

    allowed_relations = set(edge_schema["properties"]["relation"]["enum"])
    node_ids = {node["id"] for node in graph_ir["nodes"]}
    for edge in graph_ir["edges"]:
        assert set(edge_schema["required"]).issubset(edge)
        assert re.match(edge_schema["properties"]["id"]["pattern"], edge["id"])
        assert edge["from"] in node_ids
        assert edge["to"] in node_ids
        assert edge["relation"] in allowed_relations
        _assert_source_ref_objects(edge["source_refs"])


def _assert_workflow_schema_shape(workflow_ir: dict[str, Any]) -> None:
    schema = _load_schema("workflow.schema.yaml")
    workflow_schema = schema["properties"]["workflow"]
    stage_schema = workflow_schema["properties"]["stages"]["items"]
    transition_schema = workflow_schema["properties"]["transitions"]["items"]

    assert set(schema["required"]).issubset(workflow_ir)
    workflow = workflow_ir["workflow"]
    assert set(workflow_schema["required"]).issubset(workflow)
    assert workflow["non_goals"]
    assert all(isinstance(source_ref, str) for source_ref in workflow["source_refs"])

    for stage in workflow["stages"]:
        assert set(stage_schema["required"]).issubset(stage)
        assert stage["source_refs"]
        assert all(isinstance(source_ref, str) for source_ref in stage["source_refs"])

    allowed_relations = set(transition_schema["properties"]["relation"]["enum"])
    stage_ids = {stage["id"] for stage in workflow["stages"]}
    for transition in workflow["transitions"]:
        assert set(transition_schema["required"]).issubset(transition)
        assert transition["from"] in stage_ids
        assert transition["to"] in stage_ids
        assert transition["relation"] in allowed_relations
        assert all(isinstance(source_ref, str) for source_ref in transition["source_refs"])


def _assert_source_ref_objects(source_refs: list[dict[str, Any]]) -> None:
    assert source_refs
    for source_ref in source_refs:
        assert source_ref["ref_type"] == "path"
        assert source_ref["ref"]


def _assert_forbidden_body_keys_absent(value: Any) -> None:
    forbidden_keys = {
        "body",
        "content",
        "prompt",
        "command_body",
        "hook_logic",
        "template_body",
        "lifecycle_body",
        "ci_log",
        "evidence",
    }
    if isinstance(value, dict):
        assert not (set(value) & forbidden_keys)
        for child in value.values():
            _assert_forbidden_body_keys_absent(child)
    elif isinstance(value, list):
        for child in value:
            _assert_forbidden_body_keys_absent(child)


def _write_minimal_required_inputs(root: Path) -> None:
    yaml_payloads = {
        ".sdlc/registry/sdlc-artifacts.yaml": {"artifacts": []},
        ".sdlc/registry/cursor-artifacts.yaml": {"artifacts": []},
        ".sdlc/registry/relationships.yaml": {"relationships": []},
        ".sdlc/stages/lifecycle.yaml": {"stages": []},
        ".sdlc/workflows/transitions.yaml": {"workflows": []},
    }
    for source_path in compiler_core.REQUIRED_SOURCE_PATHS:
        path = root / source_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if source_path.endswith((".yaml", ".yml")):
            payload = yaml_payloads.get(source_path, {})
            path.write_text(yaml.safe_dump(payload, sort_keys=True), encoding="utf-8")
        else:
            path.write_text("reference only\n", encoding="utf-8")


def _load_schema(name: str) -> dict[str, Any]:
    schema = yaml.safe_load((REPO_ROOT / "studio/schemas" / name).read_text())
    assert isinstance(schema, dict)
    return schema
