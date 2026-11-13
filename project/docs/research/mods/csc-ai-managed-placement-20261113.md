# Managed Quarter delivery and quality candidate - 13 November 2026

**Current status:** corrected footprint candidate passes243 native checks and
Astra's final source review; replay04 completes175 and passes delivery
qualification. It does not establish construction or sustained benefit. Its Release02
DLL SHA256 is400e675522916ce54a17a6765132da89ee23c90304a89e721c6289c31327394f.
Use frozen03/candidate-packages03.json. Earlier packages, preliminary observations
and failed qualifications below are historical evidence, not current acceptance.
The fresh ordinary Online250 game is now running through the shared controller;
main CSC policy and the pinned CE fork are the only tuning code.

## Question and acceptance

Problems **1.6/1.8**, preserving **2.2**: does CSC's complete Quarter value reach
all relevant new-investment consumers, including reserved sites and requests
that retained an older price? Then, does an ordinary game place fewer weak
Quarters and more worthwhile ones? Henno prioritises output quality over a neat
architecture, provided performance remains acceptable. No upstream PR is made.

The first acceptance is real consumed values, not receipt counts alone. A short
shared-controller replay of the recorded150 checkpoint must show the managed
values at native decisions, healthy APIs, retained-request reductions where
encountered, and clean closure. Only then start a fresh normal Online250 game.
Offline tests do not establish real ABI, timing, placement or Service outcomes.

## What the actual updated binary does

REA/Ghidra rechecked the installed Steam XP2 image:
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
The complete32-record evidence bundle is
`Desktop/Codex/csc-ai-placement-coverage-20261113/rea-current-consumers.json`.
It includes the current functions and relevant assembly; addresses below are
RVAs on that exact image.

| Consumer | Verified meaning | Integration consequence |
|---|---|---|
| GetBestDistrict3e4a50 | Can compare live reserved cells and can choose negative values above its invalid floor. | Refresh before comparison; leave reservation thresholds native; mask nonpositive new managed investments transiently. |
| GetDistrictLocation3e5550 | Existing pillaged district returns its own footprint; new locations skip live reservations. | Preserve its distinct reservation rule and repair branch; refresh new-site values and apply supplier exclusions. |
| PresentValueOf3e7f40 | Reads a specific cell; null Plot means maximum of the column with zero floor. No new forecast aggregation here. | Refresh immediately before the read; distinguish a locationless value from a site. |
| UnitRequestContract.Update3fa5e0 | Building+190 and unit+178 precede district+1a8. District bid becomes max(stored+158,current); return success is AL bool. | Successful managed new-Quarter requests need a separate downward rebase after normal validation/ETA. A cache reduction alone is insufficient. |
| Tracked assignment2ca0f0 | RCX wrapper, RDX int pointer; marks tracked owner and stores wrapper+10. Incoming R8 is overwritten before use. | Use native tracked assignment on request+148 rather than a raw+158 store. No guessed third argument. |
| District count11ec40 | Count(type,onlyComplete,includeReplacements); no pillage exclusion. | Locationless repricing excludes existing Quarters/foundations/repairs using false,true. |
| CheckForDistrict3e0ee0 | A new district nomination waits for a free district planning slot. | A new packet does not imply a new comparison that turn. |

Additional inspected value consumers include trigger decoding55a680,
production opportunity cost3ea150 and city value480540. They use the same
PresentValue/location accessors; their non-district branches stay native.
The earlier reservation thresholds remain in [AI-C174](../../civ6-ai/findings.md#ai-c174).
The max(old,current) rule was already AI-N023; this investigation rechecks it
on the current image and connects it to the complete-value delivery gap.

## Candidate implementation

Main CSC owns all valuation and normal turn publication. The CE fork owns generic
numeric transport; no CSC names or Quarter economics enter native CE code.

1. Declare each original AI's managed Quarter type with a negative default.
   Publish only fully priced positive site offers. New cities and missing,
   unknown or omitted offers defer rather than inherit native building premiums.
2. Enumerate revealed radius-three owned/purchasable potential, without limiting
   quotes to today's BUILD menu. Native invalid values/eligibility remain final.
3. Count current materials, rivers/local Mill geometry and completed customers.
   Future customer footprints earn no yield. Rank bounded producer alternatives
   on the final placement bid, so Water+2 cannot hide a profitable Wind+3 plan.
4. Defer below+3 or no-Base investments. Only after costs/risks leave positive
   economics, add96/192/288/384 native utility for+3/+4/+5/+6+; both material
   classes add16. These are bounded initial preferences, not measured exact
   vanilla values. They do not guarantee victory over another district/unit.
5. Refresh valid matrix cells after aggregation and before Best, Location and
   PresentValue consumers. Nonempty reservations do not block pricing. Preserve
   invalid cells and existing district footprints. Supplier masks protect both
   placement selectors; native reservations still decide actual admission.
6. Reprice only successful genuine managed new-district requests through the
   tracked setter. Preserve unit/building requests, existing construction/repair,
   coordinates, reservations, ETA and queues. Locationless requests use the
   native zero-floor column value, not a made-up exact-plot bid.
7. At packet capacity, preserve defaults and strongest positive offers alongside
   priority material protection. Omitted sites defer; no wholesale return to
   untouched Quarter premiums merely because a large empire filled the table.

No new purchase order, subsidy, research grant or external test policy is added.

## Review, bounds and offline evidence

Astra's first review found three blockers (Mill alternative choice, request AL
ABI, diagnostic saturation) and additional locationless/masking gaps. All were
fixed. Its second review reports no remaining demonstrated code blocker and
independently reproduces25 Lua economy tests. It requests live performance
measurement and exact evidence scope, retained here.

-235 native checks pass, including20,000 repeated consumer writes beyond the
  legacy write/journal limits; shared Runtime4 failure/cleanup checks and
  instruction-call delivery/restoration also pass.
-25 economy tests pass, including Water+2 versus profitable Wind+3 and+3/+4
  alternatives, unknown invoices, future-owned sites and live Mill multipliers.
-19 frontend/main-script tests pass, including managed staging, rejection,
  sparse no-city defaults and protection-first/highest-positive capacity trim.
-25 observer/full-game result checks pass, including native ordinal/phase,
  reservation and managed-default attribution. Tests that create temporary files
  run with the existing writable Desktop test directory; sandbox temp denial is
  not a code failure.

Managed native work is bounded to37 rows and16 types per player per pass.
No native hook calls Lua; complete packets replace versions atomically. Optional
managed samples cap at2048 and reserve8192 core slots. Dropping a sample increments
managedTraceDropped rather than disabling policy. Managed writes have a separate
counter from the legacy4096 write budget. Core/legacy exhaustion retains its
previous fail-closed behavior. Native processing microseconds measure matrix
passes only, not all masks/requests/Lua; end-to-end refresh timing is also needed.

## Package scope and live qualification

Artifact root: `Desktop/Codex/csc-ai-placement-coverage-20261113`.
CE branch: `codex/quarter-value-delivery`, based on3421b37/6f53037.
Release DLL SHA256:
`91f2830f8596d82d524e9ed6a96886832b8a91bb048143b7e2d79f05966281e2`.
The corrected exact package pins are in candidate-packages02.json (frozen02). The corrected six-file CE carrier and
639-file CSC carrier preserve the previous qualified gameplay snapshot. Only
five main CSC Lua_UI/AI modules and the CE DLL differ. Concurrent unrelated
SQL/art/UI edits in the workspace are excluded, preserving attribution. This
is the integrated main-mod policy in an isolated carrier, not a probe policy.

The source save is turn150 SHA256
`e951c015f0d551946fb2a9ea8275db8d202aa7b9ec1129f61221340b753d48a3`.
Replay150-175-03 uses corrected explicit candidate inputs, verifies archived
originals and candidate save GUIDs, records all changed files, and adds only
read-only placement/consumer observation. That window later failed on the flag; the corrected replay04 is pending.
Earlier failed packages/windows are preserved below.

## Qualification attempts and packaging correction

- **replay150-175-01:** deliberately handed off at165 when qualification showed
  zero positive offers and unavailable Quarter readiness. Nativeexit0, owners
  absent and preferences/packages restored. It is an incomplete diagnostic,
  not a completed175 comparison; final journal is not drained. Reserved/default
  writes were observed, but correct positive bidding was not qualified.
- **replay150-151-facts02:** completed151 and cleanly restored with nativeexit0.
  Read-only facts show positive production and completed Craftsmanship but
  missing UI cost readers, Gameplay cost errors and Quarter readiness=inf.
- **Cause:** the initial candidate used older `frozen`, not the successful run's
  exact package. It omitted the UI economic read bindings (UI SHA2c3c9a93...)
  and recreated the previous fact-boundary problem. Astra independently found
  the omission. This was a packaging error, not a new readiness-model defect.
- **Correction:** `frozen02` is copied from the actual successful250-run archive;
  only the five intended main AI files and CE DLL differ. UI SHA256 is verified
  equal to both archive and current source:
  `49c23e058c6d4e71a40eb3030808dd9da6603af0157ba39c5121edca00b21ab2`.
  Exact pins and allowed differences are in candidate-packages02.json.
- **replay150-175-03:** completed175/clean restoration with the UI fix, but
  failed delivery qualification on the improvement-flag bypass detailed below.
  No bid or gameplay fixture was injected.

Full-game preflight now also rejects missing UI readers, independently of native
API availability, with the missing-dependency regressions passing. Earlier
candidate-packages.json remains preserved as the failed input record; use02.


### Preliminary corrected-package evidence (historical; later failed on the flag)

In replay03, the fact probe restores finite readiness (example Bakers1281,
player1/city65536: Production39.59765625, district cost35, Craftsmanship done,
Quarter readiness1). At151, the five players publish6/6/6/2/0 positive site bids
with zero unavailable quotes. Deferred sites remain sparse defaults.

A drain at153 records a genuine retained Bakers request for player1/c65536,
plot987, packet3/generation8:410368Q8 becomes-262144Q8 through request rebase,
matching its managed default. Existing Tailors2321/player5/c65536 remains native
at371357Q8 with existingDistrict=1. Native reserved-cell writes are nonzero.
One sampled round has82 managed passes and6134 microseconds in matrix refresh;
that is not total policy overhead and does not establish all-eight-Quarter scale.
No new-site winner or improved placement rate is inferred from these events.

CE implementation is committed/pushed as a95e697; reusable engine findings are
in civ6-ai2bdcf6c (AI-N023 recheck and AI-N125). No upstream PR is created.


## Correction: improvement flag is not an existing district

Replay03 completes175 with nativeexit0, restored preferences/packages and a
complete, fault-free observation. It records4 foundations (3below+3) and4
completions (all below+3). It **fails delivery qualification**: Tailors2321 is
marked existingDistrict=1 at native Best, but is founded159 and completed161
with no Base and+0. Tailors2608 is similarly founded165 after the exemption.

The first implementation and review misidentified row+50 as district presence.
Actual evaluator3e2aa0 reads Plot+44 improvement type and writes HasImprovement
at+50. Row+51 is district presence only after completion and nonpillage gates;
switching to51 would mishandle foundations/repairs. The prior paragraph calling
Tailors2321 an existing-district preservation proof is **retracted**. Its unchanged
native value was a bypass. The request reduction itself remains a valid write.

The corrected native code queries the actual city district collection through
the already-used repair getter11e520(city+b58,&xy), which includes unfinished
and pillaged district objects. It applies that guard to managed refresh/masks/
request rebasing and to shared supplier/typed-decline masks whose scopes can
outlive a foundation transition until the next publication. Unknown lookups
preserve native state. Improved empty plots receive the managed value normally.

The full160-byte getter body and5952-byte evaluator body match reference324c51e9
and installed092abfbb exactly. The actual patched evaluator is retained in the
previous34-record REA evidence bundle, record
`ev_550ac784f7e989e39988b332840a330d60c52f53b92f8d29d24a4222b9c3c624`.
Reference annotations identify Plot+44 as improvement type; the independent
live foundation sequence corroborates the error. Current code qualification is
in district-footprint-binary-qualification.json. New independent fixtures cover
improved empty land, foundations before/after improvement removal, pillage and
stale decline/exclusion scopes. A new Release build and replay are required;
a95e697/DLL91f2830f are preserved failed candidates, not qualified delivery.


### Corrected physical-footprint replay04: early exact comparison

CE correction dbfb93b, Release02 DLL400e6755..., frozen03. A drain at158
records player3/city65536 Bakers1094 at forecast adjacency+5. The published
319757Q8 bid comprises246029 economicQ8 plus73728 preferenceQ8. A preceding
native final write and the actual joint-selector result both equal319757,
reason0/existingDistrict0. This is a genuine positive new-site comparison,
not a foundation exemption or merely accepted transport. The stale Bakers987
request is again reduced410368 to-262144. Final lifecycle/health and placement
counts are still pending; neither exact comparison guarantees completion.


## Completed delivery qualification and new full game

Replay04 completes150-175 with complete journal/lifecycle observation, native
exit0, owners absent and preferences/packages restored. The independent audit
record delivery-audit.json finds4 new-site Quarter comparison events across3
sites, all original AI, adjacency5/4/3/4, all actual native values equal their
positive publication and prior write. One retained request is reduced;7705
nonempty-reservation-cell writes are counted (repeated writes, not distinct live
claims). No new original-AI Quarter reaches foundation in this short window:
this closes the demonstrated value-delivery gap, not follow-through or1.8.

Managed matrix refresh takes median16.693ms/max28.205ms per sampled global round
in this mature world. This excludes Lua, masks, request setters and unrelated
engine work. All-eight-Quarter scale has not been measured. Optional read samples
may drop at their documented limit; native Best comparison records retain their
core budget. The observer now reports physical-presence metadata only for
qualified Best/Location records, avoiding PV default fields masquerading as a
fresh district observation;10 observer checks pass after that diagnostic fix.

The authorised fresh **Online250** starts with main CSCbe00cad9, CEdbfb93b /
DLL400e6755..., same639+6 content, Small Continents, Prince, map/game seeds
18461107/29461107. Root fresh250-01. No pre-unlocks, subsidies, external
AI/probe policy or custom production orders. Read-only observations capture
selection-time bids, foundation/completion geometry,25-turn economics and
Services. The shared controller owns console/launch/cleanup; agent checks are
about15min apart. Current outcome is pending. The first packaging attempts and
flag-bypass replay remain preserved; no outcome is inferred from readiness.


Astra independently audits the completed replay04 and confirms all four exact
write-before-comparison chains, request reduction,7705 nonempty-ID writes,
25 timing packets and clean closure. **All four comparisons are Bakers sites
on players1/3.** This does not independently establish Tailors positive selection,
repair continuity, purchases, construction or Services. The one replay completion
belongs to observer player0. Those limits remain live outcome questions.
Reusable flag/footprint knowledge is now AI-N126, committed/pushed in civ6-ai
0bc0440; N023/N125 in2bdcf6c remain valid. The earlier false exemption claim is
explicitly corrected above, not used as repair evidence.
