# River valuation: prospective Mill benefit and native Quarter choice

Active **Problem 1.3**, after Astra-validated representative completion of 1.1
and 1.2. Acceptance: real river/Mill geometry changes the reusable main policy's
offer and a native Quarter choice in a controlled comparison. Trace the exact
loaded rule, prospective versus current value, ordinary Q8 offer, consumed
comparison and changed type/site. A forecast or write alone is insufficient.
Construction completion remains 1.6.

## Existing lead and bounded observation

The earlier unchanged turn-22→24 scout identifies **London, player 4 / city
65536 / Bakers plot 2495**. Its loaded Water Mill rule counts three river edges,
which produce **one** projected Production point, not three. Base Maize 2496,
that Mill point, City Center adjacency and future Commercial Hub 2569 combine
to **4** and the ordinary **+48** offer. Removing just that projected river point
would yield 3, ordinarily the +24 band, subject to normal candidate ranking.

The prior native caches are 26,984 Q8 for turn 22 and 25,329 for 23. London's
held Holy Site contract 143 finishes on 23. An inactive endpoint at 24 captures
the preceding round, not its possible fresh 24 choice. This gives a concrete
reason for an unchanged **22→26** observation; it is not a new world search or
an indefinite extension.

`river-london-full-01`, under `Desktop/Codex/csc-ai-problems-1-2-20261110`, uses the
same pinned original turn-22 source, all-five-AI role setup, current four main AI
modules, UI bridge and read-only CE prefix tracing. `--early-through 26` keeps
the observation bounded. Existing rule lines are retained; companion
`CSC_EARLY_RULE_GATES` lines explicitly log `activeNow`, `inPlan` and the required
Mill so a projected benefit cannot be mistaken for realised output.

Astra independently checked the lead, rule arithmetic, completion window and
scope before launch. Four early-helper checks, six reader checks, nine discovery
checks and five Boston helper checks pass. This run adds no diagnostic score
writer, map edit or new native hook.

## Conditional control

Only if the full run exposes a useful native comparison, suppress the exact
loaded `CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER` contribution for this
player/city/site inside the shared score model. Preserve the prospective Water
Mill branch, actual river edges, host/supply facts, eligibility, other rules and
ordinary bands. Let the model recompute its preferred candidates; inspect all
packet differences and native baselines before attributing a changed choice.

This would test the value of a **prospective Water Mill river benefit**, not
whether that Mill has been built or has begun paying. If the full Quarter offer
still loses by a wide margin, retain the measurement and do not run an ablation
that cannot satisfy the changed-choice acceptance condition.
