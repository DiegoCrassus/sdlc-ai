# Command: Finish Change

## Objetivo

Encerrar uma unidade de trabalho com validate, commit, push e PR — fechando o loop SDLC.

## Quando usar

- Ao concluir implementação ou spec de uma task
- Ao fim de sessão de agente com arquivos modificados
- Antes de pedir review humano
- Após `issue_resolution` corrigir lint/CI

## Agente e skills

- Agente: `github-integrator` + `code-reviewer` (handoff)
- Skills:
  - `.sdlc/skills/github-sdlc/`
  - `.sdlc/skills/branch-naming/`
  - `.sdlc/skills/plane-card-execution/`
  - `.sdlc/skills/pr-code-review/`

## Entradas

- Branch atual (`feature/RPG-N` ou `bugfix/RPG-N`)
- Plane task identifier
- Issue GitHub (opcional)
- Mensagem de commit (ou gerar a partir do diff)

## Procedimento

1. **Verificar branch** — deve seguir branch-naming; nunca commitar em branch protegida.
2. **Validar**:

```bash
make validate
```

3. **Revisar diff** — sem edição manual em `generated/`; specs atualizadas se contrato mudou.
4. **Commit** — mensagem convencional:

```bash
git add -A
git commit -m "feat: descrição clara alinhada ao RPG-123"
```

5. **Push**:

```bash
git push -u origin HEAD
```

6. **Abrir PR** (se ainda não existir):

```bash
.sdlc/scripts/gh-pr-open.sh "feat: título do PR" <issue-number>
```

7. **Plane** — comentar link do PR; mover para **In Review** se PR aberto.
8. **Delegar** — `pr_code_review` → `pr_approval_watch`.

## Saída esperada

```text
Change finished:
- Commit: abc1234
- Branch: feature/RPG-123 (pushed)
- PR: #55
- Plane: RPG-123 → In Review

Checks: aguardando Actions SDLC
Próximo: pr_code_review / pr_approval_watch
```

## Guardrails

- Não push sem validate verde (salvo WIP explícito autorizado)
- Não mergear — delegar `pr_approval_watch`
- Não fechar Plane como Done até merge em develop
- Commits atômicos por unidade lógica; evitar "misc fixes"

## Referências

- Workflow: `.sdlc/workflows/change-lifecycle.md`
- PR template: `.github/PULL_REQUEST_TEMPLATE.md`
