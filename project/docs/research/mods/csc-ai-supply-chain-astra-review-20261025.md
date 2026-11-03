# CSC AI supply-chain capability — Astra review, 25 October 2026

Requested by Henno after the V8 partial175 test and original-placement breakdown.
Reviewer: gpt-6-astra, high reasoning, read-only source/evidence review. This is
advice and an experimental roadmap, not implementation or permission to start a
new game. RH Workshop content remains read-only. No native session or schedule
was started for this review.

## Human objective

Fair capability across the whole CSC development pipeline:

1. Place Quarters beside the appropriate mapped resources.
2. Improve and repair those resources; avoid sacrificing them later without
   accounting for their value to the chain.
3. Encourage appropriate adjacent customer districts while respecting stronger
   alternatives (for example a genuinely better Harbor elsewhere).
4. Construct the relevant Quarter and customer buildings.
5. Match Service effects to player agenda/strategy later; this is deferred.

Standalone Basic and automatic RH compatibility remain distinct. CSC assistance
and its dependent subsidy option default On, including with RH; users can keep
RH active with CSC assistance Off. A fair outcome is not maximum CSC density at
the expense of the AI's ordinary economy, defence, growth or victory path.

## Overall assessment

CSC has demonstrated site acquisition and construction assistance, but not
dependable supply-chain planning. The decisive gap is developing and preserving
inputs after placement. More Quarter priority alone risks more fragile chains.

The latest cohort analysis is useful, but AI-placed is a residual opportunity
cohort: CSC takes Both sites first and removes the same Quarter type from those
cities' remaining native choices. It is not an untreated counterfactual. One
interacting same-map world is not five independent experiments. City counts,
placement ages, captures, expansion and strategic commitments all matter.

The original native cohort completed64/65; all52 at least25 turns old completed.
CSC's11/11 supports construction assistance but not an isolated causal advantage.
Nine of11 assisted sites lost the original Base resource; eight old Base tiles
now host districts and one hosts a resource-less Mine. Those are observed losses,
not proof that preserving each tile was strategically preferable. Aqueduct and
Spaceport locations particularly need an opportunity-cost assessment.

No Base or no Service does not mean a Quarter is worthless. Ordinary adjacent
building transactions, internal building relationships and trade-route effects
are not universally gated by Service supply. Bakers Mill–Granary trading and a
supplied Feudalism Service are different benefits. The supplied-Base metric is
one component of value, not a full economic success label.

## Source findings and integration constraints

### Native placement lacks the exact material vocabulary

Current Data/CSC_AI.sql rewards every bonus-class resource by12 in prospective
native district adjacency. Exact mapped Base/Specialty40 presence attaches to an
existing Quarter, and matching improvement80 is another later path. Pre-placement
and post-placement incentives therefore express different information.

The shipped Base/Assets/Gameplay/Data/Schema/01_GameplaySchema.sql defines
Adjacency_YieldChanges.AdjacentResource as boolean and AdjacentResourceClass as
a class, with no exact ResourceType or CSC-tag selector. Per-resource names
cannot simply replace the generic bonus row. An exact prospective native
forecast needs proof that the actual placement scorer consumes it. The assisted
planner remains the verified exact-site selection route.

### Our own planner is not yet a complete investment planner

CSC_AI_OpportunityPolicy.Better orders Base count, Specialty count, missing tile
count and plot IDs. It does not order expected payoff, usable customer frontage,
actual route cost or scarce future Campus/Aqueduct/Spaceport land. A technically
perfect Both location can be a strategically awkward investment. Every assisted
site in this pilot had only one Base and one Specialty: no redundancy.

### Customer30 is shared, not exclusively RH

The reverse10->30 change lives in shared CSC_AI.sql and is loaded by both Basic
and RH. Finish300 is RH-only. Current Basic would also receive30, whereas the
frozen Basic reference received10. Historical comparisons remain descriptive,
but future qualification must either test the new shared layer in both profiles
or deliberately make the customer override RH-only.

### Preserve RH's baseline and strategic freedom

The existing Basic/RH split is appropriate. RH5.097 already sets general
improvement pseudo-yield30 and has Builder movement, need scoring and purchasing.
Another blanket Builder weight is not evidence of solving a specific repair or
worker-assignment problem.

RH_AutoPurchase.lua's RH_ScoreCityBuilderNeed branch counts an existing
improvement as improved without distinguishing a pillaged improvement there.
A CSC repair backlog can add information that branch lacks; this does not prove
RH never repairs or that its purchases caused the observed delays.

RH_AutoPurchaseBuildings.lua has a private vanilla building priority table with
Granary/Lighthouse/Workshop and no CSC buildings. It is not a public extension
registry. Treat it as a design reference or seek a supported extension contract;
do not edit the RH file or assume a hidden table is safe to monkey-patch.

The registry's nativeCombinedProfileTested=false describes stale/release
qualification metadata, not the absence of our native combined tests. Reconcile
that distinction before release rather than silently changing it during review.

Private yields can change citizen allocation and real output even without direct
currency conversion. Actual original-human/role exclusions and ordinary-yield
controls are required; an empty icon or hidden UI is not economic inertness.

## Recommended work order

### 1. Improve the proven assistance planner

Keep native legality, own-funds-first quoted debits, reserves, subsidy caps,
cooldowns and persistent one-shot receipts. Rank existing Both opportunities by
operational Base redundancy, native-valid improvement potential, acquisition
cost and usable customer frontage, rather than increasing placement frequency
or funding. Separate currently actionable supply from future-tech potential.

Prefer adjacency to an already well-sited customer where possible. A good Harbor
can keep its native location while CSC chooses the Quarter site around it. Where
no customer exists, count legal non-material customer positions and flag scarce
future district land. CanHaveDistrict and existing operation-target/CanStartOperation
readbacks provide legality, not a complete strategic site score.

Base-only fallback or a cap on outstanding undeveloped chains are later policy
hypotheses, not automatic changes approved by this review.

### 2. Prove a preservation decision channel

Do not repeat larger160/80/20 numbers. Earlier care tests established native
getter application, not protection; V2 included four confirmed harvests and
seven district-occupied resource removals. A working Sheep Pasture was removed
and harvested for a Farm. A no-response recommendation probe is informative,
though caching prevents a universal claim of non-consumption.

Test a fresh, uncommitted replacement decision: last Base, redundant Base and
unrelated resource. Apply the candidate value before contract/reservation; require
a working positive control on that same decision path, unchanged ordinary yields,
and actual proposal/choice/operation evidence.

There is no verified CSC district-location veto in the inspected interfaces.
Plot properties and CanHaveDistrict queries are not vetoes. If the relevant loss
is not consumed by native scoring, say so. Do not present hard map restrictions,
resource restoration or forced cancellation as native AI understanding. Legitimate
high-value replacements may still win after accounting for chain value.

### 3. Separate development from repair

Maintain a CSC backlog of working, repairable, unimproved-and-legal, technology-
locked, unsafe/unreachable and permanently lost inputs. Prioritize actionable
last Base, then unique Specialty, then redundancy. Check actual job reservations,
eligible worker assignments and reachability; empire charges/proximity alone are
not availability or path proof.

Test whether improvement-owned80 enters fresh marginal build and repair
forecasts. Earlier Pasture80 changed one Farm/harvest path to Pasture construction;
that all-owner improvement-wide mechanism is not a release-ready solution.
Camp/Plantation additions had no additional physical response and did alter
citizen allocation.

If soft forecasting is ineffective, a bounded existing-Builder helper is a
possible separate fallback design, not implemented/proven. It would require
verified nonlocal command authority, safe paths, assignment respect, ordinary
movement/charges and one-shot receipts. Do not assume more Builders or free
repairs are necessary.

### 4. Test a genuine building-production channel

V7's27 Buildings-list additions produced identical captured behavior and outcomes
to V6. Do not repeat that mechanism with larger Value; this does not prove all
Buildings lists are ignored.

Shipped Leaders.xml around906–916 and AiBuildSpecializations expose BuildingYield,
PrioritizationYield and PriorityOffset, referenced by an AiBuildSpecializations
list. Six ordinary yield-building routes exist; no CSC-private route does. An
additive CSC specialization with the existing forecasts, zero offset and unchanged
RH policy is a coherent small test. Custom native support/consumption is unproven.

Use legal unbuilt supplied/unsupplied cases and an ordinary-yield building positive
control. Require a fresh proposal/score or selection response, not another getter.
If successful, separate building-production valuation from the shared placement/
material yield before release. Express actual marginal producer/consumer/specialty/
customer benefits and prerequisite bottlenecks. Do not gate all ordinary exchanges
on Service conditions. Agenda-specific Services remain deferred.

### 5. Calibrate customer adjacency as a bounded preference

Native District_Adjacencies is a grounded placement input. Private30 is not known
to be small or comparable with4 ordinary Harbor Gold; several neighbouring
Quarters can stack it. Static adjacency also cannot express only a functioning
chain or avoid destroying the sole Base.

Use a native tie where CSC should help, an inferior adjacent Harbor versus a
genuinely better +4 alternative, and a tempting customer position on the sole
material. The bonus must preserve sensible alternatives after accounting for real
CSC benefits. A strong real chain may legitimately outweigh ordinary adjacency;
this is not a rule to always take the largest displayed native number.

Base/Assets/UI/AdjacencyBonusSupport.lua:198 calls
plot:GetAdjacencyYield(Game.GetLocalPlayer(), cityID, district, yield). This is
a promising read-only opportunity-cost measurement lead; explicit AI-player
support/projection still needs native controls without role switching. It is not
proof of an engine hook that enforces a custom regret cap.

## Minimal discriminating tests before another long combined run

1. Existing building forecasts, specialization absent/present, matched legal
   opportunities and a fresh native planning cycle.
2. Fresh replacement opportunity, last/redundant/unrelated material, positive
   control and exact operation/world attribution.
3. Customer tie, superior alternative and sole-material conflict, with actual
   future customer-building eligibility.

Only channels with a decision-level response proceed to complete-game tests.
For siting, compare the same profile with foundation injection disabled, not
the AI-placed subset of an assisted world. Keep resource pass, subsidy policy and
unrelated guidance fixed. Separate finish priority and customer adjacency arms
only when attributing their individual effects is necessary; avoid broad weight
sweeps. First solve the observer lifecycle/bounded capture problem so a long run
can actually produce comparable endpoints.

## Success measures and decision-changing gaps

- Legal opportunities at the actual selection/reservation instant and material
  quality chosen, not only endpoint stock.
- Time from first actionable development/repair opportunity; working supply-turns;
  last-Base loss; harvest, district occupancy, pillage and capture separately.
- Completion/producer/building conversion by placement and unlock age, retaining
  failed/captured original episodes and late censoring.
- Actual customer buildings per eligible source/customer opportunity; City Centers
  separately; private forecasts, flags and links separate from monetary payments.
- Real yields, growth, treasury, paid acquisition/subsidies, major competing
  district delays, defence/military and victory development.
- Totals and per-city rates together, not CSC density as the sole target.

The alternatives at the actual decision instant, marginal economic returns of
each chain stage, and a demonstrated preservation input/extension would most
change the recommendations. Until then fair capability is an engineering goal,
not a property established by the current combined profile.

## Evidence trail

- csc-ai-foundation-handholding-breakdown-20261025.md and underlying per-site CSV/JSON.
- csc-ai-foundation-priority200-20261025-results.md and independent-partial175-audit.json.
- csc-ai-rh5-parity-campaign-20261024.md and V6/V7 native input/log comparisons.
- Current CSC_AI.sql, CSC_AI_Basic.sql, ModSupport_RH_AI.sql/Roles.lua and
  CSC_AI_OpportunityPolicy.lua; active action manifest/profile registry.
- Shipped GameplaySchema/Leaders.xml/AdjacencyBonusSupport.lua and read-only
  subscribed RH5.097 strategies, AutoPurchase and AutoPurchaseBuildings sources.

No gameplay source, installed package, settings, Workshop file or native state
was changed as part of the Astra review. Parent saved this assessment as durable
documentation; proposed mechanisms remain unimplemented and unproven unless
explicitly identified above.
