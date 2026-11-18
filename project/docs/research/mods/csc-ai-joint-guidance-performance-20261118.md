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
