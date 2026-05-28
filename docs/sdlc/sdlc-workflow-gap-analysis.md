# SDLC AI-Native — Critical Workflow Gap Analysis

> **Date:** 2026-05-27  
> **Context:** SDLC workflow failure in the MarketPulse greenfield session (financial/crypto app request)  
> **References:** `docs/references/` (6 papers) + current repository state  
> **Next step:** plan tracking and aggressive improvement of the SDLC system

---

## 1. Executive summary

The `sdlc-ai` repository has **rich documentation, subagents, skills, Plane/GitHub scripts, and observability** — which explains the 99% Autonomy Score in the Doctor. However, that score measures **structural presence**, not **behavioral adherence of the agent at runtime**.

In the MarketPulse session, the agent:

1. Read `AGENTS.md` (root) and `change-lifecycle.md`, but **collapsed the entire pipeline into a single turn**.
2. Interpreted *"sem interrupções"* as **license to skip gates**, not as *autonomy within the workflow*.
3. Created a Plane card (INVES-25) with minimal description, **without going through the plane-task-creation gate**.
4. Skipped **Orchestrator → Planner → Architect → QA → Reviewer** and went straight to `Write` in `app/`.
5. Reused legacy docs (`investment-radar-api.md`) despite the explicit greenfield request.
6. Card INVES-25 was later **not found** by `plane_state.py` — evidence of broken traceability.

**Diagnosis:** we have an SDLC that is **specified**, not **enforced**. Rules exist as text; enforcement mechanisms are weak or absent.

---

## 2. What happened vs what should have happened

### Expected sequence (change-lifecycle.md + Orchestrator)

| # | Stage | Agent / Skill | Required evidence |
|---|-------|---------------|-------------------|
| 0 | Classify request | Orchestrator | greenfield → plane-task-creation |
| 1 | Create epic + sub-tasks | Planner + plane-sdlc | Plane card with complete HTML plan |
| 2 | Refine requirements | Planner | Measurable AC, non-goals, risks |
| 3 | Architecture | Architect | ADR / API contract before code |
| 4 | start-change | Orchestrator | `plane_state.py in-progress` + branch |
| 5 | Implementation | Implementer (delegated Task) | Commits on feature branch |
| 6 | Validation | QA (delegated Task) | Real pytest/build |
| 7 | Review | Reviewer (delegated Task) | APPROVE + auto-merge-policy |
| 8 | Merge | DevOps | `auto_merge_pr.py` + green CI |
| 9 | Done | Plane | Structured evidence on card |

### Actual sequence (MarketPulse session)

| # | What the agent did | Violation |
|---|-------------------|-----------|
| 1 | WebSearch APIs + Glob repo | OK (discovery) |
| 2 | Read AGENTS.md + change-lifecycle (partial) | OK |
| 3 | Read `investment-radar-api.md` (legacy) | Contradicts "from scratch" |
| 4 | Created INVES-25 via ad hoc POST | Without plane-task-creation |
| 5 | `plane_state in-progress` + branch | Partial — card possibly invalid |
| 6 | Massive `Write` backend + frontend | **Total bypass of Orchestrator/delegation** |
| 7 | No Task(QA), Task(Reviewer), PR, merge | Truncated pipeline |

### Identified bypass trigger

The user said: *"sem interrupções"*. The agent treated it as:

> "Don't stop to ask questions; implement everything at once."

When it should have meant:

> "Execute the full pipeline autonomously, without asking the human to merge — but **respecting every gate**."

**Rule gap:** there is no explicit instruction that resolves the conflict between user urgency/autonomy and SDLC anti-bypass.

---

## 3. Strengths of the current structure

### 3.1 Documented governance

| Area | Artifact | Strength |
|------|----------|----------|
| Source of truth | `docs/sdlc/change-lifecycle.md` | Clear hierarchy: prevails over ad hoc chat |
| Stages | `.sdlc/stages.yaml` + `gates.md` | Evidence defined per transition |
| Roles | 15 subagents in `.cursor/subagents/` | Specialization aligned with V-Bounce (validation > implementation) |
| Operational skills | start-change, finish-change, plane-sdlc | Concrete procedures with scripts |
| Machine-readable | `.sdlc/workflows.yaml`, `lifecycle.yaml` | Foundation for future automation |

### 3.2 Real integrations

- **Plane REST:** `plane_state.py`, `plane_card.py`, `auto_merge_pr.py`
- **GitHub:** issue triage, CI with Doctor + gitleaks
- **Observability:** SQLite collector, sessionStart/stop hooks

### 3.3 Anti-patterns already prohibited (on paper)

- No local `specs/`
- No file-based backlog
- No direct push to develop/main
- Plane as primary tracker

### 3.4 Alignment with literature (potential)

The architecture **already points** to the right model — what is missing is **enforcement middleware** (ALTK, Spec Kit Agents, Claude Code hooks).

---

## 4. Critical gaps (with severity)

| ID | Gap | Severity | Evidence in repo |
|----|-----|----------|------------------|
| G1 | **Orchestrator is not enforced** — main agent implements `app/` directly | CRITICAL | Skill exists; rule `002-sdlc-orchestrator-principal.mdc` referenced in AGENTS.md but **not listed in doctor.yaml** |
| G2 | **`plane-task-creation` skill missing** — referenced in start-change and orchestrator | CRITICAL | Glob returns 0 files |
| G3 | **`sdlc_gate.py` missing** — mechanical gate before editing code | CRITICAL | Referenced in start-change; file does not exist |
| G4 | **Doctor validates structure, not workflow** | HIGH | 99% autonomy = files exist, not correct execution |
| G5 | **Naming conflict** INVES-N vs INVESTIMENTS-N | MEDIUM | sdlc-core.mdc vs gates.md vs actual branch |
| G6 | **Hooks are observability only** — no pre-write/pre-commit gate | HIGH | hooks.json: only sessionStart/stop |
| G7 | **"sem interrupções" has no resolution policy** | HIGH | Root cause of MarketPulse bypass |
| G8 | **Greenfield vs legacy ambiguous** | MEDIUM | investment-radar docs remain; agent reused them |
| G9 | **CI does not validate product** — only Doctor + secrets | MEDIUM | No pytest/build of app/ in workflow |
| G10 | **Task(QA/Reviewer) delegation is prompt opt-in** | HIGH | No mechanism prevents skip |

---

## 5. Summary of reference papers

### 5.1 AI-Native SDLC / V-Bounce (Hymel, 2408.03416)

**Thesis:** AI compresses implementation phases; **the human becomes the validator**; emphasis shifts to requirements, architecture, and continuous validation.

**Implication for us:**
- The MarketPulse agent did the opposite: maximized implementation, minimized validation.
- Proposed rule: **no `Write` in `app/` before Requirements + Architecture artifacts exist on Plane**.

### 5.2 Agentic Coding Manifests (Chatlatanagulchai et al., 2509.14744)

**Thesis:** Effective manifests are **action-oriented**, shallow (1 heading + subsections), dominated by operational commands — not long prose.

**Implication:**
- We have ~6 rules + AGENTS.md + long skills → **high cognitive load**.
- Missing a **single decision manifest** at the top: "If request = product → ALWAYS orchestrate first".
- Consolidate into **1 page gate decision tree** injected into every session.

### 5.3 Agent Workflow Optimization / Meta-tools (Abuzakuk et al., 2601.22037)

**Thesis:** Recurring tool call sequences should become **deterministic meta-tools** to reduce LLM drift.

**Implication:**
- `start-change` should be **a single command/script** (`make start-change CARD=INVES-N SLUG=...`) that:
  1. Validates card on Plane
  2. Opens mechanical gate
  3. Creates branch
  4. Emits pre_task
- Today there are 4–6 manual steps the agent can skip.

### 5.4 Spec Kit Agents (Taghavi & Bhavani, 2604.05278)

**Thesis:** Structured workflows fail due to **context blindness** — internally coherent artifacts that are incompatible with the repo.

**Implication:**
- We need **discovery hooks** (read-only) before each phase:
  - Pre-Plan: git state, open Plane cards, legacy docs
  - Pre-Arch: app/ structure, existing ADRs
  - Pre-Impl: branch + open gate + API contract
- And **validation hooks** after each phase:
  - Post-Plan: does the card have AC + non-goals?
  - Post-Impl: green pytest?

**Empirical result from the paper:** +0.15 quality, 99.7–100% test compatibility — exactly what we fail to measure.

### 5.5 Dive into Claude Code (Liu et al., 2604.14228)

**Thesis:** Mature agentic systems invest in **permission system**, **hooks**, **subagent delegation**, **compaction** — not just prompts.

**Implication:**
- Our equivalent of "permission modes" = **gate states** (closed/open per card+branch).
- Subagent delegation must be **mandatory via Orchestrator**, not a suggestion.
- Hooks must intercept **before write to protected paths**.

### 5.6 ALTK — Agent Lifecycle Toolkit (Wright et al., 2603.15473)

**Thesis:** Middleware at **6 lifecycle points**: post-request, pre-LLM, post-LLM, pre-tool, post-tool, pre-response.

**Implication — direct mapping:**

| ALTK point | Proposed SDLC equivalent |
|------------|--------------------------|
| Post-user-request | Intent classifier (product vs SDLC meta vs docs) |
| Pre-LLM | Inject gate status + active card + branch |
| Post-LLM | Validate whether next action respects current stage |
| Pre-tool (Write app/) | **Block if gate closed** |
| Post-tool | Record evidence in obs DB |
| Pre-response | Checklist: did it skip any gate? |

---

## 6. Comparison: current state vs target state

| Dimension | Today | Target |
|-----------|-------|--------|
| Enforcement | Honor system (prompts) | Mechanical gates + hooks |
| Orchestrator | Documented, ignorable | Only path to `app/` |
| Plane | Card can be created ad hoc | plane-task-creation skill + HTML template |
| Validation | Structural Doctor | Doctor + workflow compliance score |
| Tracking | Token/tool obs | **Workflow events** (gate_pass, gate_fail, bypass_attempt) |
| User urgency | Free interpretation | Explicit policy: autonomy ≠ bypass |
| Greenfield | Ambiguous with legacy | Flag on card + wipe checklist |
| CI | SDLC meta only | + app/ tests when impl gate is open |

---

## 7. Prioritized recommendations (for next phase)

### P0 — Prevent bypass (mechanical)

1. **Implement `sdlc_gate.py`** — states: `closed | open`; associates `INVES-N` + branch; persist in `.sdlc/memory/session-gate.json`.
2. **Pre-write hook** (Cursor) or script wrapper — block writes to `app/backend`, `app/frontend` if gate is closed.
3. **Create `plane-task-creation` skill** — HTML template, AC, non-goals, risks; gate before start-change.
4. **Rule `001-sdlc-anti-bypass.mdc`** — commit and include in doctor.yaml (currently referenced but absent from the list).

### P1 — Clarify sequence

5. **1-page decision tree** in root `AGENTS.md` — first thing the agent reads.
6. **"Autonomy vs bypass" policy** — fixed text: *"sem interrupções = execute the full pipeline without asking the human"*.
7. **Unify prefix** → `INVES-N` across the entire repo (fix sdlc-core.mdc).
8. **`make start-change`** single meta-tool encapsulating all steps.

### P2 — Tracking for aggressive improvement

9. **Workflow event schema** in obs DB: `{event, card, stage, agent, gate, pass/fail, timestamp}`.
10. **Workflow compliance score** in auditor — % of sessions that followed the sequence.
11. **Dashboard canvas** of bypass attempts and gate failures.
12. **End-to-end simulation** with MarketPulse scenario as SDLC regression test.

### P3 — Context grounding (Spec Kit pattern)

13. Pre-phase discovery hooks per stage.
14. Post-phase validation hooks (card completeness, tests, doctor).
15. Ablation tracking: baseline vs full-augmented workflow.

---

## 8. Proposed tracking metrics

| Metric | Definition | Initial target |
|--------|------------|----------------|
| **Workflow Compliance Rate** | Product sessions that went through Orchestrator → Plan → start-change before 1st Write | ≥ 95% |
| **Gate Bypass Attempts** | Writes blocked in app/ with gate closed | 0 merges |
| **Plane Traceability** | Referenced cards exist and passed In Progress | 100% |
| **Stage Skipping Rate** | Impl without QA or QA without Reviewer | 0% |
| **Context Blindness Index** | References to paths/APIs that do not exist in the plan | ↓ weekly |
| **Time-to-Done (autonomous)** | Card created → merge without human | baseline + trend |

---

## 9. Conclusion

The SDLC AI-Native structure of the repository is **mature in specification** and **immature in enforcement**. The 99% Autonomy Score creates a false sense of security: we measure whether files exist, not whether the agent follows them.

The MarketPulse session is a **perfect reproduction case** of the "context blindness + workflow collapse" failure mode described in Spec Kit Agents — with the additional layer of **misinterpreted urgency**.

Aggressive improvement is not about adding more documentation. It is:

1. **Less text, more mechanical gates** (action-oriented manifest + meta-tools).
2. **Orchestrator as the only entry point** for product work.
3. **Workflow event tracking** to measure and iterate.

This document serves as the foundation for the next planning round with the additional context you will provide.

---

## 10. P1 update (2026-05-27) — granularity + delegation

After greenfield retest with human interference, P1 addresses:

| Observed problem | P1 deliverable |
|------------------|----------------|
| Single `[AI][FULLSTACK]` card | `plane-granularity.yaml` + `validate-all` + rule 003 |
| Orchestrator commits/lints directly | `subagent-delegation/SKILL.md` + autonomous Implementer commits |
| Subagents only after card creation | Mandatory loop in `master-workflow.md` Step 4 + `AGENTS.md` |
| Legacy discovery in greenfield | `discovery_hook.py` → `.sdlc/memory/discovery-context.json` |
| Ad hoc QA | `qa-minimum-checklist/SKILL.md` |
| `workflow start` on epic | Block in `workflow.py` |

**Doctor:** 113 PASS · **Tests:** 9 passed (gate + granularity)

**Pending (P2/P3):** obs DB workflow events · CI pytest/build `app/` · Spec Kit validation hooks · full autonomous retest without human interference.

---

## References

| File | Title / Topic |
|------|---------------|
| `2408.03416v3.pdf` | AI-Native SDLC, V-Bounce model |
| `2509.14744v1.pdf` | Agentic Coding Manifests (Claude.md study) |
| `2601.22037v2.pdf` | Agent Workflow Optimization (meta-tools) |
| `2603.15473v2.pdf` | ALTK — lifecycle middleware |
| `2604.05278v1.pdf` | Spec Kit Agents — context grounding hooks |
| `2604.14228v1.pdf` | Claude Code design space — hooks, permissions, delegation |
