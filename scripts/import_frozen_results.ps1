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
$destination = Join-Path $paperRoot "generated\frozen"

$sources = @(
    @{ Kind = "result"; Name = "pd_observability_horizons.csv" },
    @{ Kind = "result"; Name = "e04a_b0_b1_b2_summary.csv" },
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
    @{ Kind = "report"; Name = "FINAL_VALIDATION_REPORT.md" },
    @{ Kind = "report"; Name = "e04a_full_validation.md" },
    @{ Kind = "report"; Name = "e04a3_calibration.md" },
    @{ Kind = "report"; Name = "e04a4_colored_discrepancy.md" },
    @{ Kind = "report"; Name = "e04a5_discrepancy_placement.md" },
    @{ Kind = "report"; Name = "e06_standard_validation.md" },
    @{ Kind = "report"; Name = "e06e_breakpoint_audit.md" },
    @{ Kind = "report"; Name = "e06e_online_recentering.md" }
)

New-Item -ItemType Directory -Force -Path $destination | Out-Null
$records = foreach ($source in $sources) {
    $base = switch ($source.Kind) {
        "result" { $resultRoot }
        "report" { $reportRoot }
        "manifest" { $manifestRoot }
        default { throw "Unknown source kind: $($source.Kind)" }
    }
    $sourcePath = Join-Path $base $source.Name
    if (-not (Test-Path -LiteralPath $sourcePath)) {
        throw "Required frozen artifact not found: $sourcePath"
    }
    $targetName = if ($source.Kind -eq "report") { "report_$($source.Name)" } else { $source.Name }
    $targetPath = Join-Path $destination $targetName
    Copy-Item -LiteralPath $sourcePath -Destination $targetPath -Force
    $hash = (Get-FileHash -LiteralPath $targetPath -Algorithm SHA256).Hash.ToLowerInvariant()
    [pscustomobject]@{
        imported_name = $targetName
        source_kind = $source.Kind
        sha256 = $hash
        bytes = (Get-Item -LiteralPath $targetPath).Length
        source_relative_path = [IO.Path]::GetRelativePath($SourceRepository, $sourcePath)
    }
}

$sourceCommit = git -C $SourceRepository rev-parse HEAD
$sourceBranch = git -C $SourceRepository branch --show-current
$sourceRepositoryRelative = [IO.Path]::GetRelativePath($paperRoot, $SourceRepository)
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
