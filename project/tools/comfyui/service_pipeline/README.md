# CSC Service Icon Pipeline

Generates abstract service/unit icons using `civ6_unit_icons.safetensors`, then post-processes them into the same structural format as Civ VI `Units256.dds` training samples:

- transparent background
- flat white pictogram
- centered 256×256 RGBA PNG

## Scripts

- `service_icon_generate.py` — ComfyUI smoke-test generator for service concepts.
- `service_postprocess.py` — standalone post-processing: dark/black background → transparent, foreground → flat white alpha silhouette.
- `service_icon_compose.py` — deterministic one/two-concept compositor: primary at 100%, optional secondary at 80%, centered at the accepted Bakers scale.
- `analyze_service_atlas.py` — reports cell bounds and alpha levels and can produce a reference contact sheet.

## Run

Start ComfyUI on `127.0.0.1:8188`, then:

```powershell
cd "C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods"
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

Generate or extract the primary and secondary pictograms separately so their
opacity remains controllable, then compose them:

```powershell
py -3.12 project\tools\comfyui\service_pipeline\service_icon_compose.py `
  primary.png output.png --secondary secondary.png `
  --primary-scale 1.0 --secondary-scale 0.58 `
  --secondary-x 0.23 --secondary-y -0.23
```

The default 179px maximum combined extent is the median of Bakers atlas service
cells 8–12. It is about 70% of the 256px canvas. Adjust layer scale and offset
for the silhouettes, while retaining the combined extent and centered bounds.
When two concepts overlap, preserve an approximately 8px transparent separation
at 256px so the foreground and 80%-opacity background silhouettes remain distinct.

Choose symbols for the service as an entity in its own right. The supply chain
explains how the service is established; it does not normally supply the icon's
main imagery. The Bakers service icons contain no bread or cake. The Storekeeper's
flour sack is the accepted exception, and it remains the 80%-opacity secondary cue.
