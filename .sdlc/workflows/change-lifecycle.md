# Change lifecycle — toda alteração de código

Workflow **obrigatório** para qualquer mudança no repositório. Complementa [github-lifecycle.md](github-lifecycle.md) e [plane-lifecycle.md](plane-lifecycle.md).

```mermaid
flowchart TB
    A[Plane task ready] --> B[start_change]
    B --> C[Branch feature/RPG-N ou bugfix/RPG-N]
    C --> D[Implement]
    D --> E[make test + lint + validate]
    E --> F[finish_change]
    F --> G[Commit + push + PR]
    G --> H[GitHub Actions]
    H --> I{Checks verdes?}
    I -->|não| K[Issue + issue_resolver]
    K --> H
    I -->|sim| L[Owner approval]
    L --> M[Merge develop]
```

## Regra de ouro

**Nenhuma alteração de código** em branch protegida (`main`, `develop`, `master`). Toda mudança começa com `start_change` e termina com `finish_change`.

## Fase 0 — Plane obrigatório

| Artefato | Onde | Quando |
|----------|------|--------|
| Work item | Plane | Antes de criar branch |
| Descrição rica | Plane (4 seções) | Antes de codar |
| Issue espelhada | GitHub | Criada automaticamente para falha de CI/lint/test ou manualmente quando útil |

O workflow GitHub só pode iniciar depois de existir uma tarefa Plane identificável, por exemplo `RPG-123`.

## Fase 1 — start_change

**Command:** `start_change` · **Script:** `.sdlc/scripts/gh-branch-start.sh`

1. Resolver identificador Plane (`RPG-123`) — skill [branch-naming](../skills/branch-naming/SKILL.md).
2. Classificar: `feature/` para trabalho planejado ou `bugfix/` para bug, regressão, lint ou teste falho.
3. Atualizar card Plane → **In Progress**.
4. Criar branch sempre a partir de `develop`:

```bash
.sdlc/scripts/gh-branch-start.sh feature RPG-123
.sdlc/scripts/gh-branch-start.sh bugfix RPG-456
```

5. Confirmar padrão: `^(feature|bugfix)/[A-Za-z]+-\d+$`

## Fase 2 — Trabalho

Ordem recomendada:

1. **Implement** — código em `apps/`, `.sdlc/`, `.cursor/` ou `.github/`, conforme o escopo.
2. **Validate** — `make test`, `make lint` e `make validate` antes de commit.
3. **Evidence** — registrar comandos executados no PR e no card Plane.

Guardrails locais:

- Commit em branch protegida
- Force-push em `main`/`master`
- Branch sem identificador Plane

## Fase 3 — finish_change

**Command:** `finish_change`

1. `make validate` (ou `.sdlc/scripts/validate.sh`)
2. Commit com mensagem convencional (`feat:`, `fix:`, `spec:`, `chore:`)
3. Push da branch
4. Abrir PR com `.sdlc/scripts/gh-pr-open.sh` ou GitHub MCP
5. Comentar no Plane com link do PR e mover card para **In Review**
6. Aguardar GitHub Actions obrigatórias: lint + testes unitários
7. Se CI falhar: issue automática → `issue_resolution` → nova validação
8. Com aprovação humana e checks verdes: merge em `develop`

## Commits

| Tipo | Prefixo | Exemplo |
|------|---------|---------|
| Feature | `feat:` | `feat: add sheet validation endpoint` |
| Bugfix | `fix:` | `fix: correct DPA analyzer edge case` |
| Spec | `spec:` | `spec: extend TemplateAnalysisResult` |
| Chore | `chore:` | `chore: align branch naming docs` |

Um commit por unidade lógica. Ao fim de cada sessão de agente com alterações, **commit obrigatório** via `finish_change`.

## Integração lint / bugs

Falhas de lint ou CI → ver [lint-bug-resolution.md](lint-bug-resolution.md).

## Commands relacionados

| Command | Uso |
|---------|-----|
| `start_change` | Início: branch + Plane In Progress |
| `finish_change` | Fim: validate + commit + push + PR |
| `plane_card_execution` | Transições Plane com evidência |
| `issue_resolution` | Corrigir issue gerada por CI/lint |
| `issue_resolution_validation` | Validar fix até develop verde |

## Anti-patterns

- Codar direto em `develop` ou `main`
- Branch `feat/12-slug` ou nomes livres (legado — migrar para `feature/RPG-N`)
- PR sem card Plane, sem checks verdes ou sem aprovação humana
- Fechar issue de lint sem evidência de checks verdes
