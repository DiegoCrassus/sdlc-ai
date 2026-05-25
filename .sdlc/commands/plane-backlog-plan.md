# Command: Plane Backlog Plan

## Objetivo

Analisar uma intenção e criar ou atualizar tarefas no backlog Plane com rastreabilidade para o SDLC.

## Quando Usar

- Uma nova intenção precisa virar backlog acionável.
- Um épico ou melhoria precisa ser quebrado em work items.
- Issues GitHub precisam ser espelhadas no Plane.
- O time precisa de próximos passos claros antes de spec/implementação.

## Agente E Skills

- Agente: `plane-integrator`
- Adapter Cursor: `.cursor/agents/subagents/plane-integrator.md`
- Skills:
  - `.sdlc/skills/plane-sdlc/`
  - `.sdlc/skills/github-sdlc/`

## Entradas

- Intenção ou problema a resolver.
- Contexto de produto/negócio.
- Links de GitHub issue, PR, docs ou specs existentes.
- Projeto Plane alvo, quando conhecido.

## Procedimento

1. Confirmar autenticação Plane via MCP e resolver workspace/projeto.
2. Ler a intenção e extrair objetivos, entregáveis, dependências e riscos.
3. Consultar backlog existente para evitar duplicatas.
4. Propor decomposição em work items pequenos e rastreáveis.
5. Criar ou atualizar work items no Plane quando autorizado pelo usuário.
6. Linkar GitHub issue/PR quando existir.
7. Retornar resumo com IDs Plane, status e próximos passos SDLC.

## Saída Esperada

```text
Backlog Plane:
- RPG-123: título -> objetivo -> status -> link

Rastreabilidade:
- GitHub issue/PR relacionado
- Specs/docs relacionados

Próximos passos:
1. ...
2. ...
```

## Guardrails

- Não deletar work items sem confirmação humana.
- Não expor `PLANE_API_KEY` ou tokens.
- Specs técnicas continuam em `specs/`; Plane recebe resumo, decisões e links.
