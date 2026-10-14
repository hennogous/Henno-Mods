# Capture one manually reproduced AE crash. Does not launch or operate AE.
[CmdletBinding()]
param(
    [string]$ProcDump = "$env:USERPROFILE\Desktop\Codex\Tools\ProcDump\procdump64.exe",
    [string]$OutputRoot = "$env:USERPROFILE\Desktop\Codex\AE_Crash_Captures",
    [string]$AssetEditorDirectory = "${env:ProgramFiles(x86)}\Steam\steamapps\common\Sid Meier's Civilization VI SDK\AssetModTools\AssetEditor",
    [string]$Note = '',
    [ValidatePattern('^[A-Za-z0-9_.-]+\.exe$')]
    [string]$ProcessName = 'AssetEditor.exe',
    [switch]$Mini,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $ProcDump -PathType Leaf)) {
    throw "ProcDump is missing: $ProcDump. See project/docs/art/asset-editor-crash-diagnostics.md."
}
$signature = Get-AuthenticodeSignature -LiteralPath $ProcDump
if ($signature.Status -ne 'Valid' -or $signature.SignerCertificate.Subject -notmatch 'O=Microsoft Corporation') {
    throw 'ProcDump must have a valid Microsoft signature.'
}
$existing = @(Get-CimInstance Win32_Process -Filter "Name LIKE 'procdump%'" |
    Where-Object { $_.CommandLine -match [regex]::Escape($ProcessName) })
if ($existing.Count) { throw 'An Asset Editor ProcDump capture is already running. Finish or cancel it first.' }
$started = Get-Date
$folder = Join-Path $OutputRoot ($started.ToString('yyyyMMdd_HHmmss') + '_' + [guid]::NewGuid().ToString('N').Substring(0, 6))
$arguments = @('-accepteula')
if (-not $Mini) { $arguments += '-ma' }
$arguments += @('-e', '-g', '-n', '1', '-w', $ProcessName, $folder)
if ($CheckOnly) {
    [pscustomobject]@{ Tool = $ProcDump; Signature = $signature.Status.ToString(); Arguments = $arguments; Output = $folder }
    return
}
New-Item -ItemType Directory -Path $folder | Out-Null
$metadata = [ordered]@{
    Started = $started.ToString('o'); Finished = $null; Note = $Note; ProcessName = $ProcessName
    DumpType = $(if ($Mini) { 'Mini' } else { 'Full' })
    ProcDump = $ProcDump; ProcDumpVersion = (Get-Item -LiteralPath $ProcDump).VersionInfo.FileVersion
    ProcDumpSHA256 = (Get-FileHash -LiteralPath $ProcDump -Algorithm SHA256).Hash
    Arguments = $arguments; ExitCode = $null; Dumps = @(); Binaries = @()
}
foreach ($name in @('AssetEditor.exe', 'Civ6ToolHost_Win64_DX11_Release.dll')) {
    $binary = Join-Path $AssetEditorDirectory $name
    if (Test-Path -LiteralPath $binary -PathType Leaf) {
        $metadata.Binaries += [ordered]@{
            Path = $binary; Version = (Get-Item -LiteralPath $binary).VersionInfo.FileVersion
            SHA256 = (Get-FileHash -LiteralPath $binary -Algorithm SHA256).Hash
        }
    }
}
$metadata | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $folder 'capture.json') -Encoding UTF8
@"
Started: $($started.ToString('o'))
Asset and reproduction steps: $Note

Add the asset name, exact action, whether a clean AE launch was used,
and the last successful asset opened. Keep related source files unchanged
until the dump and relevant source versions have been recorded.
"@ | Set-Content -LiteralPath (Join-Path $folder 'reproduction.txt') -Encoding UTF8

function Save-AELogs([string]$Phase) {
    $destination = Join-Path $folder $Phase
    New-Item -ItemType Directory -Path $destination -Force | Out-Null
    $logs = Join-Path $env:APPDATA 'AssetEditor\1.1\Logs'
    if (Test-Path -LiteralPath $logs) {
        # Keep the latest sessions plus everything written during this capture.
        $all = @(Get-ChildItem -LiteralPath $logs -File | Sort-Object LastWriteTime -Descending)
        $selected = @($all | Select-Object -First 4) + @($all | Where-Object { $_.LastWriteTime -ge $started })
        foreach ($file in ($selected | Sort-Object FullName -Unique)) {
            try { Copy-Item -LiteralPath $file.FullName -Destination $destination -Force }
            catch { $_.ToString() | Add-Content -LiteralPath (Join-Path $folder 'collection-errors.txt') }
        }
    }
}
Save-AELogs 'logs-before'
Write-Host "Capturing one AE crash. Evidence: $folder"
Write-Host 'Launch AE yourself and reproduce the crash. Ctrl+C cancels capture.'
Write-Host 'Full dumps can take several seconds to finish; wait for the completion message.'
try {
    # ProcDump handles Ctrl+C by detaching. Do not add -k or install a global debugger.
    $ErrorActionPreference = 'Continue'
    & $ProcDump @arguments 2>&1 | Tee-Object -FilePath (Join-Path $folder 'procdump.log')
    $metadata.ExitCode = $LASTEXITCODE
}
finally {
    $ErrorActionPreference = 'Continue'
    Save-AELogs 'logs-after'
    $events = @(Get-WinEvent -FilterHashtable @{ LogName = 'Application'; StartTime = $started; Id = 1000, 1001 } -ErrorAction SilentlyContinue |
        Where-Object { $_.Message -match 'AssetEditor|Civ6ToolHost' } |
        Select-Object TimeCreated, Id, ProviderName, Message)
    ConvertTo-Json -InputObject $events -Depth 5 | Set-Content -LiteralPath (Join-Path $folder 'windows-events.json') -Encoding UTF8
    $metadata.Finished = (Get-Date).ToString('o')
    $metadata.Dumps = @(Get-ChildItem -LiteralPath $folder -Filter '*.dmp' | Select-Object Name, Length, LastWriteTime)
    $metadata | ConvertTo-Json -Depth 5 | Set-Content -LiteralPath (Join-Path $folder 'capture.json') -Encoding UTF8
    if ($metadata.Dumps.Count) { Write-Host "Capture saved: $folder" }
    else { Write-Host "No crash dump was captured. Session logs saved: $folder" }
}
