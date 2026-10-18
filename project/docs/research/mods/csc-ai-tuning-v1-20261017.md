# CSC AI tuning v1 — matched-seed native trial

The first candidate produced much more Quarter/sales co-location in one real game. Material-site choice did not show a convincing improvement, and more supporting deposits were covered by districts. The exact-material modifier works on completed Bakers' Quarters; prospective AI recognition remains unproven.

Implementation and RomanHoliday references: [CSC AI tuning](../../integrations/csc-ai-tuning.md). Control: [paired Standard baseline](csc-ai-paired-standard-20261016.md), vanilla game 1. This is exploratory evidence, not a calibrated release or proof of general superiority.

## Treatment and setup

- Native private placement yield: reciprocal Quarter/sales adjacency **10 per neighbor**, owned visible Base presence **12 once**, Specialty presence **4 once**. Only Bakers and Tailors are included. Material conditions are AI-gated native district modifiers; sales rules use native district adjacency and live sales tags, including direct unique replacements.
- Major-civ improvement pseudo-yield preference **25**; the global default remains **3.0**. This is a general valuation preference, not specific Builder orders or a promised percentage increase.
- Map seed **830102**, game seed **940104**; `Continents.lua`, Small **74×46**, six majors, nine city states, Online, Prince, vanilla Standard resources. CSC v3 map assistance and animal mappings enabled, unused modded resources cleaned, M&C off. TAR and RH disabled.
- Leaders: Kristina, Ludwig, Amanitore, Dido, Lady Trieu, Pericles. Starting map, leader identities and initial research matched the control. All 3,404 tiles matched across the 13 recorded world fields.
- Continuous native autoplay from turn 1 to the beginning of turn 250. No scripted construction, research grants, plot manipulation or forced adjacency refresh. The original read-only observer/controller is unchanged.

The virtual yield has no real-yield conversion. No marker technology, Quarter construction preference, research preference or Service-planning script was added. Existing district/building definitions, material tags and global pseudo-yield defaults matched the baseline.

## Choices when relevant owned alternatives existed

Candidates passed native plot-placement checks and were scanned at most one turn before placement. They do not establish affordability, future tile purchases or the best overall city plan. Capture-related repeated district events are excluded.

| Choice | Baseline | Tuning v1 |
|---|---:|---:|
| Bakers chose sales adjacency | 31/46 (67%) | 54/54 (100%) |
| Later sales chose Bakers adjacency | 9/28 (32%) | 49/51 (96%) |
| Tailors chose sales adjacency | 2/8 (25%) | 22/23 (96%) |
| Later sales chose Tailors adjacency | 12/25 (48%) | 27/32 (84%) |
| Bakers chose Base access | 14/25 (56%) | 16/28 (57%) |
| Bakers chose Base + sales | 11/21 (52%) | 16/26 (62%) |
| Tailors chose Base access | 1/1 | 1/4 |
| Tailors chose Base + sales | 0/0 | 0/2 |

The strong sales response supports using native placement signals. It does not identify the separate causal contributions of sales weights, material modifiers and improvement preference. Tailors' material denominators are especially small.

These behavior tables retain all six autoplay majors, matching the baseline. Player 0 remains flagged human during native autoplay and is therefore excluded by the AI-only material modifier. Restricting material choices to the five non-human players gives Bakers Base **12/21 → 12/23**, Bakers Base + sales **10/19 → 12/21**, and Tailors Base **0/0 → 0/3**. This also provides no convincing material-choice improvement. The native material probe uses only these non-human players.

## Endpoint development

| Metric | Baseline | Tuning v1 |
|---|---:|---:|
| Major cities / population | 48 / 551 | 57 / 686 |
| Owned unpillaged improved plots | 223 | 331 |
| Completed Bakers | 45 | 49 |
| Bakers with Base | 8/45 | 6/49 |
| Bakers with sales other than City Center | 9/45 | 37/49 |
| Adjacent owned Bakers Base plots improved | 2/9 | 3/6 |
| Supporting Bakers material plots subsequently covered by districts | 5 | 10 |
| Bakers stage 2 / 3 / 4 buildings | 44 / 15 / 9 | 45 / 30 / 16 |
| Completed Tailors | 22 | 29 |
| Tailors with Base | 1/22 | 0/29 |
| Tailors with sales | 10/22 | 26/29 |
| Adjacent owned Tailors Base plots improved | 1/1 | 0/0 |
| Tailors stage 2 / 3 / 4 buildings | 19 / 7 / 5 | 26 / 15 / 9 |
| Native Growth Service source cities | 1 | 2 |
| Native Housing Service source cities | 0 | 3 |

Four completed trial Bakers were pillaged; none of the completed control Quarters or trial Tailors were pillaged. Endpoint adjacency/building counts include completed Quarters, with pillage retained separately in raw data; improvement counts exclude pillaged improvements. Both-class access was zero for both Quarters in both endpoints. No other native Service source flags were active.

More improvements and Services are encouraging observations, but cities, population, wars and later development also diverged. These counts do not establish a specific Builder or Service-planning improvement. Material-free Quarters can still be worthwhile for sales. Base supports stages 2/3; Specialty is for rarer stage 4.

## Native material/placement probe

The probe ran **after** the natural benchmark, final save and logs were archived. It was read-only and executed in UI `PlotInfo`, whose private-yield enumeration was filtered but indexed lookup remained available.

- 648 candidate rows, 540 for non-human players. Of 72 native plot-legal AI candidate rows, only two had adjacent owned visible materials. Neither included an extra material contribution in `Plot:GetAdjacencyYield`.
- All 43 AI candidate rows with materials, including currently illegal candidates, omitted the material contribution in that prospective adjacency call.
- Seven complete, unpillaged AI Bakers had owned visible Base or Specialty. In **all seven**, `district:GetYield(privateYield) - plot:GetAdjacencyYield(...)` was exactly **12 for Base or 4 for Specialty**. `district:GetAdjacencyYield` included the same completed material contribution as the total yield.
- Example Base site: completed total/adjacency **32**, prospective plot adjacency **20**. Example Specialty site: **24** versus **20**. Another Base site was **22** versus **10**.
- A simple count of neighboring sales districts overpredicted one completed site's sales signal by 10. Native completion/pillage/other adjacency semantics differ from the geographic count; the material comparison therefore uses the native plot value, not `10 × counted sales`.
- Material modifier introspection succeeded: 174 instances, 172 marked active. Active instance counts alone are not evidence that their subject requirements passed; the measured completed yields provide the useful activation evidence.

**Interpretation:** the material effect exists after construction. The prospective plot API does not reproduce it. That API reports adjacency rather than a complete internal AI score, so absence there does not prove that the AI ignores a base-yield modifier. Conversely, completed activation does not prove pre-construction planning. No Tailors material activation was available at this endpoint.

A material-only controlled comparison is the next useful diagnostic: identical pre-decision states with amounts 0 versus 12/4, keeping sales weights, improvement preference, resources and legality fixed. Compare actual selected sites and attributable native contract values; mirror site positions to check deterministic tie-breaking. Resource preservation deserves a separate intervention/test because the sales-clustering response coincided with more deposits being covered.

## Verification and evidence

Output root on Shadow: `Desktop/Codex/csc-ai-placement-v1-20261017/trial`. Earlier turn-one smoke attempts in its parent directory and the superseded improvement-only folder are excluded.

- `batch.json`: complete. `validation.json`: one game, eleven snapshots, 1,370 recorded events, zero observer errors, all event prefixes intact, initial/final save hashes verified, 121 installed gameplay files unchanged during the run.
- `baseline-build-comparison.json`: six new AI/text/UI files and four changed existing files (manifest plus three UI include wrappers); all other installed gameplay files matched the baseline.
- `native-database-validation.json`: 33 sales edges, correct coefficients, no marker technology, global improvement default unchanged, repeated SQL application identical.
- Native UI smoke passed in PlotInfo, PlotToolTip, ReportScreen and CivilopediaScreen. Gameplay enumerated the private yield; these four UI contexts enumerated the six real yields and preserved indexed lookup. The offline read-only-cache fixture also exercised the shipped report's worked-tile summation.
- No gameplay database errors or Lua runtime errors in the archived run. Database.log contains unrelated official `CurrentClickouts` duplicate localization errors for `LOC_CLICKOUT_26_CAROUSEL_TOOLTIP`; these are not CSC AI failures.
- `preferences-restored.json`: native verification passed for all 141 unique installed mod IDs and auto-start restored to false. Civ returned to the main menu. There is no active test controller.
- `comparison.json`, report and CSVs retain placements, alternatives, improvement timing, resource retention, building gates, Services and timeline. `placement-probe.json` retains native totals/adjacency/candidates/modifier observations. Commands and source/installed hashes remain alongside them.

Benchmark timing is the first major activation at 250, matching the control procedure. Closing queued disaster playback before saving allowed one existing Bakers district in Vasteras to finish and its no-river flag to appear without advancing the game turn. The benchmark counts **78** completed Quarters; the separate settled save census has **79**. The native yield probe observes that settled state. Original snapshots are preserved and were not replaced by save-state data.

The post-archive probe was finalized while autoplay ran and is outside the controller's initial source pin. Its executed source is preserved in the command transcript; SHA-256 `06fc3656e65c82e1fe6bc452fd177cf202eb585e8401dab1812dfff5eebcef9b`. It did not alter the observed game. The controller and gameplay/UI tuning source pins all verified unchanged.
