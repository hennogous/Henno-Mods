param([Parameter(Mandatory=$true)][string]$OutputRoot)
$ErrorActionPreference = 'Stop'
. (Join-Path $PSScriptRoot 'ae_capture_storage.ps1')
if (Test-Path -LiteralPath $OutputRoot) { throw 'Use a fresh test directory.' }
New-Item -ItemType Directory -Path $OutputRoot | Out-Null
$checks = 0
function Assert-True([bool]$Condition, [string]$Message) {
    if (-not $Condition) { throw $Message }
    $script:checks++
}
foreach ($scriptFile in @(Get-ChildItem -LiteralPath $PSScriptRoot -Filter '*.ps1')) {
    $parseErrors = $null; $tokens = $null
    $null = [Management.Automation.Language.Parser]::ParseFile($scriptFile.FullName, [ref]$tokens, [ref]$parseErrors)
    Assert-True ($parseErrors.Count -eq 0) "Parse failed: $($scriptFile.Name): $parseErrors"
}
Assert-True ((Get-AEDumpSwitch) -eq '-mm') 'Default must be a mini dump.'
Assert-True ((Get-AEDumpSwitch -Mini) -eq '-mm') 'Legacy -Mini must work.'
Assert-True ((Get-AEDumpSwitch -Full) -eq '-ma') 'Explicit full capture must work.'
$rejected = $false
try { Get-AEDumpSwitch -Full -Mini } catch { $rejected = $true }
Assert-True $rejected 'Conflicting sizes must be rejected.'
$source = Join-Path $OutputRoot 'source.log'
$tail = Join-Path $OutputRoot 'tail.log'
[IO.File]::WriteAllBytes($source, [byte[]](0..255) * 4096)
Save-AEFileTail -Source $source -Destination $tail
Assert-True ((Get-Item -LiteralPath $tail).Length -eq 262144) 'Log tail must be bounded.'
Assert-True ([IO.File]::ReadAllBytes($tail)[262143] -eq 255) 'Tail must include latest bytes.'
$bounded = Join-Path $OutputRoot 'bounded.log'
for ($i=0; $i -lt 80; $i++) { Write-AEBoundedLog -Path $bounded -Message ('a' * 32768) }
Assert-True ((Get-Item -LiteralPath $bounded).Length -le 1048576) 'Repeated messages must stay under 1 MiB.'

function New-TestDump([string]$Area, [string]$Name, [int]$Bytes, [int]$Days = 0, [string]$Metadata = '{"Finished":"done"}') {
    $folder = Join-Path (Join-Path $OutputRoot $Area) $Name
    New-Item -ItemType Directory -Path $folder -Force | Out-Null
    if ($Metadata) { $Metadata | Set-Content -LiteralPath (Join-Path $folder 'capture.json') }
    $path = Join-Path $folder 'test.dmp'
    [IO.File]::WriteAllBytes($path, (New-Object byte[] $Bytes))
    (Get-Item -LiteralPath $path).LastWriteTimeUtc = [DateTime]::UtcNow.AddDays(-$Days)
    return $path
}
$old = New-TestDump 'count' 'old' 10 2
$recent = New-TestDump 'count' 'recent' 10 1
Invoke-AEDumpRetention -OutputRoot (Join-Path $OutputRoot 'count') -MaxDumps 1
Assert-True (-not (Test-Path -LiteralPath $old)) 'Count must remove oldest dump.'
Assert-True (Test-Path -LiteralPath $recent) 'Count must preserve newest dump.'
Assert-True (Test-Path -LiteralPath (Join-Path (Split-Path $old) 'capture.json')) 'Metadata must survive.'
Assert-True ((Get-Content -LiteralPath ($old + '.retention.json') -Raw | ConvertFrom-Json).Removed) 'Removal receipt must confirm success.'
$oversize = New-TestDump 'size' 'large' 30
$small = New-TestDump 'size' 'small' 10 1
Invoke-AEDumpRetention -OutputRoot (Join-Path $OutputRoot 'size') -MaxBytes 20
Assert-True (-not (Test-Path -LiteralPath $oversize)) 'Oversize dump must be removed.'
Assert-True (Test-Path -LiteralPath $small) 'Budget must retain a fitting dump.'
$expired = New-TestDump 'age' 'expired' 10 15
Invoke-AEDumpRetention -OutputRoot (Join-Path $OutputRoot 'age')
Assert-True (-not (Test-Path -LiteralPath $expired)) 'Expired dumps must be removed.'
$pin = New-TestDump 'protected' 'pinned' 10 30
'Pinned' | Set-Content -LiteralPath (Join-Path (Split-Path $pin) 'keep-dumps.txt')
$active = New-TestDump 'protected' 'active' 10 30 '{"Finished":null}'
$unknown = New-TestDump 'protected' 'unknown' 10 30 ''
$locked = New-TestDump 'protected' 'locked' 10 30
$handle = [IO.File]::Open($locked, 'Open', 'ReadWrite', 'None')
try { Invoke-AEDumpRetention -OutputRoot (Join-Path $OutputRoot 'protected') -MaxDumps 0 }
finally { $handle.Dispose() }
foreach ($path in @($pin, $active, $unknown, $locked)) {
    Assert-True (Test-Path -LiteralPath $path) "Protected dump removed: $path"
}
[ordered]@{Passed=$true; Checks=$checks; OutputRoot=$OutputRoot} | ConvertTo-Json |
    Tee-Object -FilePath (Join-Path $OutputRoot 'result.json')
