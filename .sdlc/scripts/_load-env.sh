#!/usr/bin/env bash
# Load repo .env into the current shell session.
# Usage: source "$(dirname "$0")/_load-env.sh"

_script_dir="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)"
_root="$(cd "$_script_dir/../.." && pwd)"
_env_file="$_root/.env"

if [[ ! -f "$_env_file" ]]; then
  echo "info: .env not found at $_env_file (skipping)" >&2
  return 0 2>/dev/null || exit 0
fi

while IFS= read -r line || [[ -n "$line" ]]; do
  line="${line#"${line%%[![:space:]]*}"}"
  [[ -z "$line" || "$line" == \#* ]] && continue
  if [[ "$line" =~ ^([^=]+)=(.*)$ ]]; then
    key="${BASH_REMATCH[1]// /}"
    value="${BASH_REMATCH[2]}"
    value="${value#"${value%%[![:space:]]*}"}"
    value="${value%"${value##*[![:space:]]}"}"
    value="${value#\"}"; value="${value%\"}"
    value="${value#\'}"; value="${value%\'}"
    export "$key=$value"
  fi
done < "$_env_file"

echo "info: .env loaded from $_env_file" >&2

if [[ -n "${GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC:-}" ]]; then
  export GH_TOKEN="$GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC"
fi
