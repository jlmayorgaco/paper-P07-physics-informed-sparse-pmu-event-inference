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
$loadTangentV2Root = Join-Path $benchmarkRoot "output\load_tangent_v2\results"
$loadBayesV1Root = Join-Path $benchmarkRoot "output\load_bayes_fd_v1\results"
$loadBayesV2Root = Join-Path $benchmarkRoot "output\load_bayes_fd_v2\results"
$global137Root = Join-Path $benchmarkRoot "output\global_137_confirmatory_v1"
$weakResolutionRoot = Join-Path $benchmarkRoot "output\exact_weak_regime_resolution_v2"
$likelihood120Root = Join-Path $benchmarkRoot "output\likelihood_120_contract_v2"
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
    @{ Kind = "report"; Name = "e06e_online_recentering.md" },
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
    @{ Kind = "legacy-figure"; Name = "event_traces.png"; Target = "legacy_event_traces.png" },
    @{ Kind = "load-tangent-v2"; Name = "load_fd_central_operator.npz"; Target = "load_tangent_fd_operator.npz" },
    @{ Kind = "load-tangent-v2"; Name = "load_fd_central_consistency.csv"; Target = "load_tangent_fd_consistency.csv" },
    @{ Kind = "load-tangent-v2"; Name = "load_finite_amplitude_stress.csv"; Target = "load_tangent_finite_stress.csv" },
    @{ Kind = "load-bayes-v1"; Name = "load_bayes_summary.csv"; Target = "load_bayes_v1_summary.csv" },
    @{ Kind = "load-bayes-v1"; Name = "load_bayes_model_comparison.csv"; Target = "load_bayes_v1_model_comparison.csv" },
    @{ Kind = "load-bayes-v1"; Name = "load_calibration.csv"; Target = "load_bayes_v1_calibration.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_bayes_fd_v2_summary.csv"; Target = "load_bayes_v2_summary.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_bayes_dictionary_manifest.csv"; Target = "load_bayes_v2_dictionary_manifest.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_bayes_cal_manifest.csv"; Target = "load_bayes_v2_cal_manifest.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_bayes_dev_manifest.csv"; Target = "load_bayes_v2_dev_manifest.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_bayes_test_manifest.csv"; Target = "load_bayes_v2_test_manifest.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_whitening_model.csv"; Target = "load_bayes_v2_whitening.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_truncation_order.csv"; Target = "load_bayes_v2_truncation_order.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_truncation_dev.csv"; Target = "load_bayes_v2_truncation_dev.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_dev_likelihood_ablation.csv"; Target = "load_bayes_v2_dev_likelihood.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_weak_detection.csv"; Target = "load_bayes_v2_weak_detection.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_weak_localization.csv"; Target = "load_bayes_v2_weak_localization.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_detectability_thresholds.csv"; Target = "load_bayes_v2_detectability.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_predictive_tests.csv"; Target = "load_bayes_v2_predictive_tests.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_finite_calibration.csv"; Target = "load_bayes_v2_finite_calibration.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_selected_likelihood.csv"; Target = "load_bayes_v2_selected_likelihood.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_q_stability.csv"; Target = "load_bayes_v2_q_stability.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_pair_geometry_whitened.csv"; Target = "load_bayes_v2_pair_geometry.csv" },
    @{ Kind = "load-bayes-v2"; Name = "load_pair_confusion.csv"; Target = "load_bayes_v2_pair_confusion.csv" },
    @{ Kind = "global137-result"; Name = "cardinality_summary.csv"; Target = "global137_cardinality_summary.csv" },
    @{ Kind = "global137-result"; Name = "support_summary.csv"; Target = "global137_support_summary.csv" },
    @{ Kind = "global137-result"; Name = "event_detection.csv"; Target = "global137_event_detection.csv" },
    @{ Kind = "global137-result"; Name = "source_inclusion_summary.csv"; Target = "global137_source_inclusion_summary.csv" },
    @{ Kind = "global137-result"; Name = "weak_weak_transition.csv"; Target = "global137_weak_transition.csv" },
    @{ Kind = "global137-result"; Name = "gk_reference_check.csv"; Target = "global137_gk_reference_check.csv" },
    @{ Kind = "global137-result"; Name = "run_manifest.csv"; Target = "global137_run_manifest.csv" },
    @{ Kind = "global137-result"; Name = "retrospective_vs_confirmatory.csv"; Target = "global137_retrospective_comparison.csv" },
    @{ Kind = "global137-result"; Name = "pair_difficulty_atlas.csv"; Target = "global137_pair_difficulty_atlas.csv" },
    @{ Kind = "global137-report"; Name = "global_137_confirmatory_v1.md"; Target = "report_global_137_confirmatory_v1.md" },
    @{ Kind = "weak-resolution-result"; Name = "case_level_predictor_metrics.csv"; Target = "weak_resolution_predictor_metrics.csv" },
    @{ Kind = "weak-resolution-result"; Name = "gamma_horizon_scaling.csv"; Target = "weak_resolution_gamma_scaling.csv" },
    @{ Kind = "weak-resolution-result"; Name = "run_manifest.csv"; Target = "weak_resolution_run_manifest.csv" },
    @{ Kind = "weak-resolution-report"; Name = "exact_weak_regime_resolution_v2.md"; Target = "report_exact_weak_regime_resolution_v2.md" },
    @{ Kind = "likelihood120-result"; Name = "information_growth.csv"; Target = "likelihood120_information_growth.csv" },
    @{ Kind = "likelihood120-result"; Name = "gamma_infinity.csv"; Target = "likelihood120_gamma_infinity.csv" },
    @{ Kind = "likelihood120-result"; Name = "equilibrium_pair_resolvability.csv"; Target = "likelihood120_equilibrium_pairs.csv" },
    @{ Kind = "likelihood120-result"; Name = "runtime_scaling.csv"; Target = "likelihood120_runtime_scaling.csv" },
    @{ Kind = "likelihood120-result"; Name = "t30_backward_compatibility.csv"; Target = "likelihood120_t30_compatibility.csv" },
    @{ Kind = "likelihood120-result"; Name = "model_error_relative_to_margin.csv"; Target = "likelihood120_model_error_margin.csv" },
    @{ Kind = "likelihood120-result"; Name = "physical_manifold_validation_by_horizon.csv"; Target = "likelihood120_physical_validation.csv" },
    @{ Kind = "likelihood120-report"; Name = "likelihood_120_contract_v2.md"; Target = "report_likelihood_120_contract_v2.md" }
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
        "load-tangent-v2" { $loadTangentV2Root }
        "load-bayes-v1" { $loadBayesV1Root }
        "load-bayes-v2" { $loadBayesV2Root }
        "global137-result" { Join-Path $global137Root "results" }
        "global137-report" { Join-Path $global137Root "reports" }
        "weak-resolution-result" { Join-Path $weakResolutionRoot "results" }
        "weak-resolution-report" { Join-Path $weakResolutionRoot "reports" }
        "likelihood120-result" { Join-Path $likelihood120Root "results" }
        "likelihood120-report" { Join-Path $likelihood120Root "reports" }
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
