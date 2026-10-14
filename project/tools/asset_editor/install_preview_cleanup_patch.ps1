# Version-locked, reversible fix for orphaned asset previews. Does not start AE.
[CmdletBinding()]
param(
    [ValidateSet('Check','Install','Restore')][string]$Mode = 'Check',
    [Parameter(Mandatory=$true)][string]$PackageDirectory,
    [string]$AssetEditorDirectory = "${env:ProgramFiles(x86)}\Steam\steamapps\common\Sid Meier's Civilization VI SDK\AssetModTools\AssetEditor"
)
$ErrorActionPreference = 'Stop'
$originalHash = 'B1855D6319F0CE804162342252892247FD3540DA25F0F6872D64713F4A38F990'
$patchedHash = '6A897703193D74E86F01AA657F1CA5EA71E8879D5777A2410CEB70DA3868C9BF'
$dllPath = Join-Path $AssetEditorDirectory 'Firaxis.AssetPreviewing.dll'
$originalPath = Join-Path $PackageDirectory 'Firaxis.AssetPreviewing.original.dll'
$patchedPath = Join-Path $PackageDirectory 'Firaxis.AssetPreviewing.patched.dll'
function Assert-Hash([string]$Path, [string]$Expected) {
    $actual = (Get-FileHash -Algorithm SHA256 -LiteralPath $Path).Hash
    if ($actual -ne $Expected) { throw "Unexpected hash for $Path; refusing to overwrite anything." }
}
Assert-Hash $originalPath $originalHash
Assert-Hash $patchedPath $patchedHash
$currentHash = (Get-FileHash -Algorithm SHA256 -LiteralPath $dllPath).Hash
if ($currentHash -notin @($originalHash,$patchedHash)) { throw 'Unsupported installed DLL; no files changed.' }
if ($Mode -eq 'Check') {
    [pscustomobject]@{Path=$dllPath; Patched=($currentHash -eq $patchedHash); AssetEditorRunning=[bool](Get-Process AssetEditor -ErrorAction SilentlyContinue)}
    return
}
if (Get-Process AssetEditor -ErrorAction SilentlyContinue) { throw 'Close Asset Editor first. No files changed.' }
$sourcePath = if ($Mode -eq 'Install') { $patchedPath } else { $originalPath }
$expectedHash = if ($Mode -eq 'Install') { $patchedHash } else { $originalHash }
if ($currentHash -eq $expectedHash) { Write-Output "Already in requested state: $Mode"; return }
# Both source copies are hash-verified before touching the installed DLL.
# A failed copy/verification restores its previous state from the other retained copy.
$previousPath = if ($currentHash -eq $originalHash) { $originalPath } else { $patchedPath }
try {
    if (Get-Process AssetEditor -ErrorAction SilentlyContinue) { throw 'AE started during preparation; no files changed.' }
    Copy-Item -LiteralPath $sourcePath -Destination $dllPath -Force
    Assert-Hash $dllPath $expectedHash
} catch {
    $failure = $_
    if ((Get-FileHash -Algorithm SHA256 -LiteralPath $dllPath).Hash -ne $currentHash) {
        Copy-Item -LiteralPath $previousPath -Destination $dllPath -Force
        Assert-Hash $dllPath $currentHash
    }
    throw $failure
}
$result = [ordered]@{Time=(Get-Date).ToString('o'); Action=$Mode; Path=$dllPath; PreviousSHA256=$currentHash; SHA256=$expectedHash; Backup=$originalPath; RuntimeValidation='Pending manual AE test'}
$result | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $PackageDirectory "$($Mode.ToLowerInvariant())-result.json") -Encoding UTF8
$result | ConvertTo-Json
