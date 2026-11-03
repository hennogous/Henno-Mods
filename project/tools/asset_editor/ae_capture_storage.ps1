# Shared, deliberately bounded storage for the two AE capture monitors (PowerShell 5.1).
function Get-AEDumpHeader([string]$Path) {
    $stream = [IO.File]::Open($Path, 'Open', 'Read', 'Read')
    try {
        $header = New-Object byte[] 32
        if ($stream.Read($header, 0, 32) -ne 32 -or [Text.Encoding]::ASCII.GetString($header, 0, 4) -ne 'MDMP') { throw "Invalid dump header: $Path" }
        $flags = [BitConverter]::ToUInt64($header, 24)
        return [pscustomobject]@{Flags=$flags; FullMemory=[bool]($flags -band 2)}
    }
    finally { $stream.Dispose() }
}

function Get-AEDumpSwitch([switch]$Full, [switch]$Mini) {
    if ($Full -and $Mini) { throw 'Choose either -Full or -Mini.' }
    if ($Full) { return '-ma' }
    return '-mm'
}

function Save-AEFileTail {
    param([string]$Source, [string]$Destination, [int]$MaxBytes = 262144)
    $inputStream = [IO.File]::Open($Source, 'Open', 'Read', 'ReadWrite')
    try {
        $count = [int][Math]::Min($MaxBytes, $inputStream.Length)
        $null = $inputStream.Seek(-$count, 'End')
        $buffer = New-Object byte[] $count
        $read = 0
        while ($read -lt $count) {
            $next = $inputStream.Read($buffer, $read, $count - $read)
            if ($next -eq 0) { break }
            $read += $next
        }
        $outputStream = [IO.File]::Open($Destination, 'Create', 'Write', 'Read')
        try { $outputStream.Write($buffer, 0, $read) }
        finally { $outputStream.Dispose() }
    }
    finally { $inputStream.Dispose() }
}

function Save-AERecentLogs([string]$Destination) {
    $logs = Join-Path $env:APPDATA 'AssetEditor\1.1\Logs'
    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    if (-not (Test-Path -LiteralPath $logs)) { return }
    $inventory = @()
    foreach ($file in @(Get-ChildItem -LiteralPath $logs -File |
            Sort-Object LastWriteTime -Descending | Select-Object -First 2)) {
        Save-AEFileTail -Source $file.FullName -Destination (Join-Path $Destination $file.Name)
        $inventory += [ordered]@{Name=$file.Name; OriginalBytes=$file.Length; TailBytes=[Math]::Min(262144,$file.Length)}
    }
    ConvertTo-Json -InputObject $inventory | Set-Content -LiteralPath (Join-Path $Destination 'log-tails.json') -Encoding UTF8
}

function Write-AEBoundedLog([string]$Path, [string]$Message) {
    # Exception chatter must not turn a long-running debug session into a huge log.
    if ($Message.Length -gt 32768) { $Message = $Message.Substring($Message.Length - 32768) }
    if ((Test-Path -LiteralPath $Path) -and (Get-Item -LiteralPath $Path).Length -gt 983040) {
        $temporary = $Path + '.tail'
        Save-AEFileTail -Source $Path -Destination $temporary -MaxBytes 524288
        [IO.File]::Copy($temporary, $Path, $true)
        Remove-Item -LiteralPath $temporary
    }
    [IO.File]::AppendAllText($Path, $Message + [Environment]::NewLine, [Text.UTF8Encoding]::new($false))
}

function Invoke-AEDumpRetention {
    param(
        [string]$OutputRoot,
        [int]$MaxDumps = 10,
        [long]$MaxBytes = 536870912,
        [int]$MaxAgeDays = 14
    )
    # Only completed, recognized capture folders directly below this root qualify.
    # Never recurse through junctions, delete evidence folders, or touch an active dump.
    $rootItem = Get-Item -LiteralPath $OutputRoot
    if ($rootItem.Attributes -band [IO.FileAttributes]::ReparsePoint) { throw 'Retention root cannot be a link.' }
    $rootPrefix = $rootItem.FullName.TrimEnd('\') + '\'
    $mutex = New-Object Threading.Mutex($false, 'Local\CSC_AE_DumpRetention')
    $owned = $false
    try {
        try { $owned = $mutex.WaitOne(0) }
        catch [Threading.AbandonedMutexException] { $owned = $true }
        if (-not $owned) { return }
        $dumps = @()
        foreach ($folder in @(Get-ChildItem -LiteralPath $OutputRoot -Directory)) {
            if ($folder.Attributes -band [IO.FileAttributes]::ReparsePoint) { continue }
            if (-not $folder.FullName.StartsWith($rootPrefix, [StringComparison]::OrdinalIgnoreCase)) { throw 'Capture outside retention root.' }
            if (Test-Path -LiteralPath (Join-Path $folder.FullName 'keep-dumps.txt')) { continue }
            $completed = $false
            foreach ($metadataName in @('capture.json', 'assertion.json')) {
                $metadataPath = Join-Path $folder.FullName $metadataName
                if (-not (Test-Path -LiteralPath $metadataPath)) { continue }
                try {
                    $record = Get-Content -LiteralPath $metadataPath -Raw | ConvertFrom-Json
                    if ($record.Finished -or $record.Completed) { $completed = $true }
                }
                catch { continue }
            }
            if (-not $completed) { continue }
            $dumps += @(Get-ChildItem -LiteralPath $folder.FullName -File -Filter '*.dmp' |
                Where-Object { -not ($_.Attributes -band [IO.FileAttributes]::ReparsePoint) })
        }
        [long]$keptBytes = 0
        $keptCount = 0
        foreach ($dump in @($dumps | Sort-Object LastWriteTimeUtc -Descending)) {
            $reason = ''
            if ($dump.LastWriteTimeUtc -lt [DateTime]::UtcNow.AddDays(-$MaxAgeDays)) { $reason = 'Age' }
            elseif ($keptCount -ge $MaxDumps) { $reason = 'Count' }
            elseif ($keptBytes + $dump.Length -gt $MaxBytes) { $reason = 'Bytes' }
            if (-not $reason) { $keptCount++; $keptBytes += $dump.Length; continue }
            try {
                # ProcDump opens its output without sharing: a failed open means skip it.
                $handle = [IO.File]::Open($dump.FullName, 'Open', 'ReadWrite', 'None')
                $handle.Dispose()
                $receipt = [ordered]@{RemovedAt=[DateTime]::UtcNow.ToString('o'); Name=$dump.Name; Bytes=$dump.Length; Reason=$reason}
                # Record intent before removal; mark completion only after removal succeeds.
                $receiptPath = Join-Path $dump.DirectoryName ($dump.Name + '.retention.json')
                $receipt | ConvertTo-Json | Set-Content -LiteralPath $receiptPath -Encoding UTF8
                Remove-Item -LiteralPath $dump.FullName -ErrorAction Stop
                $receipt.Removed = $true
                $receipt | ConvertTo-Json | Set-Content -LiteralPath $receiptPath -Encoding UTF8
            }
            catch { Write-AEBoundedLog -Path (Join-Path $OutputRoot 'retention-errors.log') -Message $_.ToString() }
        }
    }
    finally {
        if ($owned) { $mutex.ReleaseMutex() }
        $mutex.Dispose()
    }
}
