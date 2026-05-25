# Cursor — RPG-OP

Integração IDE com harness SDLC AI-native (Deep Agent), adapters de agentes,
hooks e MCP (GitHub, Plane, Supabase).

## Layout

```
.cursor/
├── AGENTS.md
├── agents/                 # adapters Cursor para agentes canônicos em .sdlc/agents/
├── hooks.json              # pre/post hooks → LangSmith
├── hooks/                  # scripts Python
├── mcp.json
├── mcp.json.example
├── rules/                # inclui github-mcp-sdlc.mdc
├── skills/
└── hooks.json
```

## Agents

| Camada | Papel |
|--------|-------|
| `.sdlc/agents/` | Fonte canônica operacional: YAMLs com prompts, skills, tools, permissões e refs. |
| `.cursor/agents/` | Camada de adaptação do Cursor: quando chamar cada agente e como delegar. |

Não duplique configuração operacional em `.cursor/agents/`. Alterações em
modelo, tools, skills, permissões ou `system_prompt` pertencem a `.sdlc/agents/`.

## GitHub MCP — setup

1. Crie PAT: https://github.com/settings/tokens (`repo`, `workflow`)
2. Defina `GITHUB_PERSONAL_ACCESS_TOKEN` (variável de sistema ou `.env`)
3. Confirme `.cursor/mcp.json` (copie de `mcp.json.example` se necessário)
4. Reinicie Cursor → Settings → MCP → indicador verde em `github`
5. Teste no chat: "Liste issues abertas neste repositório"

Alternativa local: Docker — ver `.sdlc/integrations/github.md`

## Supabase MCP — setup

1. Crie um PAT em https://supabase.com/dashboard/account/tokens
2. Defina `SUPABASE_ACCESS_TOKEN` e `SUPABASE_PROJECT_REF` no `.env`
3. Abra o Cursor via `.\launch.ps1`
4. Reinicie Cursor → Settings → Tools & MCP → indicador verde em `supabase`

Detalhes: `.sdlc/integrations/supabase.md`

## gh CLI

```powershell
winget install GitHub.cli
gh auth login
.sdlc/scripts/gh-labels-bootstrap.ps1
```

## SDLC

[../.sdlc/README.md](../.sdlc/README.md) · [github-lifecycle](../.sdlc/workflows/github-lifecycle.md)
