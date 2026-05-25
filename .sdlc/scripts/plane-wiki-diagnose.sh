#!/usr/bin/env bash
# Diagnose Plane wiki/pages: list project pages and workspace wiki.
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

[[ -n "${PLANE_API_KEY:-}" ]] || { echo "error: PLANE_API_KEY not set" >&2; exit 1; }
[[ -n "${PLANE_WORKSPACE_SLUG:-}" ]] || { echo "error: PLANE_WORKSPACE_SLUG not set" >&2; exit 1; }

BASE="${PLANE_BASE_URL:-https://api.plane.so}"
BASE="${BASE%/}"
SLUG="$PLANE_WORKSPACE_SLUG"

export PLANE_BASE="$BASE"
export PLANE_SLUG="$SLUG"
export PLANE_API_KEY="$PLANE_API_KEY"

python3 << 'PY'
import json
import os
import urllib.error
import urllib.request

base = os.environ["PLANE_BASE"]
slug = os.environ["PLANE_SLUG"]
key = os.environ["PLANE_API_KEY"]
headers = {"x-api-key": key, "Accept": "application/json"}


def req(url):
    r = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"GET {url} -> {e.code}: {body[:300]}")


print("== Plane wiki diagnostic ==")
print(f"Workspace: {slug}")

projects = req(f"{base}/api/v1/workspaces/{slug}/projects/")
for p in projects.get("results", []):
    print()
    print(f"Project: {p.get('name')} ({p.get('identifier')}) id={p.get('id')}")
    print(f"  pages_view enabled: {p.get('page_view')}")

    pages_url = f"{base}/api/v1/workspaces/{slug}/projects/{p['id']}/pages/"
    print(f"  GET {pages_url}")
    try:
        pages_resp = req(pages_url)
        page_list = pages_resp.get("results", [])
        print(f"  Pages count: {len(page_list)}")
        for page in page_list:
            print(f"    - {page.get('name')} id={page.get('id')}")
            print(
                f"      URL: https://app.plane.so/{slug}/projects/{p.get('identifier')}/pages/{page.get('id')}"
            )
    except RuntimeError as exc:
        print(f"  LIST FAILED: {exc}")

ws_pages_url = f"{base}/api/v1/workspaces/{slug}/pages/"
print()
print(f"Workspace WIKI: GET {ws_pages_url}")
try:
    ws_pages = req(ws_pages_url)
    ws_list = ws_pages.get("results", [])
    print(f"Wiki pages count: {len(ws_list)}")
    for page in ws_list:
        print(f"  - {page.get('name')} id={page.get('id')}")
        print(f"    URL: https://app.plane.so/{slug}/wiki/{page.get('id')}")
except RuntimeError as exc:
    print(f"Wiki LIST FAILED: {exc}")
PY
