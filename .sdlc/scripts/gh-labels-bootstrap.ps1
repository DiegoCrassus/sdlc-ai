param(
    [switch]$DryRun
)

$ErrorActionPreference = "Stop"
. "$PSScriptRoot/_load-env.ps1"

if (-not (Get-Command gh -ErrorAction SilentlyContinue)) {
    Write-Error "gh CLI required."
}

$labels = @(
    @{ name = "sdlc:intent"; color = "0E8A16"; description = "Fase intent" },
    @{ name = "sdlc:spec"; color = "1D76DB"; description = "Spec DSL" },
    @{ name = "sdlc:implement"; color = "FBCA04"; description = "Implementacao" },
    @{ name = "sdlc:eval"; color = "5319E7"; description = "Evals agente" },
    @{ name = "sdlc:ready"; color = "006B75"; description = "Pronto PR" },
    @{ name = "sdlc:blocked"; color = "B60205"; description = "Bloqueado" },
    @{ name = "type:feature"; color = "A2EEEF"; description = "Feature" },
    @{ name = "type:bug"; color = "D93F0B"; description = "Bug" },
    @{ name = "type:spec"; color = "C5DEF5"; description = "Spec" },
    @{ name = "type:agent"; color = "D4C5F9"; description = "Agent" }
)

foreach ($l in $labels) {
    $cmd = "gh label create `"$($l.name)`" --color $($l.color) --description `"$($l.description)`" --force"
    if ($DryRun) {
        Write-Host $cmd
    } else {
        Invoke-Expression $cmd 2>$null
        Write-Host "label: $($l.name)"
    }
}

Write-Host "Done."
