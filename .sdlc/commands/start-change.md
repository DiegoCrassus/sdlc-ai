# Command: Start Change

## Objetivo

Iniciar qualquer alteração de código com branch SDLC correta, card Plane em progresso e rastreabilidade GitHub.

## Quando usar

- Antes da primeira edição de código na sessão
- Ao pegar um card Plane para implementar
- Ao iniciar correção de bug (`bugfix/`)
- Quando o agente detecta branch protegida ou nome inválido

## Agente e skills

- Agente: `dev-orchestrator` ou `plane-integrator` + `github-integrator`
- Skills:
  - `.sdlc/skills/branch-naming/`
  - `.sdlc/skills/plane-sdlc/`
  - `.sdlc/skills/plane-task-creation/`
  - `.sdlc/skills/plane-card-execution/`
  - `.sdlc/skills/github-sdlc/`

## Entradas

- Identificador Plane (`RPG-123`) — **obrigatório e já criado no Plane**
- Tipo: `feature` ou `bugfix`
- Issue GitHub relacionada (opcional)
- Base branch (default: `develop`)

## Procedimento

1. **Validar task Plane** — descrição com seções `context`, `changes`, `acceptance criteria`, `comments` (skill `plane-task-creation`). Se incompleta, enriquecer antes de codar.
2. **Classificar branch** — `feature/` para entrega nova; `bugfix/` para defeito, lint ou regressão.
3. **Atualizar Plane** — mover card para **In Progress**; comentar início com branch prevista.
4. **Criar branch sempre a partir de `develop`**:

```bash
.sdlc/scripts/gh-branch-start.sh feature RPG-123
.sdlc/scripts/gh-branch-start.sh bugfix RPG-456
```

5. **Espelhar GitHub** (se issue existir) — label `sdlc:implement`; comentário com branch.
6. **Confirmar** — branch atual casa com `^(feature|bugfix)/[A-Za-z]+-\d+$`.

## Saída esperada

```text
Change started:
- Plane: RPG-123 (In Progress)
- Branch: feature/RPG-123
- Base: develop
- GitHub issue: #42 (se aplicável)

Próximo: implementar → make validate → finish_change
```

## Guardrails

- Não editar código em `main`, `develop` ou `master`
- Não criar branch sem identificador Plane existente
- Não usar slugs livres (`feat/foo-bar`) — padrão canônico é `feature/RPG-N`
- Não passar base customizada; o script usa `develop`
- Se Plane task não existir, usar `plane_backlog_plan` primeiro

## Referências

- Workflow: `.sdlc/workflows/change-lifecycle.md`
- Script: `.sdlc/scripts/gh-branch-start.sh`
