# Convenience job generator for the two approved workshop variants.
[CmdletBinding()]
param(
    [Parameter(Mandatory=$true)][string]$BlendDirectory,
    [Parameter(Mandatory=$true)][string]$Library,
    [Parameter(Mandatory=$true)][string]$OutputDirectory,
    [Parameter(Mandatory=$true)][string]$Blender,
    [string]$Python = 'python',
    [string]$Texconv = 'texconv.exe',
    [string]$ModRoot,
    [switch]$DecodeOnly,
    [switch]$SkipConversion
)
$ErrorActionPreference = 'Stop'
$repo = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '../../../..'))
if (-not $ModRoot) { $ModRoot = Join-Path $repo 'Civ Supply Chains' }
$job = Get-Content (Join-Path $PSScriptRoot 'workshops.example.json') -Raw | ConvertFrom-Json
$job.library = [IO.Path]::GetFullPath($Library)
$job.mod_root = [IO.Path]::GetFullPath($ModRoot)
$job.output = [IO.Path]::GetFullPath($OutputDirectory)
foreach ($entry in @($job.buildings) + @($job.decals)) {
    $entry.blend = [IO.Path]::GetFullPath((Join-Path $BlendDirectory $entry.blend))
}
New-Item -ItemType Directory -Force -Path $job.output | Out-Null
$jobPath = Join-Path $job.output 'job.json'
# UTF8 without BOM works with both Windows PowerShell and Python's JSON reader.
[IO.File]::WriteAllText($jobPath, ($job | ConvertTo-Json -Depth 20), (New-Object Text.UTF8Encoding($false)))
$tool = Join-Path $PSScriptRoot 'export_scene.py'
& $Python $tool decode $jobPath --blender $Blender
if ($LASTEXITCODE -ne 0) { throw "Blender decode failed ($LASTEXITCODE)" }
if ($DecodeOnly) { return }
& $Python $tool build $jobPath
if ($LASTEXITCODE -ne 0) { throw "Asset staging failed or has unresolved placements; read $OutputDirectory/report.json" }
if (-not $SkipConversion) {
    $converter = Join-Path $repo 'project/tools/cn6libs/CN6ToFGX.exe'
    $textureTool = (Get-Command $Texconv -ErrorAction Stop).Source
    & $Python $tool convert $jobPath --converter $converter --texconv $textureTool
    if ($LASTEXITCODE -ne 0) { throw "Windows conversion failed; see $OutputDirectory/logs" }
}
Write-Host "Staged export: $OutputDirectory. Install is a separate export_scene.py install command."
