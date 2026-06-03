from __future__ import annotations

from pathlib import Path

import pytest

from app.infra.sdlc_obs.store import EventStore, build_correlation_id


@pytest.fixture
def store(tmp_path: Path) -> EventStore:
    return EventStore(tmp_path / "obs.db")


def test_append_event_has_schema_version_and_correlation_id(store: EventStore) -> None:
    event = store.append_event(
        event_type="gateway.shell_denied",
        source="sdlc_pre_gateway",
        category="gateway",
        correlation={"run_id": "run-1", "card": "INVES-82"},
        payload={"command": "rm -rf /", "reason": "blocked"},
    )
    assert event["schema_version"] == "1.0"
    assert event["category"] == "gateway"
    assert event["correlation_id"] == build_correlation_id(
        {"run_id": "run-1", "card": "INVES-82"}
    )


def test_build_timeline_orders_events(store: EventStore) -> None:
    store.append_event(
        event_type="handoff.updated",
        source="handoff_watcher",
        category="handoff",
        timestamp="2026-06-03T12:00:01Z",
        payload={"next_agent": "qa"},
    )
    store.append_event(
        event_type="gateway.shell_denied",
        source="sdlc_pre_gateway",
        category="gateway",
        timestamp="2026-06-03T12:00:02Z",
        payload={"command": "curl evil"},
    )
    timeline = store.build_timeline(limit=10)
    assert [event["category"] for event in timeline] == ["handoff", "gateway"]
    assert all(event["schema_version"] == "1.0" for event in timeline)


def test_build_timeline_category_filter(store: EventStore) -> None:
    store.append_event(
        event_type="gate.write_denied",
        source="sdlc_gate_hook",
        category="gate",
        timestamp="2026-06-03T12:00:03Z",
        payload={"path": "app/backend/foo.py"},
    )
    store.append_event(
        event_type="gateway.shell_denied",
        source="sdlc_pre_gateway",
        category="gateway",
        timestamp="2026-06-03T12:00:04Z",
        payload={"command": "bad"},
    )
    timeline = store.build_timeline(limit=10, category="gate")
    assert len(timeline) == 1
    assert timeline[0]["category"] == "gate"
