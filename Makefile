.PHONY: sdlc-doctor sdlc-validate sdlc-stages sdlc-sync-model docs-check obs-init obs-server obs-seed sdlc-audit plane-in-progress auto-merge-pr issue-triage plane-reformat plane-evidence workflow-status workflow-start workflow-discover sdlc-compact-memory sdlc-session-status sdlc-meta-start sdlc-meta-commit sdlc-meta-qa studio-dev studio-api studio-smoke studio-e2e help

help:
	@echo "SDLC AI — Available targets:"
	@echo ""
	@echo "  sdlc-doctor    Run the SDLC Doctor (validates structure, YAML, docs)"
	@echo "  sdlc-validate  Validate YAML schema consistency"
	@echo "  sdlc-sync-model  Compare lifecycle-model write_policy vs paths.yaml shim"
	@echo "  sdlc-stages    List lifecycle stages"
	@echo "  docs-check     Check that all required docs exist and are non-empty"
	@echo ""
	@echo "  obs-init       Initialize SDLC observability database"
	@echo "  obs-server     Start SDLC observability dashboard (http://localhost:7700)"
	@echo "  obs-seed       Insert sample data for dashboard preview"
	@echo ""
	@echo "  sdlc-audit     Run autonomous SDLC audit — generates canvas report"
	@echo "  plane-in-progress  Move Plane card to In Progress (CARD=INVES-N)"
	@echo "  auto-merge-pr  Autonomous squash merge when CI green (PR=N CARD=INVES-N)"
	@echo "  issue-triage   Close superseded GitHub issues (TRIAGE=1 to apply)"
	@echo "  plane-reformat Reformat Plane descriptions (CARD=INVES-N or ALL=1)"
	@echo "  plane-evidence Post structured Done evidence (CARD=INVES-N)"
	@echo "  workflow-status  Show SDLC session gate + handoff"
	@echo "  workflow-start   Open gate (CARD=INVES-N SLUG=... STAGE=sdlc_meta|implementation)"
	@echo "  workflow-discover  Refresh discovery context from repo + Plane"
	@echo ""
	@echo "  sdlc-compact-memory  Compact operational-context.md (rolling summary)"
	@echo "  sdlc-session-status  Show session gate status with last_agent + last_commit"
	@echo ""
	@echo "  sdlc-meta-start   Meta-tool: validate + gate + branch (CARD=INVES-N SLUG=...)"
	@echo "  sdlc-meta-commit  Meta-tool: lint + commit + push (CARD=INVES-N MSG='...')"
	@echo "  sdlc-meta-qa      Meta-tool: tests + doctor + QA evidence (CARD=INVES-N)"
	@echo ""
	@echo "  studio-dev        Studio API :8100 + UI :5174 (install npm in app/studio-frontend first)"
	@echo "  studio-api        Studio API only on :8100"
	@echo "  studio-smoke      HTTP smoke (API must be running; honors STUDIO_AUTH_TOKEN)"
	@echo "  studio-e2e        Playwright smoke — dashboard, workflows, observability"
	@echo ""
	@echo "Workflow: .sdlc/process/change-lifecycle.md"

PYTHON ?= $(shell command -v python3 2>/dev/null || command -v python 2>/dev/null)

sdlc-doctor:
	@echo "Running SDLC Doctor..."
	@$(PYTHON) .sdlc/dsl/cli.py doctor

sdlc-validate:
	@echo "Running SDLC validation..."
	@$(PYTHON) .sdlc/dsl/cli.py validate

sdlc-sync-model:
	@$(PYTHON) .sdlc/scripts/sdlc_sync_model.py

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

plane-in-progress:
	@test -n "$(CARD)" || (echo "Usage: make plane-in-progress CARD=INVES-N" && exit 1)
	@$(PYTHON) .sdlc/scripts/plane_state.py in-progress --card $(CARD)

auto-merge-pr:
	@test -n "$(PR)" || (echo "Usage: make auto-merge-pr PR=32 CARD=INVES-N" && exit 1)
	@$(PYTHON) .sdlc/scripts/auto_merge_pr.py --pr $(PR) $(if $(CARD),--card $(CARD) --plane-comment,)

issue-triage:
	@$(PYTHON) .sdlc/scripts/github_issue_triage.py $(if $(TRIAGE),--close-superseded,--dry-run)

plane-reformat:
	@if [ "$(ALL)" = "1" ]; then $(PYTHON) .sdlc/scripts/plane_card.py reformat-all; \
	else test -n "$(CARD)" || (echo "Usage: make plane-reformat CARD=INVES-N or ALL=1" && exit 1); \
	$(PYTHON) .sdlc/scripts/plane_card.py reformat-description --card $(CARD); fi

plane-evidence:
	@test -n "$(CARD)" || (echo "Usage: make plane-evidence CARD=INVES-N" && exit 1)
	@$(PYTHON) .sdlc/scripts/plane_card.py post-evidence --card $(CARD) \
	  --file .sdlc/templates/plane/evidence-$(CARD).json

workflow-status:
	@$(PYTHON) .sdlc/dsl/cli.py workflow status

workflow-start:
	@test -n "$(CARD)" || (echo "Usage: make workflow-start CARD=INVES-N SLUG=my-feature STAGE=implementation" && exit 1)
	@$(PYTHON) .sdlc/dsl/cli.py workflow start --card $(CARD) --slug $(or $(SLUG),work) --stage $(or $(STAGE),implementation) $(if $(FORCE),--force,)

workflow-discover:
	@$(PYTHON) .sdlc/dsl/cli.py workflow discover

sdlc-compact-memory:
	@echo "Compacting SDLC memory context..."
	@$(PYTHON) .sdlc/scripts/compact_memory.py

sdlc-session-status:
	@$(PYTHON) .sdlc/dsl/cli.py workflow status

sdlc-meta-start:
	@test -n "$(CARD)" || (echo "Usage: make sdlc-meta-start CARD=INVES-N SLUG=my-feature [STAGE=implementation]" && exit 1)
	@bash .sdlc/scripts/meta-tools/validate-and-start.sh --card $(CARD) --slug $(or $(SLUG),work) --stage $(or $(STAGE),implementation)

sdlc-meta-commit:
	@test -n "$(CARD)" || (echo "Usage: make sdlc-meta-commit CARD=INVES-N MSG='Short summary' [PATHS='.']" && exit 1)
	@bash .sdlc/scripts/meta-tools/commit-and-push.sh --card $(CARD) --msg "$(MSG)" $(if $(PATHS),--paths "$(PATHS)",)

sdlc-meta-qa:
	@test -n "$(CARD)" || (echo "Usage: make sdlc-meta-qa CARD=INVES-N [TEST_CMD=pytest]" && exit 1)
	@bash .sdlc/scripts/meta-tools/qa-to-review.sh --card $(CARD) $(if $(TEST_CMD),--test-cmd "$(TEST_CMD)",)

export-pdf:
	@echo "Generating simulation PDF..."
	@$(PYTHON) app/infra/sdlc_obs/export_simulation_pdf.py
	@echo "PDF: simulacao-end-to-end-sdlc.pdf"

studio-api:
	@echo "Studio API http://127.0.0.1:8100 (Ctrl+C stops)"
	@STUDIO_REPO_ROOT=$$(pwd) PYTHONPATH=app/studio-backend/src:$$PWD $(PYTHON) -m uvicorn studio_service.main:app --reload --host 127.0.0.1 --port 8100

studio-smoke:
	@cd app/studio-frontend && npm run smoke

studio-e2e:
	@bash tests/e2e/run-studio-e2e.sh

studio-dev:
	@test -d app/studio-frontend/node_modules || (echo "Run: cd app/studio-frontend && npm install" && exit 1)
	@echo "Starting Studio API http://127.0.0.1:8100 and UI http://127.0.0.1:5174 (Ctrl+C stops both)"
	@trap 'kill 0' INT TERM EXIT; \
	  STUDIO_REPO_ROOT=$$(pwd) PYTHONPATH=app/studio-backend/src:$$PWD $(PYTHON) -m uvicorn studio_service.main:app --reload --host 127.0.0.1 --port 8100 & \
	  cd app/studio-frontend && npm run dev & \
	  wait
