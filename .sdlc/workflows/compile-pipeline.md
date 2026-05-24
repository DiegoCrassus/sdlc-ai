# Compile pipeline

```bash
# From repo root (future)
rpg validate specs/
rpg compile --target pydantic
rpg compile --target typescript
rpg compile --target agent_manifest
rpg compile --target cursor_rules
```

## Outputs

| Target | Consumer |
|--------|----------|
| pydantic | backend validation |
| typescript | apps/web types |
| agent_manifest | services/agent |
| cursor_rules | .cursor/rules/generated-*.mdc |

## Local gate script

```powershell
.sdlc/scripts/validate.ps1
```

Until `rpg` exists, script runs pytest smoke only.
