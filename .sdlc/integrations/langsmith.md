# LangSmith — observabilidade Cursor + agentes

LangSmith recebe **logs do Cursor** (hooks pre/post) e, no futuro, traces do **Deep Agent** em runtime.

## Projetos recomendados

| Projeto LangSmith | Fonte |
|-------------------|--------|
| `rpg-op-cursor` | Hooks IDE (`.cursor/hooks/`) |
| `rpg-op` | Deep Agent produto + evals (F2+) |

Configure via `LANGCHAIN_PROJECT` no `.env`.

## Setup

1. Conta: https://smith.langchain.com/
2. API key: Settings → API Keys → `LANGCHAIN_API_KEY`
3. Instalar deps dos hooks:

```powershell
pip install -r .sdlc/requirements-hooks.txt
```

4. `.env`:

```bash
LANGCHAIN_API_KEY=lsv2_pt_...
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=rpg-op-cursor
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
```

5. Reinicie o Cursor após salvar `.env` (ou exporte variáveis no sistema)

## O que é logado

Cada hook emite runs `cursor/{evento}`:

- `sessionStart` / `sessionEnd` — sessão IDE (run raiz + filhos)
- `beforeSubmitPrompt` — preview sanitizado do prompt (sem secrets)
- `preToolUse` / `postToolUse` — ferramentas do agente
- `beforeShellExecution` / `afterShellExecution` — terminal
- `beforeMCPExecution` / `afterMCPExecution` — GitHub MCP
- `stop` — fim de resposta

**Redação automática:** tokens `sk-`, `ghp_`, keys em texto.

## Fallback local

`.sdlc/logs/cursor-hooks.jsonl` — sempre append (mesmo sem LangSmith).

## Visualizar

1. https://smith.langchain.com/
2. Projeto `rpg-op-cursor`
3. Filtrar por nome `cursor/sessionStart`, `cursor/preToolUse`, etc.

## Runtime Deep Agent (F2+)

No serviço Python:

```python
import os
os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
os.environ.setdefault("LANGCHAIN_PROJECT", "rpg-op")
```

Traces LangGraph aparecem no mesmo workspace, projeto diferente.

## CI / evals

Workflow futuro: upload datasets de `.sdlc/evals/` — ver `suites.yaml`.

## Troubleshooting

| Problema | Solução |
|----------|---------|
| Hooks não rodam | Settings → Hooks; reiniciar Cursor |
| LangSmith vazio | Verificar `LANGCHAIN_API_KEY`; testar script manual |
| Python não encontrado | Apontar venv em `hooks.json` |
| Secrets no trace | Hooks sanitizam; revisar `before_submit_prompt` |

Config declarativa: [langsmith.yaml](langsmith.yaml)
