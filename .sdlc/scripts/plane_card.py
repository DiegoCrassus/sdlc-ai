#!/usr/bin/env python3
"""Plane card formatting and evidence publishing."""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from pathlib import Path

import httpx

SCRIPTS = Path(__file__).resolve().parent
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from plane_evidence import build_completion_evidence, build_start_comment  # noqa: E402
from plane_html import convert_legacy_description  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROJECT_ID = "04ac3a5d-7457-40f3-b94f-fccd4c29a589"
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
        sys.exit("ERROR: PLANE_API_KEY not set")
    return api_key, workspace, project_id


def _headers(api_key: str) -> dict[str, str]:
    return {"X-API-Key": api_key, "Content-Type": "application/json"}


def parse_card(card: str) -> int:
    m = CARD_RE.match(card.strip())
    if not m:
        sys.exit(f"ERROR: invalid card {card!r}")
    return int(m.group(1))


def find_issue_uuid(api_key: str, workspace: str, project_id: str, sequence_id: int) -> str:
    url = f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/{project_id}/issues/"
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_headers(api_key), params={"per_page": 100})
        resp.raise_for_status()
        for item in resp.json().get("results", []):
            if item.get("sequence_id") == sequence_id:
                return item["id"]
    sys.exit(f"ERROR: INVES-{sequence_id} not found")


def get_issue(api_key: str, workspace: str, project_id: str, issue_uuid: str) -> dict:
    url = (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/"
        f"{project_id}/issues/{issue_uuid}/"
    )
    with httpx.Client(timeout=30.0) as client:
        resp = client.get(url, headers=_headers(api_key))
        resp.raise_for_status()
        return resp.json()


def patch_description(
    api_key: str, workspace: str, project_id: str, issue_uuid: str, html: str
) -> None:
    url = (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/"
        f"{project_id}/issues/{issue_uuid}/"
    )
    with httpx.Client(timeout=30.0) as client:
        resp = client.patch(url, headers=_headers(api_key), json={"description_html": html})
        resp.raise_for_status()


def post_comment(
    api_key: str, workspace: str, project_id: str, issue_uuid: str, html: str
) -> None:
    url = (
        f"https://api.plane.so/api/v1/workspaces/{workspace}/projects/"
        f"{project_id}/issues/{issue_uuid}/comments/"
    )
    with httpx.Client(timeout=30.0) as client:
        resp = client.post(url, headers=_headers(api_key), json={"comment_html": html})
        resp.raise_for_status()


def reformat_description(card: str) -> None:
    api_key, workspace, project_id = _api()
    seq = parse_card(card)
    uuid = find_issue_uuid(api_key, workspace, project_id, seq)
    issue = get_issue(api_key, workspace, project_id, uuid)
    old = issue.get("description_html") or ""
    new = convert_legacy_description(old)
    patch_description(api_key, workspace, project_id, uuid, new)
    print(f"OK: reformatted description INVES-{seq}")


def post_evidence(card: str, data: dict, *, replace: bool = False) -> None:
    api_key, workspace, project_id = _api()
    seq = parse_card(card)
    uuid = find_issue_uuid(api_key, workspace, project_id, seq)
    data.setdefault("card", card)
    html = build_completion_evidence(data)
    if replace:
        patch_description(api_key, workspace, project_id, uuid, html)
        print(f"OK: evidence appended to description INVES-{seq}")
    else:
        post_comment(api_key, workspace, project_id, uuid, html)
        print(f"OK: evidence comment on INVES-{seq}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Plane formatting and evidence")
    sub = parser.add_subparsers(dest="command", required=True)

    r = sub.add_parser("reformat-description", help="Upgrade description to TipTap HTML")
    r.add_argument("--card", required=True)

    e = sub.add_parser("post-evidence", help="Post structured Done evidence comment")
    e.add_argument("--card", required=True)
    e.add_argument("--file", required=True, help="JSON evidence file")
    e.add_argument(
        "--append-to-description",
        action="store_true",
        help="Also append evidence block to card description",
    )

    b = sub.add_parser("reformat-all", help="Reformat INVES-19..24 descriptions")

    args = parser.parse_args()
    if args.command == "reformat-description":
        reformat_description(args.card)
    elif args.command == "post-evidence":
        data = json.loads(Path(args.file).read_text(encoding="utf-8"))
        post_evidence(args.card, data, replace=args.append_to_description)
    elif args.command == "reformat-all":
        for n in range(19, 25):
            reformat_description(f"INVES-{n}")


if __name__ == "__main__":
    main()
