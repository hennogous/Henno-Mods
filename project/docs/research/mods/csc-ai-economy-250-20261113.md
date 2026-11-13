# Central-economy outcome test: 250 turns

The requested fresh Online-speed game **completed turn 250**, saved, exited with
code 0 and restored the original mod preferences. The implementation remained
active without reported policy faults or fallback. **This is not yet a placement
quality success:** most Quarters still have low adjacency, and only one Bakers
Stage 2 chain delivers a sustained measured Service.

The [architecture guide](../../civ6-ai/architecture.md) explains the implementation;
the [preceding qualification](csc-ai-central-economy-20261113.md) records its native
transport and unit tests. This experiment measures normal play using that code.

## Setup and integrity

- Normal Small Continents, Prince, Online speed; map/game seeds
  **18461107 / 29461107**. Original assisted major players **1–5**; original
  human player 0 runs under ordinary autoplay, outside the per-turn Lua/CE
  scoring cohort. Static SQL adjacency and Builder settings apply globally,
  including player 0 and city-states; they are not wholly untuned controls.
- Main CSC policy only, with its qualified CE dependency. No RHAI5, external AI
  policy, separate test/probe policy, Frida, forced unlocks or diagnostic world
  edits. Normal CSC gameplay and map behaviour remain part of the package.
- Complete qualified snapshot: **639 CSC files + 6 CE files**, including the
  central model and all ten placement/problem paths. All eight AI/UI source
  hashes match the main working source and the final qualified smoke.
- CE code `6f53037`, documentation `3421b37`; DLL SHA256
  `09d51ddd0c471959b8f0ebece33b30bf0758201b79928696610cd82597bdcdc9`.
  Upstream `develop` remains `2986a746b396eb93aad14f9afffb043a09c2c489` at preflight.
  No upstream PR was created.
- Shared controller, bounded five-turn windows, passive observations, agent
  checks about every 15 minutes. The user's diagnostic question prompted an
  additional read-only log check at turn 125. No second console client was used.
- All ten censuses, turns **25–250**, reconstruct exactly from the raw log.
  Saves at **50, 100, 150, 200 and 250** have native completion acknowledgements,
  unchanged inactive phases and matching native/archive hashes. All five
  original AI players survive to 250.

Artifact root:
`C:/Users/Shadow/Desktop/Codex/csc-ai-economy-250-20261113/`.
Run: `run-continents/`; inputs: `frozen/`; derived records: `audit.json`,
`comparison.json`, `quarter-origins.json`, `placement-origin-quality.json` and
`auxiliary-policy-audit.json`. The driver retires its temporary mod copies into
the run directory. Original installed CSC content remains unchanged.

The endpoint save SHA256 is
`7d0ef4515a379289cf1105d861e578336658b85a81b9c53cac289c8551ba8a8c`.
No game, FireTuner or test worker remains active.

## Did the code run and reach native decisions?

Yes at the transport level. The distinction from successful winning-placement
control is important:

| Recorded measurement | Result |
|---|---:|
| Publications / player plans |250 /1,250 |
| Plans containing complete economic values |1,225 |
| Complete entries across refreshes |82,391 |
| Largest district packet / capacity |707 /4,096 |
| District, decline, exclusion and ownership omissions |0 |
| Unknown quotes / unavailable economy / economic faults / capacity fallbacks |0 |
| Economic readiness checks, including initial preflight |11, all ready |
| Bounded exact economic receipts |3,968 |
| Receipt rows showing at least one write |1,536 |
| Receipt rows showing cache reads |3,968 |
| Receipt rows showing eligible city comparisons |394 |
| Sampled site-win receipt rows |5 |
| Aggregate previous-packet matched / changed score calls |67,929 /66,097 |
| Positive frontier offers suppressed by the buyer screen, across refreshes |858 |
| Largest coarse logged publication duration |1 second |

Offers and counters repeat across turns; these are not distinct sites or
investments. Aggregate score calls can include retained non-final guidance.
Exact receipt logging is capped at 16 identities per refresh and is biased
towards early identities. Readiness does not prove every optional operation was
exercised. The older `placement_bids` counter measures early positive deltas,
so its zeros do **not** mean the complete economic path was inactive.

There are no logged economic, placement or observer failure markers. The coarse
timer totals 69 seconds over 250 publications; it is not a precise CPU profile
or a causal overhead estimate. At the largest packet, this ordinary game's
recurring work remains comfortably below the packet limit.

### Important winning-comparison gap

All five sampled site-win receipts have **`scoreAttempts=0, writes=0` in that
packet version**, despite `cacheReads=1`, `cacheEligible=1`, `citySelections=1`
and `siteWins=1`:

| Published version | Player / city | District / plot | Published whole bid, Q8 |
|---:|---|---|---:|
|72 |4 /131073 |Bakers /1423 |18,306 |
|148 |1 /65536 |Bakers /987 |55,621 |
|166 |1 /327684 |Tailors /1062 |38,258 |
|180 |2 /65536 |Bakers /2530 |109,921 |
|228 |1 /720905 |Tailors /396 |3,937 |

This does **not** prove the engine bypassed the intervention. A cached value,
retained plan, reservation or a different calculation path may explain it.
Some selected sites have earlier changed-value samples, but those samples do
not prove which value the eventual selector consumed. Nor does a current
positive published offer prove it caused that selection.

The diagnostics therefore establish ongoing publication and native delivery,
and expose a concrete missing link: **the last value write, guard state, actual
winning operand and resulting request need to be joined for a weak placement**.
Do not assume 82,391 offers means 82,391 effective corrections at winning
decisions. Do not increase penalties before resolving this timing/coverage
question on a representative weak-site request.

## Quarter quality at the endpoint

These are current recorded adjacency bonuses, **Production + Gold**, using the
actual loaded rules. They are not the published score or a claim about exact
placement-time conditions. Population, neighbours, improvements and damage can
change after foundation.

| Completed Quarters at 250 | Bakers | Tailors | Total |
|---|---:|---:|---:|
|Complete |14 |12 |26 |
|Current adjacency at least +3 |6 |2 |8 |
|Current adjacency at least +4 |3 |1 |4 |
|Below +3 |8 |10 |18 |
|Adjacent usable Base |12 |11 |23 |
|Adjacent usable Base and Specialty |3 |2 |5 |
|Working compatible Base improvement |8 |10 |18 |
|Both material classes working |0 |2 |2 |
|River adjacency |3 |4 |7 |
|Working Stage 2 producer |10 |10 |20 |
|Adjacent Stage 2 customer district |5 |1 |6 |
|Working Stage 2 customer building |1 |0 |1 |
|Physical / active-property Stage 2 chain |1 |0 |1 |

Current adjacency distribution: **nine +1, nine +2, four +3, two +4 and two +5**.
Thus 18/26 (69%) remain below +3. Counting prospective local Mill geometry
separately raises the potential +3 count to 11 and +4 to 5; it assumes no future
customer district and does not prove those Mills will be built or repaired.

### Who originally built these Quarters?

Do not attribute every current holding to assisted placement. Matching completed
native district contracts to a unique same-city/type reservation footprint
before execution identifies:

- **21** current Quarters built by the major actors receiving guidance.
- **4** inherited from city-states outside the Lua/CE scoring cohort: the Bakers and Tailors Quarters
  at Bologna and Samarkand.
- **1** unresolved by this conservative contract/footprint match.

This is origin attribution, not proof that CSC drove a particular choice. Among
the 21 traced major-built Quarters, only **6 currently reach +3** and **2 reach
+4**. Captured holdings do not explain away the low-quality result. These are
endpoint classifications; detailed construction-time input/score attribution
remains open.

## Producer, customer and Service follow-through

The endpoint has 20 working Stage 2 producers but only one working Stage 2
customer building connected to a Quarter. There are five adjacent City Centers
for Bakers, three still lacking a Granary and one of the two built Granaries
not working. Tailors has one adjacent Harbor and no Lighthouse there.

There are later ordinary exchanges worth recording: Tailors has five working
Stage 3 producers and five working Stage 4 producers; two Quarters have working
Stage 3 customer links and four have working Stage 4 links. None has an active
Stage 3/4 Service property at the endpoint. This does not establish which unlock,
material threshold or other requirement is missing.

Actual native Storekeeper evidence covers **every turn 2–249**, with no gaps or
ambiguous attribution. One chain, player4/city131073/Quarter1423 (Melbourne), is
active **138–249: 112 chain-turns**. There is no measured interruption in that
range. Endpoint native source properties also identify one active Bakers chain;
Tailors has no active Dockmaster chain. Persistent hidden Service buildings are
not counted as active Services on their own.

## Historical comparisons

Initial original seats, terrain/resource signature, leaders/starts and units
match the preceding same-seed runs. **Content and CE changed, and Quarters now
consume population-limited slots.** These are descriptive historical comparisons,
not isolated causal estimates of this AI revision or mod balance.

| Comparable turn 200 | Stock baseline | Earlier conservative tuning | New economy |
|---|---:|---:|---:|
|Completed Quarters |30 |32 |18 |
|With usable Base |6 |26 |16 |
|With both materials |0 |3 |3 |
|Working Base |3 |18 |14 |
|Working Stage 2 chain/property |1 |4 |1 |
|Current adjacency at least +3 |not available |13 |5 |
|Current adjacency at least +4 |not available |5 |2 |
|Cities |37 |42 |35 |
|Total Production/turn |946.75 |1,356.03 |1,000.90 |
|Net Gold/turn |310.09 |573.45 |391.05 |
|Food surplus/turn |226 |251 |274 |

| Turn 250 | Previous harmonised run | New economy |
|---|---:|---:|
|Completed Quarters |36 |26 |
|Current adjacency at least +3 |11 |8 |
|Current adjacency at least +4 |3 |4 |
|With usable Base |30 |23 |
|With both materials |5 |5 |
|Working Stage 2 chain/property |8 |1 |
|Measured Storekeeper chain-turns, 2–249 |685 |112 |
|Cities / population |43 /489 |45 /532 |
|Total Production/turn |1,461.94 |1,505.20 |
|Gross Gold/turn |1,744.84 |1,348.21 |
|Net Gold/turn |807.84 |340.21 |
|Food surplus/turn |282 |245 |

New per-original-AI averages at 250: **301.04 Production, 68.04 net Gold and
49 Food surplus** per turn; 9 cities and 106.4 population. Fewer Quarters is
observable, but the +3 share is almost unchanged from the previous 250-turn
sample, and Service development is weaker. The lower Quarter count cannot be
assigned to the new economic bids separately from the corrected district-slot
rule and other content changes.

## What this closes, and the next question

The requested run, source/deployment audit, observation coverage, saves and
cleanup are complete. It validates continued execution of the new architecture
through an ordinary long game. It does **not** close broad poor-placement
suppression or the Stage 2 chain milestone.

The next focused question is under **1.6/1.8**: for one observed weak Quarter,
what exact score and row state did its winning comparison consume, and where
was the last complete CSC write? Include cache age, reservations and request
lineage before changing values. Then distinguish initial poor selection from
later material/customer changes under **2.2**. Producer/customer completion
remains a separate bottleneck under the later numbered problems.

No additional game, replay, tuning change or upstream PR was launched as part of
this result. The older automatic goal remains paused.
