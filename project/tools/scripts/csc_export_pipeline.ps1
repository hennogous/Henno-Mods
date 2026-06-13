<#
.SYNOPSIS
    CSC Blender → Asset Editor Pipeline
    Fully automated: .blend → .fgx + .geo in mod Geometries folder.

.PARAMETER BlendFile
    Path to the source .blend file

.PARAMETER GeoClass
    Geometry class (default: LandmarkModel)

.PARAMETER VertexFormat
    0=1UV, 1=2UV, 2=3UV No Bone Bindings (default: 2)

.PARAMETER OutputDir
    Override output directory (default: mod Geometries folder)

.NOTES
    Naming convention for -AddToAsset:
      {AssetName}.blend         → base geometry, visible in Worked state
      {AssetName}_PIL.blend     → pillaged geometry, visible in Pillaged state, DefaultBurnMaterial applied
      {AssetName}_CON.blend     → construction geometry, visible in Construction state
    
    The material is auto-detected from the existing asset's Worked state.
    The target .ast file is inferred as {AssetName}.ast in the Assets folder.

.EXAMPLE
    .\csc_export_pipeline.ps1 "C:\...\CSC_Storage_L_PIL.blend"
    # Exports FGX + GEO to Geometries folder

.EXAMPLE
    .\csc_export_pipeline.ps1 "C:\...\CSC_Storage_L_PIL.blend" -AddToAsset
    # Exports AND adds PIL geometry to CSC_Storage_L.ast (Pillaged state only)

.EXAMPLE
    .\csc_export_pipeline.ps1 "C:\...\CSC_Storage_L_PIL.blend" -AddToAsset -Asset "CSC_BAKERS_Storage_L"
    # Exports AND adds to CSC_BAKERS_Storage_L.ast instead (for Quarter-specific assets)
#>
param(
    [Parameter(Mandatory=$true)]
    [string]$BlendFile,
    [string]$GeoClass = "LandmarkModel",
    [int]$VertexFormat = 2,
    [string]$OutputDir = "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\Civ Supply Chains\Geometries",
    [switch]$AddToAsset,
    [string]$Asset = ""
)

$Blender = 'C:\Program Files\Blender Foundation\Blender 3.1\blender.exe'
$CN6ToFGX = "C:\Users\Shadow\.openclaw\workspace\csc\cn6libs\CN6ToFGX.exe"
$CN6LibsDir = "C:\Users\Shadow\.openclaw\workspace\csc\cn6libs"
$TempDir = "C:\Users\Shadow\.openclaw\workspace\test_pipeline"
$BaseName = [System.IO.Path]::GetFileNameWithoutExtension($BlendFile)

New-Item -ItemType Directory -Path $TempDir -Force | Out-Null

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CSC Pipeline: $BaseName" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

# === Step 1: Blender validate + export CN6 ===
Write-Host "`n[1/4] Blender → CN6..." -ForegroundColor Yellow

$cn6Out = Join-Path $TempDir "$BaseName.cn6"

$blenderScript = @'
import bpy, sys
sys.path.insert(0, r"C:\Users\Shadow\AppData\Roaming\Blender Foundation\Blender\3.1\scripts\addons")
from io_export_cn6 import do_export

output = sys.argv[sys.argv.index("--") + 1]

obj = [o for o in bpy.data.objects if o.type == 'MESH'][0]
mesh = obj.data

# Ensure we're in Object Mode (file may have been saved in Edit Mode)
if bpy.context.mode != 'OBJECT':
    bpy.ops.object.mode_set(mode='OBJECT')

# Validate UV maps
if len(mesh.uv_layers) < 3:
    while len(mesh.uv_layers) < 3:
        mesh.uv_layers.new(name=f"UV{len(mesh.uv_layers) + 1}")
    print(f"FIXED: Added UV maps -> {len(mesh.uv_layers)}")
else:
    print(f"UV maps: OK ({len(mesh.uv_layers)})")

# Validate bone names (colons etc. corrupt the FGX)
arm = [o for o in bpy.data.objects if o.type == 'ARMATURE'][0]
for bone in arm.data.bones:
    bad = [c for c in ':/<>|' if c in bone.name]
    if bad:
        old = bone.name
        bone.name = bone.name.replace(':', '_').replace('/', '_').replace('<', '_').replace('>', '_').replace('|', '_')
        # Fix matching vertex group
        for mo in bpy.data.objects:
            if mo.type == 'MESH':
                for vg in mo.vertex_groups:
                    if vg.name == old:
                        vg.name = bone.name
        print(f"FIXED: Bone name '{old}' -> '{bone.name}'")

# Fix unweighted vertices
unweighted = sum(1 for v in mesh.vertices if len(v.groups) == 0)
if unweighted > 0:
    vg = obj.vertex_groups.get("Bone")
    if vg:
        for v in mesh.vertices:
            if len(v.groups) == 0:
                vg.add([v.index], 1.0, 'ADD')
        print(f"FIXED: {unweighted} unweighted vertices")
else:
    print(f"Weights: OK")

# Report counts (pre-triangulation for .geo)
print(f"VERTS:{len(mesh.vertices)}")

# Export CN6 (triangulates internally)
do_export(output, triangulate=True, use_selection=False)
print("CN6_OK")
'@

$scriptPath = Join-Path $TempDir "_export_cn6.py"
$blenderScript | Out-File -Encoding utf8 $scriptPath

$output = & "$Blender" --background "$BlendFile" --python "$scriptPath" -- "$cn6Out" 2>&1 | ForEach-Object { $_.ToString() }
$outputText = $output -join "`n"

if ($outputText -notmatch "CN6_OK") {
    Write-Host "FAILED: CN6 export" -ForegroundColor Red
    $output | ForEach-Object { Write-Host "  $_" }
    exit 1
}

# Extract vertex count
$nVerts = 0
if ($outputText -match "VERTS:(\d+)") { $nVerts = [int]$Matches[1] }

Write-Host "  CN6: OK ($nVerts verts)" -ForegroundColor Green

# === Step 2: CN6 → FGX ===
Write-Host "`n[2/4] CN6 → FGX..." -ForegroundColor Yellow

$fgxOut = Join-Path $TempDir "$BaseName.fgx"
if (Test-Path $fgxOut) { Remove-Item $fgxOut }

Push-Location $CN6LibsDir
$fgxOutput = & $CN6ToFGX "$cn6Out" "$fgxOut" $VertexFormat 2>&1 | Where-Object {
    $_ -notmatch "VirtualSpace|Invalid Path|Error refreshing virtual space|WARNING:|---+|^\s*$"
}
Pop-Location

if (-not (Test-Path $fgxOut)) {
    Write-Host "FAILED: FGX conversion" -ForegroundColor Red
    $fgxOutput | ForEach-Object { Write-Host "  $_" }
    exit 1
}
Write-Host "  FGX: $((Get-Item $fgxOut).Length) bytes" -ForegroundColor Green

# === Step 3: Generate .geo ===
Write-Host "`n[3/4] Generating .geo..." -ForegroundColor Yellow

# Read CN6 to get accurate counts post-triangulation
$cn6Lines = Get-Content $cn6Out
$skeleton = @()
$meshName = ""
$inVerts = $false; $inTris = $false
$vertCount = 0; $triCount = 0

foreach ($line in $cn6Lines) {
    if ($line -match '^(\d+) "(.+?)"') { $skeleton += $Matches[2] }
    if ($line -match '^mesh:"(.+?)"') { $meshName = $Matches[1] }
    if ($line -eq "vertices") { $inVerts = $true; $inTris = $false; continue }
    if ($line -eq "triangles") { $inTris = $true; $inVerts = $false; continue }
    if ($line -eq "end") { $inVerts = $false; $inTris = $false }
    if ($inVerts -and $line.Trim().Length -gt 0) { $vertCount++ }
    if ($inTris -and $line.Trim().Length -gt 0) { $triCount++ }
}

$bonesXml = ($skeleton | ForEach-Object { "<Element text=`"$_`"/>" }) -join "`n"
$geoXml = @"
<?xml version="1.0" encoding="UTF-8" ?>
<AssetObjects:GeometryInstance>
<m_CookParams>
<m_Values/>
</m_CookParams>
<m_Version>
<major>0</major>
<minor>0</minor>
<build>0</build>
<revision>0</revision>
</m_Version>
<m_Meshes>
<Element>
<m_Name text="$meshName"/>
<m_Groups>
<Element>
<m_Name text="$meshName"/>
<m_nFirstPrim>0</m_nFirstPrim>
<m_nPrims>$triCount</m_nPrims>
</Element>
</m_Groups>
<m_nBoundBoneCount>1</m_nBoundBoneCount>
<m_nPrimitiveCount>$triCount</m_nPrimitiveCount>
<m_nVertexCount>$vertCount</m_nVertexCount>
</Element>
</m_Meshes>
<m_Bones>
$bonesXml
</m_Bones>
<m_ModelName text="$($skeleton[0])"/>
<m_SourceFilePath text=""/>
<m_SourceObjectName text=""/>
<m_ImportedTime>0</m_ImportedTime>
<m_ExportedTime>0</m_ExportedTime>
<m_ClassName text="$GeoClass"/>
<m_DataFiles>
<Element>
<m_ID text="GR2"/>
<m_RelativePath text="$BaseName.fgx"/>
</Element>
</m_DataFiles>
<m_Name text="$BaseName"/>
<m_Description text="$BaseName"/>
<m_Tags>
<Element text="$GeoClass"/>
</m_Tags>
<m_Groups/>
</AssetObjects:GeometryInstance>
"@

$geoOut = Join-Path $TempDir "$BaseName.geo"
$geoXml | Out-File -Encoding utf8 $geoOut
Write-Host "  GEO: $meshName | $vertCount verts, $triCount tris" -ForegroundColor Green

# === Step 4: Copy to Geometries ===
Write-Host "`n[4/4] Deploy to Geometries..." -ForegroundColor Yellow

Copy-Item $fgxOut (Join-Path $OutputDir "$BaseName.fgx") -Force
Copy-Item $geoOut (Join-Path $OutputDir "$BaseName.geo") -Force

Write-Host "  $BaseName.fgx → Geometries" -ForegroundColor Green
Write-Host "  $BaseName.geo → Geometries" -ForegroundColor Green

# Cleanup temp
Remove-Item (Join-Path $TempDir "_export_cn6.py") -ErrorAction SilentlyContinue

# === Optional: Add geometry to asset ===
if ($AddToAsset) {
    Write-Host "`n[5/5] Adding to asset..." -ForegroundColor Yellow
    
    $AssetsDir = Join-Path (Split-Path $OutputDir) "Assets"
    
    # Infer asset name and state from filename convention:
    #   CSC_Storage_L_PIL → asset=CSC_Storage_L, suffix=PIL (Pillaged)
    #   CSC_Storage_L_CON → asset=CSC_Storage_L, suffix=CON (Construction)
    #   CSC_Storage_L     → asset=CSC_Storage_L, suffix=none (Worked/base)
    
    $suffix = ""
    $assetName = $BaseName
    if ($BaseName -match '^(.+)_(PIL|CON)$') {
        $assetName = $Matches[1]
        $suffix = $Matches[2]
    }
    # Override with explicit asset name if provided
    if ($Asset) { $assetName = $Asset }
    
    $stateMap = @{
        "PIL" = @{ VisibleState = "Pillaged"; UseBurn = $true }
        "CON" = @{ VisibleState = "Construction"; UseBurn = $false }
        ""    = @{ VisibleState = "Worked"; UseBurn = $false }
    }
    $stateInfo = $stateMap[$suffix]
    
    $astPath = Join-Path $AssetsDir "$assetName.ast"
    if (-not (Test-Path $astPath)) {
        Write-Host "  SKIP: Asset $astPath not found" -ForegroundColor Yellow
    } else {
        $ast = Get-Content $astPath -Raw
        
        # Check if this geometry is already in the asset
        if ($ast -match [regex]::Escape("<m_GeoName text=`"$BaseName`"/>")) {
            Write-Host "  SKIP: $BaseName already in asset" -ForegroundColor Yellow
        } else {
            # Read material from existing Worked state
            $material = ""
            if ($ast -match '<m_StateName text="Worked"/>[\s\S]*?<m_ObjectName text="([^"]+)"[^/]*/>\s*<m_eObjectType>MATERIAL</m_eObjectType>\s*<m_ParamName text="Material"/>') {
                # Regex didn't work well on multiline, use simpler approach
            }
            # Find material from Worked state using regex (XML has non-standard namespaces)
            # Pattern: StateName=Worked block → first non-empty Material ObjectName
            if ($ast -match '(?s)<m_StateName text="Worked"/>.*?<m_ObjectName text="([^"]+)"/>[\s\r\n]*<m_eObjectType>MATERIAL</m_eObjectType>[\s\r\n]*<m_ParamName text="Material"/>') {
                $material = $Matches[1]
            }
            
            if (-not $material) {
                Write-Host "  WARN: Could not find material from Worked state" -ForegroundColor Yellow
                $material = ""
            } else {
                Write-Host "  Material: $material (from Worked state)" -ForegroundColor Green
            }
            
            # Read mesh name from .geo
            $geoPath = Join-Path $OutputDir "$BaseName.geo"
            $meshName = "${BaseName}_Bldg"
            if (Test-Path $geoPath) {
                $geoContent = Get-Content $geoPath -Raw
                if ($geoContent -match '<m_Name text="([^"]+)"/>') {
                    $meshName = $Matches[1]
                }
            }
            
            # Build state entries
            $allStates = @("Worked", "Unworked", "Pillaged", "Construction", "Unbuilt")
            $stateEntries = ""
            
            foreach ($s in $allStates) {
                $visible = if ($s -eq $stateInfo.VisibleState) { "true" } else { "false" }
                $mat = if ($s -eq $stateInfo.VisibleState) { $material } else { "" }
                $burn = if ($s -eq $stateInfo.VisibleState -and $stateInfo.UseBurn) { "DefaultBurnMaterial" } else { "" }
                
                $stateEntries += @"
					<Element>
						<m_Values>
							<m_Values>
								<Element class="AssetObjects..ObjectValue">
									<m_ObjectName text="$mat"/>
									<m_eObjectType>MATERIAL</m_eObjectType>
									<m_ParamName text="Material"/>
								</Element>
								<Element class="AssetObjects..BoolValue">
									<m_bValue>$visible</m_bValue>
									<m_ParamName text="Visible"/>
								</Element>
								<Element class="AssetObjects..ObjectValue">
									<m_ObjectName text="FOW/DefaultMaterial"/>
									<m_eObjectType>MATERIAL</m_eObjectType>
									<m_ParamName text="FOWMaterial"/>
								</Element>
								<Element class="AssetObjects..ObjectValue">
									<m_ObjectName text="$burn"/>
									<m_eObjectType>MATERIAL</m_eObjectType>
									<m_ParamName text="BurnMaterial"/>
								</Element>
								<Element class="AssetObjects..ObjectValue">
									<m_ObjectName text="DefaultSnowMaterial"/>
									<m_eObjectType>MATERIAL</m_eObjectType>
									<m_ParamName text="SnowMaterial"/>
								</Element>
								<Element class="AssetObjects..BoolValue">
									<m_bValue>true</m_bValue>
									<m_ParamName text="EmissiveEnabled"/>
								</Element>
								<Element class="AssetObjects..BoolValue">
									<m_bValue>false</m_bValue>
									<m_ParamName text="FOWVisibleOnly"/>
								</Element>
							</m_Values>
						</m_Values>
						<m_GroupName text="$meshName"/>
						<m_MeshName text="$meshName"/>
						<m_StateName text="$s"/>
					</Element>

"@
            }
            
            $modelInstance = @"
			<Element>
				<m_Name text="$BaseName"/>
				<m_GeoName text="$BaseName"/>
				<m_GroupStates>
$stateEntries				</m_GroupStates>
			</Element>
"@
            
            # Insert before closing </m_ModelInstances>
            $ast = $ast -replace '(\s*)</m_ModelInstances>', "$modelInstance`$1</m_ModelInstances>"
            $ast | Out-File -Encoding utf8 $astPath
            
            Write-Host "  Added $BaseName to $assetName.ast ($($stateInfo.VisibleState) state)" -ForegroundColor Green
        }
    }
}

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "DONE: $BaseName" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
