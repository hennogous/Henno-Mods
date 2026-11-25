# AI guidance processing time

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
and shared customer investments are reconsidered. Queue times, population
rounding and shared benefits are still recomputed in each candidate world.

The current mature-save qualification and resulting full-game measurements are
recorded in the [customer-world implementation report](../research/mods/csc-customer-world-pricing-20261117.md).

On 18 November, the joint search began reusing exact priced plans within each
forecast. It keeps at most 16 states for a single world and releases them when
that forecast ends. Revisited plans still count against the same logical
budget. The Pangaea turn-200 comparison confirmed equality for all bids,
plans, and detailed forecasts in two tested player passes.
[Optimization and measurements](../research/mods/csc-ai-joint-guidance-performance-20261118.md).

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
