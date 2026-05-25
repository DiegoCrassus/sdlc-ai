#!/usr/bin/env bash
# RPG-OP — start dev. Run from repo root: ./dev.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$ROOT/.sdlc/scripts/common.sh"

require_cmd uv "Install: curl -LsSf https://astral.sh/uv/install.sh | sh"
require_cmd npm "Install Node.js 20+"

if ! resolve_python >/dev/null 2>&1; then
  bash "$ROOT/.sdlc/scripts/setup.sh"
fi

exec bash "$ROOT/.sdlc/scripts/dev-all.sh"
