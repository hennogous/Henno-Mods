param(
    [string]$BlenderVersion = "5.1",
    [switch]$ImportOnly,
    [switch]$ExportOnly
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$addonDir = Join-Path $env:APPDATA "Blender Foundation\Blender\$BlenderVersion\scripts\addons"

$copies = @()
if (-not $ExportOnly) {
    $copies += @{
        Source = Join-Path $scriptDir "io_import_cn6_b4.py"
        Target = Join-Path $addonDir "io_import_cn6.py"
    }
}
if (-not $ImportOnly) {
    $copies += @{
        Source = Join-Path $scriptDir "io_export_cn6_b4.py"
        Target = Join-Path $addonDir "io_export_cn6.py"
    }
}

New-Item -ItemType Directory -Path $addonDir -Force | Out-Null

foreach ($copy in $copies) {
    if (-not (Test-Path -LiteralPath $copy.Source)) {
        throw "Missing source addon: $($copy.Source)"
    }

    Copy-Item -LiteralPath $copy.Source -Destination $copy.Target -Force
    Write-Host "Installed $($copy.Target)"
}

Write-Host "Restart Blender $BlenderVersion, then enable the CivNexus6 import/export addons if they are not already enabled."
