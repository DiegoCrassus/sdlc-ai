"""Repository-level Doctor checks for SDLC compliance."""

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


def _check_dir(root: str, rel_path: str) -> Finding:
    full = os.path.join(root, rel_path)
    if os.path.isdir(full):
        return ("PASS", f"Required directory exists: {rel_path}")
    return ("FAIL", f"Missing directory: {rel_path}")


def _check_file(root: str, rel_path: str) -> Finding:
    full = os.path.join(root, rel_path)
    if os.path.isfile(full):
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
        with open(full, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            return ("FAIL", f"YAML file is empty: {rel_path}")
        return ("PASS", f"YAML valid: {rel_path}")
    except yaml.YAMLError as e:
        return ("FAIL", f"YAML parse error in {rel_path}: {e}")


def _check_makefile_target(root: str, target: str) -> Finding:
    makefile = os.path.join(root, "Makefile")
    if not os.path.isfile(makefile):
        return ("FAIL", f"Makefile missing — cannot check target: {target}")
    with open(makefile, "r", encoding="utf-8") as f:
        content = f.read()
    if f"{target}:" in content:
        return ("PASS", f"Makefile target exists: {target}")
    return ("FAIL", f"Missing Makefile target: {target}")


def _check_integration_env(integration_id: str, env_var: str) -> Finding:
    if os.environ.get(env_var):
        return ("PASS", f"Integration configured: {integration_id} ({env_var})")
    return ("WARN", f"Integration not configured: {integration_id} ({env_var} not set)")


def run_doctor(root: str) -> List[Finding]:
    """Run all Doctor checks and return findings."""
    findings: List[Finding] = []

    # --- Required directories ---
    required_dirs = [
        ".cursor",
        ".cursor/rules",
        ".cursor/commands",
        ".cursor/skills",
        ".cursor/subagents",
        ".cursor/hooks",
        ".sdlc",
        ".sdlc/dsl",
        ".sdlc/memory",
        "docs",
        "docs/architecture",
        "docs/infrastructure",
        "docs/handoff",
        "docs/roadmap",
        "docs/operations",
        "docs/sdlc",
        "app",
        "app/frontend",
        "app/backend",
        "app/infra",
        "app/shared",
    ]
    for d in required_dirs:
        findings.append(_check_dir(root, d))

    # --- Required files ---
    required_files = [
        ".sdlc/sdlc.yaml",
        ".sdlc/lifecycle.yaml",
        ".sdlc/stages.yaml",
        ".sdlc/workflows.yaml",
        ".sdlc/agents.yaml",
        ".sdlc/skills.yaml",
        ".sdlc/rules.yaml",
        ".sdlc/integrations.yaml",
        ".sdlc/doctor.yaml",
        ".sdlc/dsl/cli.py",
        ".sdlc/dsl/doctor.py",
        "Makefile",
        "README.md",
    ]
    for f in required_files:
        findings.append(_check_file(root, f))

    # --- Cursor structure ---
    cursor_files = [
        ".cursor/commands/sdlc-doctor.md",
        ".cursor/commands/sdlc-plan.md",
        ".cursor/commands/sdlc-implement.md",
        ".cursor/commands/sdlc-review.md",
        ".cursor/commands/sdlc-handoff.md",
        ".cursor/rules/000-project-governance.mdc",
        ".cursor/rules/010-ai-native-sdlc.mdc",
        ".cursor/rules/020-code-quality.mdc",
        ".cursor/rules/030-docs-and-handoff.mdc",
        ".cursor/rules/040-doctor-gates.mdc",
        ".cursor/skills/requirements-refinement.md",
        ".cursor/skills/architecture-analysis.md",
        ".cursor/skills/implementation.md",
        ".cursor/skills/qa-validation.md",
        ".cursor/skills/code-review.md",
        ".cursor/skills/observability.md",
        ".cursor/skills/documentation.md",
        ".cursor/subagents/planner.md",
        ".cursor/subagents/architect.md",
        ".cursor/subagents/implementer.md",
        ".cursor/subagents/reviewer.md",
        ".cursor/subagents/qa.md",
        ".cursor/subagents/devops.md",
        ".cursor/subagents/doctor.md",
        ".cursor/hooks/pre-task.md",
        ".cursor/hooks/post-task.md",
        ".cursor/hooks/pre-review.md",
        ".cursor/hooks/post-review.md",
    ]
    for f in cursor_files:
        findings.append(_check_file(root, f))

    # --- Docs (non-empty) ---
    doc_files = [
        "docs/architecture/overview.md",
        "docs/architecture/decisions.md",
        "docs/architecture/system-context.md",
        "docs/infrastructure/overview.md",
        "docs/infrastructure/local-development.md",
        "docs/infrastructure/deployment.md",
        "docs/handoff/template.md",
        "docs/handoff/current-state.md",
        "docs/roadmap/roadmap.md",
        "docs/operations/observability.md",
        "docs/operations/incident-response.md",
        "docs/operations/maintenance.md",
        "docs/sdlc/ai-native-sdlc.md",
        "docs/sdlc/workflows.md",
        "docs/sdlc/gates.md",
        "docs/sdlc/doctor.md",
    ]
    for f in doc_files:
        findings.append(_check_file_nonempty(root, f))

    # --- YAML validity ---
    yaml_files = [
        ".sdlc/sdlc.yaml",
        ".sdlc/lifecycle.yaml",
        ".sdlc/stages.yaml",
        ".sdlc/workflows.yaml",
        ".sdlc/agents.yaml",
        ".sdlc/skills.yaml",
        ".sdlc/rules.yaml",
        ".sdlc/integrations.yaml",
        ".sdlc/doctor.yaml",
    ]
    for f in yaml_files:
        findings.append(_check_yaml(root, f))

    # --- Makefile targets ---
    for target in ["sdlc-doctor", "sdlc-validate", "sdlc-stages", "docs-check"]:
        findings.append(_check_makefile_target(root, target))

    # --- Integration env vars (warnings only) ---
    integration_envs = [
        ("github", "GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC"),
        ("plane", "PLANE_API_KEY"),
        ("openai", "OPENAI_API_KEY"),
    ]
    for integration_id, env_var in integration_envs:
        findings.append(_check_integration_env(integration_id, env_var))

    return findings


def print_report(findings: List[Finding]) -> int:
    """Print the Doctor report and return exit code (0=pass, 1=fail)."""
    pass_count = 0
    warn_count = 0
    fail_count = 0

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
