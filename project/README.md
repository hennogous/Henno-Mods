# CSC Project Resources

Working docs, reference material, and tools that don't belong in the mod source tree.

## docs/

| File | What it is |
|------|-----------|
| `QUARTER-PLAYBOOK.md` | 8-phase checklist for implementing a new Quarter — use this when starting Tailors' etc. |
| `BUILDING-SHAPES.md` | CSC art language — the Marble Rule, roof types, proportions, exaggeration guide |
| `building_schema.md` | JSON spec for the procedural building generator (volumes, features, meta) |
| `building-geometry-catalogue.md` | Vertex/tri/island counts for all vanilla Civ 6 district buildings (deep mesh analysis) |
| `building-geometry-patterns.md` | Observed patterns and modelling guidelines derived from the catalogue |
| `ART-KIT-3D-PASS.md` | Active TODO for the Bakers' art kit (GIMP/Blender/AE tasks) |
| `COMFYUI-SETUP.md` | ComfyUI setup, LoRA models + trigger words, prompt templates, training status |
| `COMFYUI-MANUAL.md` | Step-by-step manual for generating icons and SV sprites — start here if you haven't used ComfyUI before |
| `MAB_MANUAL.md` | Full Ruivo MAB framework reference — `Ruivo_New_Adjacency` schema, AdjacencyTypes, ProvideTypes, examples |
| `taxes+politics.md` | Full design doc for the political loyalty system (Guilds/Elite/Church/Monarchy) |
| `all-buildings-list.md` | Vanilla Civ 6 buildings by era — quick lookup reference |
| `districts_buildings_art_guide.md` | Official Firaxis art guide for districts and buildings |
| `strategic-view-sprites.md` | Full SV sprite pipeline — Blender → img2img → post-process → DDS. LoRA trained (457 sprites, loss 0.0443) |
| `export-pipeline.md` | Art export pipeline reference |
| `geometry-catalogue.md` / `geometry-patterns.md` | Vanilla geometry stats + modelling patterns (skill version) |
| `icons-pipeline.md` | Icon generation pipeline |
| `lora-training.md` | LoRA training reference |
| `textures-and-uvs.md` | Texture + UV reference |
| `SKILL-REVIEW.md` | Analysis of 10+ published mods (Project Metropolis, Sukritact's Oson, MAB, JNR, etc.) |
| `community-extension-modding.md` | CE usage from mod context (SQL/Lua), distinct from the FireTuner/wiki CE docs |

## firetuner/

FireTuner is Firaxis's in-game debug console. CE = Community Extension (the Lua API it exposes).

| File | What it is |
|------|-----------|
| `FIRETUNER-PROTOCOL.md` | Reverse-engineered TCP protocol for FireTuner ↔ game communication |
| `CE-API-REPORT.md` | Findings from CE API probing — what's accessible, what's not |
| `firetuner-research.md` | Research notes from FireTuner/CE investigation sessions |
| `AUTONOMOUS-LAUNCH-NOTES.md` | Notes on launching Civ 6 and loading mods autonomously via FireTuner |

## community-extension/

Community Extension (CE) is a Civ 6 modding framework that exposes game internals via Lua.

- `README.md` — CE overview and setup
- `wiki/` — Full CE wiki (offline copy):
  - `Home.md` — Getting started
  - `Objects.md` — Game object API
  - `Memory-Manipulation.md` — Direct memory access
  - `Singletons-&-Namespaces.md` — Global access points
  - `Events-&-Processors.md` — Event hooks
  - `Configurations.md` — Config options
  - `Contributor's-Guide.md` — Contributing to CE

## tools/

Scripts accumulated during development. Paths may need updating if the source data has moved.

| Folder | Contents |
|--------|---------|
| `blender/` | Blender scripts — SV sprite rendering pipeline, mesh inspection |
| `comfyui/` | ComfyUI scripts — icon post-processing, img2img, bakery/SV generation |
| `scripts/` | Pipeline scripts — CN6 I/O, bone fixing, export pipeline, geo parsing |
| `training/` | LoRA training — data extraction, kohya-ss training launchers |
| `firetuner/` | FireTuner/CE automation — proxy sniffer, game control, CE probing |

### Key scripts

- `blender/render_to_sv_sprite.py` — Full Blender → ControlNet → SV sprite pipeline
- `comfyui/icon_pipeline/icon_postprocess.py` — rembg + canny + outline post-processing for icons
- `scripts/csc_export_pipeline.ps1` — Main asset export: Blender → FGX/GEO
- `scripts/io_import_cn6_b4.py` / `io_export_cn6_b4.py` — CN6 binary format I/O
- `training/prepare_sv_training.py` — Extract SV sprites from SDK pantry for LoRA training
- `firetuner/firetuner_proxy.py` — TCP sniffer for FireTuner protocol analysis
- `firetuner/firetuner_csc_test.py` — CSC mod test harness via FireTuner
- `firetuner/run_csc_demo.py` — **Full end-to-end script**: kill → Steam launch → new game → 50-turn autoplay → snapshot (~90s, confirmed working)
- `cn6libs/` — CN6 tool binaries: `CivNexus6.exe`, `CN6ToFGX.exe`, `FGXToCN6.exe` (pipeline dependencies)
