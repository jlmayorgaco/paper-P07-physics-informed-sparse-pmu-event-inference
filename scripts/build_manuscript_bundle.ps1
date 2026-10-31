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
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/verify_protected_figures.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/verify_protected_event_figure.py')
    Write-Host 'Regenerating deterministic theory checks...'
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/generate_continuous_evidence.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/generate_narrative_artifacts.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_method_architecture.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/generate_shared_review_evidence.py')
    if (Test-Path -LiteralPath 'generated/frozen/ei_x02_20261030/MANIFEST.json') {
        Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_ei_x02_artifacts.py')
    }
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/refresh_narrative_c01.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('scripts/verify_theory_identities.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('scripts/verify_cone_bayes_identities.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('scripts/verify_information_limits.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('scripts/verify_discrepancy_design.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/verify_causal_amplitude_identity.py')

    Write-Host 'Building the standalone supplementary material...'
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'supplement.tex')
    Invoke-CheckedCommand -Command 'bibtex' -Arguments @('supplement')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'supplement.tex')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'supplement.tex')
    Copy-Item -LiteralPath (Join-Path $paperRoot 'supplement.pdf') -Destination $supplementArtifact -Force

    Write-Host 'Building the standalone main article...'
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'main.tex')
    Invoke-CheckedCommand -Command 'bibtex' -Arguments @('main')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'main.tex')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'main.tex')
    Copy-Item -LiteralPath (Join-Path $paperRoot 'main.pdf') -Destination $combinedArtifact -Force
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/export_article_only.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/verify_protected_figures.py', '--pdf', 'main.pdf')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/verify_protected_event_figure.py')

    Write-Host "Standalone supplement: $supplementArtifact"
    Write-Host "Main article (legacy stable filename): $combinedArtifact"
}
finally {
    Pop-Location
}
