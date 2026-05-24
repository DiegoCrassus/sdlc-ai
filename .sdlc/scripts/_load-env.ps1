# Helper: carrega o .env da raiz do projeto na sessão PowerShell atual.
# Use com: . "$PSScriptRoot/_load-env.ps1"

$envFile = Join-Path (Split-Path (Split-Path $PSScriptRoot -Parent) -Parent) ".env"

if (-not (Test-Path $envFile)) {
    Write-Host "info: .env not found at $envFile (skipping)"
    return
}

foreach ($line in Get-Content $envFile) {
    # ignora linhas vazias e comentários
    if ($line -match "^\s*$" -or $line -match "^\s*#") { continue }

    if ($line -match "^\s*([^=]+?)\s*=\s*(.*)\s*$") {
        $key   = $Matches[1].Trim()
        $value = $Matches[2].Trim().Trim('"').Trim("'")
        [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

Write-Host "info: .env loaded from $envFile"
