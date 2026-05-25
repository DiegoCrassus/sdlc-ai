#!/usr/bin/env bash
# Open Cursor with .env loaded for MCP.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$ROOT/.sdlc/scripts/common.sh"

require_cmd cursor "Install Cursor and add 'cursor' CLI to PATH"

echo "Variáveis do .env carregadas. Abrindo Cursor..."
exec cursor .
