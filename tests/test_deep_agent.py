"""Tests for the backend Deep Agent foundation."""

from app.services.deep_agent import get_deep_agent_status


def test_deep_agent_status_is_available_without_llm_credentials():
    status = get_deep_agent_status()

    assert status.name == "rpg-op-deep-agent"
    assert status.enabled is True
    assert status.model
    assert {capability.key for capability in status.capabilities} >= {
        "template_analysis",
        "human_in_the_loop",
        "tool_orchestration",
    }
