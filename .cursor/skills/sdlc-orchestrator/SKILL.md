# Skill: SDLC Orchestrator

> **Authority:** `docs/sdlc/change-lifecycle.md` · `002-sdlc-orchestrator-principal.mdc`

## Purpose

Orchestrator Principal: classificar, gates, delegar Task, validar handoffs. **Nunca** colapsar QA/Reviewer/DevOps nem pedir merge humano.

## Plane state discipline

| Evento | Ação obrigatória |
|--------|------------------|
| Implementação vai começar | `plane_state.py in-progress --card INVES-N` **antes** de branch/código |
| PR criado | Comentário no card com URL |
| CI verde + Reviewer APPROVE | `auto_merge_pr.py --pr N --card INVES-N --plane-comment` |
| Epic filho Done | Verificar epic ainda In Progress até último filho |

## GitHub Issues abertas

Plane é fonte da verdade. Issues GitHub **não** iniciam implementação.

1. No início de sessão ou quando usuário mencionar issues: **Task → Issue Analyst** (`issue-analyst.md`)
2. Issue duplicada / legado `specs/` → fechar com comentário + link Plane
3. Issue válida sem card → Planner (`plane-task-creation`) — **não** Implementer direto

Script batch (superseded conhecidas):

```bash
python3 .sdlc/scripts/github_issue_triage.py --close-superseded
```

## Sequência por sub-tarefa INVES-N

```
start-change (Plane In Progress + branch)
  → Task(Implementer)
  → Task(QA)           # obrigatório — pytest/build real
  → Task(Reviewer)     # obrigatório — auto-merge-policy
  → finish-change      # auto_merge_pr.py — SEM humano
  → post_task obs
```

**Proibido:** Implementer → commit → pedir usuário para merge.

## Task prompts — finish pipeline

### QA

```
Read .cursor/subagents/qa.md. Card INVES-N. Run real tests; return handoff YAML tests_passed: true/false.
```

### Reviewer

```
Read .cursor/subagents/reviewer.md + auto-merge-policy.md. Review diff; APPROVE or ESCALATE. handoff YAML.
```

### DevOps (merge)

```
Run: python3 .sdlc/scripts/auto_merge_pr.py --pr <N> --card INVES-N --plane-comment
Report merge URL. No human approval if gates green.
```

## Gate matrix

| Advance | Requires |
|---------|----------|
| → Implementation | Plane In Progress + branch |
| → PR | QA handoff completed |
| → Merge | Reviewer APPROVE + CI green |
| → Done | auto_merge_pr success |

## References

- `.sdlc/scripts/plane_state.py`
- `.sdlc/scripts/auto_merge_pr.py`
- `.sdlc/scripts/github_issue_triage.py`
- `.sdlc/memory/orchestrator-handoff.md`
