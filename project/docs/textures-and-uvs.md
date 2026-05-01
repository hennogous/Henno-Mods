# Textures and UV Mapping Reference

UV channel architecture, texture atlas system, DDS format details, and the full texture pipeline for Civ 6 building assets.

---

## UV Channel Architecture

Every Civ 6 building mesh has **exactly 3 UV channels**. No more, no fewer. The order matters — the engine reads by index, not name.

### UV1: Diffuse/Albedo (Index 0)

- **Purpose:** Maps to the shared district texture atlas for colour/diffuse
- **Typical utilisation:** 2–8% of 0–1 UV space per building
- **Range:** Can extend outside 0–1 for tiling (brick, wood, ground textures)
  - Market: 0% outside 0–1 (no tiling)
  - Factory: 57% of verts outside 0–1 (heavy tiling on brick/industrial textures)
  - Granary: some tiling on ground textures
- **Island count = mesh island count** — each floating quad gets its own UV island
- Buildings from the same district share the same atlas (e.g., all Encampment buildings use `DIS_ENC_Base`)

### UV2: Lightmap/AO (Index 1)

- **Purpose:** Baked ambient occlusion / lightmap
- **Typical utilisation:** 5–18% per building
- **Range:** Always within 0–1 — **no tiling allowed**
- **Must be non-overlapping** — each surface needs unique lightmap space
- Higher utilisation for complex buildings: Factory 18.5%, Airport 12.2%
- Lower for simple buildings: Market 5.0%, Shrine 4.4%

### UV3: Emissive (Index 2)

- **Purpose:** Night-time window glow, lit elements
- **Typical utilisation:** 0.1–2.5% — tiny areas marking windows/lights
- **Range:** V typically stops at 0.3–0.4 (only bottom third of texture space used)
- **Optional but expected** — not all buildings have meaningful UV3 data
- Controls the `EmissiveEnabled` flag in .ast files

### UV Statistics Across Buildings

| Building | UV1% | UV2% | Outside 0-1 (UV1) | Notes |
|----------|-----:|-----:|-------------------:|-------|
| Market | 3.0% | 5.0% | 0% | No tiling |
| Market (Modern) | 2.5% | — | — | |
| Library | 3.5% | 5.0% | — | |
| Lighthouse | 6.8% | — | — | Tallest cylindrical surface |
| Workshop | 2.5% | — | — | |
| Stable | 4.0% | — | — | |
| Shrine | 2.0% | — | — | Smallest building |
| University | 5.4% | — | — | |
| Madrasa | 5.0% | — | — | |
| Factory | 7.1% | 18.5% | 57% | Heavy tiling |
| Airport | 7.8% | 12.2% | — | |
| Power Plant | 5.1% | — | — | |
| Stadium | 4.8% | — | — | |

---

## Texture Atlas Architecture

### Per-Quarter Albedo Atlas

The CSC mod uses a **1K texture per Quarter** (district building group), divided into 4 quadrants:

```
┌──────────┬──────────┐
│  512×512 │  512×512 │
│  Bldg A  │  Bldg B  │
├──────────┼──────────┤
│  512×512 │  512×512 │
│  Bldg C  │  Bldg D  │
└──────────┴──────────┘
        1024×1024
```

Each 512×512 quadrant holds one building's diffuse texture. Four buildings per 1K atlas.

### Shared Maps (All Quarters Share These)

| Map | Resolution | Format | Purpose |
|-----|-----------|--------|---------|
| AO | 1024×1024 | DDS BC1 | Ambient occlusion — shared across all Quarters |
| Normal | 1024×1024 | DDS BC1 | Surface detail normals — shared |
| Metalness | 1024×1024 | DDS BC1 | Metal mask — shared |
| Gloss | 1024×1024 | DDS BC1 | Roughness (white=shiny, black=dull) — shared |

These reference textures apply to all buildings uniformly. Create them once for the district.

### Emissive (Per Quarter)

| Map | Resolution | Format | Purpose |
|-----|-----------|--------|---------|
| Emissive | 1024×1024 | DDS BC1 | Lit windows/lights — per Quarter |

**Approach:** Copy the UV1 diffuse layout to UV3. Paint lit windows directly on the emissive map. The result is a mostly-black texture with small bright spots.

**DDS/BC1 is block-compressed at fixed size** — a "mostly black" 1K BC1 texture is the same file size as a fully-painted one. There's no space saving from empty areas. Accept this; it's how block compression works.

---

## Texture Types in Detail

### Generic_BaseColor (Diffuse/Albedo)
- **Format:** sRGB RGB
- **Purpose:** Main colour texture. On metallic surfaces, it scales specular instead of diffuse
- **Resolution:** Typically 1024×1024 per district atlas
- **Density:** ~128 pixels per building story is the Firaxis standard
- **Style:** Hand-painted look, visible brushstrokes, muted palette. Not photorealistic.

### Generic_Normal
- **Format:** Tangent-space normal map
- **Purpose:** Surface detail (brick courses, tile edges, wood grain)
- **Generation:** Use Ndo, CrazyBump, or Substance from simplified heightmap. **Never** just desaturate the base colour
- **Note:** Engine post-processes to CLEAN format during cook

### Generic_AO (Ambient Occlusion)
- **Format:** Linear greyscale
- **Purpose:** Baked ambient occlusion for self-shadowing
- **Baking:** Use Marmoset or Substance for AO bakes
- **Maps to UV2** (lightmap channel)

### Generic_Gloss (Roughness)
- **Format:** Linear greyscale
- **Purpose:** Surface roughness. White = shiny, black = dull
- **Key insight:** Variation in gloss creates visual contrast (e.g., wet vs dry roof shingles). This is more important than colour variation for material read.
- **Model:** GGX via dual Beckman lobes

### Generic_Metalness
- **Format:** Linear greyscale
- **Purpose:** Binary mask — metal (white) vs non-metal (black)
- **Usage:** Most building surfaces are non-metallic. Metal only for handles, fixtures, industrial machinery

### Generic_Emissive
- **Format:** sRGB RGB
- **Purpose:** Lit windows, lamps, glowing elements. Added verbatim after linear conversion
- **Maps to UV3** (emissive channel)
- **Usage:** Paint bright spots where windows should glow at night. Rest is black.

### Generic_OPAC (Opacity)
- **Format:** Linear greyscale
- **Purpose:** Transparency mask for alpha-tested elements (awnings, lattice, foliage)
- **Implementation:** Screendoor transparency via MSAA coverage mask (not true alpha blending)

### Generic_TintMask
- **Format:** Linear greyscale
- **Purpose:** Blends between base colour and an external tint colour (set in ArtDef)
- **Usage:** Player colour tinting on banners, flags

### Generic_BurnMap
- **Format:** sRGB RGB
- **Purpose:** Alternate base colour shown during procedural burn effect (pillaged state)
- **Cook params:** GradientScale, BurnHeight control the burn progression

### Generic_LightMap
- **Format:** sRGB RGB
- **Purpose:** Pre-computed global illumination for buildings
- **Maps to UV2**

---

## DDS Format Notes

### BC1 (DXT1) Compression
- **Block-based:** Compresses 4×4 pixel blocks independently
- **Fixed size:** File size is determined by resolution, not content. A black 1K BC1 = same size as detailed 1K BC1
- **Quality:** Good for diffuse/AO. Some banding on smooth gradients
- **Alpha:** 1-bit alpha only (punch-through transparency)

### BC3 (DXT5) Compression
- **Same as BC1** for RGB channels + independent 4-bit alpha channel
- **Use for:** Opacity textures, anything needing smooth alpha gradients

### .tex Companion Files
- Every .dds has a `.tex` wrapper file that the engine loads
- .tex contains internal path references — if you move/rename the .dds, re-cook
- Generated automatically by the ModBuddy cook pipeline

### Common Texture Sizes

| Use | Typical Size | Format |
|-----|-------------|--------|
| Building atlas (per Quarter) | 1024×1024 | BC1 |
| Shared AO/Normal/Metal/Gloss | 1024×1024 | BC1 |
| Emissive | 1024×1024 | BC1 |
| Icons | 256×256 down to 22×22 | BC3 (needs alpha) |
| Strategic view sprites | 256×256 | BC3 |

---

## SDK Pantry Texture Locations

Firaxis SDK provides reference textures at:
```
C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK\
  Assets\DLC\Expansion1\pantry\textures\     (R&F)
  Assets\DLC\Expansion2\pantry\textures\     (GS)
  Assets\pantry\textures\                    (Base game)
```

Texture naming pattern:
```
DIS_{DIST}_{Name}_B.tex     (BaseColor)
DIS_{DIST}_{Name}_N.tex     (Normal)
DIS_{DIST}_{Name}_AO.tex    (Ambient Occlusion)
DIS_{DIST}_{Name}_G.tex     (Gloss)
DIS_{DIST}_{Name}_M.tex     (Metalness)
DIS_{DIST}_{Name}_E.tex     (Emissive)
```

---

## Connecting Textures to Materials in Asset Editor

### Material Setup

1. **Create material** (.mat file) in Materials folder
2. **Material class:** `Landmark` for all buildings
3. **Assign texture maps** to slots:
   - BaseColor → your `_B.tex`
   - Normal → your `_N.tex`
   - AO → your `_AO.tex`
   - Gloss → your `_G.tex`
   - Metalness → your `_M.tex`
   - Emissive → your `_E.tex` (optional)

### Asset-Level AO

AO can be assigned at the **asset level** (in the .ast) instead of per-material. This overwrites material AO and ensures consistent occlusion across multi-material assets.

### FOW (Fog of War) Materials

Every building needs a FOW material variant:
- Assigned in the .ast `FOWMaterial` field
- Standard: `FOW/DefaultMaterial`
- Controls the parchment-style rendering when the building is in fog of war
- `FOWLineDrawing` material controls stroke types. Null = invisible in FOW

### Burn/Snow Materials

Standard assignments in .ast:
- `BurnMaterial` → `DefaultBurnMaterial` (for Pillaged state)
- `SnowMaterial` → `DefaultSnowMaterial` (procedural snow overlay)

---

## Practical UV Workflow

### Step 1: UV1 — Diffuse Atlas
1. Unwrap each floating quad/surface
2. Pack into a small region of the 1K atlas (target 5–10% utilisation)
3. Position in the correct 512×512 quadrant for your building
4. Tiling OK for repeating materials (brick, wood)

### Step 2: UV2 — Lightmap
1. Create second UV layer
2. Unwrap with no overlaps
3. Pack within 0–1 range
4. Every surface needs unique space (this is the AO/lightmap)
5. Can be less precise than UV1 — lightmap detail is subtle

### Step 3: UV3 — Emissive
1. Create third UV layer
2. **Shortcut:** Copy UV1 layout (same islands, same positions)
3. The emissive texture is a separate map — paint lit windows on it
4. Only window/light surfaces need meaningful UV3 coordinates
5. Everything else can share UV space with black emissive regions

### Verification
- Check layer count: must be exactly 3
- Check layer order: diffuse first, lightmap second, emissive third
- Names don't matter to the engine — order does
- The pipeline script auto-creates missing layers but won't reorder existing ones
