"""YAML loader for SDLC configuration files."""

import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is not installed. Run: pip install PyYAML", file=sys.stderr)
    sys.exit(1)

from .models import (
    Agent,
    Integration,
    LifecycleStage,
    Rule,
    SDLCConfig,
    Skill,
    StageDefinition,
    Workflow,
)


class LoadError(Exception):
    pass


def _load_yaml(path: str) -> Dict[str, Any]:
    """Load a YAML file safely. Raises LoadError on failure."""
    p = Path(path)
    if not p.exists():
        raise LoadError(f"File not found: {path}")
    try:
        with open(p, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)
        if data is None:
            raise LoadError(f"Empty YAML file: {path}")
        return data
    except yaml.YAMLError as e:
        raise LoadError(f"YAML parse error in {path}: {e}") from e


def load_lifecycle(root: str) -> List[LifecycleStage]:
    data = _load_yaml(os.path.join(root, ".sdlc", "lifecycle.yaml"))
    stages = []
    for s in data.get("stages", []):
        stages.append(
            LifecycleStage(
                id=s["id"],
                name=s["name"],
                order=s["order"],
                description=s["description"],
            )
        )
    return stages


def load_stages(root: str) -> List[StageDefinition]:
    data = _load_yaml(os.path.join(root, ".sdlc", "stages.yaml"))
    defs = []
    for s in data.get("stages", []):
        defs.append(
            StageDefinition(
                id=s["id"],
                name=s["name"],
                objective=s["objective"],
                inputs=s.get("inputs", []),
                outputs=s.get("outputs", []),
                required_evidence=s.get("required_evidence", []),
                gates=s.get("gates", []),
            )
        )
    return defs


def load_workflows(root: str) -> List[Workflow]:
    data = _load_yaml(os.path.join(root, ".sdlc", "workflows.yaml"))
    workflows = []
    for w in data.get("workflows", []):
        workflows.append(
            Workflow(
                id=w["id"],
                name=w["name"],
                from_stage=w["from_stage"],
                to_stage=w["to_stage"],
                description=w["description"],
                agent=w.get("agent"),
                skill=w.get("skill"),
                preconditions=w.get("preconditions", []),
                outputs=w.get("outputs", []),
            )
        )
    return workflows


def load_agents(root: str) -> List[Agent]:
    data = _load_yaml(os.path.join(root, ".sdlc", "agents.yaml"))
    agents = []
    for a in data.get("agents", []):
        agents.append(
            Agent(
                id=a["id"],
                name=a["name"],
                stages=a.get("stages", []),
                description=a["description"],
                primary_skill=a.get("primary_skill"),
            )
        )
    return agents


def load_skills(root: str) -> List[Skill]:
    data = _load_yaml(os.path.join(root, ".sdlc", "skills.yaml"))
    skills = []
    for s in data.get("skills", []):
        skills.append(
            Skill(
                id=s["id"],
                name=s["name"],
                stages=s.get("stages", []),
                description=s["description"],
                expected_outputs=s.get("expected_outputs", []),
            )
        )
    return skills


def load_rules(root: str) -> List[Rule]:
    data = _load_yaml(os.path.join(root, ".sdlc", "rules.yaml"))
    rules = []
    for r in data.get("rules", []):
        rules.append(
            Rule(
                id=r["id"],
                name=r["name"],
                severity=r["severity"],
                description=r["description"],
                enforced_at=r.get("enforced_at", []),
            )
        )
    return rules


def load_integrations(root: str) -> List[Integration]:
    data = _load_yaml(os.path.join(root, ".sdlc", "integrations.yaml"))
    integrations = []
    for i in data.get("integrations", []):
        integrations.append(
            Integration(
                id=i["id"],
                name=i["name"],
                status=i["status"],
                description=i["description"],
                config_env=i.get("config_env"),
                capabilities=i.get("capabilities", []),
                notes=i.get("notes"),
            )
        )
    return integrations


def load_sdlc_config(root: str) -> SDLCConfig:
    """Load the complete SDLC configuration from the repository root."""
    main = _load_yaml(os.path.join(root, ".sdlc", "sdlc.yaml"))
    return SDLCConfig(
        version=main.get("version", "unknown"),
        name=main.get("name", "unknown"),
        description=main.get("description", ""),
        lifecycle_stages=load_lifecycle(root),
        stage_definitions=load_stages(root),
        workflows=load_workflows(root),
        agents=load_agents(root),
        skills=load_skills(root),
        rules=load_rules(root),
        integrations=load_integrations(root),
    )
