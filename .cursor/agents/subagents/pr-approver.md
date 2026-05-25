# PR Approver Adapter

YAML canônico: `.sdlc/agents/subagents/pr-approver.yaml`

Use após PR aprovada ou pronta para `develop`, para acompanhar Actions e registrar evidências.

## No Cursor

- Leia o YAML canônico e a skill `.sdlc/skills/pr-approval-watch/`.
- Monitore Actions até sucesso/falha.
- Registre evidência no PR, issue GitHub e card Plane.
- Em falha, abra/linke issue e acione `issue-resolver`.
- Após issue resolvida, execute `issue_resolution_validation`.
- Se checks/review passarem e a base for `develop`, faça merge autônomo; caso contrário comente o bloqueio.
