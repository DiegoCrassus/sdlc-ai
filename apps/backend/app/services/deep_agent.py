"""LangChain Deep Agent foundation for RPG-OP backend."""

from __future__ import annotations

from functools import lru_cache
from typing import Any

from pydantic import BaseModel, Field

from app.config import settings


class DeepAgentCapability(BaseModel):
    key: str
    description: str


class DeepAgentStatus(BaseModel):
    name: str = "rpg-op-deep-agent"
    enabled: bool = True
    model: str
    provider: str = "langchain-deepagents"
    capabilities: list[DeepAgentCapability] = Field(default_factory=list)
    runtime_importable: bool


def _capabilities() -> list[DeepAgentCapability]:
    return [
        DeepAgentCapability(
            key="template_analysis",
            description="Prepare orchestration for future sheet template analysis workflows.",
        ),
        DeepAgentCapability(
            key="human_in_the_loop",
            description="Keep publish and destructive operations behind explicit human approval.",
        ),
        DeepAgentCapability(
            key="tool_orchestration",
            description="Provide a single backend entry point for future LangChain tools.",
        ),
    ]


def is_deepagents_available() -> bool:
    try:
        import deepagents  # noqa: F401
    except ImportError:
        return False
    return True


def get_deep_agent_status() -> DeepAgentStatus:
    return DeepAgentStatus(
        model=settings.agent_model,
        capabilities=_capabilities(),
        runtime_importable=is_deepagents_available(),
    )


@lru_cache
def build_deep_agent() -> Any:
    """Build the Deep Agent lazily so imports and tests do not require LLM credentials."""
    from deepagents import create_deep_agent

    return create_deep_agent(
        model=settings.agent_model,
        tools=[],
        system_prompt=(
            "You are the RPG-OP backend deep agent. Coordinate sheet template "
            "analysis workflows and require human approval before publishing changes."
        ),
    )
