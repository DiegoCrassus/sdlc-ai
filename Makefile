.PHONY: sdlc-doctor sdlc-validate sdlc-stages docs-check obs-init obs-server obs-seed sdlc-audit help

help:
	@echo "SDLC AI — Available targets:"
	@echo ""
	@echo "  sdlc-doctor    Run the SDLC Doctor (validates structure, YAML, docs)"
	@echo "  sdlc-validate  Validate YAML schema consistency"
	@echo "  sdlc-stages    List lifecycle stages"
	@echo "  docs-check     Check that all required docs exist and are non-empty"
	@echo ""
	@echo "  obs-init       Initialize SDLC observability database"
	@echo "  obs-server     Start SDLC observability dashboard (http://localhost:7700)"
	@echo "  obs-seed       Insert sample data for dashboard preview"
	@echo ""
	@echo "  sdlc-audit     Run autonomous SDLC audit — generates canvas report"
	@echo ""
	@echo "Workflow: docs/sdlc/change-lifecycle.md"

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
runs = [\
  dict(task_name='[AI][PLAN] Backend API design',stage='requirements',agent='planner',task_tags=['[AI]','[PLAN]'],completion_status='completed',tokens_input=900,tokens_output=600,cost_usd=0.0036,tool_calls_total=3,tool_calls_success=3,doctor_exit_code=0),\
  dict(task_name='[AI][INFRA] Setup obs tool',stage='implementation',agent='devops',task_tags=['[AI]','[INFRA]'],completion_status='completed',tokens_input=1500,tokens_output=1100,cost_usd=0.0072,tool_calls_total=8,tool_calls_success=7,tool_calls_failed=1,tests_passed=5,doctor_exit_code=0),\
];\
col = Collector();\
[col.record(**r) for r in runs];\
print('[obs] sample data inserted')"

sdlc-audit:
	@echo "Running SDLC Audit..."
	@$(PYTHON) app/infra/sdlc_obs/auditor.py

export-pdf:
	@echo "Generating simulation PDF..."
	@$(PYTHON) app/infra/sdlc_obs/export_simulation_pdf.py
	@echo "PDF: simulacao-end-to-end-sdlc.pdf"
