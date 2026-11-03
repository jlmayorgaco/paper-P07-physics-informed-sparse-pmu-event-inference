[CmdletBinding()]
param([switch]$Apply)
$ErrorActionPreference = 'Stop'
$closureRoot = Split-Path -Parent $PSScriptRoot
$paperRoot = Split-Path -Parent (Split-Path -Parent $closureRoot)
$scienceRoot = Join-Path (Split-Path -Parent $paperRoot) 'SGSMA26-Physics-Informed-AD'
$a01 = Join-Path $scienceRoot 'experiments/PAPER_ABLATION_A01'
$run = Join-Path $a01 'run'
$import = Join-Path $paperRoot 'generated/frozen/ablation_a01_20261102'
$stage = Join-Path $closureRoot 'staging'
$baseline = Get-Content (Join-Path $closureRoot 'BASELINE_MANIFEST.json') -Raw | ConvertFrom-Json
$baselineHashes = @{}
foreach ($item in $baseline.files) { $baselineHashes[$item.path] = $item.sha256 }
function Get-Hash([string]$Path) { (Get-FileHash -LiteralPath $Path -Algorithm SHA256).Hash.ToLowerInvariant() }
function Assert-Baseline([string]$Relative) {
    if (-not $baselineHashes.ContainsKey($Relative)) { throw "No current source baseline hash recorded for $Relative" }
    $target = Join-Path $paperRoot $Relative
    if ((Get-Hash $target) -ne $baselineHashes[$Relative]) { throw "Active source changed since closure baseline: $Relative" }
}
# This is an explicit finalization command, never a watcher. It is safe to run in check-only mode while A01 is active.
$live = Get-CimInstance Win32_Process | Where-Object { $_.CommandLine -match 'PAPER_ABLATION_A01' }
if ($live) { throw "A01 process/import still active; no files copied. PIDs: $($live.ProcessId -join ', ')" }
$completePath = Join-Path $run 'COMPLETE.json'
$progressPath = Join-Path $run 'PROGRESS.json'
$updatedPath = Join-Path $run 'PAPER_UPDATED.json'
foreach ($p in @($completePath,$progressPath,$updatedPath,(Join-Path $run 'PREDICTIONS_SEAL.json'))) {
    if (-not (Test-Path -LiteralPath $p)) { throw "Missing completion artifact: $p" }
}
$complete = Get-Content $completePath -Raw | ConvertFrom-Json
$progress = Get-Content $progressPath -Raw | ConvertFrom-Json
if ($complete.status -ne 'ALL_INTENDED_ARMS_ACCOUNTED' -or $complete.records -ne 24 -or $complete.arms -ne 4 -or $complete.new_inferences -ne 72 -or $complete.methods_retuned) { throw 'A01 completion fields do not match the frozen 24-record, four-arm, 72-inference contract.' }
if ($progress.stage -ne 'complete') { throw "A01 progress is not complete: $($progress.stage)" }
$parity = Get-Content (Join-Path $a01 'checks/BASELINE_PARITY.json') -Raw | ConvertFrom-Json
if (-not $parity.passed -or $parity.reports -ne 3601 -or -not $parity.events_identical) { throw 'Baseline parity check failed or is incomplete.' }
$auditPath = Join-Path $run 'results/EVALUATION_AUDIT.json'
$audit = Get-Content $auditPath -Raw | ConvertFrom-Json
if ($audit.intended_outputs -ne 96 -or ($audit.available_outputs + $audit.failures) -ne 96 -or -not $audit.prediction_sealed_before_evaluation -or $audit.methods_retuned -or -not $audit.posthoc_existing_C01 -or $audit.raw0002_opened) { throw 'A01 evaluation audit does not satisfy the frozen denominator/seal constraints.' }
$seal = Get-Content (Join-Path $run 'PREDICTIONS_SEAL.json') -Raw | ConvertFrom-Json
if (-not $seal.before_evaluation -or -not $seal.files) { throw 'Prediction seal is absent or not prior to evaluation.' }
foreach ($property in $seal.files.PSObject.Properties) {
    $source = Join-Path $a01 $property.Name
    if (-not (Test-Path -LiteralPath $source) -or (Get-Hash $source) -ne $property.Value) { throw "Prediction seal mismatch: $($property.Name)" }
}
$updated = Get-Content $updatedPath -Raw | ConvertFrom-Json
if (-not $updated.compiled -or $updated.methods_changed_in_C01) { throw 'A01 import build record is absent or records a method change.' }
if ((Get-Hash (Join-Path $paperRoot 'main.pdf')) -ne $updated.article_sha256 -or (Get-Hash (Join-Path $paperRoot 'supplement.pdf')) -ne $updated.supplement_sha256) { throw 'Imported PDFs differ from PAPER_UPDATED hashes; inspect before applying staging.' }
$manifestPath = Join-Path $import 'MANIFEST.json'
$manifest = Get-Content $manifestPath -Raw | ConvertFrom-Json
foreach ($name in @('SUMMARY.csv','PAIRED_INTERVALS.csv','INTERACTION.json','EVALUATION_AUDIT.json','PREDICTIONS_SEAL.json')) {
    $entry = $manifest.$name
    $source = Join-Path $import $name
    if (-not $entry -or -not (Test-Path -LiteralPath $source) -or (Get-Hash $source) -ne $entry.sha256) { throw "Frozen import manifest check failed: $name" }
}
$summary = Import-Csv (Join-Path $import 'SUMMARY.csv')
if ($summary.Count -ne 12) { throw "Unexpected A01 summary shape: $($summary.Count) rows; expected 12 method-by-lane rows." }
Write-Output 'A01 complete, parity/seal/audit/import verified. This script never starts a watcher.'
if (-not $Apply) { Write-Output 'Check-only mode; no files changed. Re-run with -Apply after review to integrate the editorial allowlist.'; exit 0 }
$marker = Join-Path $closureRoot 'A01_STAGING_APPLIED.json'
if (Test-Path -LiteralPath $marker) {
    $prior = Get-Content $marker -Raw | ConvertFrom-Json
    foreach ($rel in $prior.target_hashes.PSObject.Properties.Name) {
        if ((Get-Hash (Join-Path $paperRoot $rel)) -ne $prior.target_hashes.$rel) { throw "Post-integration target changed; refusing idempotent replay: $rel" }
    }
    Write-Output 'Editorial staging already applied with matching hashes; no files changed.'
    exit 0
}
foreach ($rel in @('main.tex','supplement.tex','references.bib','sections/article_intro.tex','sections/article_related.tex','sections/article_method.tex','sections/narrative_protocol.tex','sections/article_recovery_x04.tex','sections/article_ei_x02.tex','supplement/appendix_causal_walkthrough.tex','supplement/appendix_submission_contract.tex','scripts/c01_main_tables.py')) { Assert-Baseline $rel }
$targetHashes = @{}
# Merge only the reviewed abstract and new input lines into the importer-preserved top-level TeX files.
$mainTarget = Join-Path $paperRoot 'main.tex'; $mainStage = Get-Content (Join-Path $stage 'main.tex') -Raw; $main = Get-Content $mainTarget -Raw
$abstract = [regex]::Match($mainStage,'(?s)\\begin\{abstract\}.*?\\end\{abstract\}')
if (-not $abstract.Success) { throw 'Staged abstract block missing.' }
$main = [regex]::Replace($main,'(?s)\\begin\{abstract\}.*?\\end\{abstract\}',$abstract.Value,1)
$anchor = '\input{sections/08c_c01_confirmatory}'
if ($main.Contains('\input{sections/article_closure_results}')) { } elseif (($main.Split($anchor).Count - 1) -eq 1) { $main = $main.Replace($anchor,$anchor+"`r`n\input{sections/article_closure_results}") } else { throw 'Main insertion anchor is not unique.' }
Set-Content -LiteralPath $mainTarget -Value $main -NoNewline -Encoding utf8
$targetHashes['main.tex'] = Get-Hash $mainTarget
$suppTarget = Join-Path $paperRoot 'supplement.tex'; $supp = Get-Content $suppTarget -Raw
if (-not $supp.Contains('\input{supplement/measurement_contract}')) {
    $anchor = '\input{supplement/appendix_causal_walkthrough}'
    if (($supp.Split($anchor).Count - 1) -ne 1) { throw 'Supplement insertion anchor is not unique.' }
    $supp = $supp.Replace($anchor,$anchor+"`r`n\input{supplement/measurement_contract}`r`n\input{supplement/domain_profile}")
}
Set-Content -LiteralPath $suppTarget -Value $supp -NoNewline -Encoding utf8
$targetHashes['supplement.tex'] = Get-Hash $suppTarget
$bibTarget = Join-Path $paperRoot 'references.bib'; $bib = Get-Content $bibTarget -Raw; $bibStage = Get-Content (Join-Path $stage 'references.bib') -Raw
if (-not $bib.Contains('@misc{yang2021particle,')) {
    $entry = [regex]::Match($bibStage,'(?s)@misc\{yang2021particle,.*?\n\}')
    if (-not $entry.Success) { throw 'Verified Yang et al. reference entry missing from staging.' }
    $bib += "`r`n`r`n" + $entry.Value + "`r`n"
}
Set-Content -LiteralPath $bibTarget -Value $bib -NoNewline -Encoding utf8
$targetHashes['references.bib'] = Get-Hash $bibTarget
$existingAllowlist = @('sections/article_intro.tex','sections/article_related.tex','sections/article_method.tex','sections/narrative_protocol.tex','sections/article_recovery_x04.tex','sections/article_ei_x02.tex','supplement/appendix_causal_walkthrough.tex','supplement/appendix_submission_contract.tex','scripts/c01_main_tables.py')
$newAllowlist = @('sections/article_closure_results.tex','supplement/measurement_contract.tex','supplement/domain_profile.tex','tables/generated/closure_restoration.tex','tables/generated/closure_compute_cost.tex','figures/generated/closure_restoration.pdf','figures/generated/closure_restoration.png','generated/closure_analysis/RESTORATION_AUDIT.csv','generated/closure_analysis/RESTORATION_AUDIT.json','generated/closure_analysis/COMPUTE_COST.csv','generated/closure_analysis/COMPUTE_COST.json','generated/closure_analysis/DOMAIN_PROFILE.json')
foreach ($rel in $existingAllowlist) {
    $dst = Join-Path $paperRoot $rel; Copy-Item -LiteralPath (Join-Path $stage $rel) -Destination $dst -Force; $targetHashes[$rel] = Get-Hash $dst
}
foreach ($rel in $newAllowlist) {
    $dst = Join-Path $paperRoot $rel; $src = Join-Path $stage $rel
    if (Test-Path -LiteralPath $dst) { if ((Get-Hash $dst) -ne (Get-Hash $src)) { throw "New destination exists with different content: $rel" } }
    else { New-Item -ItemType Directory -Force -Path (Split-Path -Parent $dst) | Out-Null; Copy-Item -LiteralPath $src -Destination $dst }
    $targetHashes[$rel] = Get-Hash $dst
}
$record = [ordered]@{status='EDITORIAL_STAGING_APPLIED_AFTER_COMPLETE_A01'; applied_local=(Get-Date).ToString('o'); a01_manifest_sha256=(Get-Hash $manifestPath); a01_complete_sha256=(Get-Hash $completePath); target_hashes=$targetHashes}
$record | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath $marker -Encoding utf8
Write-Output 'Editorial staging allowlist applied. Compile, inspect every page, verify protected figures, then package; this script does not compile or publish.'
