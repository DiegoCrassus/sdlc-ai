# Pendências SDLC AI-native — RPG-OP

**Data da validação:** 2026-05-24  
**Maturidade atual:** L1 → **meta L2** (ao fim da F2)  
**Validação:** `.sdlc/scripts/validate.ps1` passou (exit 0)

---

## Visão geral do estado

```
Camada               Status
─────────────────────────────────────────────────────
.sdlc/ harness       ✅ Ativo (agentes canônicos em .sdlc/agents/)
.cursor/ IDE         ✅ Ativo (adapters em .cursor/agents/, hooks ativos)
Hooks Cursor         ✅ Funcionando (logs em .sdlc/logs/)
GitHub Actions CI    ✅ Scaffolded (.github/workflows/sdlc.yml)
packages/rpg_dsl     ✅ Mínimo implementado (validate/compile via python -m)
specs/               ✅ 3 specs carregadas (canvas, sheet, subagent)
generated/           ✅ Artefatos gerados para pydantic/schema/agent/registry/skills
gh CLI               ❌ Não instalada localmente
Backend deps         ⚠️  Não instaladas no env global
Git commits          ✅ HEAD e origin configurados
LangSmith remoto     ⚠️  Configurado via env; confirmar traces no dashboard
GitHub MCP           ⚠️  Configurado; confirmar conexão no Cursor
```

---

## 1. DSL `rpg_dsl` — base mínima de L1

**Caminho:** `packages/rpg_dsl/`  
**Estado atual:** pacote mínimo implementado; `.sdlc/scripts/validate.ps1` consegue validar specs via `python -m rpg_dsl._cli`. O executável `rpg` ainda precisa estar no PATH com `pip install -e packages/rpg_dsl`.

### Pendências

| # | Item | Critério de conclusão |
|---|------|-----------------------|
| 1.1 | Decorador `@Field` com `label`, `type`, `computed` | ✅ Base implementada |
| 1.2 | Decorador `@Canvas` com `Region` e `PresentationType` | ✅ Spec de exemplo compila |
| 1.3 | CLI `rpg validate specs/` | ⚠️ Funciona via `python -m`; falta `rpg` no PATH local |
| 1.4 | CLI `rpg compile --target pydantic` | ✅ Emite `generated/pydantic/` |
| 1.5 | CLI `rpg compile --target typescript` | Emite `generated/typescript/api.ts` |
| 1.6 | CLI `rpg compile --target openapi` | Emite `generated/openapi/bff_v1.yaml` |
| 1.7 | CLI `rpg compile --target agent_manifest` | ✅ Emite `generated/agent_manifest/orchestrator.json` |
| 1.8 | CLI `rpg compile --target skills` | ✅ Emite `generated/skills/` |
| 1.9 | CLI `rpg compile --target evals` | Emite `generated/evals/*.json` |
| 1.10 | CLI `rpg compile --target all` | Todos os targets acima de uma vez |
| 1.11 | Decorador `@SubAgent` → manifest | ✅ Manifest contém `sheet-template-analyst` |
| 1.12 | Decorador `@Eval` com assertions | Upload dataset LangSmith |
| 1.13 | `SheetSpec.version` + `migrations_from` | Compilador emite `SheetMigrator` |
| 1.14 | Decorador `@api` com `@GET` / `@POST` | Emite `RouteSpec` para OpenAPI |

**Referência:** `docs/06-sdlc-ai-native.md` — seções "Pacote rpg_dsl" e "Compilador"

---

## 2. Specs `specs/` — base MVP existente

**Caminho:** `specs/`  
Atualmente contém specs MVP para D&D 5e e `sheet-template-analyst`.

### Pendências

| # | Item | Arquivo alvo |
|---|------|--------------|
| 2.1 | Spec do canvas D&D 5e (MVP) | ✅ `specs/templates/dnd5e_canvas.py` |
| 2.2 | Spec do schema de ficha D&D 5e | ✅ `specs/templates/dnd5e_sheet.py` |
| 2.3 | Spec do orchestrator de produto | `specs/agents/orchestrator.py` |
| 2.4 | Spec do `sheet-template-analyst` | ✅ `specs/agents/sheet_template_analyst.py` |
| 2.5 | Contrato BFF v1 | `specs/api/bff_v1.py` |
| 2.6 | Evals smoke (2 fixtures mínimos) | `specs/evals/template_analysis/` |
| 2.7 | Fixture de ficha D&D 5e anonimizada | `specs/evals/fixtures/dnd5e_fighter.json` |

**Regra:** mudança de comportamento de ficha ou agente **exige** diff em `specs/` antes do código.

---

## 3. Artefatos gerados `generated/` — parcialmente emitidos

**Caminho:** `generated/`  
Derivado exclusivamente via compile; não editar manualmente.

### Pendências (emitidos automaticamente após 1 e 2)

| # | Artefato | Gerado por |
|---|----------|------------|
| 3.1 | `generated/pydantic/sheets/dn_d5e_sheet_v1.py` | ✅ `--target pydantic` |
| 3.2 | `generated/schemas/dn_d5e_sheet_v1.json` | ✅ `--target jsonschema` |
| 3.3 | `generated/openapi/bff_v1.yaml` | `--target openapi` |
| 3.4 | `generated/typescript/api.ts` | `--target typescript` |
| 3.5 | `generated/agent_manifest/orchestrator.json` | ✅ `--target agent_manifest` |
| 3.6 | `generated/agent_manifest/permissions.json` | ✅ `--target agent_manifest` |
| 3.7 | `generated/skills/sheet-template-analyst/SKILL.md` | ✅ `--target skills` |
| 3.8 | `generated/evals/template_analysis.json` | `--target evals` |
| 3.9 | `generated/registry/manifest.json` | ✅ `--target registry` |
| 3.10 | `.cursor/rules/generated-*.mdc` (derivados) | `--target cursor_rules` |

**Política:** commitar `generated/` para PRs legíveis; nunca editar à mão (hook `preToolUse` bloqueia).

---

## 4. Integração GitHub — MCP + gh CLI + Actions

### 4.1 Setup local

| # | Item | Como fazer |
|---|------|------------|
| 4.1.1 | Instalar `gh` CLI | `winget install GitHub.cli` |
| 4.1.2 | Autenticar gh CLI | `gh auth login` → `gh auth setup-git` |
| 4.1.3 | Criar PAT com scopes `repo`, `workflow` | GitHub → Settings → Developer Settings → Fine-grained PAT |
| 4.1.4 | Exportar `GITHUB_PERSONAL_ACCESS_TOKEN` no sistema | Variável de ambiente do Windows (não só no .env) |
| 4.1.5 | Criar repo remoto e push inicial | `gh repo create rpg-op --private` + commit inicial |
| 4.1.6 | Bootstrap de labels SDLC no repo | `.sdlc/scripts/gh-labels-bootstrap.ps1` |

### 4.2 GitHub MCP no Cursor

| # | Item | Status |
|---|------|--------|
| 4.2.1 | `.cursor/mcp.json` configurado com URL remote | ✅ Pronto |
| 4.2.2 | `GITHUB_PERSONAL_ACCESS_TOKEN` exportado | ❌ Pendente (item 4.1.3) |
| 4.2.3 | Reiniciar Cursor após token exportado | ❌ Pendente |
| 4.2.4 | Verificar MCP ativo: "Liste issues via GitHub MCP" | ❌ Pendente |
| 4.2.5 | Testar criação de issue via agente | ❌ Pendente |

**Alternativa Docker:** ver `.sdlc/integrations/github.md` — seção "Local (Docker)".

### 4.3 GitHub Actions CI

| # | Item | Status |
|---|------|--------|
| 4.3.1 | Workflow `SDLC` (`.github/workflows/sdlc.yml`) | ✅ Scaffolded |
| 4.3.2 | Gate `rpg validate` ativo no CI | ❌ Aguarda `rpg_dsl` (item 1.3) |
| 4.3.3 | Gate `pytest backend/` funcional | ⚠️ CI OK; local depende de venv |
| 4.3.4 | Gate evals LangSmith no CI (F2) | ❌ Aguarda specs/evals/ (item 2.6) |
| 4.3.5 | `OPENAI_API_KEY` em GitHub Secrets | ❌ Pendente para F2 |
| 4.3.6 | Secret `LANGCHAIN_API_KEY` em GitHub Secrets | ❌ Pendente para evals CI |

### 4.4 Lifecycle de issues e PRs

| # | Item | Script / MCP |
|---|------|--------------|
| 4.4.1 | Criar issue de intent S0 (DSL mínima) | `gh-issue-intent.ps1` ou GitHub MCP |
| 4.4.2 | Criar issue de intent F1 | idem |
| 4.4.3 | Branch `sdlc/s0-rpg-dsl` linkada à issue | `gh issue develop <n>` |
| 4.4.4 | PR template preenchido a cada merge | `.github/PULL_REQUEST_TEMPLATE.md` |
| 4.4.5 | `gh-sdlc-status.ps1` funcionando | Depende de 4.1.2 |

---

## 5. Cursor — arquivos `.cursor/`

### 5.1 Hooks (estado atual: funcionando em modo local)

| # | Item | Status |
|---|------|--------|
| 5.1.1 | `hooks.json` com todos os 11 eventos | ✅ |
| 5.1.2 | Scripts Python pré/pós (11 arquivos) | ✅ |
| 5.1.3 | `_lib/langsmith_emit.py` com redação de secrets | ✅ |
| 5.1.4 | Fallback JSONL (`.sdlc/logs/cursor-hooks.jsonl`) | ✅ Ativo |
| 5.1.5 | `pip install -r .sdlc/requirements-hooks.txt` no env ativo | ⚠️ Verificar |
| 5.1.6 | LangSmith remoto ativo (`LANGCHAIN_API_KEY` configurada) | ❌ Pendente |
| 5.1.7 | Traces visíveis em smith.langchain.com → `rpg-op-cursor` | ❌ Pendente |
| 5.1.8 | Hook `session_start` recebe stdin do Cursor (não manual) | ✅ By design |

### 5.2 Rules `.cursor/rules/`

| Arquivo | Finalidade | Status |
|---------|------------|--------|
| `sdlc-core.mdc` | Princípios e ordem de trabalho | ✅ |
| `specs-dsl.mdc` | Convenções da DSL | ✅ |
| `generated-readonly.mdc` | Bloqueia edição de `generated/` | ✅ |
| `github-mcp-sdlc.mdc` | Lifecycle GitHub + scripts | ✅ |
| `hooks-langsmith.mdc` | Observabilidade hooks | ✅ |
| `backend-python.mdc` | Convenções FastAPI | ✅ |
| `frontend-react.mdc` | Convenções React/Vite | ✅ |
| `deep-agent.mdc` | Primitivas Deep Agent | ✅ |
| Rules geradas `generated-*.mdc` | Derivadas da DSL via compile | ❌ Aguarda `rpg_dsl` |

### 5.3 Skills `.cursor/skills/`

| Skill | Status |
|-------|--------|
| `sdlc-orchestrator/SKILL.md` | ✅ |
| `github-sdlc/SKILL.md` | ✅ |
| `plane-sdlc/SKILL.md` | ✅ |

### 5.4 Agent adapters `.cursor/agents/`

| Adapter | Status |
|---------|--------|
| `dev-orchestrator.md` | ✅ |
| `subagents/spec-author.md` | ✅ |
| `subagents/codegen-integrator.md` | ✅ |
| `subagents/eval-engineer.md` | ✅ |
| `subagents/sdlc-doctor.md` | ✅ |
| `subagents/github-integrator.md` | ✅ |
| `subagents/plane-integrator.md` | ✅ |

---

## 6. Observabilidade — LangSmith

| # | Item | Status |
|---|------|--------|
| 6.1 | Conta LangSmith criada | ? |
| 6.2 | `LANGCHAIN_API_KEY` no `.env` | ❌ |
| 6.3 | `LANGCHAIN_PROJECT=rpg-op-cursor` no `.env` | ❌ |
| 6.4 | `LANGCHAIN_TRACING_V2=true` no `.env` | ❌ |
| 6.5 | Variáveis exportadas no sistema (não só .env) | ❌ |
| 6.6 | Reiniciar Cursor após configurar | ❌ |
| 6.7 | Confirmar traces em smith.langchain.com | ❌ |
| 6.8 | Projeto `rpg-op` para runtime Deep Agent (F2) | ❌ Aguarda F2 |
| 6.9 | Upload de datasets de evals para LangSmith CI | ❌ Aguarda specs/evals/ |

**Fallback ativo:** `.sdlc/logs/cursor-hooks.jsonl` grava localmente mesmo sem LangSmith.

---

## 7. Backend + Frontend (ambiente local)

| # | Item | Status |
|---|------|--------|
| 7.1 | `python -m venv .venv` e ativar | ⚠️ Usar venv, não env global |
| 7.2 | `pip install -r backend/requirements.txt` | ❌ No env global (pydantic-settings, sqlalchemy ausentes) |
| 7.3 | `.env` com `DATABASE_URL`, `OPENAI_API_KEY` | ❌ |
| 7.4 | `uvicorn app.main:app --reload` | ❌ Bloqueado por 7.2 |
| 7.5 | `cd apps/web && npm install && npm run dev` | ? |
| 7.6 | Docker Compose com Postgres | ❌ Aguarda F1 |
| 7.7 | `pytest backend/tests/ -q` | ❌ Sem testes criados ainda |

---

## 8. Git e versionamento

| # | Item | Status |
|---|------|--------|
| 8.1 | Commit inicial do scaffolding | ❌ Branch master sem commits |
| 8.2 | `.gitignore` presente | ✅ |
| 8.3 | `.env` fora do git | ✅ (no .gitignore) |
| 8.4 | Remote origin configurado | ❌ |
| 8.5 | Política de `generated/` definida: commitar no PR | ✅ Documentado |

---

## Ordem de execução recomendada

```
Passo  O que fazer                               Desbloqueia
─────────────────────────────────────────────────────────────
  1    Commit inicial (item 8.1)                 Git history
  2    Instalar gh CLI + gh auth login (4.1)     Scripts locais
  3    Criar PAT + exportar token (4.1.3–4.1.4)  GitHub MCP
  4    Configurar LangSmith no .env (6.1–6.6)   Observabilidade remota
  5    pip install -r backend/requirements.txt   Backend local
  6    gh repo create + push (4.1.5)             CI Actions
  7    gh-labels-bootstrap.ps1 (4.1.6)           Labels SDLC
  8    Implementar rpg_dsl mínimo (1.1–1.4)      L1 + specs
  9    Escrever specs/ S0 (2.1–2.2)              Compile pipeline
 10    rpg compile --target pydantic (3.1–3.2)   Backend tipado
 11    Issue + PR S0 via GitHub MCP (4.4)        Lifecycle completo
 12    Evals smoke + LangSmith CI (2.6, 4.3.4)   L2
```

---

## Métricas de maturidade

| Nível | Critério | Estado |
|-------|----------|--------|
| **L0** | Harness scaffolded; specs só para schema de ficha | ✅ Concluído |
| **L1** | + manifest de agente gerado (`rpg compile` funcional) | ✅ **Atual** |
| **L2** | + evals smoke em CI (LangSmith) | ❌ Aguarda itens 1, 2, 6 |
| L3 | + dev harness wired ao runtime Deep Agent | backlog |
| L4 | + migrações de sheet geradas; RAG rules na DSL | backlog |

---

## Referências

| Doc | Conteúdo |
|-----|----------|
| `docs/06-sdlc-ai-native.md` | Visão completa do modelo AI-native |
| `docs/05-roadmap.md` | Roadmap S0 → F6 com critérios de saída |
| `.sdlc/AGENTS.md` | Memória do dev orchestrator |
| `.sdlc/phases.yaml` | Fases e gates do SDLC |
| `.sdlc/workflows/github-lifecycle.md` | Ciclo completo intent → deploy |
| `.sdlc/integrations/github.md` | Setup GitHub MCP + gh CLI |
| `.sdlc/integrations/langsmith.md` | Setup LangSmith observabilidade |
| `.cursor/hooks/README.md` | Documentação dos hooks Cursor |
