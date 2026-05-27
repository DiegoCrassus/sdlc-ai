.PHONY: sdlc-doctor sdlc-validate sdlc-stages docs-check obs-init obs-server obs-seed sdlc-audit help backend-install backend-test backend-dev backend-docker

# Default target
help:
	@echo "SDLC AI — Available targets:"
	@echo ""
	@echo "  sdlc-doctor    Run the SDLC Doctor (validates structure, YAML, docs)"
	@echo "  sdlc-validate  Validate YAML schema consistency"
	@echo "  sdlc-stages    List lifecycle stages"
	@echo "  docs-check     Check that all required docs exist and are non-empty"
	@echo ""
	@echo "  backend-install  Install backend Python dependencies"
	@echo "  backend-test     Run backend unit + integration tests"
	@echo "  backend-dev      Start FastAPI dev server (port 8000)"
	@echo "  backend-docker   Start backend + Redis via docker compose"
	@echo ""
	@echo "  obs-init       Initialize SDLC observability database"
	@echo "  obs-server     Start SDLC observability dashboard (http://localhost:7700)"
	@echo "  obs-seed       Insert sample data for dashboard preview"
	@echo ""
	@echo "  sdlc-audit     Run autonomous SDLC audit — generates canvas report"
	@echo ""
	@echo "Usage: make <target>"

PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)

sdlc-doctor:
	@echo "Running SDLC Doctor..."
	@$(PYTHON) .sdlc/dsl/cli.py doctor

sdlc-validate:
	@echo "Running SDLC validation..."
	@$(PYTHON) .sdlc/dsl/cli.py validate

sdlc-stages:
	@$(PYTHON) .sdlc/dsl/cli.py list-stages

docs-check:
	@echo "Checking docs structure..."
	@$(PYTHON) .sdlc/dsl/cli.py doctor > /dev/null && echo "Docs check passed." || echo "Docs check failed — run make sdlc-doctor for details."

obs-init:
	@echo "Initializing SDLC observability database..."
	@mkdir -p app/infra/sdlc_obs/data
	@$(PYTHON) -c "import sys; sys.path.insert(0,'.'); from app.infra.sdlc_obs.collector import Collector; c=Collector(); print('[obs] database initialized at ' + str(c.db_path))"

obs-server:
	@echo "Starting SDLC observability dashboard..."
	@$(PYTHON) app/infra/sdlc_obs/server.py 7700

obs-seed:
	@echo "Inserting sample data..."
	@$(PYTHON) -c "\
import sys; sys.path.insert(0,'.');\
from app.infra.sdlc_obs.collector import Collector;\
import time; col = Collector();\
runs = [\
  dict(task_name='[AI][BACKEND] Init Flask skeleton',stage='implementation',agent='implementer',task_tags=['[AI]','[BACKEND]'],completion_status='completed',tokens_input=1200,tokens_output=800,cost_usd=0.0048,tool_calls_total=5,tool_calls_success=5,tests_passed=8,doctor_exit_code=0),\
  dict(task_name='[AI][PLAN] Backend API design',stage='requirements',agent='planner',task_tags=['[AI]','[PLAN]'],completion_status='completed',tokens_input=900,tokens_output=600,cost_usd=0.0036,tool_calls_total=3,tool_calls_success=3,doctor_exit_code=0),\
  dict(task_name='[AI][INFRA] Setup obs tool',stage='implementation',agent='devops',task_tags=['[AI]','[INFRA]'],completion_status='completed',tokens_input=1500,tokens_output=1100,cost_usd=0.0072,tool_calls_total=8,tool_calls_success=7,tool_calls_failed=1,tests_passed=5,doctor_exit_code=0),\
  dict(task_name='[AI][BACKEND] Add Plane endpoint',stage='architecture',agent='architect',task_tags=['[AI]','[BACKEND]'],completion_status='completed',tokens_input=800,tokens_output=500,cost_usd=0.0026,tool_calls_total=4,tool_calls_success=4,doctor_exit_code=0),\
  dict(task_name='[AI][QA] Validate Plane integration',stage='validation',agent='qa',task_tags=['[AI]','[QA]'],completion_status='completed',tokens_input=600,tokens_output=400,cost_usd=0.0018,tool_calls_total=6,tool_calls_success=6,tests_passed=12,doctor_exit_code=0),\
];\
[col.record(**r) for r in runs];\
print('[obs] sample data inserted — 5 runs across 5 stages')"

sdlc-audit:
	@echo "Running SDLC Audit..."
	@$(PYTHON) app/infra/sdlc_obs/auditor.py

export-pdf:
	@echo "Generating simulation PDF..."
	@$(PYTHON) app/infra/sdlc_obs/export_simulation_pdf.py
	@echo "PDF: simulacao-end-to-end-sdlc.pdf"

VENV ?= .venv
VENV_PYTHON := $(VENV)/bin/python
VENV_PIP := $(VENV)/bin/pip

backend-install:
	@test -d $(VENV) || python3 -m venv $(VENV)
	@$(VENV_PIP) install -q pydantic httpx "SQLAlchemy[asyncio]" aiosqlite redis beautifulsoup4 fastapi "uvicorn[standard]" python-dotenv pytest pytest-asyncio

backend-test: backend-install
	@PYTHONPATH=. MARKET_DATA_MODE=mock $(VENV_PYTHON) -m pytest app/backend/tests/ -v

backend-dev: backend-install
	@PYTHONPATH=. $(VENV_PYTHON) -m uvicorn app.backend.src.main:app --reload --host $${BACKEND_HOST:-0.0.0.0} --port $${BACKEND_PORT:-8000}

backend-docker:
	@docker compose up --build -d
	@echo "Backend: http://localhost:8000/health"
	@echo "API docs: http://localhost:8000/docs"
