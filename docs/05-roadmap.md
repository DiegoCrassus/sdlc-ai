# Roadmap de MVPs — RPG-OP

Roadmap realista para chegar ao objetivo final do ciclo atual: **interface funcional para mestre e jogador**, **backend com BFF**, persistência estruturada e base preparada para o subagente `sheet-template-analyst`.

O norte do produto continua sendo o mesmo: o mestre envia uma ficha real da mesa, o sistema transforma isso em `SheetSchema` + `CanvasSpec`, e os jogadores usam a ficha em um canvas visual fiel ao modelo original.

## Premissas

- O MVP deve validar primeiro a experiência de ficha visual, mesmo antes do LLM.
- O backend expõe uma API BFF estável para a UI; lógica de domínio e validação ficam fora do agente.
- A DSL em `specs/` é fonte de verdade para contratos, schemas, canvas e agent manifest.
- O subagente propõe drafts; publicação de template sempre passa pelo mestre.
- Plugins por sistema, chat amplo, OCR em massa e app móvel ficam fora do ciclo principal.

## Estado atual

| Área | Estado |
|------|--------|
| SDLC AI-native | Harness `.sdlc/` e `.cursor/` ativos |
| DSL | Base mínima implementada; specs de canvas, sheet e subagente existem |
| Artefatos gerados | Pydantic, JSON Schema, manifest de agente, skills e registry parciais |
| Backend | FastAPI scaffolded; dependências locais ainda precisam ser instaladas |
| Frontend | React/Vite scaffolded; UI provisória |
| Plane/GitHub/LangSmith | Integrações documentadas; confirmação operacional depende de credenciais locais |

## MVP 0 — Fundação SDLC e contratos

**Objetivo:** consolidar a base técnica que permite evoluir sem duplicar schema entre backend, frontend e agente.

**Entregas principais**

- DSL `rpg_dsl` mínima instalada e executável via `rpg`.
- Specs em `specs/templates/` para ficha e canvas D&D 5e de referência.
- Spec do subagente `sheet-template-analyst`.
- `rpg validate specs/` e `rpg compile` funcionando localmente.
- Targets gerados prioritários: Pydantic, JSON Schema, TypeScript, OpenAPI e agent manifest.
- CI local via `.sdlc/scripts/validate.ps1`.

**Critério de saída**

Uma spec versionada compila para artefatos consumíveis pelo backend e frontend, sem edição manual em `generated/`.

## MVP 1 — Backend/BFF e UI funcional sem LLM

**Objetivo:** entregar o primeiro fluxo usável de campanha e ficha visual, usando template fixture/manual, sem depender ainda do subagente.

**Entregas principais**

- Modelo de dados inicial: `campaigns`, `campaign_members`, `sheet_templates`, `characters`, `sheets`, `sheet_revisions`, `attachments`.
- BFF `/v1` com rotas de campanha, template publicado e fichas.
- Payload agregado para UI: `sheet` + `schema_json` + `canvas_spec_json` + `template_version`.
- Validação de dados da ficha contra JSON Schema do template.
- `SheetCanvas` React com apresentações mínimas: `field_grid`, `stat_row`, `rich_text`.
- Fluxo jogador: abrir a própria ficha, editar campos permitidos e salvar.
- Fluxo mestre: ver fichas da campanha em dashboard simples.
- Seed/fixture de campanha piloto para testar ponta a ponta.

**Critério de saída**

Um mestre consegue abrir uma campanha piloto, ver fichas dos jogadores, e um jogador consegue editar a própria ficha no canvas. Tudo funciona com BFF + persistência, sem LLM.

## MVP 2 — Upload, análise e publicação de template

**Objetivo:** transformar a ficha exemplo do mestre em um template revisável, mantendo HITL antes da publicação.

**Entregas principais**

- Upload de ficha exemplo (`PDF`, `PNG`, `JPG`) em `template/source`.
- Serviço de agente com orquestrador leve e subagente `sheet-template-analyst`.
- Skill `template-analysis` com passos: segmentar regiões, listar campos, inferir tipos, montar canvas e emitir warnings.
- Persistência de `analysis_json`, `schema_json` e `canvas_spec_json` como draft.
- UI de revisão com passos da análise + preview do canvas ao lado do exemplo.
- Correções manuais do mestre antes de publicar.
- Endpoint `template/publish` com confirmação humana.
- Evals smoke com 2 fixtures anonimizadas e trace LangSmith.

**Critério de saída**

O mestre envia uma ficha real, revisa a análise, publica um template e passa a usar esse template no mesmo fluxo funcional do MVP 1.

## MVP 3 — Campanha pronta para sessão real

**Objetivo:** fechar lacunas de uso em mesa para mestre e jogador.

**Entregas principais**

- `role_overrides` no canvas: campos somente GM, campos somente leitura e permissões por papel.
- Indicadores no dashboard do mestre: fichas incompletas, versão do template e último update.
- Histórico básico de revisões por ficha.
- Layout responsivo para notebook/tablet.
- Estados de erro e loading para upload, análise, publish e save.
- Testes focados nos fluxos principais do BFF e componentes críticos do canvas.

**Critério de saída**

Uma campanha pequena consegue usar o RPG-OP em uma sessão real com mestre e jogadores, sem edição de JSON ou intervenção técnica.

## MVP 4 — Extensão controlada de template

**Objetivo:** permitir que o mestre evolua o template sem reenviar a ficha original.

**Entregas principais**

- Endpoint `template/extend`.
- Modo `extend` do `sheet-template-analyst` para propor novos campos/seções.
- Nova versão de template a partir de patch append-only.
- Defaults para fichas existentes quando novos campos forem adicionados.
- UI "Adicionar campo/seção" com preview antes de publicar.
- Confirmação explícita para remoção de campos com dados.

**Critério de saída**

O mestre adiciona pelo menos uma seção ou campo novo, publica uma nova versão do template, e fichas existentes continuam válidas.

## Depois do ciclo principal

| Fase | Conteúdo |
|------|----------|
| F5 | Assistente conversacional sobre a ficha e ações assistidas |
| F6 | Registry global com presets D&D/Tormenta como atalhos opcionais |
| F7 | Import OCR de fichas preenchidas antigas |
| F8 | App móvel e experiência offline parcial |
| F9 | RAG de regras, automações avançadas e subagentes por cenário |

## Sequência recomendada

1. Fechar MVP 0: instalar `rpg_dsl`, validar specs e garantir compile dos targets essenciais.
2. Implementar MVP 1: priorizar BFF + `SheetCanvas` funcional com fixture.
3. Só então iniciar MVP 2: adicionar o agente de análise ao fluxo já funcional.
4. Usar MVP 3 para preparar piloto real.
5. Implementar MVP 4 após validar que a estrutura de template publicado está estável.

## Riscos e mitigação

| Risco | Mitigação |
|-------|-----------|
| Canvas não ficar fiel ao modelo real | Começar com poucos `presentation` types e evoluir a partir de fichas reais |
| LLM gerar schema errado | Passos visíveis, warnings, preview e correção pelo mestre antes do publish |
| Backend e frontend divergirem nos contratos | Specs DSL + compile para Pydantic/JSON Schema/TypeScript/OpenAPI |
| Escopo crescer para chat e regras cedo demais | MVP 1 valida ficha visual sem agente; MVP 2 limita o agente ao template |
| Migração de template quebrar fichas existentes | Versionamento, patches append-only e defaults para novos campos |

## Definição de sucesso do ciclo

- Mestre cria ou seleciona uma campanha.
- Mestre publica um template de ficha a partir de fixture ou upload analisado.
- Jogador preenche e salva a própria ficha no canvas.
- Mestre acompanha todas as fichas da campanha.
- Backend/BFF, UI e specs estão alinhados por artefatos gerados.
- O produto está pronto para piloto com uma mesa pequena.
