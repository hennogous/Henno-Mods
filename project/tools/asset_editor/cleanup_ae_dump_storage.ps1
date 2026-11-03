# Remove full-memory dumps under the named Codex output root. Preview unless -Apply.
param(
    [string]$CodexRoot = "$env:USERPROFILE\Desktop\Codex",
    [switch]$Apply
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'ae_capture_storage.ps1')
$codexItem = Get-Item -LiteralPath $CodexRoot
if ($codexItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Codex root cannot be a link.' }
$prefix = $codexItem.FullName.TrimEnd('\') + '\'
$dumps = @()
$retained = @()
foreach ($dump in @(Get-ChildItem -LiteralPath $CodexRoot -Recurse -File -Filter '*.dmp')) {
    if ($dump.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
    try { $header = Get-AEDumpHeader -Path $dump.FullName }
    catch { continue } # Invalid/incomplete files are never cleanup candidates.
    if ($header.FullMemory) { $dumps += $dump }
    else { $retained += $dump }
}
$remove = $dumps
$report = [ordered]@{
    Applied=$false; Date=[DateTime]::UtcNow.ToString('o')
    RetainedMiniCount=$retained.Count
    RemoveCount=$remove.Count; RemoveBytes=($remove | Measure-Object Length -Sum).Sum
    Removed=@(); SummaryErrors=@()
}
if (-not $Apply) { $report | ConvertTo-Json -Depth 5; return }
$receiptDir = Join-Path $CodexRoot ('AE-storage-cleanup-' + (Get-Date -Format 'yyyyMMdd_HHmmss'))
New-Item -ItemType Directory -Path $receiptDir | Out-Null
foreach ($dump in $dumps) {
    # Resolve and validate each individual file; delete no directories or source assets.
    $resolved = (Resolve-Path -LiteralPath $dump.FullName).ProviderPath
    if (-not $resolved.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) -or [IO.Path]::GetExtension($resolved) -ne '.dmp') { throw 'Unsafe dump path.' }
    $ancestor = $dump.Directory
    while ($ancestor.FullName -ne $codexItem.FullName) {
        if ($ancestor.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Dump has a linked parent directory.' }
        $ancestor = $ancestor.Parent
        if ($null -eq $ancestor) { throw 'Dump is outside output root.' }
    }
    if (-not (Get-AEDumpHeader -Path $resolved).FullMemory) { throw 'Dump changed; preserving it.' }
    $handle = [IO.File]::Open($resolved, 'Open', 'ReadWrite', 'None')
    $handle.Dispose()
    $summary = $resolved + '.stack-summary.json'
    & py -3 (Join-Path $PSScriptRoot 'summarize_ae_dump.py') $resolved 2>&1 |
        Out-File -LiteralPath $summary -Encoding UTF8
    if ($LASTEXITCODE -ne 0) {
        $report.SummaryErrors += $resolved
        throw "Could not summarize $resolved; original preserved."
    }
    $entry = [ordered]@{Path=$resolved;Bytes=$dump.Length;Summary=$summary;Removed=$false}
    $entry | ConvertTo-Json | Set-Content -LiteralPath ($resolved + '.cleanup.json') -Encoding UTF8
    Remove-Item -LiteralPath $resolved -ErrorAction Stop
    $entry.Removed = $true
    $entry | ConvertTo-Json | Set-Content -LiteralPath ($resolved + '.cleanup.json') -Encoding UTF8
    $report.Removed += $entry
    $report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $receiptDir 'cleanup.json') -Encoding UTF8
}
$report.Applied = $true
$report | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath (Join-Path $receiptDir 'cleanup.json') -Encoding UTF8
[ordered]@{Receipt=$receiptDir;RemovedCount=$report.Removed.Count;RemovedGiB=[Math]::Round($report.RemoveBytes/1GB,3);RetainedMiniCount=$report.RetainedMiniCount} | ConvertTo-Json -Depth 4
