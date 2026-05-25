# Diagnostico: listar pages do projeto Plane e verificar escrita na wiki.
$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_load-env.ps1"

$apiKey = $env:PLANE_API_KEY
$slug   = $env:PLANE_WORKSPACE_SLUG
$base   = if ($env:PLANE_BASE_URL) { $env:PLANE_BASE_URL.TrimEnd("/") } else { "https://api.plane.so" }
$headers = @{ "x-api-key" = $apiKey; "Accept" = "application/json" }

Write-Host "== Plane wiki diagnostic =="
Write-Host "Workspace: $slug"

$projectsUrl = "$base/api/v1/workspaces/$slug/projects/"
$projects = Invoke-RestMethod -Uri $projectsUrl -Headers $headers -Method Get
foreach ($p in @($projects.results)) {
    Write-Host ""
    Write-Host "Project: $($p.name) ($($p.identifier)) id=$($p.id)"
    Write-Host "  pages_view enabled: $($p.page_view)"

    $pagesUrl = "$base/api/v1/workspaces/$slug/projects/$($p.id)/pages/"
    Write-Host "  GET $pagesUrl"
    try {
        $pagesResp = Invoke-RestMethod -Uri $pagesUrl -Headers $headers -Method Get
        $pageList = @($pagesResp.results)
        Write-Host "  Pages count: $($pageList.Count)"
        foreach ($page in $pageList) {
            Write-Host "    - $($page.name) id=$($page.id)"
            Write-Host "      URL: https://app.plane.so/$slug/projects/$($p.identifier)/pages/$($page.id)"
        }
    }
    catch {
        Write-Host "  LIST FAILED: $($_.Exception.Message)"
        if ($_.ErrorDetails.Message) { Write-Host "  Body: $($_.ErrorDetails.Message)" }
    }
}

# Workspace-level pages (Wiki)
$wsPagesUrl = "$base/api/v1/workspaces/$slug/pages/"
Write-Host ""
Write-Host "Workspace WIKI: GET $wsPagesUrl"
try {
    $wsPages = Invoke-RestMethod -Uri $wsPagesUrl -Headers $headers -Method Get
    $wsList = @($wsPages.results)
    Write-Host "Wiki pages count: $($wsList.Count)"
    foreach ($page in $wsList) {
        Write-Host "  - $($page.name) id=$($page.id)"
        Write-Host "    URL: https://app.plane.so/$slug/wiki/$($page.id)"
    }
}
catch {
    Write-Host "Wiki LIST FAILED: $($_.Exception.Message)"
}

# Known page id from previous sync
$knownId = "530159e5-9192-4595-a6ea-c75867bce6c0"
$projectId = "9441ac9d-c70e-4794-afee-7d23722da2d0"
$detailUrl = "$base/api/v1/workspaces/$slug/projects/$projectId/pages/$knownId/"
Write-Host ""
Write-Host "Fetch known page: $detailUrl"
try {
    $detail = Invoke-RestMethod -Uri $detailUrl -Headers $headers -Method Get
    Write-Host "  Found: $($detail.name)"
    Write-Host "  description_html length: $($detail.description_html.Length)"
    Write-Host "  archived_at: $($detail.archived_at)"
    Write-Host "  access: $($detail.access)"
}
catch {
    Write-Host "  GET FAILED: $($_.Exception.Message)"
    if ($_.ErrorDetails.Message) { Write-Host "  Body: $($_.ErrorDetails.Message)" }
}
