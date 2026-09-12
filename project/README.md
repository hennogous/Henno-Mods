# CSC Project Resources

Working docs, reference material, and tools that don't belong in the mod source tree.

## Documentation split

| Location | Audience / purpose |
|---|---|
| `../docs/` | Public-facing Quartz site: player-facing design docs, Quarter explanations, mechanics, concepts, screenshots, and polished narrative documentation. |
| `docs/` | Internal/project documentation: durable, human-readable reference for collaborators and future maintainers: implementation notes, MAB change logs, branch/PR notes, build/playtest procedures, art-pipeline notes, asset inventories, and non-public decisions. If a CSC collaborator should be able to use it without Hermes, it belongs here. |
| `../memory/` | Versioned agent/project memory: session carryover, working notes, feedback, local lessons, and historical context. Treat it as agent-facing scratch/reference; promote durable human-facing truth to `docs/` or public `../docs/` when it matters. |
| Hermes `civ-supply-chains` skill | Agent operational context only: local paths, workspace rules, what Bill/Garfield should read first, and stable CSC gotchas. Do not use it as the only home for collaborator-facing project truth. |
| Hermes `civ6-gameplay` skill | Generic reusable Civ VI modding knowledge. Do not put CSC-specific notes there. |

## docs/

Start at the [internal documentation index](docs/README.md). The [full documentation audit](docs/DOCUMENT-AUDIT.md) classifies every document and records known stale guidance.

| Area | Entry point |
|---|---|
| Current Quarter building art direction | [Building art plan](docs/art/quarter-building-art-plan.md) |
| Art production, icons and strategic view | [Art plans and production](docs/art/README.md) |
| Quarter implementation and validation | [Workflow references](docs/quarters/README.md) |
| Gameplay systems and related projects | [System references](docs/integrations/README.md) |
| Art studies, trials and reference-mod research | [Research index](docs/research/README.md) |
| Superseded Quarter checklist | [Archived playbook](docs/archive/QUARTER-PLAYBOOK-2026-06-26-outdated.md) |

Current pipeline and workflow documents retain their established paths. Art research
and reference-mod studies are grouped under `docs/research/`.

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

The shared [Civ VI art skill](https://github.com/hennogous/civ6-art) is maintained in its own repository and installed alongside the CSC and Civ VI modding skills. Project-specific art decisions remain in [the building art plan](docs/art/quarter-building-art-plan.md).

Shared skills are split by responsibility: [civ6-gameplay](https://github.com/hennogous/civ6-gameplay) owns gameplay, SQL/Lua and general mod structure; [civ6-art](https://github.com/hennogous/civ6-art) owns visual assets from creation through export, registration and cooking. CSC-specific plans and implementation contracts stay in this repository.

CSC-specific art budgets, scale baselines, palettes and tool observations live in the [CSC skill](https://github.com/hennogous/civ-supply-chains), starting with its [production conventions](https://github.com/hennogous/civ-supply-chains/blob/main/references/art-production-conventions.md). Shared Civ VI guidance remains in `civ6-art`; the project art plan remains the source for asset decisions.

The generic skills refer to the modder’s projects without depending on CSC. For this project, `civ-supply-chains` supplies that context. ComfyUI setups, building-icon generation and strategic-view automation remain project-specific; their publication has not been decided.
