"""Dataclass models for SDLC YAML structures."""

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class LifecycleStage:
    id: str
    name: str
    order: int
    description: str


@dataclass
class StageDefinition:
    id: str
    name: str
    objective: str
    inputs: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)
    required_evidence: List[str] = field(default_factory=list)
    gates: List[str] = field(default_factory=list)


@dataclass
class Workflow:
    id: str
    name: str
    from_stage: str
    to_stage: str
    description: str
    agent: Optional[str] = None
    skill: Optional[str] = None
    preconditions: List[str] = field(default_factory=list)
    outputs: List[str] = field(default_factory=list)


@dataclass
class Agent:
    id: str
    name: str
    stages: List[str]
    description: str
    primary_skill: Optional[str] = None


@dataclass
class Skill:
    id: str
    name: str
    stages: List[str]
    description: str
    expected_outputs: List[str] = field(default_factory=list)


@dataclass
class Rule:
    id: str
    name: str
    severity: str  # required | warning
    description: str
    enforced_at: List[str] = field(default_factory=list)


@dataclass
class Integration:
    id: str
    name: str
    status: str  # placeholder | not_configured | active
    description: str
    config_env: Optional[str] = None
    capabilities: List[str] = field(default_factory=list)
    notes: Optional[str] = None


@dataclass
class SDLCConfig:
    version: str
    name: str
    description: str
    lifecycle_stages: List[LifecycleStage] = field(default_factory=list)
    stage_definitions: List[StageDefinition] = field(default_factory=list)
    workflows: List[Workflow] = field(default_factory=list)
    agents: List[Agent] = field(default_factory=list)
    skills: List[Skill] = field(default_factory=list)
    rules: List[Rule] = field(default_factory=list)
    integrations: List[Integration] = field(default_factory=list)
