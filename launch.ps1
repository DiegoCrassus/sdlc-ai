# Abre o Cursor com as variáveis do .env carregadas no processo.
# Necessário para que o GitHub MCP leia GITHUB_PERSONAL_ACCESS_TOKEN.
# Uso: .\launch.ps1  (execute na raiz do projeto)

$envFile = Join-Path $PSScriptRoot ".env"

if (-not (Test-Path $envFile)) {
    Write-Error ".env not found at $envFile"
    exit 1
}

foreach ($line in Get-Content $envFile) {
    if ($line -match "^\s*$" -or $line -match "^\s*#") { continue }
    if ($line -match "^\s*([^=]+?)\s*=\s*(.*)\s*$") {
        $key   = $Matches[1].Trim()
        $value = $Matches[2].Trim().Trim('"').Trim("'")
        [System.Environment]::SetEnvironmentVariable($key, $value, "Process")
    }
}

Write-Host "Variáveis do .env carregadas. Abrindo Cursor..."
& cursor .
