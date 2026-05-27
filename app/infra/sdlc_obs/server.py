#!/usr/bin/env python3
"""
SDLC Observability Server
--------------------------
Lightweight web server (stdlib only) that exposes:
  GET /           → HTML dashboard
  GET /api/kpis   → JSON: top-level KPIs
  GET /api/runs   → JSON: recent runs (query param: ?stage=implementation&limit=50)
  GET /api/summary → JSON: metrics per stage/agent

Usage:
    python app/infra/sdlc_obs/server.py [port]
    make obs-server
"""

import json
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

sys.path.insert(0, str(Path(__file__).parents[3]))  # repo root
from app.infra.sdlc_obs.collector import Collector  # type: ignore

_col = Collector()

# ── HTML dashboard (inline, zero deps) ────────────────────────────────────

_HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>SDLC Observability</title>
<style>
  :root { --bg:#0d1117; --surface:#161b22; --border:#30363d; --text:#e6edf3;
          --muted:#8b949e; --accent:#58a6ff; --success:#3fb950; --warn:#d29922;
          --danger:#f85149; }
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body { background: var(--bg); color: var(--text); font-family: -apple-system,
         BlinkMacSystemFont,'Segoe UI',monospace; font-size: 14px; padding: 24px; }
  h1 { font-size: 20px; font-weight: 600; margin-bottom: 4px; }
  h2 { font-size: 14px; font-weight: 600; color: var(--muted); text-transform: uppercase;
       letter-spacing: .06em; margin: 24px 0 12px; }
  .subtitle { color: var(--muted); font-size: 13px; margin-bottom: 24px; }
  .kpi-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 12px; }
  .kpi { background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
         padding: 14px 16px; }
  .kpi-value { font-size: 26px; font-weight: 700; line-height: 1; }
  .kpi-label { font-size: 11px; color: var(--muted); margin-top: 4px; text-transform: uppercase;
               letter-spacing: .05em; }
  .success { color: var(--success); }
  .warn    { color: var(--warn); }
  .danger  { color: var(--danger); }
  .accent  { color: var(--accent); }
  table { width: 100%; border-collapse: collapse; background: var(--surface);
          border: 1px solid var(--border); border-radius: 8px; overflow: hidden; }
  th { padding: 8px 12px; text-align: left; font-size: 11px; color: var(--muted);
       text-transform: uppercase; letter-spacing: .05em; border-bottom: 1px solid var(--border); }
  td { padding: 8px 12px; border-bottom: 1px solid var(--border); font-size: 13px; }
  tr:last-child td { border-bottom: none; }
  tr:hover td { background: rgba(255,255,255,.02); }
  .pill { display: inline-block; padding: 2px 8px; border-radius: 20px; font-size: 11px;
          font-weight: 600; }
  .pill-success { background: rgba(63,185,80,.15); color: var(--success); }
  .pill-warn    { background: rgba(210,153,34,.15); color: var(--warn); }
  .pill-danger  { background: rgba(248,81,73,.15);  color: var(--danger); }
  .pill-neutral { background: rgba(139,148,158,.15); color: var(--muted); }
  .divider { border: none; border-top: 1px solid var(--border); margin: 24px 0; }
  .refresh { font-size: 12px; color: var(--muted); float: right; }
  code { font-family: monospace; font-size: 12px; color: var(--accent); }
</style>
</head>
<body>
<span class="refresh" id="ts"></span>
<h1>SDLC Observability</h1>
<p class="subtitle">sdlc-ai &mdash; AI-Native SDLC metrics &mdash; auto-refreshes every 30s</p>

<div class="kpi-grid" id="kpis">Loading…</div>

<hr class="divider">
<h2>Metrics by Stage &amp; Agent</h2>
<div id="summary-table"></div>

<hr class="divider">
<h2>Recent Runs</h2>
<div id="runs-table"></div>

<script>
const fmt = (v, suffix='') => v === null || v === undefined ? '—' : v + suffix;
const pill = (label, cls) => `<span class="pill pill-${cls}">${label}</span>`;

const statusPill = s => ({
  completed: pill('completed','success'),
  failed:    pill('failed','danger'),
  escalated: pill('escalated','warn'),
  abandoned: pill('abandoned','neutral'),
  unknown:   pill('unknown','neutral'),
}[s] || pill(s,'neutral'));

const agentColor = a => ({
  planner:'accent', architect:'warn', implementer:'success',
  qa:'accent', reviewer:'neutral', devops:'accent', doctor:'neutral',
}[a] || 'neutral');

async function loadKPIs() {
  const d = await fetch('/api/kpis').then(r => r.json());
  const items = [
    { label:'Total Runs',          value: fmt(d.total_runs),                   cls:'' },
    { label:'Completion Rate',     value: fmt(d.completion_rate_pct,'%'),       cls: d.completion_rate_pct >= 80 ? 'success' : d.completion_rate_pct >= 60 ? 'warn' : 'danger' },
    { label:'Avg Duration',        value: fmt(d.avg_duration_sec,'s'),          cls:'' },
    { label:'Total Cost',          value: '$'+fmt(d.total_cost_usd,''),         cls:'' },
    { label:'Tool Success',        value: fmt(d.tool_success_rate_pct,'%'),     cls: d.tool_success_rate_pct >= 90 ? 'success' : 'warn' },
    { label:'Hallucination Rate',  value: fmt(d.hallucination_rate_pct,'%'),    cls: d.hallucination_rate_pct === 0 ? 'success' : 'danger' },
    { label:'Regressions',         value: fmt(d.regressions),                  cls: d.regressions === 0 ? 'success' : 'danger' },
    { label:'Tests Passed',        value: fmt(d.tests_passed),                 cls:'success' },
  ];
  document.getElementById('kpis').innerHTML = items.map(i =>
    `<div class="kpi"><div class="kpi-value ${i.cls}">${i.value}</div>
     <div class="kpi-label">${i.label}</div></div>`
  ).join('');
}

async function loadSummary() {
  const rows = await fetch('/api/summary').then(r => r.json());
  if (!rows.length) { document.getElementById('summary-table').innerHTML = '<p style="color:var(--muted)">No data yet.</p>'; return; }
  const cols = ['stage','agent','total_runs','completion_rate_pct','avg_duration_sec',
                'total_cost_usd','tool_success_rate_pct','hallucination_rate_pct','regressions'];
  const head = cols.map(c => `<th>${c.replace(/_/g,' ')}</th>`).join('');
  const body = rows.map(r => `<tr>
    <td><code>${r.stage}</code></td>
    <td><span class="pill pill-${agentColor(r.agent)}">${r.agent}</span></td>
    <td>${fmt(r.total_runs)}</td>
    <td class="${r.completion_rate_pct >= 80 ? 'success' : 'warn'}">${fmt(r.completion_rate_pct,'%')}</td>
    <td>${fmt(r.avg_duration_sec,'s')}</td>
    <td>$${fmt(r.total_cost_usd)}</td>
    <td class="${r.tool_success_rate_pct >= 90 ? 'success' : 'warn'}">${fmt(r.tool_success_rate_pct,'%')}</td>
    <td class="${r.hallucination_rate_pct === 0 ? 'success' : 'danger'}">${fmt(r.hallucination_rate_pct,'%')}</td>
    <td class="${r.regressions === 0 ? 'success' : 'danger'}">${fmt(r.regressions)}</td>
  </tr>`).join('');
  document.getElementById('summary-table').innerHTML =
    `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

async function loadRuns() {
  const rows = await fetch('/api/runs?limit=20').then(r => r.json());
  if (!rows.length) { document.getElementById('runs-table').innerHTML = '<p style="color:var(--muted)">No runs recorded yet.</p>'; return; }
  const head = ['task','stage','agent','status','duration','cost','tools','hall.','reg.'].map(c => `<th>${c}</th>`).join('');
  const body = rows.map(r => `<tr>
    <td style="max-width:260px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" title="${r.task_name}"><code>${r.task_name}</code></td>
    <td><code>${r.stage}</code></td>
    <td><span class="pill pill-${agentColor(r.agent)}">${r.agent}</span></td>
    <td>${statusPill(r.completion_status)}</td>
    <td>${r.duration_ms ? (r.duration_ms/1000).toFixed(1)+'s' : '—'}</td>
    <td>${r.cost_usd ? '$'+r.cost_usd.toFixed(4) : '—'}</td>
    <td class="${r.tool_calls_total && r.tool_calls_failed===0 ? 'success' : r.tool_calls_failed ? 'danger' : ''}">
      ${r.tool_calls_success}/${r.tool_calls_total}</td>
    <td class="${r.hallucination_flag ? 'danger' : 'success'}">${r.hallucination_flag ? 'yes' : 'no'}</td>
    <td class="${r.regression_flag ? 'danger' : 'success'}">${r.regression_flag ? 'yes' : 'no'}</td>
  </tr>`).join('');
  document.getElementById('runs-table').innerHTML =
    `<table><thead><tr>${head}</tr></thead><tbody>${body}</tbody></table>`;
}

async function refresh() {
  document.getElementById('ts').textContent = 'Updated: ' + new Date().toLocaleTimeString();
  await Promise.all([loadKPIs(), loadSummary(), loadRuns()]);
}

refresh();
setInterval(refresh, 30000);
</script>
</body>
</html>"""


# ── HTTP handler ──────────────────────────────────────────────────────────

class Handler(BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):  # silence default access log
        pass

    def do_GET(self):
        parsed = urlparse(self.path)
        path = parsed.path
        qs = parse_qs(parsed.query)

        if path == "/":
            self._send(200, "text/html", _HTML.encode())

        elif path == "/api/kpis":
            self._json(_col.get_kpis())

        elif path == "/api/summary":
            self._json(_col.get_summary())

        elif path == "/api/runs":
            limit = int(qs.get("limit", ["50"])[0])
            stage = qs.get("stage", [None])[0]
            self._json(_col.get_runs(limit=limit, stage=stage))

        else:
            self._send(404, "application/json",
                       json.dumps({"error": "not found"}).encode())

    def _send(self, code: int, content_type: str, body: bytes):
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def _json(self, data):
        body = json.dumps(data, default=str).encode()
        self._send(200, "application/json", body)


def main():
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 7700
    print(f"SDLC Observability → http://localhost:{port}")
    print(f"DB: {_col.db_path}")
    print("Ctrl-C to stop.")
    HTTPServer(("", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
