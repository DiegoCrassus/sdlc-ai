# Template analysis workflow — DPA Agent

## Passos

1. **Carregar fonte** — imagem, PDF, JSON ou descrição textual do workspace.
2. **Segmentar regiões** — cabeçalho, atributos, combate, anotações.
3. **Extrair campos** — key snake_case, label, type, constraints.
4. **Inferir tipos** — string, integer, text, boolean; marcar confidence.
5. **Montar canvas_spec** — regions, presentation (field_grid, stat_row, rich_text).
6. **Emitir warnings** — campos incertos, regiões ambíguas.

## Saída

`TemplateAnalysisResult` conforme `specs/templates/analysis_result.py`.

## HITL

Publicação só após `POST /v1/workspaces/{id}/template/publish` com confirmação do mestre.
