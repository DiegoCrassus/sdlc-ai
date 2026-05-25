#!/usr/bin/env bash
# Usage: gh-issue-intent.sh "Title" [body-file]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"
require_cmd gh "Install: https://cli.github.com/"

TITLE="${1:?Usage: gh-issue-intent.sh \"Title\" [body-file]}"
BODY_FILE="${2:-}"

args=(issue create --title "$TITLE" --label sdlc:intent --label type:feature)
if [[ -n "$BODY_FILE" && -f "$BODY_FILE" ]]; then
  args+=(--body-file "$BODY_FILE")
else
  args+=(--body "SDLC intent — fill template in follow-up.")
fi

gh "${args[@]}"
echo "Issue created."
