#!/usr/bin/env python3
"""Pre-interaction SDLC gateway for shell and subagent starts."""

from __future__ import annotations

import json
import re
import sys

from sdlc_gateway_lib import (
    allow,
    deny,
    extract_command,
    extract_subagent,
    require_policy,
    routing,
)


def deny_unsafe_shell(command: str, policy: dict) -> None:
    if not command:
        return
    pre_policy = policy.get("pre_gateway") or {}
    for pattern in pre_policy.get("deny_shell_patterns") or []:
        if re.search(pattern, command):
            deny(
                pre_policy.get(
                    "deny_message",
                    "Deterministic SDLC gateway blocked this shell command.",
                ),
                (
                    "The command matched a deterministic deny pattern "
                    f"({pattern!r}). Return to the previous SDLC step and use the "
                    "approved workflow instead."
                ),
                event_type="gateway.shell_denied",
                event_payload={"command": command, "matcher": pattern},
            )


def enforce_next_subagent(payload: dict, policy: dict) -> None:
    requested = extract_subagent(payload)
    if not requested:
        return

    valid_agents = set(policy.get("valid_agents") or [])
    generic_agents = {"explore", "generalpurpose", "general-purpose", "shell"}
    if requested not in valid_agents and requested not in generic_agents:
        return

    current = routing(policy)
    expected = current.get("next_agent", "")
    if not expected or expected == "none":
        return

    # Exploration and generic agents are allowed when they are only gathering context.
    if requested in generic_agents:
        return

    if requested == expected:
        return

    deny(
        "SDLC gateway: subagent does not match the current handoff route.",
        (
            f"The handoff expects '{expected}', but this interaction requested "
            f"'{requested}'. Read `.sdlc/memory/orchestrator-handoff.md` and "
            "return to the routed step before continuing."
        ),
        event_type="gateway.subagent_start",
        event_payload={
            "subagent_type": requested,
            "expected_agent": expected,
            "allowed": False,
        },
    )


def main() -> None:
    try:
        payload = json.loads(sys.stdin.read() or "{}")
        if not isinstance(payload, dict):
            payload = {}
    except json.JSONDecodeError:
        deny('SDLC gateway: invalid hook payload.', 'Non-JSON stdin.')

    policy = require_policy()

    deny_unsafe_shell(extract_command(payload), policy)
    enforce_next_subagent(payload, policy)
    allow()


if __name__ == "__main__":
    main()
