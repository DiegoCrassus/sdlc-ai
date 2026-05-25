# Command: PR Approval Watch

## Objetivo

Acompanhar PR aprovada até integração em `develop`, monitorando Actions e registrando evidências.

## Procedimento

1. Confirmar aprovação ou prontidão para `develop`.
2. Conferir branch base, branch head e checks obrigatórios.
3. Monitorar Actions até conclusão.
4. Se falhar, criar/linkar issue e acionar `issue-resolver`.
5. Se passar, comentar evidência no PR, issue GitHub e Plane.
6. Atualizar cards Plane conforme critérios de aceite.

## Guardrails

- Não ignorar checks falhos.
- Não burlar branch protection.
- Não considerar concluído sem evidência remota.
