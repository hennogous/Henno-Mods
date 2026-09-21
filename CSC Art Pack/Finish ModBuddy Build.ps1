param(
    [Parameter(Mandatory = $true)]
    [string]$BuiltModPath
)

$artDefPath = Join-Path $BuiltModPath 'ArtDefs\CSC_ArtPack_Landmarks.artdef'
$depPath = Join-Path $BuiltModPath 'CSC_Art_Pack.dep'
$modInfoPath = Join-Path $BuiltModPath 'CSC Art Pack.modinfo'
$tilebasePath = Join-Path $BuiltModPath 'Platforms\Windows\BLPs\Landmarks\CSC_ArtPack_Tilebases.blp'
$sharedDataPath = Join-Path $BuiltModPath 'Platforms\Windows\BLPs\SHARED_DATA'
if (-not (Test-Path -LiteralPath $artDefPath -PathType Leaf)) {
    throw "Built ArtDef not found: $artDefPath"
}
if (-not (Test-Path -LiteralPath $depPath -PathType Leaf)) {
    throw "Built art dependency file not found: $depPath"
}
if (-not (Test-Path -LiteralPath $modInfoPath -PathType Leaf)) {
    throw "Built modinfo not found: $modInfoPath"
}
foreach ($relativePath in @(
    'ArtDefs\CSC_GamePropertyRanges.artdef',
    'Data\CSC_ArtPack_Properties.sql',
    'Lua_UI\ArtProperties\CSC_ArtProperties.lua'
)) {
    $sourcePath = Join-Path $BuiltModPath $relativePath
    if (-not (Test-Path -LiteralPath $sourcePath -PathType Leaf)) {
        throw "The Art Pack build is missing $relativePath. Rebuild in ModBuddy."
    }
}
if (-not (Test-Path -LiteralPath $tilebasePath -PathType Leaf) -or
    (Get-Item -LiteralPath $tilebasePath -ErrorAction SilentlyContinue).Length -eq 0) {
    throw 'The cooked Art Pack tilebase is missing or empty. Rebuild in ModBuddy and check its cooker output.'
}
$cookedTilebases = [System.Text.Encoding]::ASCII.GetString([System.IO.File]::ReadAllBytes($tilebasePath))
foreach ($asset in @(
    'CSC_BAKERS_Wind_Mill_2',
    'CSC_BAKERS_Water_Mill_2',
    'CSC_BAKERS_Bakery_2',
    'CSC_BAKERS_Cafe_2',
    'CSC_TAILORS_Textile_Workshop_2',
    'CSC_TAILORS_Tailor_2'
)) {
    if (-not $cookedTilebases.Contains($asset)) {
        throw "The cooked Art Pack tilebase is missing '$asset'. Check the ModBuddy cooker output."
    }
}
foreach ($name in @(
    'TEXTURE_DiffuseTint_CSC_Atlas_B_BAKERS_2_null',
    'TEXTURE_CSC_Atlas_G_2',
    'TEXTURE_CSC_Atlas_M_2'
)) {
    $texturePath = Join-Path $sharedDataPath $name
    if (-not (Test-Path -LiteralPath $texturePath -PathType Leaf) -or
        (Get-Item -LiteralPath $texturePath -ErrorAction SilentlyContinue).Length -eq 0) {
        throw "The cooked Art Pack texture '$name' is missing or empty. Rebuild in ModBuddy and check its cooker output."
    }
}
$modInfo = [System.IO.File]::ReadAllText($modInfoPath)
if (-not $modInfo.Contains('d96a046a-ce49-4701-94cf-e22d431f5ff4') -or
    -not $modInfo.Contains('<File>CSC_Art_Pack.dep</File>') -or
    -not $modInfo.Contains('CSC_ArtPack_Properties.sql') -or
    -not $modInfo.Contains('CSC_ArtProperties.lua')) {
    throw 'The selected folder does not contain the expected CSC Art Pack build'
}

$document = [System.Xml.XmlDocument]::new()
$document.PreserveWhitespace = $true
$document.Load($artDefPath)
$expectedVariants = @{
    '01 Ancient: Wind Mill 2' = 'BUILDING_CSC_BAKERS_WIND_MILL'
    '01 Ancient: Water Mill 2' = 'BUILDING_CSC_BAKERS_WATER_MILL'
    '02 Medieval: Bakery 2' = 'BUILDING_CSC_BAKERS_BAKERY'
    '03 Renaissance: Cafe 2' = 'BUILDING_CSC_BAKERS_CAFE'
    '01 Classical: Textile Workshop 2' = 'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'
    '02 Medieval: Tailor 2' = 'BUILDING_CSC_TAILORS_TAILOR'
}
foreach ($name in $expectedVariants.Keys) {
    $variant = $document.SelectSingleNode("//Element[m_Name[@text='$name']]")
    if ($null -eq $variant) {
        throw "The cooked ArtDef is missing variant '$name'. Rebuild in ModBuddy."
    }
    $reference = $variant.SelectSingleNode('./m_Fields/m_Values/Element[m_ParamName[@text="Tag_HeroBuilding"]]')
    if ($null -eq $reference) {
        throw "The cooked variant '$name' has no building reference."
    }
    $building = $reference.SelectSingleNode('m_ElementName')
    $artDef = $reference.SelectSingleNode('m_ArtDefPath')
    $expectedBuilding = $expectedVariants[$name]
    if ($building.GetAttribute('text') -notin @('DEFAULT', $expectedBuilding) -or
        $artDef.GetAttribute('text') -notin @('Buildings.artdef', 'CSC_Buildings.artdef')) {
        throw "The cooked building reference for '$name' differs from the expected source or fallback value."
    }
    $building.SetAttribute('text', $expectedBuilding)
    $artDef.SetAttribute('text', 'CSC_Buildings.artdef')
}
$document.Save($artDefPath)
Write-Output 'CSC Art Pack is ready: its cooked tilebases and art bridges are present, and all six CSC building references are restored.'
