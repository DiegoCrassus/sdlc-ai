# Visão e escopo



## Problema



Mesas de RPG podem durar anos. Fichas em papel degradam, somem ou ficam ilegíveis. Jogadores e mestres precisam ver e controlar personagens de forma clara, no **mesmo layout** que já usam na mesa.



## Objetivos do produto (MVP)



1. **Template a partir do exemplo do mestre** — GM envia ficha real (PDF/foto); sistema deriva schema e layout.

2. **Apresentação em canvas** — jogadores e GM veem fichas num layout visual alinhado ao exemplo, não num formulário genérico.

3. **Controle por papel** — jogador edita a própria ficha; GM vê todas e pode estender o template (mais campos/seções).

4. **Persistência durável** — dados validados contra schema versionado; histórico de revisões (fase 2).



## Objetivos posteriores (fora do MVP)



- Assistente conversacional (regras, sugestões, import em massa).

- Plugins por sistema (D&D, Tormenta) como atalho opcional.

- App móvel.



## Princípios arquiteturais



| Princípio | Implicação |

|-----------|------------|

| **Ficha visual primeiro** | `canvas_spec` é cidadão de primeira classe, gerado junto com o schema. |

| **Exemplo do GM manda** | Schema não vem de preset fixo; vem da análise da ficha exemplo. |

| **Um subagente especializado** | `sheet-template-analyst` faz análise passo a passo; sem zoo de cenários. |

| **Fonte da verdade fora do LLM** | PostgreSQL guarda template publicado e dados; agente propõe drafts. |

| **BFF para o cliente** | Web consome API estável; canvas renderizado no frontend. |

| **SDLC AI-native** | DSL descreve `SheetSchema`, `CanvasSpec`, saída do subagente; `rpg compile` gera tipos. |



## Fora do escopo inicial (MVP)



- Subagentes de combate, leveling, inventário, Q&A de regras.

- Mapas táticos, voz, marketplace.

- OCR em massa de fichas antigas dos jogadores (só **template** a partir de um exemplo).



## Atores



- **Mestre (GM)** — envia exemplo, revisa análise, publica template, vê todas as fichas, estende campos.

- **Jogador** — vê e edita a própria ficha no canvas.

- **Subagente `sheet-template-analyst`** — analisa exemplo, constrói schema + canvas; não publica sozinho.



## Glossário



- **Ficha exemplo** — PDF/imagem que o GM envia como referência visual e estrutural.

- **Template de campanha** — `sheet_schema` + `canvas_spec` publicados para uma campanha.

- **Sheet Canvas** — componente UI que renderiza ficha conforme `canvas_spec` + dados.

- **Análise por passos** — trace do subagente (`analysis.steps`) para revisão do GM.

- **Harness** — Deep Agents SDK (orquestrador + subagente de template).

- **Extensão de template** — novos campos/seções sem reupload do exemplo.

