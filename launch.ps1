# Abre o Cursor com as variáveis do .env carregadas no processo.
# Necessário para GitHub, Plane e Supabase MCP.
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

# gh CLI usa GH_TOKEN — aponta para o classic PAT
$classic = [System.Environment]::GetEnvironmentVariable("GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC", "Process")
if ($classic) {
    [System.Environment]::SetEnvironmentVariable("GH_TOKEN", $classic, "Process")
}

Write-Host "Variáveis do .env carregadas. Abrindo Cursor..."
& cursor .
