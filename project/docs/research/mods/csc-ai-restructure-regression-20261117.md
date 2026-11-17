# Post-restructure Continents regression

**Completed turn250 and closed/restored normally.** The restructured package
still delivers Quarter bids and customer adjustments. Government and Policies
both opened and closed in the actual BRS/EPC UI at25, without Lua errors.
Finding **AI-C209**; [compact results](csc-ai-restructure-regression-20261117.json).

## Outcome and previous-run comparison

| Measure | Previous ordinary-economy run | Post-restructure run |
|---|---:|---:|
| Bakers / Tailors foundations |17 /5|16 /7|
| Base-adjacent foundations |22/22|23/23|
| Rated+3 or better |20|21|
| Rated+4 or better |7|7|
| Both material classes at foundation |5|3|
| Completed Bakers / Tailors held at250 |15 /4|14 /5|
| Active Storekeepers / Innkeepers at250 |8 /2|8 /3|
| Active Dockmasters / Sacristans at250 |0 /0|0 /0|
| Native Storekeeper chain-turns |1,101|1,031|
| Customer economic score writes, sampled |1,587|1,204|
| Guidance average / maximum, all five AIs |2.03s /4.61s|1.97s /3.86s|

All36 observed native new-Quarter BEST values exactly match published bids.
22/23 foundations tie the best physical rating among their city/type packet's
positive offers. The remaining Tailors foundation (player3,plot2387,turn207)
has no matching positive packet metadata and needs reservation/delivery follow-up.
250 turn publications have complete wall-time coverage and zero
failed attempts; no policy/planning faults or Lua runtime errors are recorded.
Native managed refresh separately averages14.15ms, maximum35.74ms.

At250 all five Tailors have working Workshops and improved Base; none has an
adjacent Harbor. Bakers have13 working Stage2 producers, nine working adjacent
customer buildings and eight physically complete Stage2 chains. Stage4 Service
properties remain zero. One original AI was eliminated; totals include its
earlier construction, while endpoint inventory reflects surviving ownership.

This is a useful package/behavior regression against the same initial world.
Complete play diverged, and the new run adds BRS/EPC for its UI check. Small
outcome differences should guide the next investigation rather than be assigned
to unchanged tuning coefficients. Quarter/customer delivery remains active.

### How customer guidance connects

There are24 distinct Quarter/customer-provider district links, excluding18 City
Center links.15 customers follow their Quarter; nine precede it. Eleven distinct
customer foundations record the SQL private placement yield. Five links have a
prior Lua economic proposal at that customer plot. Two match the exact reverse
customer-first planned Quarter footprint; two match the latest logged forward
Quarter layout. A link can satisfy multiple measures; these counts do not add.
The previous run's corresponding counts are20 links,13/7 order,10 SQL readings,
seven prior economic offers and one exact match in each planning direction.

Both directions therefore meet in real construction, with incomplete persistence
between them. The exact forward measure covers the leading two logged Quarter
offers only. Lua economic delivery has1,204 native writes, two sampled site-win
windows and zero readback errors. The diagnostic totals record38 unavailable
reference quotes,18 unavailable native quotes,141 nonpositive native candidates
and858 unvisited groups within the existing work budget. None was classified
as a missing candidate-world quote. Preserve bounded work; investigate coverage
and durable joint layouts before increasing blanket customer incentives.

The new passive diagnostics produced49 Quarter funnel summaries,337 already-
priced alternative records and576 Harbor-neighbour records. None of those
Harbor-neighbour cells is water: the built Tailors are inland. Raising a native
Harbor adjacency bonus cannot make a Harbor legal beside those Quarters.
Across the sampled funnel visits, rejection totals are6,797 below-adjacency,
1,247 no-Base,61 economics,13 missing facts and10 ambiguous buyer;160 visits are
positive. These are repeated candidate visits, not distinct missed sites.

### Material retention, acquisition and empire output

The15 material-loss observations comprise six pillages, six ownership changes,
two improvement removals/changes with resources retained, and one Wheat removal
for a Wonder at48. That Wheat was a non-last Base deposit. No voluntary
last-material resource destruction is observed. Native managed exclusion masks
are active in227 turn windows.

Native purchases spend10,860Gold on116 tiles, all debit/ownership confirmed;
two purchases match Quarter sites. Savings offers/receipts are preserved in the
raw financial record. The endpoint's five-seat average is582.40Production,
1,027.80gross Gold,366.40net Gold and67.80food surplus per turn, versus the prior
512.78/1,038.50/423.50/63.41. These reflect the diverged empires and warfare;
the JSON retains all ten25-turn economic samples for later balancing.

[Dockmaster map survey](csc-dockmaster-opportunity-survey-20261117.md) follows
with zero-turn inspections and earlier-map comparison. No resource-placement or
guidance values change as part of this regression.

## Run qualification

17 November2026. Henno authorized one fresh Continents game to250 and requested
the additional opportunity diagnostics. Use the previous Continents map/game
seeds18461107/29461107, Small/Prince/Online, same original AI seats, City Lights,
Resourceful2 and Sukritact's Resources. Main CSC provides all tuning; the shared
controller and passive observers record play with15-minute check-ins.

Keep the qualified CE DLL `b7194a83569283033a7c9687ae6d92c33cef7b7d04daaf8e115c641077cd7da9`.
Before this run, upstream develop/master still resolve to2986a746/e59b5aa9.
No upstream PR or native rebuild is involved.

## Frozen inputs and build

Output root: `Desktop/Codex/csc-ai-restructure-regression-20261117`.
The new freeze helper reads committed Content and project actions, runs the real
SDK Content copy/GenerateModInfo build, and reuses the comparison package's
cooked art. This checks source/action packaging without recooking unchanged art
or sweeping unrelated workspace edits into the game. Its freeze manifest records
the source commit and all Content hashes. The shared controller owns installation
and restoration. This is a source/action regression, not art-cooker qualification.

Eight AI module comparisons against the prior freeze found only Facts/Adapters
changed, for the diagnostic additions below. No tuning values or decisions were
changed. The other gameplay changes are the reviewed SQL organization and
startup/action fixes described in the shared-SQL documentation.

## Added passive diagnostics

- `CSC_AI_CUSTOMER_ECONOMIC_GAPS`: distinguishes missing reference/candidate
  world quotes from missing/nonpositive native raw site values, and records
  groups not visited within the existing work budget.
- `CSC_AI_CUSTOMER_ALTERNATIVE`: every25 turns, records each already-priced
  alternative, its reference, ordinary adjacency, signed delta and outcome,
  including zero-difference and rejected-native-gate cases.
- `CSC_AI_CUSTOMER_OPPORTUNITY`: every25 turns, up to96 adjacent cells/player
  for existing Quarters mapped to Harbors/unique Harbors. Records water/lake,
  ownership, occupancy, resource/protection, observed unlock/native admission,
  cached ordinary adjacency and reference. `native=-1` means admission was not
  queried; it is not an illegal-site verdict. No extra native quotes/scans.
- `CSC_AI_QUARTER_FUNNEL`: every25 turns, counts existing candidate evaluation
  outcomes and samples up to8 rejected identities/player, preferring the best
  adjacency within each reason. Existing score/native/production/purchase and
  placement observers complete the follow-through trace.

No diagnostic publishes a bid, mutates a plan or changes candidate ordering.
Whole-publisher/native timing remains enabled.126 economy checks pass, including
split reason counters, bounded funnel output and unchanged coast-query counts.

## Government-screen regression

BRS and EPC are added as explicitly pinned UI dependencies for this check; they
were not in the old three-game optional-mod stack. Initial map/leader/unit parity
is still required. At the first inactive boundary at/after25, the shared driver
opens Government and Policies via their actual callbacks for observer0, waits
for animation and closes the unedited screen. It captures the transcript and
new Lua errors, checks the original RMA API and CSC attachment marker. No card or
government is selected, no civic granted, and no studied-player orders issued.
The run stops for diagnosis if this UI check fails.

## Required comparison

Fresh SQL validation/loaded definitions, initial world parity, packet/receipt
coverage, opportunity funnels, Quarter/customer chronology, Base/Spec retention,
buildings/all Services, production/Gold/food-surplus trajectory, and average/max
guidance time. The reference is the completed ordinary-economy Continents250,
not a newly labelled untuned baseline. Extra UI dependencies are recorded.
Do not automatically start Pangaea/Fractal after this one game.

Status: `continents250-02` completed250, closed exit0 and restored preferences.
Initial map/AI/start/unit parity passed.
The Government and Policies pages both opened and closed successfully at25,
with no new Lua errors. BRS initialized normally and CSC confirmed attachment.
`government-screen-check.json` and its transcript/log delta preserve this proof.
SDK source commit is `d6a9114a`, with276 committed Content inputs and the same
qualified CE hash. The package uses the prior controller test identity, leaving
the user's installed CSC distinct; this changes no content or policy.

The first launch preflight stopped before creating a game because the historical
driver required a CE dependency in CSC's manifest. Main CSC correctly keeps CE
optional behind its criterion. The explicit main-package driver option now
verifies that criterion against the pinned CE identity instead; runtime native
capability qualification remains mandatory. Connector detection follows the SQL
file, including its consolidated name, rather than relying on an action ID.

The initial same-ID package was also rejected by the duplicate-entry guard in
the main menu. The owned process was closed through shared-session recovery;
original mod-ID flags were verified and its temporary alias packages retired.
No turns/game were created on that attempt. The replacement package uses SDK's
Guid property to produce the established distinct regression identity. A
separate reference-source option verifies initial world parity without treating
this source-regression comparison as an opposite-policy untuned arm.

Henno additionally requested final counts showing how the two planning
directions meet: exact Quarter-planned customer footprints realized, reverse
customer-first footprints later receiving Quarters, native SQL private-yield
readings at customer foundation, prior Lua economic offers and physical links.
`customer_coordination_results.py` joins those separately and excludes City
Centers from influence counts. Read-only Dockmaster opportunity surveys of this
and earlier maps follow; do not change resource generation in the running game.
