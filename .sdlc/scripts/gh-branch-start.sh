#!/usr/bin/env bash
# Create and switch to an SDLC branch from a Plane task identifier.
# Usage: gh-branch-start.sh <feature|bugfix> <RPG-123> [base-branch]
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

require_cmd git "Install git: https://git-scm.com/"

KIND="${1:?Usage: gh-branch-start.sh <feature|bugfix> <RPG-123> [base-branch]}"
TASK_ID="${2:?Usage: gh-branch-start.sh <feature|bugfix> <RPG-123> [base-branch]}"
BASE="${3:-develop}"

case "$KIND" in
  feature|bugfix) ;;
  *)
    echo "error: kind must be 'feature' or 'bugfix', got '$KIND'" >&2
    exit 1
    ;;
esac

if [[ ! "$TASK_ID" =~ ^[A-Za-z]+-[0-9]+$ ]]; then
  echo "error: task id must match Plane identifier (e.g. RPG-123), got '$TASK_ID'" >&2
  exit 1
fi

BRANCH="${KIND}/${TASK_ID}"

if ! git rev-parse --git-dir >/dev/null 2>&1; then
  echo "error: not a git repository" >&2
  exit 1
fi

if git status --porcelain | grep -q .; then
  echo "warning: working tree has uncommitted changes" >&2
fi

CURRENT="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$CURRENT" == "$BRANCH" ]]; then
  echo "Already on branch $BRANCH"
  exit 0
fi

if git show-ref --verify --quiet "refs/heads/$BRANCH"; then
  git switch "$BRANCH"
  echo "Switched to existing branch $BRANCH"
  exit 0
fi

if git show-ref --verify --quiet "refs/remotes/origin/$BASE"; then
  git fetch origin "$BASE" --quiet 2>/dev/null || true
fi

if git show-ref --verify --quiet "refs/heads/$BASE"; then
  git switch "$BASE"
  git pull --ff-only origin "$BASE" 2>/dev/null || true
elif git show-ref --verify --quiet "refs/remotes/origin/$BASE"; then
  git switch -c "$BASE" "origin/$BASE"
else
  echo "error: base branch '$BASE' not found locally or on origin" >&2
  exit 1
fi

git switch -c "$BRANCH"
echo "Created and switched to $BRANCH (from $BASE)"
