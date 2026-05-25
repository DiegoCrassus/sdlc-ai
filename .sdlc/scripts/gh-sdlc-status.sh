#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"
require_cmd gh "Install: https://cli.github.com/"

echo "== SDLC issues by label =="
for label in sdlc:intent sdlc:spec sdlc:implement sdlc:ready sdlc:blocked; do
  echo ""
  echo "--- $label ---"
  gh issue list --label "$label" --limit 10 || echo "(no issues or label not created yet)"
done

echo ""
echo "== Recent workflow runs (sdlc.yml) =="
gh run list --workflow=sdlc.yml --limit 5 || echo "(workflow not on remote yet)"
