$ErrorActionPreference = "Stop"
. "$PSScriptRoot/_load-env.ps1"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "gh CLI not found."
}

Write-Host "== SDLC issues by label =="
$labels = @("sdlc:intent", "sdlc:spec", "sdlc:implement", "sdlc:ready", "sdlc:blocked")

foreach ($label in $labels) {
    Write-Host "`n--- $label ---"
    gh issue list --label $label --limit 10 2>$null
    if ($LASTEXITCODE -ne 0) {
        Write-Host "(no issues or label not created yet)"
    }
}

Write-Host "`n== Recent workflow runs (sdlc.yml) =="
gh run list --workflow=sdlc.yml --limit 5 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-Host "(workflow not on remote yet)"
}
