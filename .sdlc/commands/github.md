# gh CLI — referência SDLC

## Instalação

- Windows: `winget install GitHub.cli`
- https://cli.github.com/

## Autenticação

```bash
gh auth login
gh auth status
```

Defina repositório padrão (opcional):

```bash
export GITHUB_REPOSITORY="owner/rpg-op"
gh repo set-default owner/rpg-op
```

## Issues

```bash
# Listar
gh issue list
gh issue list --label "sdlc:intent"

# Criar (manual)
gh issue create --title "Intent: …" --body-file .sdlc/templates/intent.md --label "sdlc:intent,type:feature"

# Ver
gh issue view 12 --web

# Não use `gh issue develop` neste projeto.
# Branches devem vir de tarefa Plane:
.sdlc/scripts/gh-branch-start.sh feature RPG-123
.sdlc/scripts/gh-branch-start.sh bugfix RPG-456
```

## Pull requests

```bash
gh pr create --base develop --title "feat: …" --body-file .github/PULL_REQUEST_TEMPLATE.md
gh pr list
gh pr checks
gh pr view --web
# Merge apenas após aprovação humana explícita e checks verdes
gh pr merge --squash
```

## Actions

```bash
gh workflow list
gh run list --workflow=sdlc.yml
gh run view <run-id> --log-failed
```

## Repo

```bash
gh repo clone owner/rpg-op
gh repo view
```

Scripts encapsulados em `.sdlc/scripts/gh-*.sh`.
