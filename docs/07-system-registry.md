# Template Registry (fase posterior)

> **Status:** backlog — o MVP não usa plugins D&D/Tormenta. O template vem do **exemplo que o mestre envia**. Ver [08-sheet-canvas.md](08-sheet-canvas.md).

## Papel no MVP

| Conceito | MVP | Futuro |
|----------|-----|--------|
| Origem do schema | Análise da ficha exemplo (GM) | + presets opcionais no registry |
| Registry | `sheet_templates` por campanha | Catálogo global de presets |
| Subagentes | `sheet-template-analyst` | + import, rules, etc. |

## Template por campanha (MVP)

Cada campanha tem zero ou um template **publicado**:

```
campaign → sheet_template (published)
         → sheet_template (drafts)
         → sheets[] (dados dos jogadores)
```

Resolução em runtime:

```python
def get_canvas_context(campaign_id: str) -> CanvasContext:
    template = repo.get_published_template(campaign_id)
    if not template:
        raise TemplateNotPublished()
    return CanvasContext(
        schema=template.schema_json,
        canvas_spec=template.canvas_spec_json,
        version=template.version,
    )
```

## Registry global (fase F6+)

Quando existir, permitirá:

- Presets (`dnd5e-official-sheet@v1`) como **atalho** — GM escolhe preset **ou** upload.
- Preset acelera análise (subagente parte de schema base + ajusta layout ao scan).
- Mesma IR: `SheetSchema` + `CanvasSpec`.

Estrutura prevista:

```
specs/systems/          # presets opcionais
packages/rpg_registry/  # loader
generated/registry/
```

## Por que adiar

1. Foco atual: canvas fiel ao **exemplo real da mesa**, não ao SRD genérico.
2. Menos superfície: um subagente, um fluxo GM.
3. Presets podem ser adicionados sem quebrar templates derivados de upload.

## Referência histórica

Documentação anterior descrevia registry agnóstico com subagentes por cenário (combat, leveling, …). Isso foi **arquivado** em favor do fluxo template-analyst. Recuperar cenários quando o canvas MVP estiver estável.
