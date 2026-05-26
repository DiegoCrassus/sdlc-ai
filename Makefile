SHELL := bash

UV ?= uv
NPM ?= npm

.PHONY: help setup dev dev-backend dev-frontend test smoke validate lint format bootstrap-linux

help:
	@echo "RPG-OP — shell-only toolchain"
	@echo "  make setup            Install dependencies"
	@echo "  make dev              Backend + frontend"
	@echo "  make dev-backend      FastAPI :8000"
	@echo "  make dev-frontend     Vite :5173"
	@echo "  make test             pytest"
	@echo "  make smoke            API smoke (backend running)"
	@echo "  make validate         local validation"
	@echo "  make lint             Python lint + frontend build"
	@echo "  make format           Format Python files"
	@echo "  make bootstrap-linux  Ubuntu/WSL prerequisites"
	@echo ""
	@echo "Shortcut: ./dev.sh"

setup:
	bash .sdlc/scripts/setup.sh

dev:
	bash .sdlc/scripts/dev-all.sh

dev-backend:
	bash .sdlc/scripts/dev-backend.sh

dev-frontend:
	cd apps/frontend && $(NPM) run dev

test:
	bash .sdlc/scripts/run-tests.sh

smoke:
	bash .sdlc/scripts/smoke.sh

validate:
	bash .sdlc/scripts/validate.sh

lint:
	$(UV) run --with ruff ruff check apps/backend .cursor/hooks
	cd apps/frontend && $(NPM) run build

format:
	$(UV) run --with ruff ruff format apps/backend .cursor/hooks

bootstrap-linux:
	bash .sdlc/scripts/bootstrap-linux.sh
