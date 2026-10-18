# Implemented-Quarter native map study — 16 October 2026

The production material pass now scopes matching, targets and preservation to **Bakers and Tailors**. Bakers retain their natural geography because their calibrated coverage is already above the aim; direct repair draws target missing Tailor opportunities. Stonemasons, Apothecaries, Goldsmiths and the other design-only Quarters cannot cause resource additions, palette allocations or protection constraints. Their old broader experiments remain historical research.

## Native experiment

Fifteen fresh Civ maps: five each at vanilla Sparse, Standard and Abundant, with the same five map/game seeds and leader rosters paired across levels. Small size, Continents.lua, Gathering Storm, Online speed, Prince, six majors and nine city-states. CSC and official content only; animal resources enabled, unused modded resources cleanup enabled, M&C off. Games ran backgrounded and remained at turn1, without autoplay or game saves.

The installed v3 Lua pass ran automatically after native resource/start placement and before the in-game UI. FireTuner configured games and read outcomes; it did not invoke the planner or resource setters. The pre-pass capture and final export both record native resource quantities (`GetResourceCount`). The planner records quantity=1 per new deposit and the live adapter verifies that exact native readback.

| Map | Map seed | Game seed |
|---|---:|---:|
| 1 | 830102 | 940104 |
| 2 | 830203 | 940207 |
| 3 | 830304 | 940310 |
| 4 | 830405 | 940413 |
| 5 | 830506 | 940516 |

## Implemented-Quarter coverage

Counts are continents with at least one ordinarily clearable material opportunity, **out of 15 continent instances per level**. These are five paired terrains, not 45 independent terrains. Base supply describes Stage 2/3 geography; both-class supply describes Stage 4 geography. Research, improvements, city reach and complete district legality still apply during play.

| Resource level | Bakers Base before → after | Bakers both before → after | Tailors Base before → after | Tailors both before → after | Added copies |
|---|---:|---:|---:|---:|---:|
| Sparse | 15 → 15 | 11 → 11 | 15 → 15 | 1 → 6 | 5 |
| Standard | 15 → 15 | 11 → 11 | 14 → 15 | 4 → 9 | 6 |
| Abundant | 15 → 15 | 12 → 12 | 15 → 15 | 3 → 9 | 6 |

Tailor coverage aims scale to approximately 8.2/15 at Sparse, 9.1/15 at Standard and 10/15 at Abundant. Standard and Abundant finish near the aims; Sparse remains lower, starting from just 1/15 natural both-class coverage. Selection is probabilistic and this five-seed sample should not be rerolled or fitted to force the target. No repair was rejected for native placement feasibility or budget in these maps.

## Individual resource copies

Every added copy occupied one previously empty resource tile and had native quantity 1. Thus the batch added **17 copies on 17 tiles**. This is about 0.29% of the 5,911 resource tiles already present across the 15 maps.

| Level | Map1 | Map2 | Map3 | Map4 | Map5 | Total added tiles / copies |
|---|---:|---:|---:|---:|---:|---:|
| Sparse | 1 | 1 | 2 | 1 | 0 | 5 / 5 |
| Standard | 1 | 1 | 3 | 1 | 0 | 6 / 6 |
| Abundant | 1 | 2 | 2 | 1 | 0 | 6 / 6 |

| Level | Dyes | Silver | Silk | Sheep |
|---|---:|---:|---:|---:|
| Sparse | 2 | 2 | 1 | 0 |
| Standard | 2 | 2 | 1 | 1 |
| Abundant | 3 | 2 | 1 | 0 |
| **Total** | 7 | 6 | 3 | 1 |

The Sheep and one Silver on Standard map 3 form a two-resource repair around the same Quarter center (665): Sheep on plot 738, Silver on plot 591. Its other Dyes addition supports a separate center. Extra copies therefore do not always mean the same number of newly covered continent/industry pairs.

## Candidate sites and interpretation

| Level | Bakers both-class sites before → after | Tailors both-class sites before → after | Tailor connected clusters before → after |
|---|---:|---:|---:|
| Sparse | 120 → 120 | 1 → 11 | 1 → 9 |
| Standard | 121 → 121 | 6 → 17 | 5 → 11 |
| Abundant | 158 → 158 | 9 → 20 | 7 → 15 |

- The intended missing-continent Tailor help works with very few added deposits. All existing generated resources and their native quantities survive unchanged.
- Bakers need no direct help in this sample: both-class coverage and both-class site counts remain unchanged. Some Base-supported candidate tiles are occupied by added luxuries (three at Sparse, three at Standard, two at Abundant), but every continent retains Base coverage. Preservation guarantees cover the last supported opportunity, not every candidate tile.
- Standard map 3 shows why Base and Specialty need separate measurement: a two-deposit repair restores missing Tailor Base support as well as Stage 4 geography.
- More resource abundance does not guarantee higher coverage on each paired landscape: native placement and start adjustment redistribute resources, and the helper has keyed probabilistic selection. Standard and Abundant both end at 9/15 Tailor coverage.
- Connected site clusters and raw candidate tiles are alternative placement geometry, not independent material supplies or proof of simultaneous city placement. No AI district-building behavior was tested.

## Verification and artifacts

All 15 native captures pass once-only startup before the UI, v3 scope (two runtime definitions, only direct Tailor draws), empty/eligible placement, native quantity 1 readback, exact before/after preservation on 51,060 plot pairs, and independent coverage checks. Exact offline replay uses each map’s actual native eligibility. All five Abundant pre-pass worlds exactly match the original four-luxury-type controls on terrain, features, resources, continent IDs, ownership, districts, rivers, lakes and neighbors.

Scoped Lua fixture checks pass all five reference maps and all ten vanilla/TAR profiles, including rollback, script reload, saved-game guards, two-resource Tailor repair and optional resource mappings. Native dataset viewer checks pass 4,320 geometric/census comparisons and 240 before/after functional checks; quantity columns and six inactive target rows are verified. These functional checks do not constitute a fresh browser visual rendering review.

All 115 installed SQL/Lua/XML/modinfo files stayed unchanged during generation. Source fingerprints for the controller, exporter and runtime Lua also match. Original 141 mod flags and auto-start=false were freshly checked after restoration; temporary diagnostics are false and Civ is back at its main menu. Native save/reload, multiplayer, Random and optional-mod native batches are not part of this study.

Evidence: `C:/Users/Shadow/Desktop/Codex/csc-implemented-native-20261016/`. Key files: `analysis.json`, `map-stats.csv`, `coverage.csv`, `added-resource-copies.csv` (one row per added tile), `resource-copy-totals.csv`, per-map before/after worlds, native audits/debug captures, logs, `final-verification.json`, and the standalone 15-map `viewer.html`. The main viewer retains the historical 125 entries and now has 140 total. Source: `project/tools/map_lab/implemented_study.py`.
