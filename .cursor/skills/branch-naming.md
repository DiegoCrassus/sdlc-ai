# Skill: Branch Naming

## Purpose

Garantir que todo branch criado no repositório tenha um nome significativo, rastreável e consistente, sempre vinculado à tarefa ou Issue de origem.

## When to use

- Antes de criar qualquer branch
- Ao revisar se um branch existente segue a convenção
- Ao sugerir nome de branch no comentário de triagem de Issue (Issue Analyst)
- Ao iniciar qualquer tarefa (Implementer)

## Regra fundamental

> **Todo branch deve referenciar o trabalho ao qual está associado.**
> Nenhum branch sem rastreabilidade para uma tarefa Plane ou Issue GitHub é permitido.

---

## Formato geral

```
<prefixo>/<referências>-<slug-descritivo>
```

### Prefixos válidos

| Prefixo | Quando usar |
|---------|-------------|
| `feature/` | Nova funcionalidade (não existia antes) |
| `bugfix/` | Correção de bug confirmado |
| `hotfix/` | Correção urgente em produção |
| `docs/` | Apenas documentação (nenhum código de produção) |
| `infra/` | Infraestrutura, ferramentas, CI/CD, observabilidade |
| `refactor/` | Refatoração sem mudança de comportamento externo |
| `sdlc/` | Mudanças em `.sdlc/`, `.cursor/`, `Makefile`, governance |
| `test/` | Apenas adição ou correção de testes |

---

## Padrões de referência

### Caso 1 — Tarefa Plane (sem Issue GitHub)

```
<prefixo>/SDLCINVEST-<N>-<slug>
```

Exemplos:
```
feature/SDLCINVEST-12-add-plane-endpoint
bugfix/SDLCINVEST-15-fix-token-count
docs/SDLCINVEST-18-update-arch-overview
infra/SDLCINVEST-21-setup-obs-server
```

### Caso 2 — Issue GitHub (sem tarefa Plane prévia)

```
<prefixo>/issue-gh-<N>-<slug>
```

Exemplos:
```
bugfix/issue-gh-42-fix-null-token-count
feature/issue-gh-58-add-plane-webhook
docs/issue-gh-63-update-local-dev-guide
```

### Caso 3 — Tarefa Plane + Issue GitHub vinculada (caso mais comum)

```
<prefixo>/SDLCINVEST-<N>-issue-gh-<N>-<slug>
```

Exemplos:
```
bugfix/SDLCINVEST-15-issue-gh-42-fix-token-count
feature/SDLCINVEST-20-issue-gh-58-add-plane-endpoint
infra/SDLCINVEST-21-issue-gh-61-add-obs-server
```

### Caso 4 — Hotfix urgente (sem tempo de criar card Plane antes)

```
hotfix/issue-gh-<N>-<slug>
```

> Criar o card Plane retrospectivamente assim que possível.

---

## Regras do slug

| Regra | Correto | Errado |
|-------|---------|--------|
| Apenas letras minúsculas | `add-endpoint` | `AddEndpoint` |
| Palavras separadas por hífen | `fix-token-count` | `fix_token_count` |
| Máximo 5 palavras | `add-plane-work-item-api` | `add-the-new-plane-work-item-api-endpoint` |
| Em inglês | `add-endpoint` | `adicionar-endpoint` |
| Imperativo (ação + objeto) | `add-endpoint`, `fix-null-check` | `endpoint`, `nullfix` |
| Sem artigos ou preposições | `add-plane-endpoint` | `add-the-plane-endpoint` |
| Sem números arbitrários | `add-endpoint` | `add-endpoint-v2` (use o ID do card) |

---

## Procedimento de criação

```bash
# 1. Confirmar ID do card Plane
#    Ex: SDLCINVEST-20

# 2. Confirmar número da Issue GitHub (se existir)
#    Ex: GH #58

# 3. Construir o nome conforme o padrão
BRANCH="feature/SDLCINVEST-20-issue-gh-58-add-plane-endpoint"

# 4. Criar a partir do develop atualizado
git checkout develop
git pull origin develop
git checkout -b "$BRANCH"

# 5. Confirmar que o branch foi criado corretamente
git branch --show-current
```

---

## Ciclo de vida do branch

```
develop (base)
   │
   └─► branch criado ────────────────────────────────────┐
       │                                                  │
       │  commits por subtarefa                          │
       │                                                  │
       └─► PR aberto (draft)                             │
           │                                             │
           │  QA + Doctor + Review                       │
           │                                             │
           ├─► PR APROVADO → squash merge → develop      │
           │   └─► branch DELETADO automaticamente        │
           │                                             │
           └─► PR FECHADO (rejeitado)                    │
               └─► branch DELETADO pelo DevOps            │
                                                          │
       NENHUM branch fica órfão ──────────────────────────┘
```

---

## Regras de deleção de branch

### Ao fazer merge (PR aprovado)

1. O PR **deve** ter `delete_branch_on_merge: true` configurado no momento da criação
2. O GitHub deleta o branch automaticamente após o squash merge
3. O DevOps confirma a deleção via `git branch -r` ou MCP `git.listBranches`

### Ao fechar sem merge (PR rejeitado)

1. O DevOps fecha o PR via `pulls.update(state: closed)`
2. Deleta o branch manualmente:
   ```bash
   git push origin --delete <branch-name>
   ```
   ou via MCP `git.deleteBranch`
3. Documenta o motivo do fechamento no PR antes de fechar

### Verificação periódica (Doctor)

O Doctor verifica se existem branches remotos sem PR associado há mais de 7 dias e emite `[WARN] Branch órfão: <nome>`.

---

## Validação checklist

- [ ] Prefixo correto para o tipo de trabalho
- [ ] Referência ao card Plane (`SDLCINVEST-N`) se existir
- [ ] Referência à Issue GitHub (`issue-gh-N`) se existir
- [ ] Slug em inglês, kebab-case, máx 5 palavras, imperativo
- [ ] Branch criado a partir do `develop` atualizado
- [ ] `delete_branch_on_merge: true` configurado no PR

---

## Failure modes

| Problema | Causa | Solução |
|----------|-------|---------|
| Branch sem prefixo | Criação manual sem ler a skill | Renomear ou recriar |
| Branch sem rastreabilidade | Issue/card não identificado | Criar card Plane, renomear branch |
| Slug muito longo | Falta de síntese | Usar apenas substantivo + verbo chave |
| Branch direto em main/develop | Falta de revisão | Reverter imediatamente, abrir PR |
| Branch órfão após PR fechado | DevOps não executou deleção | Deletar via MCP ou CLI |
