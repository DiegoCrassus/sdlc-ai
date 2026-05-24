# Eval suites — RPG-OP

Configuração declarativa; cenários detalhados em `specs/evals/` quando existirem.

```yaml
# suites.yaml
suites:
  smoke:
    description: Gates rápidos em PR
    required_from: f2-agent
    scenarios: []

  template-analysis:
    description: sheet-template-analyst extrai campos mínimos
    fixtures: .sdlc/evals/fixtures/
    scenarios: []
```

## MVP (F2)

- Fixture: imagem/PDF anonimizado de ficha
- Assert: `character_name`, bloco atributos presentes no schema draft
- Assert: `canvas_spec.regions` não vazio

## Tooling

- LangSmith quando `LANGCHAIN_TRACING_V2=true`
- Local: `rpg eval run --suite smoke` (future)
