# SDLC Doctor

## What Is the Doctor?

The SDLC Doctor is a validation tool that checks the repository structure, YAML configuration, Cursor setup, documentation, and Makefile against the expected state defined in `.sdlc/doctor.yaml`.

The Doctor is the first line of defense against structural drift and configuration errors.

## Running the Doctor

```bash
make sdlc-doctor
# or directly:
python .sdlc/dsl/cli.py doctor
```

## Output Format

```
[PASS] Required directory exists: .cursor
[PASS] Required file exists: .sdlc/sdlc.yaml
[FAIL] Missing file: docs/handoff/current-state.md
[WARN] Integration not configured: github (GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC not set)

Doctor summary: 42 passed, 3 warnings, 1 failed
```

## Exit Codes

| Code | Meaning |
|------|---------|
| `0`  | All required checks passed (warnings allowed) |
| `1`  | One or more required checks failed |

## What the Doctor Checks

### 1. Required Directories

Validates that all key directories exist:
- `.cursor/` and its subdirectories
- `.sdlc/` and its subdirectories
- `docs/` and its subdirectories
- `app/` and its subdirectories

### 2. Required Files

Validates that critical files exist:
- All `.sdlc/*.yaml` files
- `.sdlc/dsl/cli.py` and `.sdlc/dsl/doctor.py`
- `Makefile` and `README.md`

### 3. Cursor Configuration

Validates that all expected Cursor files exist:
- Rules (5 files)
- Commands (5 files)
- Skills (7 files)
- Subagents (7 files)
- Hooks (4 files)

### 4. Docs Completeness

Validates that all expected docs exist and are non-empty.

### 5. YAML Validity

Parses all `.sdlc/*.yaml` files and reports parse errors.

### 6. Makefile Targets

Validates that required Makefile targets exist.

### 7. Integration Status (Warnings)

Checks environment variables for configured integrations.
Missing integrations produce warnings, not failures.

## When to Run the Doctor

Run after:
- Adding or removing top-level directories
- Creating or deleting `.sdlc/*.yaml` files
- Creating or deleting `.cursor/` configuration files
- Changing the Makefile structure
- Any structural initialization or restructuring

## Doctor Configuration

Doctor check rules are defined in `.sdlc/doctor.yaml`.
The Python implementation is in `.sdlc/dsl/doctor.py`.

## Important Rules

- Never modify Doctor rules to hide real failures.
- Never claim the Doctor passed without running it.
- Warnings must be reviewed — if a warning represents a real risk, address it.
