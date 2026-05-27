# Skill: Auto-Merge Policy

## Purpose

Definir os critérios exatos que permitem o merge automático de um PR sem intervenção humana, garantindo que a autonomia da IA só seja exercida quando todos os gates de qualidade foram atendidos.

## When to use

- Ao configurar um novo repositório
- Ao revisar se um PR está apto para auto-merge
- Como referência para o DevOps decidir se mergeia automaticamente

## Critérios para auto-merge (TODOS devem ser verdadeiros)

### Gates obrigatórios

| Gate | Check | Status necessário |
|------|-------|-----------------|
| Doctor | `make sdlc-doctor` | exit code 0 |
| Testes unitários | `pytest` ou `npm test` | 100% passando |
| Testes de integração | `pytest -m integration` | 100% passando |
| Container | `docker compose up` | todos healthy |
| Migrations | `alembic upgrade head` | sem erros |
| Security scan | `gitleaks + bandit + npm audit` | 0 HIGH/CRITICAL |
| Secrets check | `gitleaks detect` | 0 findings |
| Reviewer | Agent Reviewer decision | APPROVE |
| Doctor orphan branches | Doctor check | Sem branches órfãos |
| Branch naming | Segue branch-naming.md | Validado |

### Gates condicionais (aplicam quando relevante)

| Condição | Gate adicional |
|----------|----------------|
| PR modifica `app/frontend/` | E2E tests passando |
| PR modifica endpoints de API | ContractValidator sincronizado |
| PR modifica `app/backend/migrations/` | MigrationRunner reversível |
| PR modifica arquivos de performance crítica | Performance thresholds dentro do baseline |
| PR modifica `Dockerfile*` | Container build sem warnings de segurança |

### Critérios de BLOQUEIO (qualquer um impede auto-merge)

| Bloqueio | Motivo |
|----------|--------|
| Mudança em `app/backend/auth/` | Autenticação requer revisão humana |
| Mudança em lógica de autorização/permissões | Segurança crítica |
| Mudança em configuração de banco de produção | Risco de perda de dados |
| Mudança em variáveis de ambiente de produção | Impacto operacional |
| Security scan com CRITICAL ou HIGH | Vulnerabilidade conhecida |
| Diff > 500 linhas | Escopo muito grande para revisão autônoma confiável |
| Reviewer emitiu ESCALATE | Requer julgamento humano explícito |

## Procedimento de verificação

```python
# DevOps executa antes do merge
def pode_auto_merge(pr) -> tuple[bool, list[str]]:
    bloqueios = []

    # Gates obrigatórios
    if pr.doctor_exit_code != 0:
        bloqueios.append("Doctor falhou")
    if pr.tests_passing < pr.tests_total:
        bloqueios.append(f"Testes: {pr.tests_passing}/{pr.tests_total}")
    if pr.security_scan_level in ("CRITICAL", "HIGH"):
        bloqueios.append(f"Security: {pr.security_scan_level} encontrado")
    if pr.reviewer_decision != "APPROVE":
        bloqueios.append(f"Reviewer: {pr.reviewer_decision}")
    if pr.diff_lines > 500:
        bloqueios.append(f"Diff muito grande: {pr.diff_lines} linhas")

    # Critérios de bloqueio por área
    if any(f in pr.changed_files for f in ["auth/", "permissions/", "prod.env"]):
        bloqueios.append("Arquivo crítico alterado — requer revisão humana")

    return len(bloqueios) == 0, bloqueios
```

## Confidence Score do Reviewer (para auto-APPROVE)

O Reviewer pode emitir um APPROVE autônomo se o confidence score ≥ 0.95:

```
score = 1.0
- Doctor falhou:              score -= 0.5
- Teste falhou:               score -= 0.4
- Security HIGH:              score -= 0.6
- Security MEDIUM:            score -= 0.2
- Diff > 200 linhas:          score -= 0.1
- Diff > 500 linhas:          score -= 0.3
- Mudança em auth:            score = 0 (força escalada humana)
- ContractValidator divergiu: score -= 0.3
- Performance regrediu:       score -= 0.2

Se score < 0.95: REQUEST_CHANGES ou ESCALATE
Se score >= 0.95: APPROVE automático
```

## Validation checklist

- [ ] Todos os gates obrigatórios estão verdes
- [ ] Nenhum critério de bloqueio ativo
- [ ] Confidence score ≥ 0.95
- [ ] Card Plane em **In Progress** durante implementação
- [ ] Card Plane vinculado ao PR
- [ ] **Merge executado pelo agente** via `.sdlc/scripts/auto_merge_pr.py` — não aguardar humano

## Autonomous merge (default)

When all gates pass, **DevOps/Orchestrator MUST run**:

```bash
python3 .sdlc/scripts/auto_merge_pr.py --pr <N> --card INVES-N --plane-comment
```

Human merge in GitHub UI is **exception only** (ESCALATE, auth changes, policy block).

## Outputs

- Decisão: PODE_MERGEAR ou BLOQUEADO
- Lista de bloqueios (se houver)
- Confidence score calculado
- Registro no Observer (metrics de auto-merge)
