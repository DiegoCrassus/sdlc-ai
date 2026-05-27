"""
Generate a PDF of the InvestTracker End-to-End Simulation.
Uses Chrome headless to render an HTML report and save as PDF.

Usage:
    python3 app/infra/sdlc_obs/export_simulation_pdf.py [--output PATH]
"""
from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

HTML = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>InvestTracker — Simulação End-to-End SDLC AI-Native</title>
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600&display=swap');
  *{box-sizing:border-box;margin:0;padding:0}
  body{font-family:'Inter',system-ui,sans-serif;background:#0d1117;color:#e6edf3;font-size:13px;line-height:1.5}
  @page{size:A4 landscape;margin:12mm 12mm 12mm 12mm}
  @media print{body{background:#fff!important;color:#0d1117!important}.page-break{page-break-before:always}.card{border:1px solid #e2e8f0!important;background:#f8fafc!important;color:#0d1117!important}.tag-success{background:#dcfce7!important;color:#15803d!important}.tag-warn{background:#fef3c7!important;color:#92400e!important}.tag-info{background:#dbeafe!important;color:#1e40af!important}.tag-neutral{background:#f1f5f9!important;color:#334155!important}h1,h2,h3{color:#0d1117!important}.muted{color:#475569!important}.code{background:#e2e8f0!important;color:#0d1117!important}table{border-color:#e2e8f0!important}td,th{border-color:#e2e8f0!important;color:#0d1117!important}.header{background:linear-gradient(135deg,#1e293b,#334155)!important;color:#e6edf3!important}.stat-card{background:#f1f5f9!important}}
  h1{font-size:22px;font-weight:800;margin-bottom:4px}
  h2{font-size:15px;font-weight:700;margin:20px 0 10px;border-bottom:1px solid #21262d;padding-bottom:6px}
  h3{font-size:13px;font-weight:700;margin-bottom:6px}
  .header{background:linear-gradient(135deg,#161b22 0%,#21262d 100%);padding:20px 24px;border-radius:12px;margin-bottom:20px;border:1px solid #30363d}
  .subtitle{color:#8b949e;font-size:12px;margin-top:6px}
  .tag{display:inline-block;padding:2px 10px;border-radius:99px;font-size:11px;font-weight:700;margin:2px}
  .tag-success{background:#1a4731;color:#3fb950}
  .tag-warn{background:#3d2b00;color:#d29922}
  .tag-info{background:#1d3a5e;color:#58a6ff}
  .tag-danger{background:#3d1616;color:#f85149}
  .tag-neutral{background:#21262d;color:#8b949e}
  .grid{display:grid;gap:12px}
  .g2{grid-template-columns:1fr 1fr}
  .g3{grid-template-columns:1fr 1fr 1fr}
  .g4{grid-template-columns:1fr 1fr 1fr 1fr}
  .card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:16px}
  .stat-card{background:#161b22;border:1px solid #30363d;border-radius:10px;padding:14px;text-align:center}
  .stat-val{font-size:26px;font-weight:800;line-height:1.1}
  .stat-lbl{font-size:11px;color:#8b949e;margin-top:4px}
  .stat-desc{font-size:10px;color:#6e7681;margin-top:2px}
  .muted{color:#8b949e}
  .code{font-family:'JetBrains Mono',monospace;font-size:10px;background:#21262d;padding:2px 6px;border-radius:4px}
  table{width:100%;border-collapse:collapse;margin:6px 0}
  th{background:#21262d;color:#8b949e;font-size:11px;font-weight:600;padding:6px 8px;text-align:left;border:1px solid #30363d}
  td{padding:6px 8px;border:1px solid #30363d;font-size:11px;vertical-align:top}
  tr:nth-child(even){background:#0d1117}
  tr.closed td:first-child::before{content:"✓ ";color:#3fb950}
  .callout{background:#1d3a5e;border:1px solid #2d5a8e;border-radius:8px;padding:14px;margin:14px 0}
  .callout-success{background:#1a4731;border-color:#2d6a4a}
  .divider{border:none;border-top:1px solid #21262d;margin:18px 0}
  .score-ring{display:inline-flex;align-items:center;gap:6px;font-size:20px;font-weight:800}
  .check{color:#3fb950}
  .cross{color:#f85149}
  .warn{color:#d29922}
  ul{padding-left:16px}
  li{margin:3px 0;font-size:12px}
  .agent-badge{display:inline-block;padding:1px 8px;border-radius:4px;font-size:10px;font-weight:600}
</style>
</head>
<body>

<!-- HEADER -->
<div class="header">
  <div style="display:flex;justify-content:space-between;align-items:flex-start">
    <div>
      <h1>InvestTracker — Simulação End-to-End</h1>
      <div class="subtitle">SDLC AI-Native · Exercício de Autonomia Completa · Resultado Final</div>
      <div style="margin-top:10px">
        <span class="tag tag-success">Autonomy Score: 99%</span>
        <span class="tag tag-success">Health Score: 97%</span>
        <span class="tag tag-info">18 tarefas · 100% IA</span>
        <span class="tag tag-success">12 gaps originais fechados</span>
        <span class="tag tag-success">2 gaps residuais fechados</span>
      </div>
    </div>
    <div style="text-align:right;color:#8b949e;font-size:11px">
      <div style="font-size:28px;font-weight:800;color:#3fb950">99%</div>
      <div>Autonomia</div>
      <div style="margin-top:6px;font-size:26px;color:#58a6ff">97%</div>
      <div>Saúde</div>
    </div>
  </div>
</div>

<!-- KPIs -->
<div class="grid g4" style="margin-bottom:18px">
  <div class="stat-card"><div class="stat-val" style="color:#3fb950">99%</div><div class="stat-lbl">Autonomy Score</div><div class="stat-desc">70 PASS · 2 WARN · 0 FAIL</div></div>
  <div class="stat-card"><div class="stat-val" style="color:#58a6ff">18/18</div><div class="stat-lbl">Tarefas 100% IA</div><div class="stat-desc">Do issue ao merge</div></div>
  <div class="stat-card"><div class="stat-val" style="color:#d29922">12/12</div><div class="stat-lbl">Gaps originais fechados</div><div class="stat-desc">+ 2 residuais</div></div>
  <div class="stat-card"><div class="stat-val" style="color:#f85149">0</div><div class="stat-lbl">Intervenção humana obrigatória</div><div class="stat-desc">Apenas opcional em auth</div></div>
</div>

<!-- STACK -->
<h2>Arquitetura do Software (InvestTracker)</h2>
<div class="grid g2">
  <div class="card">
    <h3>Stack Tecnológico</h3>
    <table>
      <tr><th>Camada</th><th>Tecnologia</th></tr>
      <tr><td>Frontend</td><td>Next.js + TypeScript</td></tr>
      <tr><td>Backend</td><td>FastAPI (Python)</td></tr>
      <tr><td>Banco de dados</td><td>PostgreSQL + Alembic migrations</td></tr>
      <tr><td>Cache / Fila</td><td>Redis (sessão + rate limit + jobs)</td></tr>
      <tr><td>Observabilidade</td><td>OpenTelemetry + Prometheus + Grafana</td></tr>
      <tr><td>Infraestrutura</td><td>Docker Compose (local) + GitHub Actions CI</td></tr>
    </table>
  </div>
  <div class="card">
    <h3>Agentes do SDLC</h3>
    <div style="columns:2;gap:10px">
      <div><span class="tag tag-info">Planner</span> <span class="tag tag-success">Architect</span><br>
      <span class="tag tag-success">Implementer</span> <span class="tag tag-info">QA</span><br>
      <span class="tag tag-neutral">Reviewer</span> <span class="tag tag-warn">DevOps</span><br>
      <span class="tag tag-neutral">Doctor</span> <span class="tag tag-neutral">Observer</span><br>
      <span class="tag tag-danger">IssueAnalyst</span> <span class="tag tag-info">SDLCAuditor</span><br>
      <span class="tag tag-warn">MigrationRunner</span> <span class="tag tag-success">ContractValidator</span><br>
      <span class="tag tag-danger">AutoFixer</span> <span class="tag tag-warn">RollbackAgent</span><br>
      <span class="tag tag-danger">SecurityScanner</span></div>
    </div>
    <div style="margin-top:10px;font-size:11px;color:#8b949e">15 agentes especializados · Cada um com Role, Responsabilidades, Fronteiras e Escalação definidos.</div>
  </div>
</div>

<hr class="divider">

<!-- JORNADA -->
<h2>Jornada Completa — 18 Tarefas (100% Autônomas)</h2>
<table>
  <tr><th>#</th><th>Tarefa [AI][TIPO]</th><th>Agente</th><th>Estágio</th><th>Artefato entregue</th><th>Gap fechado?</th></tr>
  <tr><td>1</td><td><span class="code">Issue GitHub: 'Build InvestTracker v1'</span></td><td><span class="tag tag-danger">Issue Analyst</span></td><td>triagem</td><td>Triagem + card Plane criado</td><td>—</td></tr>
  <tr><td>2</td><td><span class="code">[AI][PLAN] Create InvestTracker MVP</span></td><td><span class="tag tag-info">Planner</span></td><td>requisitos</td><td>Plano 11 seções + DoD</td><td>—</td></tr>
  <tr class="closed"><td>3</td><td><span class="code">[AI][ARCH] Define full architecture</span></td><td><span class="tag tag-success">Architect</span></td><td>arquitetura</td><td>ADR-001–005 + impacted tree</td><td><span class="tag tag-success">G01 fechado</span></td></tr>
  <tr class="closed"><td>4</td><td><span class="code">[AI][INFRA] Setup Docker Compose</span></td><td><span class="tag tag-success">Implementer</span></td><td>implementação</td><td>docker-compose.yml + .env.example</td><td><span class="tag tag-success">G02 fechado</span></td></tr>
  <tr><td>5</td><td><span class="code">[AI][BACKEND] FastAPI skeleton + /health</span></td><td><span class="tag tag-success">Implementer</span></td><td>implementação</td><td>app/backend/ + health check</td><td>—</td></tr>
  <tr class="closed"><td>6</td><td><span class="code">[AI][BACKEND] PostgreSQL schema + migrations</span></td><td><span class="tag tag-warn">MigrationRunner</span></td><td>implementação</td><td>models.py + Alembic validados</td><td><span class="tag tag-success">G03 fechado</span></td></tr>
  <tr><td>7</td><td><span class="code">[AI][BACKEND] Investment CRUD API</span></td><td><span class="tag tag-success">Implementer</span></td><td>implementação</td><td>5 endpoints + OpenAPI spec</td><td>—</td></tr>
  <tr><td>8</td><td><span class="code">[AI][BACKEND] Redis caching + rate limit</span></td><td><span class="tag tag-success">Implementer</span></td><td>implementação</td><td>RedisClient + cache decorators</td><td>—</td></tr>
  <tr><td>9</td><td><span class="code">[AI][BACKEND] Instrument OpenTelemetry</span></td><td><span class="tag tag-success">Implementer</span></td><td>implementação</td><td>Traces + metrics + logs</td><td>—</td></tr>
  <tr><td>10</td><td><span class="code">[AI][FRONTEND] Next.js skeleton + routing</span></td><td><span class="tag tag-success">Implementer</span></td><td>implementação</td><td>app/frontend/ + pages</td><td>—</td></tr>
  <tr><td>11</td><td><span class="code">[AI][FRONTEND] Investment dashboard UI</span></td><td><span class="tag tag-success">Implementer</span></td><td>implementação</td><td>Dashboard + table + charts</td><td>—</td></tr>
  <tr class="closed"><td>12</td><td><span class="code">[AI][FRONTEND] Connect frontend to API</span></td><td><span class="tag tag-success">ContractValidator</span></td><td>implementação</td><td>API client + tipos TS sincronizados</td><td><span class="tag tag-success">G05 fechado</span></td></tr>
  <tr><td>13</td><td><span class="code">[AI][INFRA] Prometheus + Grafana</span></td><td><span class="tag tag-success">Implementer</span></td><td>implementação</td><td>prometheus.yml + dashboard.json</td><td>—</td></tr>
  <tr class="closed"><td>14</td><td><span class="code">[AI][QA] Integration + E2E tests</span></td><td><span class="tag tag-info">QA</span></td><td>validação</td><td>pytest + Playwright evidence</td><td><span class="tag tag-success">G04 fechado</span></td></tr>
  <tr><td>15</td><td><span class="code">make sdlc-audit → Autonomy Score 99%</span></td><td><span class="tag tag-neutral">Doctor/Auditor</span></td><td>validação</td><td>70 PASS · 2 WARN · 0 FAIL</td><td>—</td></tr>
  <tr class="closed"><td>16</td><td><span class="code">[AI][REVIEW] PR review + confidence score</span></td><td><span class="tag tag-neutral">Reviewer</span></td><td>revisão</td><td>APPROVE (score ≥ 0.95)</td><td><span class="tag tag-success">G08 fechado</span></td></tr>
  <tr class="closed"><td>17</td><td><span class="code">auto-merge-gate: all green → merge</span></td><td><span class="tag tag-warn">DevOps + CI</span></td><td>deploy</td><td>Branch deletado + Issue fechada</td><td><span class="tag tag-success">G09 fechado</span></td></tr>
  <tr><td>18</td><td><span class="code">Observer fecha ciclo + emite KPIs</span></td><td><span class="tag tag-neutral">Observer</span></td><td>observabilidade</td><td>SQLite run + dashboard :7700</td><td>—</td></tr>
</table>

<hr class="divider">
<div class="page-break"></div>

<!-- GAPS ORIGINAIS -->
<h2>12 Gaps Originais — Todos Fechados</h2>
<table>
  <tr><th>ID</th><th>Área</th><th>Problema que existia</th><th>Solução implementada</th><th>Agente/Artefato</th></tr>
  <tr><td><span class="code">G01</span></td><td>Arquitetura</td><td>ADRs de alto risco pediam revisão humana</td><td>auto-merge-policy.md: confidence score ≥ 0.95 → APPROVE automático</td><td><span class="tag tag-neutral">Reviewer</span></td></tr>
  <tr><td><span class="code">G02</span></td><td>Infra/CI</td><td>Docker build sem validação automática</td><td>container-validation.md + job container no ci.yml</td><td><span class="tag tag-warn">DevOps</span></td></tr>
  <tr><td><span class="code">G03</span></td><td>Database</td><td>Migrations sem validação em banco real</td><td>MigrationRunner: alembic upgrade + downgrade + schema inspect</td><td><span class="tag tag-warn">MigrationRunner</span></td></tr>
  <tr><td><span class="code">G04</span></td><td>Testes E2E</td><td>Sem Playwright no pipeline</td><td>e2e-testing.md: Playwright headless como gate de QA</td><td><span class="tag tag-info">QA</span></td></tr>
  <tr><td><span class="code">G05</span></td><td>Contrato API</td><td>Drift OpenAPI ↔ TypeScript sem detecção</td><td>ContractValidator: openapi-typescript + diff automático</td><td><span class="tag tag-success">ContractValidator</span></td></tr>
  <tr><td><span class="code">G06</span></td><td>Segurança</td><td>Sem SAST ou scan de dependências</td><td>SecurityScanner: Bandit + npm audit + Trivy como gate</td><td><span class="tag tag-danger">SecurityScanner</span></td></tr>
  <tr><td><span class="code">G07</span></td><td>Segredos</td><td>Segredos sem detecção no diff</td><td>secrets-management.md + gitleaks-action no ci.yml</td><td><span class="tag tag-danger">SecurityScanner</span></td></tr>
  <tr><td><span class="code">G08</span></td><td>Revisão</td><td>Sem critério automático para APPROVE</td><td>Confidence score ≥ 0.95 habilita APPROVE autônomo</td><td><span class="tag tag-neutral">Reviewer</span></td></tr>
  <tr><td><span class="code">G09</span></td><td>Merge/Deploy</td><td>Trigger de merge manual</td><td>auto-merge-gate no ci.yml: todos gates verdes → merge</td><td><span class="tag tag-warn">DevOps</span></td></tr>
  <tr><td><span class="code">G10</span></td><td>Auto-Fix</td><td>Falhas de CI sem agente para corrigi-las</td><td>AutoFixer: lê CI output, abre PR de correção automaticamente</td><td><span class="tag tag-danger">AutoFixer</span></td></tr>
  <tr><td><span class="code">G11</span></td><td>Performance</td><td>Sem teste de carga antes do deploy</td><td>performance-testing.md: k6 + baseline comparison</td><td><span class="tag tag-info">QA</span></td></tr>
  <tr><td><span class="code">G12</span></td><td>Rollback</td><td>Rollback documentado mas não automatizado</td><td>RollbackAgent: executa plano documentado quando health degrada</td><td><span class="tag tag-warn">RollbackAgent</span></td></tr>
</table>

<hr class="divider">

<!-- GAPS RESIDUAIS -->
<h2>2 Gaps Residuais do Auditor — Fechados Autonomamente (Sem Humano)</h2>
<div class="grid g2">
  <div class="card">
    <h3><span class="tag tag-success">GR1 — IaC (Terraform)</span></h3>
    <p><strong>Falha identificada:</strong> <span class="code">app/infra/terraform/</span> não existia</p>
    <p style="margin-top:8px"><strong>Por que o gap existia:</strong> Sem skill nem estrutura para gerar infraestrutura como código.</p>
    <p style="margin-top:8px;color:#3fb950"><strong>Solução autônoma (Implementer + DevOps):</strong></p>
    <ul>
      <li>Criada skill <span class="code">iac-generation.md</span> com templates de módulos</li>
      <li>Estrutura <span class="code">app/infra/terraform/modules/</span> criada</li>
      <li>Implementer gera módulos a partir do <span class="code">docs/architecture/overview.md</span></li>
      <li>Job <span class="code">terraform</span> no ci.yml valida automaticamente</li>
    </ul>
  </div>
  <div class="card">
    <h3><span class="tag tag-success">GR2 — GitHub Actions CI</span></h3>
    <p><strong>Falha identificada:</strong> <span class="code">.github/workflows/</span> não existia</p>
    <p style="margin-top:8px"><strong>Por que o gap existia:</strong> Pipeline conceitual nas skills mas não conectado ao repositório real.</p>
    <p style="margin-top:8px;color:#3fb950"><strong>Solução autônoma (DevOps):</strong></p>
    <ul>
      <li>DevOps agent mapeou cada skill para um job de CI</li>
      <li>Criado <span class="code">.github/workflows/ci.yml</span> com 7 jobs</li>
      <li>Jobs: sdlc-doctor, secrets-scan, backend, frontend, container, terraform, auto-merge-gate</li>
      <li>Nenhuma decisão humana necessária — gates são verificáveis mecanicamente</li>
    </ul>
  </div>
</div>

<hr class="divider">

<!-- ROADMAP -->
<h2>Roadmap de Autonomia — Estado Final</h2>
<div class="grid g3">
  <div class="card">
    <div class="tag tag-neutral" style="margin-bottom:8px">Fase 1 — 61% (superado)</div>
    <p class="muted" style="font-size:12px">Estado inicial. 11/18 tarefas autônomas. Sem CI, sem segurança, sem E2E, sem migrations validadas.</p>
  </div>
  <div class="card">
    <div class="tag tag-neutral" style="margin-bottom:8px">Fase 2 — ~85% (superado)</div>
    <ul>
      <li class="check">container-validation.md</li>
      <li class="check">e2e-testing.md</li>
      <li class="check">gitleaks-action (ci.yml)</li>
      <li class="check">bandit + npm audit</li>
    </ul>
  </div>
  <div class="card" style="border-color:#3fb950">
    <div class="tag tag-success" style="margin-bottom:8px">Fase 3 — 99% ← ATUAL</div>
    <ul>
      <li class="check">MigrationRunner</li>
      <li class="check">ContractValidator</li>
      <li class="check">SecurityScanner</li>
      <li class="check">AutoFixer</li>
      <li class="check">RollbackAgent</li>
      <li class="check">auto-merge-gate</li>
      <li class="check">iac-generation.md + terraform/</li>
      <li class="check">GitHub Actions (7 jobs)</li>
    </ul>
  </div>
</div>

<hr class="divider">

<!-- PRÓXIMA FRONTEIRA -->
<h2>Próxima Fronteira — Para Produção Real</h2>
<div class="grid g3">
  <div class="card">
    <h3>Terraform Cloud Provider</h3>
    <p style="font-size:12px;margin-top:6px">Substituir módulos Docker locais por providers AWS/GCP/Azure. O Implementer faz isso a partir de <span class="code">iac-generation.md</span>.</p>
    <div style="margin-top:8px"><span class="tag tag-info">Implementer</span> <span class="tag tag-success">100% autônomo</span></div>
  </div>
  <div class="card">
    <h3>Staging Environment</h3>
    <p style="font-size:12px;margin-top:6px">Criar <span class="code">environments/staging.tfvars</span> + job de deploy no ci.yml para branch develop.</p>
    <div style="margin-top:8px"><span class="tag tag-warn">DevOps</span> <span class="tag tag-success">100% autônomo</span></div>
  </div>
  <div class="card">
    <h3>Auth/Security Gate (opcional)</h3>
    <p style="font-size:12px;margin-top:6px">Único ponto que permanece como opção humana: PRs com mudança em auth quando confidence score &lt; 0.95.</p>
    <div style="margin-top:8px"><span class="tag tag-neutral">Reviewer</span> <span class="tag tag-warn">gate opcional</span></div>
  </div>
</div>

<!-- CALLOUT FINAL -->
<div class="callout callout-success" style="margin-top:18px">
  <h3 style="color:#3fb950;margin-bottom:8px">Conclusão — O SDLC é capaz de se autoevoluir</h3>
  <p>O exercício mais importante desta simulação não foi identificar os gaps — foi provar que o próprio SDLC consegue fechá-los autonomamente. O Auditor identificou as 2 falhas estruturais restantes (IaC e GitHub Actions), e os agentes DevOps e Implementer as fecharam imediatamente, sem nenhuma intervenção humana.</p>
  <p style="margin-top:8px">O único ponto que permanece como <strong>opção humana</strong> (não obrigatório) é a revisão de PRs com impacto em autenticação — e mesmo esse gate pode ser tornando autônomo com o confidence scoring do Reviewer (score ≥ 0.95).</p>
  <p style="margin-top:8px;color:#8b949e;font-size:11px">Para produção real: substituir módulos Terraform locais por providers cloud + staging.tfvars. A decisão de qual cloud usar é a única que precisa de humano.</p>
</div>

<div style="margin-top:16px;text-align:right;font-size:10px;color:#6e7681">
  Gerado automaticamente por <span class="code">app/infra/sdlc_obs/export_simulation_pdf.py</span> · SDLC AI-Native · sdlc-ai
</div>

</body>
</html>
"""


def main() -> None:
    output_path = Path("simulacao-end-to-end-sdlc.pdf")
    for i, arg in enumerate(sys.argv[1:]):
        if arg == "--output" and i + 1 < len(sys.argv) - 1:
            output_path = Path(sys.argv[i + 2])

    # Write HTML to temp file
    html_path = Path("/tmp/simulacao_sdlc.html")
    html_path.write_text(HTML)
    print(f"  HTML escrito: {html_path}")

    # Find Chrome
    chrome = None
    for candidate in ["google-chrome", "chromium-browser", "chromium", "google-chrome-stable"]:
        result = subprocess.run(["which", candidate], capture_output=True, text=True)
        if result.returncode == 0:
            chrome = candidate
            break

    if not chrome:
        print("ERROR: Chrome/Chromium não encontrado. Instale com: sudo apt install chromium-browser")
        sys.exit(1)

    abs_output = output_path.resolve()

    cmd = [
        chrome,
        "--headless",
        "--disable-gpu",
        "--no-sandbox",
        "--print-to-pdf=" + str(abs_output),
        "--no-pdf-header-footer",
        "--print-to-pdf-no-header",
        "--disable-extensions",
        "file://" + str(html_path),
    ]

    print(f"  Executando Chrome headless...")
    result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)

    if abs_output.exists() and abs_output.stat().st_size > 1000:
        print(f"\n  ✅ PDF gerado: {abs_output} ({abs_output.stat().st_size // 1024} KB)\n")
    else:
        print(f"ERROR: PDF não foi gerado. Chrome output:\n{result.stderr}")
        sys.exit(1)


if __name__ == "__main__":
    main()
