# Remove only abandoned disposable per-client Ghidra copies, never the master project.
# Also installed beside launch_mcp.py; startup runs this without restarting active clients.
[CmdletBinding()]
param(
    [string]$SessionRoot = 'C:\Users\Shadow\Desktop\Codex\csc-ghidra-mcp-20261029\sessions',
    [ValidateRange(1, 8760)][int]$MinimumAgeHours = 1,
    [string]$ReceiptDirectory = '',
    [switch]$Apply,
    [switch]$Quiet
)
$ErrorActionPreference = 'Stop'
$mutex = New-Object System.Threading.Mutex($false, 'Local\CSC_GhidraSessionCleanup')
$owned = $false
try {
    try { $owned = $mutex.WaitOne(0) }
    catch [System.Threading.AbandonedMutexException] { $owned = $true }
    if (-not $owned) { return }
    $root = Get-Item -LiteralPath $SessionRoot
    if (-not $root.PSIsContainer -or ($root.Attributes -band [IO.FileAttributes]::ReparsePoint)) { throw 'Sessions root must be a plain directory.' }
    $resolvedRoot = (Resolve-Path -LiteralPath $root.FullName).ProviderPath.TrimEnd('\')
    if ($root.Name -ne 'sessions') { throw 'Expected an explicitly named sessions directory.' }
    $prefix = $resolvedRoot + '\'
    # Fail closed if the full process list cannot be read. PyGhidra embeds its JVM
    # in Python, so inspect Python command lines as well as standalone Java.
    $processes = @(Get-CimInstance Win32_Process -ErrorAction Stop)
    $clients = @($processes | Where-Object { $_.Name -match 'python|java|ghidra' })
    $active = @{}
    foreach ($client in $clients) {
        if (-not $client.CommandLine) { continue }
        $normalized = $client.CommandLine.Replace('/', '\')
        foreach ($match in [regex]::Matches($normalized, [regex]::Escape($prefix) + '([0-9a-f]{32})(?=[\\\s"'']|$)', 'IgnoreCase')) {
            $active[$match.Groups[1].Value.ToLowerInvariant()] = $true
        }
    }
    $cutoff = [DateTime]::UtcNow.AddHours(-$MinimumAgeHours)
    $candidates = @()
    $protected = @()
    foreach ($folder in @(Get-ChildItem -LiteralPath $resolvedRoot -Directory -Force)) {
        $id = $folder.Name.ToLowerInvariant()
        if ($id -notmatch '^[0-9a-f]{32}$') { continue }
        if ($folder.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
        if ($active.ContainsKey($id)) { $protected += $id; continue }
        if ($folder.CreationTimeUtc -ge $cutoff) { continue }
        $resolved = (Resolve-Path -LiteralPath $folder.FullName).ProviderPath
        if (-not $resolved.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase) -or
            (Split-Path -Path $resolved -Parent) -ne $resolvedRoot) { throw 'Unexpected session path.' }
        # This layout is specific to the disposable copies made by this launcher.
        if (-not (Test-Path -LiteralPath (Join-Path $resolved 'project\CSC_Native_AI.gpr') -PathType Leaf) -or
            -not (Test-Path -LiteralPath (Join-Path $resolved 'project\CSC_Native_AI.rep') -PathType Container)) { continue }
        $children = @(Get-ChildItem -LiteralPath $resolved -Recurse -Force)
        if (@($children | Where-Object { $_.Attributes -band [IO.FileAttributes]::ReparsePoint }).Count) { continue }
        $files = @($children | Where-Object { -not $_.PSIsContainer })
        $candidates += [pscustomobject][ordered]@{Session=$id;Path=$resolved;Bytes=[long](($files | Measure-Object Length -Sum).Sum);Files=$files.Count;Removed=$false}
    }
    $result = [ordered]@{
        Started=[DateTime]::UtcNow.ToString('o');Applied=[bool]$Apply;MinimumAgeHours=$MinimumAgeHours
        ActiveSessions=$protected;Candidates=$candidates.Count
        CandidateBytes=[long](($candidates | Measure-Object Bytes -Sum).Sum)
        RemovedSessions=0;RemovedBytes=[long]0;Entries=$candidates;Errors=@()
    }
    $receiptPath = $null
    if ($Apply) {
        if (-not $ReceiptDirectory) { $ReceiptDirectory = Join-Path (Split-Path $resolvedRoot -Parent) 'storage-cleanup-receipts' }
        New-Item -ItemType Directory -Path $ReceiptDirectory -Force | Out-Null
        $receiptPath = Join-Path $ReceiptDirectory ('cleanup-' + (Get-Date -Format 'yyyyMMdd_HHmmss_fff') + '-' + $PID + '.json')
        $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
        foreach ($entry in $candidates) {
            try {
                # The final resolved target is checked immediately before recursive
                # deletion. No source/master directory can pass this boundary.
                $target = (Resolve-Path -LiteralPath $entry.Path).ProviderPath
                if ((Split-Path -Path $target -Parent) -ne $resolvedRoot -or
                    -not $target.StartsWith($prefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Unsafe final target.' }
                if ((Get-Item -LiteralPath $target).Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Session became a link.' }
                Remove-Item -LiteralPath $target -Recurse -Force -ErrorAction Stop
                $entry.Removed = $true
                $result.RemovedSessions++
                $result.RemovedBytes += $entry.Bytes
            }
            catch { $result.Errors += [ordered]@{Session=$entry.Session;Error=$_.ToString()} }
            $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
        }
        $result.Finished = [DateTime]::UtcNow.ToString('o')
        $result | ConvertTo-Json -Depth 6 | Set-Content -LiteralPath $receiptPath -Encoding UTF8
    }
    if (-not $Quiet) {
        [ordered]@{Candidates=$result.Candidates;CandidateGiB=[Math]::Round($result.CandidateBytes/1GB,3);
            ActivePreserved=$protected.Count;RemovedSessions=$result.RemovedSessions;
            ReclaimedGiB=[Math]::Round($result.RemovedBytes/1GB,3);Errors=$result.Errors;Receipt=$receiptPath} | ConvertTo-Json -Depth 4
    }
}
finally {
    if ($owned) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
