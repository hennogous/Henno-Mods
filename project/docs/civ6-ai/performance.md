# AI guidance processing time

The [Large Standard turn-350 performance review](../research/mods/csc-guidance-performance-review-20261126.md) compares guidance on and off with City Lights. It traces mature-turn growth to the district-planning pass and ranks changes to economic forecasting, site discovery and Dev CE delivery.

### Actually skipping Quarter forecasts, 27 November

The experimental candidate refreshes every eligible Quarter site after a city has no positive bid for that Quarter. It also reprices the previous leading Quarter site's proposed customer footprints as possible Quarter sites. It retains the prior top two, changed or new sites, confirmed plans, a rotating spare and the eight-turn refresh. A skip occurs immediately before the expensive economic forecast. The ordinary full planner remains the default.

Both arms loaded the same turn-one Small Continents save (Online, Prince, CSC + City Lights, seed 171124605). The full planner reached turn 250. The candidate's observer civilization was eliminated during turns 225–230. Turn 225 is the last shared physical census. The complete comparison covers 224 publications per arm and 176 matched whole-turn intervals, with popup and controller-handoff intervals excluded. On an earlier seed, 27112601, the full planner lost its observer after turn 195; that run contributes no timing or placement figures below.

| Through turn 225 | Full planner | Selective planner |
| --- | ---: | ---: |
| Deep Quarter forecasts executed | 7,810 | 7,125 |
| Whole turn, mean / maximum | 9.46 / 26.99 s | 9.56 / 27.36 s |
| CSC guidance, mean / maximum | 1.800 / 3.572 s | 1.777 / 3.617 s |
| Whole turn, mean in turns 201–225 | 16.41 s | 17.07 s |
| AI-founded Bakers / Tailors | 21 / 6 | 21 / 6 |
| Founded with Base / with both Base and Spec | 27 / 7 | 27 / 7 |
| Founded with at least +2 current Production and Gold | 26 | 26 |
| Founded with at least +4 including potential local Mill | 7 | 8 |
| Completed Quarters with Base and a completed mapped customer | 24 | 23 |

The candidate skipped 978 of its own 8,103 eligible forecasts (12.1%). Its game generated 293 more forecast opportunities as play diverged. Across the arms, CSC spent 0.023 seconds less per turn on guidance, and whole turns averaged 0.098 seconds longer. Estimating each site's eligibility and detecting changes still incurs work before the cutoff, as do all customer and other planning decisions.

The original AI players founded 26 of their 27 Quarters on identical plots, including every Tailors location. The full-only Bakers site had one Base, +2 at foundation and +3 with a Wind Mill. The candidate-only Bakers site had two Base, river adjacency, +3 at foundation and +4 with a Water Mill. They were built by different civilizations. Counting all holdings at turn 225, including transfers, both groups held 22 Bakers and seven Tailors, with 28 of 29 plots in common. The full planner had 29 complete and the candidate had 28. Neither group had a Tailors Quarter adjoining a working Stage 2 customer district.

The controller's census reads gameplay-defined material and customer relations. Physical founding events include the original five AI players, and sampled customer coverage includes completed Quarters and completed mapped customer districts. The per-turn accounting counts calls at the economic forecast itself. [Matched replay and result checker](../../tools/native_ai/late_placement/shortlist_pair.py)

**Mature timing check.** Both arms also reloaded the same Large Continents, Standard-speed turn-350 save and played turns 351–360. The full planner executed 600 Quarter forecasts. The candidate executed 537 and skipped 63 (10.5%). All 237 leading city/Quarter proposals matched on plot and final bid. The eight matched whole-turn intervals averaged 37.94 seconds with full pricing and 37.23 seconds with selective pricing. Each interval was faster, averaging a 0.72-second saving (1.9%). The respective maxima were 57.92 and 57.81 seconds. Over all ten turns, direct CSC guidance averaged 6.57 and 6.21 seconds (0.36 seconds saved, 5.5%), with maxima of 6.88 and 7.03 seconds.

Keep the candidate experimental. The mature-save result makes selective pricing worth considering for expensive late-game turns. On the Small game the cutoff preserved placement quality but produced no whole-game timing gain. These two games do not establish a threshold for switching the policy on automatically.

### Testing a shorter list of Quarter forecasts, 27 November

The full planner bids on every qualifying site. In a diagnostic game the controller also tracks which sites a cheaper planner would have priced. It makes that choice before seeing the current scores. For each city and Quarter it keeps its own two previous leaders, newly eligible or locally changed sites, confirmed plans and saved footprints. It adds one other plot in rotation. A new city, a gap in observation or the scheduled eight-turn refresh gets a complete evaluation.

The comparison counts calls to the Quarter economy forecast after the ordinary eligibility and adjacency checks. It also checks the leading plot and bid against the normal publisher's log for each city and Quarter. A missed leader can mean an equally valuable alternative, a lower offer, or a lost offer altogether. The observer follows missed plots for up to ten turns to record repricing and occupation. All construction in this game follows the full planner.

The observer is loaded by the game controller only when requested. See [the observation rules](../../tools/native_ai/late_placement/shortlist_observer.lua) and [the results checker](../../tools/native_ai/late_placement/shortlist_results.py). Run the checker with the archived game directory containing the protocol, observer receipt and Lua log.

**Full-game result.** Small Continents, Online, Prince, CSC + City Lights, map seed 27112601, game seed 27112602. From turns 2–250 all 1,245 original-AI player passes were observed and all 2,698 leading proposals matched the independent full-planner log before applying the hypothetical shortlist. The endpoint save was verified and the controller restored the original mod preferences.

| Quarter | Full forecasts | Could skip | Exact preferred plot retained | Turns with a bid lost entirely¹ |
| --- | ---: | ---: | ---: | ---: |
| Bakers | 3,037 | 380 (12.5%) | 1,028 / 1,034 | 3 |
| Tailors | 5,192 | 760 (14.6%) | 1,649 / 1,664 | 5 |
| Both | 8,229 | 1,140 (13.9%) | 2,677 / 2,698 (99.2%) | 8 |

¹ Each observation refers to one player's city and Quarter type on one turn. Across the 21 missed leaders, five alternatives were within 5% of the leading value, eight were further behind and eight had no positive alternative. Late-game savings were smaller: 178 of 1,847 calls (9.6%) over turns 201–250. The shortlist recovered all 19 tracked miss episodes within two turns (17 within one). Their Quarter plots were still free when repriced.

The shortlist kept 299 of 300 leading layouts with both Base and Spec. It kept all 246 leading Tailors layouts with Base and a possible or completed Harbor, representing ten distinct city/site combinations across seven cities. One of the 48 full leaders newly confirmed by the native best-site journal was missed. On turn 49, Harald's leading Bakers proposal named plot 1122 as a customer site. On turn 50, that tile became the best Quarter site with both Base and Spec. Its bid was 2,170 against the shortlist's 1,176. Civ selected it before the shortlist rediscovered it. CSC withdrew support on turn 52 as the economics changed.

**Decision.** Keep full evaluation in ordinary games. Sixteen of the 21 misses occurred when the full planner had no bid the preceding turn. Repricing all candidates after the *shortlist* had no bid would cover 17 misses for 344 extra calls on the recorded history, leaving 796 calls (9.7%) available to skip. A revised rule would build a different history. Test that rule and retain the previous lead's customer footprints before testing a live cutoff. In a matched replay, check actual turn time as well as native selections of lower-ranked plots.

For this instrumented run the full guidance averaged 2.34 seconds per turn with a 5.10-second maximum (turn 211). Whole turns averaged 11.38 seconds over 198 popup-free intervals inside controller windows, peaking at 32.56 seconds on turn 239. The live game executed every forecast, so these timings include the diagnostic and provide a reference for a later timed comparison.

### Removing the second Quarter scan, 26 November

**Matched mature-save result.** Both builds replayed turns 351–360 from the original guided turn-350 checkpoint on Large Continents, Standard speed, with City Lights and Dev CE. The control used the original November 26 benchmark Lua. The candidate included the legal-target cache, shorter forecast lifetimes, independent-chain reuse and scan changes. Both loaded the same save and published all ten turns successfully.

| Timed work | Original mean | Optimized mean | Original maximum | Optimized maximum |
| --- | ---: | ---: | ---: | ---: |
| CSC guidance, all 10 turns | 6.82 s | 6.18 s | 7.43 s | 6.55 s |
| Whole turn, 8 matched clean intervals | 37.03 s | 35.76 s | 56.55 s | 55.54 s |

CSC saved 0.64 seconds per turn on average (9.4%) and finished sooner on all ten turns. Whole turns averaged 1.26 seconds faster (3.4%) and finished sooner on all eight measured intervals. The clock excludes popups and controller handoffs. This is one mature map with the optimizations measured together.

All 594 logged Quarter forecasts and all 340 ranked Quarter site bids matched exactly, including site, score and customer footprints. All 631 customer bid records matched (208 future, 73 prospective and 350 economic), as did 3,245 footprint protection costs, 230 connection plans and 72 completion records. The original emitted 160 owned-site fallback scan summaries. The optimized arm needed none. A failed-planner regression separately exercised the fallback with material protection intact. [Game-controller replay and comparison](../../tools/native_ai/late_placement/mature_guidance_replay.py)

The economic planner publishes a score for each worthwhile Quarter plot, a default for the remaining plots, and the customer bids for its layouts. The older siting scan used to visit the owned and frontier plots first. Its Quarter scores were discarded on every successful managed pass. It now runs if the economic snapshot is unavailable, if the managed pass fails, or if the snapshot relies on the older customer nominations. Material protection is computed before either planner runs. The `CSC_AI_QUARTER_PLAN` and `CSC_AI_FRONTIER_QUARTER_PLAN` log rows now describe fallback scans. Use `CSC_AI_ECONOMY_PLAN` and `CSC_AI_SPATIAL_BID` for normal play.

Quarter, customer and City Lights provider planning share the ordered radius-three tile list for each city within a player pass. Bakers and Tailors also share the initial plot ownership, frontier and visibility checks. Each still evaluates its own materials, customers, purchase quotes and economic bids. At the next turn the planner reads ownership and eligibility again. CSC skips the native selection journal when the prior packet has no new positive Quarter offer that could establish a plan. When one bid appears in multiple diagnostic categories, CSC reads its receipt once and uses it for each category's log.

### Reusing independent supply chains, 26 November

The Quarter and customer planners used to reschedule and reprice every established chain for each proposed district plot. When an existing chain keeps the same suppliers, customers and investment plan, and has its production queues to itself, the planner can carry its scheduled buildings, yield streams and successful individual prices forward. It does this within one player's planning pass. A new pass starts from current game facts. Ordinary and Service-aware forecasts each use their own baseline.

Each candidate still gets a whole-empire comparison. A shared city queue, shared Market, or yield loss timed to another Quarter's construction takes the full scheduling path. Population payouts are combined before rounding. The planner recalculates trade, Amenities and Housing after combining chains, so a prospective district can still break a route or change the value of a Service elsewhere.

In a Lua 5.1 fixture, a new Quarter competed against the same baseline while the number of independent existing chains increased. Each row shows the median time per forecast across seven paired batches of 25 forecasts, after warming the cache. All cases returned the same marginal value of 27,648 Q8 and visited the same ten investment choices.

| Existing independent chains | Full forecast | Reused forecast | Price calls, full → reused |
| ---: | ---: | ---: | ---: |
| 1 | 0.198 ms | 0.180 ms | 16 → 10 |
| 4 | 0.480 ms | 0.378 ms | 52 → 28 |
| 8 | 0.925 ms | 0.728 ms | 100 → 52 |
| 16 | 1.727 ms | 1.277 ms | 196 → 100 |

The fixture measures a single forecast with a simple Lua price function. The price counts include calls that the game's existing price cache could already answer. Offline regressions also compare the complete result from the Quarter and customer adapters with and without City Lights, shared buyer queues and rounded returns, a tile purchase, losing and regaining a supplier, route loss and restoration, and pooled Service Housing. The effect on average and late-game turn times still needs a matched game measurement. [Benchmark](../../tools/ai_economy/benchmark_independent_chains.py) · [Regression cases](../../tools/ai_economy/test_independent_chain_forecasts.py)

### Shared legal targets and shorter forecast lifetimes, 26 November

The customer-first planner now uses the same player/publication BUILD-target cache as the Quarter planner. A fixture queried two city/district keys from both paths, one populated and one empty. Each key needed one UI call. The following publication picked up a change in legality. Standalone fact readers can still query their supplied UI directly.

The facts reader releases each candidate Quarter world after the site calculation. The adapter retains shared baseline and customer results and releases each site's winning ledger after extracting its marginal value. A Lua 5.1 comparison against commit `2573f6c9` matched the entire returned forecast, placement score and score components on 128 quotes across ordinary and City Lights fixtures, with Service pricing enabled and disabled. Each batch warmed one three-chain forecast, varied its land invoice 32 times in one publication, and collected garbage before reading the retained heap. The previous code retained about 1,190 KiB of additional heap per batch, and the revised code retained 39–40 KiB, after accounting for the serialized comparison output. This measures retained memory on those inputs. Live turn-time savings remain unmeasured.

Henno requested average and maximum added processing time in the next full-game
run,17 November2026. Every subsequent full-run report should include these
measurements alongside placement and supply-chain outcomes.

The main CSC publisher records elapsed wall time around its complete synchronous
pass: receipts, live facts, economic forecasts, all original AI players, packet
staging and continuity writes. `CE_AIMonotonicSeconds()` provides a read-only
steady clock. Timings are logged as integer microseconds and reported in
milliseconds or seconds. Per-player spans explain the work inside that envelope;
they are not added to the whole-publisher total a second time. The additional
`os.clock()` readings are labelled Lua-clock time without assuming the game's
implementation measures process CPU time.

Before replacing a policy packet, CSC reads CE's cumulative managed-cell refresh
time. The shared controller also reads the final packet at the terminal inactive
boundary. This native work is reported separately, by packet publication turn;
repeated observations of the same version contribute their maximum. These
counters cover the managed score refresh, rather than every CE hook or the
ordinary native routines it calls.

The run's `ai-processing-time.json` contains:

- Average, maximum and total whole-publisher wall time, summed over all attempts
  on each game turn, including failed attempts and retries.
- Per-player averages/maxima and the five slowest turns.
- Native managed-cell timing, publication counts and failures.
- Missing turns and incomplete clock coverage. A partially measured turn is
  excluded from the average; missing data never becomes a zero-cost turn.

Turn0 startup is outside the default turn1–250 distribution. The ordinary Lua
log retains it for separate inspection. Whole-turn game speed also includes
native AI, rendering, passive test observers and controller waits; the direct
publisher measurement isolates the synchronous guidance cost from those tasks.
The matched layout report also records launch-to-endpoint wall time and its
average per game turn. These use the controller's launch clock and confirmed
inactive endpoint. Startup and passive observations are included.

Keep recurring work bounded: definitions are cached; a publication shares an
immutable route observation and at most128 distinct route timelines; customer
economic comparisons receive at most16 world forecasts per player/publication.
Unchanged chains retain their discrete investment choices while affected chains
and shared customer investments are reconsidered. Shared queue times, population
rounding and shared benefits are recomputed in each candidate world.

The current mature-save qualification and resulting full-game measurements are
recorded in the [customer-world implementation report](../research/mods/csc-customer-world-pricing-20261117.md).

On 18 November, the joint search began reusing exact priced plans within each
forecast. It keeps at most 16 states for a single world and releases them when
that forecast ends. Revisited plans still count against the same logical
budget. The Pangaea turn-200 comparison confirmed equality for all bids,
plans, and detailed forecasts in two tested player passes.
[Optimization and measurements](../research/mods/csc-ai-joint-guidance-performance-20261118.md).

## Qualified Quarter-layout default, 25 November

In the final matched Online games, the planner added an average of
0.84 seconds per turn standalone and 0.89 seconds with City Lights.
Maximum whole-publisher time per turn was 4.97 and 5.42 seconds in the
two candidate games. Average total game time was 13.17 → 14.52 seconds
standalone and 14.12 → 16.67 seconds with City Lights. Total time also
includes startup, passive observation and changes in what the AI did.
The qualification paired these costs with more supplied layouts and
working buyers. Keep the City Lights total-turn measurement in later
performance comparisons.
[Final matched placement and timings](../research/mods/city-lights-ai-placement-20261116.md#final-calibrated-turn-250-qualification).

## Quarter-layout campaign, 24 November

Timing over the full 250 turns averaged 1.65 → 2.75 seconds with CSC alone
and 1.97 → 3.93 with City Lights. The rise was largest in mature empires.
Each cell below is the mean and maximum whole-publisher time in seconds.

| Turns | CSC default | CSC candidate | City Lights default | City Lights candidate |
| --- | ---: | ---: | ---: | ---: |
| 1–100 | 0.56 / 1.63 | 1.17 / 3.07 | 0.64 / 1.49 | 0.97 / 2.58 |
| 101–200 | 2.23 / 3.34 | 3.55 / 7.82 | 2.99 / 4.92 | 5.40 / 7.88 |
| 201–250 | 2.67 / 3.55 | 4.29 / 5.77 | 2.61 / 3.36 | 6.93 / 8.96 |

The mature City Lights candidate spent 2.59 seconds per turn on average in
player 5's span, versus 0.16 in the default. The recorded joint forecast
work for that seat rose from 223 to 1,049 logical evaluations per turn.
The same-save checks separate the cost of the economic model from
differences in what the two empires built during the full games.
[Standalone layout results](../research/mods/city-lights-ai-placement-20261116.md#matched-standalone-result-24-november)
and [City Lights results](../research/mods/city-lights-ai-placement-20261116.md#matched-city-lights-result-at-turn-250).

A separate turn-200 City Lights replay compared caching the existing
customer's adjacency footprint with the current facts reader. Four
same-save passes produced identical forecast and layout fingerprints.
The two current passes averaged 1.39 seconds for the measured player;
the two cached passes averaged 1.45 seconds. Customer-site work averaged
0.156 and 0.158 seconds respectively. The current reader stays in use.

The joint model now skips the second sweep when the first accepts no
producer or customer investment change. Those states would repeat in the
same world. The old logical visit count still applies to the work budget
and the failure boundary. The offline comparison returned identical bids,
ledgers, plans and errors across 226 forecasts, including 23 route cases.
The 203 joint cases made 148,484 price calls instead of 163,989. In the
City Lights turn-200 replay, the four passes for player 5 returned the
same forecast, bid and plan fingerprint. The full player passes averaged
2.45 seconds before the skip and 2.56 after it. World pricing averaged
1.95 and 2.07 seconds respectively. The sample confirms identical
outputs and fewer offline price calls. It showed no wall-time gain.

At the five sampled turns from 150 to 250, the full prospective forecasts
rejected 195 of 381 standalone quotes and 116 of 346 City Lights quotes on
placement quality. The planner now avoids a full forecast on an unreserved,
unsaved plot when the current adjacency, the best possible Stage 2 terrain
gain and its admitted partner's gain still fall below the placement floor.
Saved plans, reserved plots and unknown values keep their normal quote.
The same-save City Lights comparison on turn 200 skipped five candidate
forecasts per pass for player 5. Both baseline and screened passes returned
the same bids and saved layouts. Average total player time was 2.58 seconds
before the screen and 2.51 with it. World pricing averaged 2.04 and 1.99
seconds respectively. The old rejection counts are the upper limit on what
this check can save, because some sites excluded by the full forecast can
still pass its conservative upper bound.

The turn-200 standalone profiling replay measured seven turns after the
matched switch, across all original AI seats. It sampled successful
Quarter forecasts with a variable investment plan.

| Measured work, turns 203–209 | Control | Candidate |
| --- | ---: | ---: |
| Forecasts | 160 | 499 |
| Actual ledger builds | 2,370 | 5,576 |
| Time building those ledgers | 3.20 s | 7.16 s |
| Time pricing the built ledgers | 1.00 s | 2.11 s |

Building the candidate's ledgers took 77% of these measured stages. A
shadow cache for 16 extra previously priced states found 569 revisits
with 0.87 seconds of gross build and pricing time across the seven turns.
Avoiding impossible placements before building their ledgers is a larger
opportunity than retaining more trial states. The final matched games measure
the effect over full turns and across all AI players.
