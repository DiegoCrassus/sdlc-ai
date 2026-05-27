#!/usr/bin/env python3
"""Plane work item state transitions for SDLC workflow."""

from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

import httpx

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from plane_evidence import build_completion_evidence, build_start_comment  # noqa: E402
from plane_html import document, paragraph_text  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT_ID = "04ac3a5d-7457-40f3-b94f-fccd4c29a589"
STATE_IDS = {
    "backlog": "afa03d47-1db7-4224-8455-c8fa1290d871",
    "todo": "ab4b3f48-5a3f-4f33-a912-41f85475cf48",
    "in_progress": "c0c41658-211c-4f30-9ffc-ecf39dacb99f",
    "done": "13f60172-30af-40b3-9894-64f8a184656b",
    "cancelled": "c8e2af1b-9a32-43c2-9288-f58ac31fe6ee",
}
CARD_RE = re.compile(r"^INVES-(\d+)$", re.IGNORECASE)


def _load_dotenv() -> None:
    env_path = ROOT / ".env"
    if not env_path.is_file():
        return
    for line in env_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        os.environ.setdefault(key.strip(), val.strip().strip('"').strip("'"))


def _api() -> tuple[str, str, str]:
    _load_dotenv()
    api_key = os.environ.get("PLANE_API_KEY")
    workspace = os.environ.get("PLANE_WORKSPACE_SLUG", "investments-sdlc")
    project_id = os.environ.get("PLANE_PROJECT_ID", DEFAULT_PROJECT_ID)
    if not api_key:
        print("ERROR: PLANE_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    return api_key, workspace, project_id


def _headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key, "Content-Type": "application/json"}


def parse_card(card: str) -> int:
    m = CARD_RE.match(card.strip())
    if not m:
        print(f"ERROR: invalid card {card!r} — expected INVES-N", file=sys.stderr)
        sys.exit(1)
    return int(m.group(1))


def find_issue_uuid(api_key: str, workspace: str, project_id: str, sequence_id: int) -> str:
    url = f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/{project_id}/issues/"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_headers(api_key), params={"per_page": 100})
        resp.raise_for_status()
        for item in resp.json().get("results", []):
            if item.get("sequence_id") == sequence_id:
                return item["id"]
    print(f"ERROR: INVES-{sequence_id} not found", file=sys.stderr)
    sys.exit(1)


def set_state(api_key: str, workspace: str, project_id: str, issue_uuid: str, state_key: str) -> dict:
    url = (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/"
        f"{project_id}/issues/{issue_uuid}/"
    )
    with httpx.Client(timeout=30.0) as client:
        resp = client.patch(
            url, headers=_headers(api_key), json={"state": STATE_IDS[state_key]}
        )
        resp.raise_for_status()
        return resp.json()


def add_comment_html(
    api_key: str, workspace: str, project_id: str, issue_uuid: str, html: str
) -> None:
    url = (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/"
        f"{project_id}/issues/{issue_uuid}/comments/"
    )
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, headers=_headers(api_key), json={"comment_html": html})
        resp.raise_for_status()


def wrap_comment(comment: str) -> str:
    if comment.strip().startswith("<div"):
        return comment
    if comment.strip().startswith("<"):
        return document(paragraph_text(comment))
    return document(paragraph_text(comment))


def main() -> None:
    parser = argparse.ArgumentParser(description="Plane card state transitions")
    sub = parser.add_subparsers(dest="command", required=True)

    for name, state_key in (
        ("in-progress", "in_progress"),
        ("done", "done"),
        ("todo", "todo"),
        ("backlog", "backlog"),
        ("cancelled", "cancelled"),
    ):
        p = sub.add_parser(name)
        p.add_argument("--card", required=True)
        p.add_argument("--comment", default="")
        p.add_argument("--branch", default="", help="For in-progress start comment")
        p.add_argument("--evidence-file", default="", help="JSON completion evidence (done)")
        p.set_defaults(state_key=state_key)

    c = sub.add_parser("comment")
    c.add_argument("--card", required=True)
    c.add_argument("--comment", default="")
    c.add_argument("--evidence-file", default="")
    c.set_defaults(state_key=None)

    args = parser.parse_args()
    api_key, workspace, project_id = _api()
    seq = parse_card(args.card)
    issue_uuid = find_issue_uuid(api_key, workspace, project_id, seq)

    html_comment = ""
    if args.evidence_file:
        import json

        data = json.loads(Path(args.evidence_file).read_text(encoding="utf-8"))
        data.setdefault("card", args.card)
        html_comment = build_completion_evidence(data)
    elif args.command == "in-progress" and args.branch:
        html_comment = build_start_comment(args.card, args.branch)
    elif args.comment:
        html_comment = wrap_comment(args.comment)

    if args.command == "comment":
        if not html_comment:
            sys.exit("ERROR: --comment or --evidence-file required")
        add_comment_html(api_key, workspace, project_id, issue_uuid, html_comment)
        print(f"OK: comment on INVES-{seq}")
        return

    data = set_state(api_key, workspace, project_id, issue_uuid, args.state_key)
    state_name = (data.get("state_detail") or {}).get("name", args.state_key)
    print(f"OK: INVES-{seq} -> {state_name}")
    if html_comment:
        add_comment_html(api_key, workspace, project_id, issue_uuid, html_comment)


if __name__ == "__main__":
    main()
