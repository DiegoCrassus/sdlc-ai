# System Context

## Project Purpose

**sdlc-ai** is an AI-Native SDLC platform — a system that enables AI agents to operate across the full software development lifecycle alongside human developers.

The platform is both:
1. **A product** — providing tools for AI-native development workflows.
2. **A meta-example** — built using the same SDLC model it implements.

## Stakeholders

| Role          | Concern                                              |
|---------------|------------------------------------------------------|
| Developer     | Fast, safe, well-governed development workflow       |
| AI Agent      | Clear context, deterministic gates, safe autonomy    |
| Tech Lead     | Visibility into decisions, risks, and validation     |
| Operations    | Deployable, observable, maintainable system          |

## External Dependencies

| System   | Purpose                         | Status     |
|----------|---------------------------------|------------|
| GitHub   | Version control and PR workflow | configured |
| Plane    | Task and project management     | configured |
| OpenAI   | LLM inference                   | configured |

## System Boundaries (Current)

```
User / AI Agent
      │
      ▼
  .cursor/ (Cursor IDE agent instructions)
      │
      ▼
  .sdlc/ (SDLC configuration and DSL)
      │
      ▼
  app/ (application code — not yet implemented)
      │
      ├── frontend/ (web UI)
      ├── backend/  (API + business logic)
      ├── infra/    (infrastructure-as-code)
      └── shared/   (shared types and utilities)
```

## Constraints

- No application code exists yet — this is the initialization phase.
- Frontend framework not yet decided.
- Deployment target not yet decided.
- Authentication strategy not yet decided.

## Business Context

TBD — to be defined when product requirements are specified.
