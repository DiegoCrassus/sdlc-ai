param(
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [string]$BodyFile = "",
    [string[]]$Labels = @("sdlc:intent", "type:feature")
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/_load-env.ps1"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "gh CLI not found. Install: https://cli.github.com/"
}

$labelArgs = $Labels | ForEach-Object { "--label", $_ }

if ($BodyFile -and (Test-Path $BodyFile)) {
    & gh issue create --title $Title --body-file $BodyFile @labelArgs
} else {
    & gh issue create --title $Title --body "SDLC intent — fill template in follow-up." @labelArgs
}

Write-Host "Issue created."
