# Observe assertion-dialog metadata only. Never operate or dismiss AE windows.
[CmdletBinding()]
param(
    [string]$OutputRoot = "$env:USERPROFILE\Desktop\Codex\AE_Crash_Captures",
    [string]$ProcDump = "$env:USERPROFILE\Desktop\Codex\Tools\ProcDump\procdump64.exe",
    [ValidatePattern('^[A-Za-z0-9_.-]+\.exe$')]
    [string]$ProcessName = 'AssetEditor.exe',
    [switch]$Mini,
    [int]$MaxCaptures = 0
)
$ErrorActionPreference = 'Stop'
$signature = Get-AuthenticodeSignature -LiteralPath $ProcDump
if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'O=Microsoft Corporation') {
    throw 'ProcDump must have a valid Microsoft signature.'
}
Add-Type -TypeDefinition @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;
public class AEAssertWindow {
    public long Handle; public uint ProcessId; public string Title;
}
public static class AEAssertMetadata {
    private delegate bool EnumCallback(IntPtr window, IntPtr data);
    [DllImport("user32.dll")] private static extern bool EnumWindows(EnumCallback callback, IntPtr data);
    [DllImport("user32.dll")] private static extern uint GetWindowThreadProcessId(IntPtr window, out uint process);
    [DllImport("user32.dll", CharSet=CharSet.Unicode)] private static extern int GetWindowText(IntPtr window, StringBuilder title, int capacity);
    public static AEAssertWindow[] Find(uint process) {
        var matches = new List<AEAssertWindow>();
        EnumWindows(delegate(IntPtr window, IntPtr data) {
            uint owner; GetWindowThreadProcessId(window, out owner);
            if (owner != process) return true;
            var title = new StringBuilder(1024); GetWindowText(window, title, title.Capacity);
            if (title.ToString().IndexOf("Assert Failed", StringComparison.OrdinalIgnoreCase) >= 0)
                matches.Add(new AEAssertWindow { Handle=window.ToInt64(), ProcessId=owner, Title=title.ToString() });
            return true;
        }, IntPtr.Zero);
        return matches.ToArray();
    }
}
'@
$mutex = New-Object System.Threading.Mutex($false, "Local\CSC_AE_AssertionCapture_$ProcessName")
$owned = $false
try {
    try { $owned = $mutex.WaitOne(0) }
    catch [System.Threading.AbandonedMutexException] { $owned = $true }
    if (-not $owned) { return }
    New-Item -ItemType Directory -Path $OutputRoot -Force | Out-Null
    $markers = Join-Path $OutputRoot 'assertion-markers'
    New-Item -ItemType Directory -Path $markers -Force | Out-Null
    $status = Join-Path $OutputRoot 'assertion-watcher-status.json'
    $captured = 0
    while (-not (Test-Path -LiteralPath (Join-Path $OutputRoot 'pause-monitoring.txt'))) {
        [ordered]@{Updated=(Get-Date).ToString('o');PID=$PID;Phase='Monitoring assertions';Captures=$captured;ProcessName=$ProcessName} |
            ConvertTo-Json | Set-Content -LiteralPath $status -Encoding UTF8
        foreach ($process in @(Get-Process -Name ([IO.Path]::GetFileNameWithoutExtension($ProcessName)) -ErrorAction SilentlyContinue)) {
            try {
                $started = $process.StartTime.ToUniversalTime().Ticks
                foreach ($window in [AEAssertMetadata]::Find($process.Id)) {
                    $key = "$($process.Id)-$started-$($window.Handle)"
                    $marker = Join-Path $markers ($key + '.json')
                    if (Test-Path -LiteralPath $marker) { continue }
                    $folder = Join-Path $OutputRoot ((Get-Date -Format 'yyyyMMdd_HHmmss') + '_assert_' + $key)
                    New-Item -ItemType Directory -Path $folder | Out-Null
                    $record = [ordered]@{
                        Detected=(Get-Date).ToString('o');ProcessId=$process.Id;ProcessStartTicks=$started
                        WindowHandle=$window.Handle;WindowTitle=$window.Title;Folder=$folder
                        Kind='Assertion memory snapshot; process remains alive';DumpType=$(if ($Mini) {'Mini'} else {'Full'});Completed=$null;DumpBytes=0
                    }
                    $record | ConvertTo-Json | Set-Content -LiteralPath $marker -Encoding UTF8
                    $record | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $folder 'assertion.json') -Encoding UTF8
                    $logs = Join-Path $env:APPDATA 'AssetEditor\1.1\Logs'
                    if (Test-Path -LiteralPath $logs) {
                        Get-ChildItem -LiteralPath $logs -File | Sort-Object LastWriteTime -Descending | Select-Object -First 4 |
                            ForEach-Object { Copy-Item -LiteralPath $_.FullName -Destination $folder -Force -ErrorAction Continue }
                    }
                    $dump = Join-Path $folder 'AE_assertion.dmp'
                    [ordered]@{Updated=(Get-Date).ToString('o');PID=$PID;Phase='Capturing assertion';Captures=$captured;ProcessName=$ProcessName;Folder=$folder} |
                        ConvertTo-Json | Set-Content -LiteralPath $status -Encoding UTF8
                    $arguments = @('-accepteula')
                    if (-not $Mini) { $arguments += '-ma' }
                    $arguments += @([string]$process.Id, ('"' + $dump + '"'))
                    $writer = Start-Process -FilePath $ProcDump -ArgumentList $arguments -WindowStyle Hidden -PassThru -RedirectStandardOutput (Join-Path $folder 'snapshot.log') -RedirectStandardError (Join-Path $folder 'snapshot-errors.log')
                    $writer.WaitForExit()
                    $record.Completed = (Get-Date).ToString('o')
                    $record.ExitCode = $writer.ExitCode
                    if (Test-Path -LiteralPath $dump) { $record.DumpBytes = (Get-Item -LiteralPath $dump).Length }
                    $record | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $folder 'assertion.json') -Encoding UTF8
                    $record | ConvertTo-Json | Set-Content -LiteralPath $marker -Encoding UTF8
                    $captured++
                }
            }
            catch {
                "$(Get-Date -Format o) $($_.ToString())" | Add-Content -LiteralPath (Join-Path $OutputRoot 'assertion-watcher-errors.log')
            }
        }
        if ($MaxCaptures -gt 0 -and $captured -ge $MaxCaptures) { break }
        Start-Sleep -Seconds 2
    }
    [ordered]@{Updated=(Get-Date).ToString('o');PID=$PID;Phase='Stopped';Captures=$captured;ProcessName=$ProcessName} |
        ConvertTo-Json | Set-Content -LiteralPath $status -Encoding UTF8
}
finally {
    if ($owned) { $mutex.ReleaseMutex() }
    $mutex.Dispose()
}
