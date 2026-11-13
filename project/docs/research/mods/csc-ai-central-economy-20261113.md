# Central Quarter economy and late bids — 13 November 2026

Read the [architecture guide and diagram](../../civ6-ai/architecture.md) first.
This is the evidence record for its implementation, covering Problems **1.1–1.8
and 2.1–2.2**. The old automatic goal remains paused.

## Result and scope

Main CSC now contains a shared live-facts adapter, a pure transaction model and
decision adapters. Quarter valuation uses a complete CSC bid after native
building aggregation. It no longer stacks the old positive adjacency preference
with Civ's future-building premium for the same pair. Native competition with
other districts, units and projects remains native.

The new path is qualified through actual native writes, cache reads and eligible
district comparisons. **No improved placement, completed investment or Service
result is claimed from these short windows.** Earlier representative purchase,
follow-through, deferral and material-protection results retain their tested
version/scope; they are not new outcome evidence for this economic valuation.

## Implementation

- `CSC_AI_EconomyFacts.lua` reads actual definitions, current ownership and
  completed district footprints, unique building replacements, native costs,
  research progress and current rates, staffing and supply. UI-only methods use
  explicit read-only wrappers; snapshot caches expire each publication.
- `CSC_AI_EconomyModel.lua` records direct adjacency and reciprocal returns,
  local Mill terrain, material/producer/customer transactions, maintenance,
  displaced worked-footprint income, population payouts and eligible amenities.
  It chooses one alternative Mill and serialises each city's construction,
  including missing ordinary building prerequisites. Optional later investments
  cannot worsen the best available plan. Stage 3 uses property-level receiving
  city rounding and existing other-seller targets; regional same-building
  amenities do not stack on already-served recipients.
- `CSC_AI_EconomyAdapters.lua` uses native read-only yield, fixed-amount and
  amenity pricing, then applies bounded placement policy. It prices all admitted
  owned and revealed frontier candidates coherently. Raw land invoices are
  separate from buyer eligibility: a positive frontier bid still needs the
  established unambiguous-buyer screen. Otherwise its complete value is at most
  zero. Native acknowledgement only recognises ownership after it exists; it
  does not select Economic's buyer.
- The existing publisher, bridge, planning and protection adapters remain main
  CSC code. Shared chain facts and marginal economic loss enrich protection,
  including resource adjacency lost when a district removes the deposit.
  Structural last-deposit/working-Service safeguards remain. If any quote is
  unknown, or complete coverage would exceed the packet budget, retain coherent
  earlier guidance rather than partially mixing score systems.
- Native SQL customer adjacency now deduplicates all mapped Stage 2–4 ordinary
  district edges and expands direct unique replacements. City Center settlement
  and Wonder placement are different consumers. The earlier native Stage 2
  consumption evidence remains; no new isolated Stage 3/4 choice is claimed.

The initial assumptions are explicit: a 50-turn horizon, discount parameter 4.0,
current research/production rates, current population and an initial five-turn
supplier-job allowance. Only completed customer districts earn forecast exchange
income. The model supports current unit-transfer leaves and checks their loaded
amounts; it does not infer arbitrary changed modifier graphs. Future specialist,
trade-route and Service premiums are omitted. These are calibration/coverage
limits, not silent native credits left in the complete Quarter bid.

## CE mechanism and maintainability

Isolated fork branch **`codex/quarter-economy-forecast`**, commit **`6f53037`**, from
the latest tested ownership base `e4f3228`. No upstream pull request was created.
WildW's `develop` remained `2986a746b396eb93aad14f9afffb043a09c2c489` at preflight.

The generic API adds complete final entries plus native recurring-yield,
fixed-amount and amenity quotes. It uses CE's existing Runtime aggregation hook,
HavokScript registration and lifecycle. No new raw MinHook calls or CSC policy
are introduced in CE. Named RVAs/layouts, typed native ABIs, full binary identity,
helper fingerprints, input bounds and nil-on-unavailable behaviour are documented
beside the code and in `native/README.md`.

Supported Windows XP2 SHA256:
`092abfbb2176f8df04b5212f819dc269dd83aea866ff05aaf489904a1ff7c41f`.
Reference Ghidra image `324c51e9…` has matching relevant text. DX11 executable:
`d1a0cfd439e7451be515f47595cfa0b6b983f56d1faf4ea434a4ce3b21491ebe`.
Built CE DLL:
`09d51ddd0c471959b8f0ebece33b30bf0758201b79928696610cd82597bdcdc9`.

The supported MSVC project builds successfully with the existing pinned MinHook
library staged in its expected ignored local path. This adds no alternative
build approach. Existing upstream compiler/link warnings remain outside this
feature. Native tests pass **184 district checks**, **4 Runtime hook-group
cases**, and instruction-call delivery/restoration.

## Controlled runtime evidence

Artifact root: `C:/Users/Shadow/Desktop/Codex/csc-ai-economy-20261113/`.
All windows use the shared controller, normal fresh Small Continents, Online
speed, seeds 18461107/29461107, original AI players 1–5. The temporary package is a
complete main CSC build with its local carrier identity and CE dependency; it
contains no separate AI test policy, Frida, forced unlocks or world edits.
Diagnostic endpoint reads change no bids or gameplay state. The human installed
CSC and original mod preferences are restored; temporary Mods folders are retired
into the corresponding artifact directory after native exit.

| Window | Revision and result |
|---|---|
| `smoke03` | Initial bindings, fresh through turn 3. Native quote API qualifies for all five AI cities, but every Quarter readiness quote is unavailable. Legacy guidance remains active. This negative exposed the UI-binding gap. Exit0/restoration pass. |
| `smoke30` | `frozen02`, corrected UI numeric reads/raw invoice boundary, through turn 30. Actual complete bids and native consumption; measured below. This revision predates the final buyer-screen/partial-data/direct-loss review fixes. Exit0/restoration pass. |
| `smoke03-final` | `frozen03`, final review fixes, fresh through turn 3. All 8 main AI/UI source files match the recorded source hashes. Native price/fact preflights pass for all five AI cities. Sixteen exact receipts show sixteen writes, cache reads and eligible city comparisons; no site win is claimed. Exit0/restoration pass. |

In the final smoke, all five players have known quotes at turn 3:12/12,12/12,
14/14, 16/16 and 8/8 final values, respectively. There are no unknown quotes.
Actual Production and Quarter cost reads work; Craftsmanship is still locked,
with current-rate estimates of 22, 22, 22, 13 and 23 turns. No unlock is granted.
`RequiresPopulation=1/true` is verified from the loaded gameplay definitions
for both Quarters. Native slot-constrained normal-play outcomes remain to measure.

Exact receipt in both accepted revisions: player1/city65536/Bakers36/plot985,
version 2, whole bid **−70,076 Q8**. The next ordinary refresh reads:
`staged=1, scoreAttempts=1, writes=1, cacheReads=1, cacheEligible=1,
citySelections=1, siteWins=0`. This proves write/consumption at that scope,
including a negative complete value; it does not prove a better site won.

### Thirty-turn audit

`smoke30-audit.json` is reconstructed from archived raw logs and exact receipts:

| Measurement | Recorded value |
|---|---:|
| Publications |30 |
| Player plans / plans containing final values |150 /144 |
| Complete entries published across refreshes |4,628 |
| Largest packet / shared capacity |304 /4,096 |
| Unknown quotes / omitted entries / recorded policy failures |0 /0 /0 |
| Bounded exact-pair receipts |448 |
| Receipts with a write |413 |
| Receipts with cache reads |448 |
| Receipts with a city selection/comparison |49 |
| Site wins in those bounded receipts |0 |
| Aggregate previous-packet matched/changed score calls |3,696 /3,696 |
| Largest coarse logged publication duration |1second |

Counts across refreshes are repeated offers, not unique sites or investments.
The older `CSC_AI_BAKERS_PLACEMENT.bids` counter counts early positive deltas;
it excludes complete economic entries. Use `CSC_AI_ECONOMY_PLAN.final` and the
exact economic receipts for this path, not that legacy counter.
Receipt logging is bounded and samples early identities; zero wins there is not
a census of all players' choices. Aggregate score counters can include retained
non-final guidance and are not labelled 4,628 final writes. Endpoint version30
has zero counters because it is freshly published at the inactive boundary;
earlier receipts establish consumption. The small early empire and coarse timer
do not qualify mature-empire performance or balance.

Read-only native price example (same world, horizon 50, ready 0, discountQ8=1024):
1Production/turn→6,435Q8; a one-off−70Gold invoice→−10,745Q8 for four players,
−12,530Q8 for the fifth; 1Amenity→5,148Q8. Invalid yield/time/city returns nil.
These are fixture observations, not universal bid constants. Reusable engine
knowledge is recorded as **AI-N123** in the maintained `civ6-ai` skill.

## Review, regressions and remaining work

Astra independently reviews the code and diagram against all ten sub-problems,
reproduces 22 economic/fact/boundary tests and finds no remaining blocker in this
scope. Its corrections include optional investment selection, queue/prerequisite
timing, Q8 property aggregation/baselines, amenity stacking, footprint loss,
coherent frontier coverage, buyer eligibility and partial UI fallbacks.

Local verification additionally passes 15 real-publisher/CE bridge checks,
28 adjacency scanner checks, the actual district INSERT capacity regression,
ModBuddy action regeneration and scoped whitespace checks. The overflow fixture
deliberately supplies 4,097 economic entries and verifies whole-publication
fallback before trimming, keeping the established native/protection packet.

Still separate: normal longer-game placement quality, strong-site win rates,
paid acquisition with these new values, retained-plan/quote changes, mature
performance, City Lights acceptance, complete Service economics and balance.
No new full outcome game is launched by this change. The next experiment can
measure the revised Quarter investments, not spend another run merely proving
that a staged offer reached the late decision boundary.
