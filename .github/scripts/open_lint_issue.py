"""
Cria (ou atualiza) uma GitHub Issue para erros de lint.
Saída: sets GITHUB_OUTPUT com issue_number.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.request

TOKEN       = os.environ["SDLC_PAT_CLASSIC"]
REPO        = os.environ["REPO"]
COMMIT_SHA  = os.environ.get("COMMIT_SHA", "")[:7]
COMMIT_MSG  = os.environ.get("COMMIT_MSG", "").split("\n")[0][:80]
BRANCH      = os.environ.get("BRANCH", "unknown")
PY_ERRORS   = os.environ.get("PYTHON_ERRORS", "").replace("%0A", "\n")
TS_ERRORS   = os.environ.get("TS_ERRORS", "").replace("%0A", "\n")
PY_FAILED   = os.environ.get("PYTHON_FAILED", "false") == "true"
TS_FAILED   = os.environ.get("TS_FAILED", "false") == "true"
RUN_URL     = os.environ.get("RUN_URL", "")

BASE    = f"https://api.github.com/repos/{REPO}"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept":        "application/vnd.github+json",
    "Content-Type":  "application/json",
    "X-GitHub-Api-Version": "2022-11-28",
}


def api(method: str, path: str, body: dict | None = None) -> tuple[int, dict]:
    data = json.dumps(body).encode() if body else None
    req  = urllib.request.Request(f"{BASE}{path}", data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, json.loads(r.read())
    except urllib.error.HTTPError as e:
        return e.code, {}


def ensure_label(name: str, color: str, description: str) -> None:
    s, _ = api("GET", f"/labels/{name}")
    if s == 404:
        api("POST", "/labels", {"name": name, "color": color, "description": description})


def find_open_issue(title_prefix: str) -> int | None:
    s, data = api("GET", "/issues?state=open&labels=sdlc:lint-fail&per_page=10")
    if s != 200:
        return None
    for issue in data:
        if issue.get("title", "").startswith(title_prefix):
            return issue["number"]
    return None


# --- Build body ---
sections: list[str] = []

if PY_FAILED and PY_ERRORS.strip():
    sections.append(f"## Python — ruff\n\n```\n{PY_ERRORS.strip()}\n```")

if TS_FAILED and TS_ERRORS.strip():
    sections.append(f"## TypeScript — tsc\n\n```\n{TS_ERRORS.strip()}\n```")

body = f"""\
## Lint falhou no commit `{COMMIT_SHA}`

**Branch:** `{BRANCH}`
**Commit:** {COMMIT_MSG}
**Run:** {RUN_URL}

{chr(10).join(sections)}

---
> Criado automaticamente pelo workflow `lint.yml`.
> O agente `lint-fix` será disparado para tentar corrigir automaticamente.
> Se o fix não for possível, este issue receberá a label `sdlc:blocked`.
"""

title = f"[lint-fail] {BRANCH} — {COMMIT_SHA}: {COMMIT_MSG}"[:120]

# Garante que a label existe
ensure_label("sdlc:lint-fail", "E4E669", "Falha de lint — aguardando auto-fix")

# Evita abrir issue duplicada para o mesmo branch
existing = find_open_issue(f"[lint-fail] {BRANCH}")
if existing:
    # Adiciona comentário na issue existente
    api("POST", f"/issues/{existing}/comments", {
        "body": f"### Nova falha — `{COMMIT_SHA}`\n\n{chr(10).join(sections)}\n\n[Run]({RUN_URL})"
    })
    issue_number = existing
    print(f"Updated existing issue #{existing}")
else:
    s, issue = api("POST", "/issues", {
        "title":  title,
        "body":   body,
        "labels": ["sdlc:lint-fail", "type:bug"],
    })
    if s not in (200, 201):
        print(f"Failed to create issue: {s}", file=sys.stderr)
        sys.exit(1)
    issue_number = issue["number"]
    print(f"Created issue #{issue_number}: {title}")

# Expõe o número da issue para o step seguinte
output_file = os.environ.get("GITHUB_OUTPUT", "")
if output_file:
    with open(output_file, "a") as f:
        f.write(f"issue_number={issue_number}\n")
