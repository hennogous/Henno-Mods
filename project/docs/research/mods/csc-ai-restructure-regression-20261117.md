# Post-restructure Continents regression

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

Status: `continents250-02` is running. Initial map/AI/start/unit parity passed.
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
