param(
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [int]$Issue = 0,
    [string]$BodyFile = ""
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/_load-env.ps1"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "gh CLI not found."
}

$body = ""
if ($BodyFile -and (Test-Path $BodyFile)) {
    $body = Get-Content $BodyFile -Raw
} else {
    $body = @"
## Summary

<!-- o que mudou -->

## SDLC checklist

- [ ] Spec em ``specs/`` (se contrato/agente/canvas)
- [ ] ``.sdlc/scripts/validate.ps1`` verde
- [ ] Sem edição manual em ``generated/``

"@
}

if ($Issue -gt 0) {
    $body += "`n`nCloses #$Issue"
}

$tmp = New-TemporaryFile
Set-Content -Path $tmp.FullName -Value $body -Encoding utf8
try {
    gh pr create --title $Title --body-file $tmp.FullName
} finally {
    Remove-Item $tmp.FullName -Force -ErrorAction SilentlyContinue
}
