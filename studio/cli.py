"""Local, non-authoritative Studio command line entrypoint."""

from __future__ import annotations

import argparse
import json
import sys
from collections.abc import Sequence
from pathlib import Path
from typing import Any

from studio.canvas_view_model import build_canvas_from_sources, render_canvas_text
from studio.compiler_core import CompilerInputError, compile_studio_sources
from studio.reporting import render_report_text
from studio.validation_inspection import (
    ValidationInspectionInputError,
    build_validation_inspection_from_sources,
    render_validation_inspection_text,
)
from studio.validator_core import validate_studio_sources


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
        if args.command == "canvas":
            return _run_canvas(root, args.format)
        if args.command == "inspect-validation":
            return _run_inspect_validation(root, args)
    except (CompilerInputError, ValidationInspectionInputError) as exc:
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
    for command in ("compile", "validate", "canvas"):
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
    inspect_parser = subparsers.add_parser("inspect-validation")
    inspect_parser.add_argument(
        "--format",
        choices=("text", "json"),
        default="text",
        help="Output format.",
    )
    inspect_parser.add_argument(
        "--root",
        type=Path,
        default=None,
        help="Repository root to inspect. Defaults to the current directory.",
    )
    inspect_parser.add_argument("--status", default=None, help="Filter by validation status.")
    inspect_parser.add_argument("--check-type", default=None, help="Filter by validation check type.")
    inspect_parser.add_argument("--target-type", default=None, help="Filter by validation target type.")
    inspect_parser.add_argument(
        "--group-by",
        default="status",
        help="Group visible records by status, check_type, or target_type.",
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
        _write_report_text(result.report)
    return 0


def _run_validate(root: Path, output_format: str) -> int:
    result = validate_studio_sources(root)
    payload = {
        "report": result.report,
        "results": result.results,
        "summary": result.summary,
    }
    if output_format == "json":
        _write_json(payload)
    else:
        _write_report_text(result.report)
    return 1 if result.summary.get("fail", 0) else 0


def _run_canvas(root: Path, output_format: str) -> int:
    model = build_canvas_from_sources(root)
    if output_format == "json":
        _write_json(model.to_dict())
    else:
        sys.stdout.write(render_canvas_text(model))
    return 1 if model.legend["validation_statuses"].get("fail", 0) else 0


def _run_inspect_validation(root: Path, args: argparse.Namespace) -> int:
    model = build_validation_inspection_from_sources(
        root,
        status=args.status,
        check_type=args.check_type,
        target_type=args.target_type,
        group_by=args.group_by,
    )
    if args.format == "json":
        _write_json(model)
    else:
        sys.stdout.write(render_validation_inspection_text(model))
    return 1 if model["summary"]["by_status"].get("fail", 0) else 0


def _write_json(payload: dict[str, Any]) -> None:
    json.dump(payload, sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


def _write_report_text(report: dict[str, Any]) -> None:
    sys.stdout.write(render_report_text(report))


if __name__ == "__main__":
    raise SystemExit(main())
