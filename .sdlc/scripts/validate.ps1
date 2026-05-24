# SDLC gate — validate + smoke (Windows)
$ErrorActionPreference = "Stop"
$Root = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
Set-Location $Root
. "$PSScriptRoot/_load-env.ps1"

Write-Host "== RPG-OP SDLC validate =="

$rpgOk = $false
if (Get-Command rpg -ErrorAction SilentlyContinue) {
    $rpgOk = $true
    rpg validate specs/
    if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
}
if (-not $rpgOk) {
    $hasDsl = python -c "import rpg_dsl; print('ok')" 2>&1
    if ($hasDsl -match "ok") {
        python -m rpg_dsl._cli validate specs/
        if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
    } else {
        Write-Host "skip: rpg_dsl not installed -- run: pip install -e packages/rpg_dsl"
    }
}

if (Test-Path "backend/.venv/Scripts/python.exe") {
    & backend/.venv/Scripts/python.exe backend/scripts/smoke_test.py
} else {
    Write-Host "skip: backend venv not found"
}

Write-Host "== done =="
