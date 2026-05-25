# Tests

Repository-level tests live here.

Planned layout:

```text
tests/
├── backend/
├── frontend/
├── integration/
└── e2e/
```

Guidelines:

- Put API and domain tests in `tests/backend/`.
- Put frontend behavior and component tests in `tests/frontend/`.
- Put cross-boundary tests in `tests/integration/`.
- Put user journey tests in `tests/e2e/`.
- Keep generated artifacts out of tests unless they are fixtures reviewed in the PR.
