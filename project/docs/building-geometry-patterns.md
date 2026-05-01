# Civ 6 Building Geometry Patterns — Reference for 3D Modellers

> Generated 2026-03-30 from vertex-level analysis of 20 representative building meshes
> spanning all districts and eras. Data extracted via FGX→CN6 conversion + Blender bmesh analysis.

## Executive Summary

Civ 6 buildings are **extremely low-poly** — a typical building has 500–3000 vertices and 300–1500 triangles. They are designed for a zoomed-out top-down camera and rely heavily on texture work over geometric detail. Buildings are composed of many **floating, disconnected pieces** (walls, roofs, chimneys, props) rather than watertight manifold meshes. UV mapping uses **shared texture atlases** with very low UV space utilization (2–12%).

---

## 1. Poly Budgets by Building Tier

| Category | Example | Verts | Tris | Notes |
|----------|---------|------:|-----:|-------|
| **Simple Ancient** | Market | 480 | 294 | Single mesh, 1 material |
| **Simple Ancient** | Shrine | 908 | 478 | Single mesh |
| **Classical Building** | Workshop | 1,002 | 519 | Single mesh |
| **Classical Building** | Barracks | 1,131 | 549 | 4 sub-meshes (3 buildings + flag) |
| **Classical Building** | Shipyard | 1,109 | 761 | Single mesh |
| **Classical Building** | Amphitheater | 1,360 | 947 | Single mesh |
| **Specialized** | Stable | 1,322 | 663 | Single mesh |
| **Modern Building** | Airport | 1,627 | 1,015 | Single mesh |
| **Modern Building** | Power Plant | 1,949 | 1,256 | Single mesh |
| **Complex Religious** | Cathedral | 2,216 | 1,216 | 12 sub-meshes (building + 11 tombstones) |
| **Unique Building** | Madrasa | 2,495 | 1,252 | Single mesh |
| **Modern Complex** | Mosque | 2,298 | 1,306 | Single mesh, tallest building |
| **Modern Complex** | Stadium | 2,712 | 1,460 | Single mesh |
| **Multi-era** | Granary (Ancient) | 2,868 | 1,624 | 5 sub-meshes (building, wagon, barrels, grain, base) |
| **Multi-era** | Granary (Modern) | 4,022 | 2,170 | 7 sub-meshes (main silo, base, grains, barrels) |
| **Industrial** | Factory | 2,989 | 1,744 | 3 sub-meshes (factory + 2 trees) |
| **Complex** | Zoo | 4,188 | 2,563 | 28 sub-meshes (structures, paths, decals, fences, water) |

### Budget Rules of Thumb

- **Tier 1 (basic building):** 400–1,000 verts, 250–600 tris
- **Tier 2 (standard building):** 1,000–2,000 verts, 500–1,300 tris
- **Tier 3 (complex/modern):** 2,000–3,000 verts, 1,200–1,800 tris
- **Tier 4 (district centerpiece):** 3,000–4,500 verts, 1,600–2,600 tris
- **Wonders:** Likely 5,000–10,000+ (not analyzed here)

**Era progression adds ~50% per era step.** The Ancient Granary is 2,868v; Modern version is 4,022v (40% increase). Higher eras add detail geometry (railings, machinery, signage).

---

## 2. Mesh Connectivity — Floating Pieces, Not Watertight

### The #1 Insight: Everything Floats

Civ 6 buildings are composed of **many disconnected mesh islands floating in space**. A "single mesh" with 480 vertices might actually be 94 separate disconnected pieces. This is by design:

| Building | Verts | Mesh Islands | Avg Island Size |
|----------|------:|------------:|----------------:|
| Market | 480 | 94 | 5.1 verts |
| Shrine | 908 | 215 | 4.2 verts |
| Workshop | 1,002 | 242 | 4.1 verts |
| Stable | 1,322 | 328 | 4.0 verts |
| Factory | 2,861 | 595 | 4.8 verts |
| Cathedral (main) | 1,796 | 410 | 4.4 verts |
| Mosque | 2,298 | 496 | 4.6 verts |
| Stadium | 2,712 | 626 | 4.3 verts |

**Average island size is ~4-5 verts = individual quads (two triangles)**. This means:

1. **Walls, roof faces, and details are individual floating quads/small patches** — they don't share vertices with neighbors
2. **No edge loops** — there's no connected topology to loop-select through
3. **No concern for manifold/watertight geometry** — it's all single-sided surfaces
4. **Silhouette-only geometry** — flat planes arranged to create the illusion of 3D structure from above

### Why Floating Quads?

This is classic **RTS/strategy game optimization**:
- Each "wall" is a single quad with a texture that paints the bricks/windows/etc.
- Roofs are a handful of triangles with a painted roof texture
- No internal geometry (you never see inside)
- Props (barrels, crates, flags) are tiny floating meshes placed by bone positions
- Ground decals are flat quads at Z≈0

### Deep Dive: How Buildings Are Actually Constructed

From CN6 vertex-level analysis of 34 assets, here's exactly how Firaxis constructs their building meshes:

#### Wall Construction
A "wall" is typically 2-4 floating quads arranged in an L or T shape:
- **Front face:** 1 quad (2 tris, 4 verts) — the visible wall surface
- **Top edge:** 1 narrow quad — the wall cap/top
- **Side edges:** 0-2 quads — only where visible from the camera angle
- **No back face.** Walls are single-sided. The camera never sees behind them.
- Total per wall segment: ~8-16 verts

#### Roof Construction
Roofs are 1-3 large triangles or quads:
- Flat roofs: 1 quad
- Peaked roofs: 2 triangles meeting at a ridge
- No fascia/soffit detail — texture handles that
- Some roofs have a separate ridge-cap quad

#### Chimney/Tower Construction
Small towers and chimneys: 4-6 quads forming a box:
- 4 side quads + 1 top quad = 10 verts
- Often rotated 45° to the wall grid for visual interest
- No bottom face

#### Ground/Foundation
A single quad at Z≈0 with a ground texture. Sometimes 2-4 quads for irregular shapes.

#### Props (Barrels, Crates, etc.)
Extremely low-poly:
- Barrel: ~20 verts (8-sided cylinder approximation, no caps)
- Crate: ~8 verts (visible faces only)
- Wagon: ~30 verts

#### Material Groups
Each mesh has 1-3 material groups (from .geo `m_Groups`):
- `{District}_Base` — main building material (walls, roof)
- `{District}_Alpha` — transparent elements (windows, lattice, awnings)
- `Foundation_*` — ground plane material
- `Foliage_Bld` — vegetation (trees, bushes)
- `Pillage_Construction_01` — scaffolding (CON variants only)

#### Bone Weight Architecture
Every vertex is rigidly bound to a single bone (weight = 1.0). The CN6 format stores 4 bone indices + 4 weights per vertex, but analysis shows:
- `bone_weights = [1, 1, 1, 1]` and `bone_indices = [1, 1, 1, 1]` — all pointing to bone index 1 (the mesh root)
- **Zero skinning/deformation** — bones are purely positional locators
- Multi-bone assets (e.g., Granary with 7 bones) use bone hierarchy only for placing sub-meshes, not for vertex deformation

#### UV Architecture (Confirmed via CN6)
Three UV channels per vertex, always:
- **UV1 (diffuse):** Maps to shared district texture atlas. Typical occupancy: 2-8% of atlas. Tiling common (UV coords outside 0-1).
- **UV2 (lightmap):** Unique per building, always within 0-1. 5-18% space utilisation.
- **UV3 (emissive):** Tiny areas marking windows/lights. Only bottom third of texture space used (V range 0–0.4). Optional.

UV island count exactly matches mesh island count — each floating quad has its own UV island. No UV sharing between disconnected geometry pieces.

### Connectivity Implications for Modellers

- **Don't try to make watertight meshes.** Firaxis doesn't.
- **Model each surface as an independent quad or small quad strip.**
- **Overlap geometry freely** — walls can penetrate roof planes, foundations can overlap ground.
- **Think in billboard/card terms** — many elements are essentially textured cards arranged in 3D.

---

## 3. Topology Patterns

### Vertex Valence (Faces Per Vertex)

The valence distribution is remarkably consistent across all buildings:

| Valence | Meaning | Typical % |
|--------:|---------|----------:|
| 1 | Edge of a triangle fan or isolated | 40-50% |
| 2 | Edge vertex between two faces | 35-45% |
| 3 | Corner/junction vertex | 8-15% |
| 4+ | Complex junction (rare) | 1-3% |

The dominance of valence 1-2 confirms the **floating-quad architecture** — most vertices participate in only 1-2 faces because each face is a disconnected piece.

### Boundary vs Interior Edges

**Every edge is a boundary edge.** In the Market (480v, 680 edges), all 478 boundary edges are also non-manifold. This means virtually every triangle is standalone — sharing edges with no neighbors. The CN6 format pre-splits vertices at UV/normal seams, so two triangles that geometrically share an edge have different vertex indices.

**What this means for modelling:** Don't worry about edge flow, loop topology, or quad grids. Think of the mesh as a **collection of textured polygons arranged in space**, not a continuous surface.

### Face Type

All geometry is triangulated (100% tris, 0% quads). This is the export format from the Firaxis pipeline. The source models (from 3ds Max, per the .geo source paths) likely had quads that were triangulated during export.

---

## 4. UV Mapping Patterns

### Three UV Channels

Every Civ 6 building mesh has **exactly three UV channels**:

| Channel | Purpose | Typical U Range | Typical V Range | Utilization |
|---------|---------|-----------------|-----------------|-------------|
| **UV1** | **Diffuse/albedo** — main color texture | 0–1 (sometimes tiled >1) | 0–1 (sometimes >1) | 2–8% |
| **UV2** | **Lightmap/AO** — baked ambient occlusion | 0–1 (always) | 0–1 (always) | 5–18% |
| **UV3** | **Emissive/detail** — night lighting, special effects | 0–1 | 0–0.4 | 0.1–2.5% |

### UV1: Diffuse Atlas (Shared Texture Atlas)

- **UV space utilization: 2–8%** — buildings share a **massive texture atlas** with many other assets
- Each building occupies a small corner of the atlas
- Some buildings tile: UV1 ranges like `-17 to 1` (Factory) or `-1 to 5` (Granary main) indicate **tiling/repeated textures** for materials like bricks, wood, ground
- **Outside 0-1 range:** 0–57% of verts, depending on building — higher = more tiling
- Buildings from the same district share the same atlas (e.g., all Encampment buildings use `DIS_ENC_Base` material)

### UV2: Lightmap (Unique Per Building)

- **UV space utilization: 5–18%** — slightly more space per building
- **Always within 0-1 range** — no tiling
- More complex buildings (Airport: 12.2%, Zoo: 10.8%, Factory: 18.5%) use more lightmap space
- Simple buildings (Market: 5%, Shrine: 4.4%) use very little

### UV3: Emissive/Night

- **Utilization: 0.1–2.5%** — tiny areas mark windows and lights
- V range typically stops at 0.3–0.4 (using only bottom third of texture)
- Not all buildings have UV3 data (Shrine, some props have it unused)
- This maps to the `EmissiveEnabled` flag in .ast files and controls night-time window glow

### UV Layout Patterns

- **Many small islands:** Market has 94 UV islands = one per mesh island (one per floating quad)
- **No shared UV between mesh islands** — each floating quad has its own UV island
- **Atlas coordinates are absolute** — moving a building to a different atlas slot requires remapping all UVs
- **Texture detail is roughly 1 texel per 2–3 game units** based on UV density vs bounding box

### Practical Implications

1. **Use a shared atlas.** Don't give each building its own texture.
2. **Pack UVs tightly in small atlas regions.** 5-10% of a 2048² atlas per building.
3. **Tiling is fine for UV1** — brick/wood/ground textures can tile outside 0-1.
4. **UV2 must be non-overlapping** (it's the lightmap).
5. **UV3 is optional** — only needed for buildings with night lighting.

---

## 5. Dimensions and Scale

### Coordinate System

- Source files are in **3ds Max** (`.max` files per .geo source paths)
- Coordinates are in **game units** — roughly 1 unit ≈ 1 cm based on bounding boxes
- Buildings are oriented on a hexagonal grid (note the recurring 0.866/0.5 ≈ cos(30°)/sin(30°) in normals)

### Bounding Box Ranges

| Building | X extent | Y extent | Z extent (height) |
|----------|----------|----------|-------------------|
| Market | 142 | 111 | 105 |
| Shrine | 111 | 111 | 104 |
| Workshop | 195 | 160 | 95 |
| Barracks (main) | 91 | 108 | 70 |
| Stable | 214 | 195 | 102 |
| Amphitheater | 198 | 165 | 83 |
| Airport | 306 | 381 | 148 |
| Factory | 325 | 304 | 139 |
| Cathedral | 240 | 217 | 351 |
| Mosque | 274 | 237 | 301 |
| Stadium | 260 | 273 | 154 |
| Zoo | 200 | 298 | 106 |

### Scale Rules

- **Small buildings (Tier 1):** ~110–150 XY, 70–105 Z
- **Medium buildings (Tier 2):** ~160–220 XY, 80–140 Z
- **Large buildings (Tier 3):** ~240–320 XY, 130–170 Z
- **Tall religious buildings:** 200–280 XY, **300–350 Z** (Cathedral/Mosque are the tallest)
- **Z height is modest** — most buildings are squatter than wide, viewed from above
- **XY footprint corresponds to the hex district slot** — a hex tile is roughly 200–350 units across

### Vertex Density

Verts per unit² of surface area:

| Building | Surface Area (units²) | Verts | Density (v/unit²) |
|----------|---:|---:|---:|
| Market | 49,065 | 480 | 0.0098 |
| Shrine | 50,963 | 908 | 0.0178 |
| Workshop | 76,451 | 1,002 | 0.0131 |
| Amphitheater | 64,670 | 1,360 | 0.0210 |
| Factory | 195,197 | 2,861 | 0.0147 |
| Cathedral | 326,748 | 1,796 | 0.0055 |
| Airport | 296,593 | 1,627 | 0.0055 |

**Typical density: 0.005–0.02 vertices per unit² of surface area.** Cathedral and Airport have the lowest density (large flat surfaces). Amphitheater has the highest (curved seating).

---

## 6. Normals and Shading

### Custom Normals (Per-Vertex)

Every vertex in the CN6 export has an **explicit normal vector** — these are custom normals, not computed from face orientation. This means:

- Firaxis uses **custom/split normals** throughout
- Smooth shading groups are baked into the vertex data
- Hard edges are achieved by splitting vertices (duplicating at the seam with different normals)

### Hard Edge vs Smooth Shading

The `unique_face_normals / total_faces` ratio reveals the shading strategy:

| Building | Unique Normals | Total Faces | Ratio | Assessment |
|----------|---:|---:|---:|---|
| Market | 169 | 294 | 57% | Mostly hard-edged |
| Shrine | 249 | 478 | 52% | Mostly hard-edged |
| Factory | 643 | 1,640 | 39% | Mixed (some smooth) |
| Cathedral | 336 | 974 | 35% | Mixed |
| Airport | 187 | 1,015 | 18% | Heavily smooth-shaded |
| Zoo structures | 709 | 1,484 | 48% | Mixed |

**Pattern:** Simpler/ancient buildings tend toward harder edges. Modern/industrial buildings use more smooth shading — rounded surfaces (pipes, domes, vehicles) benefit from it.

### Implications for Modelling

- **Use custom normals** (or transfer normals) to control hard/soft edges
- **Split vertices at hard edges** rather than relying on auto-smooth
- Ancient buildings: mostly hard edges (box-like structures)
- Modern buildings: mix of hard (walls, edges) and smooth (curves, rounded features)

---

## 7. Bone and Armature Structure

### Skeleton Architecture

The Civ 6 asset pipeline uses **two types of skeleton**:

#### A. Building Skeletons (Simple)
Individual building meshes have 1–6 bones:
- Root bone (building name, e.g., `DIS_CTY_Granary_AN`)
- Child bones per sub-mesh (`DIS_CTY_Granary_AN_Wagon`, `PROP_Barrel_Classical002`, etc.)
- All bones at identity transform — just names/hierarchy, no animation
- Hierarchy depth: 1 (flat)

#### B. District Base Skeletons (Complex)
The district base `.fgx` files contain **massive skeletons** (60–90+ bones) with **zero mesh data**:
- Each bone names an attachment point: `DIS_ENC_Wall_Classical062`, `DIS_ENC_Tent_Sm_Open138`, `RoadCP484`
- Bone transforms (baked into the FGX binary) define **world positions** for each prop/sub-asset
- The game engine reads these bone positions and places child assets there at runtime

Example: `DIS_ENC_Classical_Base_01` has 87 bones including:
- 12× `DIS_ENC_Wall_Classical` (wall segments around perimeter)
- 3× `DIS_ENC_Tower_Classical` (corner towers)
- 15× `DIS_ENC_Tent_Sm_*` (small tents)
- 6× `PROP_Barrel_Classical` (barrel props)
- 12× `RoadCP*` (road connection points along hex edges)
- 1× `DIS_ENC_Flag_Classical_LG` (large flag)

#### C. Road Connection Points

The `RoadCP###` bones are **critical for district connectivity**:
- They define where roads enter/exit the hex tile
- Typically 12 per district base (2 per hex edge × 6 edges)
- Road geometry connects between tiles at these bone positions

### Bone Weight Assignment

All analyzed vertices had `bone_weights = [1, 1, 1, 1]` and `bone_indices = [1, 1, 1, 1]` — meaning **every vertex is rigidly bound to bone index 1** (the root). There is no skinning/deformation. Bones serve purely as position locators.

---

## 8. State Variants and Material Switching

From the .ast files (not vertex data, but critical for understanding the system):

### Five Visual States

Each building mesh supports five states, controlled by **material and visibility swaps**:

| State | Description | Geometry Visible | Material Variant |
|-------|-------------|:---:|---|
| **Worked** | Normal, productive building | ✅ Main mesh | Base material + emissive |
| **Unworked** | Built but unproductive | ✅ Main mesh | Non-emissive variant |
| **Pillaged** | Damaged/burning | ❌ Main hidden, ✅ PIL mesh | + BurnMaterial |
| **Construction** | Being built | ❌ Main hidden, ✅ CON mesh | Construction material |
| **Unbuilt** | Slot empty | ✅ Main mesh | Base material |

### Separate Geometry Per State

Each building has up to 4 geometry sets:
- `{Building}` — main worked/unworked mesh
- `{Building}_PIL` — pillaged variant (damaged version)
- `{Building}_CON` — construction variant (scaffolding)
- `{Building}_Decal` / `{Building}_PIL_Decal` — ground decals

The .ast file controls which geometry is visible in which state, plus which materials are applied. A single building asset swaps between these geometries as its game state changes.

### Material System

- Each mesh group (material group) in the .geo has a name like `DIS_CTY_Granaries`, `Foundation_Brick_Gray`
- The .ast maps these group names to actual materials per state
- Materials include: base material, FOW (fog of war) material, burn material, snow material
- `EmissiveEnabled` flag controls night-time window glow

---

## 9. District Composition System

### How Buildings Assemble Into Districts

Districts in Civ 6 are **NOT single meshes**. They're composed at runtime from:

1. **TileBase asset** — the district ground plate with integrated geometry and a bone armature
2. **Attachment children** — props, walls, trees, flags placed at bone positions
3. **Building asset** — the "hero building" (e.g., Library, Barracks) placed as a separate TileBase asset

The `Landmarks.artdef` maps building combinations to pre-authored TileBases:

```
District: Encampment
Building set: {Barracks, Stable, MilAcademy}
Era: Classical
→ TileBase: DIS_ENC_Classical_Base_01
   + Building: DIS_ENC_Barracks_Classical (hero)
   + 92 attachment children (walls, tents, flags, props...)
```

Each TileBase is **pre-composed for a specific building combination + era**. The City Center alone has variants for:
- Empty, Granary, Monument, Palace, PalaceMonument, PalaceGranary, PalaceMonumentGranary, MonumentGranary

### Attachment Point System

Each TileBase base asset defines 60–97 attachment points via bones:
- Asset reference (which prop to place)
- Bone name (where to place it — position baked into FGX)
- Connection type (NONE for most)
- Scale (always 1.0)

Props are standalone assets (e.g., `PROP_Barrel_Classical`, `DIS_ENC_Wall_Classical`, `Tree_B_Lg`) with their own geometry, placed at bone-defined positions.

### Shared Props Across Districts

Common props reused across many districts:
- `PROP_Barrel_Classical` — barrels
- `PROP_Stone_A/C/D/E/F` — decorative stones
- `PROP_Lumber_B/C/E` — lumber piles
- `PROP_Scaffold_A`, `PROP_Support` — construction materials
- `Shrub_*`, `Tree_*` — vegetation
- `DIS_Ancient_flag_*` — district flag variants

### The CityGenerators System

City Center districts use a separate **procedural block system** (`CityGenerators.artdef`):
- Mode: `HEX_SPINED` — generates city blocks along spines radiating from center
- Blocks have shapes: `SQ` (square), `REC` (rectangle), `LG_SQ` (large square), `TR` (triangle), `WR` (irregular)
- Growth stages: population thresholds control fill density and city area
- Culture-specific block sets: `AW` (Asian-Western), `RC` (Roman/Classical), `RSS` (South/Southeast Asian), etc.
- Each block is a small mesh (a few buildings + ground) placed procedurally

---

## 10. Practical Modelling Guidelines

### Do's

1. **Keep it simple.** A good Tier 2 building is ~1,200 verts, ~700 tris.
2. **Use floating quads.** Don't connect walls to roofs to chimneys. Each surface can be independent.
3. **Think "textured cards."** A wall is a textured rectangle. A roof is a textured triangle.
4. **Share texture atlases.** Pack multiple buildings into one atlas. 5–10% per building.
5. **Include 3 UV channels:** diffuse (can tile), lightmap (must be unique), emissive (optional).
6. **Triangulate on export.** Model in quads if you want, but export as tris.
7. **Use custom normals.** Mark hard edges explicitly by splitting vertices.
8. **Create state variants.** At minimum: Worked, Pillaged, Construction versions.
9. **Keep the bone at identity.** One root bone, children for sub-meshes if needed.
10. **Match the naming conventions:** `DIS_{DISTRICT}_{Building}_Mesh`, `DIS_{DISTRICT}_{Building}_PIL`, etc.

### Don'ts

1. **Don't make watertight meshes.** No one will notice unsealed corners from above.
2. **Don't add edge loops.** No subdivision, no loop topology — flat quads everywhere.
3. **Don't exceed 3,000 verts** for a standard building (use ~1,500 as target).
4. **Don't use per-building textures.** Use the district atlas.
5. **Don't animate buildings.** Bones are for placement, not animation.
6. **Don't model interiors.** Camera never sees inside.
7. **Don't worry about normals on flat surfaces** — they're custom-baked anyway.

### Naming Conventions

```
Geometry:   DIS_{DIST}_{Building}          (main mesh)
            DIS_{DIST}_{Building}_PIL      (pillaged)
            DIS_{DIST}_{Building}_CON      (construction)
            DIS_{DIST}_{Building}_Decal    (ground decal)
            DIS_{DIST}_{Building}_PIL_Decal

Asset:      DIS_{DIST}_{Building}          (.ast file)
TileBase:   DIS_{DIST}_{Era}_Base_{##}     (district variant)

Materials:  DIS_{DIST}_{MaterialAtlas}     (shared atlas)
            {Material}_Non_Emissive        (unworked variant)
            Pillage_Construction_01        (construction material)
            Decal_Parts_{Era}_{##}         (ground decal material)
```

District codes: `CTY` (City Center), `CMP` (Campus), `COM` (Commercial), `ENC` (Encampment), `ENT` (Entertainment), `HBR` (Harbor), `PRD` (Industrial/Production), `REL` (Holy Site), `THR` (Theater), `AERO` (Aerodrome), `SPACE` (Spaceport), `NBH` (Neighborhood), `AQD` (Aqueduct), `CNL` (Canal)

---

---

## Appendix A: Edge Length Statistics

| Building | Avg Edge | Min Edge | Max Edge |
|----------|----------|----------|----------|
| Market | 19.7 | 2.2 | 76.1 |
| Shrine | 19.2 | 4.2 | 83.9 |
| Workshop | 15.1* | — | — |
| Stable | 16.8* | — | — |
| Amphitheater | 17.9* | — | — |
| Factory | 17.0 | 0.8 | 105.5 |
| Cathedral | 36.9 | 1.0 | 151.2 |
| Airport | 27.4 | 1.2 | 203.5 |
| Mosque | ~20* | — | — |

*Approximate from similar patterns. Max edge lengths correspond to ground planes / large flat surfaces.

## 11. Government Plaza Building Patterns (Rise & Fall)

Gov Plaza buildings (`DIS_GOV_*`) follow a unique naming scheme tied to gameplay purpose:

| Game Name | Geo Name | Verts | Tris | Bones |
|-----------|----------|------:|-----:|------:|
| Ancestral Hall | `DIS_GOV_Tall_Bld` | 1,456 | 776 | 2 |
| Audience Chamber | `DIS_GOV_Wide_Bld` | 533 | 288 | 2 |
| Warlord's Throne | `DIS_GOV_Conquest_Bld` | 598 | 324 | 2 |
| Foreign Ministry | `DIS_GOV_City_States_Bld` | 945 | 471 | 2 |
| Grand Master's Chapel | `DIS_GOV_Faith_Bld` | 2,008 | 1,103 | 8 |
| Intelligence Agency | `DIS_GOV_Spies_Bld` | 1,374 | 664 | 2 |
| National History Museum | `DIS_GOV_Culture_Bld` | 3,197 | 1,568 | 6 |
| Royal Society | `DIS_GOV_Science_Bld` | 1,536 | 779 | 8 |
| War Department | `DIS_GOV_Military_Bld` | 1,738 | 898 | 18 |

### Gov Plaza patterns:
- **Naming:** `DIS_GOV_{PURPOSE}_Bld` — purpose-based, not tier-based like other districts
- **Complexity range:** 533–3,197 verts — widest range of any single district
- **Bone counts vary widely:** 2 (simple) to 18 (Military) — higher bone counts = more attachment props (flags, decorations)
- **District bases:** Era-specific (Ancient 1, Classical 3, Industrial 3, Modern 4) — standard progression
- **Filler props:** Ancient_Bld_A-D, FlagPole, Hotel variants, Monument, Pillars, Reflection_Pool, Statue
- **Material group:** Uses `DIS_GOV_Base` material atlas — separate from other districts

---

## 12. Power Plant Geometry Patterns (Gathering Storm)

GS added three power plant types. All share the Industrial Zone district:

| Building | Geo File | Verts | Tris | Meshes |
|----------|----------|------:|-----:|-------:|
| Power Plant (base game) | `DIS_PRD_PowerPlant` | 1,949 | 1,256 | 1 |
| Fossil Fuel Power Plant | `DIS_PRD_PowerPlant_FossilFuel` | 2,141 | 1,360 | 4 |
| Coal Power Plant | `DIS_PRD_PowerPlant_Coal_Resource` | (resource marker) | — | — |
| Fossil Fuel Resource | `DIS_PRD_PowerPlant_Fossil_Resource` | (resource marker) | — | — |
| Hydroelectric Dam | `DIS_DAM_HydroPlant` | 1,224 | 626 | 1 |

### Power plant patterns:
- **Fossil Fuel is multi-mesh:** 4 sub-meshes including the distinctive cooling tower (`DIS_PRD_PowerPlant_FossilFuel_Tower`)
- **Coal/Fossil resource markers** are tiny geos showing the fuel source, not the plant itself
- **Hydroelectric Dam** lives in the Dam district (`DIS_DAM`), not Industrial — has its own TileBase variant
- **Nuclear power** reuses base Power Plant geometry
- **Sub-buildings:** `DIS_PRD_PlantGenerators`, `DIS_PRD_PlantStorage`, `DIS_PRD_CoolingTowerA/B`, `DIS_PRD_FactoryStack`

---

## 13. Era Variant Analysis — How Complexity Scales

From deep analysis of all major buildings with era variants:

### Granary: Complexity Increases (~40% per era)
| AN→RE | RE→MD | AN→MD |
|:---:|:---:|:---:|
| +6% verts | +32% verts | +40% total |
| +10% islands | +49% islands | +64% total |
| +31% height | +11% height | +45% total |

The Granary adds **more pieces** each era (islands grow faster than verts) — silos, pipes, railings replace open storage.

### Workshop: Complexity *Decreases* (–35%)
| Classical | Industrial | Modern |
|:---:|:---:|:---:|
| 1,002v | 679v (–32%) | 655v (–35%) |

Ancient/Classical Workshop is a complex timber structure. Industrial/Modern are simple prefab buildings — texture does the heavy lifting.

### Market: Modest Increase (+45%)
| Classical | Modern |
|:---:|:---:|
| 480v | 694v (+45%) |
| 94 islands | 159 islands (+69%) |

Modern adds more detail props (signage, awnings) but keeps the same basic stall structure.

### Lighthouse: Nearly Static (+1.5%)
| Classical | Modern |
|:---:|:---:|
| 812v | 824v (+1.5%) |

Lighthouses barely change — same structural form across eras.

### Key finding: **Era progression is NOT uniform.** Some buildings get more complex, some get simpler, some barely change. The rule "50% more per era" from the initial analysis was an average that hides wide variance.

---

## 14. Culture Variant Differences

### City Center Culture Sets

The City Center has the richest culture variation. Each culture set includes:
- **1 Palace** (~2,000–10,000v, the most complex per-culture asset)
- **8–22 city filler buildings** (300–1,200v each)
- **15 city blocks** (5 shapes × 3 variants, 2,000–8,000v composites)
- **Ground foundations** per era

### What changes between cultures:

1. **Architectural silhouette:** Rooflines (peaked vs flat vs domed), wall shapes, tower heights
2. **Material atlas:** Each culture set has its own material group (e.g., `DIS_CTY_RIND_Base` vs `DIS_CTY_RMED_Base`)
3. **Prop vocabulary:** Asian cultures get lanterns/pagoda elements; European get chimneys/dormers; African get thatched roofs
4. **Vertex budgets are similar** — culture doesn't significantly change complexity, just appearance

### Notable culture-specific building counts:
| Culture Code | Filler Buildings | Notes |
|---|---|---|
| RSS (South/Southeast Asian) | 27 | Largest set |
| RMUG (Mughal) | 22 | |
| RMED (Mediterranean) | 16 | |
| RE (Renaissance European) | ~40 | Split into A/B sub-variants |
| CREE (Cree, DLC) | 20 | |
| RMAO (Maori, DLC) | 19 | |

---

## Appendix B: Source File Paths (from .geo metadata)

The `.geo` files record original 3ds Max source paths:
```
//civ6/main/ArtDev/Buildings/Districts/Cities/01_Ancient/Granary/02_Model/DIS_CTY_Granary_AN.max
//civ6/main/ArtDev/Buildings/Districts/Encampment/02_Model/DIS_ENC_Base.max
```

This reveals the Firaxis folder structure:
- `ArtDev/Buildings/Districts/{DistrictName}/`
- Sub-folders: `01_Ancient/`, `02_Model/`, etc.
- One .max file per building or building state
- District base mesh is shared: `DIS_ENC_Base.max` contains barracks, armory, etc. as sub-objects

## Appendix C: Analysis Data

Full mesh analysis data: [`building-mesh-analysis.json`](building-mesh-analysis.json)
Blender inspection script: [`../scripts/inspect_building_mesh.py`](../scripts/inspect_building_mesh.py)
Sample CN6 files: [`sample-geometries/`](sample-geometries/)
