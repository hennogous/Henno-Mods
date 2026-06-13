# Export Pipeline Reference

The full workflow from Blender model to in-game building geometry.

> **Platform note:** Asset Editor, ModBuddy, CN6ToFGX, and the cook pipeline are **Windows-only**.

## Overview

```
.blend → [Blender headless] → .cn6 → [CN6ToFGX.exe] → .fgx + .geo → Geometries/ → Asset Editor → Cook → Game
```

The automated pipeline script handles steps 1–4. Asset Editor wiring and cooking are manual.

---

## Tool Locations

| Tool | Path |
|------|------|
| Blender 3.1.2 | `C:\Program Files\Blender Foundation\Blender 3.1\blender.exe` |
| CN6ToFGX converter | `csc/cn6libs/CN6ToFGX.exe` |
| Pipeline script | `csc/scripts/csc_export_pipeline.ps1` |
| Blender addon | `csc/scripts/csc_asset_editor_export.py` |
| Mesh inspector | `csc/scripts/inspect_building_mesh.py` |
| CN6 export addon | `%APPDATA%\Blender Foundation\Blender\3.1\scripts\addons\io_export_cn6\` |
| Output (Geometries) | `C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods\Civ Supply Chains\Geometries` |

---

## Pre-Export Checklist

Run through this before every export. The pipeline script auto-fixes some of these, but catching them early saves time.

### Mandatory
- [ ] **Exactly 3 UV layers** in correct order (diffuse, lightmap, emissive)
- [ ] **No colons in bone names** (also no `/ < > |`)
- [ ] **Object Mode active** (not Edit Mode — VertexGroup.add() fails silently in Edit Mode)
- [ ] **Every vertex weighted** to at least one bone (unweighted verts break burn material)
- [ ] **Single armature** with root bone + child bones as needed
- [ ] **Single mesh object** parented to armature via Armature modifier

### Recommended
- [ ] Vertex count within budget for target tier
- [ ] Custom normals set (hard edges at wall/roof boundaries)
- [ ] Material name matches intended mesh group name in .geo
- [ ] File saved (the addon exports the saved version)

---

## Automated Pipeline

### Basic Usage

```powershell
.\csc_export_pipeline.ps1 -BlendFile "C:\path\to\model.blend"
```

### Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `-BlendFile` | (required) | Path to source .blend file |
| `-GeoClass` | `LandmarkModel` | Geometry class for .geo |
| `-VertexFormat` | `2` | 0=1UV, 1=2UV, **2=3UV No Bone Bindings** |
| `-OutputDir` | CSC mod Geometries folder | Override output path |
| `-AddToAsset` | (switch) | Inject geometry into matching .ast file |
| `-Asset` | (auto from filename) | Override asset name for -AddToAsset |

### What Each Step Does

#### Step 1: Blender → CN6
Runs Blender headless with a validation + export script:
1. Finds the mesh object
2. Ensures Object Mode
3. Validates UV layers — adds missing layers up to 3
4. Validates bone names — replaces colons and other bad characters
5. Fixes unweighted vertices — assigns to root bone with weight 1.0
6. Exports CN6 via the `io_export_cn6` addon (triangulates internally)

#### Step 2: CN6 → FGX
Runs `CN6ToFGX.exe` with vertex format 2:
- **Position, Normal, Tangent, Binormal, UV0, UV1, UV2**
- "No Bone Bindings" — bones are for hierarchy only, not per-vertex skinning
- Produces byte-identical output to CivNexus6 GUI
- Suppress spurious VirtualSpace/Invalid Path warnings (they're harmless)

#### Step 3: Generate .geo
Parses the CN6 file to extract:
- Skeleton (bone names + hierarchy)
- Mesh name, vertex count, triangle count
- Generates XML .geo file with correct metadata

Key .geo fields:
```xml
<m_ClassName text="LandmarkModel"/>
<m_nBoundBoneCount>1</m_nBoundBoneCount>
<m_nPrimitiveCount>{triCount}</m_nPrimitiveCount>
<m_nVertexCount>{vertCount}</m_nVertexCount>
```

The `m_Groups` section names the mesh group (material slot) — this name must match what you assign in Asset Editor.

#### Step 4: Deploy
Copies both `.fgx` and `.geo` to the mod's Geometries folder.

### Adding to Existing Assets (-AddToAsset)

For PIL/CON variants, use the `-AddToAsset` switch:

```powershell
# Export pillaged variant and inject into CSC_Storage_L.ast
.\csc_export_pipeline.ps1 "C:\...\CSC_Storage_L_PIL.blend" -AddToAsset

# Export CON variant into a different asset
.\csc_export_pipeline.ps1 "C:\...\CSC_Storage_L_CON.blend" -AddToAsset -Asset "CSC_BAKERS_Storage_L"
```

**Naming convention drives state detection:**
- `{AssetName}.blend` → base geometry (Worked state)
- `{AssetName}_PIL.blend` → Pillaged state (+ DefaultBurnMaterial)
- `{AssetName}_CON.blend` → Construction state

The script:
1. Infers asset name and state from filename
2. Reads the existing .ast to find the Worked state material
3. Generates `<m_GroupStates>` entries for all 5 states (visible only in the target state)
4. Injects a new `<Element>` into `<m_ModelInstances>` in the .ast

---

## Blender Addon (File > Export)

Install `csc_asset_editor_export.py` as a Blender addon for one-click export from the UI:

1. Copy to Blender addons folder or install via Edit > Preferences > Add-ons > Install
2. Enable "CSC Asset Editor Export"
3. File > Export > Asset Editor (.fgx / .geo)

Behavior:
- Saves the file first (exports the saved version)
- Runs the pipeline script in a background thread
- Shows success/failure popup in Blender
- Hold **Alt** while clicking to show the options dialog (Add to .ast checkbox)

---

## Manual Steps After Pipeline

### 1. Asset Editor Setup

If this is a **new asset** (not adding to an existing one):

1. Open your mod project in Asset Editor
2. Create a new TileBase asset (or appropriate class)
3. **Geometry tab:** Import the .geo file from Geometries folder
4. **Materials tab:** Assign your district material to each mesh group
5. For each state:
   - **Worked:** main geometry visible, base material, EmissiveEnabled=true
   - **Unworked:** main geometry visible, non-emissive material variant
   - **Pillaged:** PIL geometry visible (main hidden), BurnMaterial=DefaultBurnMaterial
   - **Construction:** CON geometry visible (main hidden), construction material
   - **Unbuilt:** main geometry visible, base material

### 2. The .ast File Structure

The asset file binds everything together:

```xml
<m_ModelInstances>
  <Element>
    <m_Name text="CSC_Storage_L"/>
    <m_GeoName text="CSC_Storage_L"/>
    <m_GroupStates>
      <!-- One entry per state × mesh group -->
      <Element>
        <m_StateName text="Worked"/>
        <m_MeshName text="CSC_Storage_L_Bldg"/>
        <m_GroupName text="CSC_Storage_L_Bldg"/>
        <!-- Material, Visible=true, FOWMaterial, BurnMaterial, SnowMaterial, EmissiveEnabled -->
      </Element>
      <Element>
        <m_StateName text="Pillaged"/>
        <!-- Visible=false for base geo, true for PIL geo -->
      </Element>
      <!-- ... Unworked, Construction, Unbuilt -->
    </m_GroupStates>
  </Element>
</m_ModelInstances>
```

### 3. Asset Editor Cache

Assets created outside Asset Editor (scripted/pipeline) won't appear in AE's browser until registered in:
```
%APPDATA%\AssetCloud\mod-<modname>-asset-deps.json
```

Options:
- Create a minimal entry in AE first, then modify externally
- Manually add entries to the cache JSON
- Delete the cache file and reopen (slow rebuild)

### 4. XLP Registration

Each geometry needs an XLP entry:
```xml
<Element>
    <m_EntryID text="CSC_Storage_L"/>
    <m_ObjectName text="CSC_Storage_L"/>
</Element>
```

The XLP class is typically `TileBase` for buildings. See the civ6-modding skill's art-pipeline reference for full XLP/ArtDef wiring.

### 5. Cook and Test

1. **ModBuddy Build:** Compiles .xlp → .blp, resolves dependencies, generates .dep
2. **Enable mod** in Additional Content
3. **Test in-game:** Verify all 5 states render correctly
4. **Check for:** Missing textures, wrong material assignments, broken burn effect, invisible geometry

---

## CN6ToFGX Settings Reference

| VertexFormat | Channels | Use Case |
|:---:|----------|----------|
| 0 | Position, Normal, Tangent, Binormal, UV0 | 1 UV map only |
| 1 | + UV1 | 2 UV maps |
| **2** | + UV1 + UV2, No Bone Bindings | **Standard for buildings (3 UVs)** |

Always use **VertexFormat=2** for buildings. The "No Bone Bindings" is correct — building bones are hierarchy-only, not vertex-weighted in the FGX sense.

## GeoClass Reference

| Class | Use |
|-------|-----|
| **LandmarkModel** | Buildings, clutter, city blocks (default) |
| DecalGeometry | Terrain decals |
| LandmarkObstructionProfile | 2D planar collision areas |
| Unit | Unit models |
| VFXModel | VFX geometry |

---

## Mesh Inspector Script

For analysing existing Firaxis buildings or verifying your own exports:

```powershell
& "C:\Program Files\Blender Foundation\Blender 3.1\blender.exe" --background --python "csc\scripts\inspect_building_mesh.py"
```

Parses CN6 files, creates Blender meshes for analysis, outputs JSON report with:
- Topology: verts, edges, faces, valence distribution
- Connectivity: island count, island sizes
- Dimensions: bounding box, surface area, vertex density
- UV analysis: per-channel bounds, utilisation, island count
- Normals: unique count, hard/soft assessment
- Bone weights: single vs multi-bone vertices

Place CN6 files in `csc/docs/sample-geometries/` and run. Output: `csc/docs/building-mesh-analysis.json`.

---

## Troubleshooting

### FGX Export Produces No File
- CN6ToFGX.exe must run from within `csc/cn6libs/` directory (it loads DLLs from there)
- Check the CN6 file isn't empty or malformed
- VirtualSpace/Invalid Path warnings are harmless — ignore them

### Geometry Invisible In-Game
- Check .ast states: is your geometry marked Visible=true in the correct state?
- Check material assignment: null material = invisible
- Check XLP: is the asset entry registered and does m_ObjectName match the .ast filename?
- Check ArtDef: is the building wired in Landmarks.artdef?

### Burn Material Not Working on PIL Variant
- Every vertex must be weighted to a bone — check for strays
- BurnMaterial must be set to `DefaultBurnMaterial` in the Pillaged state
- PIL geometry must be its own ModelInstance in the .ast

### Textures Wrong/Missing
- Verify 3 UV layers exist in correct order
- Check material in Asset Editor has correct texture assignments
- Re-cook textures if paths changed (.tex files contain internal path refs)

### Pipeline Script Fails at Step 1
- Blender 3.1.2 required (newer versions may have API changes)
- CN6 export addon must be installed at the expected path
- File must contain at least one MESH and one ARMATURE object
