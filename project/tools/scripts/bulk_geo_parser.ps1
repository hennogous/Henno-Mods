# Bulk .geo XML parser — extracts stats from ALL building geometry files
# Outputs TSV for easy consumption

$pantry = "C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\pantry\Geometries"
$outFile = "C:\Users\Shadow\.openclaw\workspace\csc\docs\geo-stats-all.tsv"

$results = @()
$geoFiles = Get-ChildItem $pantry -Filter "DIS_*.geo" | Where-Object { $_.Name -notmatch '_Decal|_OB|_HMedit|_HEdit|_RoadCPs|_Attachments' }

foreach ($f in $geoFiles) {
    try {
        [xml]$xml = Get-Content $f.FullName -Raw
        $meshes = $xml.'AssetObjects..GeometryInstance'.m_Meshes.Element
        $bones = $xml.'AssetObjects..GeometryInstance'.m_Bones.Element
        $modelName = $xml.'AssetObjects..GeometryInstance'.m_ModelName.text
        $sourcePath = $xml.'AssetObjects..GeometryInstance'.m_SourceFilePath.text
        $dataFile = $xml.'AssetObjects..GeometryInstance'.m_DataFiles.Element | Where-Object { $_.m_ID.text -eq 'GR2' } | Select-Object -First 1
        $fgxName = if ($dataFile) { $dataFile.m_RelativePath.text } else { '' }
        
        $totalVerts = 0
        $totalTris = 0
        $meshCount = 0
        $meshNames = @()
        $groups = @()
        
        if ($meshes) {
            $meshArray = @($meshes)
            $meshCount = $meshArray.Count
            foreach ($m in $meshArray) {
                $vc = [int]$m.m_nVertexCount
                $tc = [int]$m.m_nPrimitiveCount
                $totalVerts += $vc
                $totalTris += $tc
                $meshNames += $m.m_Name.text
                
                $grps = @($m.m_Groups.Element)
                foreach ($g in $grps) {
                    if ($g.m_Name.text) { $groups += $g.m_Name.text }
                }
            }
        }
        
        $boneCount = if ($bones) { @($bones).Count } else { 0 }
        $boneNames = if ($bones) { @($bones) | ForEach-Object { $_.text } } else { @() }
        
        # Determine variants from filename
        $name = $f.BaseName
        $isPIL = $name -match '_PIL'
        $isCON = $name -match '_CON'
        $isBase = $name -match '_Base_'
        
        # Determine district
        $district = ''
        if ($name -match '^DIS_([A-Z]+)_') { $district = $Matches[1] }
        
        $results += [PSCustomObject]@{
            File = $f.BaseName
            District = $district
            Model = $modelName
            Verts = $totalVerts
            Tris = $totalTris
            Meshes = $meshCount
            Bones = $boneCount
            MeshNames = ($meshNames -join '; ')
            Groups = ($groups -join '; ')
            BoneNames = ($boneNames -join '; ')
            IsPIL = $isPIL
            IsCON = $isCON
            IsBase = $isBase
            FGX = $fgxName
            Source = $sourcePath
        }
    } catch {
        Write-Host "ERROR: $($f.Name) - $_"
    }
}

$results | Export-Csv -Path $outFile -Delimiter "`t" -NoTypeInformation
Write-Host "Exported $($results.Count) entries to $outFile"

# Quick summary by district
Write-Host "`n=== District Summary ==="
$results | Where-Object { -not $_.IsPIL -and -not $_.IsCON -and -not $_.IsBase } | Group-Object District | Sort-Object Name | ForEach-Object {
    Write-Host "$($_.Name): $($_.Count) building geos"
}
