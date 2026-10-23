# CSC Quarter resource incentives — 19 October 2026

The native incentives work, and the preserved turn-200 observations show better material placement and more active Services. Improvement use is mixed: improved plots per city rose, but improved plots per population and the Bakers' mapped-material improvement fraction did not improve. This is an exploratory single-seed result, not a validated AI default.

The simulation reached **turn251**. A one-turn autoplay overshoot triggered the controller's endpoint assertion before it exported the frozen250 census. Complete primary observations are preserved through **turn225**, with a real common comparison at200. Autosaves249/250/251 are preserved and hashed; the250 analysis is unfinished. No additional reloads or games were started after this endpoint failure. Original142 mod preferences and auto-start=false were restored and verified.

| Turn200 metric | Previous density-v4 | Quarter-resource candidate |
|---|---:|---:|
| Cities / population | 47 /537 | 50 /653 |
| Owned unpillaged improved plots | 315 | 373 |
| Improved plots per city | 6.70 | 7.46 |
| Improved plots per100 population | 58.66 | 57.12 |
| Builders alive / remaining charges | 39 /101 | 29 /65 |
| Completed Bakers with owned Base access | 15/44 | 17/44 |
| Completed Tailors with owned Base access | 1/20 | 4/28 |
| Bakers' adjacent owned Base plots improved | 10/16 | 11/19 |
| Tailors' adjacent owned Base plots improved | 0/1 | 2/4 |
| Cities with Bakers Growth Service | 7 | 8 |
| Cities with Bakers Housing Service | 1 | 3 |
| Cities with Tailors Faith Service | 0 | 1 |

For comparable placement events where a Base-supported alternative was available, excluding turns51–67 from **both** runs, Bakers selected one13/17 previously versus19/20 now; Tailors1/5 versus6/7. Those are observed decision samples, not counts of every completed Quarter.

Builder event totals over the common observed window **turns68–200** were103 versus104 trained,40 versus46 purchased, and176 versus172 added to the map. Additions include captures/grants. The smaller remaining Builder stock does not by itself prove faster work: losses and charges spent can both reduce it.

At225, the candidate had54 cities,743 population and389 improved plots(7.20/city), versus51/607/322(6.31/city). Bakers had16/44 Base access and one both-material site; Tailors4/26 Base access. Active Service-source cities were6 Bakers Growth,4 Housing and1 Tailors Faith, versus5/1/0. Service counts can overlap within cities.

## Native mechanism and versions

Quarter-owned matching-resource private yield40 is retained; an additional80 uses the Textile Workshop pattern: player-improvement attachment followed by a single-plot yield modifier. Exact live CSC resource mappings drive the filters. Improvement valuation90, Builder priority50, and native bonus-resource12/river4/sales10 guidance remain. The previous run used Builder900.

The disposable fixture verified actual UI values40 unimproved,120 improved,40 pillaged,0 for unrelated material and0 for matching Flax away from the Quarter. Original world census was identical after pristine reload. In these tests the gameplay Plot:GetYield read omitted modifier additions; UI readback was required. Fixtures must use plots already in native city yield collections: manually assigning outer-ring ownership had produced misleading zeros.

The actual native sample at201 matched all28 expected resource signals. Earlier samples included incomplete/pillaged Quarters and newly placed districts while the probe assumed every source functioned. One earlier discrepancy remains unresolved; samples occurred several turns after their similarly named frozen primary checkpoint. Full audit is retained, not suppressed. Effect application does not establish prospective AI forecasting.

All natural segments use gameplay SQL SHA256 `237b6d344bf92603d289d53a8ebc38ac8ed480c1099107c392f3bc71fb81f995`. Actual source and121 installed gameplay files were archived before each segment:

- Initial natural segment: `trial-v2b/source-version/`.
- Continued same game: `trial-v2e-resume/source-version/`,42 source files, code version `quarter-owned-workshop80-builder50-v2e-atomic-observer-recovery`.
- Earlier failed setups/recovery attempts have separate archives and are not separate natural experiments. They changed instrumentation, not gameplay.

## Limits and next step

Map830102/game940104, Online/Prince/Small Continents, vanilla Standard resources, CSC material pass4, CSC without RH/TAR. Starting world matched the previous run. Current renderer was DX12; previous was DX11. Both private resource incentives and Builder priority changed, and later expansion/war/research diverged. One seed cannot isolate their effects.

A read-only UI probe error interrupted the original observer after50. The same63 autosave was recovered; its byte-identical copy in the normal native save directory loaded successfully. A subsequent observer timing race was fixed with an atomic capture at67. Events51–67 and the50 Builder/private-yield exports are missing. Primary endpoint counts are actual state; decision histories cover observed windows. Source/controller/installed hashes verified with no mismatches, event prefixes are consistent, and native database validation passed. This is a **partial analysis**, not a successful250-export validation.

Before the deferred multi-game work, inspect the preserved250 autosave and repair endpoint archival so a frozen target checkpoint is exported before strict stopping-turn checks. Optional probes must remain nonfatal, and named checkpoints should be paired with durable observer state. No further tests are scheduled. The candidate remains experimental.

Evidence root: `C:/Users/Shadow/Desktop/Codex/csc-ai-quarter-resources-20261018/`. Compact data: `final-partial-comparison.json`; checks and signal audit: `partial-validation.json`; original segment: `trial-v2b/`; continuation and249–251 autosaves: `trial-v2e-resume/`. The experiment ledger retains the setup and recovery history.

## Detailed turn-225 audit

This read-only analysis uses the last full primary checkpoint, turn225, at Online speed. Completed counts are holdings at that checkpoint, including acquisitions; they are not personal construction histories. Historical placement events have the explicit51–67 observation gap. No gameplay files, games or schedules were changed for this analysis.

### Players and completed Quarters

Parentheses show Quarters with at least one owned, visible matching Base material. Services count positive source-activation flags, with multiple Service types allowed in one city.

| Player | Cities | Population | Bakers (Base) | Tailors (Base) | Active Service-source flags |
|---|---:|---:|---:|---:|---:|
| Sweden / Kristina | 6 | 82 | 5 (0) | 3 (0) | 0 |
| Germany / Ludwig | 13 | 155 | 11 (5) | 6 (0) | 5 |
| Nubia / Amanitore | 10 | 130 | 8 (3) | 6 (2) | 1 |
| Phoenicia / Dido | 9 | 124 | 6 (2) | 4 (0) | 2 |
| Vietnam / Bà Triệu | 9 | 132 | 7 (4) | 4 (2) | 3 |
| Greece / Pericles | 7 | 120 | 7 (2) | 3 (0) | 0 |
| **Total** | **54** | **743** | **44 (16)** | **26 (4)** | **11** |

Germany also had two Bakers under construction. One completed Nubian Tailors was pillaged. Observed new Quarter placements by original placing player (incomplete history, not completed holdings) were Sweden5B/4T, Germany12B/6T, Nubia7B/6T, Phoenicia6B/5T, Vietnam8B/5T and Greece7B/2T. Capture, later removal and missing events explain why this differs from holdings.

### Resource adjacency

Counts are resource copies adjacent to completed Quarters, visible to and owned by the Quarter owner. Correct means mapped Base or Specialty for that Quarter. Incorrect means another ordinary resource, not inherently a bad tile. Artifact sites and shipwrecks are excluded. A resource shared by two Quarters contributes once to each Quarter. Completed pillaged Quarters remain in the denominator.

| Metric | Bakers | Tailors |
|---|---:|---:|
| Completed Quarters | 44 | 26 |
| Correct adjacent copies | 19 (18 Base + 1 Specialty) | 4 (all Base) |
| Incorrect adjacent copies | 35 | 27 |
| Mean correct / Quarter | 0.43 | 0.15 |
| Mean incorrect / Quarter | 0.80 | 1.04 |
| No correct owned material | 28/44 | 22/26 |
| Both Base and Specialty access | 1/44 | 0/26 |
| Quarters with improved Base access | 9/44 | 2/26 |
| Incorrect bonus resource, no Base material | 4/44 | 11/26 |
| Adjacent sales district including City Center | 43/44 | 23/26 |
| Adjacent non-City-Center sales district | 31/44 | 23/26 |

The previous run at225 averaged0.40 correct/0.70 incorrect for Bakers and0.09 correct/0.96 incorrect for Tailors. Including visible materials outside ownership only changes current correct means to0.45 Bakers and0.15 Tailors. Ownership alone does not explain the low counts. The generic bonus-resource guidance is an imperfect proxy, especially for Tailors; these endpoint counts do not establish whether a correct alternative was available at each placement decision.

### Services and buildings

Positive source flags at225:6 Bakers Growth,4 Bakers Housing,1 Tailors Faith;0 Tailors stage2 Production and0 stage4 Tourism for either industry. These are11 source/Service combinations across7 cities/Quarters, so7 of70 completed Quarters have any positive Service flag.

The separate unpillaged Service marker-building count is19:13 Bakers stage2,5 Bakers stage3 and1 Tailors stage3. Building presence is not interchangeable with a currently positive source flag; do not report19 as19 active sources.

Bakers had42 stage2 buildings,31 stage3 and15 stage4, but only9 Quarters had improved Base access. Tailors had23 Textile Workshops,19 Tailors and6 Fashion Houses, but only2 Quarters had improved Base access. No player had CIVIC_NAVAL_TRADITION or CIVIC_OPERA_BALLET in the captured complete civic lists at225; source SQL confirms these gate Tailors stage2 and stage4 respectively. All had the stage3 civic. Improving resources alone therefore cannot unlock the missing Tailors stage2 Service in this run. Nearby customer buildings and other complete Service conditions still matter.

### Resource losses under later districts

The following table counts observed new major-player districts on tiles whose last observed ordinary resource was subsequently absent. It excludes City Centers, Wonders, artifact sites and city-state placements. It does not treat retained strategic deposits as destroyed.

| Placement turns | Resource last seen unimproved | Last seen improved and unpillaged | Total |
|---|---:|---:|---:|
| 1-100 | 7 | 0 | 7 |
| 101-150 | 8 | 3 | 11 |
| 151-225 | 10 | 7 | 17 |
| **Total** | **25** | **10** | **35** |

All10 improved-resource cases were other districts, not Quarters. The three major-player Quarter placements over ordinary resources were last seen unimproved. Seven lost resource tiles after150 had been adjacent mapped supplies for existing matching Quarters.

Important evidence limit: improvement/removal/harvesting was not fully instrumented. These are last-observed states; a Builder may have harvested in the interval before district placement. For the10 improved cases, only one observation is within one turn of placement; other ages range6–24 turns. We cannot claim every district directly erased an intact improvement.

Three useful chronological examples, verified against the neighboring primary checkpoints:

| City | Last preceding state | Later district | Next observed state |
|---|---|---|---|
| Kawa | Turn150: improved Flax supports Bakers and is Tailors sole Base; Bakers Growth active | Commercial Hub at171 | Turn175: Flax gone, Tailors Base0, Bakers improved Base0 and Growth inactive |
| Sidon | Turn175: improved Maize is Bakers sole Base; Growth active | Commercial Hub at181 | Turn200: Base0 and Growth inactive |
| Granada | Turn200: improved Rice is Bakers sole Base; Growth active | Commercial Hub at219 | Turn225: Base0 and Growth inactive |

These sequences establish lost material access and lost Service flags, without proving the exact intermediate harvest/removal action or how the AI forecast the pseudo yield. Resource preservation deserves its own experiment rather than assuming a successful improvement remains safe.

Full ordinary-resource district cases (last-seen evidence, same observation limits):

| Turn | Player | Resource | Later district | Last improvement | Observation age | Supported existing Quarter |
|---|---|---|---|---|---:|---|
| 45 | Vietnam | BANANAS | HOLY_SITE | none | 20 | none recorded |
| 47 | Phoenicia | BANANAS | THEATER | none | 22 | none recorded |
| 68 | Vietnam | BANANAS | CSC_TAILORS_QUARTER | none | 1 | none recorded |
| 74 | Sweden | DEER | CAMPUS | none | 7 | none recorded |
| 77 | Germany | DEER | ENCAMPMENT | none | 2 | none recorded |
| 89 | Greece | STONE | COMMERCIAL_HUB | none | 14 | none recorded |
| 91 | Vietnam | DEER | AQUEDUCT | none | 16 | none recorded |
| 106 | Vietnam | COPPER | THANH | none | 6 | none recorded |
| 111 | Phoenicia | FISH | COTHON | none | 11 | none recorded |
| 115 | Germany | WHEAT | HOLY_SITE | FARM | 15 | none recorded |
| 116 | Greece | SHEEP | CSC_BAKERS_QUARTER | none | 16 | none recorded |
| 119 | Nubia | DEER | CAMPUS | none | 19 | none recorded |
| 121 | Nubia | DEER | COMMERCIAL_HUB | none | 21 | none recorded |
| 124 | Greece | STONE | COMMERCIAL_HUB | QUARRY | 24 | none recorded |
| 125 | Germany | CATTLE | ENCAMPMENT | none | 0 | none recorded |
| 131 | Greece | SHEEP | INDUSTRIAL_ZONE | none | 6 | none recorded |
| 134 | Phoenicia | BANANAS | INDUSTRIAL_ZONE | PLANTATION | 9 | none recorded |
| 138 | Nubia | SHEEP | ENCAMPMENT | none | 13 | none recorded |
| 152 | Sweden | RICE | NEIGHBORHOOD | none | 2 | none recorded |
| 152 | Germany | CSC_FLAX | CSC_BAKERS_QUARTER | none | 2 | none recorded |
| 171 | Nubia | CSC_FLAX | COMMERCIAL_HUB | FARM | 21 | BAKERS, TAILORS |
| 172 | Sweden | STONE | NEIGHBORHOOD | none | 22 | none recorded |
| 176 | Nubia | CSC_FLAX | THEATER | FARM | 1 | none recorded |
| 180 | Germany | CSC_FLAX | THEATER | none | 5 | none recorded |
| 181 | Germany | RICE | SPACEPORT | FARM | 6 | BAKERS |
| 181 | Phoenicia | MAIZE | COMMERCIAL_HUB | FARM | 6 | BAKERS |
| 182 | Sweden | CATTLE | COMMERCIAL_HUB | none | 7 | BAKERS |
| 188 | Sweden | FISH | WATER_ENTERTAINMENT_COMPLEX | none | 13 | none recorded |
| 189 | Vietnam | MAIZE | DAM | FARM | 14 | BAKERS |
| 190 | Phoenicia | DEER | CAMPUS | none | 15 | none recorded |
| 197 | Germany | SHEEP | ENCAMPMENT | none | 22 | none recorded |
| 199 | Germany | WHEAT | AERODROME | FARM | 24 | BAKERS |
| 202 | Germany | STONE | THEATER | none | 2 | none recorded |
| 217 | Germany | SHEEP | CAMPUS | none | 17 | none recorded |
| 219 | Germany | RICE | COMMERCIAL_HUB | FARM | 19 | BAKERS |

Reproduction: `project/tools/ai_baseline/quarter_resource_detail.py`, output `quarter-detail-20261019/details.json` under the evidence root. Resource visibility/classes come from archived `diagnostic-11/native-debug.sqlite` in read-only mode. Only Resources metadata is used from that disposable diagnostic DB; district and Service state comes from natural-play snapshots. Raw excluded cases and retained-resource cases remain in the output.

## Builders per player — turn200

Latest complete Builder census is200, not225. These ratios divide each player's total Builders alive by cities currently held; they are empire averages, not Builder assignments to individual cities. Current Builder priority50/improvement valuation90; previous Builder priority900/improvement valuation90. Resource incentives and other simulation outcomes also differ.

| Player | Current cities | Builders alive | Builders/city | Charges left | Previous Builders/city |
|---|---:|---:|---:|---:|---:|
| Sweden | 6 | 5 | 0.83 | 13 | 0.50 |
| Germany | 11 | 8 | 0.73 | 22 | 0.67 |
| Nubia | 9 | 5 | 0.56 | 10 | 0.75 |
| Phoenicia | 8 | 4 | 0.50 | 6 | 0.60 |
| Vietnam | 9 | 3 | 0.33 | 4 | 1.20 |
| Greece | 7 | 4 | 0.57 | 10 | 1.00 |
| **Total / weighted average** | **50** | **29** | **0.58** | **65** | **0.83** |

Current total progression at100/150/200 is21/24/29 Builders across28/39/50 cities (0.75/0.62/0.58 per city). Previous200 had39 Builders across47 cities and101 charges. No current player exceeds one Builder per city; largest stock is Germany8 across11 cities. These holdings do not establish idleness or quantify production opportunity cost. Current improved plots373 vs315 previously,7.46 vs6.70 per city (but57.12 vs58.66 per100 population). Keeping priority50 and improvement valuation90 fixed for the next resource-signal experiment is reasonable; this is not causal validation of optimal Builder production.

Compact reproducible census joins saved under the evidence root at `quarter-detail-20261019/builders-by-player.json`.

## Technology and civic progression

Furthest era among completed items; not world era, full era completion or selected in-progress research. Definitions from archived native diagnostic11; known items from actual natural game checkpoints.

| Player | Tech era at200 | Civic era at200 | Tech era at225 (total techs) | Civic era at225 (total civics) |
|---|---|---|---|---|
| Sweden | Atomic | Modern | Information (53) | Information (43) |
| Germany | Information | Future | Future (68) | Future (55) |
| Nubia | Information | Information | Information (64) | Future (53) |
| Phoenicia | Information | Information | Information (57) | Future (48) |
| Vietnam | Information | Atomic | Future (64) | Information (44) |
| Greece | Atomic | Atomic | Future (64) | Information (45) |

Every player had reached Information/Future research on both trees by225; the absence of Naval Tradition is not explained by a generally Medieval research frontier. The snapshot observer records HasTech/HasCivic, not current research selection.

Naval Tradition (Medieval) requires Defensive Tactics. Opera and Ballet (Industrial) requires The Enlightenment. Neither is a prerequisite for another civic in the archived native CivicPrereqs table. All six had Defensive Tactics by100 and The Enlightenment by150, yet neither optional civic was completed by anyone at100/150/200/225. They were eligible but bypassed.

All six already had the producer/Quarter unlocks Craftsmanship, The Wheel, Construction, Guilds and Humanism by100. All also had Bakers Feudalism/Medieval Faires by100 and Urbanization by150. Divine Right, the Tailors stage3 Service gate, was held by1/6 at100,3/6 at150,5/6 at200,6/6 at225. Targeted optional Service-civic guidance is more justified than indiscriminately increasing every CSC technology/civic preference.

An additional vanilla-data defect: the archived native PericlesCivics favored-item row uses CIVIC_NAVAL_TRADITIION (extra I), which is not a valid civic. RH corrects that exact typo in core/Main/RH_LAI_Main4.sql:438. It may explain a missing intended Greek preference, not why all six skipped the civic. No CSC correction has been implemented during this audit.

RH demonstrates direct native research guidance: core/Strategies/RH_Naval.sql registers a Civics list, connects it to STRATEGY_NAVAL and favors CIVIC_NAVAL_TRADITION (Favored1,Value0). Its CultureVictoryCivics list similarly favors Opera and Ballet. These are implementation precedents, not evidence that a particular CSC preference magnitude is optimal.

Proposed next research treatment, not deployed: native Civics preferences for useful Tailors Service unlocks, with Naval Tradition the first diagnostic target; avoid automatically rushing Opera and Ballet everywhere while stage4 material access remains scarce. Conditional prioritization when the player has a viable Quarter/customer setup would be preferable once the condition mechanism is validated. Leave Builder and placement treatment unchanged while measuring research adoption and resulting Services.

Compact data: evidence-root quarter-detail-20261019/research-by-player.json. No game launch, schedule, gameplay edit or research preference was applied.

## Follow-through on adjacent Base improvements

At225, distinct owned Base resource plots adjacent to completed Quarters are Bakers9/17 improved (53%),8 unimproved; Tailors2/4 improved (50%),2 unimproved. None of the remaining unimproved plots are merely pillaged improvements. These are per-industry unique resource plots, not per-Quarter adjacency instances; shared plots are counted once within each industry. Current improved state alone does not show whether the improvement preceded the Quarter.

Checkpoint histories confirm longstanding unfinished cases under the same owner with an adjacent completed matching Quarter: Germany Rice1753 was unimproved at every captured checkpoint100–225; Nubia Wheat2526 at50–225; Greece Maize1417 at67–225; Vietnam Sheep1572 at75–225. This means lack of improvement is not solely recent placements awaiting Builders. Other examples are newer, and snapshots cannot exclude intervening improvement/removal between observations.

At200, the comparable Bakers Base improvement rate was11/19 (58%) versus previous10/16 (63%), with no demonstrated improvement from the new treatment; Tailors2/4 versus0/1 remains a tiny sample. Better placement, resource preservation and actual improvement priorities remain separate issues. Effect application is proven, AI forecasting is not. Compact histories: evidence-root quarter-detail-20261019/unimproved-base-history.json. No tuning changes or live game operations.
