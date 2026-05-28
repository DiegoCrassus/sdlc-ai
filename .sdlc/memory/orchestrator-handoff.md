# Orchestrator Handoff (latest)

```yaml
intent: SDLC_META
confidence: 0.97
card: INVES-29
branch: sdlc/INVES-29-agents-manifest-pipeline
next_agent: implementer
stage: sdlc_meta
greenfield_signals: []
scope_hint: >
  Batch of uncommitted SDLC-meta changes: migrate .cursor/subagents/ →
  .cursor/agents/ (Cursor agent format, 16 files), add post-tool validation
  hook, new manifest.yaml, pipeline.yaml, session-gate schema, memory
  utilities, meta-tool scripts, and updates to governance rules, doctor,
  gate, AGENTS.md, and Makefile. Delete deprecated files. No app/ touch.
requires_plane: true
requires_branch: true
autonomous: true
branch_prefix: sdlc/
plane_issue_uuid: acdcc4ce-4b9a-4888-b7fa-c435303bd14f
rationale: |
  Planner created INVES-29 for this well-scoped batch of SDLC-meta changes
  exclusively within .cursor/ and .sdlc/ (agents, hooks, manifest, pipeline,
  session-gate schema, memory scripts, governance rules, doctor, gate configs,
  AGENTS.md, Makefile). No app/ files are touched. The architect must confirm
  .cursor/agents/ format compatibility and doctor.yaml path check alignment
  before the implementer begins on branch sdlc/INVES-29-agents-manifest-pipeline.
legacy_docs: []
```
