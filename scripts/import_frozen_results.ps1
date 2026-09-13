param(
    [string]$SourceRepository = ""
)

$ErrorActionPreference = "Stop"
$paperRoot = Split-Path -Parent $PSScriptRoot
if ([string]::IsNullOrWhiteSpace($SourceRepository)) {
    $SourceRepository = Join-Path (Split-Path -Parent $paperRoot) "SGSMA26-Physics-Informed-AD"
}
$SourceRepository = [IO.Path]::GetFullPath($SourceRepository)
$benchmarkRoot = Join-Path $SourceRepository "research\pmu_hybrid_dae_bayes\powerdynamics_ieee39"
$resultRoot = Join-Path $benchmarkRoot "output\results"
$reportRoot = Join-Path $benchmarkRoot "output\reports"
$manifestRoot = Join-Path $benchmarkRoot "output\manifests"
$topologyRoot = Join-Path $SourceRepository "data\topology\ieee39"
$legacyEvidenceRoot = Join-Path $SourceRepository "paper_journal\evidence"
$legacyFigureRoot = Join-Path $SourceRepository "paper_journal\figures\journal"
$destination = Join-Path $paperRoot "generated\frozen"

function Get-RelativePathCompat([string]$BasePath, [string]$TargetPath) {
    $baseFull = [IO.Path]::GetFullPath($BasePath).TrimEnd('\') + '\'
    $targetFull = [IO.Path]::GetFullPath($TargetPath)
    $baseUri = [Uri]$baseFull
    $targetUri = [Uri]$targetFull
    return [Uri]::UnescapeDataString($baseUri.MakeRelativeUri($targetUri).ToString()).Replace('/', '\')
}

$sources = @(
    @{ Kind = "result"; Name = "pd_observability_horizons.csv" },
    @{ Kind = "result"; Name = "e04a_b0_b1_b2_summary.csv" },
    @{ Kind = "result"; Name = "e04a_per_case.csv" },
    @{ Kind = "result"; Name = "e04a_paired_comparisons.csv" },
    @{ Kind = "result"; Name = "e04a_b3_summary.csv" },
    @{ Kind = "result"; Name = "e04a_b3_runtime.csv" },
    @{ Kind = "result"; Name = "e04a1_e03_vs_e04.csv" },
    @{ Kind = "result"; Name = "e04a3_test_calibration.csv" },
    @{ Kind = "result"; Name = "e04a3_low_rank_residual.csv" },
    @{ Kind = "result"; Name = "e04a4_test_metrics.csv" },
    @{ Kind = "result"; Name = "e04a5_test_metrics.csv" },
    @{ Kind = "result"; Name = "e06_standard_summary.csv" },
    @{ Kind = "result"; Name = "e06_standard_per_case.parquet" },
    @{ Kind = "result"; Name = "e06_standard_adequacy.csv" },
    @{ Kind = "result"; Name = "e06_standard_oracle_subset.csv" },
    @{ Kind = "result"; Name = "e06e_breakpoints_canonical.csv" },
    @{ Kind = "result"; Name = "e06e_summary.csv" },
    @{ Kind = "result"; Name = "e06e_oracle_closure.csv" },
    @{ Kind = "result"; Name = "e06e_dev_selection.csv" },
    @{ Kind = "result"; Name = "e04a3_cal_split_manifest.csv" },
    @{ Kind = "result"; Name = "e06_standard_manifest.csv" },
    @{ Kind = "result"; Name = "e06_standard_refined_manifest.csv" },
    @{ Kind = "result"; Name = "e06e_dev_manifest.csv" },
    @{ Kind = "result"; Name = "e06e_test_manifest.csv" },
    @{ Kind = "result"; Name = "e06h_summary.csv" },
    @{ Kind = "result"; Name = "e06h_closure.csv" },
    @{ Kind = "result"; Name = "e06h_claim_cleanup.csv" },
    @{ Kind = "result"; Name = "e06h_nominal_control.csv" },
    @{ Kind = "result"; Name = "e06h_identifiability.csv" },
    @{ Kind = "result"; Name = "e06h_rejections.csv" },
    @{ Kind = "result"; Name = "e06h_runtime.csv" },
    @{ Kind = "result"; Name = "e06h_solver_subset.csv" },
    @{ Kind = "result"; Name = "e06h_test_per_case.csv" },
    @{ Kind = "result"; Name = "e06h_uncertainty.csv" },
    @{ Kind = "result"; Name = "e06h_dev_manifest.csv" },
    @{ Kind = "result"; Name = "e06h_dev_selection.csv" },
    @{ Kind = "result"; Name = "e06h_test_manifest.csv" },
    @{ Kind = "data"; Name = "branches_physical.csv" },
    @{ Kind = "report"; Name = "FINAL_VALIDATION_REPORT.md" },
    @{ Kind = "report"; Name = "e04a_full_validation.md" },
    @{ Kind = "report"; Name = "e04a3_calibration.md" },
    @{ Kind = "report"; Name = "e04a4_colored_discrepancy.md" },
    @{ Kind = "report"; Name = "e04a5_discrepancy_placement.md" },
    @{ Kind = "report"; Name = "e06_standard_validation.md" },
    @{ Kind = "report"; Name = "e06e_breakpoint_audit.md" },
    @{ Kind = "report"; Name = "e06e_online_recentering.md" }
    @{ Kind = "report"; Name = "e06h_corrected_m6_static_recentering.md" },
    @{ Kind = "legacy-evidence"; Name = "replayed_summary.csv"; Target = "legacy_replayed_summary.csv" },
    @{ Kind = "legacy-evidence"; Name = "feature_group_ablation_summary.csv"; Target = "legacy_feature_group_ablation_summary.csv" },
    @{ Kind = "legacy-evidence"; Name = "availability_gate_ablation.csv"; Target = "legacy_availability_gate_ablation.csv" },
    @{ Kind = "legacy-evidence"; Name = "paired_intervals_recomputed.csv"; Target = "legacy_paired_intervals_recomputed.csv" },
    @{ Kind = "legacy-evidence"; Name = "descriptor_paired_intervals.csv"; Target = "legacy_descriptor_paired_intervals.csv" },
    @{ Kind = "legacy-evidence"; Name = "pmu_sparsity_ablation.csv"; Target = "legacy_pmu_sparsity_ablation.csv" },
    @{ Kind = "legacy-evidence"; Name = "unseen_sources_recomputed.csv"; Target = "legacy_unseen_sources_recomputed.csv" },
    @{ Kind = "legacy-evidence"; Name = "raw0001_transfer_results.csv"; Target = "legacy_raw0001_transfer_results.csv" },
    @{ Kind = "legacy-evidence"; Name = "raw_event_figure_values.csv"; Target = "legacy_raw_event_figure_values.csv" },
    @{ Kind = "legacy-evidence"; Name = "figure_trace_manifest.json"; Target = "legacy_figure_trace_manifest.json" },
    @{ Kind = "legacy-evidence"; Name = "source_manifest.json"; Target = "legacy_source_manifest.json" },
    @{ Kind = "legacy-figure"; Name = "event_traces.pdf"; Target = "legacy_event_traces.pdf" },
    @{ Kind = "legacy-figure"; Name = "event_traces.png"; Target = "legacy_event_traces.png" }
)

New-Item -ItemType Directory -Force -Path $destination | Out-Null
$records = foreach ($source in $sources) {
    $base = switch ($source.Kind) {
        "result" { $resultRoot }
        "report" { $reportRoot }
        "manifest" { $manifestRoot }
        "data" { $topologyRoot }
        "legacy-evidence" { $legacyEvidenceRoot }
        "legacy-figure" { $legacyFigureRoot }
        default { throw "Unknown source kind: $($source.Kind)" }
    }
    $sourcePath = Join-Path $base $source.Name
    if (-not (Test-Path -LiteralPath $sourcePath)) {
        throw "Required frozen artifact not found: $sourcePath"
    }
    $targetName = if ($source.ContainsKey("Target")) {
        $source.Target
    } elseif ($source.Kind -eq "report") {
        "report_$($source.Name)"
    } else {
        $source.Name
    }
    $targetPath = Join-Path $destination $targetName
    Copy-Item -LiteralPath $sourcePath -Destination $targetPath -Force
    $hash = (Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash.ToLowerInvariant()
    [pscustomobject]@{
        imported_name = $targetName
        source_kind = $source.Kind
        sha256 = $hash
        bytes = (Get-Item -LiteralPath $targetPath).Length
        source_relative_path = Get-RelativePathCompat $SourceRepository $sourcePath
    }
}

$sourceCommit = git -C $SourceRepository rev-parse HEAD
$sourceBranch = git -C $SourceRepository branch --show-current
$sourceRepositoryRelative = Get-RelativePathCompat $paperRoot $SourceRepository
$records | Export-Csv -LiteralPath (Join-Path $destination "SOURCE_MANIFEST.csv") -NoTypeInformation -Encoding utf8

$metadata = @(
    "source_repository_relative=$sourceRepositoryRelative"
    "source_branch=$sourceBranch"
    "source_commit=$sourceCommit"
    "imported_utc=$([DateTime]::UtcNow.ToString('o'))"
    "note=The source working tree contained unrelated and ongoing changes; SHA-256 hashes above identify every imported artifact exactly."
)
Set-Content -LiteralPath (Join-Path $destination "SOURCE_SNAPSHOT.txt") -Value $metadata -Encoding utf8

Write-Host "Imported $($records.Count) frozen artifacts into $destination"
