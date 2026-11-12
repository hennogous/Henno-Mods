# Nuremberg: from a worthwhile frontier offer to paid acquisition

Active **Problem 1.5**, after the independently accepted 1.1–1.4 scopes.

**Acceptance:** ordinary main CSC guidance changes a relevant native acquisition
decision/action and reaches native payment, ownership by the intended city and
Quarter foundation. The separate supplier route must reach acquisition and
improvement too. A quote, request, savings check or unexplained ownership change
does not close this item. Astra validates each completed scope.

## Why this existing case

The earlier Continents comparison identified newly founded Nuremberg,
player3/city458758, City Center787 and worthwhile owned Bakers site788. Existing
frontier862 was inferior to free788, so buying862 was not justified by the
observed alternatives. Astra approved qualifying a controlled release of788,
not inflating a bid or forcing an inferior purchase. The old quote85 was for862,
not788. The old rotating202 autosave was not accepted as an inactive source.

`nuremberg-paused-source-01` replayed the exact verified Continents200 source
to inactive202 using all four current main AI modules and the UI bridge.
It saved once with SaveComplete and unchanged human0 phase, then closed normally
with exit0 and verified preference/package restoration. SHA-256:
`bb95dc3a33c423bc6b4231eb862819bbc2d3faba895b62a88aec3d7934401894`.
The ancestry starts at the maintained turn200 source
`e333251ec7318fb6b170678a956c28e02e2f9b01c4c4753c99e84b1a112fe19a`.

Current main policy gives788 +12,288 Q8 at projected adjacency4: counted Base
Production2, City Center Gold1 and one feasible future customer Gold1 at713.
There is one viable supplier, Flax861, ready but unimproved; the City Center's
Flax787 is counted adjacency, not another improvable supplier. Both Mill unlocks
are known. Nuremberg is population1 with no zoned specialty district, producing
Walls. No Nuremberg joint district winner is recorded before the202 boundary;
that absence does not substitute for the later fresh-comparison receipt.

## One common release, no payment or subsidy

`nuremberg-released-source-01` reloads that verified inactive source and first
qualifies active main policy. It clears only empty788 through
`WorldBuilder.CityManager():SetPlotOwner(x,y,false)`. Native inspection confirms
the boolean keeps the wrapper's invalid CityID, and the manager permits clearing
an empty district plot. This is explicit diagnostic preparation, never an AI
purchase. Terrain3, feature3 (Floodplains), river count0, resources and improvement
state remain unchanged. No treasury or research change is supplied.

Fresh readback finds788 genuinely unowned, with no purchasing city. Seven new
UI quotes give **40 Gold for Nuremberg and−1 for every other German city**.
Treasury remains **942.6484375 Gold**. The model still gives4 with the retained
Flax861 and future713. Those are bank and quote facts, not usable native savings.

The common inactive202 derivative is saved once with SaveComplete, unchanged
human0 phase and matching archive/native bytes, SHA-256
`d579ecc2c54909f1b21aaa96caad237daeb9fc0f67cd78c8602191c70c2a9026`.
The zero-turn creation run closes normally with restoration verified.

## Pilot: request and sufficient savings, unexplained ownership

`nuremberg-purchase-full-01` runs current main CSC policy202→208. Its selector
and purchase observers are read-only; they add no bid, command, funds or owner.
The session closes normally, both native traces have no fault and the measured-
debit observer has no pending unmatched call at freeze.

| Boundary | Observed evidence |
| --- | --- |
| 202 | Native Bakers selection/request and new district tree59244585/control59375659 |
| 202 | Purchase contract4316, target788, same tree/control and origin city458758 |
| 203 | Seven native Economic quotes; Nuremberg40, all others−1 |
| 203 | Plot account150 Gold, slush119183/256 Gold; both native savings predicates pass |
| 203 | Actual treasury196668/256 Gold, accounted balance identical; weights[3,4,1,1], total9 |
| Snapshots202/203 | Target unowned and empty |
| Snapshots204–208 | Target owned by player3, purchasing city458758, district−1 |

The savings factor is64 Q8 (one quarter), so the required earmarked plot amount
is2,560 Q8 =10 Gold for the40-Gold quote. The combined funds also suffice.
These predicates reconstruct the next native comparisons; they do not prove
command admission. The native purchase request is separately accepted in the
behavior log. At207 its decorator still reports waiting5 of10 turns, and Walls
remain in production at208. There is no Quarter foundation.

**Critical limit:** no plot command quote, debit or annex callback fired, despite
the later correct-city ownership. Existing debit-return fields historically
recorded only a preserved argument; the new observer measures actual Treasury
before/after at the same callbacks, but those callbacks did not execute here.
Payment is **unproved**, and ownership could have another source. Do not call
this a successful paid purchase or infer a40-Gold debit from the quote.

## Native command permission and focused repeat

On Windows XP2 reference SHA
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`,
whose file-backed text matches current Steam XP2
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`:

- `GetPlotPurchaseCost`121170 checks maximum distance, unowned target and an
  adjacent plot owned by the player. It has no minimum-distance condition and
  is not complete command permission.
- `Economic::TryPurchasePlot`459090 applies quote and savings gates, constructs
  a request through6808c0, checks Manager.CanStart and dispatches Manager.Start.
- `Manager::CanStart`13560 requires the player's turn-active byte288 and allowed
  strategic phase for an immediate request, then the handler's permission.
  Lua `IPlayer::IsTurnActive`6ee350 reads the same byte.
- `Purchase::CanStart`6803c0 additionally checks plot-buying capability and
  `City::Gold::CanPurchasePlots`120e00. `Purchase::Start`680f70 recalculates the
  quote, checks affordability, debits through3432e0 and annexes through11b100.

Astra independently verified that RDI really is the City at the existing
purchase callbacks; a statically wrong city-register filter does not explain
their absence. The next **same-source202→204** read-only repeat adds receipts at
4591f3 (request-built AL),45921f (command-admitted AL) and459241 (Start returned,
**not** a success Boolean). Culture Annex and plot-owner setter callers identify
the acquisition route. Turn-active is read, never changed. This directly
addresses the missing payment provenance; no new world or policy arm is needed.

The observer's measured-debit pairs validate thread, caller stack, city pointer,
Treasury receiver and preserved argument. Missing returns/identity mismatches
fail observation. An actual measured delta mismatch remains explicit; synchronous
notifications can affect the interval. Node fixtures cover those boundaries,
interleaving, partial returns, admission's AL semantics, caller scope and detach.

## Execution repeat: the expansion handler was missing from observation

`nuremberg-purchase-execution-01` repeats the same source 202–204 and closes
normally with verified restoration. Both request construction and command
admission return true at 203; the player's turn-active byte is true. The target
becomes owned by player 3 / city 458758, with no district at 204. No funds or
ownership are written by either observer.

The Culture Annex callback's caller RVA is **71c69a**, inside
`XP1::Purchase::Start` at **71c3b0**, rather than the base `Purchase::Start`
at 680f70. The original paid-branch observer covered only the base implementation.
Its silence was a coverage failure, not evidence of a free acquisition or a
permission failure. Actual payment is still unmeasured in this repeat.

Astra independently verifies the expansion branch: quote return 71c63e,
debit call 71c671, debit return 71c676 and annex return 71c69a. RDI is City;
target XY is RBP+38/+3c, Treasury is R15 and the preserved negative Q8 debit
is EBX. The command reprices, checks affordability, changes Treasury and
annexes in that order. Static call order alone does not measure the bank debit.

The observer now shares guarded measurement logic across separate base/XP1
descriptors, fingerprints both implementations and tags receipts by handler.
Synthetic XP1 cases cover decoding, failed reads, incomplete/mismatched pairs,
cross-handler returns and distinct frame/register layouts. The next full arm
uses those read-only callbacks and preserves an inactive endpoint through the
shared save helper. It retains the same policy, price and common released source.

Henno requested preserving the finished repeat. Its rotating 204 autosave was
copied byte-for-byte to `Henno_Preserved_Nuremberg_T204_20261112.Civ6Save` and
a separate `Desktop/Codex/csc-ai-preserve-nuremberg-20261112` backup. All hashes
match `819d36af685d313d1a3d089bc0cf923991972b1a25aadd20547bdc55fcfcc39f`.
This preserved autosave is not silently promoted to an inactive replay source.

## Measured full arm: paid acquisition, failed foundation

`nuremberg-purchase-paid-full-01` completes 202–216 and closes normally:
exit 0, owners absent, preferences restored and packages retired. The terminal
traces match all streamed records exactly: 36 purchase and 18 selector records,
no faults and no pending debit/execution callbacks. The
[sealed full-arm capsule](csc-ai-nuremberg-acquisition-20261112-full.json)
preserves the relevant native records, complete first city/site matrix, ownership
timeline, endpoint receipt and hashes of the underlying artifacts.

At 202 the native selection is Bakers 788 at **286,075 Q8** (1,117 whole utility
points in the request log), followed by purchase contract 4316. At 203 the
expanded observer measures the XP1 handler's **40-Gold payment**:

| Measurement | Q8 Gold | Gold |
| --- | ---: | ---: |
| Treasury immediately before debit | 196,668 | 768.234375 |
| Treasury immediately after debit | 186,428 | 728.234375 |
| Measured difference | −10,240 | −40 |

The signed debit argument matches that measured difference. Handler, thread,
caller stack, city identity, Treasury receiver, target and turn match across
the pair. Annex returns from XP1 and physical snapshots show player 3 /
purchasing city 458758 from 204 through 216. The observer also measures other
ordinary paid plots for the same player; its positive coverage is no longer
limited to the targeted attempt.

**The Quarter does not reach foundation.** Purchase contract 4316 remains
waiting through 10/10 at 212 and the tree fails at 213. At 214 the next native
district selection is Campus (46,10), 485,797 Q8. Plot 788 remains district −1
through 216. Production moves from Ancient to Medieval Walls during the window.
Do not explain this as merely losing the final production auction: the purchase
node did not release its already-paid prerequisite to the reservation/build path.
Its completion lifecycle is the next unresolved foundation dependency.

The shared controller saves a verified inactive human-0 endpoint at 216,
`CSC_PURCHASE_FOLLOWTHROUGH_3ff4c61621fb.Civ6Save`, SHA-256
`2d567261de7ba582dded065ab5f6d039639ad990200f3ad6206e3b422f51421c`.
SaveComplete, unchanged native phase and archive/native equality are verified.

This establishes a paid acquisition following ordinary integrated guidance.
It does not yet establish that guidance caused acquisition, nor close 1.5:
the matched control, foundation and separate supplier route remain required.

## Predeclared causal control

Astra recommends withholding positive Bakers **and Tailors** frontier offers
for exactly player3/city458758/plot788. The intervention unit is one footprint's
CSC positive acquisition guidance, not either Quarter's individual bid. Preserve
native prices, savings, legality, deductions, other sites and ordinary bands.
Assert the affected profiles. A Bakers-only control could leave the same land
actively promoted by Tailors and answer a narrower question.

The staged control now withholds both profile IDs 36 and 37 at this footprint;
the main CSC sources are unchanged. An isolated Lua predicate check verifies
that other players, cities, districts and sites remain outside the exclusion.
The measured full arm qualifies launching the same-source 202–204 control.
Both arms use identical expanded observer coverage. The exclusion removes the
footprint from positive candidate selection: a different frontier fallback or
deferral outcome can follow. Audit these consequences rather than promising
that exactly two final packet entries disappear.
If both matched arms buy788, preserve that result; do not broaden the intervention
afterward merely to manufacture acquisition causality. Supplier acquisition and
improvement are still separate unresolved work.

### Matched result: Quarter identity changes, acquisition does not

`nuremberg-purchase-paid-control-01` closes normally after 202–204 with a verified
inactive endpoint. Both traces exactly match their streams, with no faults or
pending callbacks. The package manifests differ only in the scanner's exact
declared footprint exclusion; source bytes reproduce that transformation.
The [sealed comparison](csc-ai-nuremberg-acquisition-20261112-control.json)
preserves the audit, native differences and file hashes.

| First native comparison / outcome | Main full arm | Footprint-offer control |
| --- | --- | --- |
| Bakers score at 788 | 286,075 Q8 | 273,787 Q8 |
| Winning Quarter at 788 | Bakers, 286,075 Q8 | Tailors, 277,289 Q8 |
| Native payment at 203 | 40 Gold | 40 Gold |
| Ownership at 204 | Nuremberg | Nuremberg |
| District at 204 | None | None |

Of 36 Bakers city/site rows, 35 are byte-for-field identical; only 788 loses
12,288 Q8. Main placement bids fall 27→25 and total packet entries 502→500.
Weak-site count 261 and customer count 0 match. Builder allowances remain 20,
building nominations 1 (same preview), repairs 0 and exclusions 20. These
counts do not establish equality of every other packet entry; this is a full
local Bakers matrix comparison, not the complete all-player CE packet audit
used for the earlier Liverpool tests.

**Negative for acquisition causality:** without CSC's positive candidates for
this footprint, native Tailors still wants the same land and pays the same
40 Gold. The guidance demonstrably changes Quarter identity, but necessity
for buying this tile is not shown. Keep this declared result; do not broaden
the exclusion after seeing it to manufacture a purchase difference.

The remaining immediate issue is the full arm's purchase contract completion.
Static inspection suggests that Economic can remove a newly ineligible local
handle after ownership while the tree still retains a waiting contract. This
is a hypothesis, not yet an engine-defect finding. A read-only 202–205 repeat
records actual contract status/vtable and dispatch, the two Economic eligibility
returns and the decorator's retained status. Inactive 204 stops before AI turn
204; endpoint 205 is needed to observe that post-purchase processing. Unknown
contracts are ignored, known ones are revalidated, and no state is changed.
Neither eligibility rejection nor decorator observation is labelled completed
vector removal or destruction.

### Lifecycle result: paid, ineligible, still waiting

`nuremberg-purchase-lifecycle-01` completes 202–205 with normal closure,
verified restoration and exact stream agreement: 27 purchase / 5 selector
records, no faults or unresolved callback pairs. The
[sealed lifecycle capsule](csc-ai-nuremberg-acquisition-20261112-lifecycle.json)
preserves native state/dispatch records and their source hashes.

The actual contract vtable is **9fa930**, with Execute thunk **3f82c0**,
Update **3fa260** and eligibility thunk **3fa880**. This confirms the class
used in the static lifecycle trace rather than assuming it from mapped names.

| Native boundary | Turn | Contract state / result |
| --- | ---: | --- |
| Purchase contract created | 202 | State 1 |
| Economic eligibility, compaction pass | 203 | True, state 3 |
| Paid purchase command returns | 203 | State 3; measured −40 Gold |
| Construction decorator reads contract | 203 | State 3, waiting |
| Economic eligibility, compaction pass | 204 | False, state 3 |
| Construction decorator reads retained contract | 204 | State 3, waiting |

Both eligibility midpoints, 457515 and 45755f, return from vtable+80;
they are **not** the ownership-only Update call. False selects the native
removal branch. The decorator at 55a056 still resolves the same ID/control/
player/target, then reads state 3. It does not execute the Purchase Plot child
while that retained contract blocks it. A READY child log is not evidence
that its owner check ran. These observations explain the specific waiting
path behind the full arm's timeout; final vector compaction/destruction was
not separately observed.

At inactive 205 the plot is still empty and owned by Nuremberg. Its verified
paused save SHA is
`6977d48d856ea1f08f8f1876371898495a3e182d9b8d7cffbee0de09fdab1a03`.
The next implementation question is how to acknowledge completed acquisition
through a normal native lifecycle operation, scoped dynamically to CSC's plans.
No contract status was written in this probe, and no repair is yet integrated.
Do not generalize this controlled release case to every natural purchase.

### Controlled acknowledgement prototype

The next experiment leaves the shared source, main policy, native prices and
production values unchanged. At the decorator's existing status read, it may
acknowledge only the observed purchase after verifying the current intended
city owns the target. It uses the native completion idiom demonstrated by
BuildingCreated 3f81d0 / DistrictCreated 3f8210: tracked assignment 64a6d0 of
int32 state 7 through `contract+a0`. It never writes `contract+b0` directly,
removes a handle, reserves land or issues a build command.

**Acceptance for this diagnostic:** the ordinary decorator consumes that
acknowledgement, submits the native Quarter request and reaches a physical
foundation through 216, compared with the unchanged full arm's timeout.
An acknowledged state alone does not prove any of the downstream steps.
Even a positive result is not level-3 integration or acquisition causality.

`nuremberg-purchase-acknowledgement-01` is a failed tooling attempt, not a
construction comparison. Its owner decoder requested unsupported `i8`; the
shared memory adapter rejected the read before tracked assignment. The native
trace is faulted and the driver exits unsuccessfully, with normal game exit
and restoration verified. No completion receipt or contract write is claimed.

The corrected `-02` prototype reads supported `u8` and converts the signed
owner explicitly. Its synthetic reader now enforces the real adapter's type
vocabulary. It also rejects null game/map pointers, binds the debit to the
admitted request's thread/contract/pointer/control/root identities, and reserves
intent/outcome journal space before any assignment. Capacity exhaustion and
interleaved receipt cases are covered by fixtures. An outcome reservation
survives ordinary callbacks; a post-write failure remains explicitly unverified.

At the same pre-write boundary it records the executing tree's district,
city and plot, then compares them with the independently observed creation
binding. R14 is the **executing** BehaviorTree: analysis district is +29c,
City pointer +2f0 and Plot pointer +308. Root IDs require a bounded parent+120
walk; root analysis is not substituted for the current trigger. Missing or
inconsistent identity prevents acknowledgement.

These checks test the identity path proposed for a later generic CE capability.
The proposed shipping scope would be numeric player/city/district allowances
published dynamically by main CSC, with current native tree/ownership validation.
Its receipt would mean ownership prerequisite fulfilled, not paid purchase:
cultural acquisition can legitimately satisfy ownership too. Runtime reload
reconstruction and the CE/main adapter are not yet implemented or qualified.

## Operational scope

The same CE f812 and current DX11 binary identity used in the accepted placement
cases apply. WildW develop remains2986a746b396eb93aad14f9afffb043a09c2c489
when checked before this campaign. No upstream PR or CE binary change is made.
Shared controller owns all live access. Main-mod AI modules are integrated;
large saves and trace packages stay in the Desktop evidence store.

Pinned existing Frida17.24.3 is at
`Desktop/Codex/csc-ce-ai-tooling-probe-20261028/dependencies`. Reuse it; do not
reinstall merely because default Python cannot import it. The maintained replay
now records dependency root/version and source turn in its input manifest.
