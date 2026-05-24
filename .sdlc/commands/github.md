# gh CLI — referência SDLC

## Instalação

- Windows: `winget install GitHub.cli`
- https://cli.github.com/

## Autenticação

```powershell
gh auth login
gh auth status
```

Defina repositório padrão (opcional):

```powershell
$env:GITHUB_REPOSITORY = "owner/rpg-op"
gh repo set-default owner/rpg-op
```

## Issues

```powershell
# Listar
gh issue list
gh issue list --label "sdlc:intent"

# Criar (manual)
gh issue create --title "Intent: …" --body-file .sdlc/templates/intent.md --label "sdlc:intent,type:feature"

# Ver
gh issue view 12 --web

# Branch a partir de issue
gh issue develop 12 --checkout
```

## Pull requests

```powershell
gh pr create --title "feat: …" --body-file .github/PULL_REQUEST_TEMPLATE.md
gh pr list
gh pr checks
gh pr view --web
gh pr merge --squash
```

## Actions

```powershell
gh workflow list
gh run list --workflow=sdlc.yml
gh run view <run-id> --log-failed
```

## Repo

```powershell
gh repo clone owner/rpg-op
gh repo view
```

Scripts encapsulados em `.sdlc/scripts/gh-*.ps1`.
