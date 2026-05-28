# SDLC i18n Normalization Audit

> **Date:** 2026-05-28  
> **Plane card:** INVES-28  
> **Policy:** SDLC operational docs in **English**; user chat responses in **Portuguese** (see `000-project-governance.mdc`).

---

## Summary

| Category | Count | Action |
|----------|-------|--------|
| SDLC agent-facing (translated this sprint) | 35+ files | Done |
| Intentional PT (user phrase examples) | 6 refs | Keep |
| Out of scope — infra/obs tools | 3 files | Backlog (optional) |
| Out of scope — product/docs legacy | varies | Not SDLC ops |

**Doctor after normalization:** 114 PASS · 0 FAIL

---

## SDLC scope — standardized to English (this delivery)

### Entry & governance
- `AGENTS.md` (root L0 manifest)
- `.sdlc/HANDBOOK.md` (renamed from `.sdlc/AGENTS.md`)
- `.cursor/rules/sdlc-core.mdc`, `000-project-governance.mdc`, `010-ai-native-sdlc.mdc`

### Process docs
- `docs/sdlc/master-workflow.md`
- `docs/sdlc/change-lifecycle.md`
- `docs/sdlc/sdlc-workflow-gap-analysis.md`

### Human guides (English for consistency)
- `SDLC-GUIDE.md`
- `SDLC-DEEP-DIVE.md`
- `SDLC-basic.txt` (already EN)

### Skills (translated)
- `start-change`, `finish-change`, `plane-sdlc`, `branch-naming`, `auto-merge-policy`
- `secrets-management`, `e2e-testing`, `iac-generation`, `container-validation`, `performance-testing`
- `sdlc-orchestrator`, `intent-classification` (mixed → EN + quoted PT examples)

### Subagents (translated)
- `devops`, `auto-fixer`, `issue-analyst`, `rollback-agent`, `sdlc-auditor`
- `security-scanner`, `contract-validator`, `migration-runner`, `observer`
- `intent-analyst` (EN + PT trigger examples for classification)

### Other
- `.cursor/commands/sdlc-audit.md`
- `.sdlc/memory/operational-context.md`
- `docs/operations/observability.md` (instrumentation section)
- `.cursor/hooks/sdlc_gate_hook.py` (deny message)

---

## Intentional Portuguese (keep)

These are **not** bugs — they support intent classification or document real user phrases:

| File | Content |
|------|---------|
| `.cursor/rules/001-sdlc-anti-bypass.mdc` | `"sem interrupções"` user phrase |
| `.cursor/skills/intent-classification/SKILL.md` | PT/EN urgency examples |
| `.cursor/subagents/intent-analyst.md` | PT greenfield trigger words |
| `.sdlc/dsl/workflow.py` | PT keywords in `classify_intent()` |
| `.sdlc/dsl/plane_granularity.py` | `"cards filhos"` breakdown marker |
| `SDLC-DEEP-DIVE.md`, gap analysis | quoted MarketPulse user input |

---

## Out of scope — remaining Portuguese (backlog)

### `app/infra/sdlc_obs/` (observability tooling — not agent instructions)

| File | Notes |
|------|-------|
| `auditor.py` | FAIL/WARN messages and gap descriptions in PT |
| `export_simulation_pdf.py` | Simulation PDF HTML template in PT |

**Recommendation:** translate in a follow-up `[AI][SDLC]` card when obs DB P2 is prioritized.

### `.sdlc/scripts/github_issue_triage.py`

- Superseded-issue comment template partially in PT  
**Recommendation:** translate comment template to EN in next infra pass.

### Product / legacy docs (not SDLC ops)

- `docs/product/*`, `docs/architecture/investment-radar-api.md` — legacy product docs  
- `docs/handoff/*`, `docs/roadmap/*` — may contain PT  
**Recommendation:** translate when product work restarts; exclude from SDLC agent context for greenfield (`discovery_hook.py` flags these).

### `docs/operations/` (partial)

- Other ops docs beyond `observability.md` may still have PT sections — audit per file when touched.

---

## Language policy (documented)

```
User chat responses     → Portuguese
SDLC docs, rules, skills, subagents, commands → English
Code comments           → English
User phrase examples in classifiers → any language (quoted)
```

Updated in:
- `.cursor/rules/000-project-governance.mdc` — Communication section
- `.cursor/rules/sdlc-core.mdc` — Language section

---

## Verification commands

```bash
make sdlc-doctor
python3 -m pytest .sdlc/dsl/test_gate.py .sdlc/dsl/test_granularity.py -q
```

---

## Next steps (optional follow-ups)

1. Translate `app/infra/sdlc_obs/auditor.py` messages to EN  
2. Translate `github_issue_triage.py` comment template  
3. Add Doctor check: warn if new `.cursor/skills/*.md` contains PT prose (excluding quoted examples)
