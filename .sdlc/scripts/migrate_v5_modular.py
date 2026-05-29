#!/usr/bin/env python3
"""One-shot migration: flat .sdlc/*.yaml -> modular v5.2 layout."""

from __future__ import annotations

import shutil
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SDLC = ROOT / ".sdlc"


def load(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def dump(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.dump(data, default_flow_style=False, allow_unicode=True, sort_keys=False), encoding="utf-8")


def main() -> None:
    stages_full = load(SDLC / "stages.yaml")
    lifecycle_stages = []
    for s in stages_full.get("stages", []):
        lifecycle_stages.append(
            {
                "id": s["id"],
                "name": s["name"],
                "order": s["order"],
                "description": (s.get("objective") or s["name"])[:200],
            }
        )
    dump(SDLC / "stages" / "lifecycle.yaml", {"stages": lifecycle_stages})
    dump(SDLC / "stages" / "definitions.yaml", stages_full)

    gates_raw = load(SDLC / "gate-paths.yaml")
    dump(
        SDLC / "gates" / "paths.yaml",
        {
            "gate_paths": gates_raw.get("gate_paths")
            or {
                "protected_prefixes": gates_raw.get("protected_prefixes", []),
                "stages": gates_raw.get("stages", {}),
            }
        },
    )

    pg = load(SDLC / "plane-granularity.yaml")
    dump(
        SDLC / "workboard" / "granularity.yaml",
        {"workboard_granularity": pg.get("plane_granularity") or pg.get("workboard_granularity") or pg},
    )

    dump(SDLC / "pipeline" / "agents.yaml", load(SDLC / "pipeline.yaml"))
    dump(SDLC / "workflows" / "transitions.yaml", load(SDLC / "workflows.yaml"))

    rules = load(SDLC / "rules.yaml")
    dump(SDLC / "rules" / "governance.yaml", rules)

    integrations = load(SDLC / "integrations.yaml")
    services = []
    env_map = {
        "github": "vcs_token",
        "plane": "workboard_api_key",
        "openai": "llm_api_key",
    }
    for i in integrations.get("integrations", []):
        services.append(
            {
                "id": i["id"],
                "role": {"github": "vcs", "plane": "workboard", "openai": "llm"}.get(i["id"], i["id"]),
                "name": i["name"],
                "status": i.get("status", "placeholder"),
                "description": i.get("description", ""),
                "env_logical": env_map.get(i["id"]),
                "config_env": i.get("config_env"),
                "capabilities": i.get("capabilities", []),
            }
        )
    dump(SDLC / "integrations" / "services.yaml", {"integrations": services})

    doctor = load(SDLC / "doctor.yaml")
    dump(SDLC / "doctor" / "checks.yaml", doctor)

    manifest = load(SDLC / "manifest.yaml")
    dump(SDLC / "manifest" / "catalog.yaml", manifest)

    sdlc_old = load(SDLC / "sdlc.yaml")
    dump(
        SDLC / "settings" / "config.yaml",
        {
            "settings": sdlc_old.get("settings", {}),
            "memory": sdlc_old.get("memory", {}),
        },
    )
    dump(SDLC / "meta" / "tools.yaml", {"meta_tools": sdlc_old.get("meta_tools", [])})

    rules_index = {
        "rules_index": [
            ".cursor/rules/000-project-governance.mdc",
            ".cursor/rules/001-sdlc-anti-bypass.mdc",
            ".cursor/rules/002-sdlc-orchestrator-principal.mdc",
            ".cursor/rules/003-orchestrator-delegation-only.mdc",
            ".cursor/rules/010-ai-native-sdlc.mdc",
            ".cursor/rules/030-docs-and-handoff.mdc",
            ".cursor/rules/040-doctor-gates.mdc",
            ".cursor/rules/050-sdlc-stage-governance.mdc",
            ".cursor/rules/sdlc-core.mdc",
        ]
    }
    dump(SDLC / "rules" / "index.yaml", rules_index)

    for name, readme_body in MODULE_READMES.items():
        (SDLC / name / "README.md").write_text(readme_body, encoding="utf-8")

    # Remove legacy flat YAMLs at .sdlc root
    for legacy in (
        "manifest.yaml",
        "stages.yaml",
        "pipeline.yaml",
        "workflows.yaml",
        "rules.yaml",
        "integrations.yaml",
        "doctor.yaml",
        "gate-paths.yaml",
        "plane-granularity.yaml",
    ):
        p = SDLC / legacy
        if p.is_file():
            p.unlink()

    print("OK: modular data files created; legacy flat YAMLs removed.")


MODULE_READMES = {
    "manifest": "# Manifest\n\nData: `catalog.yaml` — agents, skills, MCPs.\n",
    "stages": "# Stages\n\n- `lifecycle.yaml` — ordered stage ids\n- `definitions.yaml` — full stage contracts\n",
    "gates": "# Gates\n\nData: `paths.yaml` — session write permissions.\n",
    "workboard": "# Workboard\n\nData: `granularity.yaml` — epic/child card rules.\n",
    "pipeline": "# Pipeline\n\nData: `agents.yaml` — stage → agent mapping.\n",
    "workflows": "# Workflows\n\nData: `transitions.yaml` — stage transitions.\n",
    "rules": "# Rules\n\n- `governance.yaml` — rule definitions\n- `index.yaml` — `.cursor/rules` paths\n",
    "integrations": "# Integrations\n\nData: `services.yaml` — vendor roles + env.\n",
    "doctor": "# Doctor\n\nData: `checks.yaml` — structure validation.\n",
    "meta": "# Meta tools\n\nData: `tools.yaml` — deterministic scripts.\n",
    "settings": "# Settings\n\nData: `config.yaml` — memory paths, flags.\n",
}


if __name__ == "__main__":
    main()
