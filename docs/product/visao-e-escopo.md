# Visão e escopo

## Problema

Mesas de RPG podem durar anos. Fichas em papel degradam, somem ou ficam ilegíveis. Jogadores e mestres precisam ver e controlar personagens de forma clara, no **mesmo layout** que já usam na mesa.

## Objetivos validados no PoC

1. **Template a partir do exemplo do mestre** — GM envia ficha real (PDF/foto); sistema deriva schema e layout.
2. **Apresentação em canvas** — jogadores e GM veem fichas num layout visual alinhado ao exemplo.
3. **Controle por papel** — jogador edita a própria ficha; GM vê todas e estende o template.
4. **Persistência durável** — dados validados contra schema versionado; revisões básicas.

Evidências: [docs/poc/00-indice-poc.md](../poc/00-indice-poc.md)

## Objetivos posteriores

Ver [docs/05-roadmap.md](../05-roadmap.md) — Fases 1–4 (hardening → alpha → beta → produto).

- Assistente conversacional (regras, sugestões, import em massa)
- Presets por sistema (D&D, Tormenta) como atalho opcional
- App móvel

## Princípios arquiteturais

| Princípio | Implicação |
|-----------|------------|
| **Ficha visual primeiro** | `canvas_spec` é cidadão de primeira classe, gerado junto com o schema |
| **Exemplo do GM manda** | Schema vem da análise da ficha exemplo, não de preset fixo |
| **DPA Agent especializado** | Análise passo a passo; sem zoo de subagentes por cenário |
| **Fonte da verdade fora do LLM** | DB guarda template publicado; agente propõe drafts |
| **BFF para o cliente** | Web consome API estável; canvas no frontend |
| **SDLC AI-native** | DSL em `specs/`; `rpg compile` gera tipos e manifests |

## Fora do escopo (PoC e Fase 1)

- Subagentes de combate, leveling, inventário, Q&A de regras
- Mapas táticos, voz, marketplace
- OCR em massa de fichas antigas (só template a partir de um exemplo)

## Atores

- **Mestre (GM)** — envia exemplo, revisa análise, publica template, vê todas as fichas, estende campos
- **Jogador** — vê e edita a própria ficha no canvas
- **DPA Agent** — analisa exemplo, constrói schema + canvas; **não publica** sozinho

## Glossário

| Termo | Definição |
|-------|-----------|
| **Workspace** | Mesa de RPG (substitui “campanha” no PoC) |
| **Ficha exemplo** | PDF/imagem que o GM envia como referência |
| **Template** | `sheet_schema` + `canvas_spec` publicados para um workspace |
| **Sheet Canvas** | Componente UI que renderiza ficha conforme `canvas_spec` |
| **PoC** | Proof of Concept local — fases 0–4 concluídas |
