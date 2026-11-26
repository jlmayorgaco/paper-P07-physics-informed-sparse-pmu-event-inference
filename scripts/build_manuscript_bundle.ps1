[CmdletBinding()]
param([switch]$RefreshArtifacts)

$ErrorActionPreference = 'Stop'
$paperRoot = Split-Path -Parent $PSScriptRoot
Push-Location $paperRoot
try {
    python -B scripts/verify_protected_figures.py
    if ($LASTEXITCODE -ne 0) { throw 'Protected-figure source check failed.' }
    python -B scripts/verify_protected_event_figure.py
    if ($LASTEXITCODE -ne 0) { throw 'Protected event-figure check failed.' }

    $latexArgs = @('-interaction=nonstopmode', '-halt-on-error', '-file-line-error')
    foreach ($document in @('main', 'supplement', 'historical_notes')) {
        & pdflatex @latexArgs "$document.tex" | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "First LaTeX pass failed for $document.tex; see $document.log." }
        & bibtex $document | Out-Null
        if ($LASTEXITCODE -ne 0) { throw "BibTeX failed for $document.tex; see $document.blg." }
        for ($pass = 2; $pass -le 3; $pass++) {
            & pdflatex @latexArgs "$document.tex" | Out-Null
            if ($LASTEXITCODE -ne 0) { throw "LaTeX pass $pass failed for $document.tex; see $document.log." }
        }
    }

    python -B scripts/verify_protected_figures.py --pdf main.pdf
    if ($LASTEXITCODE -ne 0) { throw 'Protected figures are missing from main.pdf.' }
    python -B scripts/verify_protected_event_figure.py
    if ($LASTEXITCODE -ne 0) { throw 'Protected event-figure check failed.' }
    Write-Host 'Built main.pdf, supplement.pdf and historical_notes.pdf.'
}
finally {
    Pop-Location
}
