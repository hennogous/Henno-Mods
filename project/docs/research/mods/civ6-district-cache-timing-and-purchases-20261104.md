# District score components, refresh and tile purchases

4 November 2026. Follow-up questions after the [soft-penalty test](csc-ai-placement-penalties-20261103.md): what is cached, which future land/districts enter, when values and production choices refresh, what explains the later score gains, and how plots are bought.

**The native opportunity set is broader than our pilot scanner, and its score is
a forecast of more than adjacency.** Ordinary analysis runs on a per-turn cycle;
the two late interventions do not establish a slow multi-turn refresh interval.
The large positive later contribution has an identified building-forecast path,
but the previous runtime capture did not itemize individual building components.
Henno therefore asked to understand and supplement CSC valuation before treating
the final aggregate as something to suppress indiscriminately.

This investigation used the existing handbook, captured test records, shipped
data and read-only Ghidra decompilation. No game was launched or loaded, no live
instrumentation was attached, and tuning, installed content and game settings
were not changed. Existing Ghidra target SHA256 matches the inspected XP2 DLL:
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.

## 1. Cache capacity is not current permission

Each city allocates a matrix for the complete DistrictDefinition collection and
up to37 plot rows: the city center plus three rings, skipping off-map positions.
Each row points into type-indexed score storage. This includes slots for locked
districts, unique types the player cannot use and otherwise rejected pairs;
having a slot does not mean having a valid/selectable score.

The evaluator loops all district definitions, applying InternalOnly, OnePerCity,
preference, player-mapping/CanEverZone and plot-potential gates. It estimates
missing technology and civic time, takes their maximum, adds construction time
and calls NetValue. Readiness beyond its evaluation horizon is invalid. Thus
future unlocks can be valued before current construction permission exists,
without making every distant future district an admitted option. [AI-N066]

## 2. Native planning includes potential future land

The per-plot evaluator requires revelation, not current visibility. Foreign land
and land assigned to another city are rejected in this route. Revealed unowned
rows can receive estimates. The eventual ordinary selector requires a district-
capable row that is either owned or adjacent to this player's territory.

There are consequently three different sets: allocated radius-three slots,
evaluated/valid possibilities, and currently admitted winners. An unowned border
tile can win as a future district site. Its NetValue includes a normalized,
discounted plot-purchase cost. This is not a search over arbitrary distant land
or possible future conquest. [AI-N066]

Our pilot scanner was narrower: already owned, revealed, city-assigned land with
current Lua plot potential. The native AI can therefore propose a site before it
appears in our policy table. The precise earlier exclusion for the two observed
misses remains unknown; ownership alone was not recorded as the cause.

## 3. There are several update clocks

| Layer | Verified ordinary path |
| --- | --- |
| Fresh plot/type values | CityManager StartTurn resets per-city off-turn/job-done flags. DoOffTurn waits for five subsystem readiness flags, schedules one City Analysis job for the cycle, and the job evaluates all stored rows. |
| Building contribution and opportunity checks | Matching-priority, full-activation CityBuild pass aggregates building values and checks growth, threats, units/buildings, districts, improvements and wonders. |
| New district winner/proposal | CheckForDistrict calls GetBestDistrict when its district event-tree slot is free and an event definition exists. A live tree can prevent a new proposal despite fresh scores. |
| Actual next production | Matching DoTurn/activation passes call QueueNextBuild when the queue is empty. A busy queue is not routinely replaced by the newest district winner every turn. |
| Gold purchases | Matching full Economic activation processes spending contracts and its opportunistic plot-purchase pass, subject to savings and native legality. |

The analysis is asynchronous and readiness-gated. A native city cycle need not
line up with our once-per-global-turn inactive scanner boundary. The outer
scheduler's full-activation Boolean was not traced far enough to assign it a
more specific universal calendar meaning. This is an ordinary per-turn cycle,
not a proof covering every event or exactly one selector call per turn. New
cities have an explicit initialization analysis. AnalyzeCityPlots reads cached
rows; ReconsiderDistrictConstruction cancels/releases matching nonexecuting
contracts rather than recomputing the matrix. [AI-N067]

## 4. Adjacency is an input to utility, not the whole utility

Scores use signed Q8 fixed point:256 stored units per utility unit, nominal
resolution1/256. Large integers partly reflect that representation and partly
the value of future income streams. They are neither raw yields nor Gold, and
fine numerical resolution does not establish forecast accuracy. This pass also
clarifies the older sentinel wording:−9999 utility is stored as−2559744 Q8;
it is not the raw stored integer−9999. The signed-selection conclusion is unchanged.

The [maintained score anatomy](../../civ6-ai/topics/native/district-score-anatomy.md)
separates admission, direct benefits, empire weights, timing, costs, competing
land use, district preference and future-building aggregation.

The later pass accumulates positive qualifying building forecasts for a missing
or pillaged prerequisite district. The resulting district-type sum is added to
already-positive non-center district/plot entries. It is a city/type contribution,
not a fresh calculation of a separate building chain at every candidate tile.
Mutually-exclusive canonicalization, definition order and other gates matter;
this is not a general fixed-point plan for every future building. [AI-N068]

The observed weak winners expose the positive gate:

| Case | Native fresh output | Our deduction | After deduction | Final cache |
| --- | ---: | ---: | ---: | ---: |
| Delhi Bakers1429 |66,743|65,536|1,207|1,358,358|
| Majapahit Bakers1829 |228,808|196,608|32,200|1,623,830|

Both stayed positive, preserving admission to later building aggregation. The
measured net gains after our hook were1,357,151 and1,591,630 Q8. These differences
include subsequent processing; the captured boundaries do not itemize a separate
amount for every building, preference or effect. Delhi's final value is about
5306 utility units, not1.36 million raw yields.

Current Bakers definitions identify the ordinary candidate family as Wind/Water
Mill, Bakery and Café. Bakery and Café each supply an amenity; Café has regional
range6. BuildingValue has explicit yield, dynamic building-yield, pseudo-yield,
amenity/regional, housing, power, supported modifier and discounting paths, as
applicable to the building. Maintenance is deducted from an income subtotal;
production cost enters the forecast through construction time. Do not replace
that native treatment with an unverified formula subtracting all Production cost
as a one-time amount. Research and prerequisite/production delays also matter.

### An additional prerequisite-depth heuristic

Fresh BuildingValue52b900 lines438–455 follows the first non-null prerequisite
building along its own prerequisite vectors, counting depth d. The direct
prerequisite vector at+1f8/+200 is independently identified by the native SQL
loader in the IZ study. It transforms the early normalized benefit subtotal as:

```text
income subtotal = (1 + 2*d) * earlier benefit subtotal - normalized maintenance
```

That income subtotal then enters discounted-stream calculations. Depth0/1/2
therefore yields factors1/3/5 for this part of valuation. Later amenity, housing,
power and modifier additions are separate; this is not a multiplier on the
entire final building score. Nor is it a sum over every branch of an OR/AND graph:
the inspected loop follows the first prerequisite at each step. [AI-N068]

This is relevant to CSC. The loaded Bakers rows put the internal River Access
building before Water Mill and list the Mills as Bakery/Café prerequisites.
Hidden implementation prerequisites can consequently affect a native heuristic
even when they are not an economic investment for the player. The exact first
prerequisite pointer/order and numerical subtotal for Delhi/Majapahit were not
captured; no factor3/5 contribution is claimed for either observed total.

Those are possible contributors, **not a measured per-building attribution** of
the two totals. The pilot recorded Quarter NetValue/cache/Best/PV, not the entire
building vector or each helper's contribution. Its archived saves and logs do
not supply that omitted breakdown. Static source establishes the propagation
channel; a component observation is needed before naming the dominant building.

Nor may every hypothetical contribution be accepted as faithful CSC economics.
The [modifier study](csc-future-economy-forecast-20261103.md) found unsupported
collections, omitted requirements, missing plot context and ordinary customer
building gates. Current-state Lua returns are not a simulation of a jointly
missing chain. We should preserve genuine benefits and correct measured gaps,
rather than assume either that the whole later sum is correct or that it should
all be penalized.

## 5. Requests and production retain their own state

The district winner creates a preparation tree, then an offered construction
contract. QueueNextBuild validates/updates offered contracts and selects the
highest signed contract value. At its contract gate it compares that result with
the best unit value minus256 Q8 and the best project value; it does not compare
the best building at that particular gate. Its ordinary fallback compares
buildings, units and projects. Districts arrive through contracts. [AI-N025]

A running contract is separately validated/updated. The inspected district
request update retains the higher of stored and current values, so a fresh lower
score need not demote an existing request. Threat interruption has additional
conditions; a better new district score alone does not establish cancellation
of current production. [AI-N023] [AI-N051]

This explains why fresh evaluation, a new category winner, a new request and a
queue switch cannot be treated as the same event or given one universal cadence.

## 6. Buying tiles has two routes

**A targeted site purchase.** The shipped Build City District tree receives the
chosen Location and contains a Purchase Plot node before reservation/construction
work, alongside research preparation. An already-owned location succeeds without
buying; foreign ownership fails. An unowned target can create a PurchasePlotContract
for Economic. Its execution looks for the lowest positive quote across
the player's cities and requests the exact target plot. [AI-N069]

**An opportunistic resource-development purchase.** Economic's full activation
also checks each city's cached best-plot-to-buy coordinate. AnalyzeCityPlots
chooses this from resource-bearing purchasable frontier rows, using improvement
forecasts and an order-sensitive feature heuristic. It is not a simple auction
of every district site or every high-yield map tile. The row field at+4 is Feature,
not Improvement; HasImprovement is at+0x50. [AI-N069]

Both routes respect earmarked plot savings, general slush savings and the native
purchase command's legality/affordability checks. In Q8 terms, with cost C, plot
fund P and slush S:

| Route | Savings gate before native command checks |
| --- | --- |
| Opportunistic | C < P+S and fixed(0.5×C) < P |
| Requested target | quoted Gold <= floor((P+S)/256) and fixed(0.25×C) <= P |

Thus a planned district's request has a more permissive savings hurdle. Both use
plot savings first, then slush. Default shipped allocation weights are slush3,
units4, plots1 and Great People1; these are weights, not a guaranteed fraction of
all per-turn displayed Gold. No independent N-turn purchase countdown was found
inside these inspected routines. Successful buying is still distinct from
reservation, clearance, production and completion.

The two late pilot cases do **not** establish actual tile purchases. Their
behavior logs say `SUCCESS, Purchase Plot, Not Buying anything` before reservation
(The Hague74; Pokrovka92). That node can succeed on an already-owned location
without a spending contract. The exact pre-scan eligibility transition remains
unrecorded.

### Starting rings and a purchase receipt

On patched XP2, `City::Culture::DoFoundCity` at `11be40` calls
`AcquirePlots` at `11b000` in founding mode. That mode enumerates
radius 1 through `4fa40` and `4f9c0`. The callback thunk at
`11d670` reaches `11a290`, which annexes an unowned ring tile or
a same-owner ring tile without a district. It skips foreign tiles
and same-owner tiles with a district. If starting acquisitions
remain, `AcquirePlots` uses its ordinary next-plot selection.
This explains why a Bakers footprint next to a present friendly
City Center usually already belongs to that player. A mapped
supplier beside the proposed Quarter can sit outside the City
Center's starting ring. A request for the footprint does not
buy the supplier.

The tuned and untuned turn-45 development logs contain the same
early native request for Aachen. At turn 2 the district tree's
Purchase Plot node logged `Purchase 56 11: Accepted on #32`.
That contract is evidence of reaching the request stage. It
does not establish spending. For a focused replay, distinguish
the accepted contract from the targeted Economic attempt and
record the native debit, ownership and acquiring city for that
exact plot. A supplier-only purchase also needs a later legal
improvement and observed chain benefit.

Both routes converge on the plot branch of `City::Commands::Purchase::Start`
at `680f70`. This branch recomputes the positive quote and checks
`Treasury::CanAffordPlot` at call site `68135d`. The debit call at
`681379` passes the negative quote multiplied by 256 to
`ChangeGoldBalance`. The annex call at `68139d` assigns the plot
to the buying city, after which the branch emits the purchase
notification. These two call sites distinguish paid acquisition
from the culture route and from contract acceptance. The tuned
`AI_Behavior_Trees.csv` SHA-256 is
`cbaa80d3923719c2592e1b7f3a33c61990ebaa9ae326582daed2cd9700d36ebf`.

The Ghidra reference SHA-256 starts `324c51e9`; the installed
patched Steam image starts `092abfbb`. Their full file-backed
`.text` matched across 10,180,135 bytes, SHA-256
`4ebd266b7d324fc9f97daa9dc39fa5cafcd09d6257e7a446914ddb13fd8927e9`.

### Where a supplier purchase can enter city analysis

A read-only follow-up checked the frontier flag, candidate selection
and quote call on the same Ghidra reference. The plot evaluator at
`3e2aa0` checks visibility and resolves the resource visible to the
player. It sets the frontier flag at row offset `0x57` when a plot
outside the player's ownership has a same-player neighbor. A plot
owned by another player clears the flag before the candidate is
scored. The neighbor need only belong to the player. The later
purchase command still checks the buying city's actual eligibility.

CityBuild's turn activation calls `AnalyzeCityPlots` at `3e296f`.
Analysis clears the prior coordinate to the missing sentinel
`(-9999, -9999)` and scans resource-bearing rows with the frontier flag.
The first eligible row can become the candidate without a score
comparison. Later rows use the feature preference and signed
improvement forecasts. The function writes one coordinate at
`3dec1b` to the CityBuild field at `0x228`, whose value begins at
`0x238` through the auto-variable accessor at `72a920`. It does not
retain a ranked list for Economic to revisit.

The nonhuman Economic activation calls `PurchasePlots` at `4576b8`,
after checking its queued control handles and Great Person purchases.
The routine reads the coordinate at `4585dd` and `4585f0`, quotes that
plot for that city at `458619`, then checks savings. A qualifying
quote can reach purchase request construction at `45867f` and native
command validation and execution. The next city is considered after
this city. The loop cannot fall back to a different candidate for
the same city when its cached plot fails the quote or savings gate.

For a supplier-only diagnostic, start with an unowned, revealed
mapped resource adjacent to a viable Quarter and an owned border
tile. Trace the row through the ordinary comparison and cached
coordinate, then use the quote, debit and annex sites to separate
selection from spending. The static trace establishes where a scoped
supplier preference would have to compete. It has no new purchase
receipt or measured CSC bid amount.

### Which district selectors can exclude a single site

The patched image matches the reference's ordinary `GetBestDistrict`
selection test at `3e4b2c`. The joint selector compares a cell with
both the row's reservation threshold and the best score so far.
For an unreserved row the threshold is the signed Q8 sentinel
`-2559744`. The branch rejects a value equal to that threshold.
An active controller can supply a different threshold. The running
best starts at the sentinel, so a value below it would fail the
running-best test even with a lower live reservation threshold.

The type-specific `GetBestLocationFor` at `3e5550` rejects a new
location with a live reservation and requires its cell to be greater
than the same sentinel. Its existing-district path can return a
pillaged footprint before inspecting the score matrix. This routine
has callers outside the ordinary joint selector, including
`CityBuild::BuildDistrict` at `3df341` and trigger decoding at
`55abd7` and `55abe9`.

The current CE numeric adjustment is bounded. In the repair review
branch it clamps deductions at `-4096 * 256`, and it protects the
invalid sentinel. This remains a finite preference. An explicit
exclusion would need to reach the intended selector at the right
time. Existing requests, repairs and the alternate site consumers
have separate eligibility paths.

For a scoped diagnostic on an unreserved threatened supplier, the
ordinary selection boundary can isolate one district and plot cell
from competing pairs. Keep the actual request, queue, placement and
retained Service as separate observations. This static result
establishes the branch condition and neither redirects a live Dam
nor revokes an existing contract.

## Primary evidence and limits

Retained exports are under`Desktop/Codex/csc-district-placement-20261103/native/`
and`Desktop/Codex/csc-native-ai-analysis-20261028/citybuild-exports/`:

- Matrix/plots: Initialize3e64e0 lines59–67,201–217;3e7350 lines31–76;
  3e7030 lines28–31; evaluator3e2aa0 lines93–175,204–291.
- Future admission and purchase cost:52a440 lines47–50,63–72; selector3e4a50
  lines23–34,49–67; CanEverZone2c3fc0.
- Refresh: fresh exports CityManager3d98f0/3d8fc0/3d9130;3e2590 lines15–48;
  job3e2a40 lines13–20; activation3e2820 lines20–26,53–85;3e2030.
- Aggregation:3dfee0 building loop and positive district loop; BuildingValue52b900;
  evaluator's canonical building branch3e2aa0 lines879–1015.
- Proposal/queue: CheckForDistrict3e0ee0 lines35–40,50–65,83–108;
  QueueNextBuild3e8190 lines57–108,270–284; UpdateWorkingContract3ea990.
- Purchases: fresh Economic457120/458530/459090; PurchasePlotNode55ed80/55dee0;
  shipped Base BehaviorTrees.xml lines519–543,1161–1177; Leaders.xml
  lines335–340,804–807. Tiny purchase-contract thunks3f82c0/3fa880 were checked
  from their18-byte bodies; constants0.5/0.25 from pristine DLL bytes.
- Runtime reuse:`csc-placement-penalties-20261103/weak-sites.json` and original
  native windows; behavior logs at The Hague74 and Pokrovka92. No new execution.

Source locators, hashes, selected DB rows and copied native exports are retained
in`Desktop/Codex/csc-district-decisions-20261104/`. Recovered names are labels;
unresolved indirect callers, component attribution and exact earlier scanner
exclusions remain unknown. This investigation does not authorize another game
or implement another score adjustment.
