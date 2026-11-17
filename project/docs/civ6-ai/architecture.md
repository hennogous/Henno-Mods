# CSC AI architecture

**16 November economic-definition migration:** ordinary fixed, local, Stage3/4
and directional material transactions have gameplay-owned headers, payout legs
and checked native consumer bindings. Processors generate metadata, payout and
gate arguments; gameplay and AI share declared quantities, yields and gates.
The source-to-native path and diagram are in the
[migration report](../research/mods/csc-population-transaction-catalogue-20261116.md).
Population gameplay matches the QAed source in288 offline worlds and67 live
cities. Fixed/native material graphs match the QAed baseline. A bounded live pass
processes22 actual chain sites;30 lifecycle observations qualify material
damage/recovery and shared protection. The pure joint ledger now shares customer
investments/queues and pools population targets before rounding. Ordinary staffing
reads native citizen-yield definitions and actual assignments; the mature smoke
observes28 workers and30 ordinary streams.17 November adds shared native route
definitions and one route-network pass after shared scheduling, with city-level
amenity pooling. The affected-customer world now builds and prices real candidate
footprints (8/8 sampled native quotes); native residual delivery remains active
work. Explicit recurring-interval quotes preserve the native weights while
correcting the time-zero origin. [Customer worlds and pricing](../research/mods/csc-customer-world-pricing-20261117.md).
[Route implementation](../research/mods/csc-joint-route-economy-20261117.md).
[Contract](../integrations/csc-economic-contract.md).

```mermaid
flowchart LR
    DECL["Gameplay transactions<br/>fixed / population / directional materials"]
    TAG["Gameplay resource and partner tags"]
    GEN["SQL projections<br/>native effects / gates / input hosts"]
    LIVE["Live facts<br/>owners, buildings, plots, workers"]
    MODEL["Central economic ledger<br/>actual legs, recipients, timing, rounding"]
    Q["Quarter bid adapter"]
    P["Material protection adapter"]
    C["Joint customer residual<br/>implementation in progress"]
    R["Observed routes<br/>actual endpoints and paid counters"]
    T["Joint scheduling then route network<br/>pooled amenity counterfactuals"]
    W["Shared before/after customer worlds<br/>footprint, partners, suppliers, queues"]
    PRICE["Native interval quotes<br/>yield weights / city happiness / discount"]
    N["Native comparisons<br/>selection and execution"]
    DECL --> GEN
    TAG --> GEN
    GEN --> LIVE
    DECL --> MODEL
    LIVE --> MODEL
    MODEL --> Q --> N
    MODEL --> P --> N
    GEN --> R
    R --> T
    MODEL --> T
    LIVE --> W
    MODEL --> W
    T --> W
    W --> PRICE
    PRICE -.-> C -.-> N
```

**16 November Dockmaster adjustment:** Tailors +1 may bid beside a completed
owned Harbor. The shared facts carry the Harbor plot to initial/final/grace
admission; real income stays unchanged and the minimum preference/weak cap apply.
Harbor-first material preference becomes16–24 per supplier city/type, total32,
while the best ordinary-adjacency gate stays strict. Broader prospective Service
value is roadmap14.3.95 economy/Lua tests pass; no new live run.
[Details](../research/mods/csc-ai-dockmaster-siting-20261116.md).

**Native valuation/calibration,15 November:** the economic ledger now receives
native site-cost residuals and actual horizon/discount; stock item-specific
construction estimates feed readiness. An adapter maps missing-building income
to native-style investment weights without changing physical transaction amounts.
Smooth control-district references, timing-aware spatial preferences and quality
caps govern the final bid. New Quarter proposals honour the shared supplier
protection map. Eight exact native wins/eight foundations occur in Online50;
the mature200 zero-turn inspection checks weak/strong price separation.
[Mechanisms, diagram, code scope and results](../research/mods/csc-ai-native-valuation-20261115.md).

**15 November temporal coherence:** complete valuation now consumes only named
supply-protection losses from the early planner. A separate plain-record
continuity module remembers native-confirmed choices, persists bounded primitive
state, and supplies the selected footprint-cost baseline plus one-turn owned
data grace. It never holds the whole bid above current economics or constructs
anything. [Design and tests](../research/mods/csc-ai-coherent-investment-20261115.md).

**Current spatial revision,15 November:** the shared facts snapshot now exposes
concrete customer footprints and native terrain adjacency. The decision adapter
compares compatible single/pair layouts and adds bounded planning preferences
beside the economic ledger. Future customers remain absent from income/current
adjacency. One cross-quarter offer pass checks current legality, capacity and
footprint conflicts. No settlement changes or additional DLL API.
[Policy, tests and run protocol](../research/mods/csc-ai-spatial-layout-20261115.md).

**Current policy, 14 November:** +2 minimum / +3 preferred adjacency for both
families. Base supply, current customer footprints and positive economics remain
required; native capacity and competition remain authoritative. The +3/+4
thresholds in the dated results below describe those earlier test packages.

**Latest correction:** capacity is observed at publication, while native CanZone
controls admission. A global publication can precede per-player growth in the same
turn. Full/unknown allocation therefore no longer erases worthwhile future bids.
The paired short replay verifies earlier positive delivery and exact native values;
it does not improve construction in that window. A subsequent normal250 restores
the earlier ungated result: seven guided foundations and57 exact native winner
values, with byte-identical city-build logs and matching core censuses. This is
reproduction, not a new outcome beyond that earlier trial.
[Timing evidence](../research/mods/csc-ai-capacity-timing-20261113.md)
· [Full-game results](../research/mods/csc-ai-timing-correction-250-20261113.md).

The target is one shared account of a Quarter economy, with adapters that offer
its value at the decisions Civ actually makes. Civ retains legality, competition,
production, purchases and execution. We do not order a city to build a chain.

This implements the architecture agreed on 6 November (commit `057d4c55`). The
13 November revision covers **Problems 1.1–1.8 and 2.1–2.2**. It replaces the
Quarter's forecast at the late district-value boundary, rather than trying to
reconstruct and subtract each of Civ's modifier-interpreter mistakes.

**Preceding delivery revision, 13 November:** corrected source passes 243 native checks and
25 economy tests, with Astra review and controlled delivery qualification.
The normal Online game to turn 250 run completes: 57 exact new-site comparisons; all seven
AI-founded Quarters have Base and actual +3 or better at turn 250. Held Quarters drop
26 to 9 (two weak captures), with two operating Bakers Stage 2 chains and no
Tailors Stage 2 chain. This verifies placement selectivity in one world, not
all follow-through, building, Builder or Service capabilities.
[Full outcome and limitations](../research/mods/csc-ai-quality-placement-250-20261113.md),
[implementation and corrected assumptions](../research/mods/csc-ai-managed-placement-20261113.md).

**Admission is a separate boundary.** A valuable future Quarter site can win a
district nomination while the city has no population-limited district slot.
Native validation then rejects the request before city logging or production
competition. The first capacity adapter deferred full/unknown scopes, but a paired
phase replay confirms growth after publication left a stale negative bid during
newly available capacity. The corrected adapter retains future economic bids and
records readiness without treating it as permission to construct. UI counters
cross-check population/live inventory; extra-allowance freshness remains partially
observed. Existing construction/repair stays separate.
[Capacity trial](../research/mods/csc-ai-capacity-placement-20261113.md).
[Captured cases and limits](../research/mods/csc-ai-quarter-request-admission-20261113.md).

## From the world to a decision

```mermaid
flowchart TD
    DB["Loaded CSC rules<br/>materials, buildings, customers, adjacency"]
    LIVE["Live game facts<br/>ownership, districts, buildings, research,<br/>production, workers and purchase quotes"]
    FACTS["One player / publication snapshot<br/>EconomyFacts + shared supply reader<br/>current facts; bounded preparation estimates"]
    MODEL["Central Quarter economy<br/>EconomyModel<br/>eligible investment plans and transaction ledger"]
    PRICE["CE read-only pricing<br/>native context, site costs and yield discounting<br/>Q8 utility; unavailable is not zero"]
    SITE["Quarter bid adapter<br/>economic value + future-income investment weight<br/>timing-aware spatial preference + quality cap"]
    CAP["Current capacity facts<br/>UI used/allowed + live inventory<br/>readiness annotation; native admission remains final"]
    PROTECT["Material-protection adapter<br/>economic loss + structural safeguards<br/>last Base / Specialty and working supply"]
    PLAN["Planning adapters<br/>legal targets, frontier quotes,<br/>ownership completion and place/defer scopes"]
    SQL["Native customer-placement signal<br/>SQL private-yield adjacency<br/>one signal per mapped district–Quarter edge"]
    PACKET["Versioned CE packet<br/>bounded; refreshed each AI turn<br/>no duplicate early and complete bids"]
    CE["CE DLL / native decision boundaries<br/>refresh after aggregation and before consumers<br/>reprice retained new-Quarter requests<br/>supplier guards + ownership acknowledgement"]
    CIV["Civ compares and executes<br/>other districts, units and projects still compete<br/>native treasury, queues and worker allocation"]
    OBS["Evidence<br/>published → read / compared → selected / requested<br/>→ owned / built → actual economic benefit"]
    DB --> FACTS
    LIVE --> FACTS
    FACTS --> MODEL
    FACTS --> SPATIAL["Concrete future customer layouts<br/>native terrain quality, alternatives,<br/>distinct footprints and bounded material clumps"]
    SPATIAL --> SITE
    MODEL <--> PRICE
    MODEL --> SITE
    CE -. "bounded confirmed-choice journal" .-> INTENT["Persisted native intent<br/>selected footprint baseline,<br/>bounded lifetime and missing-input grace"]
    INTENT --> SITE
    FACTS --> CAP
    CAP --> SITE
    MODEL --> PROTECT
    FACTS --> PLAN
    DB --> SQL
    SQL --> REVERSE["Reverse generated partner graph<br/>customer → Quarter type → material classes"]
    REVERSE --> FIRST["Customer-first preparation<br/>concrete linear / triangular layouts<br/>one contribution per supplier city/type; total cap32"]
    FACTS --> FIRST
    CAP --> FIRST
    FIRST --> PACKET
    SITE --> PACKET
    PROTECT --> PACKET
    PLAN --> PACKET
    PACKET --> CE
    SQL --> CIV
    CE --> CIV
    CIV --> OBS
    OBS -. "next ordinary refresh" .-> FACTS
```

Read the central box as an economic ledger, not another controller. It records
who supplies whom, which buildings must exist, when a transaction could start,
who receives the yield, and whether it is tile income or city income. A decision
adapter asks a particular question of that ledger. A native system is preferable
where the game already exposes a suitable input, as with customer adjacency.

## Where the code lives

The active economic families are Bakers and Tailors. The shared pipeline is
reusable; the other six Quarters still need their gameplay/economic definitions
and acceptance data. All reusable CSC policy is in `Civ Supply Chains/Lua_UI/AI/`:

| Layer | Files and responsibility |
|---|---|
| UI read boundary | `Lua_UI/Adjacencies/CSC_AdjacencyUI.lua`: raw invoices, population-district allocation and UI-only cost/yield/research reads return scalars/plain records; the older exclusive-buyer screen stays separate. |
| Live facts | `CSC_AI_EconomyFacts.lua`: loaded definitions, completed customer footprints, actual buildings, research paths, construction estimates, supplier observations and per-publication caches. Capacity population/inventory is cross-checked against live claims. |
| Central rules | `CSC_AI_EconomyModel.lua`: transaction recipients, population rounding, exclusive producers, prerequisite and queue timing, bounded optional investment plans, recurring yields and marginal loss. No game writes. |
| Economic decisions | `CSC_AI_EconomyAdapters.lua`: native pricing, complete Quarter bids, weak-site policy and material-loss quotes. Managed types defer unquoted/unknown sites; unavailable economic capability retains the older policy explicitly. |
| Placement preparation | `CSC_AI_AdjacencyScan.lua`: adjacency, viable present/future footprints, quoted frontier options and poor-site/deferral facts. Future customer space can establish feasibility; it earns no speculative customer yield. |
| Existing chain decisions | `CSC_AI_QuarterPlacement.lua`: shared suppliers/chains, material deductions, exclusions, supplier acquisition, Builder and building/repair offers. Economic loss enriches protection; structural safeguards remain. |
| Publication | `CSC_AI_BakersGameplay.lua`: despite its historical name, coordinates Bakers and Tailors; refreshes and publishes one bounded packet, then reads receipts. |
| Transport | `CSC_AI_DistrictBridge.lua`: validates and publishes typed CE entries atomically. Complete Quarter bids are exclusive with the old early score adjustment for the same pair. |
| Native database input | `Data/CSC_AI_Connectors.sql`: moderate private-yield adjacency for mapped customer districts, with replacement expansion and edge deduplication; also retains the existing modest Builder controls. |
| CE mechanism | Isolated CE feature branch `codex/quarter-value-delivery`: managed-type defaults, consumer refresh, retained-request repricing and native economic quotes. CSC rules do not belong in CE. No upstream PR is submitted. |

The adjacent Builder, building, research and recovery problems remain distinct
roadmap capabilities. Keeping their working adapters does not mean the new
economic bid has solved those capabilities or priced every Service.

## Coverage of all ten sub-problems

| Problem | Model or shared fact | Decision path |
|---|---|---|
| **1.1 Materials** | Actual mapped Base/Specialty, viable improvements, working supply and tile staffing. | Quarter economic bid plus existing material-aware planning. |
| **1.2 Neighbors** | Completed mapped customer footprints and eligible future buildings; feasible future footprints remain preparation facts. | Quarter transaction ledger; no yield credited to an unbuilt customer district. City Lights mappings follow loaded rules; unsupported contracts fall back. |
| **1.3 Rivers** | Loaded river adjacency and one eligible local Mill; Wind terrain and Water river edges are alternatives. | Direct adjacency now and producer-terrain income only after its Mill. |
| **1.4 Adjacency** | Current materials, terrain and completed customers; alternative Mill geometry. | +2 minimum, +3 preferred. Latest spatial bands48/144/288/432/576 at+2/+3/+4/+5/+6+, plus bounded material/layout preferences. |
| **1.5 Tile purchase** | Native quoted footprint cost and credible supply; separate supplier-acquisition facts. | Frontier bid, native savings/payment, intended-city ownership acknowledgement and supplier purchase route. No subsidy or direct purchase is introduced. |
| **1.6 Follow-through** | Unlock estimates, native legal targets and population-limited capacity. | Native district comparison → request/tree → foundation → completion. Retained new-Quarter request values are repriced through the native tracked setter; reservations, queues and existing foundations/repairs remain native. |
| **1.7 Place or defer** | Whether a credible Base/customer path exists, with unknown distinguished from absent. | Negative managed default plus sparse positive offers. Nonpositive new investments are withheld during native placement selection; fresh facts can promote them next turn. |
| **1.8 Poor placement** | Missing Base, covering mapped materials, absent customer path and low realised adjacency. | Complete Quarter valuation, +2/no-Base gate and bounded profitable-site preferences; actual native choice and foundation quality qualify suppression. |
| **2.1 Customer placement** | Generated all-stage/tag partner graph reversed to Quarter material classes, native terrain adjacency and concrete future Quarter footprints, including triangles. | Native SQL beside built Quarters; customer-first preparation gives8–16 utility per supplier city/type, capped32 total, with exact distinct-Quarter matching, best ordinary adjacency and current customer eligibility. Quarter unlock/capacity can arrive later. City Center settlement and Wonder placement remain separate. |
| **2.2 Material protection** | Shared retained chains, last viable/working Base or Specialty, marginal lost transactions. | Existing district deductions and qualified native exclusion, Wonder and destructive-Builder guards. Economic quotes enrich rather than replace structural protection. |

This table is a code/ownership map, **not ten new completion claims**. For the
evidence and remaining native acceptance checks, read [current status](STATUS.md)
and the [numbered roadmap](roadmap.md).

## Timing, units and boundaries

The ordinary turn refresh creates one player snapshot. Static rules persist;
ownership, research, staffing, construction and quotes expire with the snapshot.
Raw invoices price all known frontier alternatives. Positive purchase guidance
still requires an unambiguous intended buyer; otherwise the complete bid is at
most zero. The CE ownership hook recognises an already-correct purchase and does
not choose Economic's buyer. Civ retains plans, reservations and execution; the managed request adapter refreshes the value of new-Quarter requests.

CE publishes a new version atomically and consumes entries when its native
decision runs. A packet is neither a reservation nor a construction command.

Recurring amounts are ordinary yield per turn. CE prices them in native **Q8
utility** (256 integer units per utility unit), using native yield weighting and
discounting. The initial model uses a 50-turn window and a 4.0 discount parameter;
these are explicit calibration assumptions. Purchase Gold is a fixed invoice,
not recurring upkeep. Production costs delay serial construction; they are not
also subtracted using an invented universal conversion.

Optional later construction must not reduce the best feasible Quarter plan.
Only one Mill is counted. Population payouts follow the gameplay registry and
receiving-city rounding. Improved but unworked material tiles feed a producer
without earning assumed citizen-worked tile payouts. The bid includes observed
worked-footprint income displaced by the new Quarter.

The ledger is deliberately incomplete: future specialists, trade-route changes,
Service-specific premiums and perfect empire-wide construction scheduling are
not priced. It supports the current unit-transfer contract and checks the loaded
leaf amounts; a changed unsupported contract is reported rather than guessed.
City Lights and other optional integrations require their own acceptance data.

For a managed Quarter type, unknown or omitted sites receive a negative default,
not an untouched native building premium. The adapter quotes revealed owned
and frontier radius-three potential without requiring a current BUILD menu
entry. Native eligibility, invalid sentinels and legality remain authoritative.
Sparse positive offers can be trimmed at capacity while retaining the defaults;
material protection keeps precedence. Missing economic capability is separately
logged and keeps the established non-economic path rather than claiming whole
valuation. Existing district foundations/repairs are outside new-investment
ownership, determined from the actual city district collection. Row+50 is
improvement presence; row+51 omits incomplete/pillaged districts. Neither
cached flag is an adequate exemption.

CE refreshes the matrix after aggregation and immediately before joint selection,
type-specific location selection and present-value reads. A reserved tile can be
priced: Civ still applies its reservation thresholds. GetBest can choose negative
scores, so nonpositive managed new investments are temporarily masked and every
byte restored afterwards. Location also respects critical supplier exclusions.

Native UnitRequestContract.Update keeps max(previous,current). An additional
post-update adapter rebases only managed new-Quarter requests through the native
tracked-value setter. Building/unit branches, invalid updates and existing
footprints remain native. Locationless requests use the native zero-floored
column maximum, with an existing-Quarter guard. This changes the offer, never
creates a request or cancels a reservation.

The preference estimates remain96/192/288/384 native utility for profitable
+3/+4/+5/+6+ alternatives, plus16 for both material classes. A +2 site is now
eligible without an adjacency premium. These preferences cannot make a
loss-making investment positive. Mill alternatives are ranked on the final
placement bid, so a profitable Wind+3 option can beat an earlier Water+2 option.
These bands need outcome calibration; they are not inferred exact vanilla prices.

Each native pass is bounded to37 rows and at most16 managed types per player.
No hook calls Lua. Counters distinguish delivery, masks, reserved-cell writes and
retained-request changes and report native processing time. Managed samples are
lossy/bounded (2048 per packet), separate from legacy write budgets and reserve
half the core journal for other evidence. Dropped samples are explicit; missing
samples must not be called absence of delivery. Performance and actual native
consumption remain live qualification requirements for this candidate.

## How we judge a change

Separate the layers of evidence: a ledger can be correct while an offer is never
consumed; a consumed offer can lose; a winning request can wait; a completed
building can still lack supplies or customers. Diagnostics and controlled tests
must identify the layer reached. Outcome games use only main CSC tuning, the
shared controller and pinned packages. Their results determine calibration and
remaining weaknesses; the diagram alone proves none of those outcomes.


### Initial runtime qualification

The fresh three-turn smoke (`csc-ai-economy-20261113/smoke03`) qualified native
pricing for all five AI cities and restored preferences/packages with exit0.
Both pricing and final interfaces reported ready. **No complete economic bid
was demonstrated:** Quarter readiness was unavailable, so established guidance
remained active. That result exposed the fact-binding gap; the next revision
adds explicit UI-only numeric reads and separates raw invoices from the
exclusive-buyer screen. The corrected 30-turn window demonstrates repeated
complete bids and native consumption; the final review revision repeats the
native acceptance in a fresh 3-turn smoke with 16 exact write/cache/comparison
receipts. [Full audit](../research/mods/csc-ai-central-economy-20261113.md).
Neither window establishes improved placement or Services.

### First long outcome test

The completed normal Online250 run confirms continued publication and native
consumption, but not the intended placement quality: 26 completed Quarters,
8 currently at +3 or better, 4 at +4 or better, one active Bakers Stage 2 chain
and no Tailors chain. Readiness and architecture coverage are not outcome
closure. The next diagnostic records foundation/completion geometry and the
actual native winning score, separating retained-plan timing from valuation
and later material loss. [Measurements and limitations](../research/mods/csc-ai-economy-250-20261113.md).
