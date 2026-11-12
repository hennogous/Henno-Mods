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

## Predeclared causal control, held pending measured payment

Astra recommends withholding positive Bakers **and Tailors** frontier offers
for exactly player3/city458758/plot788. The intervention unit is one footprint's
CSC positive acquisition guidance, not either Quarter's individual bid. Preserve
native prices, savings, legality, deductions, other sites and ordinary bands.
Assert the affected profiles. A Bakers-only control could leave the same land
actively promoted by Tailors and answer a narrower question.

The staged control now withholds both profile IDs 36 and 37 at this footprint;
the main CSC sources are unchanged. An isolated Lua predicate check verifies
that other players, cities, districts and sites remain outside the exclusion.
Do not launch that control until the full arm's native payment is measured.
If both matched arms buy788, preserve that result; do not broaden the intervention
afterward merely to manufacture acquisition causality. Supplier acquisition and
improvement are still separate unresolved work.

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
