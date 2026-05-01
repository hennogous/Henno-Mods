# Icons Pipeline Reference

Generating building and district icons for the Civ 6 UI from 3D Blender renders using AI-assisted stylisation.

---

## Pipeline Overview

```
3D Model → Blender Render → img2img (ControlNet Canny + Icon LoRA) → SAM Background Removal → Thick Outline → Final Icon
```

Output: Icon PNGs at multiple sizes (256 down to 22), converted to DDS for the game.

---

## Step 1: Blender Render

Render the building at an isometric angle:
- Camera: orthographic, similar to SV sprite angle but tighter framing
- Resolution: 512×512+ for img2img input
- Background: transparent or solid colour (for easy masking)
- Clean lighting, no post-effects

---

## Step 2: ControlNet Canny Preprocessing

Before img2img, extract edge maps from the render:

### Canny Edge Settings
| Parameter | Value |
|-----------|-------|
| Low threshold | 80 |
| High threshold | 180 |
| Dilate edges | 2px |

Edge dilation (2px) ensures thin architectural details survive the ControlNet guidance. Without dilation, fine window mullions and roof edges can be lost.

---

## Step 3: img2img with ComfyUI

### Setup
- **ComfyUI:** http://127.0.0.1:8188
- **Model:** SDXL 1.0
- **ControlNet:** Canny edge detection
- **LoRA:** Icon LoRA

### Icon LoRA Details
- **Training data:** 106 PNGs (buildings + wonders extracted from SDK)
- **Training:** 2,000 steps
- **Trigger prompt:** `civ 6 icon, cartoon isometric, bold outline, hand-painted, cel-shaded`

### img2img Settings

| Parameter | Value | Notes |
|-----------|-------|-------|
| **ControlNet strength** | 0.90 | High — icons need strong structural fidelity |
| **LoRA strength** | 0.92 | High — icon style is very specific |
| **Denoise strength** | 0.55 | Same as SV pipeline |
| **CFG scale** | 7 | Slightly lower than SV for more natural colours |
| **Steps** | 30 | Full quality |

### Prompt Template
```
civ 6 icon, cartoon isometric, bold outline, hand-painted, cel-shaded,
[building description], single building, clean background
```

Negative prompt:
```
photorealistic, multiple buildings, busy background, noisy, blurry,
thin lines, sketch, watermark, text
```

### Script
`csc/comfyui/icon_img2img.py` — sends render to ComfyUI with ControlNet + LoRA, returns stylised output.

---

## Step 4: Background Removal (SAM)

Use **Segment Anything Model (SAM)** for precise background removal:
- SAM provides a clean alpha mask around the building
- Much better than threshold-based removal for icons (icons have detailed outlines that threshold can eat)
- Run via ComfyUI SAM node or standalone script

---

## Step 5: Post-Processing

### Thick Outer Outline
- **Width:** 28px outer outline
- **Colour:** Dark (near-black, not pure #000)
- **Application:** Applied to the SAM-extracted alpha silhouette
- **Purpose:** Civ 6 icons have a chunky, bold outline — this is a signature visual element

### Resize to Required Sizes
Icons are needed at multiple sizes for different UI contexts:

| Size | Priority | Usage |
|------|----------|-------|
| 256 | Critical | Production panel, Civilopedia header |
| 200 | Medium | Some popups |
| 80 | Medium | Tech/civic tree |
| 64 | Critical | City production list |
| 50 | Critical | District/building tooltips |
| 48 | Medium | Various |
| 38 | Critical | Small UI elements |
| 36 | Medium | Various |
| 32 | Medium | Various |
| 22 | Low | Tiny UI contexts |

Generate at 256 first, then downsample. The 28px outline was calibrated for 256 — it scales proportionally.

### Script
`csc/comfyui/icon_postprocess.py` — SAM extraction, outline application, and multi-size output.

---

## DDS Conversion and Game Integration

### Convert to DDS
```
texconv -f BC3_UNORM -ft DDS -y -o output_dir Icon_MyBuilding_256.png
```

Use BC3 (DXT5) for icons — they need alpha transparency.

### SQL Registration

Icons are registered via SQL loaded with `UpdateIcons` (NOT `UpdateDatabase`):

```sql
-- Icon atlas (one row per size)
INSERT INTO IconTextureAtlases
    (Name, IconSize, IconsPerRow, IconsPerColumn, Filename)
VALUES
    ('ICON_ATLAS_MY_MOD', 256, 1, 1, 'Icon_MyBuilding_256.dds'),
    ('ICON_ATLAS_MY_MOD', 64,  1, 1, 'Icon_MyBuilding_64.dds'),
    ('ICON_ATLAS_MY_MOD', 50,  1, 1, 'Icon_MyBuilding_50.dds'),
    ('ICON_ATLAS_MY_MOD', 38,  1, 1, 'Icon_MyBuilding_38.dds');

-- Icon definition
INSERT INTO IconDefinitions
    (Name, Atlas, 'Index')
VALUES
    ('ICON_BUILDING_MY_BUILDING', 'ICON_ATLAS_MY_MOD', 0);
```

**Important:** Always define both the standard icon and a FOW variant:
```sql
INSERT INTO IconDefinitions (Name, Atlas, 'Index') VALUES
    ('ICON_BUILDING_MY_BUILDING', 'ICON_ATLAS_MY_MOD', 0),
    ('ICON_BUILDING_MY_BUILDING_FOW', 'ICON_ATLAS_MY_MOD_FOW', 0);
```

### XLP Entry
Icons need an XLP entry with class `UITexture`:
```xml
<Element>
    <m_EntryID text="Icon_MyBuilding_256"/>
    <m_ObjectName text="Icon_MyBuilding_256"/>
</Element>
```

---

## Known Limitation: Composition Quality

The icon LoRA learned the **colour palette and rendering style** (cel-shading, bold outlines, hand-painted feel) successfully. However, it did **not** learn single-subject composition well — it sometimes:
- Generates multiple buildings in one icon
- Adds background cityscape elements
- Includes ground/terrain that shouldn't be there

### Root Cause
The 106-image training set included some icons with busy compositions (district icons with multiple buildings, wonder icons with landscape). The LoRA learned "Civ 6 icon style" but not "single isolated building on transparent background."

### Workarounds
1. **Strong ControlNet (0.90):** Forces structural fidelity to the source render
2. **Negative prompting:** "multiple buildings, busy background" helps but isn't 100%
3. **Generate multiples:** Create 4–8 variants and pick the cleanest
4. **Manual cleanup:** Erase stray elements before post-processing

### Proper Fix
Retrain the icon LoRA with a curated dataset of only single-building icons (~50–80 clean examples). Remove all district overview and landscape icons from the training set.

---

## Quick Reference Card

```
Canny edges:       low=80, high=180, dilate 2px
CN strength:        0.90
LoRA strength:      0.92
Denoise:            0.55
CFG:                7
Steps:              30
Sampler:            dpmpp_2m karras
Outline:            28px dark
Output sizes:       256, 64, 50, 38 (minimum)
DDS format:         BC3 (DXT5)
SQL action type:    UpdateIcons (NOT UpdateDatabase)
```
