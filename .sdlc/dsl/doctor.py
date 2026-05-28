"""Repository-level Doctor checks driven by .sdlc/doctor.yaml."""

import os
import sys
from pathlib import Path
from typing import List, Tuple

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed. Run: pip install PyYAML", file=sys.stderr)
    sys.exit(1)

Finding = Tuple[str, str]  # (level, message)  level: PASS | FAIL | WARN

DOCTOR_YAML = ".sdlc/doctor.yaml"


# ─────────────────────────────────────────────
# Low-level check helpers
# ─────────────────────────────────────────────

def _check_dir(root: str, rel_path: str) -> Finding:
    if os.path.isdir(os.path.join(root, rel_path)):
        return ("PASS", f"Required directory exists: {rel_path}")
    return ("FAIL", f"Missing directory: {rel_path}")


def _check_file(root: str, rel_path: str) -> Finding:
    if os.path.isfile(os.path.join(root, rel_path)):
        return ("PASS", f"Required file exists: {rel_path}")
    return ("FAIL", f"Missing file: {rel_path}")


def _check_file_nonempty(root: str, rel_path: str) -> Finding:
    full = os.path.join(root, rel_path)
    if not os.path.isfile(full):
        return ("FAIL", f"Missing file: {rel_path}")
    if os.path.getsize(full) == 0:
        return ("FAIL", f"Empty file: {rel_path}")
    return ("PASS", f"Doc file non-empty: {rel_path}")


def _check_yaml(root: str, rel_path: str) -> Finding:
    full = os.path.join(root, rel_path)
    if not os.path.isfile(full):
        return ("FAIL", f"YAML file missing: {rel_path}")
    try:
        with open(full, "r", encoding="utf-8") as fh:
            data = yaml.safe_load(fh)
        if data is None:
            return ("FAIL", f"YAML file is empty: {rel_path}")
        return ("PASS", f"YAML valid: {rel_path}")
    except yaml.YAMLError as exc:
        return ("FAIL", f"YAML parse error in {rel_path}: {exc}")


def _check_makefile_target(root: str, target: str) -> Finding:
    makefile = os.path.join(root, "Makefile")
    if not os.path.isfile(makefile):
        return ("FAIL", f"Makefile missing — cannot check target: {target}")
    with open(makefile, "r", encoding="utf-8") as fh:
        content = fh.read()
    if f"{target}:" in content:
        return ("PASS", f"Makefile target exists: {target}")
    return ("FAIL", f"Missing Makefile target: {target}")


def _check_integration_env(integration_id: str, env_var: str) -> Finding:
    if os.environ.get(env_var):
        return ("PASS", f"Integration configured: {integration_id} ({env_var})")
    return ("WARN", f"Integration not configured: {integration_id} ({env_var} not set)")


# ─────────────────────────────────────────────
# Main runner — reads checks from doctor.yaml
# ─────────────────────────────────────────────

def run_doctor(root: str) -> List[Finding]:
    """Run all Doctor checks driven by .sdlc/doctor.yaml and return findings."""
    findings: List[Finding] = []

    doctor_path = os.path.join(root, DOCTOR_YAML)
    if not os.path.isfile(doctor_path):
        findings.append(("FAIL", f"Doctor config missing: {DOCTOR_YAML}"))
        return findings

    with open(doctor_path, "r", encoding="utf-8") as fh:
        config = yaml.safe_load(fh)

    checks = config.get("checks", {})

    # --- Directories ---
    for item in checks.get("directories", {}).get("items", []):
        findings.append(_check_dir(root, item))

    # --- Required files ---
    for item in checks.get("files", {}).get("items", []):
        findings.append(_check_file(root, item))

    # --- Cursor structure (commands, rules, skills, agents, hooks) ---
    cursor = checks.get("cursor", {})
    for section in ("commands", "rules", "skills", "agents", "hooks"):
        for item in cursor.get(section, []):
            findings.append(_check_file(root, item))

    # --- Docs (non-empty) ---
    for item in checks.get("docs", {}).get("items", []):
        findings.append(_check_file_nonempty(root, item))

    # --- YAML validity ---
    for item in checks.get("yaml_validity", {}).get("files", []):
        findings.append(_check_yaml(root, item))

    # --- Makefile targets ---
    for target in checks.get("makefile", {}).get("targets", []):
        findings.append(_check_makefile_target(root, target))

    # --- Workflow enforcement files (non-empty) ---
    for item in checks.get("workflow_files", {}).get("items", []):
        findings.append(_check_file_nonempty(root, item))

    # --- Integration env vars (warnings only) ---
    for entry in checks.get("integrations", {}).get("items", []):
        findings.append(_check_integration_env(entry["id"], entry["env"]))

    # --- Python DSL importable ---
    dsl_entry = checks.get("python_dsl", {}).get("importable")
    if dsl_entry:
        findings.append(_check_file(root, dsl_entry))

    return findings


# ─────────────────────────────────────────────
# Report printer
# ─────────────────────────────────────────────

def print_report(findings: List[Finding]) -> int:
    """Print the Doctor report and return exit code (0=pass, 1=fail)."""
    pass_count = warn_count = fail_count = 0

    for level, message in findings:
        if level == "PASS":
            pass_count += 1
            print(f"[PASS] {message}")
        elif level == "WARN":
            warn_count += 1
            print(f"[WARN] {message}")
        elif level == "FAIL":
            fail_count += 1
            print(f"[FAIL] {message}")
        else:
            print(f"[{level}] {message}")

    print()
    print(f"Doctor summary: {pass_count} passed, {warn_count} warnings, {fail_count} failed")

    return 0 if fail_count == 0 else 1
