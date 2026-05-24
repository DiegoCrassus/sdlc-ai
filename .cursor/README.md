# Cursor — RPG-OP

Integração IDE com harness SDLC AI-native (Deep Agent) + **GitHub MCP**.

## Layout

```
.cursor/
├── AGENTS.md
├── hooks.json              # pre/post hooks → LangSmith
├── hooks/                  # scripts Python
├── mcp.json
├── mcp.json.example
├── rules/                # inclui github-mcp-sdlc.mdc
├── skills/
└── hooks.json
```

## GitHub MCP — setup

1. Crie PAT: https://github.com/settings/tokens (`repo`, `workflow`)
2. Defina `GITHUB_PERSONAL_ACCESS_TOKEN` (variável de sistema ou `.env`)
3. Confirme `.cursor/mcp.json` (copie de `mcp.json.example` se necessário)
4. Reinicie Cursor → Settings → MCP → indicador verde em `github`
5. Teste no chat: "Liste issues abertas neste repositório"

Alternativa local: Docker — ver `.sdlc/integrations/github.md`

## gh CLI

```powershell
winget install GitHub.cli
gh auth login
.sdlc/scripts/gh-labels-bootstrap.ps1
```

## SDLC

[../.sdlc/README.md](../.sdlc/README.md) · [github-lifecycle](../.sdlc/workflows/github-lifecycle.md)
