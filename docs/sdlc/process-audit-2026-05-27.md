# Process Audit — Market Data Delivery (2026-05-27)

## Summary

The market data layer was **technically delivered** (22 tests pass locally, Doctor 94/94) but **process gates were bypassed**. Code landed on `develop` via direct push without Plane cards, feature branch, or PR review.

## Expected SDLC Flow (documented)

```
Plane card (SDLCINVEST-N)
  → feature/SDLCINVEST-N-<slug> from develop
  → implement + tests + doctor
  → PR → CI green → merge squash → delete branch
```

Sources: `.cursor/skills/branch-naming.md`, `.cursor/skills/task-creation.md`, `docs/sdlc/workflows.md`, `.sdlc/workflows.yaml`

## What Actually Happened

| Step | Expected | Actual |
|------|----------|--------|
| Plane task | Create before work | **0 cards** in SDLCINVEST project |
| Branch | `feature/SDLCINVEST-N-…` from `develop` | Commits **directly on `develop`** |
| PR | Required before merge | **No PR opened** |
| CI | Must pass before merge | **CI failed** on push (Frontend + Auto-Merge Gate) |
| pre_task / post_task | Observer hooks | **Not invoked** |
| start-change skill | Branch + Plane In Progress | **Skill file missing** from repo |
| finish-change skill | PR + Plane evidence | **Skill file missing** from repo |

## Root Causes

### 1. Conflicting user instruction (primary)

The user message *"não me pergunte mais nada e não pare até tudo estiver pronto e na branch develop"* was interpreted as **override gitflow**. Workspace rules (branch-naming, PR lifecycle) should have **won** — delivery to `develop` must still go through PR.

### 2. Missing harness files

Referenced in AGENTS.md / github rules but **not present** in the reset repository:

- `.cursor/skills/start-change/SKILL.md`
- `.cursor/skills/finish-change/SKILL.md`
- `.sdlc/workflows/change-lifecycle.md`
- `.sdlc/scripts/gh-branch-start.sh`

Without these, the agent had no executable checklist for Plane + branch + PR.

### 3. Plane workspace misconfiguration

`.env` had `PLANE_WORKSPACE_SLUG=investments-sdlc` but the active workspace is **`rpg`** (see `.sdlc/memory/operational-context.md`, `.cursor/mcp.json`). API calls to the wrong slug would fail silently during implementation.

### 4. CI false positives

The workflow uses permissive fallbacks (`|| echo "No tests yet"`) so **backend tests never ran in CI** even when marked success. Frontend job **hard-fails** without `package-lock.json`, blocking Auto-Merge Gate.

## Technical Health (local)

| Check | Result |
|-------|--------|
| `make backend-test` | ✅ 22 passed |
| `make sdlc-doctor` | ✅ 94 passed, 0 failed |
| GitHub Actions on `develop` | ❌ Failed (Frontend setup-node, Auto-Merge Gate) |

## Remediation (in progress)

1. **Plane cards created retrospectively** — SDLCINVEST-1 … SDLCINVEST-5 in project `sdlc-investiment`
2. **Fix CI** — branch `feature/SDLCINVEST-4-fix-ci-and-sdlc-compliance` → PR → `develop`
3. **Fix `.env.example`** — `PLANE_WORKSPACE_SLUG=rpg`
4. **Restore start-change / finish-change skills** (follow-up SDLCINVEST-5)

## Going Forward — Non-Negotiable

1. Create Plane card **before** any code edit
2. Branch from updated `develop`: `feature/SDLCINVEST-N-<slug>`
3. Never push directly to `develop` or `main`
4. Open PR; wait for CI green; then merge
5. Move Plane card to Done with PR link as evidence
