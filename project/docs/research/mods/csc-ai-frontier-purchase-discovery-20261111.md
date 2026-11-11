# Frontier purchase discovery in three existing worlds

## Purpose and scope

Problem **1.5** needs a credible Quarter footprint and an observed native
purchase, rather than another bid on Nicopolis's uncertain plot 401.
This diagnostic loaded three existing Online turn-200 checkpoints through
one exclusively owned shared-controller session. It advanced **zero turns**,
submitted no purchase or score treatment, and preserved the integrated policy.

The CE carrier SHA-256 was
`f8121151c787e4dcd4fea876eaaef5d6d1bb2b54561bc94d9d7da6385f21aa07`.
The patched stock GameCore was
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
Loaded module paths and identities were checked in every world. The frozen
CSC carrier replaced only its scanner and publisher with current main-mod
bytes. Two independent city/name/owned-plot tuples checked each loaded world
against its previous survey, in addition to exact save hashes and turn readiness.

Tools are `project/tools/native_ai/late_placement/frontier_discovery.py` and
`frontier_site_survey.lua`. Evidence is under
`Desktop/Codex/csc-ai-problems-1-2-20261110/frontier-discovery-three-saves-01`.
The controller verified exit zero, original preference restoration, absence of
remaining owned processes and retirement of the exact temporary packages.

## What was enumerated

For each alive major AI city without that Quarter, enumerate revealed,
unowned, district-free, radius-three sites with a same-player border neighbor
and a successful `CanHaveDistrict` geometry query. Keep leads with at least
one **known viable owned Base** from the actual CSC supplier reader.
Record loaded all-stage customer/provider relationships, alternative future
owned customer footprints, improvement readiness/working state, river edges,
producer unlock metadata, Treasury and raw income/maintenance fields.

These are leads, not assured investments. Future footprints are alternatives,
not benefits to sum together. Producer unlock metadata does not establish its
location-specific requirements, admission, cost or construction. Existing
reservations, active requests and district capacity still need native inspection.

Separately search for revealed unowned Base deposits beside existing Quarters.
Such deposits would need their own purchase and improvement qualification.

## Results

Counts are city/profile/plot pairs, so different cities or Quarter types can
refer to the same physical footprint.

| Saved world | Candidate pairs | Distinct plots | Future host geometry | Working Base | Both material classes | River edges present |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Continents | 4 | 4 | 1 | 0 | 0 | 0 |
| Pangaea baseline | 10 | 8 | 8 | 1 | 0 | 3 |
| Fractal baseline | 20 | 14 | 17 | 1 | 3 | 2 |

All 34 pairs had positive UI quotes. None had an existing mapped owned host;
26 had at least one future host alternative. No supplier-purchase lead met
the separate revealed/unowned/adjacent-Base enumeration in these checkpoints.
This does not establish an absence of supplier opportunities in earlier games,
unrevealed land, foreign land or supported configurations generally.

The two working-Base leads were:

- Pangaea, player 2, Takamatsu city 589832: Bakers plot 756, working Maize at
  829, quote 95 Gold, future host alternatives on 830 and 755.
- Fractal, player 2, Szeged city 589829: Tailors plot 1365, working Cotton at
  1366, two river edges, quote 85 Gold, future host alternatives on 1290.

That future host plot belongs to another friendly city, ID 524292, rather
than Szeged 589829. Resolve its identity and applicable cross-city customer
rules before treating it as a credible benefit. Its capacity and commitments
affect timing; immediate customer admission is not required for long-term
map potential. Quarter admission itself remains a separate native gate.

Szeged's player had 719.7734375 Treasury Gold, raw Gold yield 161.97265625
and maintenance 87 at this boundary. These are not its earmarked plot/slush
funds. The site still needs the canonical adjacency calculation, exact host
types, district capacity and current commitment checked. In particular, an
all-stage customer alternative does not establish a Stage 2 Harbor chain.

## Gameplay versus UI query context

The optional Gameplay quote call returned no numeric value for these pairs,
with `missing method: GetPlotPurchaseCost`. The same scoped UI reads returned
positive prices. The diagnostic preserves missing-input flags rather than
substituting zero, then joins independent UI values by player/city/plot.
This is a result for these contexts, not a universal claim about every Lua API.

The strict UI `CanStartCommand` query returned false for all pairs at the
inactive observer boundary. The archived field is named `canPurchaseNow`.
That name must not be taken as native Economic eligibility: we have not
isolated the effects of caller, player-turn state or overload semantics.
Native validation and actual spending remain separate observations. The
maintained tool uses the clearer label `uiCanStartAtBoundary` going forward.

## Qualification and next test

The six offline checks cover supply/visibility/ownership filtering, explicit
missing quotes, retained nonpositive quotes and deduplicated Gameplay/UI joins.
The live collection separately verifies the actual contexts and three source
worlds. Astra reviewed lifecycle, provenance, limits and candidate requirements.
Neither test category proves an AI choice, purchase or placement improvement.

Szeged is the first lead to inspect more deeply: verify its actual projected
adjacency and customer footprint, native district admission/reservation and
earmarked funds, and compare Takamatsu's working-Base lead. Positive frontier
offers are not implemented yet: production frontier handling currently supplies
deductions. After qualifying the model and native gates, implement the bounded
common-model offer, then compare it with a scoped ablation while observing
comparison, request, native payment, ownership and foundation.
Keep the existing native competition and actual own-funds constraints intact.

## Exact model inspection and future-type correction

The zero-turn `frontier-model-two-saves-01` inspection loaded the same Fractal
and Pangaea saves and called the live scanner's shared read-only adjacency
function. None of their 30 known-Base frontier pairs reached +4, even taking
the maximum of one future neighbor alternative. This diagnostic maximum is
not the live planner's traversal choice, nor a native utility score.

Szeged plot 1365 is **2 Production + 1 projected Gold = +3**: Cotton supplies
one Production, two river edges supply another, and one future Holy Site or
Commercial Hub can add one Gold. Neither alternative is a Stage 2 Harbor.
Takamatsu plot 756 is **1 Production + 1 projected Gold = +2**. Its flat inland
site gets no extra adjacency from its projected Wind Mill branch.

The unfiltered geometry query also accepted Lavra and Suguba for Hungary,
and Street Carnival, Suguba and Hippodrome for Japan. Consequently the earlier
26 future-host leads in AI-C142 mean raw geometry, not verified actor eligibility.

The main scanner now applies civilization/leader traits (including inherited
leaders), direct unique replacements, explicit exclusions, existing district
families and mutual exclusion to prospective empty footprints. It follows
shipped `Civ6Common.lua` and `TechAndCivicUnlockables.lua` conventions. It does
**not** require the future district's current unlock or population capacity.
An existing native customer target remains authoritative for an immediate bid.
Missing required metadata leaves a supplied site neutral, with no invented
no-host deduction or city-deferral count. This is a scoped planning filter,
not a reproduction of every native district-admission rule.

### Matched zero-turn filter inspection

`frontier-filter-two-saves-01` advanced zero turns and verified normal exit,
preference restoration, process absence and exact package retirement.
The same 30 city/profile/plot pairs remained. Future alternatives changed:

| World | Raw alternatives | Filtered alternatives | Pairs with changed alternatives | Pairs losing all future hosts | Maximum forecast changed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Fractal | 94 | 42 | 17 | 0 | 0 |
| Pangaea | 60 | 26 | 8 | 0 | 0 |

These counts include multiple district types/footprints per Quarter site;
they must not be added together as future adjacency. Szeged retained only
Holy Site/Commercial Hub at Debrecen plot 1290. Takamatsu retained Commercial
Hub/Entertainment Complex at its two other-city footprints. Their +3/+2
maxima were unchanged. This demonstrates removal of invalid possibilities,
**not** a changed native decision, acquisition or closure of Problem 1.2.

UI capacity reads succeeded where Gameplay's optional getters were absent:

| Player 2 city | Population | Allowed specialty districts | Zoned specialty districts | Current production |
| --- | ---: | ---: | ---: | --- |
| Fractal Szeged | 5 | 2 | 2 | Settler |
| Fractal Debrecen | 10 | 4 | 3 | University |
| Pangaea Takamatsu | 1 | 1 | 0 | Nothing |
| Pangaea Yokohama | 4 | 2 | 1 | Industrial Zone |
| Pangaea Shizuoka | 7 | 3 | 2 | Lighthouse |

These counts inform timing; they do not invalidate a future footprint merely
because a city needs to grow first. They are not proof of all reservations or
requests. The loaded Quarter definitions do not require specialty capacity.

The archived filter scanner SHA-256 is
`a0fb022f8078371455e7b43378990137ae76f0b416ab39dbff675db51de83253`.
The unfiltered model scanner is
`4045300c94eda59e37642cfab26760e678c7b7eb7aadf5d67f2c6e1c614d7325`.
Subsequent Astra review corrected replacement ordering to suppress the base
before exclusions, made family expansion one level, and hardened unknown
metadata handling. Those refinements pass eight helper tests, ten grouped
scanner checks and seven discovery checks. They were made **after** the live
run staged its bytes and are not claimed as live-tested final source.
Astra independently checked the source corrections and archived counts.

Filtered survey SHA-256 values:

- Fractal: `b2bd552ad291e2407b4ec4ed3adebb98122b59a13b27470ba1a27227b5d688b0`
- Pangaea: `57b9c4b62250383897224b438c1e00360406d71c03cdc1a38724295f33eabb44`

The next purchase fixture can use a transparently labelled viable +3 site or
an earlier genuinely +4 opportunity; do not rename either discovered lead a
strong site to force a demonstration. A discriminating native comparison is
also still needed for the future-host policy. Capture actual Treasury and
Economic's accounted balance/accounts alongside the quote; the
[savings mechanism](civ6-economic-plot-savings-20261111.md) is now traced statically.

## Bounded positive frontier candidate and Szeged comparison

The next candidate shares one `suppliedSite` evaluator between owned and
unowned footprints. Frontier eligibility requires revealed unowned geometry
beside own land, known viable owned Base supply, no covered/protected material,
an evidenced mapped host or actor-permitted future footprint, and a positive
UI quote for an unambiguous proposing-city buyer. A missing, declined or
competing equal/cheaper quote suppresses the positive candidate without
creating a penalty. Existing conservative frontier deductions remain separate.

For each city/profile, publish at most one positive frontier candidate alongside
the existing owned offer. Rank by projected adjacency, pending links, working
Base and material counts; price breaks otherwise equal candidates, then plot
index makes ties stable. Use the same +24 utility band below +4 and +48 at +4
as owned sites. These are bounded early-score preferences, not purchase orders.
The actual Treasury and earmarked funds are deliberately **not** eligibility
gates: the native contract can retain the target and save. They remain required
test observations. This first frontier increment does not nominate an advance
customer build or acquire a separate unowned supplier.

The read-only quote bridge is in `CSC_AdjacencyUI.lua`. The publisher logs
`CSC_AI_FRONTIER_OFFER` only for entries retained in the committed packet, with
its version and exact identity. On the next boundary it reads the previous
packet's exact-pair CE receipt before the counters reset. Readback is capped
at 32 frontier entries per publication and explicitly reports omissions.
Publication, native score consumption, selection, request and acquisition are
still distinct stages. The policy re-reads ownership/supply/quote each packet;
only city-to-plot geometry and loaded type definitions are cached.

### Matched test design

The source-identified Szeged case reuses `nicopolis_replay.py`'s exclusive
controller, package pins and native observers. It now stages exactly the two
main AI files and their quote bridge, preserving the frozen carrier's unrelated
content. The treatment is main CSC source. The control changes one condition
in the staged scanner to omit only player 2 / city 589829 / Tailors 37 / plot
1365 from the positive frontier path. All other frontier offers, owned bids,
material protection and weak-site deductions remain active in both arms.
This ablation is diagnostic code outside the shipped policy.

Before advancing, the fixture verifies the exact saved city/name/plots and
quotes plot 1365 across every Hungarian city. It requires the proposing city
to have the uniquely cheapest positive quote and sufficient source Treasury;
ties, a cheaper other buyer or insufficient bank stop the fixture. That
current-cash preflight is not a production policy veto. Subsequent native
receipts still determine the real buyer and price at execution.

Start with an Online turn-208 endpoint. Observe exact CE receipts, native
district checks and retained trees, comparison, requests and purchase attempts,
then command/debit/ownership and foundation if reached. Continue a concrete
accepted request rather than treating an unconsumed offer as follow-through.
The intended claim is a credible +3 Quarter footprint and own-funds acquisition;
Szeged's later-stage prospective neighbor does not establish a Stage 2 Harbor
Service. Supplier buying remains a separate open branch of 1.5.

### Szeged preflight stopped on tied city quotes

The szeged-frontier-control-01 run loaded the pinned source and stopped before
autoplay or native observer attachment. Its six UI quotes for plot 1365 were:

| City | City ID | Quote, Gold |
| --- | ---: | ---: |
| Buda | 65536 | -1 |
| Esztergom | 131073 | -1 |
| Szekesfehervar | 196610 | -1 |
| Miskolc | 262147 | -1 |
| Debrecen | 524292 | 85 |
| Szeged | 589829 | 85 |

The fixture rejected the ambiguous buyer as designed. It advanced zero turns
and the shared controller verified exit zero, restoration of preferences,
absence of owned processes and exact package retirement. This is a failed
fixture qualification, not a native purchase failure or completed control arm.
The raw quotes and Lua assertion survive in its command journal and failure
record. The assertion occurred before the new bank qualification read.

Debrecen appeared first in the UI enumeration. We did **not** observe native
purchase tie order or a Debrecen acquisition in this run. The targeted native
buyer retains its first cheapest quote, so the proposing city is not guaranteed.
The earlier Debrecen alternative is also not a persuasive purchase fixture:
its owned Bakers plot 1143 already has a +4 projection and +48 offer, versus
+3 frontier sites at 130 Gold. Do not force the weaker paid option to obtain
a purchase demonstration.

### Native ownership dependency

Ghidra identity was rechecked as Windows XP2 reference
324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c,
whose file-backed text matches patched Steam XP2 092abfbb.

| Boundary | Verified behavior |
| --- | --- |
| Shipped Build City District XML, node 5 | Purchase Plot binds Location and Contract; optional Required City is not bound |
| XML node 6 | Reserve Plot receives the original City explicitly |
| PurchasePlotNode Update 55ed80 | Matching player ownership can satisfy the node |
| ReservePlotNode Update 55ef10 | Calls the original city's CityBuild reservation |
| TryReservePlot 3ea040, comparison 3ea090–3ea099 | Requires the plot's purchase-city ID (CityAttributes+0xc) to match City+0xa8; mismatch returns -1 |
| BUILD CanStart 6831e0 → CanZone f9d50 → placement 25a360 | Normal ownership checks also reject a different owning city |
| SwapTileOwner Start 682740 → SwapPlotFromCity 11d590 | Separate validated swap/annex route, absent from the inspected district tree/path |

This is a direct ownership dependency, not proof that AI never swaps by any
other indirect command route. No live wrong-city purchase was demonstrated.
Astra independently checked these functions and the shipped bindings.
The captured static evidence is under
Desktop/Codex/csc-ai-problems-1-2-20261110/purchase-city-lineage-static-20261111/.

The production candidate now rejects tied/cheaper competing buyers. Failed
reads of another city's quote remain unknown rather than evidence of no
competition. The bounded first implementation scans current city quotes for
promising frontier candidates and has no long-lived quote cache. It still
does not check Treasury. **Publication-time uniqueness is not a durable
buyer guarantee:** prices and city state can change while a retained native
contract waits, and withdrawing a score preference does not cancel it.
Overlapping buyers and execution-time buyer binding remain open under 1.5.

### Next native interface investigation

The intended extension is a contract-specific required buyer, preserving
native quotes, savings, payment and annexation. First trace an initialized
purchase contract to its originating district tree and city. Control IDs
are not city IDs: AddToAiControl creates a new tree controller. GetMyCities
can return none or several and its normal implementation can allocate, so
do not call it from a supposedly read-only probe as a shortcut.

The reviewed probe adds two read-only boundaries: CheckForDistrict 3e10fd
links CityBuild to its new tree, and post-Initialize 55dc9f links that tree
to the contract. The existing savings receipt at 45918f matches only a
previously observed contract's exact target pointer and revalidates its ID,
owner control, player and coordinates. An unobserved/reloaded lineage remains
unknown; initialization is still distinct from submission or acceptance.
The known Nicopolis 200–206 replay can qualify this link despite its cash
shortfall. No buyer override has been implemented.

### Verified fresh contract lineage

The nicopolis-purchase-lineage-01 replay completed 200→206 with normal exit
zero, preference restoration, no owned processes and exact package retirement.
Its optional new hooks were read-only; the main CSC policy ran from the staged
scanner, publisher and quote bridge. Both native traces had no fault.

| Native turn / boundary | Receipt |
| --- | --- |
| 203, district-tree installation | Player 1, Nicopolis city 524295, tree 60686355, control 60817429 |
| 203, post-initialization | Purchase contract 4333, same control/tree, target 401, origin city 524295 |
| 203, behavior-tree log | Purchase 31 5: Accepted on #4333 |
| 204 and 205, targeted savings | Exact observed contract target pointer, revalidated contract 4333 and originating city 524295 |

All **24 purchase receipts** exactly match their streamed journal. Removing
the two creation records and the added lineage fields leaves the same 22
receipts as AI-C144. The district-selector record is identical too. Bank and
savings values reproduce AI-C144; the site was not bought or founded.
Here "the site" is target 401. Nearby 398 became Nicopolis-owned by an
unresolved route; it is not a measured paid purchase.
A known contract with an unobserved tree is separately tested: contract
identity can be known while originCity remains null. Unknown XY pointers
and stale identities never fabricate city provenance.

These results establish the city→tree→contract→attempt link for a fresh
plan. Initialization alone is not submission or acceptance; the separate
behavior log and later native attempts supply those stages here. Reloaded
contracts and execution-time buyer constraints remain unimplemented.

Artifact SHA-256:

| File | SHA-256 |
| --- | --- |
| Scanner | c1a3525a7e492e7e3baf55bdc87005eedfc28e98c7181d25e3b0cc416478e496 |
| Publisher | ef7440c08fbcc9b4dba5b1a0152098895aea33bdfa5cbc5e060ab5fdb28c46ca |
| Quote bridge | 0c7b20c3489523f3b6610107dd89c8245afd4708553c74792864db1c3757830c |
| Native observer | 3184f001bacb208ff4d42fc9ea536b3213d8c3c522edbe99b0bb6d863ca77354 |
| Purchase trace | a865d62c911157e41fca8308e041e3c396e739335d339130021da04b11a5bd84 |

### Positive frontier offers reached native consumers

The same replay provides bounded delivery evidence for the new main-mod
frontier adapter. Nine exact-pair CE receipts across three pairs reported
staging; eight reported a score attempt/write and an eligible cache read.
The summed citySelections counter was two, with zero site wins; one selector
can read more than one tracked pair. The remaining
receipt had a cache read but an ineligible pair and no score attempt/write.
No frontier readback omissions or placement/publication exceptions were logged.

The pairs were player 3 / city 393221 / Bakers 36 / plot 1011, and player 3 /
city 458758 / plot 862 for Bakers 36 and Tailors 37. Offers used the +24
utility band and observed quotes. These are per-publication counters, not
nine distinct sites or eight purchases. They establish consumption and native
score changes, not causal selection, acquisition, foundation or quality
improvement. No positive-offer ablation comparison has completed yet.
Astra independently verified the lineage, stream equality, native acceptance,
artifact hashes, cleanup and summed frontier receipts.

### Buyer prototype still to test

The next controlled comparison should keep the exact Szeged offer and its
diagnostic quote-screen bypass identical, then compare native buyer selection
with and without a contract-specific restriction. Merely disabling the offer
under the same restriction would test a different question. Before any quote
mutation, bind the selected Quarter/site to tree installation in the same
CheckForDistrict invocation (thread, CityBuild and frame), then to the exact
contract. A scoped quote-return prototype can reject other buyers while
preserving the intended city's price, savings and normal command.

This is a diagnostic, not a shipping CE capability. The tool now implements
explicit observe/restrict modes. Both stage the same player/city/plot-specific
UI quote-screen bypass; the native restriction additionally requires selected
Tailors district 37 and its exact contract lineage. Production CSC's quote
screen remains conservative.

The selector result is replaced or invalidated on every result, then consumed
on tree installation only with matching thread, CityBuild, frame and turn.
The known contract is revalidated before each optional quote exclusion.
Missing, mismatched or stale provenance cannot authorize a register write.
Native prices, funds checks and command/payment paths remain in place.
The synthetic matrix covers intended/other buyer, nonpositive quote, disabled
mode, wrong district/target/city, missing/failed/replaced selection, mismatched
frame/build/thread, unknown target pointer, stale contract fields and record
capacity before mutation. A later fault invalidates a run; it cannot undo
earlier exclusions.

The first two observe attempts stopped before autoplay and closed normally:
01 exposed a diagnostic context mismatch (UI uses GetCurrentProductionTypeHash,
not Gameplay's CurrentlyBuilding); 02 exposed our first observer's patch in
the second observer's original-byte guard. Optional metadata is now non-fatal.
The selector observer first verifies the original full 16-byte call/return
window. Only after its successful initialization does the second observer
accept that same attachment's proof and verify the untouched call plus XY
initialization. An observe run must still prove both listeners receive the
same live selection before restriction is enabled.

Payment, intended-city ownership and actual foundation still require live
evidence. CE integration then needs lifecycle, cancellation and reload behavior
reviewed with Henno before any upstream PR.

### Szeged observer coexistence passed; active treatment was not established

The szeged-buyer-observe-03 replay completed 200→208 and closed normally:
native exit zero, no owned processes, verified preferences and exact package
retirement. Both native traces were fault-free. Their streams exactly match
the two purchase-observer records and ten selector-observer records. Both
listeners at the shared return point saw turn 205's district 10 at plot 1360;
the native city-build log identifies the resulting request as Neighborhood.
The purchase observer also linked that selection to tree 50135054 and control
50266128. This qualifies listener coexistence and same-invocation provenance.

Tailors at unowned 1365 had a cached value of 173,875 Q8; the winning pair had
277,389 Q8. No purchase contract or buyer quote for the target was observed,
and it remained unowned and empty at 208. **This is not an active-offer loss:**
the run has no successful publisher/frontier logs, and its watcher found no
initialized Cotton Base tag. The earlier discovery initialized its model
explicitly, whereas this watcher relies on normal publisher initialization.

The publisher initializes the model after its UI, CE and original-seat safety
gates. The source baseline's archived turn-1 identity check explicitly required
the original-human properties to be absent, because tuning was disabled there.
That provides the original-identity provenance for a controlled migration.
Do not infer original identities from current autoplay IsHuman or relax the
production safety gate. The next replay now captures every gate and requires
an enabled, versioned production packet before autoplay. A restricted-buyer arm
must wait for a real target contract; increasing bids solely to exercise the
hook would be a separate artificial diagnostic, not worthwhile acquisition.

Astra independently verified both streams, selection/tree identities and
cleanup, and identified the missing publication evidence. This does not close
Problem 1.5 or validate any native buyer restriction.

The zero-turn szeged-policy-gate-01 confirmed bridge availability and
single-player mode, with native ready=1, enabled=0, version=0 and faults=0.
The absent-property logging call itself failed: this native GetProperty can
return zero Lua values, so tostring(Game:GetProperty(...)) may call tostring
without an argument. Assigning the result to a local first records nil safely.
The run stopped before autoplay and cleanup verified. Its failure receipt
retains the partial gate output; it has no complete policy-qualification JSON.

The explicit --seed-source-seats diagnostic pins source.json, protocol,
checkpoint and acknowledged turn-1 identity command/reply hashes. Its staged
publisher prelude validates turn 200, all six recorded leader/seat identities,
current controllers and every existing property before any write. Only missing
properties are populated from archived original identities; matching values
survive and conflicts abort. Production source and its late-load safety gate
remain unchanged. Both buyer arms must stage identical migration bytes.
Tests execute the Lua for zero-return reads, conflicting final-seat metadata,
wrong leader/controller/turn, matching values and repeated execution. Astra
independently verified the provenance hashes and reviewed the migration.
The migrated observe04 must qualify a published packet and the exact target
offer; the earlier observe03 cannot serve as its matched policy control.

### Artifact identities

| World | Save SHA-256 | Survey SHA-256 |
| --- | --- | --- |
| Continents | `e333251ec7318fb6b170678a956c28e02e2f9b01c4c4753c99e84b1a112fe19a` | `f7a4ab0b54936a22480ca1c03c6c675b10c0f554d4d29041480c2b5c3b61c549` |
| Pangaea | `efa19eeaf9ed4312f548d18500cb67e9ae77cf3d6af8be33efd653621e25f980` | `fb665c323ce0babff54f56c93a07543ad2de400fc7120a6c1720cb3768ed46e2` |
| Fractal | `c50976621de17e38f998fad916b22a1bd219f4cdc9af508d90b8846d011fbf91` | `cb4f1feff4fdeca59f10128c62216031c472a98bd3c46a4f7e75f15b9e661392` |
