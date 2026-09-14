# Export Pipeline Reference

> For composed building scenes using reusable props, use the [scene decoder and exporter](blender-scene-export.md). The pipeline below is legacy documentation and does not preserve that scene/attachment contract.

> **Documentation audit — 2026-09-12: Needs refresh.** The actual PowerShell script still hard-codes .openclaw/workspace/csc paths, defaults UVCount to 2, and recognizes separate _CON/_PIL suffixes. Merely correcting document paths would not fix the tool. Preserve three UV channels for the current kit; reconcile script/state handling before production use. Static export examples do not validate crane animation.
> Classification: 3D export. See the [full audit](../DOCUMENT-AUDIT.md).

The workflow for taking a finished Blender source asset into Civ VI geometry/assets. For creating or AI-assisted modelling of the asset itself, start with [AI-Assisted 3D Model Generation](ai-3d-model-generation.md).

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
- [ ] **Export scene contains only the export mesh and armature**; remove cameras, lights, starter cubes, reference planes, and helper objects
- [ ] **UV layers named `UV1`, `UV2`, `UV3`** in that order
- [ ] **Mesh vertex group matches the bound bone name**; for simple CSC props/buildings this is usually one vertex group named `Bone`
- [ ] **All texture source maps exist at 256x256** for small standalone props unless the asset deliberately uses a larger atlas
- [ ] **Source/working objects removed**; this file is the clean export scene, not the modelling sandbox

### Recommended
- [ ] Vertex count within budget for target tier
- [ ] Custom normals set (hard edges at wall/roof boundaries)
- [ ] Material name matches intended mesh group name in .geo
- [ ] The single visible armature object is named with the intended export basename

### CSC Blender File Structure

Use the same minimal structure for small CSC building props and Asset Editor tests:

| Item | Convention | Example |
|------|------------|---------|
| Armature object | `{AssetName}` | `CSC_TAILORS_SpinningWheel` |
| Mesh object | `{AssetName}_Bldg` | `CSC_TAILORS_SpinningWheel_Bldg` |
| Mesh data | Same as mesh object | `CSC_TAILORS_SpinningWheel_Bldg` |
| Material slot/material | Same as mesh group | `CSC_TAILORS_SpinningWheel_Bldg` |
| Armature data | `Armature` is acceptable | `Armature` |
| Simple prop bone | `Bone` | `Bone` |
| Simple prop vertex group | Same as bone | `Bone` |
| UV layers | Exactly `UV1`, `UV2`, `UV3` | `UV1`, `UV2`, `UV3` |

The mesh should be parented to the armature and have an `Armature` modifier targeting that armature. For simple, non-animated CSC props, assign every mesh vertex to the single `Bone` vertex group at weight 1.0. Geometry may contain disconnected low-poly islands, but keep them joined into the one export mesh object.

Keep the saved export file clean: no default cube, no cameras/lights, no reference images, and no old iteration meshes. If you need source/reference objects, keep them in a separate working `.blend` or collection that is not part of the final export file.

### CSC Texture Naming

For standalone CSC prop/building texture sets, use the asset name plus Civ's texture suffixes:

| Suffix | Civ slot | Notes |
|--------|----------|-------|
| `_B` | Base color | sRGB color map |
| `_AO` | Ambient occlusion | Linear greyscale — **baked from geometry in Blender, not generated from `_B`**. See below. |
| `_N` | Normal | Tangent-space normal map |
| `_G` | Gloss | Linear greyscale; white is shinier, black is duller |
| `_M` | Metalness | Linear greyscale; usually black for wood, wool, clay, and stone props |

Example source files for `CSC_TAILORS_SpinningWheel`:

```text
CSC_TAILORS_SpinningWheel_B.png
CSC_TAILORS_SpinningWheel_AO.png
CSC_TAILORS_SpinningWheel_N.png
CSC_TAILORS_SpinningWheel_G.png
CSC_TAILORS_SpinningWheel_M.png
```

Use **256x256** for small standalone prop source maps and Asset Editor tests. Move to a larger texture or a shared atlas only when the asset's screen importance justifies it.

For Blender preview shading, wire `_B` into Base Color, `_N` through a Normal Map node, `_M` into Metallic, and invert `_G` before feeding Principled Roughness. `_AO` is sampled through **UV2** (see below) and multiplied into Base Color for preview; Asset Editor should receive it in the AO texture slot the same way.

### AO: Bake From Geometry, Not From `_B`

AO is a **positional** property (where a face sits relative to its surroundings), not a material property, so it cannot be safely derived from the painted base color once UV1 overlaps (see below). `csc_generate_pbr_maps.mjs` deliberately does **not** produce an `_AO` map — generate `_N`/`_G`/`_M` from `_B` with the script, then bake `_AO` in Blender:

1. **UV2 must be a fresh, non-overlapping unwrap/pack — never a copy of UV1.** UV1 is allowed (expected) to overlap so repeated pieces share atlas space; the engine samples AO through UV2 (TEXCOORD_1) specifically because it is the channel where every face gets its own unique texel space. Copying UV1 into UV2 (or leaving UV2 defaulted to a copy) forces overlapping faces to share one baked AO value, which is a step backward from real geometric AO — it reproduces the same "one answer for many positions" problem that made deriving AO from `_B` necessary in the first place.
2. Pack Islands on UV2 (`Pack to: Original Bounding Box` if the model must stay confined to one atlas quadrant — see [Shared Atlas AO](shared-atlas-ao.md) for the multi-model/shared-atlas case).
3. Bake in Cycles, AO bake type, with the model isolated from other scene objects (hide others from *render*, not just viewport — AO rays see the whole scene). Ray distance should scale with the model (~20% of its largest dimension is a reasonable start).
4. Save the baked image as `{AssetName}_AO.png`, external/unpacked like the other maps.

For a single standalone prop with no shared atlas, this is the whole story. For a shared atlas where several models reuse the same painted patches (Level 1/2/3 buildings, Storage S/M/L), see [Shared Atlas AO](shared-atlas-ao.md) — variants can share the parent's baked AO texels wherever they reuse the parent's UV1 content, so the bake only needs to happen once per family.

During active texture iteration, keep Blender image textures **external/unpacked** and pointed at the PNG files in the asset folder. A packed image is only a snapshot embedded in the `.blend`; edits made later in GIMP, Photoshop, or scripts do not automatically update that embedded copy. Use Blender's image reload action, or a small reload script, after editing the PNGs externally. Pack images only for handoff/archive snapshots where portability matters, and repack deliberately after any external texture changes.

### AI-Assisted Texture Handoff

Texture generation decisions belong in [AI-Assisted 3D Model Generation](ai-3d-model-generation.md). By the time an asset reaches this export workflow:

1. `_B` is the approved artistic base-color map.
2. `_N`, `_G`, and `_M` are derived from that exact `_B` map so seams and material regions stay pixel-aligned.
3. `_AO` is baked from the actual geometry through a non-overlapping UV2 layout.
4. All active texture images are external PNGs beside the asset, not only packed inside the `.blend`.

Set up the helper once:

```bash
cd project/tools/blender
npm install
```

Generate the companion maps from an existing base map:

```bash
node project/tools/blender/csc_generate_pbr_maps.mjs \
  --base "C:/path/to/CSC_TAILORS_SpinningWheel_B.png" \
  --preset csc-textile-prop \
  --overwrite \
  --backup
```

The script infers `CSC_TAILORS_SpinningWheel` from `_B.png` and writes matching `_N.png`, `_G.png`, and `_M.png` beside the base map (no `_AO` — bake that from geometry, see above). Add `--copy-base` if the base map also needs to be resized/copied to the output folder. Use `--out-dir` to write to a temporary folder for review before replacing live textures.

For building construction detail, prefer `--height Asset_H.png` and `--regions material-regions.json` so painted color does not become accidental relief or material classification. See [Authored Relief](textures-and-uvs.md#authored-relief-with-the-companion-map-generator) for the schema, resolution scaling and explicit normal green-channel convention. The base-only command above is an approximation.

Do **not** generate `_B`, `_N`, `_G`, and `_M` independently with image generation unless the tool can guarantee exact pixel alignment. Even small shifts between maps will make seams, normals, or gloss disagree once the atlas is wrapped onto the mesh.

Avoid using Blender as the primary pixel-writing tool for generated maps. It is reliable for material wiring and scene validation, but generated image datablocks can fail quietly when saving over existing texture paths. Prefer the Node/Sharp helper for map generation, write to a temporary path first, validate pixel stats or preview, then copy the verified files into the asset folder and reload the external images in Blender. After replacing a texture file at the same path, explicitly reload or recreate Blender's image datablock so the material is not still showing stale cached pixels. Do not pack active working textures by default.

When a generated atlas has strong material regions, check the UVs against the model before flattening the texture. If wood grain, wool, or thread swatches appear on the wrong parts, remap `UV1` by connected mesh island so each physical part samples the intended atlas region. For wooden props, orient the UVs so the visible grain runs along the length of each board, spoke, post, beam, or rim segment. Check the atlas first instead of assuming the grain runs horizontally; if the useful grain direction is vertical, rotate the wood UV projection 90 degrees so the longest face direction maps to `V`. Generated prop atlases should be continuous material swatches; do not proceed with a `_B` map that already paints separate boards, planks, seams, or object parts unless the asset explicitly requires those painted features. Rebuild `UV2` (non-overlapping pack, for the AO bake) whenever `UV1` changes meaningfully; leave `UV3` (tint mask) intact unless deliberately rebuilding it.

For quick Blender previews, temporary camera and light objects are fine, but remove them before saving the export `.blend`. The final export scene should return to the clean mesh+armature structure above.

Before final handoff, reload the saved `.blend` and verify the material uses all expected external maps: `_B` through `UV1`, `_AO` through `UV2`, `_N` through a Normal Map node, `_G` inverted or otherwise converted to roughness for Blender preview, and `_M` into Metallic. Then do one viewport visual check to confirm material placement, not just path wiring.

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
| `-UVCount` | `2` | Number of exported UV maps: `1`, `2`, or `3` |
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
- Names the exported `.cn6`, `.fgx`, and `.geo` files after the single visible armature object
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

Each separately registered asset needs an XLP entry. Geometry-only model instances inside an asset do not get their own entry:
```xml
<Element>
    <m_EntryID text="CSC_Storage_L"/>
    <m_ObjectName text="CSC_Storage_L"/>
</Element>
```

The XLP class is typically `TileBase` for buildings. See the civ6-art skill's art-pipeline reference for full XLP/ArtDef wiring.

### 5. Cook and Test

1. **ModBuddy Build:** Compiles .xlp → .blp, resolves dependencies, generates .dep
2. **Enable mod** in Additional Content
3. **Test in-game:** Verify all 5 states render correctly
4. **Check for:** Missing textures, wrong material assignments, broken burn effect, invisible geometry

---

## CN6ToFGX Settings Reference

| UV maps | Channels | Use Case |
|:---:|----------|----------|
| 1 | Position, Normal, Tangent, Binormal, UV0 | 1 UV map only |
| **2** | + UV1 | **Standard export: 2 UV maps** |
| 3 | + UV1 + UV2, No Bone Bindings | Assets that specifically use a third UV map |

Use `-UVCount 2` unless the asset deliberately uses a third UV map. The 3-UV template has no bone bindings; building bones are hierarchy-only, not vertex-weighted in the FGX sense.

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
