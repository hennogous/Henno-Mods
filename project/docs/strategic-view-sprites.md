# Strategic View Sprites Reference

The pipeline for generating 256×256 strategic view sprites from source/reference images using AI-assisted stylisation via ComfyUI. Blender renders are still fine as inputs, but no longer required.

---

## Pipeline Overview

```
3D Model → Blender Render (512px+) → img2img (ControlNet + SV LoRA) → Post-Process → 256×256 Sprite
```

Each building needs two sprite variants:
- **Normal:** Full-colour sprite for explored territory
- **FOW (Fog of War):** Desaturated/muted variant for fog-covered areas

---

## Step 1: Blender Render Setup

### Building Orientation
- Front face points **-X, -Y** in Blender (isometric camera looking at the front-left corner)
- This matches the SDK pantry sprite orientation
- Camera: orthographic, looking down at ~30° elevation from the front-left

### Render Settings
- Resolution: 512×512 minimum (higher is better for img2img input)
- Background: transparent (RGBA)
- Lighting: simple 3-point or HDRI, no dramatic shadows — the sprite style is flat/painterly
- No post-processing effects (bloom, DOF, etc.)

### Script
`csc/blender/blend_render_sv.py` — automates camera setup, lighting, and render for SV sprite generation.

---

## Step 2: img2img with ComfyUI

### Setup
- **ComfyUI:** http://127.0.0.1:8188
- **Model:** SDXL 1.0 (primary)
- **ControlNet:** Canny edge detection
- **LoRA:** Strategic View LoRA

### SV LoRA Details
- **Training data:** 457 PNG sprites extracted from SDK pantry
- **Training:** 1,500 steps
- **Final loss:** 0.0443
- **Trigger prompt:** `civ 6 strategic view sprite`

### img2img Settings

| Parameter | Value | Notes |
|-----------|-------|-------|
| **Denoise strength** | 0.55 | Balance between source shape and LoRA style |
| **LoRA strength** | 0.6 | Higher = more Civ 6 style, risk losing detail |
| **CFG scale** | 8 | Moderate guidance |
| **Sampler** | dpmpp_2m karras | Best quality/speed balance |
| **Steps** | ~25–30 | Enough for clean result at this denoise |

### Prompt Template
```
civ 6 strategic view sprite, isometric building, [building description],
clean lines, flat colour, simple shadows, game art, white background
```

Negative prompt:
```
photorealistic, 3d render, complex shadows, noisy, blurry, text, watermark
```

### Script
`project/tools/blender/render_to_sv_img2img.py <source-image>` — sends any source/reference image to the ComfyUI API, applies the SV LoRA, and writes the post-processed output to `C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\ComfyUI output`.

---

## Step 3: Post-Processing

### Operations (in order)

1. **Background removal:** Threshold-based (default threshold=15 against black)
   - All near-black pixels become transparent
   
2. **Brightness adjustment:** Multiply by 1.35×
   - SV sprites are slightly washed out / bright compared to the 3D render
   - Matches the SDK pantry sprite palette

3. **Charcoal outline:** 10px outline around the building silhouette
   - Dark charcoal colour (not pure black)
   - Applied to the alpha edge of the building shape
   - This is a defining feature of the Civ 6 SV style

4. **Final resize:** To 256×256 PNG

### Script
`project/tools/blender/add_sv_shadow.py` — applies background removal, brightness, outline, and finalises the sprite. The old hard-edged shadow ellipse is intentionally removed.

### Post-Processing Toggles / Knobs

Every post-processing stage can be toggled from either CLI flags or `CSC_SV_*` environment variables. The same flags work when calling `render_to_sv_img2img.py`, because it forwards them into the post-process pass.

```powershell
py -3.12 project/tools/blender/add_sv_shadow.py "raw.png" "final.png" --no-brightness --outer-outline-px 6 --inner-edge-px 0 --sprite-size 118
py -3.12 project/tools/blender/render_to_sv_img2img.py "source.png" --no-outlines --brightness-factor 1.15
```

| Stage | CLI | Environment variable | Default |
|---|---|---|---|
| Background removal | `--background-removal` / `--no-background-removal` | `CSC_SV_ENABLE_BACKGROUND_REMOVAL` | On |
| Background threshold | `--threshold` | `CSC_SV_BG_THRESHOLD` | `15` |
| Brightness | `--brightness` / `--no-brightness` | `CSC_SV_ENABLE_BRIGHTNESS` | On |
| Brightness factor | `--brightness-factor` | `CSC_SV_BRIGHTNESS_FACTOR` | `1.35` |
| Outlines | `--outlines` / `--no-outlines` | `CSC_SV_ENABLE_OUTLINES` | On |
| Alpha mask threshold | `--mask-alpha-threshold` | `CSC_SV_MASK_ALPHA_THRESHOLD` | `10` |
| Outer outline thickness | `--outer-outline-px` | `CSC_SV_OUTER_OUTLINE_PX` | `10` |
| Inner edge thickness | `--inner-edge-px` | `CSC_SV_INNER_EDGE_PX` | `4` |
| Outline color | `--outline-color` | `CSC_SV_OUTLINE_COLOR` | `#3A3A3A` |
| Outer outline alpha | `--outer-outline-alpha` | `CSC_SV_OUTER_OUTLINE_ALPHA` | `255` |
| Inner edge alpha | `--inner-edge-alpha` | `CSC_SV_INNER_EDGE_ALPHA` | `200` |
| Resize/canvas pass | `--resize-canvas` / `--no-resize-canvas` | `CSC_SV_ENABLE_RESIZE_CANVAS` | On |
| Canvas size | `--canvas-size` | `CSC_SV_CANVAS_SIZE` | `256` |
| Sprite size | `--sprite-size` | `CSC_SV_SPRITE_SIZE` | `110` |
| Paste offset | `--offset-x`, `--offset-y` | `CSC_SV_OFFSET_X`, `CSC_SV_OFFSET_Y` | centered |

`render_to_sv_img2img.py` also mirrors the icon pipeline convention of top-of-file generation knobs with comments and env overrides:

| Generation setting | Environment variable | Default |
|---|---|---|
| ComfyUI URL | `CSC_COMFYUI_URL` | `http://127.0.0.1:8188` |
| Output directory | `CSC_COMFYUI_OUTPUT_DIR` | `C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\ComfyUI output` |
| Denoise | `CSC_SV_DENOISE` | `0.55` |
| LoRA strength | `CSC_SV_LORA_STR` | `0.6` |
| CFG variants | `CSC_SV_CFG_VALUES` | `8` |
| Steps | `CSC_SV_STEPS` | `25` |
| Seed | `CSC_SV_SEED` | `42` |
| Sampler / scheduler | `CSC_SV_SAMPLER`, `CSC_SV_SCHEDULER` | `dpmpp_2m`, `karras` |
| Checkpoint / LoRA | `CSC_SV_CHECKPOINT`, `CSC_SV_LORA_NAME` | `sd_xl_base_1.0.safetensors`, `civ6_strategic_view.safetensors` |
| Prompts | `CSC_SV_PROMPT`, `CSC_SV_NEGATIVE` | tuned defaults |

---

## Gotchas

### Green-Roofed Buildings
The threshold-based background removal (step 3.1) fails when roofs are green — it can't distinguish green roof from green background foliage or can merge with white.

**Workarounds:**
- **Manual trace:** Use a selection tool to isolate the building manually before post-processing
- **Magenta background:** Render on a magenta (#FF00FF) background instead of white, then key out magenta. No natural building colour is close to magenta

### Multiple Generations
img2img with ControlNet is non-deterministic. Generate 4–8 variants and pick the best. Look for:
- Clean silhouette matching the 3D source
- Consistent colour palette with existing SDK sprites
- No artefacts or extra structures in the background

### FOW Variant
The FOW sprite should be:
- Same composition as the normal sprite
- Desaturated (reduce saturation ~70%)
- Slightly darker/muted
- Can be generated by post-processing the normal sprite — no separate img2img needed

---

## Sprite Size Requirements

Strategic view sprites referenced from ArtDefs:

| Context | Size | Format |
|---------|------|--------|
| Main sprite | 256×256 | DDS BC3 (RGBA) |
| FOW variant | 256×256 | DDS BC3 (RGBA) |

### Naming Convention
```
Icon_{BuildingName}_256.dds          (normal)
Icon_{BuildingName}_FOW_256.dds      (fog of war)
```

### DDS Conversion
Convert final PNG to DDS BC3 (DXT5) with alpha channel:
- Use `texconv.exe` (DirectXTex) or NVIDIA Texture Tools
- Wrap in a `.tex` file for the Civ 6 engine (generated by cook pipeline)

---

## Strategic View Coordinate System

For reference when placing sprites in ArtDefs:

- Origin `(0.0, 0.0)` at hex center
- X range: -0.5 to 0.5
- Y range: -0.57 to 0.57
- Each sprite entry has: `Visible_XLPEntry`, `Visible_TopLeft`, `Visible_BottomRight`
- TopLeft/BottomRight allow atlassed textures (sub-regions of a larger sheet)

### Placement Rules

| Rule | Use |
|------|-----|
| `Centered` | Single building centered on hex |
| `Centered_NotScaled` | No vertical squish (maintains aspect) |
| `Centered_Random` | Random pick from variants |
| `OneEntryPerTile` | Multi-tile wonders |

Most custom buildings use `Centered` or `Centered_NotScaled`.

---

## Integration with ArtDefs

Each building needs entries in **three ArtDefs** for strategic view:

### 1. StrategicView.artdef
Registers the sprite XLP entries under the Buildings collection with states: Completed, Pillaged, UnderConstruction.

### 2. Buildings.artdef
Each building entry has a `StrategicView` sub-collection with entries for each build state.

### 3. Districts.artdef
District entry has a `StrategicView` sub-collection for the district icon itself.

See the **civ6-modding** skill's art-pipeline reference for full ArtDef wiring details.
