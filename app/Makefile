# MarketPulse — local development Makefile
#
# Quick start:
#   make start     install everything (if needed) and run backend + frontend together
#
# Backend:  http://127.0.0.1:8000  (docs at /docs)
# Frontend: http://127.0.0.1:5173

.PHONY: help start install install-backend install-frontend backend frontend test clean

# Repo root is one level above this app/ directory.
ROOT := $(abspath $(dir $(abspath $(lastword $(MAKEFILE_LIST))))/..)
FRONTEND_DIR := $(ROOT)/app/frontend

PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)

BACKEND_HOST ?= 127.0.0.1
BACKEND_PORT ?= 8000

help:
	@echo "MarketPulse — local development"
	@echo ""
	@echo "  make start              Install deps (if needed) and run backend + frontend"
	@echo "  make install            Install backend + frontend dependencies"
	@echo "  make backend            Run only the FastAPI backend (port $(BACKEND_PORT))"
	@echo "  make frontend           Run only the Vite frontend (port 5173)"
	@echo "  make test               Run backend tests"
	@echo "  make clean              Remove caches and build artifacts"
	@echo ""
	@echo "  Backend:  http://$(BACKEND_HOST):$(BACKEND_PORT)/docs"
	@echo "  Frontend: http://127.0.0.1:5173"

# --- Install -----------------------------------------------------------------

install: install-backend install-frontend

install-backend:
	@echo "==> Installing backend (editable) from $(ROOT)"
	@cd $(ROOT) && $(PYTHON) -m pip install -e ".[dev]"

install-frontend:
	@echo "==> Installing frontend dependencies"
	@cd $(FRONTEND_DIR) && npm install

# --- Run individually --------------------------------------------------------

backend:
	@echo "==> Backend on http://$(BACKEND_HOST):$(BACKEND_PORT) (docs at /docs)"
	@cd $(ROOT) && $(PYTHON) -m uvicorn marketpulse.main:app --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT)

frontend:
	@echo "==> Frontend on http://127.0.0.1:5173"
	@cd $(FRONTEND_DIR) && npm run dev

# --- Run everything together -------------------------------------------------

start: install
	@echo ""
	@echo "==> Starting MarketPulse (backend + frontend)"
	@echo "    Backend:  http://$(BACKEND_HOST):$(BACKEND_PORT)/docs"
	@echo "    Frontend: http://127.0.0.1:5173"
	@echo "    Press Ctrl+C to stop both."
	@echo ""
	@trap 'echo; echo "==> Stopping..."; kill 0' INT TERM EXIT; \
	( cd $(ROOT) && $(PYTHON) -m uvicorn marketpulse.main:app --reload --host $(BACKEND_HOST) --port $(BACKEND_PORT) ) & \
	( cd $(FRONTEND_DIR) && npm run dev ) & \
	wait

# --- Tests & cleanup ---------------------------------------------------------

test:
	@echo "==> Running backend tests"
	@cd $(ROOT) && PYTHONPATH=app/backend/src $(PYTHON) -m pytest app/backend/tests/ -v

clean:
	@echo "==> Cleaning caches and build artifacts"
	@find $(ROOT)/app -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	@find $(ROOT)/app -type d -name .pytest_cache -prune -exec rm -rf {} + 2>/dev/null || true
	@rm -rf $(FRONTEND_DIR)/dist 2>/dev/null || true
