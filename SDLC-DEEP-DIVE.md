# SDLC Deep Dive — Papers, P0/P1, and Real Behavior

> **Audience:** a **digestible** read when [`SDLC-GUIDE.md`](SDLC-GUIDE.md) still leaves questions unanswered.  
> **Goal:** connect each idea from the 6 papers in `docs/references/` to what was **actually built**, how it **behaves** in practice, and what **does not exist yet**.  
> **Version:** P0 + P1 · 2026-05-27

---

## Table of Contents

1. [The problem the papers describe](#1-the-problem-the-papers-describe)
2. [The 6 papers — human translation](#2-the-6-papers--human-translation)
3. [Paper → implementation → behavior](#3-paper--implementation--behavior)
4. [ALTK map — the 6 interception points](#4-altk-map--the-6-interception-points)
5. [Anatomy of each P0/P1 mechanism](#5-anatomy-of-each-p0p1-mechanism)
6. [Full walkthrough: MarketPulse corrected](#6-full-walkthrough-marketpulse-corrected)
7. [Comparison: before vs after (MarketPulse)](#7-comparison-before-vs-after-marketpulse)
8. [Quick matrix: paper → file → command](#8-quick-matrix-paper--file--command)
9. [FAQ — frequently asked questions](#9-faq--frequently-asked-questions)
10. [P2/P3 roadmap (papers not yet fully applied)](#10-p2p3-roadmap-papers-not-yet-fully-applied)

---

## 1. The problem the papers describe

### 1.1 What we had before P0/P1

The repository had **lots of documentation** and **lots of subagents** — the Doctor reached ~99% Autonomy Score. That score answers:

> *"Do the right files exist?"*

It **does not** answer:

> *"Did the agent follow the workflow in a real session?"*

### 1.2 What happened in the MarketPulse retest

You asked for a **greenfield** finance/crypto app and requested autonomy (*"sem interrupções"* — Portuguese for "without interruptions," meaning full autonomous execution). The agent:

1. Read part of the SDLC ✓  
2. Interpreted urgency as **"skip everything and code"** ✗  
3. Created **a single card** `[AI][FULLSTACK]` ✗  
4. Wrote massive code in `app/` **without delegating** ✗  
5. Skipped QA, Reviewer, structured PR ✗  
6. Reused legacy docs despite "from scratch" ✗  

This is exactly the failure mode that **Spec Kit Agents** calls *context blindness + workflow collapse*, combined with the inverse of **V-Bounce** (lots of implementation, little validation).

### 1.3 The papers' answer (one-sentence synthesis each)

| Paper | One sentence |
|-------|--------------|
| **V-Bounce** | With AI, implementation is cheap; **validation** becomes the bottleneck — human/validator agent before merge. |
| **Manifests** | Long instructions don't work; **short decision tree + commands** work. |
| **Meta-tools (AWO)** | Repeated sequences (start branch, open gate…) should become a **single script**, not 6 steps the LLM can skip. |
| **Spec Kit Agents** | Before each phase: **discovery** (what exists in the repo?); after: **validation** (does the plan/code match reality?). |
| **Claude Code** | Mature systems use **permissions, hooks, and subagents** — not just prompts. |
| **ALTK** | Middleware at **6 moments** in the agent lifecycle — not just "system prompt". |

**P0 + P1** implement the essence of these ideas in `sdlc-ai`. **P2/P3** still close gaps (tracking, product CI, full validation hooks).

---

## 2. The 6 papers — human translation

### 2.1 V-Bounce / AI-Native SDLC (`2408.03416v3.pdf`)

**Core idea:** The traditional SDLC model assumes implementation is expensive. With LLMs, implementation is **fast and cheap**; requirements, architecture, and **validation** gain weight. The "V" is: go down (refine) before coding, go up (validate) before merge.

**Analogy:** Before, the bricklayer took a long time — today the wall goes up in minutes. The risk is not "not building"; it is **building wrong fast**.

**In our workflow:**
- **Down:** Intent → Planner → Architect → plan in Plane  
- **Up:** QA → Reviewer → CI → merge  

**Derived rule:** no `Write` in `app/` before requirements + architecture are recorded in Plane and the gate is open.

---

### 2.2 Agentic Coding Manifests (`2509.14744v1.pdf`)

**Core idea:** They studied hundreds of `CLAUDE.md` / manifests. The ones that **work** are:
- Short (1 decision page)
- **Action-oriented** ("if X → do Y")
- Full of **concrete commands**, not philosophical prose

**In our workflow:**
- **`AGENTS.md` at the root** = L0 manifest (decision tree)
- **Rules 001/002/003** = alwaysApply, short
- **`SDLC-GUIDE.md`** = long prose for **humans** — does not replace the agent manifest

**Common mistake:** thinking more documentation = more compliance. The paper says the opposite for the agent: **less decision text, more mechanism**.

---

### 2.3 Agent Workflow Optimization / Meta-tools (`2601.22037v2.pdf`)

**Core idea:** LLMs **drift** when they repeat the same tool sequence manually. Packaging sequences into **deterministic meta-tools** (scripts/CLI) reduces error.

**Old example (drift):**
```
1. validate plan
2. plane in-progress
3. create branch
4. open gate
5. pre_task obs
→ agent does 2 of 5 and codes
```

**Current meta-tool:**
```bash
python3 .sdlc/dsl/cli.py workflow start --card INVES-26 --slug backend-api
```
One command does: validate (if impl) + Plane In Progress + `session-gate.json` open.

**Workflow subcommands:** `classify`, `plan`, `discover`, `start`, `implement`, `validate`, `review`, `finish`, `status`.

---

### 2.4 Spec Kit Agents (`2604.05278v1.pdf`)

**Core idea:** Structured workflows fail when the agent produces artifacts that are **internally coherent** but **incompatible with the real repository** (*context blindness*).

**MarketPulse example:** plan says "greenfield", agent reads `investment-radar-api.md` and copies old architecture.

**Paper's solution:** **read-only** hooks before each phase (discovery) and **validation** hooks after.

**What we implemented (P1):**
- **Pre-Plan discovery:** `discovery_hook.py` → `discovery-context.json`
- **Post-Plan validation:** `validate-all` / `validate-plan` in `plane_card.py`
- **Post-Impl validation (partial):** `qa-minimum-checklist` — pytest/doctor when QA runs

**What's missing (P3):** automatic post-phase validation hooks wired to the obs DB.

---

### 2.5 Dive into Claude Code (`2604.14228v1.pdf`)

**Core idea:** Analysis of the coding agent design space. Mature systems combine:

| Mechanism | Function |
|-----------|----------|
| **Permission modes** | What can be touched at each moment |
| **Hooks** | Intercept tool calls before/after |
| **Subagent delegation** | Specialized role, isolated context |
| **Compaction** | Summarize context without losing state |

**Our equivalent:**

| Claude Code | sdlc-ai |
|-------------|---------|
| Permission modes | **Gate stages** (`planning`, `implementation`, `sdlc_meta`…) |
| preToolUse hook | `sdlc_gate_hook.py` on Write |
| Subagents | `.cursor/subagents/*.md` via `Task(...)` |
| Compaction | handoff YAML + `session-gate.json` (state outside chat) |

**Critical P1:** delegation is not a suggestion — rule **003** forbids the Orchestrator from committing/linting/implementing.

---

### 2.6 ALTK — Agent Lifecycle Toolkit (`2603.15473v2.pdf`)

**Core idea:** Middleware at **6 points** between user and final response — don't rely only on the initial prompt.

See [section 4](#4-altk-map--the-6-interception-points) for the full point-by-point mapping.

---

## 3. Paper → implementation → behavior

This table is the main **mental map**:

| Paper | Gap we address | P0/P1 artifact | Runtime behavior |
|-------|----------------|----------------|------------------|
| V-Bounce | Impl before validation/plan | `gate-paths.yaml`, Write hook | Write in `app/` **blocked** without gate |
| Manifests | Prompts ignored | `AGENTS.md`, rules 001–003 | alwaysApply in every chat |
| AWO | Drift in sequences | `cli.py workflow *` | One command = several atomic steps |
| Spec Kit | Context blindness | `discovery_hook.py`, `validate-all` | Lists legacy; blocks incomplete plan |
| Claude Code | No permissions/delegation | hook + `subagent-delegation` | Orchestrator only spawns Tasks |
| ALTK | No middleware | gate + classify + handoff | State outside LLM (`session-gate.json`) |

---

## 4. ALTK map — the 6 interception points

ALTK defines **where** to inject control. Below: each point, what it means, what we have today, concrete example.

```
User → [1 post-request] → LLM → [2 pre-LLM] → LLM thinks → [3 post-LLM]
    → tool call → [4 pre-tool] → executes → [5 post-tool] → [6 pre-response] → User
```

### Point 1 — Post-user-request (classify intent)

| | |
|---|---|
| **What it is** | As soon as a message arrives, before any action |
| **Implementation** | `Task(Intent Analyst)` + `workflow classify --text "..."` |
| **Files** | `intent-analyst.md`, `intent-classification/SKILL.md`, `workflow.py::classify_intent` |
| **Output** | YAML in `orchestrator-handoff.md` + `session-gate.json` intent |

**Behavior:**  
Message *"Create MarketPulse from scratch"* + `app/` placeholder → `intent: GREENFIELD`, `next_agent: planner`.

**Exception:** if `session-gate.json` already has `gate_status: open` → **do not re-classify**; continue current stage (rule 002).

---

### Point 2 — Pre-LLM (inject state context)

| | |
|---|---|
| **What it is** | Before the model decides the next action, load objective state |
| **Partial implementation** | alwaysApply rules + `workflow status` |
| **Files** | `session-gate.json`, `orchestrator-handoff.md`, `discovery-context.json` |
| **P2 gap** | Automatic injection into context without the agent needing to "remember" to run status |

**Behavior today:**  
Orchestrator **must** run `make workflow-status` when uncertain. Shows:

```
gate_status: open
card: INVES-26
branch: feature/INVES-26-backend-api
stage: implementation
```

---

### Point 3 — Post-LLM (validate next action intent)

| | |
|---|---|
| **What it is** | Model said "I'll Write in app/" — is that allowed in the current stage? |
| **Partial implementation** | Rules 001/003 + subagent-delegation skill |
| **Behavior** | Agent **should** spawn Task(Implementer) instead of direct Write |
| **Gap** | Depends on LLM obedience — reinforced by pre-tool hook |

**Why the hook still matters:** the LLM can ignore rules; the hook **does not ignore**.

---

### Point 4 — Pre-tool (block Write)

| | |
|---|---|
| **What it is** | Intercept **before** the Write tool executes |
| **P0 implementation** | `.cursor/hooks/sdlc_gate_hook.py` + `hooks.json` matcher `Write` |
| **Logic** | Calls `gate.check_write(path)` |

**Detailed hook flow:**

```
1. Cursor is about to execute Write(path="app/backend/main.py")
2. hooks.json triggers sdlc_gate_hook.py with JSON payload
3. Hook extracts path from payload
4. gate.check_write():
   a. Is path in protected_prefixes? (app/backend/, app/frontend/, app/shared/, pyproject.toml)
      → NO: allow
   b. session-gate.json gate_status == "open"?
      → NO: DENY + message "run workflow start"
   c. Does current stage allow this path? (implementation allows app/)
      → NO: DENY
   d. YES: allow
5. Hook prints JSON {"permission": "deny"|"allow"} to Cursor
```

**Message to agent when blocked:** includes exact auto-fix command (`workflow start --card ... --stage implementation`).

**Important:** `failClosed: false` in hooks.json — if hook crashes, Write passes. P2 may revisit this.

---

### Point 5 — Post-tool (record evidence)

| | |
|---|---|
| **What it is** | After tool executes, record what happened |
| **Partial implementation** | `pre_task.py` / `post_task.py` (obs), handoff YAML |
| **P2 gap** | `gate_pass`, `gate_fail`, `bypass_attempt` events in obs DB |

**Behavior today:**  
Implementer puts `commits: [hash]` in handoff. QA puts `pytest_summary`. Plane receives comments via manual milestones/scripts.

---

### Point 6 — Pre-response (checklist before responding to user)

| | |
|---|---|
| **What it is** | Before "ending turn", verify whether gate was skipped |
| **Partial implementation** | Orchestrator skill + master-workflow loop |
| **Gap** | No automatic "stop" hook that validates complete pipeline |

**Expected behavior:**  
Orchestrator reads handoff → if `stage_complete: false`, spawn same agent or AutoFixer → if `next_agent: qa`, Task(QA) — **never** "I'll run pytest here".

---

## 5. Anatomy of each P0/P1 mechanism

### 5.1 Session Gate — the "permission mode"

**State file:** `.sdlc/memory/session-gate.json`

Example with gate **open** for implementation:

```json
{
  "gate_status": "open",
  "card": "INVES-26",
  "branch": "feature/INVES-26-backend-api",
  "stage": "implementation",
  "intent": "GREENFIELD",
  "opened_at": "2026-05-27T14:30:00+00:00",
  "meta": {}
}
```

Example with gate **closed** (default state / after finish):

```json
{
  "gate_status": "closed",
  "card": "",
  "branch": "",
  "stage": "",
  "intent": "",
  "opened_at": "",
  "meta": {}
}
```

**Who opens:** `workflow start` → `gate.open_gate()`  
**Who closes:** `workflow finish` → `gate.close_gate()`

**Stages and allowed paths** (`.sdlc/gate-paths.yaml`):

| Stage | Can write to |
|-------|--------------|
| `planning` | `.sdlc/`, `.cursor/`, `docs/sdlc/` |
| `architecture` | same as planning |
| `implementation` | `app/backend/`, `app/frontend/`, `app/shared/`, `pyproject.toml` |
| `sdlc_meta` | `.sdlc/`, `.cursor/`, `docs/sdlc/`, `.github/`, `Makefile`, `AGENTS.md` |
| `validation` | `app/`, templates |
| `review` | templates, docs |

**Common question:** *"Can I edit `.sdlc/` without a gate?"*  
→ Yes, paths in `app/` are the main protected ones; meta-SDLC uses stage `sdlc_meta` via `workflow start --stage sdlc_meta`.

---

### 5.2 CLI `workflow start` — complete meta-tool

When you run:

```bash
python3 .sdlc/dsl/cli.py workflow start --card INVES-26 --slug backend-api --stage implementation
```

**Internal sequence:**

1. **Block epic:** query Plane API; if title contains `[AI][EPIC]` → exit 1  
2. **Plane In Progress:** `plane_state.py in-progress --card INVES-26 --branch feature/INVES-26-backend-api`  
3. **Validate plan:** `plane_card.py validate-all --card INVES-26` (skip if `--skip-validate` or `--force`)  
4. **Open gate:** write `session-gate.json`  
5. Print `OK: workflow start — INVES-26 branch=... stage=implementation`

**Useful flags:**

| Flag | Effect |
|------|--------|
| `--force` | Opens gate even if Plane/validate fails (escape hatch — avoid in product work) |
| `--skip-plane` | Does not call Plane API |
| `--skip-validate` | Does not validate plan |
| `--stage sdlc_meta` | For work in `.sdlc/` / `.cursor/` |

---

### 5.3 Plane granularity — why epic + children

**Config:** `.sdlc/plane-granularity.yaml`  
**Validator:** `.sdlc/dsl/plane_granularity.py`  
**CLI:** `plane_card.py validate-all --card INVES-N`

**GREENFIELD rules:**

- Epic title must have `[AI][EPIC]`
- Single `[AI][FULLSTACK]` card forbidden
- Task Breakdown with ≥3 children or refs `INVES-27`, `INVES-28`…
- Layers: BACKEND + FRONTEND + (INFRA or SHARED)
- "Task Breakdown" / "child cards" section in HTML description

**Why this came from the retest:** monolithic card prevents parallelism, tracking, and focused QA. AWO + V-Bounce paper: **small tasks with validation between them**.

**Epic vs child:**

| | Epic INVES-25 | Child INVES-26 |
|---|---------------|----------------|
| `workflow start` | **Forbidden** | **Required** before coding |
| Branch | No | `feature/INVES-26-...` |
| Merge | Not directly | Own PR |
| Done | When all children Done | After child merge |

---

### 5.4 Delegation — Orchestrator vs subagents

**Skill:** `.cursor/skills/subagent-delegation/SKILL.md`  
**Rule:** `.cursor/rules/003-orchestrator-delegation-only.mdc`

**Simplified matrix:**

| Action | Who executes |
|------|--------------|
| Classify | Task(Intent Analyst) |
| Create Plane cards | Task(Planner) via MCP |
| Architecture notes | Task(Architect) |
| Code + commit | Task(Implementer) |
| pytest, ruff, doctor | Task(QA) |
| Fix failures | Task(AutoFixer), max 2× |
| APPROVE/ESCALATE | Task(Reviewer) |
| push, PR, merge | Task(DevOps) + `workflow finish` |
| `workflow status`, `validate-all` | Orchestrator (scripts OK) |

**Handoff YAML** (`.sdlc/memory/orchestrator-handoff.md`):

```yaml
agent: implementer
card: INVES-26
stage_complete: true
next_agent: qa
commits: ["a1b2c3d"]
branch: feature/INVES-26-backend-api
blockers: []
```

Orchestrator **reads** → spawns Task(QA). **Does not** run pytest "just this once".

---

### 5.5 Autonomy vs bypass (policy 001)

**Official phrase:**

> *"Sem interrupções"* (Portuguese user phrase meaning "without interruptions") = full pipeline, zero questions to the human for commit/merge — **does not** mean skip gates.

| User request | Correct behavior |
|--------------|------------------|
| "Do it without asking me anything" | Implementer commits, DevOps pushes, autonomous merge |
| "Do it fast, all at once" | Epic + children + sequential Tasks — **not** monolithic Write |
| "Urgent, skip documentation" | Minimum valid Plane (validate-all) still required |

**Human escalation only when:** AutoFixer exhausted 2 cycles, Reviewer ESCALATE, Plane/GitHub API down.

---

### 5.6 Discovery hook (Spec Kit — pre-plan)

```bash
make workflow-discover
```

**Output** `.sdlc/memory/discovery-context.json`:

```json
{
  "app_placeholder": true,
  "legacy_docs": [
    {"path": "docs/architecture/investment-radar-api.md", "reason": "legacy product/architecture doc"}
  ],
  "greenfield_hint": true,
  "recommendation": "ignore legacy_docs for GREENFIELD"
}
```

**Expected Planner/Orchestrator behavior:**  
GREENFIELD + recommendation ignore → **do not** base architecture on `investment-radar-api.md`.

---

### 5.7 QA minimum checklist (V-Bounce — validation)

**Skill:** `.cursor/skills/qa-minimum-checklist/SKILL.md`

QA **always** runs (via Task, autonomously):

1. `make sdlc-doctor`  
2. `pytest .sdlc/dsl/` if SDLC touched  
3. `pytest app/` if backend changed  
4. `ruff check` on changed paths  
5. `npm run build` if frontend changed  
6. `validate-all` if Plane description changed  
7. Map each AC from the child card  

**AutoFixer loop:** QA fail → Task(AutoFixer) → commit fix → Task(QA) again → max 2× → human.

---

## 6. Full walkthrough: MarketPulse corrected

Scenario: *"Create MarketPulse, finance/crypto app, from scratch, sem interrupções."* (The last phrase is the Portuguese autonomy request meaning "without interruptions.")

### Phase A — Entry (ALTK point 1)

```
User → Orchestrator
Orchestrator → Task(Intent Analyst)
Intent: GREENFIELD, next_agent: planner
Orchestrator → Task(Planner)  [does NOT write app/]
```

### Phase B — Plane granularity (AWO + Spec Kit)

Planner via Plane MCP creates:

```
INVES-30 [AI][EPIC] MarketPulse delivery
INVES-31 [AI][BACKEND] Market API mock/live
INVES-32 [AI][FRONTEND] Dashboard + watchlist
INVES-33 [AI][INFRA] Docker compose local stack
```

```bash
python3 .sdlc/scripts/plane_card.py validate-all --card INVES-30
# exit 0 required
make workflow-discover
# legacy docs listed → ignore for greenfield
```

### Phase C — Architecture

```
Task(Architect) → HTML notes on epic INVES-30 in Plane
(No local ADR needed — plane_only decision)
```

### Phase D — Child 1: backend (Claude Code delegation + gate)

```bash
python3 .sdlc/dsl/cli.py workflow start --card INVES-31 --slug market-api
# → gate open, branch feature/INVES-31-market-api, Plane In Progress
```

```
Task(Implementer):
  - Write app/backend/...  [hook ALLOW — gate open, stage implementation]
  - git commit -m "[INVES-31] Add market API scaffold."
  - handoff: next_agent: qa, commits: [...]

Task(QA):
  - pytest, ruff, doctor
  - handoff: next_agent: reviewer

Task(Reviewer):
  - APPROVE

Task(DevOps):
  - git push -u origin HEAD
  - gh pr create ...

python3 .sdlc/dsl/cli.py workflow finish --pr 45 --card INVES-31
# → autonomous merge, gate closed, card Done
```

### Phase E — Children 2 and 3

Repeat cycle for INVES-32 (frontend) and INVES-33 (infra).

### Phase F — Epic Done

When INVES-31, 32, 33 Done → mark INVES-30 Done in Plane.

**Human time:** ideally **zero** until merge — except ESCALATE.

---

## 7. Comparison: before vs after (MarketPulse)

| Stage | Before (failure) | After (P0+P1) |
|-------|------------------|---------------|
| Classification | Implicit / skipped | Intent Analyst + classify |
| Plane | 1× FULLSTACK | Epic + 3 children |
| Discovery | Read legacy and copied | discover → ignore |
| Gate | Nonexistent | hook blocks Write |
| Implementation | Orchestrator direct Write | Task(Implementer) |
| Commit | Asked human | Implementer autonomous |
| QA/Review | Skipped | Task(QA) → Task(Reviewer) |
| Merge | Manual / absent | DevOps + workflow finish |
| Epic start | workflow on wrong card | start only on children |

---

## 8. Quick matrix: paper → file → command

| Paper | Main file | Command to test |
|-------|-----------|-----------------|
| V-Bounce | `qa-minimum-checklist/SKILL.md` | Task(QA) runs checklist |
| Manifests | `AGENTS.md`, `001-*.mdc` | Open new chat — rules loaded |
| AWO | `.sdlc/dsl/workflow.py` | `make workflow-start CARD=...` |
| Spec Kit | `discovery_hook.py`, `plane_card.py` | `make workflow-discover` / `validate-all` |
| Claude Code | `sdlc_gate_hook.py`, `003-*.mdc` | Try Write app/ with gate closed |
| ALTK | `gate.py`, `session-gate.json` | `make workflow-status` |

**Automated tests:**

```bash
pytest .sdlc/dsl/test_gate.py .sdlc/dsl/test_granularity.py -q
make sdlc-doctor
```

---

## 9. FAQ — frequently asked questions

### General

**Q: Why `AGENTS.md` at the root and `.sdlc/HANDBOOK.md`?**  
A: Root = L0 manifest (1 page, alwaysApply via rules). `.sdlc/HANDBOOK.md` = full catalog (tables, MCP, history). Agent reads root first.

**Q: What's the difference between `change-lifecycle.md` and `master-workflow.md`?**  
A: `change-lifecycle` = gitflow + Plane + merge (legal authority). `master-workflow` = detailed agentic process (Steps 0–8). Complementary; anti-bypass prevails over chat.

**Q: Where is the subagent handbook?**  
A: `.sdlc/HANDBOOK.md` — do not confuse with `AGENTS.md` at the root (L0 manifest).

**Q: Does Doctor 113 PASS mean the workflow works?**  
A: **No.** It means the **infrastructure** is correct. Runtime compliance = greenfield retest + P2 metrics.

---

### Gates and hooks

**Q: Does the hook block StrReplace or only Write?**  
A: Configured for matcher **`Write`** in `hooks.json`. StrReplace may not go through the same hook — known risk; P2 may extend matcher.

**Q: Gate closed — can I edit README at the root?**  
A: Yes, if path is not in `protected_prefixes` (`app/backend/`, `app/frontend/`, `app/shared/`, `pyproject.toml`).

**Q: `--force` on workflow start — when to use?**  
A: Debug only or Plane API offline. In normal product work, **never** — masks invalid plan.

**Q: Plane and gate — which wins?**  
A: **Plane** = business truth (card, Done, evidence). **session-gate.json** = mechanical cache for hook/CLI. They should align; `workflow start` syncs both.

---

### Plane and granularity

**Q: Can I use a single card for a small bugfix?**  
A: **Yes.** `plane-granularity.yaml` allows single card for BUGFIX, HOTFIX, SDLC_META, etc.

**Q: Does the epic need children created in Plane or is listing in the breakdown enough?**  
A: Validator counts **child_count** (parent links in Plane) **or** refs `INVES-N` in HTML breakdown. Ideal: **real** children in Plane with parent link.

**Q: Why does `[AI][FULLSTACK]` exist if it's forbidden?**  
A: Legacy tag for genuinely cross-layer changes **already decomposed** into children. Never as the **only** greenfield card.

---

### Delegation and autonomy

**Q: Can the Orchestrator run `make sdlc-doctor`?**  
A: **Yes** — scripts/meta-tools are allowed. Cannot run pytest/ruff **for product** instead of QA.

**Q: Who does git commit?**  
A: **Implementer** (and AutoFixer for fixes). Orchestrator **never**. DevOps does push/PR.

**Q: What if I want to approve the PR manually?**  
A: Contradicts current autonomy policy. Reviewer agent APPROVE + green CI → autonomous merge. Human enters via ESCALATE.

**Q: Subagent = Cursor Task tool?**  
A: Yes. Orchestrator spawns `Task(subagent_type=..., prompt=...)` with instructions from `.cursor/subagents/<name>.md`.

---

### Papers and gaps

**Q: Did we implement 100% of Spec Kit Agents?**  
A: **No.** Pre-plan discovery yes; automatic validation hooks after **each** phase = P3.

**Q: Did we implement 100% of ALTK?**  
A: **Partial.** Points 1, 4 strong; 2, 3, 5, 6 partial (depend on LLM + handoff).

**Q: What's missing for "zero doubts" at runtime?**  
A: Documented greenfield retest + P2 workflow events + CI for `app/` + extend hook to more tools.

---

### Practical scenarios

**Q: Message "explain the Doctor" — does it go through the pipeline?**  
A: **No.** Intent READONLY → Orchestrator responds directly, no Plane.

**Q: Message "improve the SDLC gate" — product or meta?**  
A: **SDLC_META.** Plane card + `workflow start --stage sdlc_meta` → can edit `.sdlc/`, `.cursor/`.

**Q: Can I work on INVES-32 while INVES-31 is still open?**  
A: Technically sequential in current design (1 gate session). New `workflow start` **overwrites** session-gate. Prefer **closing** previous child cycle before the next.

---

## 10. P2/P3 roadmap (papers not yet fully applied)

| Phase | Paper origin | Deliverable | Status |
|-------|--------------|-------------|--------|
| **P2** | ALTK post-tool + AWO metrics | Obs DB: `gate_pass`, `gate_fail`, `bypass_attempt` events | Pending |
| **P2** | V-Bounce | CI pytest/build `app/` on every product PR | Pending |
| **P2** | Manifests | Compliance score in auditor (% sessions ok) | Pending |
| **P3** | Spec Kit | Automatic validation hook post-Plan, post-Arch, post-Impl | Pending |
| **P3** | Claude Code | Hook on StrReplace/Shell for protected paths | Pending |
| **P1** | All | Greenfield retest **without human interference** | Pending validation |

---

## Recommended reading (order)

1. This document (papers + behavior)  
2. [`SDLC-GUIDE.md`](SDLC-GUIDE.md) (operational overview)  
3. [`docs/sdlc/master-workflow.md`](docs/sdlc/master-workflow.md) (approved spec)  
4. [`docs/sdlc/sdlc-workflow-gap-analysis.md`](docs/sdlc/sdlc-workflow-gap-analysis.md) (MarketPulse analysis + gaps G1–G10)  
5. PDFs in [`docs/references/`](docs/references/) (academic source)

---

*Living document — update when P2/P3 close new items in the ALTK matrix.*
