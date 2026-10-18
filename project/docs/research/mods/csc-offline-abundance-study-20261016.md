# Offline resource-abundance study — 16 October 2026

**Historical v2 experiment:** these 80 layouts used the broader research policy. Production v3 now limits the pass to Bakers and Tailors. Results below are preserved as evidence for future Quarters, not relabelled as current runtime results.

Henno requested ten instances of each of eight resource setups, followed by reflection on the offline results before further native runs. **No native games were started for this study.** Gameplay policy was held fixed; no tuning was performed to make the results match the targets.

## Sample and method

- 80 resource layouts: vanilla Sparse/Standard/Abundant, and TAR Sparse/Standard/Abundant/Plentiful/Truly Abundant, ten instances each.
- Five captured landscapes at Small map size, using the Continents script (`Continents.lua`), two resource RNG seeds per landscape. This is five independent terrains, not ten; each setup therefore has 30 repeated continent instances, rather than 30 independent continents.
- The first resource replicate uses each original map seed; the second adds 1,000,003. Both resource and helper seeds are paired across all eight setups. Python MT19937 supplies resource RNG; CSC retains its own Lua stream.
- Separate frozen native SQLite rule profiles for stock and TAR; CSC material tags match exactly, while TAR habitat/frequency/harvesting rules remain distinct. The inspected installed stock/TAR ResourceGenerator.lua files and CSC planner v2 execute directly.
- Original captured terrain, features, continent IDs, rivers and lakes are reused. Existing captured resource layouts are cleared and regenerated. There is no native terrain generation or native starting-position adjustment. Fifteen captured start tiles per landscape are protected during helper eligibility checks; they are fixed reference starts, not regenerated starts.
- Primary metrics below use ordinarily clearable land and both material classes. Hidden strategic resources count. Actual research, improvements, city reach and full district placement legality are outside this material-geography census.
- The run took approximately 173 seconds, plus the one-case preflight.

## Continental Stage 4 coverage

Cells show **before → after CSC assistance, out of 30 continent instances per setup**.

| Setup | Bakers | Tailors | Apothecaries | Stonemasons | Carpenters | Blacksmiths | Goldsmiths | Brewers |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Vanilla · Sparse | 25 → 25 | 9 → 19 | 14 → 15 | 9 → 17 | 30 → 30 | 30 → 30 | 1 → 8 | 23 → 23 |
| Vanilla · Standard | 26 → 26 | 9 → 19 | 18 → 19 | 9 → 19 | 30 → 30 | 30 → 30 | 3 → 10 | 22 → 22 |
| Vanilla · Abundant | 25 → 25 | 9 → 18 | 17 → 17 | 9 → 19 | 30 → 30 | 30 → 30 | 3 → 10 | 23 → 23 |
| TAR · Sparse | 26 → 26 | 8 → 18 | 16 → 16 | 9 → 17 | 29 → 29 | 29 → 29 | 3 → 9 | 23 → 23 |
| TAR · Standard | 25 → 25 | 8 → 18 | 14 → 15 | 9 → 19 | 30 → 30 | 29 → 29 | 4 → 11 | 23 → 23 |
| TAR · Abundant | 25 → 25 | 9 → 19 | 18 → 19 | 9 → 19 | 30 → 30 | 28 → 28 | 5 → 11 | 22 → 22 |
| TAR · Plentiful | 28 → 29 | 13 → 30 | 23 → 30 | 9 → 30 | 30 → 30 | 30 → 30 | 7 → 17 | 24 → 25 |
| TAR · Truly Abundant | 27 → 27 | 13 → 30 | 24 → 30 | 9 → 30 | 30 → 30 | 30 → 30 | 7 → 21 | 24 → 24 |

## Resource counts and cost of assistance

Whole-map means, including water resources. Relative resource changes are measured against the same generator’s Standard preset, before CSC additions. These are observed emulator results, not native-game estimates or the nominal density factors.

| Setup | Resource tiles/map before CSC | Change vs own Standard | Added deposits/map | Additions / original resource tiles |
|---|---:|---:|---:|---:|
| Vanilla · Sparse | 351.7 | -13.4% | 2.8 | 0.80% |
| Vanilla · Standard | 405.9 | +0.0% | 2.8 | 0.69% |
| Vanilla · Abundant | 441.6 | +8.8% | 2.7 | 0.61% |
| TAR · Sparse | 381.4 | -9.3% | 2.4 | 0.63% |
| TAR · Standard | 420.5 | +0.0% | 2.9 | 0.69% |
| TAR · Abundant | 457.6 | +8.8% | 2.7 | 0.59% |
| TAR · Plentiful | 710.5 | +69.0% | 5.4 | 0.76% |
| TAR · Truly Abundant | 906.5 | +115.6% | 5.9 | 0.65% |

Across all 80 layouts: **276 additions**, mean 3.45/map, maximum 8/map. No selected repair failed for lack of a safe feasible placement or budget in the emulator. Every helper placement preserves the regenerated resource layout’s existing deposits and every continent’s last Base/both-class opportunity. This does not mean native feasibility will be equally permissive.

## Interpretation

1. **Resource copies alone do not solve continental specialization.** Natural Stonemason coverage remains 9/30 at every preset, while its ordinarily clearable both-class tile count rises from 149 at vanilla Sparse to 426 at TAR Truly Abundant. More sites appear on already supported continents. The stock four-type luxury allocation remains a strong constraint.
2. **The normal-level helper is close to the intended scale without heavy intervention.** Vanilla Abundant ends at Tailors 18/30, Stonemasons 19/30 and Goldsmiths 10/30, against aims 20/30, 20/30, 10/30. Its 27 additions across ten layouts add only 0.61% to resource-tile counts. Aiming for exact agreement here would overfit a small paired sample.
3. **High TAR assistance removes much of the regional rarity for three industries.** Plentiful and Truly Abundant both finish at 30/30 for Tailors, Stonemasons and Apothecaries. Goldsmiths remain 17/30 and 21/30, respectively. This is the implemented 100% capped coverage aim functioning as designed, rather than evidence that every continent naturally supports those industries. Whether this fits the desired regional identities is a design decision to review before native testing.
4. **Apothecaries remain a mild weak spot at ordinary abundance.** Their final coverage is 15–19/30 across the six normal presets. Vanilla Abundant adds nothing to its 17/30 because the keyed probabilistic draws did not select those missing continent cases. No budget/habitat rejection explains the shortfall. This sample is too small to justify changing odds by itself.
5. **Base-only supply is much more widespread.** Bakers, Tailors, Stonemasons, Carpenters, Blacksmiths and Brewers have Base support on 30/30 continent instances at every setup. Apothecaries have 24–27/30 before assistance; Goldsmiths are much more variable at 8–30/30. These Base counts concern Stage 2/3 geography, without implying improvements or Services are already established.
6. **Raw district-site counts overstate the number of distinct choices.** At vanilla Abundant, Tailors rise 46→57 sites and 25→36 connected site clusters across ten layouts; Goldsmiths 9→21 sites and 7→17 clusters. Connected clusters are still not independent material-supply pairs or proof of simultaneous city placement.

## Verification and artifacts

- All 80 runs checked source immutability, empty/eligible additions, per-map/per-continent budgets, original generated resources, and agreement between the Lua audit and an independent Python continent census.
- Fresh complete reruns of vanilla Sparse, vanilla Abundant and TAR Truly Abundant instance1 reproduce resource layouts, helper audits and final plots exactly.
- Viewer geometry/census verification passes 23,040 comparisons on all 80 maps. Functional viewer checks cover all 80 instances, all 8 setups and all 8 Quarter aggregate comparisons; no fresh browser visual rendering review was performed.
- Historical 45 viewer entries are preserved unchanged. The combined viewer now has 125 entries; the standalone offline viewer contains only the 80 new cases.

Authoritative generated evidence: `C:/Users/Shadow/Desktop/Codex/csc-offline-abundance-20261016/` (`viewer.html`, `maps.json`, `analysis.json`, `coverage.csv`, `map-stats.csv`, `continent-stats.csv`, frozen profiles, before/after maps, audits and Lua logs). Source runner: `project/tools/map_lab/abundance_study.py`.

Native validation remains deferred at Henno’s request. These runs screen the policy; they do not demonstrate native RNG, sorting, start adjustment or full engine parity.
