---
name: CivAssetForge 3D viewer prototype learnings
description: Technical findings from building the FGX → Three.js viewer prototype (April 2026)
type: project
originSessionId: 6bb875f6-5123-4916-9ed4-ebe06470a02a
---
Core pipeline confirmed working: FGX → CN6 (via FGXToCN6.exe) → GLTF → Three.js with PBR materials + attachments.

## FGX format
- Firaxis-custom GR2, NOT standard Granny3D magic bytes — standard GR2 parsers fail
- `FGXToCN6.exe` at `C:/Users/Shadow/.openclaw/workspace/csc/cn6libs/FGXToCN6.exe` is the confirmed bridge
- **Must run with `cwd` set to its own directory** (loads Firaxis.Granny.dll from same folder)
- CN6 text format: one vertex/line: `pos(3) normal(3) tangent(3) binormal(3) uv1(2) uv2(2) uv3(2) weights(8) bone_indices(8)`, then triangles as `i0 i1 i2 matIndex`

## DDS textures
- Two formats in CSC/pantry:
  - 32-bit RGBA (`bitCount=32` at header offset 88): `_B` (base color) and `_N` (normal) textures
  - 8-bit single-channel (`bitCount=8`): `_AO`, `_M`, `_G` — expand byte → RGBA by duplicating R/G/B
- Pixel rows must be Y-flipped for WebGL (read `bitCount` first to pick the right path)

## UV conventions
- V-flip required: `uv = [u, 1 - v]` — DX top-left origin → GL bottom-left. **Do not remove this.**
- AO map uses UV2 (TEXCOORD_1), not UV1. Export as separate TEXCOORD_1 accessor in GLTF.
- GLTFLoader auto-populates `uv1` from TEXCOORD_1 — no manual copy needed in viewer.

## GLTF custom extension pattern
- Single material: `extensions.CSC_material = { name, baseColor, normal, ao }`
- Multi-material scene: `extensions.CSC_materials = [...]` array + `extensions.CSC_node_materials = [name|null, ...]` per-node index
- Viewer reads these, bypasses GLTF material system entirely (DDS not supported natively)

## Material resolution chain
AST → `m_ObjectName` MATERIAL → `.mtl` file → `m_ObjectName` TEXTURE + `m_ParamName` → `.dds` file

## Atlas textures (known limitation)
- Pantry assets like `DIS_CMP_Base_B` are 1024×1024 multi-civ atlases
- Wall UVs with U up to 10.5 tile across wrong atlas regions — unfixable from geometry alone
- CSC's own textures are 1:1, no atlas issue

## Attachment placement (ast-to-scene.js)
- AST `m_attachmentPoints/m_Points/Element` has position/orientation (euler radians)/scale per attachment
- The `attachRe` regex in ast-to-scene.js was broken at end of prototype session — matched on `m_CookParams` block but that block appears before the transform, and some elements have empty `m_EntryName`
- Working approach from earlier parse: anchor on `newAttachmentPoint` name, then extract EntryName separately
- Euler → quaternion: ZYX order → `eulerToQuat(rx, ry, rz)` 

## Lighting setup (viewer.html)
- Ambient: `0xffeedd` intensity 0.5
- Sun: `0xfff5e0` intensity 2.5, position `(120, 200, 80)`, shadow map 2048×2048
- Fill: `0xaaccff` intensity 0.4, position `(-80, 60, -60)`
- Civ6 is Z-up; group rotated `-Math.PI/2` on X axis

## viewer.html traverse bug (FIXED)
Don't call `group.add(node)` inside `gltf.scene.traverse()`. Three.js traverse iterates `children` as a live array with a cached length — moving nodes to another parent removes them mid-iteration, causing `children[i]` to be undefined and crashing on `.traverse()`. Fix: collect meshes into an array first, then loop over the array to move them.

## Attachment extraction (FIXED)
The working approach for `ast-to-scene.js`: extract the `<m_attachmentPoints>...</m_attachmentPoints>` section first, then anchor on each `<m_position>` block, look backward in the section for the most recent `<m_EntryName text="...">`. Nested `<Element>` tags inside `<m_Values>` break any outer-Element regex. Skip entries with empty asset names (placeholder slots).

Also: add pantry Assets dir to `resolveMaterial` search path for pantry props like `IMP_QuarryREDO_Cart`, `PROP_Haypile`.

## Tile placement offset (CRITICAL — confirmed and fixed)
FGX vertex coordinates for base geometries (e.g. `CSC_Level_1_S`) include the tile placement offset baked in from the Max/Blender scene. The root `Bone` placement bone in the FGX has this offset but FGXToCN6 skips it (no vertex bindings). Attachment `m_position` values in the AST are in tile-local space (relative to tile centre at [0,0,0]).

**Fix:** negate the vertex bounding-box centre as the GLTF node translation for the base geometry:
```js
const centre = minPos.map((v, i) => -((v + maxPos[i]) / 2));
nodes.push({ mesh: result.meshIdx, translation: centre, ... });
```
After fix: building centred near [0,0,0], all attachment positions (Y≈-20) land within the building's Y range (±52). Wind Mill scene looks correct.

## Main geometry material resolution
The base geometry (e.g. `CSC_Level_1_S`) has no matching `.ast` file — its material is in the PARENT asset's AST (e.g. `CSC_BAKERS_Wind_Mill.ast`). Pass the input AST path explicitly to `resolveMaterial()` for main geometry, not the derived geo name.

## CivAssetForge repo
Lives at `C:\Users\Shadow\Desktop\Working Files\Tools\CivAssetForge` — its own git repo, NOT inside CivSupplyChains. GitHub: `https://github.com/hennogous/CivAssetForge`. Contains prototype files + PLAN.md.

## Confirmed working files
- `fgx-to-gltf.js` — single FGX → GLTF with material (oven, water mill confirmed good)
- `ast-to-scene.js` — multi-FGX scene from AST (Wind Mill: 18 meshes, 5 materials, all props correctly placed)
- `serve.js` — HTTP server on 8765, `/tex?path=` endpoint for DDS files
- `viewer.html` — Three.js r163, OrbitControls, GLTFLoader, custom DDS loader

**Why:** Direct FGX parsing via FGXToCN6.exe is Plan A for CivAssetForge. Full Wind Mill scene confirmed: base + tower + 11× Flour_Closed + 3× Flour_Open + cart + haypile, all correctly positioned.
## Obstruction profile findings (May 2026)
- CSC `CSC_BAKERS_Water_Mill.ast` currently leaves `Obstruction Profile` blank and uses `Obstruction Profile AutoGenerate = true`.
- Local art docs describe obstruction blockers as static 2D shapes that block city-building spawn and bend roads; they do not mention dynamic repositioning of attachments.
- Local art docs describe attachment `CullMode=Optional` as removable by city buildings, roads, or water. This appears to be culling-only, not "budge to a nearby slot" behavior.
- Firaxis pantry assets do use explicit named obstruction meshes on many district bases and monuments, so a hand-authored asymmetric `LandmarkObstructionProfile` is a real supported knob.
- Vanilla `DIS_PRD_Watermill.ast` also uses auto-generated obstruction and is attached to the district base as `OPTIONAL`, which suggests Firaxis solved Water Mill fit mostly by reserving space in the host base layout rather than runtime shuffling.
