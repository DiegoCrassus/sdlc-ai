# Sincroniza um arquivo markdown do repo para a wiki do Plane.
# Por padrao grava na Wiki do workspace (nao em Pages do projeto).
#
# Uso:
#   .\.sdlc\scripts\plane-sync-wiki-doc.ps1 -DocPath docs/05-roadmap.md
#   .\.sdlc\scripts\plane-sync-wiki-doc.ps1 -DocPath docs/05-roadmap.md -Scope project

param(
    [Parameter(Mandatory = $true)]
    [string]$DocPath,
    [string]$PageName = "",
    [string]$ReplacePageId = "",
    [ValidateSet("workspace", "project")]
    [string]$Scope = "workspace"
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot\_load-env.ps1"

$apiKey = $env:PLANE_API_KEY
$slug   = $env:PLANE_WORKSPACE_SLUG
$base   = if ($env:PLANE_BASE_URL) { $env:PLANE_BASE_URL.TrimEnd("/") } else { "https://api.plane.so" }

$repoRoot = Split-Path (Split-Path $PSScriptRoot -Parent) -Parent
$fullDocPath = if ([System.IO.Path]::IsPathRooted($DocPath)) { $DocPath } else { Join-Path $repoRoot $DocPath }

if (-not (Test-Path $fullDocPath)) {
    Write-Error "Doc not found: $fullDocPath"
}

$relDocPath = $DocPath -replace "\\", "/"
if (-not $PageName) {
    if ($relDocPath -match "05-roadmap") {
        $PageName = "Roadmap - foco Sheet Canvas"
    } else {
        $baseName = [System.IO.Path]::GetFileNameWithoutExtension($fullDocPath)
        $PageName = ($baseName -replace "^(\d+-)", "") -replace "-", " "
        $PageName = (Get-Culture).TextInfo.ToTitleCase($PageName)
    }
}

$headers = @{
    "x-api-key" = $apiKey
    "Accept"    = "application/json"
}

function Invoke-PlaneJson {
    param(
        [string]$Uri,
        [hashtable]$Payload,
        [ValidateSet("Post", "Patch", "Delete", "Get")]
        [string]$Method = "Post"
    )
    $h = $headers.Clone()
    if ($Method -in @("Post", "Patch")) {
        $json = $Payload | ConvertTo-Json -Depth 20 -Compress
        $bytes = [System.Text.Encoding]::UTF8.GetBytes($json)
        $h["Content-Type"] = "application/json; charset=utf-8"
        switch ($Method) {
            "Post"  { return Invoke-RestMethod -Uri $Uri -Headers $h -Method Post -Body $bytes }
            "Patch" { return Invoke-RestMethod -Uri $Uri -Headers $h -Method Patch -Body $bytes }
        }
    }
    if ($Method -eq "Get") { return Invoke-RestMethod -Uri $Uri -Headers $h -Method Get }
    if ($Method -eq "Delete") { return Invoke-RestMethod -Uri $Uri -Headers $h -Method Delete }
}

Write-Host "== Plane wiki sync: $relDocPath (scope=$Scope) =="

$htmlFile = Join-Path $env:TEMP "plane-wiki-sync.html"
& python "$PSScriptRoot\plane_md_to_html.py" $fullDocPath --repo-path $relDocPath -o $htmlFile
if ($LASTEXITCODE -ne 0) { Write-Error "Markdown conversion failed" }
$html = [System.IO.File]::ReadAllText($htmlFile, [System.Text.Encoding]::UTF8)
Remove-Item $htmlFile -ErrorAction SilentlyContinue
Write-Host "Converted markdown to HTML ($($html.Length) chars)"

$project = $null
$projectIdentifier = ""
$listUrl = ""
$detailUrlBase = ""

if ($Scope -eq "workspace") {
    $listUrl = "$base/api/v1/workspaces/$slug/pages/"
    $detailUrlBase = $listUrl
    Write-Host "Target: workspace wiki ($listUrl)"
} else {
    $projectsUrl = "$base/api/v1/workspaces/$slug/projects/"
    $projectsResp = Invoke-RestMethod -Uri $projectsUrl -Headers $headers -Method Get
    $project = @($projectsResp.results)[0]
    if (-not $project) { Write-Error "No projects in workspace '$slug'" }
    $projectIdentifier = $project.identifier
    $listUrl = "$base/api/v1/workspaces/$slug/projects/$($project.id)/pages/"
    $detailUrlBase = $listUrl
    Write-Host "Target: project pages ($listUrl)"
}

$pageId = $ReplacePageId
if (-not $pageId) {
    try {
        $existing = Invoke-PlaneJson -Uri $listUrl -Payload @{} -Method Get
        $match = @($existing.results) | Where-Object { $_.name -eq $PageName } | Select-Object -First 1
        if ($match) { $pageId = $match.id }
    } catch { }
}

$contentPayload = @{
    name = $PageName
    access = 0
    description_html = $html
}

if ($pageId) {
    $detailUrl = "$detailUrlBase$pageId/"
    try {
        $page = Invoke-PlaneJson -Uri $detailUrl -Payload $contentPayload -Method Patch
        Write-Host "Updated page: $($page.name) ($pageId)"
    }
    catch {
        Write-Host "PATCH not available ($($_.Exception.Message)); trying POST replace..."
        $page = Invoke-PlaneJson -Uri $detailUrlBase -Payload $contentPayload -Method Post
        $pageId = $page.id
        Write-Host "Re-created page: $($page.name) ($pageId)"
    }
} else {
    $page = Invoke-PlaneJson -Uri $listUrl -Payload $contentPayload -Method Post
    $pageId = $page.id
    Write-Host "Created page: $($page.name) ($pageId)"
    try {
        $detailUrl = "$detailUrlBase$pageId/"
        Invoke-PlaneJson -Uri $detailUrl -Payload $contentPayload -Method Patch | Out-Null
        Write-Host "PATCH applied (when supported by Plane plan)"
    }
    catch {
        Write-Host "Note: PATCH not supported on this Plane instance (content sent via POST)"
    }
}

$verify = Invoke-PlaneJson -Uri "$detailUrlBase$pageId/" -Payload @{} -Method Get
$htmlLen = if ($verify.description_html) { $verify.description_html.Length } else { 0 }
Write-Host "Verified description_html length: $htmlLen"

$appBase = "https://app.plane.so"
Write-Host ""
Write-Host "=== Done ==="
Write-Host "Doc   : $relDocPath"
Write-Host "Page  : $PageName"
Write-Host "Scope : $Scope"
if ($Scope -eq "workspace") {
    Write-Host "URL   : $appBase/$slug/wiki/$pageId"
    Write-Host "      : $appBase/$slug/pages/$pageId"
} else {
    Write-Host "URL   : $appBase/$slug/projects/$projectIdentifier/pages/$pageId"
}
