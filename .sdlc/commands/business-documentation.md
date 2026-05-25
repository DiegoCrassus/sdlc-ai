# Command: Business Documentation

## Objetivo

Transformar intenção, escopo e decisões de produto em documentação de negócio clara, rastreável e útil para backlog, priorização e validação humana.

## Quando Usar

- Uma ideia precisa virar descrição de produto.
- Um épico precisa de objetivo, escopo e critérios de sucesso.
- Uma Plane Page precisa registrar contexto de negócio.
- Uma issue técnica precisa ser explicada em linguagem de negócio.

## Agente E Skills

- Agente preferencial: `plane-integrator`
- Apoio quando necessário: `github-integrator`, `sdlc-doctor`
- Adapter Cursor: `.cursor/agents/subagents/plane-integrator.md`
- Skills:
  - `.sdlc/skills/plane-sdlc/`
  - `.sdlc/skills/github-sdlc/`

## Entradas

- Objetivo de negócio.
- Usuários/personas impactados.
- Problema, oportunidade ou hipótese.
- Critérios de sucesso e restrições.
- Links de Plane/GitHub/docs quando existirem.

## Procedimento

1. Resumir o objetivo em linguagem de negócio.
2. Separar escopo, não escopo, riscos e dependências.
3. Definir critérios de aceitação verificáveis.
4. Linkar work items Plane, GitHub issues/PRs e docs técnicos relacionados.
5. Criar ou atualizar Plane Page quando autorizado.
6. Retornar resumo executivo e próximos passos.

## Saída Esperada

```text
Resumo executivo:
- problema
- objetivo
- resultado esperado

Escopo:
- dentro
- fora

Critérios de aceitação:
1. ...
2. ...

Rastreabilidade:
- Plane
- GitHub
- Docs técnicos
```

## Guardrails

- Não duplicar specs técnicas completas no Plane.
- Linkar fontes canônicas no repositório.
- Separar decisão de negócio de detalhe de implementação.
- Não expor tokens ou dados sensíveis.
