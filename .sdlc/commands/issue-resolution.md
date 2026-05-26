# Command: Issue Resolution

## Objetivo

Resolver issues geradas por CI, lint, review, hooks ou bloqueios SDLC sem aguardar intervenção humana.

## Procedimento

1. Ler issue, labels, links de Actions, PR, branch e Plane.
2. Identificar causa raiz.
3. Mover card Plane relacionado para `In Progress`.
4. Confirmar que a correção será feita na branch da PR (`feature/RPG-N` ou `bugfix/RPG-N`).
5. Implementar correção mínima segura sem enfraquecer lint/testes.
6. Validar localmente com `make test`, `make lint` e `make validate` quando possível.
7. Atualizar PR/branch e aguardar nova execução das Actions.
8. Comentar evidência e fechar issue apenas com checks verdes no head SHA mais recente.

## Guardrails

- Não enfraquecer checks para “resolver” issue.
- Criar skill/command se a issue revelar procedimento ausente.
- Registrar toda decisão no card Plane ou issue GitHub.
- Não abrir branch sem Plane ID; correções de CI devem preservar rastreabilidade.
