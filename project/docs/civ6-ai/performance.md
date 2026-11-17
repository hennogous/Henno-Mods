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

Keep recurring work bounded: definitions are cached; a publication shares an
immutable route observation and at most128 distinct route timelines; customer
economic comparisons receive at most16 world forecasts per player/publication.
Unchanged chains retain their discrete investment choices while affected chains
and shared customer investments are reconsidered. Queue times, population
rounding and shared benefits are still recomputed in each candidate world.

The current mature-save qualification and resulting full-game measurements are
recorded in the [customer-world implementation report](../research/mods/csc-customer-world-pricing-20261117.md).
