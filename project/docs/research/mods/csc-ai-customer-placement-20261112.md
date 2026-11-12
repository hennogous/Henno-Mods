# Problem2.1: customer-district placement

Active after Astra-approved1.7 closure. Acceptance: isolate the mapped
customer-site contribution and demonstrate a changed actual native district
choice/request toward an adjacent provider Quarter or a specific credible
future Quarter footprint. Preserve standalone value, legality, other policy
and material protection. Require dynamic main-mod reproduction. Construction
and broader coverage are separate.

## Implemented scope

Main QuarterPlacement.StageTwoProfiles builds customer mappings from
CSC_QuarterCustomerBuildings rows with ProducerStage2, including building
and district replacements. In current CSC that means City Center/Granary
for Bakers and Harbor/Lighthouse for Tailors.

AdjacencyScan excludes City Center from ordinary district nominations.
The existing-Quarter customer bid is40*256 Q8. It requires a complete,
unpillaged Quarter with viable owned Base, no adjacent placed mapped customer
host, and a resource-free, unprotected, owned native-legal customer footprint.
Several qualifying chains deduplicate the same pair rather than stacking bids.

The smaller16*256 future-Quarter bid requires an owned strong site, ready
Base and a selected future host in that current native target list. The
present guard withholds it when both population-requiring districts would
share a city. It is not a general bid for every projected customer footprint.

CSC_AI_Connectors.sql supplies another path: +1 private adjacency yield from
a mapped Quarter to its Stage2 customer, with DefaultYieldBias25. That is a
+25% native yield bias, not25 times,25 utility or25 Q8. It also excludes City Center.

Thus the ordinary customer-placement paths currently address Tailors→Harbor
and replacements. Bakers' later Entertainment/Water Entertainment customers
and Commercial goods-provider links can affect Quarter siting through the
broader siting registry, but do not receive these Stage2 customer-site bids
or SQL connectors. Zero customer offers in the early Bakers tests is expected.

## Existing observed comparisons

The old Fractal receipt run has28 written/eligible customer offers and five
city comparisons. Three exact site wins span two Harbor sites:

| Decision turn | Player | City ID | Offered plot | Exact site win |
| --- | ---: | ---: | ---: | --- |
| 141 | 4 | 589832 | 2383 | Yes |
| 167 | 2 | 524295 | 1437 | No |
| 169 | 2 | 524295 | 1437 | Yes |
| 176 | 2 | 524295 | 1437 | Yes |
| 178 | 5 | 65536 | 648 | No |

Receipts are read on the following turn. The141 CityBuild row submits
Harbor contract2644, priority693, for Ka Peyakwaskonam. These prove delivery
and observed native choices, not necessity of either customer signal.

Archive: C:/Users/Shadow/Desktop/Codex/csc-ai-native-receipts-20261108/fractal.
The runtime Fractal catalogue maps district4 to Harbor. The Continents
fixture maps4 to Holy Site. Join native indices to each world's catalogue;
do not carry a numbered type across configurations.

No preserved pre141 checkpoint was identified. The later pinned Fractal
200 source, observed through207 by host-choice-fractal-scout-01, produces
zero current customer offers. Washington22→24 and Nicopolis200→254 also
produce none. These windows therefore cannot establish customer-bid
causality merely by reusing their successful Quarter comparisons.

## Next unresolved dependency

**Astra's best bounded geometry/timing lead is Hamburg**, player3/city393221,
at202. The archived owned comparison records population7, Encampment in
production, owned empty prospective Tailors1083, ready unimproved Sheep1084,
no adjacent host and potential Harbor footprints1082/1156. The later native
lifecycle in nuremberg-ownership-integrated-01 completes Encampment4192 at207
and opens a fresh Theater request4493 at208, value2195.

Source survey:
continents-owned-comparison-01/cases/run-v3-continents/owned-comparison-202/gameplay-survey.json.
These are geometry and timing observations, **not a competitive Harbor margin**.
First qualify current symbolic district types, native Harbor targets, capacity,
protection, empty1083 and viable1084 without edits. Do not infer the current
native index from the old survey.

If those checks pass, a single declared common completed-Tailors1083 fixture
could exercise the existing +40 customer path. It must leave room for Harbor,
preserve suppliers, and be identical in both arms. Observe actual native
competition before committing to an ablation; preserve the fixture and SQL
connector while withholding only the targeted Lua customer contribution.
The known208 window can shift after a controlled fixture, so actual native
timing and the queue must be recorded rather than forced.

Qualify the actual main offer and native margin before selecting an ablation. Preserve the
private-yield path unless testing it explicitly; do not attribute its effect
to the CE bid. Existing native/CE readers are sufficient to begin; no new
address or score probe is justified yet.

## Current read-only qualification

customer-hamburg-inspect-01 completes200→202 and closes normally without
gameplay edits or a saved derivative. Hamburg has no Tailors or Harbor;
population7, Encampment queued, one free population slot. Tailors is
population-free and Harbor requires one slot. Both1082/1156 are actual owned,
resource-free, unprotected native Harbor targets. Sheep1084 is ready and
unimproved. Tailors1083 is native-legal and unprotected, but carries an ordinary
Lumber Mill and Woods. The initial conservative improvement-free fixture rule
therefore refuses it. This is a preparation guard, not an inert policy result.

The next common preparation checks only the six Sheep-neighbor footprints,
preferring an unimproved native-legal Quarter site adjacent to a current safe
Harbor target. Known1083 is the declared ordinary-Lumber-Mill fallback. Any
improvement/feature conversion is recorded, the Sheep is preserved, and
queue/population/funds must remain unchanged. This common completed Quarter
is diagnostic setup, not native AI construction.

## Unsaved202 setup failure and revised timing

customer-hamburg-common-01 qualified the active native private-yield definition,
bias and Harbor–Tailors adjacency. The six-neighbor search found only the
declared1083 Lumber Mill conversion. A completed Tailors was created and the
Sheep-preservation checks passed, but the combined queue/population/funds
postcheck failed. The command was not retried, no derivative was saved, and
the controller closed normally. The old command did not print individual
after-values, so the exact failed field remains unobserved.

Targeted Ghidra review identifies a relevant native risk. On reference XP2
SHA324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c:

- Lua CreateIncompleteDistrict, RVA6c9f10, calls BuildQueue::CreateDistrict,
  RVAfbd90. Completion100 enters PostCreateDistrict.
- If the current queue item is a District and its type cannot be zoned at the
  newly completed district's plot, that factory calls PopFront, RVA1014c0,
  then CheckProduction, RVAfb940.
- CurrentlyBuilding, RVA6ca000, confirms kind2 is a District and returns a
  symbolic type string; empty production returns a placeholder string.
- WorldBuilder's Lua CreateDistrict, RVA5ef160, reaches manager607780 and
  CommandCreateDistrict::Apply606ce0, which calls the SAMEfbd90 factory.
  Swapping the public wrapper does not avoid this branch.

These are static claims, not a captured PopFront invocation in the failed
run. Prior text-identity evidence relates this reference to the patched stock
092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f.
No new native hook/address write was introduced. The source decompilations
are archived under customer-hamburg-common-01/native-reference.

The revised preparation waits for inactive208, after the archived natural
Encampment completion207 and before the known fresh208 comparison. It verifies
the ACTUAL queue is not a District before any write; otherwise it stops
unchanged. Individual before/after queue, population and Gold values are
logged before the postcheck. No queue reset, forced completion or bid increase
is used. A successful common208 save would support cold208→210 comparisons.

**Henno's latest direction is native adjacency/private yield first.** The first
matched diagnostic pair will withhold the extra CE customer-site benefit in
both arms, preserve all other guidance and protections, and vary only the
relevant Harbor–Tailors private-yield adjacency link. Keep the Yield definition,
index and bias intact. Runtime definitions alone do not prove consumption:
require native values and a changed actual customer choice/request.
No2.1 closure is claimed.

## Qualified common208 source and native-first pair

`customer-hamburg-common-02` completed normally. The common fixture removes
the ordinary Lumber Mill and Woods at1083 and creates a completed, unpillaged
Tailors there. It preserves Sheep1084. Individual before/after receipts show
the Coal Power Plant queue unchanged, population7 unchanged and Gold
400.59765625 unchanged. Both1082 and1156 remain legal Harbor targets.
These are declared diagnostic world edits, not AI Quarter construction.

The inactive208 source has SHA256
`35407699072ab37774799ea4cb7bd4aa45e43b8d00f1fc5147a227ad61e7ec0e`.
Its archived and native saves match; SaveComplete, unchanged phase and normal
controller cleanup are verified. Astra independently checked these receipts.
Artifact root: `C:/Users/Shadow/Desktop/Codex/csc-ai-problems-1-2-20261110/customer-hamburg-common-02`.

The diagnostic pair withholds only Hamburg's intact positive CE Harbor
customer entries in both arms. It removes entries rather than publishing zero,
which the bridge rejects. Unexpected merged contributions abort the setup;
material penalties and all other guidance remain. Identical metadata adds a
last SQL action in each arm. ON retains the existing native adjacency link;
OFF removes only Harbor's link to the Tailors private-yield rule, preserving
the rule, Yield definition/index and bias. This SQL change applies globally
to that district pair, so it is not a Hamburg-only database treatment.

**Save-loading qualification remains necessary.** Do not assume a SQL change
updates a saved game's live native data. Before either arm advances, inspect
the actual loaded link count and unchanged Yield/bias. If the OFF definition
does not take effect, use fresh-game sources. Even changed GameInfo rows alone
do not prove changed native caches or evaluation: require the full native
district-site matrix, actual winner and matching request. Existing-instance
modifier attachments have previously retained old effects after new SQL loaded;
that separate finding is a reason to verify, not proof this adjacency path does
the same. These were preflight requirements; the completed pair follows.

## Completed native ON/OFF comparison

Both `customer-hamburg-native-on-01` and `customer-hamburg-native-off-01`
complete208→210 and close normally: native exit0, owner absence, exact
preferences restored and package callback verified. Loaded patched stock XP2
SHA256 is `092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`;
CE is `a849eff803d68f7dc4061421c98812ae466b50f0d96a790f884f0f7bcf60eafb`.
All package manifest differences reduce to the diagnostic SQL file's contents.
Metadata and both main-publisher diagnostic wrappers are identical.

Direct read-only inspection of Firaxis's loaded `DebugGameplay.sqlite`
confirms the OFF Harbor link is absent after loading the same208 save. Its
rule row156 and private Yield row7 remain, with DefaultValue1 and bias25.
Cothon and Royal Navy Dockyard links remain. GameInfo independently records
the expected link count. ON's DB rows were captured after its normal closure,
before the next load; OFF's were captured before play. **A fresh game is not
required to apply this particular SQL link change.** This is not a general
claim about saved modifier instances or arbitrary SQL changes.

Actual GetBestDistrict208 sees the following final matrix values. District
indices are joined to this source's recorded catalogue.

| District / plot | Native ON Q8 | Native OFF Q8 | ON minus OFF |
| --- | ---: | ---: | ---: |
| Harbor1156, adjacent Tailors | 510008 | 498895 | +11113 |
| Harbor1082, adjacent Tailors | 492724 | 481607 | +11117 |
| Water Entertainment1156 | 365475 | 371043 | −5568 |
| Water Entertainment1082 | 374105 | 379674 | −5569 |
| Harbor1303, nonadjacent | 458350 | 458350 | 0 |
| Winning Theater1231 | 558486 | 558486 | 0 |

These are the only four changed cells in the full36×38 matrix. All other1364
cells and all recorded eligibility/ownership/frontier/reservation fields match.
Harbor1156 is eligible, owned and unreserved;1082 has the same reservation in
both arms. Its approximate43.4-point final increase is an observed result in
this city, not a universal exchange rate for one private yield. The competing
Water Entertainment reduction is consistent with the known alternative-land
deduction, but this experiment does not trace that exact internal branch.
Do not describe the private signal as affecting only its own district column.

Both arms select Theater1231 and submit contract4489 at2181.0 on208.
The best Harbor remains48478 Q8 below Theater in ON. The CE +10240 customer
entries at1082/1156 are withheld at each ordinary208–210 publication; exact
receipts show staged0. Native observers report fault=null/active0. There is
no forced queue, plan cancellation, subsidy or bid increase.

**Result:** native SQL adjacency is demonstrably consumed and changes final
site values after a saved-game load. It does not change the actual district
choice in this window, so2.1 is not closed. The native benefit overlaps in
purpose with the existing-Quarter CE +40 candidate; this motivates reviewing
whether both are needed, but does not prove harmful overvaluation or numerical
equivalence across cities. Future-footprint +16 guidance has a distinct role
that this static adjacency cannot express. Shipping policy remains unchanged.

Astra independently rehashes every archived package file in both arms, compares
all1368 cells and every row flag, and matches the four-record terminal native
traces exactly to their streamed journals. Loaded rules/Yields/biases match;
only the expected link differs. Each arm has six identical customer removals,
staged0 target receipts, four complete prefix boundaries and no logged failure.
The285 filtered native prefix records match as full-content multisets, though
callback order differs. These are filtered records, not a complete-world packet
capture. The scoped tooling suite passes35 tests; ModBuddy action metadata
check passes. Reusable engine result: AI-N122 in the maintained civ6-ai skill.

The next recorded timing lead is Hamburg's natural Theater completion217
and fresh218 comparison in the supplier archives. That is a lead requiring
new live legality/capacity qualification, not a promised Harbor opportunity.
The other nine closed capabilities are ready as full-game qualification
candidates; the normal complete CSC/current CE package needs a separate
deployment preflight because these controlled replays stage five current
main modules inside a frozen carrier. If a future SQL test genuinely requires
a fresh start, Henno requests using it as a full integrated run as well.
