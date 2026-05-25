# Command: Technical Documentation

## Objetivo

Criar ou atualizar documentação técnica versionada no repositório a partir de specs, arquitetura, decisões e mudanças de código.

## Quando Usar

- Uma mudança altera contrato, arquitetura, agente, workflow ou integração.
- Um ADR ou doc técnico precisa ser criado.
- Há drift entre docs, specs e implementação.
- Um PR precisa de contexto técnico para revisão.

## Agente E Skills

- Agente preferencial: `spec-author`
- Apoio quando necessário: `sdlc-doctor`, `codegen-integrator`
- Adapter Cursor: `.cursor/agents/subagents/spec-author.md`
- Skills:
  - `.sdlc/skills/dsl-authoring/`
  - `.sdlc/skills/deep-agent-harness/`
  - `.sdlc/skills/safe-refactor/`

## Entradas

- Mudança técnica ou decisão a documentar.
- Specs impactadas em `specs/`.
- Arquivos de arquitetura em `docs/`.
- Status de validate/compile quando relevante.

## Procedimento

1. Identificar a fonte canônica da mudança: `specs/`, `.sdlc/agents/`, código ou integração.
2. Localizar docs existentes antes de criar novos arquivos.
3. Documentar contratos, decisões, fluxos, limites e riscos.
4. Linkar specs, comandos e workflows relacionados.
5. Registrar lacunas e próximos passos sem esconder pendências.
6. Validar que `generated/` não foi editado manualmente.

## Saída Esperada

```text
Documentação técnica atualizada:
- arquivo -> mudança -> por quê

Decisões:
- decisão -> impacto -> alternativa rejeitada se relevante

Pendências:
1. ...
2. ...
```

## Guardrails

- Não copiar implementação inteira para docs.
- Não criar documentação paralela quando já existe doc canônico.
- Não editar `generated/` manualmente.
- Código em inglês; documentação pode seguir português do projeto.
