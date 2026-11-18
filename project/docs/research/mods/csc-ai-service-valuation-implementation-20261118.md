# Service value in Quarter forecasts: first integrated version

18 November2026. Roadmap14.3 / Quarter investment1.4. Main CSC implementation;
matching CE development build required. [Native results and source identities](csc-ai-service-valuation-implementation-20261118.json).

**Native-backed Service value now enters the complete Quarter bid.** At a retained
turn100 boundary, two Bakers bids rise by3018Q8(11.79 utility), and two Tailors
bids fall by687Q8(2.68 utility). The Tailors construction delays another chain's
growth and Engineer-point streams from relative turn5 to7. These are actual
native prices and calculated packet entries in a zero-turn diagnostic; no packet
was published and no new construction outcome is claimed.

## Mechanism and coverage

EconomyFacts compiles Service effects from registered producers' actual
`BuildingModifiers`, attachment children, modifier arguments and requirements.
Amounts, GPP classes, buyer buildings, civic unlocks and material tags come from
gameplay definitions. No gameplay SQL, amounts, prerequisites or payouts changed.
The loaded database yields27 effect bindings covering both families' ordinary
Stage2–4 recipients, including twelve mutually exclusive Dockmaster era/class
branches. Housing is discovered but unpriced; six Wonder-property branches are
explicit omissions. Display-building grants, specialist slots and art properties
do not earn recurring utility.

The compiler accepts the verified PlayerDistricts→Owner effect shape and known
requirements. Unknown/inverted gates and unsupported nesting fail closed. An
actual admitted recipient can prove its own branch of a customer ANY; it cannot
prove an unrelated Wonder or other customer. Source/root/recipient-plot identity
prevents duplicate mappings from paying twice while allowing separate physical
producers and independent roots sharing the same GPP leaf.

| Benefit | First-version price |
|---|---|
|Storekeeper growth|Native positive Food-surplus/default-Food normalization and interval discount|
|Service GPP, with its actual class|Native pseudo-yield weights and interval discount|
|Bakers/Tailors ordinary venue Tourism|Native Tourism pseudo-yield weights and interval discount|
|Sacristan Faith percentage|Current-output proxy with native100-yield basis cap, then ordinary native Faith pricing|
|Dockmaster production percentage|Observed eligible ship output through its remaining queue window, native Production pricing|
|Innkeeper Housing|Unpriced pending nonlinear city/interval qualification|
|Wonder-hosted Stage Manager effects|Unpriced pending property/recipient forecast support|

The naval numeric reader was in the wrong UI function and unreachable. It now
runs through `GetEconomyCityNumber`, returning current unit, remaining work and
eligible naval output. This also repairs the existing single-chain Dockmaster
input for building/repair marginals. The formerly dead building/district timing
branches were removed without enabling new timing behavior; existing fallbacks
remain. Percentage-output estimates stay anchored to current output, not future
population or guaranteed fifty-turn ship production.

## Shared planning and the final bid

Joint Quarter worlds opt into Services on **both** sides. They use the same
supplier, producer, customer and unlock scheduling as ordinary transactions.
Active effects stay in both worlds and cancel; delayed or destroyed effects
reduce the marginal value. No ordinary building-depth multiplier applies to a
Service. Separate customer-placement worlds retain their ordinary baseline.
Only existing admitted customer footprints are covered in this slice.

The old adjacency ceiling continues to cap ordinary forecast/siting value.
Signed marginal Service value is subtracted before that cap and added once
after it. Otherwise the ceiling could erase every useful Service contribution.
The full positive-economics gate, Base/adjacency requirements, material safeguards
and final CE score ceiling remain. Qualification tests cover equal positive and
negative shifts, uncapped values and ineligible sites staying deferred.

Both baseline objectives still search independently. They share at most16 exact
unpriced plan ledgers within one publication, identified by the physical baseline,
producer choices and disabled buyer nodes. Candidate worlds have separate ledgers.
Copied stream headers prevent cross-mode price mutation. Unknown optional Service
quotes become explicit omissions; required ordinary pricing keeps its failure
semantics. Older CE, lacking the optional capability, retains ordinary forecasts.

## Native and offline checks

Two final saved-world checks use the shared controller, preserve the source
structure/turn, repeat B/A/A/B privately and restore/close with native exit0.
All same-arm bids, economic streams and plans repeat exactly. Source Lua matches
the immutable `frozen03` candidate. All native/model budgets and unknown counters
are clear. A treatment100 checkpoint was originally unavailable; the valid
control100 checkpoint supplied the earlier state instead.

| Diagnostic player5 pass | Services off mean/max | Services on mean/max |
|---|---:|---:|
|Control100|0.380 /0.392s|0.449 /0.467s|
|Treatment250, nine chains|1.739 /1.751s|2.164 /2.207s|

This is a cold-history economic pass, not whole-turn overhead. The added cost is
0.069s at100 and0.425s at250, chiefly the additional Service-aware baseline search.
It is bounded but material; retain full-game timing instrumentation and use
larger-run measurements before further expanding the forecast. Native scalar
quotes increase1190→1202 in the mature sample; customer forecasts remain16.

Native one-point intervals at100: Engineer204+191=395Q8 over two periods;
Tourism256+209=465Q8. +10% growth with11 positive Food surplus quotes488Q8 over
two periods;14 surplus at250 quotes628Q8. Engineer pricing is0 in the mature
sample: reuse the current native weight rather than invent a universal GPP bonus.
Invalid pseudo-yield input returns unavailable. Growth/pseudo interval origins
follow the existing corrected recurring-income contract.

Validation:154 economy regressions,13 timing/controller checks, supported MSVC
CE build,253 native district/economy checks and shared hook failure/cleanup checks.
Astra reviewed the world/cache boundaries, stacking and signed-cap split.

## Delivery and next work

CE source branch: `hennogous/CivilizationVI_CommunityExtension`,
`codex/native-quarter-valuation`. New APIs are `CE_AIPseudoYieldIntervalValue` and
`CE_AIGrowthIntervalValue`; `servicePricingReady` independently qualifies them.
No hook or public gameplay effect was added. Qualified CE DLL SHA256:
`00edf646d8b32e3a03730b7902e64a9e7469124c03abe7985d31c9682293d356`.
Matching package: Desktop/Codex/csc-ai-service-valuation-20261118/frozen03/CE.
No upstream PR has been submitted. Upstream develop/master remained2986a746/e59b5aa
when checked before the native tests.

Next14.3: qualify Housing's native timed city value with pooled before/after
amounts; support Wonder-property gates; then observe a changed native district
comparison/foundation and full-game outcomes. Preserve current native competition.
Retain the turn100/250 sources and current qualification; closed duplicate
installed packages can be retired against their immutable sources.
