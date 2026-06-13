# ComfyUI & LoRA — Practical Manual for CSC Art Generation

This covers the two main pipelines you'll actually use for CSC:
1. **Building icons** — game UI icons for districts, buildings, resources
2. **Strategic view sprites** — 256×256 in-map sprites that appear on the hex grid

Both pipelines use ComfyUI as the generation engine, custom-trained LoRAs for Civ 6 style, and Python post-processing scripts to finalise the output.

---

## Background: What Is ComfyUI

ComfyUI is a node-based UI for running Stable Diffusion locally. Think of it like a visual programming tool — each "node" does one thing (load a model, encode a prompt, run the sampler, save an image), and you wire them together into a workflow.

You don't need to build workflows from scratch for CSC — the scripts in `project/tools/comfyui/` handle that via the API. You'll mainly use the browser UI to monitor generation, inspect results, and experiment manually.

---

## Step 1: Start the Server

Open a PowerShell terminal and run:

```powershell
cd C:\Users\Shadow\ComfyUI
py -3.12 main.py --listen 127.0.0.1 --port 8188
```

If `py -3.12` is not available, use the full Python path instead:

```powershell
C:\Users\Shadow\AppData\Local\Programs\Python\Python312\python.exe main.py --listen 127.0.0.1 --port 8188
```

Do **not** use plain `python` unless you've verified it points to the normal Python 3.12 install. On this machine, `python` can resolve to the Hermes Agent virtual environment first:

```text
C:\Users\Shadow\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe
```

That environment is for Hermes, not ComfyUI, and may be missing ComfyUI dependencies such as `SQLAlchemy`.

Wait for the line:

```
To see the GUI go to: http://127.0.0.1:8188
```

Then open `http://127.0.0.1:8188` in a browser. Leave the terminal running — it's the server process, closing it stops generation.

> The server does not auto-start on boot. You need to start it manually each session.

---

## Step 2: The ComfyUI Interface

The browser UI has three key areas:

| Area | What it is |
|---|---|
| **Canvas** (centre) | The node graph. Each box is a node; wires connect them. |
| **Queue / History** (right sidebar) | Shows pending and completed generations. Click a history entry to see its settings. |
| **Output folder** | `C:\Users\Shadow\ComfyUI\output\` — all generated images land here. |

You don't need to edit the graph for normal use. The scripts send their own workflows via the API.

---

## The LoRAs Available

| File | What it does | Trigger |
|---|---|---|
| `civ6_icons.safetensors` | Custom-trained on Civ 6 icon artwork. Produces bold outlines, cel-shaded style, muted earthy palette. | `civ 6 icon` |
| `civ6_strategic_view.safetensors` | Custom-trained on 457 SDK pantry sprites (1,500 steps, loss 0.0443). Produces flat painterly sprites in the Civ 6 SV style. | `civ 6 strategic view sprite` |
| `cartoon_3d_isometric.safetensors` | Isometric chunky-toy building style. Good for concept sketches. | `j_game_background` |
| `game_icon_v1.safetensors` | Generic game icon style (pre-CSC, less tailored). | `2d icon.` |

For production CSC assets, use `civ6_icons` and `civ6_strategic_view`. The others are for exploration.

---

## Pipeline 1: Building Icons

### What You Need

A reference image of the building — a screenshot, a concept sketch, a render from Blender, even a photo of a real-world analogue. The script uses it as an img2img source (ControlNet Canny holds the structure, the LoRA rewrites the style).

### Running the Script

```powershell
cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods"
py -3.12 project/tools/comfyui/icon_pipeline/icon_img2img.py "C:\path\to\your\source_image.png"
```

The script:
1. Extracts Canny edges from your source image
2. Uploads both images to ComfyUI
3. Runs SDXL with `civ6_icons.safetensors` (strength 0.92) + ControlNet Canny (strength 0.90)
4. Waits for completion, then runs post-processing automatically (background removal + outline + centering)

### Output

Raw generation (pre-post-process) and final cleaned icon both go to:

```
C:\Users\Shadow\.openclaw\workspace\tmp\
  icon_v3_raw_1.png    ← raw ComfyUI output
  icon_v3_1.png        ← post-processed final
```

Final icons are 1024×1024 RGBA with transparent background.

### Generation Settings (what the script uses)

| Setting | Value | Why |
|---|---|---|
| Model | SDXL 1.0 | Better quality than SD 1.5 for this style |
| LoRA | `civ6_icons.safetensors` | CSC custom-trained |
| LoRA strength | 0.92 | Strong style push — go lower (0.7–0.8) if structure is getting lost |
| Denoise | 0.55 | Medium freedom — respects source shape but allows style rewrite |
| CFG | 7.0 | Balanced guidance |
| ControlNet strength | 0.90 | Holds geometry firmly |
| Sampler | dpmpp_2m / karras | Best quality/speed balance |
| Steps | 30 | Enough for clean result at this denoise |

### Prompt Template

The script's built-in prompt is tuned for Bakers' Quarter buildings. To change it for other quarters, edit `PROMPT` at the top of `icon_img2img.py`:

```python
PROMPT = (
    "civ 6 icon, cartoon isometric, bold black outlines, outlined illustration, "
    "thick stroke, hand-painted, cel-shaded, sticker style, "
    "classical era [YOUR BUILDING TYPE], [MATERIALS], warm earthy tones, "
    "olive green roof tiles, game building icon, single building centered, "
    "isometric 3/4 view, muted palette, painterly brush strokes, "
    "black outline on every architectural element, outline art style"
)
```

Useful substitutions:
- `classical era bakery, stone oven, timber framing`
- `classical era loom house, wooden frame, woven textiles`
- `medieval apothecary, stone walls, herb garden`

### Post-Processing Breakdown

After generation, `icon_postprocess.py` runs automatically:

1. **Padding** — adds neutral grey border so rembg sees clean background edges
2. **Background removal** — `rembg` (U2-Net) isolates the building from whatever background SD generated
3. **Structural outlines** — Canny edges painted dark on the building interior (sharpens the cel-shaded look)
4. **Silhouette outline** — 14px thick dark border around the entire building shape (defining Civ 6 icon feature)
5. **Centering** — scales content to fill 704×704 within a 1024×1024 canvas with consistent padding

To run post-processing on an existing raw file manually:

```powershell
py -3.12 project/tools/comfyui/icon_pipeline/icon_postprocess.py "path\to\raw.png" "path\to\output.png"
```

### Getting Multiple Variants

The script runs one seed (2025) by default. To generate variants, edit `SEEDS` in the script:

```python
SEEDS = [2025, 1337, 99, 42, 777]
```

Each seed produces a different composition. Generate 4–6 and pick the best one. Look for:
- Clean silhouette matching the source building
- Consistent earthy/olive colour palette
- No spurious background elements
- Outline intact on all major shapes

---

## Pipeline 2: Strategic View Sprites

### What You Need

A source/reference image of the building — a sketch, screenshot, Blender render, or photo. A Blender render is optional now, not a prerequisite.

### Optional: Blender Render

Camera setup (must match Civ 6 SV orientation):
- Building front face pointing **-X, -Y** (front-left corner faces the camera)
- Orthographic camera, ~30° elevation, looking at front-left
- Resolution: 512×512 minimum
- Background: white (not transparent — the post-processing handles removal)
- No dramatic shadows; flat lighting is fine

Run the automated render script from inside Blender's scripting console, or via command line:

```
blender --background your_model.blend --python project/tools/blender/blend_render_sv.py
```

Output: a PNG render at the configured path.

### Step 2b: img2img via Script

```powershell
py -3.12 project/tools/blender/render_to_sv_img2img.py "C:\path\to\source_image.png"
```

This script:
1. Uploads the source/reference image to ComfyUI
2. Runs SDXL with `civ6_strategic_view.safetensors`
3. Writes the post-processed SV PNG to `C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\ComfyUI output`

| Setting | Value |
|---|---|
| LoRA | `civ6_strategic_view.safetensors` |
| LoRA strength | 0.6 |
| Denoise | 0.55 |
| CFG | 8 |
| Sampler | dpmpp_2m karras |
| Steps | 25–30 |

### Step 2c: Post-Processing

```powershell
py -3.12 project/tools/blender/add_sv_shadow.py "path\to\sv_output.png" "path\to\final.png"
```

This applies in order:
1. **Background removal** — threshold 15 against black
2. **Brightness boost** — 1.35× to match the washed-out SDK pantry palette
3. **Charcoal outline** — 10px border (defining SV style feature)
4. **Resize** — to 256×256 PNG

If no output path is supplied, the default output directory is `C:\Users\Shadow\Desktop\Working Files\2D Art\Quarters\ComfyUI output`.

All post-processing stages have CLI toggles and knobs. These flags work on both `add_sv_shadow.py` and the end-to-end `render_to_sv_img2img.py` script:

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

### Step 2d: FOW Variant

The fog-of-war sprite is the normal sprite desaturated. No second generation needed — post-process the final PNG:

```python
from PIL import Image, ImageEnhance
img = Image.open("sprite_normal.png").convert("RGBA")
r, g, b, a = img.split()
grey = ImageEnhance.Color(Image.merge("RGB", (r, g, b))).enhance(0.3)
fow = Image.merge("RGBA", (*grey.split(), a))
fow.save("sprite_FOW.png")
```

### Gotcha: Green Roofs

Threshold-based background removal breaks when roofs are green — it can confuse green with the white background's colour channel values, or fail to separate the building cleanly.

Fix: render on a **magenta background** (`#FF00FF`) and key that out instead:

```python
arr = np.array(img)
is_magenta = (arr[:, :, 0] > 200) & (arr[:, :, 1] < 50) & (arr[:, :, 2] > 200)
arr[is_magenta] = [0, 0, 0, 0]
```

### How Many Variants to Generate

img2img with ControlNet is non-deterministic. Generate 4–8 variants per building (change seed), then choose the cleanest one. Look for:
- Silhouette matches the 3D source
- Palette matches existing SDK pantry sprites (muted, earthy, slightly washed out)
- No extra structures or artefacts in the background
- Clean outline around the building

---

## Step 3: Final Format Conversion

Both pipelines produce PNGs. For Civ 6 you need DDS BC3 (DXT5 with alpha).

Using `texconv.exe` (DirectXTex):

```powershell
texconv.exe -f BC3_UNORM -y "path\to\icon.png"
```

For the `.tex` wrapper (required by the cook pipeline), the Asset Editor handles this when you import — drop the DDS into the ArtDef asset, cook, done.

Icon naming convention:

```
Icon_BUILDING_CSC_BAKERS_OVEN_256.dds
Icon_BUILDING_CSC_BAKERS_OVEN_FOW_256.dds   ← SV sprites only
```

---

## Quick Reference: Which Script for What

| Task | Script | Input | Output |
|---|---|---|---|
| Generate building icon from reference image | `project/tools/comfyui/icon_pipeline/icon_img2img.py <image>` | Any PNG/JPG | 1024×1024 RGBA PNG |
| Post-process a raw icon manually | `project/tools/comfyui/icon_pipeline/icon_postprocess.py <raw> <out>` | Raw ComfyUI PNG | Cleaned 1024×1024 RGBA PNG |
| Generate SV sprite from source image | `project/tools/blender/render_to_sv_img2img.py <source-image>` | Any PNG/JPG reference image | 256×256 SV PNG in ComfyUI output folder |
| Apply outline/resize to SV sprite | `project/tools/blender/add_sv_shadow.py <in> [out]` | SV PNG | 256×256 PNG |
| Automated Blender camera + render | `project/tools/blender/blend_render_sv.py` | .blend file | 512×512 render PNG |

---

## Tuning Guide

There are three independent knobs, and understanding what each one does lets you diagnose problems without guessing.

---

### Knob 1: How Closely the Output Follows the Input Image

These two settings control **input fidelity** — how much the source image's structure is preserved vs. reinterpreted.

#### Denoise strength (`DENOISE`)

This is the most important knob. It controls how much the sampler is allowed to change the image.

| Value | Effect |
|---|---|
| 0.20–0.35 | Source shape dominates — output looks like a re-coloured version of the input |
| 0.45–0.55 | **Good default** — LoRA rewrites the style but keeps the building's structure |
| 0.65–0.80 | Heavy creative freedom — may invent details, change proportions |
| 0.90–1.00 | Essentially txt2img — ignores the source almost entirely |

If output looks nothing like your source building, lower denoise. If it's barely changing, raise it.

#### ControlNet strength (`CN_STRENGTH`)

ControlNet Canny extracts edge lines from your source and enforces them during sampling. This acts as a second fidelity constraint on top of denoise.

| Value | Effect |
|---|---|
| 0.50–0.70 | Loose — edges suggest shapes but don't rigidly lock them |
| 0.80–0.95 | **Good default** — structural lines are held, style can still breathe |
| 1.00+ | Hard lock — output exactly follows input edges, can look mechanical |

If proportions or silhouette are drifting, raise CN strength. If it's too stiff and detail is getting crushed, lower it.

**Combined tuning example:** Source is a rough concept sketch and output is ignoring most of it:
- Lower denoise to 0.40
- Raise CN strength to 0.95
- These two together pull the result much closer to your source

---

### Knob 2: How Strong the Civ 6 Style Effect Is

#### LoRA strength (`LORA_STR`)

The LoRA injects the trained Civ 6 style into the base model. Strength controls how hard it pushes.

| Value | Effect |
|---|---|
| 0.50–0.70 | Subtle style influence — base model's look comes through |
| 0.80–0.95 | **Good default** — strong Civ 6 style, usually looks intentional |
| 1.00–1.10 | Maximum style — risk of artefacts if the LoRA's training distribution fights the prompt |
| 1.20+ | Almost always breaks — oversaturated, blotchy, or repetitive patterns |

If results don't look like Civ 6, raise LoRA strength. If results look garbled or artefacted, lower it.

#### CFG scale (`CFG`)

CFG (Classifier Free Guidance) controls how literally the sampler follows your text prompt. Higher = more literal, potentially more saturated and harsh. Lower = looser, softer.

| Value | Effect |
|---|---|
| 4–5 | Very soft, may ignore prompt details |
| 6–7 | Relaxed — good for SV sprites where you want a muted feel |
| 7–8 | **Good default** for icons |
| 9–11 | Sharp, literal, high contrast — can cause colour banding |
| 12+ | Usually over-processed; avoid |

---

### Knob 3: Post-Processing Intensity

Post-processing (outlines, background removal) runs after generation and is independent of the AI settings.

#### Silhouette outline thickness (`thickness=` in `add_silhouette_outline`)

Default is 14px. This is the thick border around the whole building.

- Increase to 18–22px for a bolder, more graphic look
- Decrease to 8–10px if the outline is overpowering small details
- Change it in `icon_postprocess.py` line: `img = add_silhouette_outline(img, thickness=14)`

#### Structural outlines (`low=`, `high=` Canny thresholds)

These are the fine interior lines on architectural details (windows, brickwork, roof edges).

- Lower `low` value → more lines detected (more detail, can get noisy)
- Raise `high` value → only the strongest edges (cleaner, less busy)
- Default: `low=60, high=140` — good for most buildings

Change in `icon_postprocess.py` line: `img = add_structural_outlines(img, low=60, high=140, line_width=1)`

---

### Quick Diagnostic Table

| Symptom | Most likely cause | Fix |
|---|---|---|
| Output looks nothing like the source | Denoise too high | Lower `DENOISE` to 0.40–0.45 |
| Silhouette drifting / wrong proportions | ControlNet too weak | Raise `CN_STRENGTH` to 0.90–0.95 |
| Doesn't look like Civ 6 | LoRA strength too low | Raise `LORA_STR` to 0.90–1.0 |
| Garbled or artefacted output | LoRA too strong | Lower `LORA_STR` to 0.75–0.85 |
| Output is barely changing from source | Denoise too low | Raise `DENOISE` to 0.55–0.65 |
| Colours are over-saturated / harsh | CFG too high | Lower `CFG` to 6–7 |
| Background removal cutting into building | rembg boundary ambiguous | Increase `pad=` in `pad_image()`, or use a plain background in source |
| SV sprites don't match SDK palette | Missing trigger word | Make sure `civ 6 strategic view sprite` is in the prompt |
| Generation is slow | SDXL is heavy | Switch to SD 1.5 for iteration (style will drift — for speed tests only) |

---

### If icons look too flat / not enough Civ 6 style
Add more explicit style keywords to the prompt: `bold outlines, cel shaded, thick stroke, sticker style, outlined illustration`.

### If background removal (rembg) is cutting into the building
The subject boundary is ambiguous. Either: increase the `pad=` value in `pad_image()` (try `pad=200`), or use a plain neutral background in your source image instead of a complex scene.

### If ComfyUI fails with `ModuleNotFoundError: No module named 'sqlalchemy'`
You're almost certainly launching ComfyUI with the wrong Python interpreter.

Check what `python` points to:

```powershell
where.exe python
```

If the first result is:

```text
C:\Users\Shadow\AppData\Local\hermes\hermes-agent\venv\Scripts\python.exe
```

then PowerShell is picking up the Hermes Agent virtual environment. Launch ComfyUI with the explicit Python 3.12 command instead:

```powershell
cd C:\Users\Shadow\ComfyUI
py -3.12 main.py --listen 127.0.0.1 --port 8188
```

or:

```powershell
C:\Users\Shadow\AppData\Local\Programs\Python\Python312\python.exe main.py --listen 127.0.0.1 --port 8188
```

Known-good local setup as of 2026-05-10:
- ComfyUI: `0.18.1`
- Python: `3.12.10`
- PyTorch: `2.5.1+cu121`
- GPU: `NVIDIA RTX 2000 Ada Generation`, ~16 GB VRAM

---

## Output Locations

| Pipeline | Raw output | Post-processed |
|---|---|---|
| Icons | `C:\Users\Shadow\.openclaw\workspace\tmp\icon_v3_raw_*.png` | `tmp\icon_v3_*.png` |
| SV sprites | `C:\Users\Shadow\ComfyUI\output\` | Wherever you specify in the script |

Copy keepers to the Dropzone for review: `C:\Users\Shadow\Desktop\Working Files\Dropzone\`
