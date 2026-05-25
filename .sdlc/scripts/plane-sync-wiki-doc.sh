#!/usr/bin/env bash
# Sync markdown doc to Plane workspace wiki.
# Usage: .sdlc/scripts/plane-sync-wiki-doc.sh docs/05-roadmap.md [page-name] [scope]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

DOC_PATH="${1:?Usage: plane-sync-wiki-doc.sh <doc-path> [page-name] [workspace|project]}"
PAGE_NAME="${2:-}"
SCOPE="${3:-workspace}"
REPLACE_PAGE_ID="${REPLACE_PAGE_ID:-}"

FULL_DOC="$SDLC_REPO_ROOT/$DOC_PATH"
[[ -f "$FULL_DOC" ]] || { echo "error: doc not found: $FULL_DOC" >&2; exit 1; }

REL_DOC="${DOC_PATH//\\//}"
if [[ -z "$PAGE_NAME" ]]; then
  if [[ "$REL_DOC" == *05-roadmap* ]]; then
    PAGE_NAME="Roadmap - foco Sheet Canvas"
  else
    base="$(basename "$FULL_DOC" .md)"
    PAGE_NAME="${base#*-}"
    PAGE_NAME="${PAGE_NAME//-/ }"
  fi
fi

BASE="${PLANE_BASE_URL:-https://api.plane.so}"
BASE="${BASE%/}"
SLUG="$PLANE_WORKSPACE_SLUG"
API_KEY="$PLANE_API_KEY"

[[ -n "$API_KEY" && -n "$SLUG" ]] || { echo "error: PLANE_API_KEY / PLANE_WORKSPACE_SLUG required" >&2; exit 1; }

echo "== Plane wiki sync: $REL_DOC (scope=$SCOPE) =="

HTML_FILE="$(mktemp)"
python3 "$SCRIPT_DIR/plane_md_to_html.py" "$FULL_DOC" --repo-path "$REL_DOC" -o "$HTML_FILE"

export PLANE_HTML_FILE="$HTML_FILE"
export PLANE_PAGE_NAME="$PAGE_NAME"
export PLANE_SCOPE="$SCOPE"
export PLANE_REPLACE_ID="$REPLACE_PAGE_ID"
export PLANE_BASE="$BASE"
export PLANE_SLUG="$SLUG"
export PLANE_API_KEY="$API_KEY"

python3 << 'PY'
import json, os, urllib.error, urllib.request

html = open(os.environ["PLANE_HTML_FILE"], encoding="utf-8").read()
base = os.environ["PLANE_BASE"]
slug = os.environ["PLANE_SLUG"]
key = os.environ["PLANE_API_KEY"]
scope = os.environ["PLANE_SCOPE"]
page_name = os.environ["PLANE_PAGE_NAME"]
replace_id = os.environ.get("PLANE_REPLACE_ID", "")

headers = {"x-api-key": key, "Accept": "application/json", "Content-Type": "application/json; charset=utf-8"}

def req(method, url, payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"{method} {url} -> {e.code}: {body[:300]}")

if scope == "workspace":
    list_url = f"{base}/api/v1/workspaces/{slug}/pages/"
else:
    projects = req("GET", f"{base}/api/v1/workspaces/{slug}/projects/")
    project = projects["results"][0]
    list_url = f"{base}/api/v1/workspaces/{slug}/projects/{project['id']}/pages/"

page_id = replace_id
if not page_id:
    try:
        existing = req("GET", list_url)
        for p in existing.get("results", []):
            if p.get("name") == page_name:
                page_id = p["id"]
                break
    except Exception:
        pass

payload = {"name": page_name, "access": 0, "description_html": html}

if page_id:
    detail = f"{list_url}{page_id}/"
    try:
        page = req("PATCH", detail, payload)
        print(f"Updated page: {page.get('name')} ({page_id})")
    except RuntimeError as exc:
        print(f"PATCH failed ({exc}); creating new page...")
        page = req("POST", list_url, payload)
        page_id = page["id"]
        print(f"Created page: {page.get('name')} ({page_id})")
else:
    page = req("POST", list_url, payload)
    page_id = page["id"]
    print(f"Created page: {page.get('name')} ({page_id})")

verify = req("GET", f"{list_url}{page_id}/")
print(f"Verified description_html length: {len(verify.get('description_html') or '')}")
print(f"URL: https://app.plane.so/{slug}/wiki/{page_id}")
PY

rm -f "$HTML_FILE"
echo "=== Done ==="
