# Pendências humanas — ações que requerem sua intervenção

**Última atualização:** 2026-05-24  
Tudo que estava no meu escopo de autonomia (rpg_dsl, specs, .env.example) foi aplicado diretamente.  
Este documento cobre **somente o que você precisa fazer**.

---

## 1. Git — commit das mudanças atuais

O repositório já tem `HEAD` e `origin` configurados, mas há mudanças locais
pendentes. Sem commit/push, o CI remoto não valida o estado atual.

```powershell
# Na raiz do projeto
git add .
git commit -m "chore: organize SDLC and Cursor agents"
```

---

## 2. Instalar `gh` CLI

Necessário para: `gh-sdlc-status.ps1`, `gh-issue-intent.ps1`, `gh-pr-open.ps1`, `gh auth login`.

```powershell
winget install --id GitHub.cli
# Feche e reabra o terminal depois
gh --version   # confirma instalação
```

Alternativa: baixar em https://cli.github.com/

---

## 3. Criar GitHub Personal Access Token (PAT)

### 3a. Fine-grained PAT (recomendado)

1. Acesse: https://github.com/settings/personal-access-tokens/new
2. **Token name:** `rpg-op-cursor`
3. **Expiration:** 90 days (ou custom)
4. **Repository access:** Only select repositories → selecione `rpg-op`
5. **Permissions — Repository:**
   - Contents: **Read and Write**
   - Issues: **Read and Write**
   - Pull requests: **Read and Write**
   - Actions: **Read**
   - Workflows: **Read and Write**
6. Clique **Generate token** e copie o valor (começa com `github_pat_...`)

### 3b. Classic PAT (alternativa se fine-grained tiver problemas)

1. Acesse: https://github.com/settings/tokens/new
2. **Note:** `rpg-op-cursor`
3. Scopes: `repo` (tudo), `workflow`
4. Clique **Generate token**

---

## 4. Fazer o GitHub MCP ler o `.env`

O MCP GitHub usa `${env:GITHUB_PERSONAL_ACCESS_TOKEN}` que lê do **processo do Cursor** — não do `.env` diretamente.  
A solução é abrir o Cursor via `launch.ps1`, que carrega o `.env` antes de iniciar:

### 4a. Preencher o `.env` (já existe na raiz)

```bash
GITHUB_PERSONAL_ACCESS_TOKEN=SEU_TOKEN_AQUI
GITHUB_REPOSITORY=SEU_USUARIO/rpg-op
```

### 4b. Abrir o Cursor sempre via `launch.ps1`

```powershell
# Na raiz do projeto (em vez de abrir o Cursor pelo atalho)
.\launch.ps1
```

Isso carrega o `.env` e executa `cursor .` — o Cursor herda todas as variáveis do processo.

### 4c. Verificar MCP ativo

No chat do Cursor, escreva:
> "Liste os issues abertos deste repositório via GitHub MCP"

Se retornar resultados (ou "sem issues"), o MCP está funcionando.

> **Alternativa (exportação permanente, one-time):** se preferir não usar `launch.ps1`, exporte para o sistema uma única vez:
> ```powershell
> [System.Environment]::SetEnvironmentVariable("GITHUB_PERSONAL_ACCESS_TOKEN", "SEU_TOKEN", "User")
> ```

---

## 5. Criar repositório remoto no GitHub

```powershell
# Após instalar gh CLI e autenticar (item 2)
gh auth login          # siga o fluxo interativo (browser)
gh auth setup-git      # configura git credential helper

# Criar repo
gh repo create rpg-op --private --source=. --push
```

Ou crie manualmente em https://github.com/new e depois:

```powershell
git remote add origin https://github.com/SEU_USUARIO/rpg-op.git
git push -u origin master
```

---

## 6. Bootstrap de labels SDLC no repo

Execute após ter o repo remoto e `gh` autenticado:

```powershell
.sdlc/scripts/gh-labels-bootstrap.ps1
```

Cria as labels: `sdlc:intent`, `sdlc:spec`, `sdlc:implement`, `sdlc:ready`, `sdlc:blocked`, `sdlc:eval`.

---

## 7. Configurar LangSmith (observabilidade remota)

Sem isso os hooks funcionam em modo fallback local (`.sdlc/logs/cursor-hooks.jsonl`), mas você não vê traces no dashboard.

### 7a. Criar conta e API Key

1. Acesse: https://smith.langchain.com/
2. Crie conta (gratuita para uso individual)
3. Vá em **Settings → API Keys → Create API Key**
4. Copie a chave (começa com `lsv2_pt_...`)

### 7b. Preencher `.env` (suporta nomenclatura nova `LANGSMITH_*`)

```bash
LANGSMITH_API_KEY=lsv2_pt_SEU_TOKEN_AQUI
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_PROJECT=rpg-op-cursor
```

Os hooks Python carregam o `.env` automaticamente via `python-dotenv` — **não é necessário exportar para o sistema**.

### 7d. Instalar deps dos hooks

```powershell
pip install -r .sdlc/requirements-hooks.txt
```

### 7e. Reiniciar Cursor e confirmar

Após reiniciar, execute qualquer ação no chat. Acesse https://smith.langchain.com/ → projeto `rpg-op-cursor` → você deve ver runs `cursor/preToolUse`.

---

## 8. Configurar backend local (venv)

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 8a. Criar e popular `.env` com DATABASE_URL

```bash
# .env na raiz (já existe .env.example como base)
DATABASE_URL=sqlite+aiosqlite:///./data/rpg_op.db
```

### 8b. Subir o backend

```powershell
# Com venv ativado, dentro de backend/
uvicorn app.main:app --reload --port 8000
```

Acesse http://127.0.0.1:8000/docs para confirmar.

### 8c. Testar smoke

```powershell
python scripts/smoke_test.py
```

---

## 9. Instalar `rpg_dsl` (pacote local)

O pacote foi implementado em `packages/rpg_dsl/`. Instale no seu ambiente:

```powershell
# Na raiz do projeto (ou com venv ativo)
pip install -e packages/rpg_dsl
# Confirma:
rpg --help
rpg validate specs/
```

---

## 10. Configurar `OPENAI_API_KEY` (para F2 — Deep Agent)

Necessário apenas quando chegar na fase F2 (subagente `sheet-template-analyst`).

1. Acesse: https://platform.openai.com/api-keys
2. Crie uma chave
3. Exporte no sistema:

```powershell
[System.Environment]::SetEnvironmentVariable("OPENAI_API_KEY", "sk-...", "User")
```

4. Adicione em `.env`:

```bash
OPENAI_API_KEY=sk-...
AGENT_MODEL=openai:gpt-4.1-mini
```

5. Para F2, adicione em GitHub Secrets (CI):  
   Repo → Settings → Secrets and variables → Actions → New repository secret

---

## Checklist rápido (ordem recomendada)

```
[ ] 1. git commit das mudanças atuais
[ ] 2. winget install GitHub.cli
[ ] 3. Criar PAT no GitHub
[ ] 4a. Preencher .env com GITHUB_PERSONAL_ACCESS_TOKEN
[ ] 4b. Abrir Cursor via .\launch.ps1 (carrega .env automaticamente)
[ ] 4c. Testar MCP no chat: "Liste issues via GitHub MCP"
[ ] 5. gh auth login + gh repo create + git push
[ ] 6. gh-labels-bootstrap.ps1
[ ] 7a. Criar conta LangSmith + API key
[ ] 7b. Preencher .env com LANGSMITH_API_KEY + LANGSMITH_PROJECT
[ ] 7c. pip install -r .sdlc/requirements-hooks.txt
[ ] 7d. Abrir Cursor via .\launch.ps1 + confirmar traces em smith.langchain.com
[ ] 8. cd backend && python -m venv .venv && pip install -r requirements.txt
[ ] 9. pip install -e packages/rpg_dsl (já instalado no env global)
[ ] 10. OPENAI_API_KEY no .env (quando iniciar F2)
```

---

## O que o agente já aplicou (não precisa fazer)

| Item | Onde está |
|------|-----------|
| `packages/rpg_dsl` implementado (`@Canvas`, `@Sheet`, `rpg compile`, `rpg validate`) | `packages/rpg_dsl/` |
| Spec D&D 5e canvas + schema | `specs/templates/dnd5e_canvas.py`, `specs/templates/dnd5e_sheet.py` |
| Spec subagente analyst | `specs/agents/sheet_template_analyst.py` |
| `.env.example` atualizado (nomenclatura `LANGSMITH_*`) | `.env.example` |
| Scripts PS1 carregam `.env` automaticamente | `.sdlc/scripts/_load-env.ps1` |
| `launch.ps1` — abre Cursor com `.env` carregado (MCP funciona) | `launch.ps1` |
| `langsmith_emit.py` suporta `LANGSMITH_*` e `LANGCHAIN_*` | `.cursor/hooks/_lib/langsmith_emit.py` |
| Doc de pendências completo | `docs/status/pendencias-sdlc.md` |
