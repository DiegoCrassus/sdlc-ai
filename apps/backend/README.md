# Backend

Target home for the Python backend application.

The current FastAPI implementation still lives in `backend/` during transition. New backend architecture work should plan the migration to this directory and update:

- `Makefile`
- `.sdlc/config.yaml`
- `.sdlc/commands/commands.yaml`
- `.cursor/rules/backend-python.mdc`
- GitHub Actions
- documentation in `docs/infrastructure/`
