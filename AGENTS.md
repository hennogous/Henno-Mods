# Civ Supply Chains — Project Context

## What This Mod Is

**Target:** Civ 6 10th anniversary release, October 2026. **Quality bar:** should feel like high-quality cut content — something that could have shipped with the game.

**Design docs:** https://hennogous.github.io/CivSupplyChains/ (canonical, living document) | **GitHub:** hennogous/CivSupplyChains

**Civ Supply Chains** is a Civ VI mod by Henno that adds 8 industry-based "Quarters" (custom districts) with a 5-stage economic model:

> materials extraction → intermediate goods → consumer goods → specialty goods → goods sales

Quarters: Bakers, Tailors, Apothecaries, Stonemasons, Carpenters, Blacksmiths, Goldsmiths, Brewers.

- Requires: Rise and Fall (XP1) + Gathering Storm (XP2)
- Hard dependency: Modular Adjacency Bonuses Core (MAB) — see [`project/docs/MAB_CHANGES.md`](../project/docs/MAB_CHANGES.md) for CSC's changes to Ruivo's mod (branches, features, PR status)
- Optional integrations: Sukritact's Resources, Resourceful 2, Cannabis & Hemp, Latin American Resources
- Mod ID: `c5e66bd1-d804-443b-ac3d-1917a20dba3c`

## Directory Structure

All mod content lives under `Civ Supply Chains/`:

| Folder | Contents |
| `Data/` | Core SQL — one `CSC_Q_*.sql` per Quarter, plus resources and M&C mode support |
| `Text/` | Localization SQL/XML — names, descriptions, Pedia entries |
| `Lua_UI/` | UI scripts: notifications (Suk MCUIS), adjacency (Ruivo), lenses |
| `ModSupport/` | Compatibility patches for ~6 other mods (R2, LAR, SR, 6T, CL, LGD) |
| `ArtDefs/` | Art definition files linking geometry/textures to game entries |
| `Geometries/` | 3D models in FGX + GEO format (Firaxis export format) |
| `Textures/` | DDS/TEX textures and atlases |
| `Icons/` | Icon SQL definitions |
| `Settings/` | Player-facing game options (XML) |
| `XLPs/` | Xlayer project files for clutter, icons, tilebases |
| `docs/` | Quartz static site — design docs for quarters and framework |
| `Archive/` | Superseded earlier implementations (do not use) |

## Naming Conventions

| Pattern | Used for |
|---|---|
| `CSC_*` | All core mod identifiers |
| `MOD_CSC_*` | Game modifiers |
| `MODIFIER_CSC_*` | Modifier type registrations in `Types` table |
| `RESOURCE_CSC_*` | Custom resources |
| `CLASS_CSC_*` | Resource class tags (TypeTags vocabulary) |
| `CLASS_CSC_[Q]_BASE` | Base material resource class for a Quarter (e.g. `CLASS_CSC_BAKERS_BASE`) |
| `CLASS_CSC_[Q]_SPEC` | Specialty material resource class for a Quarter |
| `DISTRICT_CSC_[Q]_QUARTER` | Quarter district type (e.g. `DISTRICT_CSC_BAKERS_QUARTER`) |
| `BUILDING_CSC_[Q]_*` | Buildings within a Quarter |
| `MOD_CSC_[Q]_*` | Modifiers scoped to a Quarter |
| `CSC_[Q]_*` | Adjacency yield change IDs (in `Adjacency_YieldChanges`) |
| `LOC_DISTRICT_CSC_[Q]_*` | Localization keys for Quarter districts |
| `LOC_BUILDING_CSC_[Q]_*` | Localization keys for Quarter buildings |
| `LOC_CSC_[Q]_*` | Other Quarter localization keys |
| `CSC_Q_*` | Quarter-specific SQL files |
| `ModSupport_XX_*` | Compatibility patches (XX = mod abbreviation) |

`[Q]` = Quarter abbreviation in all caps, e.g. `BAKERS`, `TAILORS`, `GOLDSMITHS`.

## SDK & Asset Locations

| Label | Path |
|---|---|
| **Pantry** (SDK source assets) | `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\Civ6\` |
| SDK Assets root | `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI SDK Assets\` |
| Game root | `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI\` |
| ModBuddy projects | `C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\` |

## Desktop Working Locations

- **Working Files** = `C:\Users\Shadow\Desktop\Working Files\` — active art assets, screenshots, VS Code workspace. Subdirs: `3D Art`, `Docs`, `Icons` (Buildings/Effects/GreatWorks/Quarters/Resources/StrategicView), `Pantry Exports`, `Screenshots`, `Textures`
- **Modding Resources** = `C:\Users\Shadow\Desktop\Modding Resources\` — reference PDFs, tech/civic tree PNGs, ERD, MC_MasterTemplate, tutorial docs
- **Ruivo's Mod / MAB** = `C:\Users\Shadow\Documents\My Games\Sid Meier's Civilization VI\Mods\NEW_ADJACENCY_BONUS_BY_RUIVO` — hard dependency for CSC, local git repo. Ruivo's tutorial: `!参考性文件(reference_folder)\Modular_Adjacency_Bonus_Tutorial-by_Ruivo.md` in that folder. Full reverse-engineered schema reference: `project/docs/MAB_MANUAL.md`
- **CivAssetForge** = `C:\Users\Shadow\Desktop\Working Files\Tools\CivAssetForge` — purpose-built replacement for the Civ6 Asset Editor, built for CSC. Local git repo, also at `https://github.com/hennogous/CivAssetForge`. Prototype viewer (FGX → Three.js) is working; Electron app to follow. Plan: `PLAN.md` in the repo root.

## Key Architecture Points

- **Each Quarter is self-contained**: follows the same SQL structure. `CSC_Q__TEMPLATE.sql` exists but is outdated — a new template will be created once the Bakers' Quarter is complete (~April 2026). Until then, use `CSC_Q_BAKERS.sql` as the reference implementation.
- **Load order matters**: files use `LoadOrder` values (50–99999); dependencies must load before dependents.
- **ActionCriteria system**: files load conditionally based on active game modes, other mods present, or Settings values. Check existing criteria before adding new conditional content.
- **ModSupport is additive**: compatibility patches are separate SQL files loaded only when the target mod is active — never embed cross-mod logic in core Quarter files.
- **Art pipeline**: geometry goes through Blender → `.cn6` export → CivNexus6 (→ `.fgx`/`.geo`) → Asset Editor (`.ast`/`.mat`/`.tex`) → ArtDefs → cook. See the `civ6-modding` skill (`art-pipeline.md` and `art-export-pipeline.md`) for the full workflow.
- **Reusable art kit**: 6 building geometries shared across all Quarters; differentiated via per-Quarter materials/textures (roof recoloring) + manual props.
- **M&C integration file**: `Data/CSC_Q_BAKERS_MC_MODE.sql` — separate file, loaded only when M&C mode is active.
- **Human-only tasks**: Blender retopo, texture creation, prop placement, in-game feel tuning.

## Quarters Status

| Quarter | Gameplay SQL | Art | Status |
|---|---|---|---|
| Bakers' | Complete (5 iterations) | Kit in progress | Reference implementation |
| Tailors' | Stub | Not started | Next up |
| Apothecaries' | Stub | Not started | |
| Stonemasons' | Stub | Not started | |
| Carpenters' | Stub | Not started | |
| Blacksmiths' | Stub | Not started | |
| Goldsmiths' | Stub | Not started | |
| Brewers' | Stub | Not started | |

Current task list is here: `project\TODO.md`

## SQL Structure Per Quarter

Each Quarter SQL follows this 9-section pattern (reference: `CSC_Q_BAKERS.sql`, 1492 lines):
1. Types (district + buildings + custom modifiers)
2. Resource tags (BASE/SPEC material classes + resource mappings)
3. Stage 1 ImprovementModifiers
4. District definition + adjacencies (standard + Ruivo custom)
5. Buildings (stage 2/3/4 + specialist buildings + river/no-river flags)
6. BuildingModifiers + ModifierArguments (bulk — transaction logic)
7. Requirements + RequirementSets + RequirementArguments
8. Population scaling (temp table pattern for per-5-citizen yields)
9. ModifierStrings (preview text)

~65–70% is directly templatable by substituting names/yields/resources/customer districts. The ~30% variance is thematic: stage 2 mechanic variant, customer districts, stage effects.

## Asset Editor Notes

- **Dependency cache**: `%APPDATA%\AssetCloud\mod-Civ Supply Chains-asset-deps.json` — maps every asset to its dependencies; what AE uses to populate the asset browser. Assets created outside AE need to be added here to appear in the browser.
- **Browser UI state**: `%APPDATA%\AssetEditor\1.1\BrowserData\browser_data.dat` (.NET binary, UI layout only)
- Setting "Add New Assets to XLP" is enabled — auto-registers assets when creating via the tool.

## Lua UI Subsystems

- **Notifications** (`Lua_UI/Notifications_Suk_MCUIS/`): Uses Sukritact's MCUIS framework. `CSC_UI_Notifications.lua` is the main entry; `CSC_UI_NotificationPanel.lua` handles panel rendering.
- **Adjacency** (`Lua_UI/Ruivo_Adjacencies/`): Ruivo's adjacency bonus system. `NEW_ADJACENCY_BONUS_BY_RUIVO_GP.lua` is the core logic.
- **Lenses** (`Lua_UI/Lenses/`): Custom map lens overlaying Quarter placement. `ModLens_CSC_Quarters.lua`.

## Settings / Game Options

Defined in `Settings/Settings.xml`. Current toggles:
- `CSC_MC_REMOVE_BONUSES` — strip M&C resource bonuses (default: On)
- `CSC_MC_REMOVE_PROJECTS` — strip M&C projects (default: On)
- `CSC_INCLUDE_ANIMAL_RESOURCES` — animal resource support (default: Off)
- `CSC_REMOVE_UNUSED_MODDED_RESOURCES` — clean unused modded resources (default: On)

## Codex Memory

Session memory for this project lives in `memory/` at the repo root — versioned with the code, not in Codex's default projects folder. Read `memory/MEMORY.md` at session start. Write to the typed files there (`project_*.md`, `feedback_*.md`, etc.) as things happen during a session.

## Project Notes

Working docs, tools, and reference material live in `project/` at the repo root. See `project/README.md` for the full index. Key subdirs:

| Path | Contents |
|---|---|
| `project/TODO.md` | Active task list |
| `project/docs/` | Reference docs — Quarter playbook, art guidelines, building geometry catalogue, MAB manual, ComfyUI/LoRA setup, SV sprite pipeline, design docs |
| `project/firetuner/` | FireTuner protocol docs + CE API findings |
| `project/community-extension/wiki/` | Offline CE wiki — memory manipulation, objects, events |
| `project/tools/` | Scripts: blender SV pipeline, ComfyUI icon gen, CN6 I/O, FireTuner automation, LoRA training |

## Testing via FireTuner

The game exposes a TCP debug console on `127.0.0.1:4318`. A working Python client and test harness live in `project/tools/firetuner/`.

- `run_csc_demo.py` — kill → Steam launch → new game → 50-turn autoplay → snapshot (~90s end-to-end, confirmed working). Requires one human click on "Begin Game".
- `firetuner_csc_test.py` — place districts/buildings, inspect modifier chains, verify adjacency bonuses in a live game
- FireTuner protocol fully documented in `project/firetuner/FIRETUNER-PROTOCOL.md`
- Enable with `EnableTuner 1` in `%LOCALAPPDATA%\Firaxis Games\Sid Meier's Civilization VI\AppOptions.txt` (already enabled on Shadow)

## AI Art Tools

ComfyUI is at `C:\Users\Shadow\ComfyUI`, API on `http://127.0.0.1:8188`.

- **SV LoRA**: trained and ready — 457 sprites, 1,500 steps, loss 0.0443. Trigger: `civ 6 strategic view sprite`. Full pipeline in `project/docs/strategic-view-sprites.md`
- **Icon LoRA** (`game_icon_v1`): trigger `2d icon. [description]`
- **Isometric LoRA** (`cartoon_3d_isometric`): trigger `j_game_background`
- Full setup + prompt templates in `project/docs/COMFYUI-SETUP.md`

## Skills Available

- `/civ6-modding` — SQL schema, modifiers, Lua scripting, .modinfo/.civ6proj structure, Blender → FGX/GEO pipeline, ArtDefs, textures, strategic view sprites, icons
