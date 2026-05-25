#!/usr/bin/env bash
# Install common prerequisites on Ubuntu / Debian / WSL.
# Usage: bash .sdlc/scripts/bootstrap-linux.sh
set -euo pipefail

echo "== RPG-OP bootstrap (Linux) =="

if ! command -v apt-get >/dev/null 2>&1; then
  echo "This script targets Ubuntu/Debian/WSL. Install manually: make, curl, git, node, uv."
  exit 1
fi

sudo apt-get update
sudo apt-get install -y make curl git ca-certificates build-essential

if ! command -v uv >/dev/null 2>&1; then
  echo "Installing uv..."
  curl -LsSf https://astral.sh/uv/install.sh | sh
  echo "Add uv to PATH: source \$HOME/.local/bin/env (or restart shell)"
fi

if ! command -v node >/dev/null 2>&1; then
  echo ""
  echo "Node.js not found. Install one of:"
  echo "  curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
  echo "  or use nvm: https://github.com/nvm-sh/nvm"
fi

echo ""
echo "Next steps (from repo root):"
echo "  make setup"
echo "  make dev    # or ./dev.sh"
echo "  make test"
