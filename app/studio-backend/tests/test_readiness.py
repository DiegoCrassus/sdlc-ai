from __future__ import annotations


def test_readiness_wraps_studio_engine(client) -> None:
    response = client.get("/studio/readiness")
    assert response.status_code == 200
    body = response.json()
    assert "readiness" in body
    assert "summary" in body
    assert "checks" in body
    assert body["readiness"]["id"] == "readiness.sdlc_studio.mvp"


def test_session_gate(client) -> None:
    response = client.get("/studio/session/gate")
    assert response.status_code == 200
    body = response.json()
    assert body["present"] is True
    assert body["gate"]["card"] == "INVES-78"


def test_session_handoff(client) -> None:
    response = client.get("/studio/session/handoff")
    assert response.status_code == 200
    body = response.json()
    assert body["present"] is True
    assert body["sections"]["Routing"]["Next agent"] in ("implementer", "qa")


def test_dashboard_summary(client) -> None:
    response = client.get("/studio/dashboard/summary")
    assert response.status_code == 200
    body = response.json()
    assert "readiness" in body
    assert "session" in body
    assert "canvas" in body
    assert body["canvas"]["available"] is True
    assert body["canvas"]["nodes"] > 0


def test_engine_compile_validate_canvas(client) -> None:
    compile_resp = client.post("/studio/engine/compile", json={})
    assert compile_resp.status_code == 200
    assert "graph_ir" in compile_resp.json()

    validate_resp = client.post("/studio/engine/validate", json={})
    assert validate_resp.status_code == 200
    assert "summary" in validate_resp.json()

    canvas_resp = client.get("/studio/engine/canvas")
    assert canvas_resp.status_code == 200
    canvas = canvas_resp.json()
    assert "nodes" in canvas
    assert "edges" in canvas
