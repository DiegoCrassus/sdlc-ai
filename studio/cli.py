"""Local, non-authoritative Studio command line entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from studio.compiler_core import CompilerInputError, compile_studio_sources
from studio.validator_core import validate_studio_sources

_STATUSES = ("pass", "warn", "fail", "not_run")


def main(argv: Sequence[str] | None = None) -> int:
    """Run the Studio CLI and return a process exit code."""

    parser = _build_parser()
    args = parser.parse_args(argv)
    root = args.root if args.root is not None else Path.cwd()
    try:
        if args.command == "compile":
            return _run_compile(root, args.format)
        if args.command == "validate":
            return _run_validate(root, args.format)
    except CompilerInputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    parser.error("missing command")
    return 2


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="python -m studio.cli",
        description="Inspect derived, non-authoritative Studio compiler outputs.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)
    for command in ("compile", "validate"):
        subparser = subparsers.add_parser(command)
        subparser.add_argument(
            "--format",
            choices=("text", "json"),
            default="text",
            help="Output format.",
        )
        subparser.add_argument(
            "--root",
            type=Path,
            default=None,
            help="Repository root to inspect. Defaults to the current directory.",
        )
    return parser


def _run_compile(root: Path, output_format: str) -> int:
    result = compile_studio_sources(root)
    payload = {
        "graph_ir": result.graph_ir,
        "workflow_ir": result.workflow_ir,
        "report": result.report,
    }
    if output_format == "json":
        _write_json(payload)
    else:
        _write_compile_text(payload)
    return 0


def _run_validate(root: Path, output_format: str) -> int:
    result = validate_studio_sources(root)
    payload = {
        "results": result.results,
        "summary": result.summary,
    }
    if output_format == "json":
        _write_json(payload)
    else:
        _write_validate_text(payload)
    return 1 if result.summary.get("fail", 0) else 0


def _write_json(payload: dict[str, Any]) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def _write_compile_text(payload: dict[str, Any]) -> None:
    graph_ir = payload["graph_ir"]
    workflow_ir = payload["workflow_ir"]
    report = payload["report"]
    coverage = report.get("coverage", {}) if isinstance(report.get("coverage"), dict) else {}
    workflow = workflow_ir.get("workflow", {}) if isinstance(workflow_ir.get("workflow"), dict) else {}
    unresolved = coverage.get("unresolved_relationships", [])
    unresolved_count = len(unresolved) if isinstance(unresolved, list) else 0
    lines = [
        "Studio compile: derived, non-authoritative output",
        f"status: {report.get('status', 'unknown')}",
        f"required inputs: {_count(coverage, 'required_inputs')}",
        f"graph nodes: {len(_list(graph_ir.get('nodes')))}",
        f"graph edges: {len(_list(graph_ir.get('edges')))}",
        f"workflow stages: {len(_list(workflow.get('stages')))}",
        f"workflow transitions: {len(_list(workflow.get('transitions')))}",
        f"unresolved relationships: {unresolved_count}",
        "reminder: CLI stdout is derived and non-authoritative only.",
    ]
    sys.stdout.write("\n".join(lines) + "\n")


def _write_validate_text(payload: dict[str, Any]) -> None:
    summary = payload["summary"]
    results = payload["results"]
    lines = [
        "Studio validate: derived, non-authoritative output",
        "summary: " + ", ".join(f"{status}={summary.get(status, 0)}" for status in _STATUSES),
    ]
    lines.extend(f"{record.get('status', 'unknown')} {record.get('id', 'unknown')}" for record in results)
    sys.stdout.write("\n".join(lines) + "\n")


def _count(coverage: dict[str, Any], key: str) -> int:
    value = coverage.get(key, 0)
    return value if isinstance(value, int) else 0


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


if __name__ == "__main__":
    raise SystemExit(main())
