#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

[[ -n "${PLANE_API_KEY:-}" ]] || { echo "error: PLANE_API_KEY not set" >&2; exit 1; }
[[ -n "${PLANE_WORKSPACE_SLUG:-}" ]] || { echo "error: PLANE_WORKSPACE_SLUG not set" >&2; exit 1; }

BASE="${PLANE_BASE_URL:-https://api.plane.so}"
BASE="${BASE%/}"

echo "Checking Plane API at $BASE ..."
resp="$(curl -sS -H "x-api-key: $PLANE_API_KEY" "$BASE/api/v1/users/me/")"
email="$(python3 -c "import json,sys; d=json.load(sys.stdin); print(d.get('email') or d.get('display_name','?'))" <<< "$resp")"
echo "OK - authenticated as: $email"
echo "Workspace slug: $PLANE_WORKSPACE_SLUG"
echo "Next: ./launch.sh and verify plane MCP is green in Cursor Settings."
