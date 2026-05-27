# SDLC Workflows

## Overview

Workflows define the transitions between SDLC stages. Each workflow has:
- A source and target stage
- Preconditions that must be met
- An agent responsible for the transition
- A skill used during the transition
- Expected outputs

Full workflow definitions: `.sdlc/workflows.yaml`

## Workflow Diagram

```
Ticket
  │ Planner
  ▼
Requirements
  │ Architect (requirements_to_architecture)
  ▼
Architecture
  │ Implementer (architecture_to_implementation)
  ▼
Implementation
  │ QA (implementation_to_validation)
  ▼
Validation
  │ Reviewer (validation_to_review)
  ▼
PR & Review
  │ DevOps (review_to_deployment)
  ▼
Deployment
  │ DevOps (deployment_to_observability)
  ▼
Observability

      ↕ (when incident occurs)

Incident
  │ Implementer (incident_to_autofix)
  ▼
Auto Fix → back to Validation
```

## Key Workflow Transitions

### Requirements → Architecture

**Preconditions:**
- Requirements document exists in `specs/`
- Non-goals documented
- At least 2 risks identified

**Agent:** Architect
**Skill:** architecture-analysis

### Architecture → Implementation

**Preconditions:**
- Trade-offs documented
- Impacted areas listed
- ADR written if applicable

**Agent:** Implementer
**Skill:** implementation

### Implementation → Validation

**Preconditions:**
- Tests exist for new logic
- Diff is focused (no scope creep)
- Docs updated if needed

**Agent:** QA
**Skill:** qa-validation

### Validation → PR & Review

**Preconditions:**
- All tests pass (real results)
- Each acceptance criterion verified

**Agent:** Reviewer
**Skill:** code-review

### Incident → Auto Fix

**Preconditions:**
- Incident documented
- Root cause identified

**Agent:** Implementer
**Skill:** implementation
**Note:** Human review required before merge.

## Skipping Stages

Stages may only be skipped with an explicit, documented reason.
Acceptable reasons:
- Trivial change (typo fix, comment update) — skip architecture and validation, note it explicitly
- Emergency rollback — skip forward; document post-hoc

Never skip validation by claiming tests pass without running them.
