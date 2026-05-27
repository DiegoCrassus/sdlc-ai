# Skill: Finish Change (RPG-OP)

## Purpose

Finalizar uma unidade de trabalho: validar, abrir PR, vincular evidência no Plane, merge apenas com CI verde.

## When to use

- Implementação completa e testes locais passando
- Antes de considerar a tarefa entregue

## Procedure

### 1. Validação local

```bash
make backend-test          # ou testes equivalentes
make sdlc-doctor
```

### 2. Commit no feature branch (nunca em develop)

```bash
git add <files>
git commit -m "feat: <summary> (SDLCINVEST-N)"
```

### 3. Push e abrir PR para develop

```bash
git push -u origin HEAD
gh pr create --base develop --title "..." --body "..."
```

PR body must include:
- Link Plane `SDLCINVEST-N`
- Test plan checklist
- Closes / relates issue if applicable

### 4. Aguardar CI verde

Workflow: `.github/workflows/ci.yml`

Merge **bloqueado** se qualquer gate falhar.

### 5. Merge squash + delete branch

Após aprovação e CI green:
- Squash merge para `develop`
- Deletar branch remoto

### 6. Plane → Done

Mover card para `Done` com link do PR como evidência.

### 7. Observer post-task

```bash
python app/infra/sdlc_obs/hooks/post_task.py --task "SDLCINVEST-N" --status completed
```

## Failure modes

| Situation | Action |
|-----------|--------|
| CI falhou | Corrigir no mesmo branch; novo push; não merge |
| Push direto em develop já feito | Documentar em audit; próximas entregas via PR; hotfix CI se necessário |
| Lint falhou | Corrigir antes de pedir review |
