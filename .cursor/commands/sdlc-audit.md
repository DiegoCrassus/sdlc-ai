# Command: SDLC Audit

## Purpose

Run a fully autonomous audit of the complete SDLC — structure, subagents, skills, MCP, pipeline, observability, gaps, and CI/CD — generating an interactive canvas report with autonomy scores.

## When to run

- `/sdlc-audit` — full audit
- After adding or modifying subagents, skills, or SDLC configuration
- Before a retrospective or sprint planning
- When autonomy score needs evaluation

## Required context

- Access to the full repository
- Python 3.8+ available
- `app/infra/sdlc_obs/auditor.py` present

## Execution procedure

### 1. Run the auditor

```bash
python app/infra/sdlc_obs/auditor.py
```

The script:
- Runs ~8 check categories automatically
- Generates the canvas at `~/.cursor/projects/.../canvases/sdlc-audit-report.canvas.tsx`
- Prints results to the terminal
- Returns exit code 0 (no FAILs) or 1 (FAILs present)

### 2. Interpret output

Read the output and identify:
- Autonomy Score (%)
- Health Score (%)
- Counts: PASS / WARN / FAIL
- FAIL list with recommendations

### 3. Present to the user

```markdown
## SDLC Audit Result

**Autonomy Score:** X% | **Health Score:** Y%

**Summary:** Z checks run — A PASS / B WARN / C FAIL

### Critical gaps (FAIL)
1. [category] check — recommendation
2. ...

### Warnings (WARN)
1. ...

### Next steps
1. Close highest-impact FAILs
2. Plan sprint for simulation gaps
```

### 4. Create GitHub Issues (if FAILs found)

For each FAIL in category "Simulation Gaps" or "Pipeline":
```
github.createIssue(
  title="[SDLC Gap] <check>",
  body="<detail>\n\n## Recommendation\n<recommendation>",
  labels=["sdlc-gap", "priority:high"]
)
```

### 5. Open canvas

Tell the user the generated canvas path and suggest opening it.

## Expected outputs

- Terminal with all checks printed
- Canvas `sdlc-audit-report.canvas.tsx` generated with real data
- Text summary in chat
- GitHub Issues created for critical FAILs (optional)

## Validation

- [ ] `auditor.py` ran without Python error
- [ ] Canvas generated with real data (not placeholder)
- [ ] Autonomy Score calculated correctly
- [ ] Recommendations presented in priority order (FAIL first)
- [ ] User informed about canvas path

## Failure modes

| Failure | Cause | Action |
|---------|-------|--------|
| `ModuleNotFoundError` | Incorrect Python path | Run from repository root |
| Canvas not generated | Canvases directory path not found | Auditor creates automatically; check permissions |
| Exit code 1 | FAILs found | List FAILs and recommend actions |
| `make sdlc-doctor` fails | Degraded SDLC structure | Fix with `make sdlc-doctor` first |
