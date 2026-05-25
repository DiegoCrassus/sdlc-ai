# Frontend

Target home for the TypeScript frontend application.

The current React + Vite implementation still lives in `apps/web/` during transition. New frontend architecture work should plan the migration to this directory and update:

- `Makefile`
- `.sdlc/config.yaml`
- `.sdlc/commands/commands.yaml`
- `.cursor/rules/frontend-react.mdc`
- GitHub Actions
- documentation in `docs/infrastructure/`
