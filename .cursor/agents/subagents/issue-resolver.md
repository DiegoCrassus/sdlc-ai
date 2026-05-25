# Issue Resolver Adapter

YAML canônico: `.sdlc/agents/subagents/issue-resolver.yaml`

Use para issues geradas por CI, lint, hooks, review ou bloqueios SDLC.

## No Cursor

- Leia o YAML canônico e a skill `.sdlc/skills/issue-resolution/`.
- Identifique causa raiz, corrija no menor escopo seguro e valide.
- Mova o card Plane relacionado e registre evidência antes de fechar a issue.
- Não finalize após push: entregue obrigatoriamente para `issue_resolution_validation`.
