# Capture one manually reproduced AE crash. Does not launch or operate AE.
[CmdletBinding()]
param(
    [string]$ProcDump = "$env:USERPROFILE\Desktop\Codex\Tools\ProcDump\procdump64.exe",
    [string]$OutputRoot = "$env:USERPROFILE\Desktop\Codex\AE_Crash_Captures",
    [string]$AssetEditorDirectory = "${env:ProgramFiles(x86)}\Steam\steamapps\common\Sid Meier's Civilization VI SDK\AssetModTools\AssetEditor",
    [string]$Note = '',
    [ValidatePattern('^[A-Za-z0-9_.-]+\.exe$')]
    [string]$ProcessName = 'AssetEditor.exe',
    [switch]$Full,
    [switch]$Mini,
    [switch]$CheckOnly
)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'ae_capture_storage.ps1')
$dumpSwitch = Get-AEDumpSwitch -Full:$Full -Mini:$Mini
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
$arguments = @('-accepteula', $dumpSwitch)
$arguments += @('-e', '-g', '-n', '1', '-w', $ProcessName, $folder)
if ($CheckOnly) {
    [pscustomobject]@{ Tool = $ProcDump; Signature = $signature.Status.ToString(); Arguments = $arguments; Output = $folder }
    return
}
New-Item -ItemType Directory -Path $folder | Out-Null
if ($Full) { 'Explicit manual full capture; excluded from routine retention.' | Set-Content -LiteralPath (Join-Path $folder 'keep-dumps.txt') }
$metadata = [ordered]@{
    Started = $started.ToString('o'); Finished = $null; Note = $Note; ProcessName = $ProcessName
    DumpType = $(if ($Full) { 'Full' } else { 'Mini' })
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
    try { Save-AERecentLogs -Destination $destination }
    catch { Write-AEBoundedLog -Path (Join-Path $folder 'collection-errors.txt') -Message $_.ToString() }
}
Save-AELogs 'logs-before'
Write-Host "Capturing one AE crash. Evidence: $folder"
Write-Host 'Launch AE yourself and reproduce the crash. Ctrl+C cancels capture.'
Write-Host 'Mini dump is the default; use -Full only for a specific heap investigation.'
try {
    # ProcDump handles Ctrl+C by detaching. Do not add -k or install a global debugger.
    $ErrorActionPreference = 'Continue'
    & $ProcDump @arguments 2>&1 | ForEach-Object {
        Write-AEBoundedLog -Path (Join-Path $folder 'procdump.log') -Message $_.ToString()
    }
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
    Invoke-AEDumpRetention -OutputRoot $OutputRoot
    if ($metadata.Dumps.Count) { Write-Host "Capture saved: $folder" }
    else { Write-Host "No crash dump was captured. Session logs saved: $folder" }
}
