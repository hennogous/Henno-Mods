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

## Rejected rotating save and corrected source preparation

`liverpool-source-inspection-01` failed **before inspection or eligibility**.
The shared controller expected inactive turn 25, but the first native handoff
was turn **27**, with player 0 still AI-controlled. The controller rejected the
source. Normal cleanup succeeded (native exit 0, owners absent, preferences and
packages verified). No Liverpool material facts or fixture edits came from this
attempt. File-origin verification is preserved; saved clock qualification failed.

This failure matches the previously documented AI-observer rotating-autosave
hazard in the natural-research report. The caller chose an unsuitable input;
the controller correctly refused to normalize its clock or change its role.

The replacement is a bounded replay of the exact verified turn-22 source to
inactive turn 25, followed by read-only reconciliation and the shared
`save_inactive_boundary` helper. `--early-save-liverpool` requires the unchanged
all-five-AI scout and endpoint 25. The reload mode now rejects raw origin JSON
before launch and requires a normally closed creation run, source lineage,
verified native SaveComplete, unchanged inactive human-0 phase, matching save
hashes and the same main AI sources. Reload still independently checks actual
clock and roles. This qualifies a source; it does not establish an uncommitted
native district slot or close 1.3. Astra approved that distinction and route.

## Verified paused source and reconciled materials

`liverpool-paused-source-01` completed the bounded **22→25** replay and closed
normally with exit 0, absent owners and verified preference/package restoration.
The shared helper observed exactly one SaveComplete and unchanged inactive
turn 25 with human player 0. The archived source SHA-256 is
`72929ef428403116ad9b34ce7fcaa4133ed44aa572513c07c2678ab97930c9b4`.
It does not overwrite Henno's separately preserved turn-3 game.

The read-only inspection reconciles all three Base contributions:

| Plot | Material | State | Counted adjacency | Viable supplier |
| --- | --- | --- | --- | --- |
| 2572 | CSC Flax | Under Liverpool City Center | 1 | No: district occupies tile; Farm query false |
| 2498 | Wheat | Liverpool-owned, unimproved | 1 | Yes: Farm allowed and unlocked |
| 2496 | Maize | London-owned, unimproved | 1 | Yes: same player; Farm allowed and unlocked |

The adjacency handler counts matching owned resource plots; it does not impose
the supplier reader's no-district and improvement-viability gates. This is not
duplicate counting or resource-quantity multiplication. These are the actual
loaded frozen-carrier rules, not a claim about all future CSC implementations.

Site 2497 remains empty with two real river edges, no Bakers Quarter and no
current production. Its projected Water Mill contributes 1 Production
(`activeNow=false`, `inPlan=true`). City Center supplies 1 Gold; an explicitly
conditional Commercial Hub projection supplies another 1. Host 2571 is empty,
owned by Liverpool, revealed, actor-permitted and geometrically feasible.
The full forecast is 6. Original roles persist as human 0 and AI 1–5.

Astra independently audited the files and normal closure. Source qualification
is complete; native freshness of the next district comparison remains unproved.
The controlled derivative removes Flax 2572 and Wheat 2498 once, retaining
Maize 2496, actual rivers, City Center and host 2571. All original resource,
ownership and district facts are asserted before either diagnostic write.
Both comparison arms must load the same saved derivative, revalidate those
facts, and use unchanged main-policy bands. Only the control withholds the exact
prospective river rule in CSC's model for 2497. This map preparation is not an
AI action, native purchase or shipping policy.
