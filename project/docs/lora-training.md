# LoRA Training Reference

Training custom LoRAs for Civ 6 art styles on Windows using sd-scripts. Covers the SV sprite, icon, and texture LoRAs.

---

## Environment Setup

### Location
```
C:\Users\Shadow\sd-scripts\
```
Python virtual environment inside the directory.

### Critical Windows Configuration

These are hard-won lessons. Skip any of them and training will crash or produce garbage.

#### 1. No Mixed Precision (MANDATORY)
```
--mixed_precision=no
```
fp16 and bf16 both cause **NaN loss and crashes** on Windows. This is not optional.

Use `AdamW` optimizer (NOT AdamW8bit or any 8-bit variant). 8-bit optimisers also crash on this Windows setup.

#### 2. Python UTF-8 Mode (MANDATORY)
```powershell
$env:PYTHONUTF8="1"
```
Without this, Python defaults to cp1252 encoding on Windows and crashes when reading training data filenames or captions with non-ASCII characters.

Set this in your shell before every training run. Or add it as a user environment variable permanently.

#### 3. Accelerate Config
Must match — no mixed precision:
```yaml
compute_environment: LOCAL_MACHINE
distributed_type: 'NO'
mixed_precision: 'no'
```

Run `accelerate config` to regenerate if needed.

#### 4. Latent Cache is Precision-Specific
When you change precision settings (e.g., from fp16 to no mixed precision), you **must delete all .npz files** in the training data directory. The latent cache was generated at the old precision and will produce garbage at the new one.

```powershell
Get-ChildItem -Path "training_data" -Filter "*.npz" -Recurse | Remove-Item
```

---

## Trained LoRAs

### 1. Strategic View LoRA

| Setting | Value |
|---------|-------|
| **Training data** | 457 PNG sprites from SDK pantry |
| **Steps** | 1,500 |
| **Final loss** | 0.0443 |
| **Trigger** | `civ 6 strategic view sprite` |
| **Base model** | SDXL 1.0 |

**img2img sweet spot:** denoise=0.55, LoRA strength=0.6, CFG=8, sampler=dpmpp_2m karras

**Training data source:** Extracted from SDK pantry strategic view sprites. All 256×256 PNGs from the StrategicView texture packages.

### 2. Icon LoRA

| Setting | Value |
|---------|-------|
| **Training data** | 106 PNG icons (buildings + wonders) |
| **Steps** | 2,000 |
| **Trigger** | `civ 6 icon, cartoon isometric, bold outline, hand-painted, cel-shaded` |
| **Base model** | SDXL 1.0 |

**img2img sweet spot:** denoise=0.55, LoRA strength=0.92, CFG=7, 30 steps

**Known issue:** Learned colour palette but not single-subject composition. Needs retraining with curated single-building dataset.

### 3. Texture LoRA

| Setting | Value |
|---------|-------|
| **Training data** | 240 PNG textures from SDK pantry DDS files |
| **Steps** | 2,000 |
| **Trigger** | `civ 6 texture, hand-painted` |
| **Base model** | SDXL 1.0 |

**img2img sweet spot:** denoise=0.50, LoRA strength=0.65, CFG=7

**Use case:** Generating new building atlas textures in Firaxis's hand-painted style. Lower denoise (0.50) preserves more structural detail from the source texture layout.

### 4. Unit Icon LoRA

| Setting | Value |
|---------|-------|
| **Training data** | 96 PNG unit icons sliced from SDK pantry `Units256.dds` using game `IconDefinitions` metadata |
| **Steps** | 1,000 |
| **Final loss** | ~0.0435 |
| **Trigger** | `civ 6 unit icon` |
| **Base model** | SDXL 1.0 |
| **Output** | `C:\Users\Shadow\ComfyUI\models\loras\civ6_unit_icons.safetensors` |

**Training data source:** `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\pantry\Textures\Units256.dds`, sliced by `project/tools/training/extract_unit_icon_training_data.py`. Captions/provenance are recorded in `C:\Users\Shadow\ComfyUI\training_data\civ6_unit_icons_lora\1_civ6unit\manifest.csv`.

---

## Training Data Extraction

### From SDK Pantry (Textures)
DDS textures from the SDK pantry can be batch-converted to PNG for training:

```python
# Use Pillow with DDS support or texconv
# Location: SDK pantry/textures/
# Filter by: DIS_* prefix for district building textures
# Output: 512×512 or 1024×1024 PNGs
```

### From SDK Pantry (SV Sprites)
Strategic view sprites are already PNG-friendly in the pantry packages. Extract from the StrategicView BLP packages.

### From SDK Pantry (Icons)
Building icons extracted from UI texture packages. Filter for building/wonder icons specifically — district overview and landscape icons contaminate the training set (see icon LoRA known issue).

---

## Training Command Template

```powershell
$env:PYTHONUTF8="1"

cd C:\Users\Shadow\sd-scripts

.\venv\Scripts\activate

accelerate launch --num_cpu_threads_per_process 1 train_network.py `
    --pretrained_model_name_or_path="path/to/sdxl_base_1.0.safetensors" `
    --train_data_dir="path/to/training_images" `
    --output_dir="path/to/output" `
    --output_name="civ6_sv_lora" `
    --resolution=1024 `
    --train_batch_size=1 `
    --learning_rate=1e-4 `
    --max_train_steps=1500 `
    --network_module=networks.lora `
    --network_dim=32 `
    --network_alpha=16 `
    --mixed_precision=no `
    --optimizer_type=AdamW `
    --save_every_n_steps=500 `
    --caption_extension=".txt" `
    --enable_bucket `
    --cache_latents `
    --seed=42
```

### Key Parameters

| Parameter | Typical Value | Notes |
|-----------|--------------|-------|
| `--mixed_precision` | `no` | **MUST be no on Windows** |
| `--optimizer_type` | `AdamW` | NOT 8-bit variants |
| `--network_dim` | 32 | LoRA rank. Higher = more capacity, more VRAM |
| `--network_alpha` | 16 | Half of dim is standard |
| `--learning_rate` | 1e-4 | Standard for SDXL LoRA |
| `--max_train_steps` | 1,500–2,000 | 1,500 for SV (larger dataset), 2,000 for icons/textures (smaller) |
| `--resolution` | 1024 | SDXL native resolution |
| `--cache_latents` | (flag) | Caches VAE encodings. **Delete .npz on precision change** |
| `--enable_bucket` | (flag) | Handles varying image sizes |
| `--caption_extension` | `.txt` | Per-image caption files |

### Caption Files
Each training image needs a companion `.txt` file with the same name:
```
image_001.png
image_001.txt  → "civ 6 strategic view sprite, ancient granary, isometric building"
```

For bulk training with uniform style, a single repeating trigger phrase works:
```
civ 6 strategic view sprite
```

---

## Evaluating Training Quality

### Loss Curve
- Good final loss for SV: ~0.04–0.05
- Good final loss for icons: ~0.04–0.06
- If loss doesn't decrease below 0.1: check precision settings, data quality
- If loss goes to NaN: mixed precision is enabled (disable it)

### Visual Evaluation
Generate test images at checkpoints (saved every 500 steps):
1. Use the same img2img workflow as production
2. Compare against SDK pantry reference images
3. Check for: colour palette match, outline style, level of detail
4. Early checkpoints (500 steps) → captures general style
5. Later checkpoints (1500–2000) → captures specific details

### Overfitting Signs
- Generated images look identical to training data
- Loss continues decreasing but visual quality degrades
- Style doesn't adapt to new building shapes (just reproduces memorised images)

---

## Troubleshooting

### NaN Loss Immediately
**Cause:** Mixed precision is enabled.
**Fix:** Set `--mixed_precision=no` AND use `AdamW` (not 8bit). Regenerate accelerate config.

### Crash with cp1252 Error
**Cause:** Missing `$env:PYTHONUTF8="1"`.
**Fix:** Set the environment variable before launching training.

### Loss Doesn't Decrease
**Cause:** Usually stale latent cache from different precision settings.
**Fix:** Delete all `.npz` files in training data directory and restart.

### Out of VRAM
**Cause:** Batch size too large or network_dim too high.
**Fix:** Reduce `--train_batch_size` to 1, reduce `--network_dim` to 16, enable `--gradient_checkpointing`.

### Training Data Quality Issues
- Remove images smaller than 256×256
- Remove images with heavy compression artefacts
- Remove non-representative images (e.g., landscape icons in a building icon dataset)
- Ensure captions are accurate and consistent
