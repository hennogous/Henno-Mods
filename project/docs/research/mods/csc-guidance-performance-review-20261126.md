# Where CSC AI spends its turn

## Benchmark

Large Continents, Standard speed, Prince, map seed 171124611 and game seed 171124612. Both arms loaded CSC, City Lights and Dev CE with the same ten major starts. Nine seats began as AI. The control disabled the CSC Lua publisher and the private-yield AI SQL action. The treatment used their ordinary defaults. Henno shortened the comparison to turn 350 while the treatment was running. The completed control supplies the same first 350 turns.

**Matched turns averaged 12.18 seconds with guidance off and 20.05 with it on, a 7.86-second increase (+65%).** The medians were 10.06 and 15.50 seconds. The respective maxima were 46.81 seconds on turn 332 and 78.67 on turn 339. There were 273 shared turn-start intervals after screening popup intervals and five-turn controller handoffs in either game.

| Turn band | Matched intervals | Off, s/turn | On, s/turn | Direct publisher inside matched intervals, s/turn | Logical joint evaluations per game turn | Chains per successful Quarter forecast |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1–50 | 39 | 3.59 | 4.06 | 0.36 | 1,807 | 1.31 |
| 51–100 | 40 | 5.06 | 6.74 | 1.03 | 3,063 | 2.39 |
| 101–150 | 40 | 8.93 | 11.60 | 3.12 | 6,028 | 3.18 |
| 151–200 | 40 | 11.25 | 16.39 | 4.64 | 6,724 | 4.12 |
| 201–250 | 39 | 14.28 | 22.92 | 6.96 | 6,753 | 5.60 |
| 251–300 | 38 | 18.24 | 35.58 | 9.96 | 5,590 | 7.37 |
| 301–350 | 37 | 25.05 | 45.38 | 11.15 | 4,184 | 8.10 |

The publisher accounted for 5.23 seconds of the 7.86-second average gap on the matched intervals. Across all 350 turns its own monotonic timer averaged 5.33 seconds and peaked at 18.26 on turn 301. Of its 1,866 seconds, **98.9% fell inside the player passes**. Seats 6 and 1 accounted for 918 seconds between them. The existing coarse Lua clock recorded 1,786 positive seconds within the placement pass (`QuarterBids`, including customer and connection planning), against 1,851 elapsed clock seconds across the player passes. This clock ticked in whole seconds on this host. It locates the expensive subsystem in aggregate and cannot assign precise times to its inner functions.

The measured native managed-district refresh averaged 22 ms and peaked at 41 ms over 349 reported packets. Other native hooks, the SQL guidance, and changes in what the players built remain in the whole-turn comparison. By turn 350 the treatment had eight surviving original AI players, 84 cities and 951 population, against nine players, 81 cities and 842 population in the control. The 2.63-second average gap outside the matched publisher span has several possible contributors.

## Which work pays for itself?

| Work observed over 350 turns | Interpretation |
| --- | --- |
| 481,529 Quarter site examinations, 54,116 joint world pricing calls and 1,707,441 logical trial evaluations | These count different steps across repeated publications. Trial counts include reuse. Forecasts got slower late even as the number of trials fell. |
| Of 6,840 consecutive city/Quarter rankings with a published proposal candidate in both turns, 6,502 kept the same leader and 6,701 kept today's leader in yesterday's top two | A two-site shortlist would have contained 98.0% of those leaders. The other 139 changes and newly eligible groups justify a discovery pass. This measures proposal rankings before packet trimming. |
| Of 23,453 same-site Quarter economic quotes repeated on consecutive turns, only 4,181 had the same economic bid component | Reuse promising **locations**, then update their economics. Reusing yesterday's numeric bid wholesale would often keep a stale value. |
| 8,767 of 24,849 successful Quarter economic forecasts had a nonzero marginal Service value | Dropping Service pricing globally would change an input on 35% of these quotes. Preserve it in the affected economy. |
| 359,992 city/type customer maps constructed and 358,674 adjacency reads | The static city ring can be shared. Within-publication legal-target sharing and a cheap first pass offer a way to narrow repeated work. An earlier standalone adjacency-footprint cache saved no time on its same-save test. |
| 909,088 selection-journal records read in 14,386 pages yielded 183 confirmations. Separately, 18,829 staged exact district receipts implied 52.6 million native trace-record visits | Plan continuity needs those confirmations. Ordinary play gains little from repeatedly transferring all other records. |
| 367,946 staged district entries, up to 1,541 in one packet, implied 231 million duplicate-key comparisons. The tagged log contained 309,197 lines, including 101,161 rival-footprint cost lines (16.0 MB) | Compact telemetry and indexed lookups are useful housekeeping. Receipts before the player loop, staging afterward and all other work outside the player spans **together** took only about 20 seconds of publisher time in this run. In-loop logs and native hooks during ordinary Civ decisions are outside that bound. |

### Offline test of unrelated chains

The production Lua priced the same new Quarter with one variable investment. Each additional incumbent had its own city and working Market. Their queues, payouts and customers were independent of the proposed Quarter. The test held the price function and candidate facts fixed, warmed each case, then took the median of seven batches of 25 calculations.

| Unrelated incumbent chains | Logical evaluations | Calls to the fixture price function | Marginal bid, Q8 | Milliseconds per forecast |
| ---: | ---: | ---: | ---: | ---: |
| 1 | 10 | 16 | 27,648 | 0.257 |
| 4 | 10 | 52 | 27,648 | 0.658 |
| 8 | 10 | 100 | 27,648 | 1.134 |
| 16 | 10 | 196 | 27,648 | 2.207 |

The exact same bid took 8.6 times as long at 16 incumbents as at one. Lua 5.1 and the fixture price function isolate the economic algorithm from Civ. This measures the scaling mechanism. The savings attainable on a live map depend on how often real chains can be separated.

## What to change first

### 1. Reprice the affected economy

A site competes for the value it adds to the player's empire. The current implementation takes an entire economic snapshot, freezes unrelated producer choices, and then schedules and prices **every** chain for each trial. Even a remote Quarter whose plan is fixed contributes another ledger on each cache miss. Queue sharing, transactions that round together, trader income, pooled amenities and Service housing justify a shared calculation for some candidates. Rebuilding the inputs of physically independent chains is the expensive part worth eliminating.

Start inside one player's publication. Prepare the unchanged contributions once, then rebuild the part a candidate can affect. The affected set has to include shared city queues and buildings, both endpoints of relevant trades, and contributors to pooled payouts or thresholds. Reuse immutable inputs to the final pooling step when the pool spans cities. Fall back to full pricing when independence cannot be established. Compare complete bids and selected layouts against the current Lua on the same facts before widening reuse across turns.

This targets `JointForecast` and its local ledger builder, reached through `WorldQuote`, `QuarterForecast` and the customer economic comparisons. The before-world, native yield quotes and up to 16 trial states already have caches. Earlier same-save profiling put **77% of measured ledger-build-plus-price time in construction**. A larger trial-state cache and skipping repeated search sweeps had much less to offer. [Prior profiles and full-game results](../../civ6-ai/performance.md)

There is also a straightforward memory-lifetime improvement. `QuarterWorld` clears its candidate's cache entry immediately before constructing it, then `investmentWorld` stores it again. `QuarterForecast` makes an objective specific to that one site, and `WorldQuote` retains its complete result under that private world identity until the player pass ends. Later proposals construct a new identity. Let these one-use candidate worlds and full ledgers go once the adapter has extracted the bid, streams and layout facts. Keep the shared baseline and reusable customer comparisons cached. The gain to check offline is lower peak retained Lua memory and garbage collection during a mature player pass.

### 2. Keep the native bid fresh while doing less speculative work

The mature planner scans every eligible city for each missing Quarter type every turn. For promising sites it finds partners, prices a whole economic world and later sorts the resulting bids. The existing prospective-connection budget takes three leading city plans and rotates a fourth **after** their Quarter sites have been priced. The customer economic comparison has its own 16-forecast budget. Neither limits the earlier Quarter forecast pass.

Keep the per-turn publication. Separate cheap discovery of new or changed sites from deep pricing. Always include confirmed plans, paid or newly affordable footprints, both sides of a recent foundation, a newly unlocked customer, and sites whose supplier or enemy occupation changed. Give other serious contenders a deterministic rotating slot and periodically revisit the full field.

Yesterday's shortlist is a scheduling hint. Reprice its leaders against current construction times, native strategy weights, trade and purchase costs. Population growth can open a slot during the player's turn. Preserve the existing native admission and material-protection rules. A trial should report worthwhile sites missed by screening, especially on the first turn a layout becomes possible and for less common Quarter types. Using this shortlist changes policy and needs a separate comparison after the exact optimizations.

### 3. Remove overlapping work on the managed placement path

- **The older Quarter scan.** `CSC_AI_QuarterSiteForecasts` walks legal owned and frontier sites, builds a completed-district inventory per profile, and searches for a best Quarter. On a successful managed pass, `QuarterBids` replaces the early Quarter rows with its own complete scores. The old numeric deductions are retained as diagnostic context. The fallback still matters when the economic pass fails, and non-Quarter entries and supplier protection have consumers. Split the cheap shared facts and live protection from the fallback-only scoring. Exercise success, missing capability and failed-quote paths before retiring any work.
- **Duplicate customer legality reads.** `Snapshot` wraps `GetLegalDistrictTargets` in a player/turn cache. `CustomerCandidateSets` uses that wrapper. `CustomerFirstOptions` closes over the original UI object and queries it directly. A miss runs the native BUILD-target query and checks each returned tile individually. Route both through the same keyed reader while preserving the handling of unavailable and empty results. Share the radius-three plot indices per city across Quarter types and customer map scans. Refresh ownership, visibility, resources, blockers and build eligibility from the current world.
- **Footprint protection with the pinned CE.** `ApplyConnectionCosts` tries rival district types at each scarce tile. This benchmark DLL lacks `CE_AIDistrictScoresEarlyCost`. Its compatibility path asks for the district's native site value before publishing a deduction. The native quote calls both NetValue and intrinsic Value. There is already a player/publication cache. Narrow the city/type iteration and reuse equivalent inputs first. The newer CE consumer can apply the guard when the game prices the rival. Qualify that delivery path separately because its decision timing differs.

### 4. Reduce the cost of observing and delivering decisions

- **Selection journal.** `ObserveNativeChoices` requests 64-record JSON pages from Dev CE, then retains exact current-version `best` selections matching offered Quarters. Confirmations drive plan continuity. Add an exact, generation-checked selected-Quarter reader or equivalent native filter. Keep the existing journal available for investigations. Compare confirmed plan identities and save/reload behaviour.
- **Receipts and ordinary logs.** `reportReceipts` separately queries samples of Quarter, frontier, customer and connection offers. Each exact district receipt for a staged row walks the whole native trace. Many high-volume records, including each rival's footprint loss from `ApplyConnectionCosts`, are printed on every publication. Keep publisher timing, faults, concise counts and changes of plan in the ordinary log. Make detailed repeated-site text and sampled diagnostic receipts opt-in. Gate the work **before** querying, sorting or formatting. Preserve the selected-Quarter reader above.
- **Native lookup and staging.** The benchmark CE scans previous entries for duplicates on each insert into a new packet. `find_pair` and `find_city` also search the whole packet, and the cache observation path scans for entries matching a city and plot. Build exact-key and city-range indexes once per immutable packet, preserving duplicate rejection, generation boundaries, row guards and trace order. Existing Builder and Wonder lookup code provides an indexed precedent. The native managed-cell timer covers only its own refresh. It cannot price the wider lookup path or explain the full turn-time gap.

### What to keep

Material protection, immediate pillage and repair readiness, Builder job nominations, production/research bids, and the change from planned to founded layouts need a fresh decision packet. Builder routing already has a 12-path-query bound per player pass. Wonder offers are gated by mapped customers and both supplier classes. Native private-yield adjacency runs through the game's district system. The current measurements give no strong case for weakening these features. The same applies to Service valuation as a whole. Earlier runs found more supplied pairs and working buyers with the layout planner enabled. [Layout outcomes](city-lights-ai-placement-20261116.md#final-calibrated-turn-250-qualification)

## Verification order

1. Compare exact bids, recipients, confirmed plans and protection entries on identical inputs after sharing reads, indexing packets and reducing diagnostic work. Include retirement of lost or occupied targets and the fallback on an unavailable economic quote.
2. Compare incremental and full economic pricing on independent and shared city queues, a Market shared by two Quarters, rounded payouts, changed routes, housing/amenity thresholds, purchases and pillage. Keep deterministic traversal, a cold path after load, and a memory bound per player.
3. Evaluate any approximate shortlist separately. Score it on turns to a good founded Quarter/customer pair, retention of Base and Spec, completed Services, and missed alternatives. Carry forward the turn-350 control and compare the final 50 turns as well as the whole mean. A mature-turn speedup that discards rare Tailors layouts would miss the purpose of the optimization.

## Sources and reproduction

The [economic model](../../../../Civ%20Supply%20Chains/Lua_UI/AI/CSC_AI_EconomyModel.lua), [facts reader](../../../../Civ%20Supply%20Chains/Lua_UI/AI/CSC_AI_EconomyFacts.lua), [decision adapters](../../../../Civ%20Supply%20Chains/Lua_UI/AI/CSC_AI_EconomyAdapters.lua) and [publisher](../../../../Civ%20Supply%20Chains/Lua_UI/AI/CSC_AI_BakersGameplay.lua) implement the paths above. The eight guidance Lua modules match the benchmark package as source text. The proxy loaded in both games had SHA-256 `120fbea9c2ebc0a660999c20cb1e37dcf085ab5ac0b5687154ebd8f85230e9ac`. The project's build record associates it with Dev CE `6244570`. [Dev CE setup](../../civ6-ai/topics/native/workshop-delivery.md#shadow-cutover-on-22-november-2026)

On Shadow, pass `Desktop/Codex/csc-cl-large-standard-guidance-t500-20261126` to the [offline workload reader](../../../tools/native_ai/late_placement/guidance_workload_review.py). It uses the shared clean intervals in `comparison.json`, the original on-arm log, and the recorded order of publisher and turn-clock events. The physical-economy snapshots are `off-retry-1/full-census-350.json` and `on/full-census-350.json`. The [independent-chain fixture](../../../tools/ai_economy/benchmark_independent_chains.py) runs against the production Lua with the same Lua 5.1 dependency as the economic tests.
