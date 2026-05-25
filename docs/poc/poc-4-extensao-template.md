# PoC 4 — Extensão controlada de template

**Status:** ✅ Concluído  
**Objetivo:** mestre evolui a ficha **sem reenviar** o arquivo original.

## Contexto

Mesas evoluem (montaria, recursos, houserules). O DPA entra em modo **extend** com patches append-only.

## Marcos entregues

| # | Marco | Entregável |
|---|-------|------------|
| P4.1 | `template/extend` | Endpoint + serviço |
| P4.2 | Modo extend | `template_extend.py` |
| P4.3 | Versionamento | Nova `template_version` |
| P4.4 | Migração fichas | Defaults para campos novos |
| P4.5 | UI GM | Formulário estender template |
| P4.6 | Remoção segura | `remove-field` + confirmação |

## Critério de saída

✅ GM adiciona campo/seção, publica nova versão; fichas existentes válidas.

## Código

| Área | Path |
|------|------|
| Extend | `apps/backend/app/services/template_extend.py` |
| Router | `apps/backend/app/routers/template.py` |
| UI | `WorkspacePage.tsx` — secção estender |
| Testes | `tests/test_template_mvp4.py` (6 testes) |

## Links

- [product/sheet-canvas.md](../product/sheet-canvas.md)
- [05-roadmap.md](../05-roadmap.md)
