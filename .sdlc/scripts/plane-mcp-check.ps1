# Verifica credenciais Plane antes de usar o MCP.
# Uso: . .\.sdlc\scripts\_load-env.ps1; .\.sdlc\scripts\plane-mcp-check.ps1

$ErrorActionPreference = "Stop"

. "$PSScriptRoot\_load-env.ps1"

$apiKey = $env:PLANE_API_KEY
$slug   = $env:PLANE_WORKSPACE_SLUG
$base   = if ($env:PLANE_BASE_URL) { $env:PLANE_BASE_URL.TrimEnd("/") } else { "https://api.plane.so" }

if (-not $apiKey) {
    Write-Error "PLANE_API_KEY not set. Add it to .env - see .sdlc/integrations/plane.md"
}
if (-not $slug) {
    Write-Error "PLANE_WORKSPACE_SLUG not set. Add it to .env - see .sdlc/integrations/plane.md"
}

Write-Host "Checking Plane API at $base ..."
try {
    $response = Invoke-RestMethod -Uri "$base/api/v1/users/me/" -Headers @{ "x-api-key" = $apiKey } -Method Get
    $email = $response.email
    if (-not $email) { $email = $response.display_name }
    Write-Host "OK - authenticated as: $email"
    Write-Host "Workspace slug configured: $slug"
    Write-Host "MCP endpoint: https://mcp.plane.so/http/api-key/mcp"
    Write-Host "Next: restart Cursor via .\launch.ps1 and verify plane MCP is green in Settings."
}
catch {
    Write-Error "Plane API check failed ($($_.Exception.Message)). Verify PLANE_API_KEY and PLANE_BASE_URL."
}
