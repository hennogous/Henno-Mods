# CSC native luxury diversity experiment — 16 October 2026

Fifteen native turn-1 maps compare 4, 5 and 6 land luxury types per continent, using the same five map/game seed pairs and leader rosters. CSC and official content only; vanilla Abundant, Online, Prince, Continents.lua at Small size (74 × 46), six majors and nine city states. Animal resources enabled; unused modded resources cleaned. No turns advanced and no native saves required.

The private test script passes `LuxuriesPerRegion` to the installed GS ResourceGenerator. All other generation decisions use the installed game scripts. Read-only phase captures and RNG traces were added during the batch for offline calibration. The five four-type controls reproduce every earlier vanilla-Abundant terrain, feature and resource tile exactly.

Background generation was tested while Henno confirmed Civ was backgrounded and he continued working. FireTuner performed setup, generation, turn-1 export and return to menu without mouse or keyboard input. Window focus could not be independently observed because Computer Use access to Civ was denied; this does not certify that loading can never steal focus on other configurations.

## Diversity and continental coverage

| Configured types | Named continents | Mean land luxury types / continent | Mean luxury tiles / continent | Mean industries with Base sites / continent | Mean industries with both-class sites / continent |
|---:|---:|---:|---:|---:|---:|
| 4 | 15 | 4.00 | 22.8 | 7.27 / 8 | 4.73 / 8 |
| 5 | 15 | 5.00 | 22.6 | 7.47 / 8 | 5.07 / 8 |
| 6 | 15 | 6.00 | 22.0 | 7.80 / 8 | 5.40 / 8 |

Diversity is measured after starting-position adjustment and counts land luxuries. It can differ from the constructor target. More types also divide the luxury occurrence budget among more types; this is not simply an abundance increase. Industry coverage means at least one candidate with ordinary future clearing allowed, not guaranteed service operation.

## Material opportunities

Mean candidate tiles per whole map, with ordinary future clearing allowed. Base includes both-class sites. Stages 2–3 can use Base supply; Stage 4 requires both classes. Improvements, research, customer districts and other service requirements still apply.

| Quarter | Base, 4 | Base, 5 | Base, 6 | Both, 4 | Both, 5 | Both, 6 | Continents with Base, 4 / 5 / 6 | Continents with both, 4 / 5 / 6 |
|---|---:|---:|---:|---:|---:|---:|---|---|
| Bakers | 338.6 | 328.4 | 334.2 | 31.6 | 37.6 | 37.4 | 15/15 / 15/15 / 15/15 | 12/15 / 14/15 / 14/15 |
| Tailors | 100.6 | 100.8 | 105.6 | 1.8 | 1.6 | 1.6 | 15/15 / 15/15 / 15/15 | 3/15 / 3/15 / 5/15 |
| Apothecaries | 82.8 | 89.0 | 96.6 | 4.6 | 2.8 | 5.8 | 11/15 / 14/15 / 15/15 | 9/15 / 9/15 / 12/15 |
| Stonemasons | 622.0 | 624.4 | 625.6 | 17.6 | 22.0 | 17.0 | 15/15 / 15/15 / 15/15 | 4/15 / 7/15 / 7/15 |
| Carpenters | 672.2 | 673.8 | 675.2 | 87.0 | 74.8 | 75.4 | 15/15 / 15/15 / 15/15 | 15/15 / 15/15 / 15/15 |
| Blacksmiths | 604.8 | 606.6 | 607.6 | 27.0 | 28.0 | 32.2 | 15/15 / 15/15 / 15/15 | 15/15 / 14/15 / 15/15 |
| Goldsmiths | 46.6 | 39.2 | 37.0 | 0.6 | 0.2 | 0.0 | 8/15 / 8/15 / 12/15 | 2/15 / 1/15 / 0/15 |
| Brewers | 245.2 | 246.6 | 245.0 | 21.0 | 16.2 | 17.6 | 15/15 / 15/15 / 15/15 | 11/15 / 13/15 / 13/15 |

## Reading the result

Continents with at least one ordinarily clearable Base-supported site for **every** Quarter: 4 types: **5/15**, 5 types: **7/15**, 6 types: **12/15**.

Six types is a promising next candidate for broader seed testing. In this sample Apothecaries gain Base coverage on all fifteen continents, while Goldsmiths still lack Base opportunities on three. Goldsmiths have no both-class sites anywhere in the six-type maps, even under the raw passable-land filter. More luxury diversity improves regional breadth but does not reliably create nearby pairs of the two classes.

Keep Stage 4 rarity as a separate design choice. A future light-touch audit could focus on missing Base materials before considering any both-class adjacency repair. No production resource intervention has been installed.

## Interpretation limits

This is a paired five-seed sample, not a guarantee for every map script, map size or resource pack. Changing the number of types changes subsequent random draws and starting adjustments, so individual resource layouts are not nested additions. The paired-map CSV records any downstream feature differences; terrain and continent IDs are checked separately.

A candidate can use material sources across a continent border. Candidate tiles can share sources and are not independent settlements or simultaneous Quarter builds. Hidden strategics and designed Hills/Woods/Rainforest materials count. Bakers/Tailors use runtime material tags; the other six use their individual design pages. Goldsmiths use Diamonds/Jade; the older overview’s additional Pearls are excluded from the main comparison.

Rare Stage 4 support is not automatically a defect. This experiment supplies evidence before choosing any production map intervention. CSC’s gameplay and installed game/Workshop files were unchanged.

## Viewer and raw results

- Open `project/tools/map_lab/viewer.html` or the standalone `project/snapshots/map-lab/index.html`. The viewer retains the original fifteen maps and adds these fifteen native experiments.
- Select a 4/5/6 luxury resource setup, then use Continent, Opportunity supply and Continent comparison. Base/both industry coverage follows the clearing filter.
- Raw evidence: `project/snapshots/map-lab/luxury-study/`; detailed tables: `continent-opportunities.csv`, `continent-inventory.csv`, `paired-map-comparison.csv`; verification: `validation.json`.
- Offline reference captures and measured API/RNG mismatches: `project/snapshots/map-lab/native-calibration/`. Recorded-draw replay is a diagnostic aid, not an implementation of Civ’s RNG or a new-terrain generator.
