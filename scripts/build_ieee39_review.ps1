[CmdletBinding()]
param()
$ErrorActionPreference = 'Stop'
$paperRoot = Split-Path -Parent $PSScriptRoot
function Invoke-Checked {
    param([string]$Command, [string[]]$Arguments)
    & $Command @Arguments
    if ($LASTEXITCODE -ne 0) { throw "$Command failed with exit code $LASTEXITCODE" }
}
Push-Location $paperRoot
try {
    Invoke-Checked 'python' @('-B', 'scripts/verify_protected_figures.py')
    # Rebuild the figure; retain the existing scientific result artifacts.
    Invoke-Checked 'python' @('-B', 'scripts/build_ieee39_tikz.py')
    Invoke-Checked 'python' @('-B', 'scripts/build_method_architecture.py')
    $latexArgs = @('-interaction=nonstopmode', '-halt-on-error', '-recorder', 'main.tex')
    Invoke-Checked 'pdflatex' $latexArgs
    Invoke-Checked 'bibtex' @('main')
    Invoke-Checked 'pdflatex' $latexArgs
    Invoke-Checked 'pdflatex' $latexArgs
    Invoke-Checked 'python' @('-B', 'scripts/verify_protected_figures.py', '--pdf', 'main.pdf')
    Copy-Item -LiteralPath main.pdf -Destination output/pdf/P07_Event_Attribution_Article.pdf -Force
    Copy-Item -LiteralPath main.pdf -Destination output/pdf/P07_Physics_Informed_State_Reconstruction_Event_Source_Inference.pdf -Force
    Write-Host 'Article: output/pdf/P07_Event_Attribution_Article.pdf'
    Write-Host 'Figure: figures/generated/narrative_topology.pdf'
}
finally { Pop-Location }
