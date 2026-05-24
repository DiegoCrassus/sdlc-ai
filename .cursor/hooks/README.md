# Cursor hooks — pre/post + LangSmith

Hooks registrados em [hooks.json](../hooks.json). Scripts Python em `hooks/`.

## Eventos

| Evento | Script | Papel |
|--------|--------|-------|
| **sessionStart** (pre) | `session_start.py` | Root run LangSmith + contexto SDLC |
| **sessionEnd** (post) | `session_end.py` | Finaliza sessão |
| **beforeSubmitPrompt** (pre) | `before_submit_prompt.py` | Audit prompt; bloqueia secrets |
| **stop** (post) | `stop.py` | Fim de turno do agente |
| **preToolUse** (pre) | `pre_tool_use.py` | Bloqueia write em `generated/` |
| **postToolUse** (post) | `post_tool_use.py` | Log tool OK |
| **postToolUseFailure** (post) | `post_tool_use_failure.py` | Log tool erro |
| **beforeShellExecution** (pre) | `before_shell.py` | Audit shell; ask em force push main |
| **afterShellExecution** (post) | `after_shell.py` | Log output shell |
| **beforeMCPExecution** (pre) | `before_mcp.py` | Audit MCP (GitHub) |
| **afterMCPExecution** (post) | `after_mcp.py` | Log resultado MCP |

## LangSmith

1. `pip install -r .sdlc/requirements-hooks.txt`
2. `.env`:
   ```
   LANGCHAIN_API_KEY=lsv2_pt_...
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_PROJECT=rpg-op-cursor
   ```
3. Projeto separado `rpg-op-cursor` para logs do IDE vs `rpg-op` (runtime agente)

Ver [.sdlc/integrations/langsmith.md](../../.sdlc/integrations/langsmith.md).

## Fallback local

Sem API key: logs em `.sdlc/logs/cursor-hooks.jsonl` (gitignored).

## Debug

Cursor → Settings → Hooks → output channel.

Teste manual:

```powershell
echo '{}' | python .cursor/hooks/session_start.py
Get-Content .sdlc/logs/cursor-hooks.jsonl -Tail 3
```

## Windows

Use `python` no PATH ou ajuste `hooks.json` para caminho do venv:

```json
"command": "backend/.venv/Scripts/python.exe .cursor/hooks/session_start.py"
```
