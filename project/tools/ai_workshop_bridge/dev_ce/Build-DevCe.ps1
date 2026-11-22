<# Build Cru's Dev CE and stage it under CSC's qualified development identity. #>
[CmdletBinding()]
param(
    [Parameter(Mandatory)][string]$Checkout,
    [Parameter(Mandatory)][string]$VcpkgRoot,
    [Parameter(Mandatory)][string]$OutputDirectory,
    [string]$MSBuild = 'MSBuild.exe'
)
$ErrorActionPreference = 'Stop'
$repo = (Resolve-Path -LiteralPath $Checkout).Path
$output = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($OutputDirectory)
if (Test-Path -LiteralPath $output) { throw "Choose a fresh output directory: $output" }
$vcpkg = (Resolve-Path -LiteralPath (Join-Path $VcpkgRoot 'vcpkg.exe')).Path
$buildTool = (Get-Command -Name $MSBuild -CommandType Application).Source
$project = Join-Path $repo 'CivilizationVI_CommunityExtension/CivilizationVI_CommunityExtension.vcxproj'
$modSource = Join-Path $repo 'dev-ce/mod/DevCE'
$sourceId = '2f6d8f0e-5b9a-4a3e-8c55-7d2b6e1c9a40'
$testId = 'a6ce92d2-7814-473e-b05f-153c1d9c62e6'
$prefix = 'GameCore_XP2_CE'
$testPrefix = 'GameCore_XP2_CE_AI'
$dllName = "${prefix}_FinalRelease.dll"
$testDllName = "${testPrefix}_FinalRelease.dll"
$manifest = [xml](Get-Content -LiteralPath (Join-Path $modSource 'DevCE.modinfo') -Raw)
$selector = Get-Content -LiteralPath (Join-Path $modSource 'Data/Config.sql') -Raw
$dllEntry = $manifest.Mod.SelectSingleNode("Files/File[text()='Binaries/Win64/$dllName']")
if ($manifest.Mod.id -ne $sourceId -or !$dllEntry -or !$selector.Contains($sourceId) -or !$selector.Contains($prefix)) {
    throw 'Dev CE package identity or layout changed'
}

New-Item -ItemType Directory -Path $output | Out-Null
$installed = Join-Path $output 'vcpkg_installed'
$triplet = 'x64-windows-static-md'
& $vcpkg install "--triplet=$triplet" "--x-manifest-root=$PSScriptRoot" "--x-install-root=$installed"
if ($LASTEXITCODE) { throw "vcpkg install failed ($LASTEXITCODE)" }
$dependencies = Join-Path $installed $triplet
$lib = Join-Path $output 'link'
New-Item -ItemType Directory -Path $lib | Out-Null
Copy-Item -LiteralPath (Join-Path $dependencies 'lib/minhook.x64.lib') -Destination (Join-Path $lib 'libMinHook.x64.lib')
$capstone = Join-Path $dependencies 'lib/capstone.lib'
$release = (Join-Path $output 'release').Replace('\','/') + '/'
$objects = (Join-Path $output 'obj').Replace('\','/') + '/'

# The upstream project has a machine-specific OutDir. Pin both output paths
# outside the checkout and link static dependencies against the Release CRT.
$previousCL = $env:CL
$previousLINK = $env:LINK
try {
    $env:CL = "$previousCL /DCAPSTONE_STATIC /I`"$dependencies/include`" /I`"$repo/CivilizationVI_CommunityExtension/include`""
    $env:LINK = "$previousLINK /LIBPATH:`"$lib`" `"$capstone`""
    & $buildTool $project /m /v:minimal /p:Configuration=Release /p:Platform=x64 /p:VcpkgEnabled=false `
        "/p:OutDir=$release" "/p:IntDir=$objects"
    if ($LASTEXITCODE) { throw "Dev CE build failed ($LASTEXITCODE)" }
} finally {
    $env:CL = $previousCL
    $env:LINK = $previousLINK
}

# CSC gates its SQL connectors on a package built with the AI APIs. The
# regular Dev CE release ID can also identify versions without those APIs.
$manifest.Mod.SetAttribute('id', $testId)
$manifest.Mod.Properties.Name = 'Dev CE (CSC development build)'
$manifest.Mod.Properties.Description = 'Built from cru121/civ6-dev-ce for CSC AI development. Enable only one GameCore mod.'
$manifest.Mod.Properties.AffectsSavedGames = '1'
$dllEntry.InnerText = "Binaries/Win64/$testDllName"
$package = Join-Path $output 'Dev CE CSC Development'
foreach ($directory in 'Data','Scripts','Binaries/Win64') {
    New-Item -ItemType Directory -Path (Join-Path $package $directory) -Force | Out-Null
}
[IO.File]::WriteAllText((Join-Path $package 'Data/Config.sql'),
    $selector.Replace($sourceId,$testId).Replace($prefix,$testPrefix), [Text.UTF8Encoding]::new($false))
Copy-Item -LiteralPath (Join-Path $modSource 'Scripts/DevCE_Loaded.lua') -Destination (Join-Path $package 'Scripts/DevCE_Loaded.lua')
Copy-Item -LiteralPath (Join-Path $release $dllName) -Destination (Join-Path $package "Binaries/Win64/$testDllName")
$manifest.Save((Join-Path $package 'DevCE.modinfo'))
$revision = git -C $repo rev-parse HEAD
if ($LASTEXITCODE) { throw 'Unable to record the Dev CE source commit' }
@{
    repository = 'https://github.com/cru121/civ6-dev-ce'
    commit = $revision
    sha256 = (Get-FileHash -Algorithm SHA256 -LiteralPath (Join-Path $package "Binaries/Win64/$testDllName")).Hash.ToLowerInvariant()
} | ConvertTo-Json | Set-Content -LiteralPath (Join-Path $output 'dev-ce-build.json') -Encoding UTF8
Write-Output $package
