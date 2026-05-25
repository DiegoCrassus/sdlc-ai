"""Public decorator API consumed by specs/*.py files."""

from __future__ import annotations

from typing import Any

from ._models import (
    ApiSpec,
    CanvasSpec,
    EvalAssertion,
    EvalSpec,
    FieldSpec,
    PresentationType,
    RegionSpec,
    RouteSpec,
    SheetSpec,
    SubAgentSpec,
)
from ._registry import register

# Re-export for spec authors
Presentation = PresentationType


# ---------------------------------------------------------------------------
# Field helpers
# ---------------------------------------------------------------------------


class Field:
    """Used inside @Canvas regions: Field.key("character_name")."""

    def __init__(
        self,
        key: str,
        *,
        label: str = "",
        type: str = "string",
        required: bool = False,
        min: int | None = None,
        max: int | None = None,
        computed: str | None = None,
        default: Any = None,
    ) -> None:
        self._spec = FieldSpec(
            key=key,
            label=label,
            type=type,
            required=required,
            min=min,
            max=max,
            computed=computed,
            default=default,
        )

    @classmethod
    def key(cls, key: str) -> str:
        """Shorthand: just reference a field by key (used in Region.fields)."""
        return key

    def __str__(self) -> str:
        return self._spec.key


# ---------------------------------------------------------------------------
# Region
# ---------------------------------------------------------------------------


class Region:
    def __init__(
        self,
        *,
        title: str,
        order: int,
        presentation: PresentationType,
        fields: list[str],
        columns: int = 2,
        id: str | None = None,
    ) -> None:
        self._spec = RegionSpec(
            id=id or title.lower().replace(" ", "_"),
            title=title,
            order=order,
            presentation=presentation,
            fields=fields,
            columns=columns,
        )

    def _as_spec(self) -> RegionSpec:
        return self._spec


# ---------------------------------------------------------------------------
# @Canvas
# ---------------------------------------------------------------------------


class Canvas:
    def __init__(self, *, version: int = 1) -> None:
        self._version = version

    def __call__(self, cls: type) -> type:
        regions: list[RegionSpec] = []
        for attr_name in dir(cls):
            if attr_name.startswith("_"):
                continue
            val = getattr(cls, attr_name, None)
            if isinstance(val, Region):
                regions.append(val._as_spec())

        regions.sort(key=lambda r: r.order)

        spec = CanvasSpec(
            name=cls.__name__,
            version=self._version,
            regions=regions,
            source_class=cls,
        )
        register("canvas", spec)
        cls._rpg_spec = spec  # type: ignore[attr-defined]
        return cls


# ---------------------------------------------------------------------------
# @Sheet — declarative sheet schema
# ---------------------------------------------------------------------------


def sheet_field(
    key: str,
    label: str,
    type: str = "string",
    *,
    required: bool = False,
    min: int | None = None,
    max: int | None = None,
    computed: str | None = None,
    default: Any = None,
) -> FieldSpec:
    """Helper to declare a field inside a @Sheet class body."""
    return FieldSpec(
        key=key,
        label=label,
        type=type,
        required=required,
        min=min,
        max=max,
        computed=computed,
        default=default,
    )


class Sheet:
    def __init__(self, *, version: int = 1, migrations_from: list[int] | None = None) -> None:
        self._version = version
        self._migrations_from = migrations_from or []

    def __call__(self, cls: type) -> type:
        fields: list[FieldSpec] = []
        # vars() preserves declaration order (Python 3.7+)
        for attr_name, val in vars(cls).items():
            if attr_name.startswith("_"):
                continue
            if isinstance(val, FieldSpec):
                if not val.key:
                    val.key = attr_name
                fields.append(val)

        spec = SheetSpec(
            name=cls.__name__,
            version=self._version,
            fields=fields,
            migrations_from=self._migrations_from,
            source_class=cls,
        )
        register("sheet", spec)
        cls._rpg_spec = spec  # type: ignore[attr-defined]
        return cls


# ---------------------------------------------------------------------------
# @SubAgent
# ---------------------------------------------------------------------------


class SubAgent:
    def __init__(self, *, name: str, response_model: str) -> None:
        self._name = name
        self._response_model = response_model

    def __call__(self, cls: type) -> type:
        skills: list[str] = getattr(cls, "skills", [])
        spec = SubAgentSpec(
            name=self._name,
            response_model=self._response_model,
            skills=list(skills),
            source_class=cls,
        )
        register("subagent", spec)
        cls._rpg_spec = spec  # type: ignore[attr-defined]
        return cls


# ---------------------------------------------------------------------------
# @Eval + assertion builders
# ---------------------------------------------------------------------------


def assert_contains(value: str) -> EvalAssertion:
    return EvalAssertion(type="contains", value=value)


def assert_tool_called(name: str) -> EvalAssertion:
    return EvalAssertion(type="tool_called", value=name)


def assert_not_contains(value: str) -> EvalAssertion:
    return EvalAssertion(type="not_contains", value=value)


class Eval:
    def __init__(self, *, suite: str, tags: list[str] | None = None) -> None:
        self._suite = suite
        self._tags = tags or []

    def __call__(self, cls: type) -> type:
        spec = EvalSpec(
            suite=self._suite,
            tags=self._tags,
            fixture=getattr(cls, "fixture", ""),
            user_message=getattr(cls, "user_message", ""),
            assertions=list(getattr(cls, "assertions", [])),
            source_class=cls,
        )
        register("eval", spec)
        cls._rpg_spec = spec  # type: ignore[attr-defined]
        return cls


# ---------------------------------------------------------------------------
# @api + HTTP verb decorators
# ---------------------------------------------------------------------------


def _http_method(method: str):
    def decorator(
        path: str, *, response: str | None = None, stream: bool = False, body: str | None = None
    ):
        def inner(fn):
            fn._rpg_route = RouteSpec(
                method=method,
                path=path,
                response=response,
                stream=stream,
                body=body,
            )
            return fn

        return inner

    return decorator


GET = _http_method("GET")
POST = _http_method("POST")
PUT = _http_method("PUT")
DELETE = _http_method("DELETE")
PATCH = _http_method("PATCH")


class api:  # noqa: N801
    def __init__(self, *, prefix: str, tag: str) -> None:
        self._prefix = prefix
        self._tag = tag

    def __call__(self, cls: type) -> type:
        routes: list[RouteSpec] = []
        for attr_name in vars(cls):
            fn = getattr(cls, attr_name, None)
            if callable(fn) and hasattr(fn, "_rpg_route"):
                routes.append(fn._rpg_route)

        spec = ApiSpec(
            prefix=self._prefix,
            tag=self._tag,
            routes=routes,
            source_class=cls,
        )
        register("api", spec)
        cls._rpg_spec = spec  # type: ignore[attr-defined]
        return cls
