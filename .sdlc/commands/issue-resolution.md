# Command: Issue Resolution

## Objetivo

Resolver issues geradas por CI, lint, review, hooks ou bloqueios SDLC sem aguardar intervenção humana.

## Procedimento

1. Ler issue, labels, links de Actions, PR, branch e Plane.
2. Identificar causa raiz.
3. Mover card Plane relacionado para `In Progress`.
4. Implementar correção mínima segura.
5. Validar localmente e/ou remotamente.
6. Atualizar PR/branch.
7. Comentar evidência e fechar issue apenas com checks verdes.

## Guardrails

- Não enfraquecer checks para “resolver” issue.
- Criar skill/command se a issue revelar procedimento ausente.
- Registrar toda decisão no card Plane ou issue GitHub.
