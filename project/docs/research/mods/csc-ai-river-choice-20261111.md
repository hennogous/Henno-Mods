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

## Observation result and next representative case

`river-london-full-01` completed **22→26**, four turns, normal exit 0 with owner
absence and verified preference/package restoration. Six prefix begin/end pairs
match; 1,251 retained native records have unique generation/index keys. Astra
independently verified the result and the longer archived timing leads.

At London's fresh **24** comparison, Royal Navy Dockyard 2566 wins at
**53,439 Q8**, versus Bakers 2495 at **25,329**. The later Bakers cache rises to
41,021 while the Dockyard plan is retained; that is not another fresh loss.
The river rule is explicitly `activeNow=false`, `inPlan=true`, requiring
`BUILDING_CSC_BAKERS_WATER_MILL` throughout. Thus the projected +1 is delivered
through the +48 offer, but no discriminating river-choice case is established.
Do not run the proposed London ablation just to observe another changed score.

A newly founded **Liverpool, player 4 / city 131073**, makes a fresh **25**
Bakers choice at **2497**, score **37,520 = 25,232 + 12,288 Q8**. This is a genuine
native Quarter win and request, but the model gives adjacency **6**: Base rule
count 3, prospective Water Mill +1, City Center +1 and future Commercial Hub
2571 +1. Removing only the river point leaves 5 and the same +48 band. It is
therefore also unsuitable for that isolated ablation. The nearby frontier 2423
has adjacency 4 from Base +1, projected river +2 and future customer +1, but the
owned site wins.

Astra recommends a controlled **predecision Liverpool-25 one-Base case** if the
natural leads remain non-discriminating. First reconcile Base rule count 3 with
the two viable supplier records (Maize 2496 and Wheat 2498). The loaded adjacency
core counts matching resource plots, not resource quantity; the supplier reader
has additional viability restrictions. The exact third counted plot is not yet
identified. Do not guess which removal produces one counted, viable Base.

Preserve the real river, City Center and future customer footprint. Save one
common derivative for both arms, require the unchanged ordinary model to give
4 versus 3 when the exact river rule is withheld, and measure fresh native
values. This is a representative controlled case, not natural-game reliability
or a reason to change a score band to fit a known gap.

The autosave written during this verified owned session is preserved at
`river-london-full-01/source-autosaves/candidate-25.Civ6Save`, SHA-256
`c598a84182c5c716e9f9626d4ece83ce77c89bc461d22d03d932cead03623b35`.
File header, size, hash and creation within the owned run's time interval are
verified. **Its actual saved clock and predecision state remain unverified by
reload**; the filename alone is not that proof. The companion origin JSON records
this limitation. No resources or other map facts have been edited for this case.
