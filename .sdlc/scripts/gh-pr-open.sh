#!/usr/bin/env bash
# Usage: gh-pr-open.sh "Title" [issue-number] [body-file]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"
require_cmd gh "Install: https://cli.github.com/"
require_cmd git "Install git: https://git-scm.com/"

TITLE="${1:?Usage: gh-pr-open.sh \"Title\" [issue] [body-file]}"
ISSUE="${2:-0}"
BODY_FILE="${3:-}"

BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ ! "$BRANCH" =~ ^(feature|bugfix)/[A-Za-z]+-[0-9]+$ ]]; then
  echo "error: PR branch must match feature/RPG-N or bugfix/RPG-N, got '$BRANCH'" >&2
  exit 1
fi

TASK_ID="${BRANCH#*/}"

tmp="$(mktemp)"
if [[ -n "$BODY_FILE" && -f "$BODY_FILE" ]]; then
  cp "$BODY_FILE" "$tmp"
else
  cat > "$tmp" << 'EOF'
## Summary

<!-- o que mudou -->

## SDLC checklist

- [ ] Plane task `RPG-N` linkada
- [ ] Branch `feature/RPG-N` ou `bugfix/RPG-N`
- [ ] Base `develop`
- [ ] `make test`, `make lint` e `make validate` verdes
- [ ] Owner approval antes do merge
EOF
fi

if [[ "$ISSUE" =~ ^[0-9]+$ && "$ISSUE" -gt 0 ]]; then
  echo "" >> "$tmp"
  echo "Closes #$ISSUE" >> "$tmp"
fi

echo "" >> "$tmp"
echo "Plane: \`$TASK_ID\`" >> "$tmp"

gh pr create --base develop --title "$TITLE" --body-file "$tmp"
rm -f "$tmp"
