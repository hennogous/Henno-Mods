# Joint guidance performance pass

The Quarter and customer adapters share a search over producer plans and
customer investments. Each of its two seeds and two sweeps can revisit a
complete state. Rebuilding those ledgers repeats scheduling, stream pooling
and pricing. The model now reuses the starting result within a producer
coordinate and caches up to 16 exact priced states across a single world's
search. The state key combines the selected producer option for every chain
and the variable customer investment flags. State is private to one forecast,
so an offer in a different world still sees its own queue, supplier, route and
native quote inputs. The same logical attempts count against the same budget.
The validated rank and tie order are unchanged.

The offline comparator matched canonical outcomes for all 224 joint and route
calls, including budget failures, forecast detail and signed payouts. Its
201-world group fell from 233,498 to 163,967 price callback calls. All 158
economy checks and 13 timing/controller tests passed.

The shared controller loaded the original Online Pangaea turn-200 save for a
read-only B/A/A/B measurement with players 1 and 3. Each arm used a fresh
private module set and identical native prices and live facts. The benchmark
compares canonical bids, status, plans and all returned forecast contents after
the timer ends. All four passes per player matched. The measurement covers
economic preparation, Quarter and nested customer valuation, with cold
history. It excludes other publisher work such as packet staging.

| Player | Previous economic pass mean | Reuse mean |
| --- | ---: | ---: |
| 1 | 1.21 s | 0.76 s |
| 3 | 1.05 s | 0.51 s |

Artifacts are under `Desktop/Codex/csc-ai-guidance-performance-20261118`.
The old Pangaea full run is the same-seed reference at 2.604 seconds average
and 6.198 seconds maximum over 250 measured turns.

## Full-game comparison

The shared controller ran a fresh Online Pangaea game to turn 250 with seeds
27061117/37061117. The frozen candidate package differs only in the CSC
economic model. The CE DLL, optional package stack, initial map and setup
matched the reference. Both runs use the integrated CSC policy and the same
passive observations.

| Whole-publisher wall time | Previous | With exact-plan reuse |
| --- | ---: | ---: |
| Average per turn | 2.604 s | 1.554 s |
| Maximum per turn | 6.198 s | 3.452 s |
| Average, turns 1–125 | 1.127 s | 0.694 s |
| Average, turns 126–250 | 4.080 s | 2.414 s |
| Total over 250 turns | 650.924 s | 388.507 s |

The average fell 40.3% and the peak fell 44.3%. The publisher used 262.417
fewer seconds in total. All 250 publications succeeded with complete clock
coverage. CE's separately measured managed-score refresh averaged 11.6 ms
before and 16.0 ms after. Whole game turn speed also depends on ordinary game
work and the test environment.

All 25 observed original-AI Quarter foundations matched by turn, player,
city, district type and plot. Both runs founded 22 Bakers and three Tailors.
The endpoint summaries also agree on completed Quarters, working Base
suppliers, Stage 2 producers and customers, and nine ready Bakers Stage 2
chains with active Service properties.
The same-state benchmark is the direct check on forecast equivalence, while
this outcome checks what happened over the full game.

Both controller sessions closed with native exit code zero and restored
preferences. The fresh game recorded all ten milestone censuses and retained
verified saves at turns 50, 100 and 200. Civ's inactive single-player save
gate refused the turn-250 archive before any save request was sent. Final
timing and placement results were recovered from the archived logs and census.
The full-game and checkpoint-replay duplicate installed packages were retired
against their verified frozen sources. See `pangaea250/timing-comparison.json`
and `pangaea250/ai-processing-time.json` in the artifact directory.
