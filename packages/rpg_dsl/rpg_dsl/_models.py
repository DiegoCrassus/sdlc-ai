"""IR (internal representation) — normalised spec objects."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class PresentationType(str, Enum):
    FIELD_GRID = "field_grid"
    STAT_ROW = "stat_row"
    RICH_TEXT = "rich_text"


@dataclass
class FieldSpec:
    key: str
    label: str
    type: str = "string"
    required: bool = False
    min: int | None = None
    max: int | None = None
    computed: str | None = None
    default: Any = None


@dataclass
class RegionSpec:
    id: str
    title: str
    order: int
    presentation: PresentationType
    fields: list[str]
    columns: int = 2


@dataclass
class CanvasSpec:
    name: str
    version: int
    regions: list[RegionSpec] = field(default_factory=list)
    source_class: type | None = None


@dataclass
class SheetSpec:
    name: str
    version: int
    fields: list[FieldSpec] = field(default_factory=list)
    migrations_from: list[int] = field(default_factory=list)
    source_class: type | None = None


@dataclass
class SubAgentSpec:
    name: str
    response_model: str
    skills: list[str] = field(default_factory=list)
    source_class: type | None = None


@dataclass
class EvalAssertion:
    type: str
    value: str


@dataclass
class EvalSpec:
    suite: str
    tags: list[str]
    fixture: str
    user_message: str
    assertions: list[EvalAssertion] = field(default_factory=list)
    source_class: type | None = None


@dataclass
class RouteSpec:
    method: str
    path: str
    response: str | None = None
    stream: bool = False
    body: str | None = None


@dataclass
class ApiSpec:
    prefix: str
    tag: str
    routes: list[RouteSpec] = field(default_factory=list)
    source_class: type | None = None
