# Geometry Patterns Reference

> From vertex-level analysis of 34 building meshes across all districts and eras.
> Data extracted via FGX→CN6 conversion + Blender bmesh analysis.

## The Fundamental Insight: Everything Floats

Civ 6 buildings are composed of **many disconnected mesh islands floating in space**. A "single mesh" with 480 vertices is actually 94 separate disconnected pieces. This is by design — classic RTS/strategy game optimisation for a zoomed-out top-down camera.

| Building | Verts | Mesh Islands | Avg Island Size |
|----------|------:|------------:|----------------:|
| Market | 480 | 94 | 5.1 verts |
| Shrine | 908 | 215 | 4.2 verts |
| Workshop | 1,002 | 242 | 4.1 verts |
| Stable | 1,322 | 328 | 4.0 verts |
| Library | 999 | 231 | 4.3 verts |
| University | 2,742 | 632 | 4.3 verts |
| Factory | 2,989 | 595 | 4.8 verts |
| Cathedral | 2,216 | 410 | 4.4 verts |
| Mosque | 2,298 | 496 | 4.6 verts |
| Stadium | 2,712 | 626 | 4.3 verts |
| Granary (AN) | 2,868 | 526 | 4.4 verts |
| Granary (MD) | 4,022 | 862 | 4.2 verts |

**Average island size is ~4–5 verts = individual quads (two triangles).** This holds across every building analysed. The Lighthouse is the notable exception at 7.1 avg — its cylindrical tower uses slightly larger connected patches.

### Why Floating Quads?

- Each "wall" is a textured rectangle — the bricks/windows/trim are painted on
- Roofs are a handful of triangles with a painted roof texture
- No internal geometry (camera never sees inside)
- Props (barrels, crates, flags) are tiny floating meshes placed by bone positions
- Ground decals are flat quads at Z≈0
- No edge loops — there's no connected topology to loop-select through
- No manifold/watertight requirement — all single-sided surfaces
- Silhouette-only geometry — flat planes creating the illusion of 3D from above

---

## How Buildings Are Constructed

### Wall Construction
A "wall" is typically 2–4 floating quads:
- **Front face:** 1 quad (2 tris, 4 verts) — the visible wall surface
- **Top edge:** 1 narrow quad — the wall cap
- **Side edges:** 0–2 quads — only where visible from camera angle
- **No back face.** Walls are single-sided.
- Total per wall segment: ~8–16 verts

### Roof Construction
1–3 large triangles or quads:
- Flat roofs: 1 quad
- Peaked roofs: 2 triangles meeting at a ridge
- No fascia/soffit detail — texture handles that
- Some roofs have a separate ridge-cap quad

### Chimney/Tower Construction
4–6 quads forming a box:
- 4 side quads + 1 top quad = ~10 verts
- Often rotated 45° to the wall grid for visual interest
- No bottom face

### Ground/Foundation
A single quad at Z≈0 with ground texture. Sometimes 2–4 quads for irregular shapes.

### Props
Extremely low-poly:
- Barrel: ~20 verts (8-sided cylinder approximation, no caps)
- Crate: ~8 verts (visible faces only)
- Wagon: ~30 verts

---

## Topology Patterns

### Vertex Valence

| Valence | Meaning | Typical % |
|--------:|---------|----------:|
| 1 | Edge of triangle fan or isolated | 40–50% |
| 2 | Edge vertex between two faces | 35–45% |
| 3 | Corner/junction vertex | 8–15% |
| 4+ | Complex junction (rare) | 1–3% |

Dominance of valence 1–2 confirms the floating-quad architecture — most vertices participate in only 1–2 faces.

### Edge Characteristics

**Every edge is a boundary edge.** In the Market (480v, 680 edges), all boundary edges are also non-manifold. CN6 format pre-splits vertices at UV/normal seams, so two triangles sharing a geometric edge have different vertex indices.

**Don't worry about edge flow, loop topology, or quad grids.** The mesh is a collection of textured polygons arranged in space, not a continuous surface.

### Face Types
All geometry is 100% triangulated. Source models (3ds Max per .geo paths) likely had quads triangulated during export. Model in quads if you want — triangulate on export.

---

## Normals and Shading

### Custom Normals
Every vertex has an **explicit normal vector** — custom/split normals baked into vertex data. Hard edges are achieved by splitting vertices at seams with different normals.

### Hard vs Smooth by Era

| Building | Unique Normals/Total Faces | Assessment |
|----------|---------------------------:|------------|
| Market | 57% | Mostly hard-edged |
| Shrine | 52% | Mostly hard-edged |
| Factory | 39% | Mixed |
| Cathedral | 35% | Mixed |
| Airport | 18% | Heavily smooth-shaded |

**Pattern:** Ancient/simple buildings tend toward hard edges (box-like structures). Modern buildings mix hard (walls, edges) with smooth (pipes, domes, curves).

**For modelling:** Use custom normals to control hard/soft edges. Split vertices at hard edges. Don't rely on auto-smooth.

---

## Material Slot Patterns

Each mesh has 1–3 material groups:
- `{District}_Base` — main building material (walls, roof)
- `{District}_Alpha` — transparent elements (windows, lattice, awnings)
- `Foundation_*` — ground plane material
- `Foliage_Bld` — vegetation (trees, bushes)
- `Pillage_Construction_01` — scaffolding (CON variants only)

---

## Bone Weight Architecture

All analysed vertices: `bone_weights = [1, 1, 1, 1]` and `bone_indices = [1, 1, 1, 1]` — every vertex rigidly bound to bone index 1 (mesh root). CN6 stores 4 indices + 4 weights per vertex, but there is **zero skinning/deformation**.

Multi-bone assets (e.g., Granary with 7 bones) use hierarchy only for placing sub-meshes, not vertex deformation.

### Building Skeletons (1–6 bones)
- Root bone named after asset (e.g., `DIS_CTY_Granary_AN`)
- Child bones per sub-mesh (wagon, barrels, etc.)
- All at identity transform, hierarchy depth 1

### District Base Skeletons (60–90+ bones)
These are **skeleton-only** FGX files with zero mesh data:
- Attachment points: `DIS_ENC_Wall_Classical062`, `DIS_ENC_Tent_Sm_Open138`
- Road connections: `RoadCP484` (typically 12 per district, 2 per hex edge)
- Props: `PROP_Barrel_Classical003`, `DIS_ENC_Flag_Classical_LG`

Example: `DIS_ENC_Classical_Base_01` has 87 bones: 12 walls, 3 towers, 15 tents, 6 barrels, 12 road CPs, 1 flag, plus misc.

---

## Dimensions and Scale

### Coordinate System
- Game units: roughly 1 unit ≈ 1 cm (based on bounding boxes)
- Hex grid orientation: recurring cos(30°)/sin(30°) in normals

### Bounding Box Ranges by Building Size

| Category | XY Extent | Z Height | Examples |
|----------|----------|----------|----------|
| Small (T1) | 110–150 | 70–105 | Market, Shrine, Barracks |
| Medium (T2) | 160–220 | 80–140 | Workshop, Stable, Amphitheater |
| Large (T3) | 240–320 | 130–170 | Airport, Factory, Stadium |
| Tall religious | 200–280 | **300–350** | Cathedral (351 Z), Mosque (301 Z) |

Most buildings are squatter than wide — viewed from above, XY footprint matters more than Z height. Exception: religious buildings punch upward dramatically.

### Vertex Density
Typical: 0.005–0.02 vertices per unit² of surface area. Cathedral and Airport are lowest density (large flat surfaces). Amphitheater highest (curved seating geometry).

### Edge Lengths
Average edge: 15–37 game units. Market averages 19.7; Cathedral 36.9. Max edges correspond to ground planes (76–203 units).

---

## District Composition System

Districts are **NOT single meshes**. They're composed at runtime from:

1. **TileBase asset** — ground plate with integrated geometry + bone armature
2. **Attachment children** — props, walls, trees, flags placed at bone positions
3. **Building asset** — the "hero building" placed as a separate TileBase

The `Landmarks.artdef` maps building combinations to pre-authored TileBases. Each TileBase is pre-composed for a specific building combination + era. Example:

```
District: Encampment
Buildings: {Barracks, Stable, MilAcademy}
Era: Classical
→ TileBase: DIS_ENC_Classical_Base_01
   + Building: DIS_ENC_Barracks_Classical (hero)
   + 92 attachment children (walls, tents, flags, props...)
```

### Shared Props Across Districts
Common reused assets:
- `PROP_Barrel_Classical`, `PROP_Stone_A/C/D/E/F`, `PROP_Lumber_B/C/E`
- `PROP_Scaffold_A`, `PROP_Support` (construction)
- `Shrub_*`, `Tree_*` (vegetation)
- `DIS_Ancient_flag_*` (district flags)

### CityGenerators System
City Center districts use procedural block generation (`CityGenerators.artdef`):
- Mode: `HEX_SPINED` — blocks along spines from center
- Shapes: SQ (square), REC (rectangle), LG_SQ, TR (triangle), WR (irregular)
- Culture-specific block sets: AW, RC, RSS, RE, etc.
- Growth stages tied to population thresholds

---

## Era Variant Analysis

How complexity scales across eras — it's **NOT uniform**:

### Granary: +40% (AN→MD)
| Era | Verts | Islands | Height |
|-----|------:|--------:|-------:|
| Ancient | 2,868 | 526 | 108 |
| Renaissance | 3,036 (+6%) | 578 (+10%) | 141 (+31%) |
| Modern | 4,022 (+40%) | 862 (+64%) | 157 (+45%) |

Modern adds more **pieces** (islands grow faster than verts) — silos, pipes, railings replace open storage.

### Workshop: –35% (Classical→Modern)
| Classical | Industrial | Modern |
|:---------:|:----------:|:------:|
| 1,002v | 679v (–32%) | 655v (–35%) |

Ancient Workshop is complex timber. Modern is simple prefab — texture does the heavy lifting.

### Market: +45% (Classical→Modern)
More detail props (signage, awnings) but same basic structure.

### Lighthouse: +1.5% (barely changes)
Same structural form across eras, just texture differences.

**Key finding:** Some buildings get more complex, some simpler, some barely change. The "50% more per era" rule is an average that hides wide variance. Match the original building's pattern for the era you're targeting.

---

## Culture Variant Differences

City Center has the richest culture variation. Each culture set includes:
- 1 Palace (2,000–10,000v — most complex per-culture asset)
- 8–22 city filler buildings (300–1,200v each)
- 15 city blocks (5 shapes × 3 variants, 2,000–8,000v composites)
- Ground foundations per era

### What Changes Between Cultures
1. **Silhouette:** Rooflines (peaked vs flat vs domed), wall shapes, tower heights
2. **Material atlas:** Each culture has its own (e.g., `DIS_CTY_RIND_Base` vs `DIS_CTY_RMED_Base`)
3. **Prop vocabulary:** Asian → lanterns/pagoda; European → chimneys/dormers; African → thatch
4. **Vertex budgets similar** — culture doesn't significantly change complexity, just appearance

---

## Naming Conventions

```
Geometry:   DIS_{DIST}_{Building}          (main mesh)
            DIS_{DIST}_{Building}_PIL      (pillaged)
            DIS_{DIST}_{Building}_CON      (construction)
            DIS_{DIST}_{Building}_Decal    (ground decal)

Asset:      DIS_{DIST}_{Building}          (.ast file)
TileBase:   DIS_{DIST}_{Era}_Base_{##}     (district variant)

Materials:  DIS_{DIST}_{MaterialAtlas}     (shared atlas)
            {Material}_Non_Emissive        (unworked variant)
            Pillage_Construction_01        (construction material)
```

District codes: `CTY` (City Center), `CMP` (Campus), `COM` (Commercial), `ENC` (Encampment), `ENT` (Entertainment), `HBR` (Harbor), `PRD` (Industrial), `REL` (Holy Site), `THR` (Theater), `AERO` (Aerodrome), `SPACE` (Spaceport), `NBH` (Neighborhood), `AQD` (Aqueduct), `CNL` (Canal), `GOV` (Government Plaza), `DAM` (Dam).

---

## Do's and Don'ts

### Do
1. Keep it simple — target ~1,200v / ~700t for Tier 2
2. Use floating quads — each surface independent
3. Think "textured cards" — a wall is a textured rectangle
4. Share texture atlases — 5–10% of a 1K atlas per building
5. Include 3 UV channels (diffuse can tile, lightmap unique, emissive optional)
6. Triangulate on export
7. Use custom normals — mark hard edges by splitting vertices
8. Create state variants (Worked, Pillaged, Construction)
9. Keep the bone at identity — one root, children for sub-meshes
10. Match naming conventions

### Don't
1. Make watertight meshes — no one notices from above
2. Add edge loops — no subdivision, flat quads everywhere
3. Exceed 3,000 verts for a standard building
4. Use per-building textures — use the district atlas
5. Animate buildings — bones are for placement only
6. Model interiors — camera never sees inside
7. Put colons in bone names — corrupts FGX silently
