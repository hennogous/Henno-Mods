# Quarter placement after fixing native delivery: 250 turns at Online speed

The new test completes turn 250 and closes cleanly. **All seven Quarters founded by
the guided major AIs have Base materials and at least +3 actual adjacency at turn 250.**
There are fewer Quarters: nine held at the endpoint versus 26 in the previous
assisted version. Seven are the new AI-founded sites; two were captured from a
city-state. The captured pair explains both remaining below +3 holdings.

The intervention now reaches the real decision: **57 / 57 new-site Quarter
comparisons consume the exact positive published value**, including 21 Tailors
comparisons. This is a strong improvement in placement selectivity on this seed,
not a claim that every planning or supply-chain problem is solved.

## What was compared

Normal Small Continents, Prince, Online speed; seeds 18461107 / 29461107. Original
major AI players 1–5; player 0 is the autoplay observer. Same initial map, leaders,
starts and units as the [previous assisted 250-turn run](csc-ai-economy-250-20261113.md).
The archived packages differ only in the CE DLL and five main CSC AI modules;
SQL, UI bindings, art and ordinary CSC map behaviour are identical. This compares
two assistance revisions, **not tuned versus untuned stock AI**. One seed does
not establish general balance or isolate the separate effects of delivery and
new bid values.

Main CSC policy only; no RHAI5, external AI/probe policy, forced unlocks, subsidies
or construction orders. Passive readers collect bids, native comparisons,
foundation/completion geometry, 25-turn censuses and native Storekeeper effects.
The shared controller owns launch, console, finite autoplay, saves and cleanup.
Scheduled file-based checks occur at turn 175 and completion; setup is also verified.
No second console client or desktop automation is used.

Census clocks use the start of the named turn, matching the preceding run.

Source: main CSC `be00cad9`, CE `dbfb93b`, native DLL SHA256
`400e675522916ce54a17a6765132da89ee23c90304a89e721c6289c31327394f`.
Engine: installed patched XP2 SHA092abfbb. Inputs `frozen03` / `candidate-packages03.json`.
The [implementation and qualification report](csc-ai-managed-placement-20261113.md)
records the failed packaging/flag assumptions and their corrections; they are
not counted as successful qualification.

## Placement quality and provenance

These are Production+Gold adjacency, using the actual loaded rules. Foundation
forecast permits one prospective local Mill, as agreed, but no future customer
district. Four of the seven sites already had direct +3 at foundation; three
needed their Mill allowance. **All seven reach current actual +3 or better by turn 250.**

| AI-founded site | Foundation | Forecast at foundation | Actual at turn 250 | Base / Specialty at turn 250 |
|---|---:|---:|---:|---|
| Bakers, player 3 / plot 1243 |27 |3 |4 |Base |
| Bakers, player 3 / plot 1094 |43 |4 |3 |Base |
| Bakers, player 1 / plot 1356 |86 |3 |4 |Both |
| Bakers, player 5 / plot 2686 |93 |3 |3 |Both |
| Bakers, player 2 / plot 2016 |136 |3 |5 |Base |
| Tailors, player 1 / plot 1137 |149 |3 |3 |Base |
| Tailors, player 2 / plot 2233 |155 |3 |3 |Base |

All seven complete, remain in the guided cohort and retain Base through the
sampled endpoint. Both dual-material sites retain Base and Specialty in every
census from 100 through 250. Only one has both classes recorded as working compatible
improvements at turn 250; resource retention is not the same as Builder development.

At turn 148 player 1 captures city-state player 6's Bakers 1799 and Tailors 1726. At turn 250
the former is actual +2 / potential +4; the latter is +0 with no Base. They were not
placed by our per-turn policy. City-states and player 0 remain outside its cohort,
although the native SQL guidance applies globally. No Quarter is demolished.

## Endpoint comparison

Counts below include all completed Quarters **held** by the five original AIs,
including captures. Improved means compatible and unpillaged, not necessarily
worked by a citizen. Current output and prospective Mill geometry are separate.

| Turn 250 measure | Previous assistance | New assistance |
|---|---:|---:|
| Completed Quarters held |26 (14 Bakers / 12 Tailors) |9 (6 Bakers / 3 Tailors) |
| Current adjacency at least +3 |8 / 26 |7 / 9 |
| Current adjacency at least +4 |4 / 26 |3 / 9 |
| Potential at least +3 with a local Mill |11 / 26 |8 / 9 |
| Potential at least +4 with a local Mill |5 / 26 |5 / 9 |
| Adjacent Base |23 |8 |
| Adjacent Base and Specialty |5 |2 |
| Compatible working Base improvement |18 |5 |
| Both classes working |2 |1 |
| Working Stage 2 producer |20 |7 |
| Working adjacent Stage 2 customer building |1 |2 |
| Physical/active-property Bakers Stage 2 chains |1 |2 |
| Physical/active-property Tailors Stage 2 chains |0 |0 |
| Verified Storekeeper active chain-turns |112 |153 |

The +3 share rises from 31% to 78%, and +4 from 15% to 33%. **There are not more strong
held sites in absolute numbers**: current +3 holdings fall 8 to 7, and current +4
fall 4 to 3. The achievement is removing weak original-AI placements, not creating
more total investment. The older conservative origin audit attributed 21 holdings
to guided AI construction, 15 below +3; the new lifecycle observer identifies seven
AI foundations and none below +3. That older origin method left one holding
unresolved, so it is not an equally complete foundation-time census.

## Historical untuned baseline: compare turn 200 with turn 200

The earlier table compares assistance revisions. The available **untuned stock-AI
baseline ends at turn 200**, so the valid time comparison uses this run's 200
census, not its 250 endpoint. Five original major AI seats and initial map,
leaders, starts and units match. The baseline uses older CSC content and CE;
notably, the current Quarters consume population-limited district slots.
These are descriptive historical results, not an isolated tuning-only experiment.
No new baseline game was launched for this comparison.

| Turn 200, completed Quarters held | Historical untuned baseline | Latest guidance |
|---|---:|---:|
| Quarters |30 (16 Bakers / 14 Tailors) |9 (6 Bakers / 3 Tailors) |
| With Base materials |6 / 30 (20%) |8 / 9 (89%) |
| Without Base materials |24 |1 |
| With compatible unpillaged Base improvement |3 |5 |
| With Base and Specialty |0 |2 |
| Both classes improved |0 |1 |
| River sites |2 |6 |
| Adjacent mapped customer district, any stage |10 |7 |
| Current adjacency at least +3 |not recorded |7 / 9 |
| Current adjacency at least +4 |not recorded |2 / 9 |
| Working Stage 2 producer |14 |5 |
| Adjacent Stage 2 customer district |5 |5 |
| Working adjacent Stage 2 customer building |1 |2 |
| Working physical / active-property Bakers Stage 2 chain |1 |1 |
| Working physical / active-property Tailors Stage 2 chain |0 |0 |
| Native Storekeeper chain-turns, turns 2–199 |39 |84 |

The latest run is much more selective and develops more useful material-supported
sites despite far fewer Quarters. It does **not** show stronger complete Stage 2
coverage at the 200 endpoint. There are two Bakers chains with recorded operation
before 200, but one is down at the census. The 84 chain-turns are 66 from player 1
(turns 134–199) and 18 from player 3 (147–164); baseline activity is one chain on
161–199. The recorded baseline has no comparable numeric adjacency census, so
no baseline +3 or +4 percentage is inferred from material counts.

| Turn 200 economy, totals for five original AI seats | Historical baseline | Latest guidance | Change |
|---|---:|---:|---:|
| Production/turn |946.75 |989.27 |+4.5% |
| Net Gold/turn |310.09 |239.36 |−22.8% |
| Food surplus/turn |226 |223 |−1.3% |
| Cities |37 |40 |+8.1% |
| Population |372 |423 |+13.7% |

Per original AI, this is Production 189.35 → 197.85, net Gold 62.02 → 47.87,
and Food surplus 45.2 → 44.6. More cities/population do not establish better
per-city productivity: Production/city is 25.59 → 24.73 (−3.3%). The economic
result remains mixed, and changed content, war and expansion prevent assigning
these differences solely to our placement intervention.

Sources: [baseline definitions and original matched v2 setup](csc-ai-integrated-stage-two-20261108.md),
[historical detailed 200 census and totals](csc-ai-harmonised-250-20261112.md).
Raw baseline: `csc-ai-integrated-20261108/endpoint-detail-baseline/continents.json`;
aggregates: `csc-ai-harmonised-250-20261112/comparison.json`, window `baseline200`;
latest: `fresh250-audit.json`, window `current200`. Storekeeper totals are clipped
to the same 2–199 observation window. The baseline's paired v2 comparison was
same-content at the time; this later candidate is not that original v2 package.

## Delivery and performance

| Recorded measurement | Result |
|---|---:|
| Publications |250 |
| Largest district packet / capacity |184 / 4096 |
| Packet omissions / capacity trims |0 / 0 |
| New-site Quarter Best results |57 (36B/21T) |
| Positive bids matching exact prior write and actual result |57 / 57 |
| Distinct compared site identities |19 |
| Distinct nominated city/type pairs |15 |
| Retained request-value reductions |4 |
| Managed matrix writes across refreshes |132688 |
| Writes with a nonempty reservation ID |68057 |
| Policy/economic/observer faults |0 |
| Temporarily unavailable site quotes |2 |
| Matrix refresh median/max per actual-work round |13.54 / 29.36 ms |
| Coarse Lua publication time, all 250 refreshes |46 s (previous 69 s) |
| Largest coarse Lua refresh |1 s (previous 1 s) |

Repeated comparisons/writes are not distinct investments. Fifteen nominated
city/type pairs lead to seven foundations; eight remain unbuilt by turn 250. Nineteen
site identities include alternatives/replanning, so 7 / 19 is not a construction
success rate. The logs now let us investigate those remaining 1.5 / 1.6 gates rather
than guessing whether the values landed. Player 4 has no Quarter foundation.

The two unavailable quotes are confined to player 4 / city 196610 on turn 174; adjacent
publications are available. Their sites safely defer instead of reviving the
native building premium. There is no player-wide economic fallback. Native
Best records on existing footprints are outside the 57 new-site count; they keep
Civ's construction/repair values, which this revision does not recalibrate.

Timing is bounded evidence, not a full CPU profile: matrix microseconds exclude
Lua, masks, tracked setters and unrelated engine work. There are 249 receipt
samples, one with no work; 248 actual-work samples have median 13.5405 ms and
maximum 29.357 ms. The Lua timer is coarse. This supports an affordable measured
implementation for this two-Quarter game, not a guarantee for all eight families
or much larger empires.

## Services, damage and remaining gaps

Two **AI-founded** Bakers chains deliver native Storekeeper effects:

- Player 1, city 393221, Quarter 1310738 (plot 1356): 116 active turns, 134–249.
- Player 3, city 131073, Quarter 196610 (plot 1243): 37 active turns, 147–164 and 231–249.

These total 153 **chain-turns**, not 153 different game turns. The second chain
has a 66-turn lapse, 165–230. Its Mill is pillaged in censuses 175 / 200 / 225, and its
Quarter is also pillaged at turn 200; operation later resumes. This is observed recovery
in ordinary play, not proof that our repair bid caused it or that the delay is
acceptable. All 248 requested per-turn effect samples 2–249 are present, with no
ambiguous source attribution. District IDs alone are not global identities:
player 3's 196610 is not the city-state district with the same numeric ID.

At turn 250 there are two active Bakers Stage 2 properties and no Tailors Stage 2 chain.
Both families have one Stage 3 active property. Tailors' inland placements can
serve later-stage customers, but **Dockmaster/Harbor completion is still open**.
Material development and building repair/construction remain weak: only 5 / 8
material-supported held Quarters have a working Base improvement, and producer
or customer damage still interrupts chains. Good sites do not finish those jobs.

## Empire output: mixed, not a balance verdict

Same five original AI seats, including zero for an eliminated seat (all survive).
Food is surplus, not a complete growth-rate/amenity/housing measure.

| Turn / total output | Previous | New | Change |
|---|---:|---:|---:|
|200 Production |1000.90 |989.27 |-1.2% |
|200 net Gold/turn |391.05 |239.36 |-38.8% |
|200 Food surplus |274.00 |223.00 |-18.6% |
|250 Production |1505.20 |1415.93 |-5.9% |
|250 net Gold/turn |340.21 |643.91 |+89.3% |
|250 Food surplus |245.00 |264.84 |+8.1% |
|250 cities / population |45 / 532 |48 / 526 |different expansion |

At turn 250 the averages per original AI are Production 283.19, net Gold 128.78 and Food
surplus 52.97 (previous 301.04 / 68.04 / 49.00). Gold's reversal between 200 and 250 is
why a single positive endpoint should not be sold as general economic superiority
or evidence that CSC itself is overpowered. This is one assistance comparison;
a fresh same-content tuned/untuned baseline and more seeds remain separate work.

## Evidence and completion

Root: `Desktop/Codex/csc-ai-placement-coverage-20261113/`.
Run: `fresh250-01/`; audit: `fresh250-audit.json`; exact source/pins:
`candidate-packages03.json`, packages.json, source.json and loaded-modules.json.
Placement-watch.json contains every lifecycle/native record; all ten censuses
25–250 reconstruct from raw `Lua.log`. Saves at 50 / 100 / 150 / 200 / 250 have native completion
acknowledgements and matching native/archive hashes. Endpoint SHA256:
`daaa67639b3a693bdd2ae08a6101e231c787ee12087037abef75766069ba091a`.

Astra independently reproduces the 57 comparisons, material/provenance counts,
153 chain-turns, economic totals, timing and source parity. Final native exit 0,
preferences restored, package callback completed and owners absent are verified.
The test session exited cleanly; no test worker remains. Main policy/CE source and reusable findings
are committed/pushed; no upstream PR is made. No AI Quartz build is required.

Next within placement scope: investigate the eight nominated-but-unbuilt
city/type pairs under 1.5 / 1.6, including acquisition, capacity and native request
follow-through. Do not raise every bid to force more construction. The larger
Stage 2 milestone, Builder development and Tailors customer completion remain
open; this trial closes a concrete delivery gap and demonstrates better placement
selectivity at a scoped, reproducible source/seed.

## Retrospective follow-through audit: no new game required

The eight unbuilt nominations can be investigated from this run's archived native
logs. A positive published offer, a native Best district result, a construction
request and an actual queue selection are distinct. In particular, the 15-pair
count above is the set returned by the observed native district selector, not
an inventory of every positive site offer CSC ever published.

The offline join uses player, city ID and district type from the native Best
record. It maps the city to the unique native tree Decode Trigger with the same
player, preceding native turn and truncated utility value. All 45 Best records
across the eight unbuilt pairs have a unique matching city name. The one-turn
offset is the observer's next-publication drain, not a different decision clock.
Searching the complete AI_CityBuild log by player, city name and Quarter type
then finds only two submitted construction requests:

| Original AI / city | Quarter | Observed native nomination turns | Construction request recorded |
|---|---|---:|---|
| 1 / Constantinople |Tailors |86-127 |2338, turn 127 |
| 1 / Antioch (Byzantium) |Bakers |62-143 |None |
| 4 / Canberra |Bakers |97-110 |None |
| 4 / Canberra |Tailors |178-180 |None |
| 4 / Sydney |Bakers |136-176 |None |
| 4 / Hobart |Bakers |56 |None |
| 4 / Geelong |Tailors |129-135 |2544, turn 135 |
| 5 / Charleston |Bakers |122-130 |None |

This means six cases lack a submitted Quarter construction request in the
archived log. Their district trees repeatedly report Build Unit / Not Building;
that text alone does not identify the failed native eligibility or request gate.
It is not evidence of a Quarter losing a final production-score comparison.
No absence claim is extended beyond this log or the original player identity.

**Constantinople provides evidence consistent with competing production.**
Contract 2338 is submitted on 127 at logged utility 1765. Its decorator records
waiting 1 through 15 on 128-142; on 143 it fails with no contract, and on 144 the
tree nominates an Industrial Zone. The production history finishes Bank on 131,
selects Military Academy on 131 and Big Ben on 136, with no Tailors foundation.
The separate queue log confirms Bank, Military Academy and Big Ben receive
production during the waiting window. There is also a managed request reprice
in packet 131 (observed 132), reducing its 451840 Q8 retained value to 316035 Q8.
This establishes waiting/other construction and a lowered bid, not the exact
Quarter-versus-Military-Academy/Big-Ben comparison or a causal rejection reason.

**Geelong does not remain an Australian planning case.** Contract 2544 is
submitted on 135 at utility 96, and waits one turn on 136. Native city-build
records put Geelong under player 62 on 137 and player 2 on 146. The recorded
ownership change interrupts attribution to player 4; do not classify its failure
to build as merely a lost production auction. The means of ownership change
are not established by these excerpts. Quarter foundation remains absent.

The archives therefore support useful retrospective classification immediately.
Exact numerical competitors and gate reasons were not logged at every native
queue decision. If those become necessary, use a targeted replay from a saved
checkpoint with additional read-only decision tracing; a fresh 250-turn game
is not the first requirement. A replay would be a new diagnostic observation,
not proof that every unrecorded original decision repeats identically.

Evidence: `fresh250-01/placement-watch.json`, `AI_Behavior_Trees.csv`,
`AI_CityBuild.csv` (request rows 4258 and 4712), and `City_BuildQueue.csv`.
Preserved SHA256s, respectively for the three native CSVs:

- AI_Behavior_Trees: `348abc3e8618cfe1e1da786346d39903886360a5f06ce63b140525062c2729b6`.
- AI_CityBuild: `deaca2f937c2df95cf2e4713ff400e61b7815e0372e0dfe28e76eeb00fbc1136`.
- City_BuildQueue: `62604042ad3544abcdccf6b3309591e9b56bada3ffd0a43c0eebdaa086feadf4`.
