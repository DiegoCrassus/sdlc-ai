#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"
require_cmd gh "Install: https://cli.github.com/"

DRY_RUN="${1:-}"

labels=(
  "sdlc:intent|0E8A16|Fase intent"
  "sdlc:spec|1D76DB|Spec DSL"
  "sdlc:implement|FBCA04|Implementacao"
  "sdlc:eval|5319E7|Evals agente"
  "sdlc:ready|006B75|Pronto PR"
  "sdlc:blocked|B60205|Bloqueado"
  "sdlc:lint-fail|E4E669|Lint falhou"
  "type:feature|A2EEEF|Feature"
  "type:bug|D93F0B|Bug"
  "type:spec|C5DEF5|Spec"
  "type:agent|D4C5F9|Agent"
)

for entry in "${labels[@]}"; do
  IFS='|' read -r name color desc <<< "$entry"
  cmd=(gh label create "$name" --color "$color" --description "$desc" --force)
  if [[ "$DRY_RUN" == "--dry-run" ]]; then
    echo "${cmd[*]}"
  else
    "${cmd[@]}" 2>/dev/null || true
    echo "label: $name"
  fi
done

echo "Done."
