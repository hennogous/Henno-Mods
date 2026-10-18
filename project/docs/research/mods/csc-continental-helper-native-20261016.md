# Native CSC continental helper comparison — 16 October 2026

Five fresh Civ maps test the continental resource helper on the same five seed pairs and rosters as the four-type Abundant controls and offline previews. CSC plus official content; Online, Prince, Small-size Continents.lua, six majors, nine city states, animal materials enabled. No turns advanced and no saves requested.

**All sixteen native additions succeeded. Continental coverage matches the offline previews for every Quarter.** Six deposits use different positions; ten match their preview coordinates. All sixteen original preview positions also pass the native eligibility check, so the location differences come from changed candidate lists rather than rejected preview placements.

## Coverage

Named continents with at least one both-class candidate, allowing ordinary future clearing. Fifteen continents across five maps. Naturally higher coverage is retained.

| Quarter | Before | Offline preview | Native Civ result | Approximate target |
|---|---:|---:|---:|---:|
| Bakers | 12/15 | 12/15 | 12/15 | 10/15 |
| Tailors | 3/15 | 11/15 | 11/15 | 10/15 |
| Apothecaries | 9/15 | 9/15 | 9/15 | 10/15 |
| Stonemasons | 4/15 | 8/15 | 8/15 | 10/15 |
| Carpenters | 15/15 | 15/15 | 15/15 | 10/15 |
| Blacksmiths | 15/15 | 15/15 | 15/15 | 10/15 |
| Goldsmiths | 2/15 | 6/15 | 6/15 | 5/15 |
| Brewers | 11/15 | 11/15 | 11/15 | 10/15 |

| Map | Map seed | Game seed | Added deposits | Deposits moved from preview | Differing final resource tiles | Native habitat checks | Offline disagreements |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | 830102 | 940104 | 5 | 4 | 8 | 24,420 | 105 |
| 2 | 830203 | 940207 | 2 | 0 | 0 | 25,839 | 110 |
| 3 | 830304 | 940310 | 1 | 0 | 0 | 26,664 | 97 |
| 4 | 830405 | 940413 | 3 | 1 | 2 | 25,509 | 99 |
| 5 | 830506 | 940516 | 5 | 1 | 2 | 24,156 | 122 |

Each moved deposit produces two differing resource cells: its old preview position and its native position. All sixteen resource types match their corresponding preview selections. Fine-grained site counts can differ even when continental coverage is identical; the viewer and `site-comparison.csv` retain those differences.

## What ran in Civ

This validates a native API-backed prototype of the proposed late resource pass. The shared **Python** helper still owns selection, continental palettes, probabilities, budgets and its seeded RNG (20261016). It was recomputed from each freshly generated native map and a live native eligibility sweep. The run did not simply replay the sixteen saved preview coordinates.

For each map, the harness:

1. Generated the stock four-type Abundant map and exported its untouched state at turn 1.
2. Verified all 3,404 terrain, feature, resource, continent, river/lake, ownership, district and adjacency records against the paired control. Material definitions also matched.
3. Queried actual `ResourceBuilder.CanHaveResource` for each mapped, map-spawnable resource on every otherwise empty passable land tile without a district.
4. Ran the same helper against that native eligibility table. Before mutation, checked every proposed deposit again; immediately before each setter, repeated the native check and then verified the resulting resource type.
5. Exported every final native plot and compared it exactly with the accepted plan. Every original deposit, terrain and feature remained intact, as did each continent's last Base-supported and both-class opportunity.
6. Returned to the menu. Original 141 community-mod flags and auto-start false were freshly verified; all 111 installed CSC gameplay/source files were unchanged.

Civ was launched with a hidden-window request; Henno confirmed it stayed backgrounded. Setup, generation, API queries, placement, export and menu transitions used FireTuner without mouse/keyboard control. The game is left at the main menu.

## What this teaches the offline model

The live sweep made **126,588 checks**, with **533 disagreements** against the existing offline habitat interpreter. All disagreements were native rejections. This is a later phase than the original resource-generation calibration: starting locations have now been assigned.

The exporter was extended during Map 3 to record `Plot:IsStartingPlot()` indices. On Maps 3–5, **all 318 disagreements occur on the fifteen reserved starting plots per map**. No habitat disagreement remains on other tested plots for those three maps. Map 2's improvement diagnostic also rules out existing improvements as the explanation there.

Maps 1–2 were captured before the starting-plot field was added. Their 215 disagreements each cover fifteen distinct tiles and have the same rejection pattern, consistent with reserved starts, but those maps lack the direct flag capture needed to prove that classification. No extra native reruns were made just to fill that diagnostic gap.

The next offline fidelity change should respect captured starting-plot reservations when modeling a pass after initialization. A helper inserted before starting-position assignment would see a different eligibility environment; later normalization could also change its outcome. The original previews remain preserved so the comparison does not hide this approximation.

## Viewer and evidence

The viewer now contains **40 entries**: thirty original native survey maps, five offline helper previews and five native helper results. The default setup is **CSC helper · Civ API test**.

- **Placement comparison** switches between original resources, the offline preview and the native result while retaining the view.
- Orange numbered outlines and coordinate buttons inspect the selected scenario's deposits. Green rings and red crosses compare its site gains/losses against the original.
- Below the map, coverage columns compare Before / Preview / Civ for every industry. Selected-continent site counts and habitat discrepancy totals remain visible.
- Starting tile metadata is captured for Maps 3–5; the first two native exports retain their original schema.

Open `project/tools/map_lab/viewer.html`, `project/snapshots/map-lab/index.html`, or the updated Desktop package at `C:/Users/Shadow/Desktop/Codex/csc-luxury-diversity-20261016/viewer.html`.

Native evidence: `C:/Users/Shadow/Desktop/Codex/csc-helper-native-20261016/`, including five before/after maps, actual eligibility lists, planned additions, native placement transcripts, logs, source fingerprints, original/restored preferences and validation. `coverage-comparison.csv`, `site-comparison.csv`, `native-additions.csv` and `analysis.json` provide detailed results. Tools: `project/tools/map_lab/native_assist.py` and `verify_native_assist.py`.

The viewer's actual geometry functions pass 7,560 count comparisons across forty entries. The complete viewer runs in a DOM/canvas fixture and passes 4,800 original/preview/native control/count checks, including deposit navigation. These are functional source-level checks, not a new browser visual review.

## Remaining boundary

The test **does not run an installed Lua helper or validate automatic mod startup ordering**. Selection and RNG still run through the shared Python controller, while eligibility, placement and final map data come from Civ. Packaging a production pass, choosing its phase relative to other mods and porting its random selection still require implementation and native tests. Optional resource packs, other map scripts/sizes, unit interactions and completed Quarter/service operation were not tested.

The five paired development maps support the preview's feasibility and coverage accounting; they do not calibrate population-wide probabilities or guarantee the approximate 10/15 and 5/15 design targets.
