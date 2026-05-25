"""CLI entry point — `rpg` command."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _cmd_validate(args: argparse.Namespace) -> int:
    from ._validator import validate_dir

    specs_dir = Path(args.specs_dir)
    if not specs_dir.exists():
        print(f"error: specs directory not found: {specs_dir}", file=sys.stderr)
        return 1

    _ok, errors, summary = validate_dir(specs_dir)

    if errors:
        for err in errors:
            print(f"  error: {err}", file=sys.stderr)
        print(f"\nvalidate FAILED — {len(errors)} error(s)", file=sys.stderr)
        return 1

    if summary["files"] == 0:
        print("skip: no spec files found")
        return 0

    spec_counts = ", ".join(f"{k}={v}" for k, v in summary["specs"].items())
    print(
        f"validate ok — {summary['files']} file(s) loaded  [{spec_counts or 'no specs registered'}]"
    )
    return 0


def _cmd_compile(args: argparse.Namespace) -> int:
    from ._compiler import TARGETS, compile_all
    from ._validator import validate_dir

    specs_dir = Path(args.specs_dir)
    out_dir = Path(args.out_dir)

    if not specs_dir.exists():
        print(f"error: specs directory not found: {specs_dir}", file=sys.stderr)
        return 1

    ok, errors, _ = validate_dir(specs_dir)
    if not ok:
        for err in errors:
            print(f"  error: {err}", file=sys.stderr)
        print("compile FAILED — fix validation errors first", file=sys.stderr)
        return 1

    targets: list[str] | None = None
    if args.target and args.target != "all":
        targets = [t.strip() for t in args.target.split(",")]
        unknown = [t for t in targets if t not in TARGETS]
        if unknown:
            print(
                f"error: unknown target(s): {unknown}. Available: {list(TARGETS)}", file=sys.stderr
            )
            return 1

    results = compile_all(out_dir, targets)

    total = sum(len(v) for v in results.values())
    if total == 0:
        print("compile ok — nothing to emit (no specs registered)")
        return 0

    for target_name, paths in results.items():
        for p in paths:
            print(f"  {target_name}: {p}")
    print(f"\ncompile ok — {total} file(s) written to {out_dir}")
    return 0


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="rpg",
        description="RPG-OP DSL compiler and validator",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # rpg validate
    p_val = sub.add_parser("validate", help="Validate spec files")
    p_val.add_argument("specs_dir", nargs="?", default="specs/", help="Path to specs directory")

    # rpg compile
    p_comp = sub.add_parser("compile", help="Compile specs to artefacts")
    p_comp.add_argument("specs_dir", nargs="?", default="specs/", help="Path to specs directory")
    p_comp.add_argument(
        "--target",
        default="all",
        help="Comma-separated targets: pydantic,jsonschema,typescript,openapi,agent_manifest,evals,registry,skills,all",
    )
    p_comp.add_argument(
        "--out",
        dest="out_dir",
        default="generated/",
        help="Output directory (default: generated/)",
    )

    args = parser.parse_args()

    if args.command == "validate":
        sys.exit(_cmd_validate(args))
    elif args.command == "compile":
        sys.exit(_cmd_compile(args))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
