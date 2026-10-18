# Automatic CSC Lua material pass — 16 October 2026

The helper is now installed in CSC and runs automatically during new-game map initialization. Five native games used the same map/game seeds, rosters and four-type Abundant setup as the earlier surveys. The Lua pass added **18 deposits**, with exact offline replay of every native plan. FireTuner made **no planner or resource-setter calls**; it configured games and read the resulting maps/audits.

## Continental coverage

Continents with at least one both-class Quarter site, allowing ordinary future clearing; fifteen named continents across five Small-size Continents.lua maps.

| Quarter | Original | Python preview / API test | Automatic Lua | Approximate target |
|---|---:|---:|---:|---:|
| Bakers | 12/15 | 12/15 | 13/15 | 10/15 |
| Tailors | 3/15 | 11/15 | 9/15 | 10/15 |
| Apothecaries | 9/15 | 9/15 | 10/15 | 10/15 |
| Stonemasons | 4/15 | 8/15 | 11/15 | 10/15 |
| Carpenters | 15/15 | 15/15 | 15/15 | 10/15 |
| Blacksmiths | 15/15 | 15/15 | 15/15 | 10/15 |
| Goldsmiths | 2/15 | 6/15 | 5/15 | 5/15 |
| Brewers | 11/15 | 11/15 | 11/15 | 10/15 |

The Lua version keeps the original probabilities, site geometry, soft continental pools and small budgets. It uses a CSC-owned deterministic random stream instead of Python's MT19937, so it draws different assistance cases and deposits. This is not exact Python seed parity. The new stream was fixed before native testing, and maps were not rerolled to fit the targets. Higher natural coverage is preserved.

| Map | Map seed | Game seed | Added deposits | Native eligibility checks | Automatic completions | Exact offline Lua replay |
|---|---:|---:|---:|---:|---:|---|
| 1 | 830102 | 940104 | 4 | 23,628 | 1 | Pass |
| 2 | 830203 | 940207 | 5 | 24,981 | 1 | Pass |
| 3 | 830304 | 940310 | 3 | 25,773 | 1 | Pass |
| 4 | 830405 | 940413 | 3 | 24,651 | 1 | Pass |
| 5 | 830506 | 940516 | 3 | 23,265 | 1 | Pass |

All eighteen native repairs used one deposit. The two-resource repair path is separately exercised by the Lua fixture tests. Every original deposit, terrain/feature and each continent's last ordinarily usable Base/both-class opportunity was preserved. Removing just the recorded additions reconstructs the original five controls exactly.

## Automatic execution

CSC registers `Lua_UI/MapGeneration/CSC_MaterialMap.lua` with `AddGameplayScripts` at LoadOrder 999901. Native logs show it completed at initialization turn 1 **before the in-game UI loaded**, once per map. This is the late setup phase after native resources and starting positions, rather than replacing or wrapping the selected map script. No turns were advanced.

The setup option **Additional industry materials** defaults On and currently applies only to new Abundant maps. A persistent once-only game property protects reloads, and existing saves are skipped. The planner chooses only empty eligible land without a district or improvement; native checks and readback protect each resource write. Failed placement rolls back all additions. It does not keep modifying the map during play.

The planner uses an independent deterministic Lua stream, with stable ordering and per-continent/industry rolls. It never calls the engine RNG. Its exact addition/palette/coverage decisions reproduce offline from the pre-pass world and native eligibility captured during loading. This validates the real Lua implementation rather than a Python approximation of it.

Full implementation and material-source boundaries: [CSC material map assistance](../../integrations/csc-material-map-assistance.md).

## Build and validation

The source action JSON and `.civ6proj` include the new modules and entry point. A focused deployment copied three Lua files and two setting files, then generated the installed manifest with Firaxis's SDK task. Existing action trees, dependencies, references and unrelated installed content were preserved; no art cook or full rebuild brought unfinished source changes into the test.

Native checks covered five maps / **17,020 plots**, **122,298 eligibility queries**, native resource readback, exact original controls, independent coverage census and exact Lua replay. Controller transcripts contain neither the planner invocation nor a resource setter. All **114 installed source/gameplay files** matched their deployment fingerprints after the batch. Original 141 community-mod flags and auto-start false were freshly verified, diagnostics cleared, and Civ left at the main menu.

The actual Lua entry point also passes fixture checks for re-entry/script reload, disabled/non-Abundant/saved/late-game skips, injected-failure rollback, independent counts, the two-resource path, active optional-resource resolution and protection against unfinished vanilla stub mappings. Those are engine-adapter tests, not a claim of native save/reload or resource-pack compatibility testing.

Civ ran through its local API without mouse/keyboard input after a hidden-window restart. The previous run established background operation and Henno confirmed it stayed backgrounded; no window foregrounding was used for this batch.

## Viewer and evidence

The viewer contains **45 entries**, retaining all prior native maps and prototypes. Its default setup is **CSC helper · automatic Lua**. The placement selector compares original resources, the original Python preview, the Python-driven Civ API prototype and the installed automatic Lua result. Coverage columns show all four; numbered resource markers and coordinates inspect the selected scenario's exact additions. Ordinary clearing remains the default.

Open `project/tools/map_lab/viewer.html`, `project/snapshots/map-lab/index.html`, or the updated Desktop viewer. Native evidence and deployment backups are at `C:/Users/Shadow/Desktop/Codex/csc-helper-lua-20261016/`: per-map before/after exports, startup audits and debug captures, logs, command transcripts, deployment fingerprints, preferences and `validation.json`. `coverage-comparison.csv` and `analysis.json` record the aggregate result. The test-only debug option is off for subsequent normal games.

This remains a five-seed development sample. Small maps, CSC and official content were tested; optional resource mods, other map sizes/scripts, multiplayer and native save/reload are not certified by it. The similar coverage targets are probabilistic design aims, not continent-by-continent quotas.
