# ComfyUI Setup for CSC Art Generation

**Location:** C:\Users\Shadow\ComfyUI
**Server:** `python main.py --listen 127.0.0.1 --port 8188`
**API:** http://127.0.0.1:8188
**GPU:** NVIDIA RTX 2000 Ada (15GB VRAM)

## Installed Models

### Checkpoints (models/checkpoints/)
| Model | Size | Use |
|---|---|---|
| `sd_xl_base_1.0.safetensors` | 6.5GB | **Primary** — SDXL 1.0, best quality for all use cases |
| `v1-5-pruned-emaonly.safetensors` | 4GB | SD 1.5, faster, good enough for quick iteration |

### LoRAs (models/loras/)
| Model | Size | Trigger | Use |
|---|---|---|---|
| `game_icon_v1.safetensors` | 63MB | `2d icon. [description]` | Building/resource icons, clean game UI style |
| `cartoon_3d_isometric.safetensors` | 80MB | `j_game_background` | Isometric pastoral buildings, village scenes |
| `sxz_wow_icons.safetensors` | 18MB | (none) | RPG-style skill/item icons, WoW aesthetic |

### Z Image Turbo (models/diffusion_models/, text_encoders/, vae/)
Fast generation pipeline — 6 steps instead of 25. Good for rapid iteration.

## Recommended Prompts by Use Case

### 1. Building Concept Art (Isometric, Civ 6 Style)
**Model:** SDXL + cartoon_3d_isometric LoRA
**Prompt template:**
```
isometric medieval [building type], Civilization 6 art style, simple exaggerated chunky shapes like toy model, 
[material details], roof detail visible from above, warm lighting from southwest, game asset on hex tile, 
stylized not realistic, big shapes with 3:2:1 ratio, fun wonky shapes avoiding straight lines, 
<lora:cartoon_3d_isometric:0.7>
```
**Negative:** `realistic, photographic, blurry, modern, sci-fi, anime, pixel art, text, watermark`
**Settings:** 768x768, 25 steps, CFG 7.5, euler_ancestral

### 2. Building/Resource Icons (Game UI)
**Model:** SD 1.5 + game_icon_v1 LoRA
**Prompt template:**
```
2d icon. a [object description]. <lora:game_icon_v1:1>
```
**Negative:** `(blurry:1.3), text, watermark, 3d render, photograph`
**Settings:** 512x512, 20 steps, CFG 7, euler
**Examples:**
- `2d icon. a stone oven with bread inside and smoke. <lora:game_icon_v1:1>`
- `2d icon. a sack of wheat grain. <lora:game_icon_v1:1>`
- `2d icon. a wooden loom with colorful fabric. <lora:game_icon_v1:1>`

### 3. RPG-Style Resource Icons
**Model:** SD 1.5 + sxz_wow_icons LoRA
**Prompt template:**
```
game icon, [item description], world of warcraft style, detailed, painted, <lora:sxz_wow_icons:0.8>
```
**Settings:** 512x512, 20 steps, CFG 7

### 4. Strategic View Sprites
**Model:** SDXL (no LoRA yet — custom training needed)
**Prompt template:**
```
simplified building illustration, [building type], flat muted earth tones, hand-painted feel, 
top-down isometric view, clear silhouette, strategy game miniature, minimal detail, 
warm desaturated palette, white background
```
**Negative:** `realistic, photograph, 3d render, complex, busy, text`
**Settings:** 512x512, 25 steps, CFG 8
**Note:** Results will be inconsistent without a trained LoRA. See training plan below.

### 5. Desktop Wallpapers (Bill Of The Week)
**Model:** SD 1.5 or SDXL
**Prompt:** Themed to current week's Bill personality
**Settings:** 1920x1080, 25 steps, CFG 7.5

## Strategic View LoRA Training Plan

### Training Data Needed
- Extract strategic view sprite PNGs from game BLP files
- Source: `strategicview_buildings.blp`, `strategicview_districts.blp`, `strategicview_improvements.blp`
- Need BLP unpacker (BLP Studio or custom parser — see memory/BLP format notes)
- Target: 30-50 individual sprite images with captions

### Training Setup
- **Base:** SDXL 1.0
- **Method:** LoRA training via kohya-ss or ComfyUI train node
- **Steps:** ~1000-2000 steps, learning rate 1e-4
- **Captions:** "[building_name], civ 6 strategic view sprite, simplified illustration, muted earth tones"
- **Output:** ~50-150MB LoRA file

### Training Data (FOUND — no BLP extraction needed!)
**Location:** `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\pantry\Textures\`
- 203 DDS sprite files already extracted in SDK Assets pantry
- 6 district sprites, 4 improvement sprites, 2 wonder sprites, 40+ terrain sprites
- Total 8,841 DDS textures in pantry across all asset types

### LoRA Training Status
- [x] Convert DDS sprites to PNG -- DONE (146 images in C:\Users\Shadow\ComfyUI\training_data\civ6_strategic_view\)
- [x] Write captions -- DONE (146 .txt files, kohya-ss format)
- [ ] Install kohya-ss (pip install kohya-ss, or clone https://github.com/kohya-ss/sd-scripts)
- [ ] Configure training: base=SDXL 1.0, resolution=256, batch_size=1, steps=1500, lr=1e-4, network_dim=32
- [ ] Run training (~1-2 hours on RTX 2000 Ada)
- [ ] Test generated sprites against real Civ 6 strategic view style
- **Note:** Training is a long-running GPU process. Run in a terminal directly, not via OpenClaw exec (SIGKILL risk).

## API Usage (Python)

### Basic SD 1.5 Generation
```python
import requests
workflow = {
    "1": {"inputs": {"ckpt_name": "v1-5-pruned-emaonly.safetensors"}, "class_type": "CheckpointLoaderSimple"},
    "2": {"inputs": {"text": "YOUR PROMPT", "clip": ["1", 1]}, "class_type": "CLIPTextEncode"},
    "3": {"inputs": {"text": "NEGATIVE", "clip": ["1", 1]}, "class_type": "CLIPTextEncode"},
    "4": {"inputs": {"width": 512, "height": 512, "batch_size": 1}, "class_type": "EmptyLatentImage"},
    "5": {"inputs": {"seed": 42, "steps": 20, "cfg": 7.5, "sampler_name": "euler_ancestral", "scheduler": "normal", "denoise": 1.0, "model": ["1", 0], "positive": ["2", 0], "negative": ["3", 0], "latent_image": ["4", 0]}, "class_type": "KSampler"},
    "6": {"inputs": {"samples": ["5", 0], "vae": ["1", 2]}, "class_type": "VAEDecode"},
    "7": {"inputs": {"filename_prefix": "output", "images": ["6", 0]}, "class_type": "SaveImage"}
}
requests.post("http://127.0.0.1:8188/prompt", json={"prompt": workflow})
```

### With LoRA
Add after checkpoint loader:
```python
"1b": {"inputs": {"lora_name": "game_icon_v1.safetensors", "strength_model": 1.0, "strength_clip": 1.0, "model": ["1", 0], "clip": ["1", 1]}, "class_type": "LoraLoader"},
```
Then reference `["1b", 0]` for model and `["1b", 1]` for clip in subsequent nodes.

## Output
Generated images save to: `C:\Users\Shadow\ComfyUI\output\`

## Notes
- ComfyUI server needs manual start (not a service yet)
- SDXL needs ~10GB VRAM — fits on RTX 2000 Ada but leaves little headroom
- SD 1.5 is faster and lighter for iteration
- PyTorch 2.5.1+cu121 installed (ComfyUI warns about cu130 but works fine)
