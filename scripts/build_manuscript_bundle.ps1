[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$paperRoot = Split-Path -Parent $PSScriptRoot
$supplementArtifact = Join-Path $paperRoot 'output\pdf\P07_Physics_Informed_State_Reconstruction_Event_Source_Inference_Supplement.pdf'
$combinedArtifact = Join-Path $paperRoot 'output\pdf\P07_Physics_Informed_State_Reconstruction_Event_Source_Inference.pdf'
$latexArguments = @('-interaction=nonstopmode', '-halt-on-error')

function Invoke-CheckedCommand {
    param(
        [Parameter(Mandatory = $true)][string]$Command,
        [Parameter(Mandatory = $true)][string[]]$Arguments
    )

    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "$Command failed with exit code $LASTEXITCODE."
    }
}

Push-Location $paperRoot
try {
    Write-Host 'Building the standalone supplementary material...'
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'supplement.tex')
    Invoke-CheckedCommand -Command 'bibtex' -Arguments @('supplement')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'supplement.tex')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'supplement.tex')
    Copy-Item -LiteralPath (Join-Path $paperRoot 'supplement.pdf') -Destination $supplementArtifact -Force

    Write-Host 'Building the main article followed by the supplementary material...'
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'main.tex')
    Invoke-CheckedCommand -Command 'bibtex' -Arguments @('main')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'main.tex')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'main.tex')
    Copy-Item -LiteralPath (Join-Path $paperRoot 'main.pdf') -Destination $combinedArtifact -Force

    Write-Host "Standalone supplement: $supplementArtifact"
    Write-Host "Combined article and supplement: $combinedArtifact"
}
finally {
    Pop-Location
}
