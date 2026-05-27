# Skill: Finish Change

> **Workflow authority:** `docs/sdlc/change-lifecycle.md`

## Purpose

Finalizar uma unidade de trabalho: validar, abrir PR, **merge autônomo** em `develop`, evidência no Plane.

## When to use

- Implementação completa e testes locais passando
- Após **QA** e **Reviewer** (subagentes Task) — ver `.cursor/skills/sdlc-orchestrator/SKILL.md`

## Procedure

### 1. Validação local

```bash
make sdlc-doctor
python3 -m pytest app/backend/tests/ -v    # quando backend existir
cd app/frontend && npm run build           # quando frontend existir
```

### 2. Commit no feature branch (nunca em develop)

```bash
git add <files>
git commit -m "feat(scope): summary (INVES-N)"
```

### 3. Push e abrir PR para develop

```bash
git push -u origin HEAD
gh pr create --base develop --title "..." --body "..."
```

Sem `gh` CLI:

```bash
# GitHub REST API ou script — ver .sdlc/scripts/auto_merge_pr.py após PR criado
```

PR body must include:
- Link Plane `INVES-N`
- Test plan checklist com saídas reais
- `Closes` apenas se houver issue GitHub vinculada (Plane é primário)

### 4. Aguardar CI verde

Workflow: `.github/workflows/ci.yml`

### 5. Merge autônomo (sem aprovação humana)

**O agente DevOps/Orchestrator executa merge** quando todos os gates passam (`.cursor/skills/auto-merge-policy.md`):

```bash
python3 .sdlc/scripts/auto_merge_pr.py --pr <N> --card INVES-N --plane-comment
```

O script:
1. Aguarda CI `success` no branch do PR
2. Squash merge → `develop`
3. Remove branch remoto
4. Move card Plane → **Done** com link do PR

**Proibido** pedir ao usuário para clicar em Merge no GitHub quando gates estão verdes.

Critérios de bloqueio (escalação humana): ver `auto-merge-policy.md` — auth, diff >500 linhas, security HIGH/CRITICAL, Reviewer ESCALATE.

### 6. Plane → Done (se script não usou --plane-comment)

```bash
python3 .sdlc/scripts/plane_state.py done --card INVES-N \
  --comment "PR #N merged · pytest output attached"
```

### 7. Observer post-task

```bash
python3 .sdlc/obs/hooks/post_task.py --task "INVES-N" --status completed
```

## Delegação obrigatória antes do merge

| Subagente | Quando |
|-----------|--------|
| **QA** | Após Implementer — evidência pytest/build real |
| **Reviewer** | Após QA — checklist code-review + auto-merge-policy |
| **DevOps** | Executar `auto_merge_pr.py` — não delegar merge ao humano |

## Failure modes

| Situation | Action |
|-----------|--------|
| CI falhou | Corrigir no branch; novo push; **não** merge |
| Merge bloqueado por policy | Escalar humano; documentar no Plane |
| Usuário pede merge manual | Explicar que finish-change é autônomo por design |
