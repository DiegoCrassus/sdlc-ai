#!/usr/bin/env bash
# Usage: gh-pr-open.sh "Title" [issue-number] [body-file]
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"
require_cmd gh "Install: https://cli.github.com/"

TITLE="${1:?Usage: gh-pr-open.sh \"Title\" [issue] [body-file]}"
ISSUE="${2:-0}"
BODY_FILE="${3:-}"

tmp="$(mktemp)"
if [[ -n "$BODY_FILE" && -f "$BODY_FILE" ]]; then
  cp "$BODY_FILE" "$tmp"
else
  cat > "$tmp" << 'EOF'
## Summary

<!-- o que mudou -->

## SDLC checklist

- [ ] Spec em `specs/` (se contrato/agente/canvas)
- [ ] `make validate` verde
- [ ] Sem edição manual em `generated/`
EOF
fi

if [[ "$ISSUE" =~ ^[0-9]+$ && "$ISSUE" -gt 0 ]]; then
  echo "" >> "$tmp"
  echo "Closes #$ISSUE" >> "$tmp"
fi

gh pr create --title "$TITLE" --body-file "$tmp"
rm -f "$tmp"
