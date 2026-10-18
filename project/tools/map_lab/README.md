# CSC map viewer and offline resource experiments

## Current implemented-Quarter native study

Production planner v3 scopes gameplay to Bakers/Tailors. Bakers retain their
above-target natural coverage; direct repairs target missing Tailor opportunities.
`implemented_study.py` generates five native maps each with vanilla Sparse,
Standard and Abundant (same five seed/roster pairs), reads automatic startup audits,
and verifies resource types **and native quantities**. It has no controller-side
resource writes. Required arguments: `--output`, `--bundle`, `--lua-dependencies`.
`--first-only` verifies one map; complete verified maps resume automatically.
`--verify-only` checks captures without generating games; `--combine-only` rebuilds
viewers and CSVs. The native study uses fixed Online/Small/Continents/CSC settings,
exports numbers without game saves, and restores original mods/auto-start.

Outputs include `map-stats.csv`, `coverage.csv`, `added-resource-copies.csv`,
before/after full quantities, audits, logs and viewer data. The viewer distinguishes
inactive design-only reference Quarters from the two runtime targets. Use
`test_assistance_viewer.cjs <maps.json> --implemented` for quantity/target/control
checks and `test_geometry.cjs <maps.json>` for census checks.

## Eight-setup offline abundance study

The historical v2 `abundance_study.py` experiment ran ten instances each of stock Sparse/Standard/Abundant
and TAR Sparse/Standard/Abundant/Plentiful/Truly Abundant. Five captured landscapes
receive two resource seeds each, paired across setups. Separate frozen native
stock/TAR database profiles are required; the actual resource Lua and CSC planner
run with emulated resource eligibility/RNG, without Civ or native start adjustment.
Use `--first-only` for one preflight case; completed instances resume automatically.
The output directory locks source hashes and must be changed after a source edit.
Required arguments: `--output`, `--bundle`, `--stock-database`, `--tar-database`,
`--game-root`, `--workshop-root`, `--lua-dependencies` and `--native-fixtures`
(the original five automatic-Lua captures supply verified fixed starting plots).

Outputs include before/after maps, helper audits, coverage/map/continent CSVs,
frozen profiles and a standalone viewer. The viewer's Abundance study table
compares all eight setups for the selected Quarter/filter. Run
`test_assistance_viewer.cjs <maps.json> --abundance` for functional checks and
`test_geometry.cjs <maps.json>` for geometric/census checks. See the
[results and interpretation](../../docs/research/mods/csc-offline-abundance-study-20261016.md).

## Automatic CSC Lua pass

CSC's installed `CSC_MaterialMap` gameplay context now runs the complete helper
automatically during loading. The setup option Additional industry materials
defaults On for new maps at every vanilla/TAR resource level. Version 2 scales
coverage aims and deposit limits against the vanilla Abundant calibration; Random
uses expected Standard density. See the [scaling factors](../../docs/research/mods/csc-material-abundance-scaling-20261016.md),
[runtime integration](../../docs/integrations/csc-material-map-assistance.md)
and [five-seed native results](../../docs/research/mods/csc-continental-helper-lua-20261016.md).
The 45-entry viewer defaults to automatic Lua, with original / offline Python /
Python API / automatic Lua comparison and exact additions for each scenario.

`automatic_assist.py` configures the same five seeds, enables temporary capture,
and reads the Lua audit and final map. It makes no planner/setter calls through
FireTuner. `verify_automatic_assist.py` validates that boundary, once-only startup
logs, original controls, coverage, installed fingerprints and preferences.
`test_lua_material_map.py` executes the real entry point and pure planner offline,
including all ten abundance profiles, guards, rollback, pairs and optional mapping
boundaries. `test_abundance_native.py` checks two fresh native maps (vanilla Sparse
and TAR Plentiful), without replacing the historical five-map v1 study. Use its
required `--output`, `--bundle` and `--lua-dependencies` arguments; it needs Civ at
the main menu and restores mod/auto-start preferences afterward.

```powershell
py -3 project/tools/map_lab/automatic_assist.py --bundle project/snapshots/map-lab/maps.json --lua-dependencies C:/Users/Shadow/Desktop/Codex/csc-adjacencies/test-deps --output C:/Users/Shadow/Desktop/Codex/csc-helper-lua-20261016
```

Like the previous runner, `--first-only` checks one map before continuing and
`--combine-only` rebuilds the viewer without starting games. Clear the temporary
`CSC_MATERIAL_MAP_DIAGNOSTICS` configuration after a test batch; normal play uses
only a compact persistent audit. The installed native pass owns its Lua random
stream; exact draws intentionally differ from the original Python stream.

## Native helper comparison

`native_assist.py` regenerates the same five native seed/roster pairs with CSC
and stock Abundant, exports each untouched map, and checks it against the paired
four-type control. It queries Civ's actual `ResourceBuilder.CanHaveResource` for
every mapped resource on every otherwise empty passable land tile. The existing
Python helper then uses that native eligibility table, the same selection logic
and the same helper seed. Accepted additions are checked again and placed through
native `ResourceBuilder.SetResourceType`, with exact readback and full final map
export. This tests a pass after initialization at turn 1, without advancing turns.

```powershell
py -3 project/tools/map_lab/native_assist.py --bundle project/snapshots/map-lab/maps.json --database project/snapshots/map-lab/native-calibration/rule-profile.sqlite --output C:/Users/Shadow/Desktop/Codex/csc-helper-native-20261016
```

Use `--first-only` to validate one map first; rerunning resumes verified entries.
Use `--combine-only` to rebuild the viewer from five verified results without
starting Civ. Generation runs through FireTuner with no mouse/keyboard control.
Mod preferences and auto-start are restored. The tool requires an existing main
menu and does not launch, close or manipulate the Civ window itself.

The resulting **CSC helper · Civ API test** setup has a three-way placement
selector: original native resources, offline preview, and Civ result. Coverage
tables compare all three, and the native eligibility discrepancy count is shown.
`verify_native_assist.py` independently checks the evidence, repeats decisions
using the saved live eligibility table, verifies preservation, native setter
transcripts and last-site protections. Run `map_survey/verify_study_preferences.py`
before that verifier to obtain fresh native confirmation of restored preferences.

This is a native API-backed prototype, with selection/RNG still in Python.
It does not test an installed Lua helper or automatic startup ordering. Late
native eligibility also rejects reserved starting plots; fresh exports now
include their indices in `starting_plots`, independently of connected geography.

See [native comparison results](../../docs/research/mods/csc-continental-helper-native-20261016.md).

## Continental helper preview

The default built viewer now includes five **CSC helper · preview additions**
entries, alongside the thirty native survey entries. Use Placement comparison
to toggle original resources and proposed additions. Orange numbered outlines
mark deposits; green rings show new opportunities and red crosses show displaced
original candidates. Coverage tables, exact additions and soft continental pools
are below the map. Counts follow the selected clearing filter and continent.

See [method, results and limitations](../../docs/research/mods/csc-continental-resource-helper-preview-20261016.md).
Rebuild the native bundle with `build.py`, then generate the additive preview:

```powershell
py -3 project/tools/map_lab/assist.py --bundle project/snapshots/map-lab/maps.json --database project/snapshots/map-lab/native-calibration/rule-profile.sqlite --output project/snapshots/map-lab
```

The seed defaults to 20261016 and is recorded with every draw and placement.
The native bundle is read before the combined viewer is replaced. Existing
helper entries are replaced rather than duplicated. Raw native map exports,
installed game/mod files and preferences are never written. To keep a separate
preview package, use `--output project/snapshots/map-lab/helper-preview` instead.
`test_assist.py` checks habitat, successful final centers, input preservation,
repeatability, last-opportunity protection, pairs and budgets. The full viewer
can run against a DOM fixture with `test_assistance_viewer.cjs`; geometry is
checked by `test_geometry.cjs`. Neither test claims browser visual review.

The following describes the earlier resource replay experiments and their
generation limits; native calibration and the helper preview are later steps.

Inspect the fifteen native maps from the 16 October survey without launching
Civilization VI. The same viewer can open separately labelled resource-script
experiments on those landscapes. The offline runner executes installed Lua through
an emulated map API; it does not generate new native terrain or implement YnAMP's
complete generation pipeline.

## Open the viewer

Open `project/tools/map_lab/viewer.html` or
`project/snapshots/map-lab/index.html` in a browser. The former redirects to the
finished viewer; `viewer.template.html` is the build-time layout. The viewer is a self-contained
file with no network requests, server, package installation or Civ session needed.
The generated snapshot directory is ignored by Git. Rebuild it from the retained
survey exports with:

```powershell
$python = 'C:\Users\Shadow\.cache\codex-runtimes\codex-primary-runtime\dependencies\python\python.exe'
& $python project/tools/map_lab/build.py --survey 'C:\Users\Shadow\Desktop\Codex\csc-map-material-opportunities-20261016'
```

For the native 4/5/6 luxury experiment, append
`--luxury-survey project/snapshots/map-lab/luxury-study`. This adds fifteen maps
to the original fifteen. A continent picker isolates each named continent;
Continent comparison lists land luxury diversity, copies, industry coverage and
the selected Quarter's site counts. Opportunity supply switches between Base
support (Stages 2–3, including both-class sites) and both-class support (Stage 4).
Material supply still requires improvements and all other Service conditions.
Older maps retain their original metadata limits.

Choose landscape 1–5 and a resource setup. The paired landscapes have identical
terrain/features; their resource layouts differ. Choose a Quarter to show its
material classes and both-class opportunities. Base and Specialty overlays,
opportunity markers, resources and terrain symbols can be toggled independently.
Scroll to zoom, drag to pan, and click to pin a tile and its supporting neighbours.
The search field outlines resources by name. Arrow keys inspect coordinates,
Enter pins a hovered tile, and Escape clears the selection.

The three opportunity filters reproduce `map_survey/analyze.py`: passable land,
ordinary clearing, and the loaded harvesting rules. The distinct-source switch
requires two separate supporting tiles. Hills and Woods/Rainforest count where
the Quarter design specifies them. Material lists for Bakers and Tailors resolve
from the captured runtime tags; the other six use their individual design pages.

These counts describe material geometry, including hidden strategics. They do not
include ownership, reach from a city, research, improvement status, or all native
district-placement rules. Several candidates can share the same source pair.
Rivers, continent boundaries and player starting coordinates are absent from the
original fifteen exports and therefore are not drawn. Raw `map.json` alone lacks
the viewer's definitions/settings envelope; use a built `maps.json` or an offline
`viewer-map.json` with **Open map data**.

## Run scripts without Civ

`offline.py` loads either the installed GS or TAR `ResourceGenerator.lua`.
`--oceans` additionally applies Oceans' feature/resource SQL when absent from the
supplied database, then executes its actual `Suk_OceansMapGen.lua` and includes.
Workshop files are read-only. No copied Firaxis or Workshop source is distributed
with this tool.

Use a native `DebugGameplay.sqlite` as an explicit rule profile. The program
clones it to memory. Selecting stock Lua does **not** remove TAR SQL changes or
other rules already present in that profile. The demo freezes a local profile
under its generated output directory, so later native games cannot silently
change the demo's inputs.

```powershell
& $python project/tools/map_lab/demo.py `
  --survey 'C:\Users\Shadow\Desktop\Codex\csc-map-material-opportunities-20261016' `
  --database 'C:\Users\Shadow\AppData\Local\Firaxis Games\Sid Meier''s Civilization VI\Cache\DebugGameplay.sqlite' `
  --game-root 'C:\Program Files (x86)\Steam\steamapps\common\Sid Meier''s Civilization VI' `
  --workshop-root 'C:\Program Files (x86)\Steam\steamapps\workshop\content\289070' `
  --lua-dependencies 'C:\Users\Shadow\Desktop\Codex\csc-adjacencies\test-deps' `
  --output project/snapshots/map-lab
```

This produces `experiments.html`, containing the native maps plus four labelled
replays on landscape 2: TAR with 4, 5 and 6 land luxury types per emulated region,
and TAR with 6 followed by Oceans. The original fifteen remain separately
available in `index.html`. `experiments.json` can also be imported into the native
viewer. These are demonstration runs, not a repeat of the native abundance study.

For an individual experiment, replace `demo.py` with `offline.py`, supply a
`--map .../map-02/map.json` instead of `--survey`, and choose `--generator tar`,
`--luxury-types 6`, `--resources 3`, `--seed 12345`, optionally `--oceans`, and an
output directory. Old exports require the explicit `--approximate` switch.
`--generator keep --oceans` runs Oceans over the existing resource layout.

The existing isolated Lupa dependency includes Lua 5.1, needed for Oceans'
legacy vararg behaviour. There is no new dependency installation. Outputs include
the viewer import, a complete tile export, counts, Lua log, source/database hashes,
resource RNG seed, runtime version and limitations.

## Fidelity and the generation boundary

| Facility | Current behaviour |
|---|---|
| Fifteen captured resource layouts and Quarter overlays | Native evidence; browser counts checked against all 120 survey combinations. |
| TAR placement decisions and Oceans' placement algorithms | Execute their installed Lua, with emulated APIs. |
| Eligibility | Partial interpretation of the supplied SQL rules; native parity is unverified. |
| Randomness | Repeatable Python MT19937 stream, not Civ's seed-to-map stream. |
| Continents in old exports | Connected landmasses substitute for missing named-continent IDs. This is a substantial difference, not native continent reconstruction. |
| Rivers in old exports | Unknown; assumed absent for placement eligibility. |
| Lakes in old exports | Inferred from small water components. |
| Starting-position normalization | Absent. |
| Stock procedural terrain and full YnAMP generation | Unsupported; native `Fractal`, `AreaBuilder` and `StartPositioner` facilities fail explicitly. |
| Native generation in the background | Verified during the native luxury study while Henno confirmed Civ was backgrounded; setup/export/menu transitions used FireTuner without input. Window focus was not independently observable. |

All offline maps show a visible emulation notice. No claim is made that their
site counts predict a native seed, that the complete TAR mod stack has been
reconstructed, or that native district placement is validated. For example,
modifiers outside the selected feature/resource SQL are not applied by the
offline runner.

`map_survey/dump.lua` now captures named continent IDs, river/lake flags, wrapping
and map size for future surveys. This additive exporter change has not yet been
checked in a new native capture; the original fifteen exports are unchanged.
Richer exports remove those particular substitutions, but native RNG and
eligibility still require comparison against the game.

A complete external runner for arbitrary Civ map scripts requires implementing
their native dependencies or hosting the native engine. The installed SDK has no
separate map-generation executable among its tools. The inspected stock terrain
generator uses `Fractal.Create`; stock maps also call native area analysis and
start-position functions. The practical next fidelity step is a controlled native
capture of continent/river/lake data and resource eligibility, followed by
comparison of the emulated placement pass. A background native worker remains the
route for authoritative full terrain/start generation; it is not implemented by
this prototype.

## Verification

`test_viewer.cjs` drives a headless browser using the bundled Playwright package
and installed Chrome. It checks all three filters against all 120 native
Quarter/map rows (360 comparisons), 120 distinct-source counts, class-source
counts, controls, tile selection, zoom and narrow-screen overflow. It writes
screenshots and a validation record under the generated directory.

```powershell
& 'C:\Users\Shadow\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe' project/tools/map_lab/test_viewer.cjs
```

`test_offline.py` accepts the same map/database/game/workshop/dependency paths as
`offline.py`, plus `--output .../offline-validation.json`. It verifies repeatable
TAR and Oceans runs, preservation of terrain and neighbour geometry, actual kelp
and custom-resource output, unchanged inputs/source files, rejection of missing
native fields without explicit approximation, and failure on native-only APIs.
It does not verify native gameplay parity.

## Tailor density preview (v4)

`preview_tailor_density.py --captures <v3 implemented-native batch>
--lua-dependencies <lupa directory> --output <review folder>` executes the
production planner on15 native pre-pass worlds and captured native eligibility.
It checks unchanged v3 additions,2× Base-only/4× both targets with the scaled
minimum, native eligibility, resource quantities, starts, continental Baker
counts, repeatability and caps. It saves plans, proposed maps and CSV/JSON
counts separately from native evidence. No game is launched or modified.
Historical `implemented_study.py` expects v3 and is not a v4 verifier.
