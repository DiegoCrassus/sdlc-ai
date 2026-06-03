# Publish Evidence Workflow Prototype

Deterministic evidence-field projection for `INVES-72` (roadmap phase 9). Maps derived Studio pipeline outputs to the Plane evidence template field shape without posting, executing gates, or writing JSON files. Template: `.sdlc/templates/plane/evidence-template.json`. Roadmap: `docs/roadmap/sdlc-studio-mvp-roadmap.md`.

Pipeline: compile → validate → canvas → validation_inspection → publish_evidence.

CLI:

```bash
python -m studio.cli publish-evidence [--format text|json] [--root PATH] \
  [--card INVES-N] [--title TITLE] [--branch BRANCH]
```

Output: `projection` (`derived_non_authoritative`, `execution_mode=non_executing_projection`), `summary`, and `evidence_fields` matching the template top-level keys (`card`, `title`, `summary`, `problems_solved`, `technical`, `validation`, `artifacts`, `context_for_future`). All metadata cites `source_refs` only.

Non-goals: no Plane/GitHub mutation, no pytest/doctor/CI execution, no persistence, no authoritative QA or gate claims. Implementation: `studio/publish_evidence.py`.
