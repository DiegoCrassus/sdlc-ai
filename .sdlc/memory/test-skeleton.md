# MVP Test Skeleton (INVES-75)

Traceability plan for epic **INVES-53** — derived, non-executing. Source module: `studio/mvp_test_skeleton.py`. No pass/fail results are claimed here.

## Acceptance criteria (INVES-75)

1. Each MVP phase has at least one planned validation approach.
2. Skeleton references Plane child card IDs and acceptance criteria.
3. Skeleton distinguishes automated tests, manual review, CLI checks, docs review, and doctor gate.
4. No test results are claimed before execution (`execution_claimed: false`).

## Validation types

| Type | Purpose |
|------|---------|
| `automated` | Future pytest/unit coverage on scoped card |
| `manual_review` | Human reviewer sign-off on derived outputs |
| `cli` | `python -m studio.cli` deterministic checks |
| `docs_review` | English docs and source-of-truth boundaries |
| `doctor_gate` | `make sdlc-doctor` structural gate |

## Phase entries

| Phase | ID | Cards | Types |
|-------|-----|-------|-------|
| 1 Foundation | `skeleton.phase.foundation` | INVES-54, INVES-55 | docs_review, manual_review |
| 2 Registry | `skeleton.phase.registry` | INVES-56, INVES-57 | automated |
| 3 Graph IR | `skeleton.phase.graph_ir` | INVES-58, INVES-59 | automated, docs_review |
| 4 Compiler/validator | `skeleton.phase.compiler_validator` | INVES-60–62 | automated, cli |
| 5 CLI | `skeleton.phase.cli` | INVES-63, INVES-64 | cli, automated |
| 6 Visual | `skeleton.phase.visual` | INVES-65–67 | automated, manual_review |
| 7 AI | `skeleton.phase.ai` | INVES-68, INVES-69 | automated, cli, manual_review |
| 8 Simulation | `skeleton.phase.simulation` | INVES-70, INVES-71 | automated, cli |
| 9 Publish | `skeleton.phase.publish` | INVES-72, INVES-73 | cli, docs_review |
| 10 Readiness | `skeleton.phase.readiness` | INVES-74, INVES-75 | cli, automated |

## Consolidated gates

| ID | Cards | Types |
|----|-------|-------|
| `skeleton.gate.registry_schema` | INVES-56–59 | automated |
| `skeleton.gate.compiler_validator` | INVES-61, INVES-62 | automated, cli |
| `skeleton.gate.cli` | INVES-63, INVES-64 | cli |
| `skeleton.gate.preview_simulation` | INVES-70, INVES-71 | cli, automated |
| `skeleton.gate.docs_review` | INVES-55, INVES-73 | docs_review, manual_review |
| `skeleton.gate.doctor` | INVES-74 | doctor_gate |

## Pytest stubs

Skipped placeholders live in `studio/test_mvp_skeleton.py` (`test_mvp_skeleton_future_validation`). Executable meta-tests verify skeleton shape only.

## CLI

```bash
python -m studio.cli list-skeleton [--format text|json]
```
