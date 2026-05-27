"""Schema-level consistency validation for SDLC configuration."""

from typing import List, Tuple

from .models import SDLCConfig

# (level, message)
Finding = Tuple[str, str]


def validate(config: SDLCConfig) -> List[Finding]:
    """Run all consistency checks. Returns list of (level, message) findings."""
    findings: List[Finding] = []

    lifecycle_ids = {s.id for s in config.lifecycle_stages}
    stage_def_ids = {s.id for s in config.stage_definitions}
    agent_ids = {a.id for a in config.agents}
    skill_ids = {s.id for s in config.skills}

    # Lifecycle vs stage definitions parity
    for lid in lifecycle_ids:
        if lid not in stage_def_ids:
            findings.append(
                ("WARN", f"Lifecycle stage '{lid}' has no entry in stages.yaml")
            )
    for sid in stage_def_ids:
        if sid not in lifecycle_ids:
            findings.append(
                ("WARN", f"Stage definition '{sid}' not found in lifecycle.yaml")
            )

    # Workflow references
    for wf in config.workflows:
        if wf.from_stage not in lifecycle_ids:
            findings.append(
                (
                    "FAIL",
                    f"Workflow '{wf.id}' references unknown from_stage '{wf.from_stage}'",
                )
            )
        if wf.to_stage not in lifecycle_ids:
            findings.append(
                (
                    "FAIL",
                    f"Workflow '{wf.id}' references unknown to_stage '{wf.to_stage}'",
                )
            )
        if wf.agent and wf.agent not in agent_ids:
            findings.append(
                (
                    "FAIL",
                    f"Workflow '{wf.id}' references unknown agent '{wf.agent}'",
                )
            )
        if wf.skill and wf.skill not in skill_ids:
            findings.append(
                (
                    "FAIL",
                    f"Workflow '{wf.id}' references unknown skill '{wf.skill}'",
                )
            )

    # Agent stage references
    for agent in config.agents:
        for stage in agent.stages:
            if stage not in lifecycle_ids:
                findings.append(
                    (
                        "FAIL",
                        f"Agent '{agent.id}' references unknown stage '{stage}'",
                    )
                )
        if agent.primary_skill and agent.primary_skill not in skill_ids:
            findings.append(
                (
                    "FAIL",
                    f"Agent '{agent.id}' references unknown skill '{agent.primary_skill}'",
                )
            )

    # Skill stage references
    for skill in config.skills:
        for stage in skill.stages:
            if stage not in lifecycle_ids:
                findings.append(
                    (
                        "WARN",
                        f"Skill '{skill.id}' references unknown stage '{stage}'",
                    )
                )

    # Rule severity values
    valid_severities = {"required", "warning"}
    for rule in config.rules:
        if rule.severity not in valid_severities:
            findings.append(
                (
                    "FAIL",
                    f"Rule '{rule.id}' has invalid severity '{rule.severity}' (expected: required|warning)",
                )
            )

    # Integration status values
    valid_statuses = {"placeholder", "not_configured", "active", "deprecated"}
    for integration in config.integrations:
        if integration.status not in valid_statuses:
            findings.append(
                (
                    "WARN",
                    f"Integration '{integration.id}' has unknown status '{integration.status}'",
                )
            )

    return findings
