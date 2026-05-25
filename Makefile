# Local development entrypoint for RPG-OP.

UV ?= uv
NPM ?= npm
PYTHON_VERSION ?= 3.12
BACKEND_DIR ?= backend
FRONTEND_DIR ?= apps/web

ifeq ($(OS),Windows_NT)
BACKEND_PY := $(BACKEND_DIR)/.venv/Scripts/python.exe
BACKEND_LOCAL_PY := .venv/Scripts/python.exe
POWERSHELL := powershell -NoProfile -ExecutionPolicy Bypass
else
BACKEND_PY := $(BACKEND_DIR)/.venv/bin/python
BACKEND_LOCAL_PY := .venv/bin/python
POWERSHELL := pwsh -NoProfile
endif

.PHONY: help setup backend-venv backend-sync frontend-install dev-backend dev-frontend build-frontend preview-frontend lint format test smoke validate plane-sync-infrastructure

help:
	@echo "RPG-OP local commands"
	@echo "  make setup                     Install local backend/frontend dependencies"
	@echo "  make dev-backend               Run FastAPI locally"
	@echo "  make dev-frontend              Run React + Vite locally"
	@echo "  make test                      Run test suite"
	@echo "  make lint                      Run Python and TypeScript checks"
	@echo "  make format                    Format Python code"
	@echo "  make validate                  Run SDLC validation script"
	@echo "  make plane-sync-infrastructure Sync architecture doc to Plane"

setup: backend-sync frontend-install

backend-venv:
	$(UV) venv "$(BACKEND_DIR)/.venv" --python "$(PYTHON_VERSION)"

backend-sync: backend-venv
	$(UV) pip sync --python "$(BACKEND_PY)" "$(BACKEND_DIR)/requirements.txt"

frontend-install:
	cd "$(FRONTEND_DIR)" && $(NPM) install

dev-backend:
	cd "$(BACKEND_DIR)" && "$(BACKEND_LOCAL_PY)" -m uvicorn app.main:app --reload --port 8000

dev-frontend:
	cd "$(FRONTEND_DIR)" && $(NPM) run dev

build-frontend:
	cd "$(FRONTEND_DIR)" && $(NPM) run build

preview-frontend:
	cd "$(FRONTEND_DIR)" && $(NPM) run preview -- --host 0.0.0.0 --port 4173

lint:
	$(UV) run --with ruff ruff check "$(BACKEND_DIR)" "packages/rpg_dsl" "specs" ".cursor/hooks"
	cd "$(FRONTEND_DIR)" && $(NPM) run build

format:
	$(UV) run --with ruff ruff format "$(BACKEND_DIR)" "packages/rpg_dsl" "specs" ".cursor/hooks"

test:
	$(UV) run --with pytest pytest "tests" "$(BACKEND_DIR)" -q

smoke:
	"$(BACKEND_PY)" "$(BACKEND_DIR)/scripts/smoke_test.py"

validate:
	$(POWERSHELL) -File ".sdlc/scripts/validate.ps1"

plane-sync-infrastructure:
	$(POWERSHELL) -File ".sdlc/scripts/plane-sync-wiki-doc.ps1" -DocPath "docs/infrastructure/project-architecture.md" -PageName "Infrastructure - Project Architecture"
