[CmdletBinding()]
param([switch]$RefreshArtifacts)

$ErrorActionPreference = 'Stop'
$paperRoot = Split-Path -Parent $PSScriptRoot
$latexArguments = @('-interaction=nonstopmode', '-halt-on-error', '-file-line-error', '-recorder')

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
    if ($RefreshArtifacts) {
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
    }
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_comparator_lineage.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/verify_history_partition.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/verify_recovery_distribution.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_scientific_revision.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_reader_figures.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_evidence_bridge.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_complete_confirmation_tables.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/verify_supplement_examples.py')
    if (Test-Path -LiteralPath 'tables/generated/ei_x02_results.tex') {
        Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/compact_signature_table.py')
    }
    # Revision 2026-11-04: theory figures/macros, then strip internal jargon from every reader-facing source.
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_theory_figures.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_channel_information_figure.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_channel_profile_figure.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_recovery_overview.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_integrity_figure.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/import_allevents.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/import_history_conditioning.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/import_fair_baselines.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/import_second_plant.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/clean_reader_vocabulary.py', '--apply')

    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_recovery_comparison.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_recovery_comparison_figure.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/build_physics_measurement_chain.py')

    Write-Host 'Building the preserved historical technical notes...'
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'historical_notes.tex')
    Invoke-CheckedCommand -Command 'bibtex' -Arguments @('historical_notes')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'historical_notes.tex')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'historical_notes.tex')

    Write-Host 'Building the standalone supplementary material...'
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'supplement.tex')
    Invoke-CheckedCommand -Command 'bibtex' -Arguments @('supplement')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'supplement.tex')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'supplement.tex')

    Write-Host 'Building the standalone main article...'
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'main.tex')
    Invoke-CheckedCommand -Command 'bibtex' -Arguments @('main')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'main.tex')
    Invoke-CheckedCommand -Command 'pdflatex' -Arguments ($latexArguments + 'main.tex')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/verify_protected_figures.py', '--pdf', 'main.pdf')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/verify_protected_event_figure.py')
    # Editorial gate: no code, paths, internal identifiers or archive jargon in the reader PDFs.
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/scan_pdf_text.py', 'main.pdf', 'supplement.pdf')

    foreach ($document in @('main', 'supplement', 'historical_notes')) {
        $log = Get-Content -LiteralPath "$document.log" -Raw
        if ($log -match 'There were undefined references|There were multiply-defined labels|Rerun to get cross-references right') {
            throw "Unresolved LaTeX references in $document.log; review before publishing."
        }
    }
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/publish_manuscript_bundle.py')
    Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/package_submission_sources.py')
    if (Test-Path -LiteralPath 'generated/frozen/ablation_a01_20261102/SUMMARY.csv') {
        Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/prepare_coauthor_brief.py')
        Invoke-CheckedCommand -Command 'python' -Arguments @('-B', 'scripts/package_coauthor_review.py')
    }
    Write-Host 'Article: output/pdf/P07_Event_Attribution_Article.pdf'
    Write-Host 'Supplement: output/pdf/P07_Event_Attribution_Supplement.pdf'
    Write-Host 'Combined review: output/pdf/P07_Event_Attribution_Review_Bundle.pdf'
}
finally {
    Pop-Location
}
