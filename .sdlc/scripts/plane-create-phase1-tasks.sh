#!/usr/bin/env bash
# Create Plane work items for Roadmap Fase 1 (Hardening).
# Usage: .sdlc/scripts/plane-create-phase1-tasks.sh
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
# shellcheck source=/dev/null
source "$SCRIPT_DIR/common.sh"

[[ -n "${PLANE_API_KEY:-}" ]] || { echo "error: PLANE_API_KEY not set" >&2; exit 1; }
[[ -n "${PLANE_WORKSPACE_SLUG:-}" ]] || { echo "error: PLANE_WORKSPACE_SLUG not set" >&2; exit 1; }

BASE="${PLANE_BASE_URL:-https://api.plane.so}"
BASE="${BASE%/}"

export PLANE_BASE="$BASE"
export PLANE_SLUG="$PLANE_WORKSPACE_SLUG"
export PLANE_API_KEY="$PLANE_API_KEY"

python3 << 'PY'
import json
import os
import urllib.error
import urllib.request

base = os.environ["PLANE_BASE"]
slug = os.environ["PLANE_SLUG"]
key = os.environ["PLANE_API_KEY"]
headers = {"x-api-key": key, "Accept": "application/json", "Content-Type": "application/json; charset=utf-8"}

TASKS = [
    {
        "name": "[Feature] F1.1 — Evals smoke LangSmith",
        "description_html": """<h2>context</h2>
<p>PoC 2.9 pendente (RPG-64). Maturidade SDLC L1→L2 exige evals smoke versionados e gate CI.</p>
<p>Ref: <code>docs/05-roadmap.md</code> Fase 1.1 · <code>docs/poc/poc-2-dpa-agent.md</code></p>
<h2>changes</h2>
<ul>
<li>Criar <code>specs/evals/template_analysis/</code> com 2 fixtures anonimizadas</li>
<li>Implementar <code>rpg compile --target evals</code></li>
<li>Gate LangSmith smoke no workflow SDLC</li>
<li>Fechar ou substituir RPG-64</li>
</ul>
<h2>acceptance criteria</h2>
<ul>
<li><code>specs/evals/</code> com 2 cenários smoke</li>
<li><code>make validate</code> inclui eval smoke ou job CI dedicado verde</li>
<li>Traces visíveis no projeto LangSmith configurado</li>
<li>SDLC Doctor reporta L2</li>
</ul>
<h2>comments</h2>
<ul>
<li>Label Plane: <code>phase-1</code></li>
<li>Branch: <code>feature/RPG-N</code> após criar item</li>
<li>GitHub: issue via <code>gh-issue-intent.sh</code></li>
</ul>""",
    },
    {
        "name": "[Feature] F1.2 — Contrato BFF alinhado (specs/api)",
        "description_html": """<h2>context</h2>
<p>Drift conhecido entre <code>specs/api/bff_v1.py</code> e routers actuais (template/extend, characters, sheets).</p>
<h2>changes</h2>
<ul>
<li>Atualizar <code>specs/api/bff_v1.py</code> com rotas PoC entregues</li>
<li><code>rpg compile</code> → OpenAPI + TypeScript</li>
<li>Revisar frontend <code>api.ts</code> se necessário</li>
</ul>
<h2>acceptance criteria</h2>
<ul>
<li><code>rpg validate specs/</code> verde</li>
<li>OpenAPI gerado reflecte <code>apps/backend/app/routers/</code></li>
<li>Sem endpoints documentados inexistentes</li>
</ul>
<h2>comments</h2>
<ul>
<li>Label: <code>phase-1</code></li>
<li>Depende de PoC concluído ✅</li>
</ul>""",
    },
    {
        "name": "[Feature] F1.3 — DPA Agent com LLM real",
        "description_html": """<h2>context</h2>
<p>PoC 2 usa stub determinístico em <code>dpa_analyzer.py</code>. Fase 1 substitui por LLM multimodal com traces LangSmith.</p>
<h2>changes</h2>
<ul>
<li>Integrar modelo multimodal no fluxo analyze/extend</li>
<li>Manter HITL publish</li>
<li>Emitir traces por análise</li>
<li>Actualizar spec <code>sheet_template_analyst</code> se necessário</li>
</ul>
<h2>acceptance criteria</h2>
<ul>
<li>Upload PDF/PNG produz draft via LLM (não stub)</li>
<li>Passos <code>analysis.steps</code> persistidos</li>
<li>Trace LangSmith por execução de análise</li>
<li>Testes existentes passam ou actualizados</li>
</ul>
<h2>comments</h2>
<ul>
<li>Label: <code>phase-1</code></li>
<li>Recomendado após F1.1 (evals)</li>
</ul>""",
    },
    {
        "name": "[Feature] F1.4 — CI obrigatório (pytest + validate)",
        "description_html": """<h2>context</h2>
<p>Workflow SDLC usa <code>continue-on-error</code> em pytest. Fase 1 endurece gates.</p>
<h2>changes</h2>
<ul>
<li>Remover <code>continue-on-error</code> de pytest no <code>sdlc.yml</code></li>
<li>Validar <code>make validate</code> equivalente no CI</li>
<li>Documentar em <code>docs/status/pendencias-sdlc.md</code></li>
</ul>
<h2>acceptance criteria</h2>
<ul>
<li>PR com teste a falhar bloqueia merge</li>
<li>18+ testes pytest required</li>
<li>validate script executado no CI</li>
</ul>
<h2>comments</h2>
<ul>
<li>Label: <code>phase-1</code></li>
</ul>""",
    },
    {
        "name": "[Feature] F1.5 — Auth mínima (substituir SessionBar mock)",
        "description_html": """<h2>context</h2>
<p>PoC usa SessionBar para alternar GM/jogador. Alpha requer identidade real por membro.</p>
<h2>changes</h2>
<ul>
<li>Sessão JWT ou auth provider mínimo</li>
<li>RBAC ligado a user id real</li>
<li>Remover mock como default em dev (flag opcional)</li>
</ul>
<h2>acceptance criteria</h2>
<ul>
<li>Login/logout ou token dev documentado</li>
<li>Jogador só edita ficha própria sem SessionBar manual</li>
<li>GM vê dashboard autenticado</li>
</ul>
<h2>comments</h2>
<ul>
<li>Label: <code>phase-1</code></li>
<li>Pode ser último item da Fase 1</li>
</ul>""",
    },
]


def req(method, url, payload=None):
    data = None
    if payload is not None:
        data = json.dumps(payload).encode("utf-8")
    r = urllib.request.Request(url, data=data, headers=headers, method=method)
    try:
        with urllib.request.urlopen(r) as resp:
            body = resp.read().decode()
            return json.loads(body) if body else {}
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")
        raise RuntimeError(f"{method} {url} -> {e.code}: {body[:400]}")


print("== Plane: create Fase 1 work items ==")
projects = req("GET", f"{base}/api/v1/workspaces/{slug}/projects/")
results = projects.get("results", [])
if not results:
    raise SystemExit("No projects found")
project = next((p for p in results if p.get("identifier") == "RPG"), results[0])
project_id = project["id"]
print(f"Project: {project.get('name')} ({project.get('identifier')}) id={project_id}")

states = req("GET", f"{base}/api/v1/workspaces/{slug}/projects/{project_id}/states/")
state_list = states.get("results", [])
todo = next((s for s in state_list if s.get("group") == "backlog" or "todo" in (s.get("name") or "").lower()), state_list[0] if state_list else None)
todo_id = todo["id"] if todo else None
print(f"Default state: {todo.get('name') if todo else 'none'} ({todo_id})")

labels_url = f"{base}/api/v1/workspaces/{slug}/projects/{project_id}/labels/"
label_id = None
try:
    labels = req("GET", labels_url)
    for lb in labels.get("results", []):
        if lb.get("name") == "phase-1":
            label_id = lb["id"]
            break
    if not label_id:
        created = req("POST", labels_url, {"name": "phase-1", "color": "#3b82f6"})
        label_id = created.get("id")
        print(f"Created label phase-1: {label_id}")
except RuntimeError as exc:
    print(f"Label skip: {exc}")

created_ids = []
for task in TASKS:
    payload = {
        "name": task["name"],
        "description_html": task["description_html"],
        "priority": "medium",
    }
    if todo_id:
        payload["state"] = todo_id
    if label_id:
        payload["labels"] = [label_id]

    wi_url = f"{base}/api/v1/workspaces/{slug}/projects/{project_id}/work-items/"
    try:
        item = req("POST", wi_url, payload)
    except RuntimeError:
        wi_url = f"{base}/api/v1/workspaces/{slug}/projects/{project_id}/issues/"
        item = req("POST", wi_url, payload)

    ident = item.get("sequence_id") or item.get("id")
    name = item.get("name")
    wi_id = item.get("id")
    created_ids.append(wi_id)
    print(f"  Created: {project.get('identifier')}-{ident} — {name}")

print(f"\nDone: {len(created_ids)} work items created.")
print("Next: make plane-sync-roadmap && make plane-sync-poc")
PY
