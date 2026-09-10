# CSC Project Resources

Working docs, reference material, and tools that don't belong in the mod source tree.

## Documentation split

| Location | Audience / purpose |
|---|---|
| `../docs/` | Public-facing Quartz site: player-facing design docs, Quarter explanations, mechanics, concepts, screenshots, and polished narrative documentation. |
| `docs/` | Internal/project documentation: durable, human-readable reference for collaborators and future maintainers: implementation notes, MAB change logs, branch/PR notes, build/playtest procedures, art-pipeline notes, asset inventories, and non-public decisions. If a CSC collaborator should be able to use it without Hermes, it belongs here. |
| `../memory/` | Versioned agent/project memory: session carryover, working notes, feedback, local lessons, and historical context. Treat it as agent-facing scratch/reference; promote durable human-facing truth to `docs/` or public `../docs/` when it matters. |
| Hermes `civ-supply-chains` skill | Agent operational context only: local paths, workspace rules, what Bill/Garfield should read first, and stable CSC gotchas. Do not use it as the only home for collaborator-facing project truth. |
| Hermes `civ6-modding` skill | Generic reusable Civ VI modding knowledge. Do not put CSC-specific notes there. |

## docs/

| File | What it is |
|------|-----------|
| `archive/QUARTER-PLAYBOOK-2026-06-26-outdated.md` | Archived, outdated 8-phase Quarter checklist retained for historical reference. Use `specs/<quarter>/` implementation contracts for current Quarter work. |
| `QUARTER-CONTRACT-WORKFLOW.md` | Current contract-first Quarter workflow, authority order, approvals, and Tailors restart sequence. |
| `REFERENCE-PATTERN-CATALOG.md` | How Bakers gameplay patterns are classified and parameterized, including Bakers-only exclusions. |
| `LOCALIZATION-PATTERNS.md` | Bakers-derived exact localization structures and required text surfaces. |
| `QUARTER-VALIDATION.md` | Contract, SQL, localization, ModBuddy, and runtime validation layers. |
| `BUILDING-SHAPES.md` | CSC art language — the Marble Rule, roof types, proportions, exaggeration guide |
| `building_schema.md` | JSON spec for the procedural building generator (volumes, features, meta) |
| `building-geometry-catalogue.md` | Vertex/tri/island counts for all vanilla Civ 6 district buildings (deep mesh analysis) |
| `building-geometry-patterns.md` | Observed patterns and modelling guidelines derived from the catalogue |
| `ART-KIT-3D-PASS.md` | Active TODO for the Bakers' art kit (GIMP/Blender/AE tasks) |
| `asset-editor-ironpython-automation.md` | Investigation note for Asset Editor IronPython preview/capture automation and how it can feed Quarter art/SV workflows |
| `COMFYUI-SETUP.md` | ComfyUI setup, LoRA models + trigger words, prompt templates, training status |
| `COMFYUI-MANUAL.md` | Step-by-step manual for generating icons and SV sprites — start here if you haven't used ComfyUI before |
| `icon-pipeline-implementation-notes.md` | Operational notes for the ComfyUI icon scripts: output paths, rembg/SAM behavior, cache handling, transparency semantics, postprocess knobs |
| `dynamic-art-properties.md` | CSC dynamic art bridge pattern: SQL source properties, Lua mirroring, GamePropertyRanges intervals, event refresh and Bakers variants |
| `bakers-service-notification-ui.md` | Bakers service notification convention: folded MCUIS text, service chains, and commented standalone notification path |
| `modbuddy-actions-json.md` | Workflow for editing ModBuddy `.civ6proj` action CDATA through `project/modbuddy/CivSupplyChains.actions.json` and the patch/export tool |
| `SPECIALTY_PRODUCTS.md` | Specialty Products implementation notes: lean Product substrate, Great Works UI overrides, and M&C compatibility stance |
| `MAB_MANUAL.md` | Full Ruivo MAB framework reference — `Ruivo_New_Adjacency` schema, AdjacencyTypes, ProvideTypes, examples |
| `taxes+politics.md` | Full design doc for the political loyalty system (Guilds/Elite/Church/Monarchy) |
| `all-buildings-list.md` | Vanilla Civ 6 buildings by era — quick lookup reference |
| `districts_buildings_art_guide.md` | Official Firaxis art guide for districts and buildings |
| `ai-3d-model-generation.md` | CSC workflow for creating/AI-assisted generation of new 3D props and small building models before export |
| `strategic-view-sprites.md` | Full SV sprite pipeline — Blender → img2img → post-process → DDS. LoRA trained (457 sprites, loss 0.0443) |
| `export-pipeline.md` | Clean Blender asset → CN6/FGX/GEO → Asset Editor/cook export pipeline reference |
| `geometry-catalogue.md` / `geometry-patterns.md` | Vanilla geometry stats + modelling patterns (skill version) |
| `icons-pipeline.md` | Icon generation pipeline |
| `lora-training.md` | LoRA training reference |
| `textures-and-uvs.md` | Texture + UV reference |
| `shared-atlas-ao.md` | Baking geometry-correct AO into a shared building atlas (UV2 sharing across model variants); tool: `tools/blender/csc_shared_atlas_ao_bake.py` |
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
| `asset_editor/` | Asset Editor IronPython helpers and diagnostics |
| `blender/` | Blender/art scripts — SV sprite rendering pipeline, mesh inspection, and PBR companion-map generation |
| `comfyui/` | ComfyUI scripts — icon post-processing, img2img, bakery/SV generation |
| `modbuddy/` | ModBuddy project helpers, including `.civ6proj` action CDATA export/check/patch |
| `scripts/` | Pipeline scripts — CN6 I/O, bone fixing, export pipeline, geo parsing |
| `training/` | LoRA training — data extraction, kohya-ss training launchers |
| `firetuner/` | FireTuner/CE automation — proxy sniffer, game control, CE probing |
| `quarter_contracts/` | Quarter contract validator for schemas, locked sources, traceability, approvals, and preserved inputs. |

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
