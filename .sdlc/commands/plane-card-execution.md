# Command: Plane Card Execution

## Objetivo

Executar uma tarefa do board Plane com movimentação de card, evidência e rastreabilidade GitHub.

## Procedimento

1. Resolver o work item Plane por identificador (`RPG-13`, por exemplo).
2. Mover o card para `In Progress` antes de editar código, docs, banco ou infraestrutura.
3. Executar a tarefa usando o fluxo SDLC apropriado.
4. Registrar evidência no card:
   - Branch, commit e PR.
   - Comandos de validação.
   - Actions/checagens remotas.
   - Riscos residuais.
5. Mover para `Done` somente quando os critérios de aceite estiverem satisfeitos.

## Guardrails

- Nunca deixar uma tarefa executada sem comentário de evidência.
- Se surgir lacuna de processo, criar ou atualizar skill/command antes de continuar.
- Não mover para `Done` quando PR/check ainda bloqueia o aceite.
