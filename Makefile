#!/usr/bin/env bash
# Local development — all targets delegate to .sh scripts (Linux / WSL / macOS).

SHELL := bash

UV ?= uv
NPM ?= npm

.PHONY: help setup dev dev-backend dev-frontend test smoke validate lint format bootstrap-linux plane-sync-infrastructure plane-sync-roadmap plane-sync-poc plane-create-phase1

help:
	@echo "RPG-OP — shell-only toolchain"
	@echo "  make setup                     Install dependencies"
	@echo "  make dev                       Backend + frontend"
	@echo "  make dev-backend               FastAPI :8000"
	@echo "  make dev-frontend              Vite :5173"
	@echo "  make test                      pytest"
	@echo "  make smoke                     API smoke (backend running)"
	@echo "  make validate                  SDLC validate"
	@echo "  make bootstrap-linux           Ubuntu/WSL prerequisites"
	@echo "  make plane-sync-infrastructure Sync architecture doc to Plane"
	@echo "  make plane-sync-roadmap        Sync docs/05-roadmap.md to Plane wiki"
	@echo "  make plane-sync-poc            Sync PoC index to Plane wiki"
	@echo "  make plane-create-phase1       Create Fase 1 work items in Plane"
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
	$(UV) run --with ruff ruff check apps/backend packages/rpg_dsl specs .cursor/hooks
	cd apps/frontend && $(NPM) run build

format:
	$(UV) run --with ruff ruff format apps/backend packages/rpg_dsl specs .cursor/hooks

bootstrap-linux:
	bash .sdlc/scripts/bootstrap-linux.sh

plane-sync-infrastructure:
	bash .sdlc/scripts/plane-sync-wiki-doc.sh docs/infrastructure/project-architecture.md "Infrastructure - Project Architecture"

plane-sync-roadmap:
	bash .sdlc/scripts/plane-sync-wiki-doc.sh docs/05-roadmap.md "Roadmap - foco Sheet Canvas"

plane-sync-poc:
	bash .sdlc/scripts/plane-sync-wiki-doc.sh docs/poc/00-indice-poc.md "PoC - Proof of Concept"
	bash .sdlc/scripts/plane-sync-wiki-doc.sh docs/poc/status-resumo.md "PoC - Status resumo"
	bash .sdlc/scripts/plane-sync-wiki-doc.sh docs/README.md "Docs - Indice"

plane-create-phase1:
	bash .sdlc/scripts/plane-create-phase1-tasks.sh
