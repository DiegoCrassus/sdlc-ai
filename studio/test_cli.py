from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

from studio import compiler_core

REPO_ROOT = Path(__file__).resolve().parents[1]
FORBIDDEN_OUTPUT_PATHS = ("studio/generated", "studio/examples", "specs")
REPRESENTATIVE_SOURCE_PATHS = (
    "studio/compiler_core.py",
    "studio/validator_core.py",
    ".sdlc/sdlc.yaml",
)


def test_compile_text_succeeds_from_repo_root_without_persisting_outputs() -> None:
    with unchanged_repo_outputs():
        completed = run_cli("compile")

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert "Studio compile: derived, non-authoritative output" in completed.stdout
    assert "status: " in completed.stdout
    assert "graph edges: " in completed.stdout
    assert "graph nodes: " in completed.stdout
    assert "required inputs: " in completed.stdout
    assert "workflow stages: " in completed.stdout
    assert "workflow transitions: " in completed.stdout
    assert "unresolved relationships: " in completed.stdout
    assert "derived and non-authoritative only" in completed.stdout


def test_compile_json_succeeds_with_stable_required_keys() -> None:
    with unchanged_repo_outputs():
        first = run_cli("compile", "--format", "json")
        second = run_cli("compile", "--format", "json")

    assert first.returncode == 0
    assert first.stderr == ""
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert set(payload) == {"graph_ir", "workflow_ir", "report"}
    assert isinstance(payload["graph_ir"], dict)
    assert isinstance(payload["workflow_ir"], dict)
    assert_standard_report_shape(payload["report"], kind="compile")
    assert payload["report"]["summary"]["counts"]["graph_nodes"] == len(payload["graph_ir"]["nodes"])


def test_validate_text_succeeds_from_repo_root_without_persisting_outputs() -> None:
    with unchanged_repo_outputs():
        completed = run_cli("validate")

    assert completed.returncode == 0
    assert completed.stderr == ""
    assert "Studio validate: derived, non-authoritative output" in completed.stdout
    assert "pass: 6" in completed.stdout
    assert "warn: 0" in completed.stdout
    assert "fail: 0" in completed.stdout
    assert "not run: 0" in completed.stdout
    assert "- validation.graph.relationship_targets: pass" in completed.stdout
    assert "- validation.compiler.authority_boundaries: pass" in completed.stdout


def test_validate_json_succeeds_with_stable_required_keys() -> None:
    with unchanged_repo_outputs():
        first = run_cli("validate", "--format", "json")
        second = run_cli("validate", "--format", "json")

    assert first.returncode == 0
    assert first.stderr == ""
    assert first.stdout == second.stdout
    payload = json.loads(first.stdout)
    assert set(payload) == {"report", "results", "summary"}
    assert isinstance(payload["results"], list)
    assert payload["summary"] == {"pass": 6, "warn": 0, "fail": 0, "not_run": 0}
    assert_standard_report_shape(payload["report"], kind="validate")
    assert payload["report"]["summary"]["counts"] == payload["summary"]


def test_compile_bad_root_exits_nonzero_with_concise_stderr(tmp_path: Path) -> None:
    completed = run_cli("compile", "--root", str(tmp_path / "missing"))

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert "Missing required compiler inputs" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_validate_bad_root_exits_nonzero_with_concise_stderr(tmp_path: Path) -> None:
    completed = run_cli("validate", "--root", str(tmp_path / "missing"))

    assert completed.returncode == 1
    assert completed.stdout == ""
    assert "Missing required compiler inputs" in completed.stderr
    assert "Traceback" not in completed.stderr


def test_cli_output_does_not_include_source_bodies_or_persisted_evidence() -> None:
    completed = run_cli("compile", "--format", "json")

    assert completed.returncode == 0
    payload = json.loads(completed.stdout)
    assert_forbidden_keys_absent(payload)


def test_cli_preserves_all_required_source_mtimes() -> None:
    before = {path: (REPO_ROOT / path).stat().st_mtime_ns for path in compiler_core.REQUIRED_SOURCE_PATHS}

    completed = run_cli("compile")

    assert completed.returncode == 0
    assert {path: (REPO_ROOT / path).stat().st_mtime_ns for path in before} == before


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
    return subprocess.run(
        [sys.executable, "-m", "studio.cli", *args],
        cwd=REPO_ROOT,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


class unchanged_repo_outputs:
    def __enter__(self) -> None:
        self._forbidden_exists = {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS}
        self._source_mtimes = {path: (REPO_ROOT / path).stat().st_mtime_ns for path in REPRESENTATIVE_SOURCE_PATHS}

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        assert {path: (REPO_ROOT / path).exists() for path in FORBIDDEN_OUTPUT_PATHS} == self._forbidden_exists
        assert {path: (REPO_ROOT / path).stat().st_mtime_ns for path in REPRESENTATIVE_SOURCE_PATHS} == self._source_mtimes


def assert_forbidden_keys_absent(value: object) -> None:
    forbidden = {
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
        assert not (set(value) & forbidden)
        for child in value.values():
            assert_forbidden_keys_absent(child)
    elif isinstance(value, list):
        for child in value:
            assert_forbidden_keys_absent(child)


def assert_standard_report_shape(report: object, *, kind: str) -> None:
    assert isinstance(report, dict)
    assert set(report) == {"id", "kind", "status", "authority", "summary", "sections", "source_refs", "non_goals"}
    assert report["id"] == f"report.studio.{kind}"
    assert report["kind"] == kind
    assert report["authority"] == "derived_non_authoritative"
    assert isinstance(report["summary"], dict)
    assert isinstance(report["summary"]["counts"], dict)
    assert report["sections"]
    assert report["source_refs"]
    assert report["non_goals"]
