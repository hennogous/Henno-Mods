# Persistent per-user supervisor. The scheduled task launches this hidden.
[CmdletBinding()]
param(
    [string]$OutputRoot = "$env:USERPROFILE\Desktop\Codex\AE_Crash_Captures",
    [string]$ProcDump = "$env:USERPROFILE\Desktop\Codex\Tools\ProcDump\procdump64.exe",
    [ValidatePattern('^[A-Za-z0-9_.-]+\.exe$')]
    [string]$ProcessName = 'AssetEditor.exe',
    [switch]$Mini,
    [int]$MaxSessions = 0
)
$ErrorActionPreference = 'Stop'
$capture = Join-Path $PSScriptRoot 'capture_ae_crash.ps1'
if (-not (Test-Path -LiteralPath $capture)) { throw "Missing capture helper: $capture" }
$mutex = New-Object System.Threading.Mutex($false, "Local\CSC_AE_CrashCapture_$ProcessName")
$owned = $false
try {
    try { $owned = $mutex.WaitOne(0) }
    catch [System.Threading.AbandonedMutexException] { $owned = $true }
    if (-not $owned) { return }
    New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
    $stopFile = Join-Path $OutputRoot 'pause-monitoring.txt'
    $statusPath = Join-Path $OutputRoot 'watcher-status.json'
    $sessions = 0
    function Write-WatcherStatus([string]$Phase, [string]$Detail = '') {
        [ordered]@{
            Updated = (Get-Date).ToString('o'); PID = $PID; ProcessName = $ProcessName
            Phase = $Phase; Detail = $Detail; CompletedSessions = $sessions
            DumpType = $(if ($Mini) { 'Mini' } else { 'Full' })
        } | ConvertTo-Json | Set-Content -LiteralPath $statusPath -Encoding UTF8
    }
    while (-not (Test-Path -LiteralPath $stopFile)) {
        $log = Join-Path $OutputRoot ('watcher-' + (Get-Date -Format 'yyyyMMdd') + '.log')
        try {
            Write-WatcherStatus 'Monitoring' 'ProcDump waits for AE, then captures an unhandled exception.'
            & $capture -ProcDump $ProcDump -OutputRoot $OutputRoot -ProcessName $ProcessName -Mini:$Mini -Note 'Automatic background capture' *>&1 |
                Out-File -LiteralPath $log -Append -Encoding UTF8
            $sessions++
            Write-WatcherStatus 'Rearming'
            if ($MaxSessions -gt 0 -and $sessions -ge $MaxSessions) { break }
            Start-Sleep -Seconds 1
        }
        catch {
            $problem = $_.ToString()
            "$(Get-Date -Format o) $problem" | Out-File -LiteralPath $log -Append -Encoding UTF8
            Write-WatcherStatus 'Retrying' $problem
            Start-Sleep -Seconds 15
        }
    }
    Write-WatcherStatus 'Stopped' 'Paused, or the requested session count completed.'
}
finally {
    if ($owned) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
