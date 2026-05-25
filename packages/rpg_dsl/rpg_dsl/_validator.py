"""Validator — imports spec files and reports errors."""

from __future__ import annotations

import importlib.util
import textwrap
import traceback
from pathlib import Path

from ._registry import all_specs, clear


def _load_spec_file(path: Path) -> list[str]:
    """Import a single spec file, return list of error strings."""
    errors: list[str] = []
    spec = importlib.util.spec_from_file_location(f"_rpg_spec_{path.stem}", path)
    if spec is None or spec.loader is None:
        errors.append(f"{path}: cannot load module")
        return errors
    module = importlib.util.module_from_spec(spec)
    try:
        spec.loader.exec_module(module)  # type: ignore[arg-type]
    except Exception:
        errors.append(f"{path}:\n{textwrap.indent(traceback.format_exc(), '  ')}")
    return errors


def validate_dir(specs_dir: Path) -> tuple[bool, list[str], dict]:
    """
    Validate all *.py files in specs_dir (recursive, excludes __init__.py).
    Returns (ok, errors, summary).
    """

    clear()
    errors: list[str] = []
    files = sorted(p for p in specs_dir.rglob("*.py") if p.name != "__init__.py")

    if not files:
        return True, [], {"files": 0, "specs": {}}

    for file_path in files:
        file_errors = _load_spec_file(file_path)
        errors.extend(file_errors)

    specs = all_specs()
    summary = {
        "files": len(files),
        "specs": {k: len(v) for k, v in specs.items() if v},
    }

    return len(errors) == 0, errors, summary
