# CSC Service Icon Pipeline

Generates abstract service/unit icons using `civ6_unit_icons.safetensors`, then post-processes them into the same structural format as Civ VI `Units256.dds` training samples:

- transparent background
- flat white pictogram
- centered 256×256 RGBA PNG

## Scripts

- `service_icon_generate.py` — ComfyUI smoke-test generator for service concepts.
- `service_postprocess.py` — standalone post-processing: dark/black background → transparent, foreground → flat white alpha silhouette.

## Run

Start ComfyUI on `127.0.0.1:8188`, then:

```powershell
cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno's Mods"
py -3.12 project\tools\comfyui\service_pipeline\service_icon_generate.py
```

Outputs:

```text
project\tools\comfyui\service_pipeline\outputs\raw\
project\tools\comfyui\service_pipeline\outputs\final\
```

## Prompt rule

The unit-icon LoRA learned symbolic icons, not portraits. Prompt the object/symbol:

```text
flat filled white stencil symbol of beer mug and key
```

not:

```text
innkeeper holding a mug
```

Keep concepts to one or two objects. The postprocessor can clean black backgrounds, but it cannot fix a generated person/scene into a proper Civ icon. Annoying but fair.
