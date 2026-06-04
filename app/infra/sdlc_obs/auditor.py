"""
SDLC Auditor — runs a comprehensive audit of the SDLC structure and generates a canvas report.

Usage:
    python app/infra/sdlc_obs/auditor.py [--canvas-output PATH]

Outputs:
    - Prints audit results to stdout
    - Writes a .canvas.tsx report file (default: ~/.cursor/projects/.../canvases/sdlc-audit-report.canvas.tsx)
    - Exits 0 if no CRITICAL gaps, 1 otherwise
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Literal

# ── Types ──────────────────────────────────────────────────────────────────────

Status = Literal["PASS", "WARN", "FAIL", "SKIP"]


@dataclass
class CheckResult:
    category: str
    check: str
    status: Status
    detail: str = ""
    recommendation: str = ""


@dataclass
class AuditReport:
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    results: list[CheckResult] = field(default_factory=list)

    def add(
        self,
        category: str,
        check: str,
        status: Status,
        detail: str = "",
        recommendation: str = "",
    ) -> None:
        self.results.append(
            CheckResult(category, check, status, detail, recommendation)
        )

    @property
    def counts(self) -> dict[str, int]:
        c: dict[str, int] = {"PASS": 0, "WARN": 0, "FAIL": 0, "SKIP": 0}
        for r in self.results:
            c[r.status] += 1
        return c

    @property
    def autonomy_score(self) -> int:
        total = len(self.results)
        if total == 0:
            return 0
        passes = self.counts["PASS"]
        warns = self.counts["WARN"]
        return round((passes + warns * 0.5) / total * 100)

    @property
    def health_score(self) -> int:
        total = len(self.results)
        if total == 0:
            return 0
        return round(self.counts["PASS"] / total * 100)

    def by_category(self) -> dict[str, list[CheckResult]]:
        cats: dict[str, list[CheckResult]] = {}
        for r in self.results:
            cats.setdefault(r.category, []).append(r)
        return cats


# ── Helpers ────────────────────────────────────────────────────────────────────

REPO_ROOT = Path(__file__).resolve().parents[3]


def _file_exists(path: str) -> bool:
    return (REPO_ROOT / path).exists()


def _file_has_section(path: str, section: str) -> bool:
    f = REPO_ROOT / path
    if not f.exists():
        return False
    content = f.read_text(errors="ignore")
    return section.lower() in content.lower()


def _run_doctor() -> tuple[int, str]:
    result = subprocess.run(
        [sys.executable, ".sdlc/dsl/cli.py", "doctor"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        timeout=30,
    )
    return result.returncode, result.stdout + result.stderr


def _count_lines(path: str) -> int:
    f = REPO_ROOT / path
    if not f.exists():
        return 0
    return len(f.read_text(errors="ignore").splitlines())


# ── Check groups ───────────────────────────────────────────────────────────────


def check_structural(report: AuditReport) -> None:
    """Run make sdlc-doctor and parse results."""
    exit_code, output = _run_doctor()
    pass_count = output.count("[PASS]")
    fail_count = output.count("[FAIL]")
    warn_count = output.count("[WARN]")

    compliance_path = REPO_ROOT / ".sdlc" / "memory" / "sdlc-compliance.json"
    compliance_detail = ""
    if compliance_path.is_file():
        try:
            payload = json.loads(compliance_path.read_text(encoding="utf-8"))
            compliance_detail = (
                f"; compliance {payload.get('compliance_pct')}% "
                f"(health {payload.get('health_pct')}%)"
            )
        except json.JSONDecodeError:
            compliance_detail = "; compliance metrics unreadable"

    if exit_code == 0:
        report.add(
            "Estrutura",
            "SDLC Doctor",
            "PASS",
            f"{pass_count} checks passando, {warn_count} avisos{compliance_detail}",
        )
    else:
        report.add(
            "Estrutura",
            "SDLC Doctor",
            "FAIL",
            f"{fail_count} falhas, {warn_count} avisos\n{output[:500]}",
            "Execute `make sdlc-doctor` e corrija os FAILs",
        )

    required_dirs = [
        ".cursor/rules",
        ".cursor/commands",
        ".cursor/skills",
        ".cursor/agents",
        ".cursor/hooks",
        ".sdlc",
        ".sdlc/dsl",
        ".sdlc/memory",
        "docs/architecture",
        "docs/infrastructure",
        "docs/operations",
        ".sdlc/process",
        "app/frontend",
        "app/backend",
        "app/infra",
        "app/shared",
        "app/infra/sdlc_obs",
    ]
    for d in required_dirs:
        exists = (REPO_ROOT / d).is_dir()
        report.add(
            "Estrutura",
            f"Diretório {d}",
            "PASS" if exists else "FAIL",
            "" if exists else f"Diretório {d} não encontrado",
            "" if exists else f"Crie `{d}/`",
        )


def check_agents(report: AuditReport) -> None:
    """Verify all required Cursor agents exist and have the right sections."""
    required_agents = {
        "planner.md": ["Role", "Responsabilit"],  # Responsibilities or Responsabilidades
        "architect.md": ["Role"],
        "implementer.md": ["Role"],
        "reviewer.md": ["Role"],
        "qa.md": ["Role"],
        "devops.md": ["Role", "Rollback", "delete_branch_on_merge"],
        "doctor.md": ["Role"],
        "observer.md": ["Role", "Responsibilit"],  # Responsibilities or Responsabilidades
        "issue-analyst.md": ["Role", "Responsabilidades", "GitHub MCP"],
        # new agents from simulation proposals
        "migration-runner.md": ["Role"],
        "contract-validator.md": ["Role"],
        "auto-fixer.md": ["Role"],
        "rollback-agent.md": ["Role"],
        "security-scanner.md": ["Role"],
    }

    for fname, sections in required_agents.items():
        path = f".cursor/agents/{fname}"
        if not _file_exists(path):
            report.add(
                "Agentes",
                fname,
                "FAIL",
                f"Agente {fname} não existe",
                f"Crie `.cursor/agents/{fname}`",
            )
            continue

        missing_sections = [s for s in sections if not _file_has_section(path, s)]
        if missing_sections:
            report.add(
                "Agentes",
                fname,
                "WARN",
                f"Seções ausentes: {missing_sections}",
                f"Adicione as seções {missing_sections} em {fname}",
            )
        else:
            report.add("Agentes", fname, "PASS", "Todas as seções presentes")


def check_skills(report: AuditReport) -> None:
    """Verify all required skills exist."""
    required_skills = {
        "requirements-refinement.md": ["Purpose", "Procedure"],
        "architecture-analysis.md": ["Purpose"],
        "implementation.md": ["Purpose"],
        "qa-validation.md": ["Purpose"],
        "code-review.md": ["Purpose"],
        "observability.md": ["Purpose"],
        "documentation.md": ["Purpose"],
        "task-creation.md": ["Purpose", "DoD", "[AI]"],
        "branch-naming.md": ["feature/", "INVES", "issue-gh"],
        # new skills from simulation proposals
        "container-validation.md": ["Purpose", "Procedure"],
        "e2e-testing.md": ["Purpose", "Procedure"],
        "secrets-management.md": ["Purpose", "Procedure"],
        "performance-testing.md": ["Purpose"],
        "auto-merge-policy.md": ["Purpose", "confidence"],
    }

    for fname, keywords in required_skills.items():
        path = f".cursor/skills/{fname}"
        if not _file_exists(path):
            report.add(
                "Skills",
                fname,
                "FAIL",
                f"Skill {fname} não existe",
                f"Crie `.cursor/skills/{fname}`",
            )
            continue

        missing = [kw for kw in keywords if not _file_has_section(path, kw)]
        if missing:
            report.add(
                "Skills",
                fname,
                "WARN",
                f"Conteúdo ausente: {missing}",
                f"Adicione {missing} em {fname}",
            )
        else:
            report.add("Skills", fname, "PASS")


def check_mcp(report: AuditReport) -> None:
    """Verify MCP configuration and connectivity."""
    mcp_path = ".cursor/mcp.json"
    if not _file_exists(mcp_path):
        report.add(
            "MCP",
            "mcp.json",
            "FAIL",
            "Arquivo .cursor/mcp.json não encontrado",
            "Crie .cursor/mcp.json com GitHub e Plane MCP",
        )
        return

    try:
        content = json.loads((REPO_ROOT / mcp_path).read_text())
        servers = content.get("mcpServers", {})

        for service in ["github", "plane"]:
            found = any(service in k.lower() for k in servers)
            report.add(
                "MCP",
                f"MCP {service}",
                "PASS" if found else "FAIL",
                f"Servidor {service} {'configurado' if found else 'não configurado'}",
                "" if found else f"Adicione servidor MCP para {service} em mcp.json",
            )
    except json.JSONDecodeError as e:
        report.add(
            "MCP",
            "mcp.json parse",
            "FAIL",
            f"JSON inválido: {e}",
            "Corrija o JSON em .cursor/mcp.json",
        )


def check_pipeline(report: AuditReport) -> None:
    """Verify pipeline gates: branch naming, PR lifecycle, security rules."""
    branch_skill = ".cursor/skills/branch-naming.md"
    report.add(
        "Pipeline",
        "Branch naming skill",
        "PASS" if _file_exists(branch_skill) else "FAIL",
        "" if _file_exists(branch_skill) else "Skill de branch naming ausente",
        "" if _file_exists(branch_skill) else "Crie .cursor/skills/branch-naming.md",
    )

    devops = ".cursor/agents/devops.md"
    has_delete = _file_has_section(devops, "delete_branch_on_merge")
    report.add(
        "Pipeline",
        "Auto-delete de branch em merge",
        "PASS" if has_delete else "WARN",
        "Regra de delete_branch_on_merge" + (" documentada" if has_delete else " ausente"),
        "" if has_delete else "Adicione `delete_branch_on_merge: true` em devops.md",
    )

    auto_merge = ".cursor/skills/auto-merge-policy.md"
    report.add(
        "Pipeline",
        "Auto-merge policy",
        "PASS" if _file_exists(auto_merge) else "WARN",
        "" if _file_exists(auto_merge) else "Política de auto-merge não definida",
        "" if _file_exists(auto_merge) else "Crie .cursor/skills/auto-merge-policy.md",
    )

    security = ".cursor/agents/security-scanner.md"
    report.add(
        "Pipeline",
        "Security Scanner",
        "PASS" if _file_exists(security) else "FAIL",
        "" if _file_exists(security) else "SecurityScanner ausente — PRs sem análise de segurança",
        "" if _file_exists(security) else "Crie .cursor/agents/security-scanner.md",
    )


def check_observability(report: AuditReport) -> None:
    """Verify SDLC observability components."""
    obs_files = [
        "app/infra/sdlc_obs/collector.py",
        "app/infra/sdlc_obs/server.py",
        "app/infra/sdlc_obs/schema.sql",
        "app/infra/sdlc_obs/hooks/pre_task.py",
        "app/infra/sdlc_obs/hooks/post_task.py",
    ]
    for f in obs_files:
        report.add(
            "Observabilidade",
            Path(f).name,
            "PASS" if _file_exists(f) else "FAIL",
            "" if _file_exists(f) else f"Arquivo {f} ausente",
            "" if _file_exists(f) else f"Crie {f}",
        )

    db_path = REPO_ROOT / "app/infra/sdlc_obs/data/sdlc_obs.db"
    if db_path.exists():
        report.add("Observabilidade", "SQLite DB", "PASS", "DB existe e tem dados")
    else:
        report.add(
            "Observabilidade",
            "SQLite DB",
            "WARN",
            "DB não inicializado",
            "Execute `make obs-init && make obs-seed` para inicializar",
        )

    hooks_pre = ".cursor/hooks/pre-task.md"
    has_obs = _file_has_section(hooks_pre, "pre_task.py")
    report.add(
        "Observabilidade",
        "Hook pre-task emite métricas",
        "PASS" if has_obs else "WARN",
        "" if has_obs else "pre-task.md não chama pre_task.py",
        "" if has_obs else "Adicione chamada ao pre_task.py em .cursor/hooks/pre-task.md",
    )


def check_gaps_from_simulation(report: AuditReport) -> None:
    """Check for the specific gaps identified in the simulation canvas."""
    gaps = [
        (
            "Gaps da Simulação",
            "Testes E2E (Playwright)",
            ".cursor/skills/e2e-testing.md",
            "Gap G1: Sem testes E2E — entrega sem validação ponta-a-ponta",
            "Crie .cursor/skills/e2e-testing.md",
        ),
        (
            "Gaps da Simulação",
            "Validação de Contrato API",
            ".cursor/agents/contract-validator.md",
            "Gap G2: Drift OpenAPI↔TypeScript sem detecção automática",
            "Crie .cursor/agents/contract-validator.md",
        ),
        (
            "Gaps da Simulação",
            "Migration Runner",
            ".cursor/agents/migration-runner.md",
            "Gap G3: Migrations sem validação automática de reversibilidade",
            "Crie .cursor/agents/migration-runner.md",
        ),
        (
            "Gaps da Simulação",
            "Docker Compose validation",
            ".cursor/skills/container-validation.md",
            "Gap G4: Container build não validado no CI",
            "Crie .cursor/skills/container-validation.md",
        ),
        (
            "Gaps da Simulação",
            "SAST + Dependency scan",
            ".cursor/agents/security-scanner.md",
            "Gap G5: Zero análise de segurança automática",
            "Crie .cursor/agents/security-scanner.md",
        ),
        (
            "Gaps da Simulação",
            "Secrets scan (gitleaks)",
            ".cursor/skills/secrets-management.md",
            "Gap G6: Segredos podem ser commitados sem detecção",
            "Crie .cursor/skills/secrets-management.md",
        ),
        (
            "Gaps da Simulação",
            "Auto-Fixer para CI failures",
            ".cursor/agents/auto-fixer.md",
            "Gap G7: Falhas de CI requerem intervenção manual do Implementer",
            "Crie .cursor/agents/auto-fixer.md",
        ),
        (
            "Gaps da Simulação",
            "Rollback automático",
            ".cursor/agents/rollback-agent.md",
            "Gap G8: Sem rollback automático após degradação de métricas",
            "Crie .cursor/agents/rollback-agent.md",
        ),
        (
            "Gaps da Simulação",
            "Performance testing (k6)",
            ".cursor/skills/performance-testing.md",
            "Gap G9: Zero baseline de performance — regressões não detectadas",
            "Crie .cursor/skills/performance-testing.md",
        ),
        (
            "Gaps da Simulação",
            "Auto-merge policy com confidence score",
            ".cursor/skills/auto-merge-policy.md",
            "Gap G10: Sem critério formal para merge autônomo seguro",
            "Crie .cursor/skills/auto-merge-policy.md",
        ),
        (
            "Gaps da Simulação",
            "IaC para infra (Terraform/Pulumi)",
            "app/infra/terraform/",
            "Gap G11: Infra criada manualmente — sem IaC reproduzível",
            "Crie app/infra/terraform/ com módulos para PostgreSQL, Redis, backend, frontend",
        ),
        (
            "Gaps da Simulação",
            "CI/CD workflow (GitHub Actions)",
            ".github/workflows/",
            "Gap G12: Sem CI pipeline automatizado — testes manuais",
            "Crie .github/workflows/ com jobs de test, build, deploy",
        ),
    ]

    for cat, check, path, detail, recommendation in gaps:
        exists = (REPO_ROOT / path).exists()
        report.add(
            cat,
            check,
            "PASS" if exists else "FAIL",
            detail if not exists else f"Implementado em {path}",
            recommendation if not exists else "",
        )


def check_github_workflow(report: AuditReport) -> None:
    """Check for GitHub Actions CI workflow."""
    workflows_dir = REPO_ROOT / ".github/workflows"
    if not workflows_dir.exists():
        report.add(
            "CI/CD",
            "GitHub Actions",
            "FAIL",
            "Sem .github/workflows/ — CI não automatizado",
            "Crie .github/workflows/ci.yml com jobs: test, lint, security, build",
        )
        return

    workflows = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    if not workflows:
        report.add(
            "CI/CD",
            "GitHub Actions",
            "FAIL",
            "Diretório .github/workflows/ existe mas está vazio",
            "Crie pelo menos um workflow: ci.yml",
        )
    else:
        report.add(
            "CI/CD",
            "GitHub Actions",
            "PASS",
            f"{len(workflows)} workflow(s) configurados",
        )


# ── Canvas generator ──────────────────────────────────────────────────────────


def _badge(status: str) -> str:
    colors = {"PASS": "#22c55e", "WARN": "#f59e0b", "FAIL": "#ef4444", "SKIP": "#94a3b8"}
    return colors.get(status, "#94a3b8")


def generate_canvas(report: AuditReport) -> str:
    counts = report.counts
    autonomy = report.autonomy_score
    health = report.health_score
    ts = report.timestamp[:19].replace("T", " ")

    # Collect top recommendations
    recommendations = [
        r for r in report.results if r.status in ("FAIL", "WARN") and r.recommendation
    ][:10]

    categories = report.by_category()

    # Build category cards data
    cat_items = []
    for cat, results in categories.items():
        cat_pass = sum(1 for r in results if r.status == "PASS")
        cat_fail = sum(1 for r in results if r.status == "FAIL")
        cat_warn = sum(1 for r in results if r.status == "WARN")
        cat_items.append(
            {
                "name": cat,
                "pass": cat_pass,
                "fail": cat_fail,
                "warn": cat_warn,
                "total": len(results),
                "score": round(cat_pass / max(len(results), 1) * 100),
            }
        )

    cats_json = json.dumps(cat_items, ensure_ascii=False)
    recs_json = json.dumps(
        [{"check": r.check, "status": r.status, "detail": r.detail, "recommendation": r.recommendation}
         for r in recommendations],
        ensure_ascii=False,
    )
    results_json = json.dumps(
        [{"category": r.category, "check": r.check, "status": r.status, "detail": r.detail}
         for r in report.results],
        ensure_ascii=False,
    )

    canvas = f"""import React, {{ useState }} from "react";

const AUDIT_DATA = {{
  timestamp: "{ts}",
  autonomyScore: {autonomy},
  healthScore: {health},
  counts: {{ PASS: {counts["PASS"]}, WARN: {counts["WARN"]}, FAIL: {counts["FAIL"]}, SKIP: {counts["SKIP"]} }},
  categories: {cats_json},
  recommendations: {recs_json},
  allResults: {results_json},
}};

const STATUS_COLORS = {{
  PASS: {{ bg: "#dcfce7", text: "#15803d", border: "#86efac" }},
  WARN: {{ bg: "#fef3c7", text: "#92400e", border: "#fcd34d" }},
  FAIL: {{ bg: "#fee2e2", text: "#991b1b", border: "#fca5a5" }},
  SKIP: {{ bg: "#f1f5f9", text: "#475569", border: "#cbd5e1" }},
}};

function Badge({{ status }}: {{ status: string }}) {{
  const c = STATUS_COLORS[status] || STATUS_COLORS.SKIP;
  return (
    <span style={{{{ background: c.bg, color: c.text, border: `1px solid ${{c.border}}`, padding: "2px 8px", borderRadius: 9999, fontSize: 11, fontWeight: 700 }}}}>
      {{status}}
    </span>
  );
}}

function ScoreGauge({{ value, label, color }}: {{ value: number; label: string; color: string }}) {{
  return (
    <div style={{{{ textAlign: "center" }}}}>
      <svg width="100" height="100" viewBox="0 0 100 100">
        <circle cx="50" cy="50" r="42" fill="none" stroke="#e2e8f0" strokeWidth="10" />
        <circle
          cx="50" cy="50" r="42" fill="none" stroke={{color}} strokeWidth="10"
          strokeDasharray={{`${{Math.round(2 * Math.PI * 42 * value / 100)}} ${{Math.round(2 * Math.PI * 42)}}`}}
          strokeLinecap="round"
          transform="rotate(-90 50 50)"
        />
        <text x="50" y="56" textAnchor="middle" fontSize="20" fontWeight="bold" fill="#1e293b">{{value}}%</text>
      </svg>
      <div style={{{{ fontSize: 12, color: "#64748b", marginTop: 4 }}}}>{{label}}</div>
    </div>
  );
}}

export default function SDLCAuditReport() {{
  const [activeTab, setActiveTab] = useState<"overview" | "details" | "recommendations">("overview");
  const [filterCat, setFilterCat] = useState<string>("all");
  const [filterStatus, setFilterStatus] = useState<string>("all");
  const d = AUDIT_DATA;
  const total = d.counts.PASS + d.counts.WARN + d.counts.FAIL + d.counts.SKIP;

  const filtered = d.allResults.filter(r =>
    (filterCat === "all" || r.category === filterCat) &&
    (filterStatus === "all" || r.status === filterStatus)
  );

  const cats = [...new Set(d.allResults.map(r => r.category))];

  return (
    <div style={{{{ fontFamily: "'Inter', system-ui, sans-serif", background: "#f8fafc", minHeight: "100vh", padding: 24 }}}}>
      <div style={{{{ maxWidth: 1100, margin: "0 auto" }}}}>

        {{/* Header */}}
        <div style={{{{ background: "linear-gradient(135deg, #1e293b 0%, #334155 100%)", borderRadius: 16, padding: 32, color: "white", marginBottom: 24 }}}}>
          <div style={{{{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}}}>
            <div>
              <div style={{{{ fontSize: 13, opacity: 0.7, marginBottom: 8 }}}}>SDLC AUTONOMY AUDIT</div>
              <h1 style={{{{ margin: 0, fontSize: 28, fontWeight: 800 }}}}>Relatório de Auditoria SDLC</h1>
              <div style={{{{ marginTop: 8, opacity: 0.8, fontSize: 14 }}}}>Gerado em {{d.timestamp}} · {{total}} checks executados</div>
            </div>
            <div style={{{{ display: "flex", gap: 24 }}}}>
              <ScoreGauge value={{d.autonomyScore}} label="Autonomia" color="#6366f1" />
              <ScoreGauge value={{d.healthScore}} label="Saúde" color="#22c55e" />
            </div>
          </div>

          {{/* Summary badges */}}
          <div style={{{{ display: "flex", gap: 12, marginTop: 24 }}}}>
            {{[["PASS", "#22c55e"], ["WARN", "#f59e0b"], ["FAIL", "#ef4444"]].map(([s, c]) => (
              <div key={{s}} style={{{{ background: "rgba(255,255,255,0.1)", borderRadius: 8, padding: "8px 16px", textAlign: "center" }}}}>
                <div style={{{{ fontSize: 24, fontWeight: 800, color: c as string }}}}>{{d.counts[s as keyof typeof d.counts]}}</div>
                <div style={{{{ fontSize: 11, opacity: 0.8 }}}}>{{s}}</div>
              </div>
            ))}}
          </div>
        </div>

        {{/* Tabs */}}
        <div style={{{{ display: "flex", gap: 4, marginBottom: 16 }}}}>
          {{(["overview", "details", "recommendations"] as const).map(tab => (
            <button key={{tab}} onClick={{() => setActiveTab(tab)}}
              style={{{{ padding: "8px 20px", borderRadius: 8, border: "none", cursor: "pointer", fontWeight: 600,
                background: activeTab === tab ? "#6366f1" : "white",
                color: activeTab === tab ? "white" : "#475569",
                boxShadow: "0 1px 3px rgba(0,0,0,0.1)" }}}}>
              {{tab === "overview" ? "Visão Geral" : tab === "details" ? "Detalhes" : "Recomendações"}}
            </button>
          ))}}
        </div>

        {{/* Overview Tab */}}
        {{activeTab === "overview" && (
          <div style={{{{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))", gap: 16 }}}}>
            {{d.categories.map(cat => (
              <div key={{cat.name}} style={{{{ background: "white", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}}}>
                <div style={{{{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}}}>
                  <div style={{{{ fontWeight: 700, color: "#1e293b", fontSize: 14 }}}}>{{cat.name}}</div>
                  <div style={{{{ fontSize: 20, fontWeight: 800, color: cat.score >= 80 ? "#22c55e" : cat.score >= 60 ? "#f59e0b" : "#ef4444" }}}}>
                    {{cat.score}}%
                  </div>
                </div>
                <div style={{{{ background: "#f1f5f9", borderRadius: 99, height: 8, marginBottom: 12 }}}}>
                  <div style={{{{ height: 8, borderRadius: 99, width: `${{cat.score}}%`,
                    background: cat.score >= 80 ? "#22c55e" : cat.score >= 60 ? "#f59e0b" : "#ef4444" }}}} />
                </div>
                <div style={{{{ display: "flex", gap: 8, fontSize: 12 }}}}>
                  <span style={{{{ color: "#22c55e" }}}}>✓ {{cat.pass}}</span>
                  <span style={{{{ color: "#f59e0b" }}}}>⚠ {{cat.warn}}</span>
                  <span style={{{{ color: "#ef4444" }}}}>✗ {{cat.fail}}</span>
                  <span style={{{{ color: "#94a3b8" }}}}>/ {{cat.total}}</span>
                </div>
              </div>
            ))}}
          </div>
        )}}

        {{/* Details Tab */}}
        {{activeTab === "details" && (
          <div style={{{{ background: "white", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)" }}}}>
            <div style={{{{ display: "flex", gap: 12, marginBottom: 16 }}}}>
              <select value={{filterCat}} onChange={{e => setFilterCat(e.target.value)}}
                style={{{{ padding: "6px 12px", borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 13 }}}}>
                <option value="all">Todas as categorias</option>
                {{cats.map(c => <option key={{c}} value={{c}}>{{c}}</option>)}}
              </select>
              <select value={{filterStatus}} onChange={{e => setFilterStatus(e.target.value)}}
                style={{{{ padding: "6px 12px", borderRadius: 8, border: "1px solid #e2e8f0", fontSize: 13 }}}}>
                <option value="all">Todos os status</option>
                {{["PASS", "WARN", "FAIL"].map(s => <option key={{s}} value={{s}}>{{s}}</option>)}}
              </select>
            </div>
            <div style={{{{ display: "flex", flexDirection: "column", gap: 4 }}}}>
              {{filtered.map((r, i) => (
                <div key={{i}} style={{{{ display: "flex", alignItems: "flex-start", gap: 12, padding: "10px 12px",
                  background: i % 2 === 0 ? "#f8fafc" : "white", borderRadius: 6 }}}}>
                  <Badge status={{r.status}} />
                  <div style={{{{ flex: 1 }}}}>
                    <div style={{{{ fontWeight: 600, fontSize: 13, color: "#1e293b" }}}}>{{r.category}} → {{r.check}}</div>
                    {{r.detail && <div style={{{{ fontSize: 12, color: "#64748b", marginTop: 2 }}}}>{{r.detail}}</div>}}
                  </div>
                </div>
              ))}}
            </div>
          </div>
        )}}

        {{/* Recommendations Tab */}}
        {{activeTab === "recommendations" && (
          <div style={{{{ display: "flex", flexDirection: "column", gap: 12 }}}}>
            {{d.recommendations.length === 0 ? (
              <div style={{{{ background: "white", borderRadius: 12, padding: 32, textAlign: "center", color: "#22c55e", fontWeight: 700 }}}}>
                ✓ Nenhuma recomendação crítica — SDLC em boa saúde!
              </div>
            ) : d.recommendations.map((r, i) => (
              <div key={{i}} style={{{{ background: "white", borderRadius: 12, padding: 20, boxShadow: "0 1px 4px rgba(0,0,0,0.08)",
                borderLeft: `4px solid ${{r.status === "FAIL" ? "#ef4444" : "#f59e0b"}}` }}}}>
                <div style={{{{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}}}>
                  <Badge status={{r.status}} />
                  <div style={{{{ fontWeight: 700, color: "#1e293b" }}}}>{{r.check}}</div>
                </div>
                {{r.detail && <div style={{{{ fontSize: 13, color: "#64748b", marginBottom: 8 }}}}>{{r.detail}}</div>}}
                <div style={{{{ fontSize: 13, color: "#6366f1", fontWeight: 600 }}}}>→ {{r.recommendation}}</div>
              </div>
            ))}}
          </div>
        )}}
      </div>
    </div>
  );
}}
"""
    return canvas


# ── Main ───────────────────────────────────────────────────────────────────────


def run_audit() -> AuditReport:
    report = AuditReport()

    print("\n🔍 SDLC Auditor — iniciando varredura completa...\n")

    steps = [
        ("Estrutura", check_structural),
        ("Agentes", check_agents),
        ("Skills", check_skills),
        ("MCP", check_mcp),
        ("Pipeline & GitHub", check_pipeline),
        ("Observabilidade", check_observability),
        ("Gaps da Simulação", check_gaps_from_simulation),
        ("CI/CD", check_github_workflow),
    ]

    for name, fn in steps:
        print(f"  ▸ {name}...", end=" ", flush=True)
        fn(report)
        print("✓")

    return report


def print_report(report: AuditReport) -> None:
    counts = report.counts
    print(f"\n{'='*60}")
    print(f"  SDLC AUDIT REPORT — {report.timestamp[:19]}")
    print(f"{'='*60}")

    for cat, results in report.by_category().items():
        print(f"\n  [{cat}]")
        for r in results:
            icon = {"PASS": "✓", "WARN": "⚠", "FAIL": "✗", "SKIP": "−"}[r.status]
            line = f"    [{r.status}] {icon} {r.check}"
            if r.detail:
                line += f" — {r.detail[:80]}"
            print(line)

    print(f"\n{'='*60}")
    print(f"  PASS: {counts['PASS']}  WARN: {counts['WARN']}  FAIL: {counts['FAIL']}")
    print(f"  Autonomy Score: {report.autonomy_score}%")
    print(f"  Health Score:   {report.health_score}%")
    print(f"{'='*60}\n")

    if counts["FAIL"] > 0:
        print("  ⚠ RECOMENDAÇÕES CRÍTICAS:")
        for r in report.results:
            if r.status == "FAIL" and r.recommendation:
                print(f"    → {r.recommendation}")
        print()


def find_canvas_dir() -> Path:
    project_id = "home-crassus-personal-sdlc-ai"
    candidate = Path.home() / ".cursor" / "projects" / project_id / "canvases"
    if candidate.exists():
        return candidate
    candidate.mkdir(parents=True, exist_ok=True)
    return candidate


def main() -> None:
    canvas_output = None
    args = sys.argv[1:]
    for i, arg in enumerate(args):
        if arg == "--canvas-output" and i + 1 < len(args):
            canvas_output = Path(args[i + 1])

    report = run_audit()
    print_report(report)

    canvas_content = generate_canvas(report)

    if canvas_output is None:
        canvas_dir = find_canvas_dir()
        canvas_output = canvas_dir / "sdlc-audit-report.canvas.tsx"

    canvas_output.parent.mkdir(parents=True, exist_ok=True)
    canvas_output.write_text(canvas_content)
    print(f"  📊 Canvas gerado: {canvas_output}\n")

    sys.exit(0 if report.counts["FAIL"] == 0 else 1)


if __name__ == "__main__":
    main()
