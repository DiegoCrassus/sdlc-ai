# PR Approver Adapter

YAML canônico: `.sdlc/agents/subagents/pr-approver.yaml`

Use após PR aprovada pelo dono ou pronta para acompanhar Actions rumo a `develop`.

## No Cursor

- Leia o YAML canônico e a skill `.sdlc/skills/pr-approval-watch/`.
- Monitore Actions até sucesso/falha.
- Registre evidência no PR, issue GitHub e card Plane.
- Em falha, abra/linke issue e acione `issue-resolver`.
- Após issue resolvida, execute `issue_resolution_validation`.
- Se checks passarem, a base for `develop` e houver aprovação humana explícita, faça merge; caso contrário comente o bloqueio.
