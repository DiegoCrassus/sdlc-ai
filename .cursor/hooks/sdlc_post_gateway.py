#!/usr/bin/env python3
"""Post-interaction SDLC gateway for deterministic handoff validation."""

from __future__ import annotations

import json
import sys

from sdlc_gateway_lib import (
    fallback_for,
    handoff_value,
    load_policy,
    normalize_agent,
    parse_handoff,
    read_handoff,
    routing,
    validate_handoff,
)


def blockers_are_clear(blockers: str) -> bool:
    lines = [line.strip(" -\t").strip().lower() for line in blockers.splitlines()]
    meaningful = [line for line in lines if line]
    if not meaningful:
        return True
    clear_values = {"none", "no", "n/a", "na", "—", "-"}
    return all(
        line in clear_values
        or line.startswith("none for ")
        or line.startswith("no blockers")
        or line.startswith("no blocker")
        for line in meaningful
    )


def followup(agent: str, reason: str, details: list[str]) -> None:
    route = normalize_agent(agent) or "planner"
    detail_text = "\n".join(f"- {item}" for item in details) if details else "- unspecified"
    message = f"""SDLC deterministic gateway blocked stage advancement.

Return to `{route}` before continuing.

Reason: {reason}

Details:
{detail_text}

Required action:
- Re-run or resume `{route}` with the current `.sdlc/memory/orchestrator-handoff.md`.
- Fix the missing evidence or blocker.
- Write a complete Markdown handoff before advancing again.
"""
    print(json.dumps({"followup_message": message}))
    sys.exit(0)


def main() -> None:
    # Read and ignore the event payload for now; the repository handoff is the
    # deterministic source for routing after subagents stop.
    sys.stdin.read()

    policy = load_policy()
    if not policy:
        sys.exit(0)

    problems = validate_handoff(policy)
    route = routing(policy)
    previous = route.get("previous_agent") or "planner"
    next_agent = route.get("next_agent") or ""

    if problems:
        followup(
            previous or fallback_for(next_agent, policy),
            "handoff contract is incomplete",
            problems,
        )

    parsed = parse_handoff(read_handoff())
    stage_complete = handoff_value(parsed, "Routing", "Stage complete").lower()
    blockers = (parsed.get("sections") or {}).get("Blockers", "")

    if (
        (policy.get("post_gateway") or {}).get("reroute_on_incomplete_stage", True)
        and stage_complete == "no"
    ):
        target = next_agent if next_agent and next_agent != "none" else previous
        followup(
            target,
            "stage is explicitly incomplete",
            ["Routing.Stage complete is `no`"],
        )

    if (
        (policy.get("post_gateway") or {}).get("reroute_on_blockers", True)
        and not blockers_are_clear(blockers)
    ):
        target = next_agent if next_agent and next_agent != "none" else fallback_for(previous, policy)
        followup(
            target,
            "handoff contains unresolved blockers",
            [line for line in blockers.splitlines() if line.strip()],
        )

    sys.exit(0)


if __name__ == "__main__":
    main()
