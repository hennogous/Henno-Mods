# Material assistance at different resource levels — 16 October 2026

**Historical v2 research scope:** production now uses v3, limited to Bakers and Tailors. The density factors below remain applicable, but the six design-only Quarters no longer cause runtime placements, targets or protection constraints. See [current runtime behavior](../../integrations/csc-material-map-assistance.md).

The Additional industry materials option now applies to all vanilla/TAR resource levels. Its tooltip no longer mentions Goldsmiths. The planner is version 2; the saved five-seed automatic-Lua results remain v1 evidence rather than being relabelled as new experiments.

## What the generators actually change

Primary sources inspected on this machine:

- Stock Gathering Storm: `DLC/Expansion2/Maps/Utility/ResourceGenerator.lua`, initialization lines 64–67 and 130–140; density is used in luxury, strategic and bonus placement calculations.
- TAR Workshop item `901009089`: `Utility/ResourceGenerator.lua`, initialization lines 64–67 and 130–144; `Config/Resources_Config.xml` and `Localisation/TrulyAbundant_Text.xml` confirm Plentiful = 25 and Truly Abundant = 45.

Both generators add **percentage points** to a nominal density target. These are not direct percentage multipliers. Vanilla starts at 30, TAR at 29. TAR also changes class shares, sea frequencies, habitat rules and placement behavior, so these figures describe nominal density, not a promise of exactly this change in realized deposits or Quarter opportunities.

| Setup | Nominal density | Change from its own Standard | Scale against vanilla Abundant | Ordinary aim / 15 continents | Goldsmith aim / 15 |
|---|---:|---:|---:|---:|---:|
| Vanilla Sparse | 27 | −10% | 81.8% | 8.2 | 4.1 |
| Vanilla Standard | 30 | 0% | 90.9% | 9.1 | 4.5 |
| Vanilla Abundant | 33 | +10% | 100% | 10 | 5 |
| TAR Sparse | 26 | −10.3% | 78.8% | 7.9 | 3.9 |
| TAR Standard | 29 | 0% | 87.9% | 8.8 | 4.4 |
| TAR Abundant | 32 | +10.3% | 97.0% | 9.7 | 4.8 |
| TAR Plentiful | 54 | +86.2% | 163.6% | 15 (capped) | 8.2 |
| TAR Truly Abundant | 74 | +155.2% | 224.2% | 15 (capped) | 11.2 |

Vanilla Random draws a density of 26–34 (−13.3% to +13.3% versus vanilla Standard). TAR Random draws 25–33 (−13.8% to +13.8% versus TAR Standard). Their expected values are 30 and 29. The late gameplay pass cannot read the generator's private resolved roll: Random therefore uses the expected Standard density, explicitly flagged in the audit. It does not make a second draw or consume shared engine RNG.

Across generators, TAR's Standard is 3.3% below vanilla's nominal Standard, and TAR Abundant is 3.0% below vanilla Abundant. TAR's class/distribution changes mean this does not imply proportionally fewer actual map resources.

## What is scaled

Our original 10/15 and 5/15 aims measure **continents with at least one viable both-class site**, not counts of district tiles. Multiply those fractions by `nominal_density / 33`, capped at 100% continent coverage. Already rich continents are untouched; the pass still performs at most one direct repair per assisted industry per continent. High TAR levels can therefore saturate the coverage aim without adding multiple clusters to an already covered continent.

The helper retains its four directly assisted industries: Tailors, Stonemasons, Apothecaries and Goldsmiths. Other industries can benefit incidentally. For an assisted industry with original natural coverage fraction `b` and original missing-continent selection chance `p`, the scaled chance is:

`target = min(1, (b + (1-b)*p) * scale)`

`estimated_natural = min(1, b * scale)`

`chance = clamp((target - estimated_natural) / (1 - estimated_natural), 0, 1)`

When estimated natural coverage saturates, the chance is 1; actual already covered continents are still skipped. This preserves the original probabilities exactly in intent at vanilla Abundant. Scaling the old probability alone would not scale the coverage aim correctly.

This is a policy approximation, not an empirically fitted density-to-adjacency model. Density and both-class adjacency do not have a linear relationship, and some classes are terrain-based. Selection is probabilistic, repairs can be infeasible, and budgets can bind. No rerolls, forced quotas or resource removal were added.

Deposit limits use the same factor, rounded to the nearest integer: vanilla Sparse 3/continent and 8/map; Standard 4/9; Abundant 4/10. TAR Sparse 3/8, Standard 4/9, Abundant 4/10, Plentiful 7/16 and Truly Abundant 9/22. Two-resource repairs remain possible at every level. These limits retain the existing Small-map calibration; other map sizes need separate evaluation.

## Wiring and verification

TAR is detected by its exact mod ID through an action criterion. Its small conditional SQL patch records density 29 in a CSC parameter. No fingerprint guessing, Workshop edits or map-generator overrides are involved. Another mod replacing ResourceGenerator may implement a different curve; these profiles describe the inspected stock/TAR generators.

`test_lua_material_map.py` executes the real entry script for all ten profiles, with native-captured eligibility. Checks cover profile math, scaled budgets, preservation of native resources and last Base/both-class coverage, repeatability, re-entry/save guards, rollback, two-resource repair and optional resource mappings. Vanilla Abundant still produces 4/5/3/3/3 additions on the original five fixtures. Replaying the actual automatic v1 captures also preserves every original chosen deposit exactly. Results: `project/snapshots/map-lab/lua-helper-scaling-validation.json`.

Two native smoke tests passed on the original first seed (830102), Online speed, Small map size, Continents script (`Continents.lua`), six majors, nine city-states, CSC and official content; TAR enabled for its case:

| Case | Density read by installed pass | Automatic deposits | Limits: continent / map |
|---|---:|---:|---:|
| Vanilla Sparse | 27 | 2 | 3 / 8 |
| TAR Plentiful | 54 | 8 | 7 / 16 |

Both completed at initialization turn 1 before the in-game UI. Each reproduced exactly offline with its captured native eligibility and abundance profile; every original resource remained intact, and each continent's existing last Base/both-class coverage survived. Native database logs showed no Gameplay errors. All 115 installed SQL/Lua/XML/modinfo files matched the deployment throughout the test. Original 141 mod preference flags and auto-start=false were freshly verified afterward, temporary diagnostics cleared, and Civ returned to the main menu.

Native evidence is kept separately under `C:/Users/Shadow/Desktop/Codex/csc-helper-scaling-20261016/`; the controller only configures new games and reads the installed pass's automatic results. An initial verification failure was in the harness's assumption that Lua.log contained only one game: Civ accumulated both maps' logs. Scoping checks to the latest `Generating Continents Map` marker, as the original verifier does, passes the existing captures without rerunning games.

The viewer accepts per-map abundance targets for future experiments while retaining the original Abundant study targets on historical entries. All 9,000 geometry/census comparisons and 8,640 DOM control checks passed, including profile-dependent target/help checks. These are functional fixtures, not a fresh visual rendering review. The two smoke tests are separate validation fixtures, not new five-seed comparison groups. Random's exact resolved roll, native save/reload, multiplayer and alternative generators remain outside this validation.
