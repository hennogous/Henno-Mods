# Service-aware foundation planning

22 October 2026. The previous three-world study is closed by the human;
its monitor has been deleted and its original runtime/settings restored. Its
outcomes and executed hashes remain immutable. The human separately authorized
building/testing a first version of this Service-aware approach, including more
forward real-gold acquisition for strongly aligned Services. The prototype below
has offline verification; no live purchases or new worlds have been executed.

## Corrected immediate rules

An existing or unfinished Quarter blocks another copy of that same Quarter type
in its city. An unfinished different Quarter is not a custom exclusion; the
native build rules, district capacity and exact target legality still apply.
Keep the one-foundation-per-city-per-scan intervention limit for now. That is a
scheduling limit, not a statement that different unfinished Quarters are illegal.

Retain the existing preference for both Base and Specialty, then rank by Base
count, total material count, plot index and Quarter key. Thus two Base plus one
Specialty beats one Base plus four Specialty. A Both-class site still outranks a
Base-only site under this immediate standalone revision. The Service-aware v1
below now replaces that universal Both preference with a stage-specific supply
test when using the new policy package; historical study inputs stay unchanged.

Maintained next-version source:
`project/tools/ai_baseline/foundation_planner.lua`. It derives from the executed
`csc-dynamic-diag-probe.lua`, changing the two policies above only. The old H
driver input and archived executed source remain unchanged. A future driver must
explicitly bind and pin the maintained source; resuming the paused study does not
silently switch its treatment. Native/UI legality and cost verification remain
driver responsibilities. No installed mod action references the new file.

`test_foundation_planner.py` runs the actual Lua file in an existing Lua5.1
runtime with simulated city/plot objects. Twelve fixtures pass, including an
unfinished different Quarter, duplicate rejection, Base-before-total ranking,
retained Both preference, stale-commit rejection and zero-progress commitment.
This is offline verification, not native reliability or gameplay benefit proof.

## Choose an intended Service before scoring a site

Prefer a small, data-driven Service profile for each implemented Service. Each
profile needs its actual producing building, material classes/improvements,
unlock research, exact customer building, source/customer adjacency and benefit
recipients. A suitable Quarter site must support the intended chain at that
site; materials and customers elsewhere in the empire cannot be pooled.

Initial Bakers/Tailors mapping, based on current SQL/localization:

| Demand | Service route | Supply gate | Customer and research |
|---|---|---|---|
| Naval production | Dockmaster, Textile Workshop | Improved Base; Specialty optional | Adjacent Harbor with Lighthouse; Naval Tradition. Current naval production benefit covers Renaissance and earlier naval units. |
| Growth | Storekeeper, Mill | Improved Base; Specialty optional | Adjacent City Center with Granary; Feudalism. |
| Housing / larger cities | Innkeeper, Bakery | Improved Base; Specialty optional | Adjacent Commercial Hub with Market; Medieval Faires. |
| Faith / religion | Sacristan, Tailor | Improved Base; Specialty optional | Adjacent Holy Site with Temple; Divine Right. |
| Culture / tourism | Groundskeeper or Ride Technician, Cafe | Improved Base and Specialty at the same source | Adjacent Zoo or Ferris Wheel; Urbanization. |
| Culture / tourism | Stage Manager and performance-Wonder variants, Fashion House | Improved Base and Specialty at the same source | Adjacent Amphitheater or the supported performance Wonder; Opera and Ballet. Preserve exact Wonder host rules. |

Start with implemented Services. Other Quarter stubs need complete contracts
before assigning them speculative benefits. Early routes should accept good
Base-only sites; Specialty can be an upgrade option rather than displacing an
otherwise useful growth/naval Service. Later cultural routes need both classes.

Agendas, strategic priorities and current city demand are different signals.
Use actual readable native priorities when available, city constraints and
production context next, and leader/agenda identity as a weak prior. Multiple
goals may coexist. Do not label an inferred naval preference an observed active
native strategy. `GetGrandStrategicAI()` is exposed in the UI, but its documented
methods return research/settlement recommendations, not a generic list of active
naval/growth/victory strategies. A dependable strategy-read adapter is a separate
verification task; callbacks proving our own strategy conditions are evaluated
do not establish that generic native-state access.

Suggested explanation-friendly score: value of the intended Service for the
city/player, multiplied by confidence that the chain can be completed, less
production, research delay, land acquisition, danger and displacement costs.
Within otherwise comparable plans, Base count precedes Specialty count. Give
credit for existing customers and protect valuable future Campus/Harbor/etc.
sites. Avoid an unrestricted ranking of yields with incomparable units.

## Material preservation

Current `Data/CSC_AI.sql` already adds an AI-only private presence signal of40
and an improvement-owned marginal80 on matching resource improvements beside
the corresponding owned Quarter. It uses `Improvement_ValidResources`, exact
material/visibility and a player-district existence/adjacency test. The adjacent
Quarter gate does not require completion. Historical19October native sampling
included constructing/pillaged sources; this effect application is not proof
that the prospective Builder or harvest score forecasts the value correctly.
Read-only verification of Game2's archived native database found all21
improvement-owned modifiers with Amount80, confirming that this is not merely
an uninstalled source proposal.

First separate three decisions: build the appropriate improvement, retain the
material instead of harvesting, and keep the material tile under the source's
owner. An increase to an improvement value may affect the first without solving
the second. Pillage and border/capture losses are separate again. Prefer a
future harvest/preservation signal that values the downstream chain and makes
the last qualifying Base especially valuable. A second Base supplies redundancy.
Do not globally forbid harvesting, invent a modifier that the engine does not
consume, add real yields merely as AI bait, or alter resources automatically.
Any proposed bias needs separate evidence of the intended decision response.

Game2 read-only endpoint breakdown supports checking persistence separately:
16/16 assisted sites had Base when placed and4/16 had Both. Fifteen assisted
completed sites were in the major-AI endpoint census; eight retained Base and
four Both. The54 natural sites had six Base and one Both. Of the seven assisted
sites in that census losing Base, six lost their original sheep/cattle resource
connection (some shared a source plot); one lost access to a resource under a
different owner. Raw resource disappearance is consistent with harvesting but
does not identify every removal action. The other assisted Quarter remains
under non-major owner62 and is outside this endpoint denominator.

## Two evaluation schedules

1. Rebuild wider city plans every5–10 turns and on founding/capture, relevant
   unlocks, strategy/need changes and major map changes. Consider revealed,
   plausibly acquirable land within actual city development reach, including
   tiles outside today's borders. Unowned resources are future dependencies,
   not current supply. Reject rival territory, unseen resources and invalid
   terrain; discount future clearing/ownership rather than pretending native
   `CanProduce` makes an unowned site ready now.
2. Use tile-ownership/purchase events to mark affected cities dirty; coalesce
   repeated events. Check only their cached plans, with one light fallback per
   AI turn. Commit at a defined safe gameplay point after ownership and city
   plot collections settle, never recursively inside every UI event. Shipped
   `AdjacencyBonusSupport.lua` explicitly warns that the purchased-plot list can
   lag `CityMadePurchase`. Events are hints; fresh ownership/native legality is
   authoritative. Invalidate on lost materials, another district commitment or
   competing plan claiming the tile.

For persistent gameplay, ownership checks and mutation belong to an authoritative
gameplay path; UI recommendations can inform it through a deliberate bridge.
Event availability/ordering for all AI players and multiplayer needs validation.
An in-game event scheduler could remove repeated external five-turn handoffs;
that is a later integration change, not a reason to restart this paused study.

## Optional land acquisition

Treat buying tiles as a distinct policy from placing a free0%-production
foundation. Affordability alone is not enough: reserve defensive/maintenance
cash, assess the entire acquisition path (Quarter tile, required materials,
customer access), bound per-city/per-player purchases, avoid contested frontiers
and imminent natural expansion, and require the expected Service benefit to
justify the cost. Start by buying only the final missing link for a high-value,
otherwise-ready chain. Use native purchase commands/costs and actual gold
deduction, followed by readback; never emulate purchasing with ownership grants.

Shipped UI uses `CityManager.CanStartCommand` and `RequestCommand` for plot
purchases and `CityGold:GetPlotPurchaseCost`. This establishes an existing
purchase path, not that an external command can safely purchase for every AI or
that its multiplayer authority is validated. Keep it disabled until separately
implemented and approved for a future run. If developed, compare it separately
from the foundation-only policy so gold-spending effects stay identifiable.

## Evidence and next implementation boundary

- Current sources: `Data/CSC_AI.sql`, Bakers/Tailors SQL and localization;
  `project/tools/ai_baseline/paired_observer.lua`.
- Historical mechanism/result limits:
  [improvement-owned signals](csc-ai-improvement-research-20261019.md) and
  [native research goals](csc-native-civic-goals-findings-20261020.md).
- [Documented grand-strategy interface](https://sukritact.github.io/Civilization-VI-Modding-Knowledge-Base/AiGrandStrategic)
  and [ownership/purchase events](https://sukritact.github.io/Civilization-VI-Modding-Knowledge-Base/Events).
- Shipped local sources inspected: `Base/Assets/UI/WorldView/PlotInfo.lua`,
  `Base/Assets/UI/AdjacencyBonusSupport.lua`, `Choosers/CivicsChooser.lua`.

The two immediate offline planner rules and the Service-aware v1 prototype
below are implemented. The old study is closed. Broader persistent mod event
registration, a native world-reader adapter and native integration verification
remain separate from the tested policy/transaction core.


## First version built: strongly aligned Service acquisition

Human direction: when an available tile can unlock a Service particularly
well aligned with player needs, purchase more readily with real gold than for a
general-purpose good Quarter site. Affordability alone is not sufficient.

Maintained package: `project/tools/ai_baseline/service_planner/`. The policy has
eight implemented Service route profiles (including performance-Wonder hosts),
an observed/inferred need adapter, normalized observation-to-candidate builder,
five-turn wide-scan cache, cheap refresh/coalesced dirty events, a safe-boundary
coordinator and a single-shot native purchase bridge through the shared runner.
It delegates0%foundation creation to the existing validated driver transaction.

V1 strong tier: need strength>=0.8, need and chain confidence>=0.75, existing
functioning customer, Service research already unlocked, and a credible chain
within20turns. It may buy Base-only for stage2/3. Stage4 requires both material
classes. A Service-aligned Base-only plan can outrank a general Both plan.
Base count then precedes Specialty count within comparable plans.

| Setting | Strongly aligned Service | General-purpose site |
|---|---:|---:|
|Share of gold left after reserve|25%|8%|
|Single-purchase ceiling|200gold|60gold|
|Example:600gold,150reserve|112gold allowance|36gold allowance|

The example80gold tile is purchased for a strong naval Service but deferred for
the general-purpose alternative. Weak agenda evidence does not earn the strong
budget. These are initial explicit policy values, not calibrated return-on-gold
estimates. Reserve is the largest of150gold, a driver emergency budget or10turns
of current deficit. Recent spending, city cooldown10turns and a player cap of
2purchases/5turns apply. Only one final missing tile can be bought in v1; all
remaining supply/customer dependencies must be owned. The tile may be the
Quarter site or its last missing material. No speculative acquisition chains,
contested/unrevealed purchases or free land/gold grants.

Native purchase Lua rechecks owner/AI identity, same-type Quarter exclusion,
visible projected supply, customer function/adjacency, research for the strong
tier, current price/gold/reserve, potential district legality and native command
permission. It requests one native PURCHASE. Before-send fsynced journal,
pending-state replay, exact ownership+treasury readback and no automatic resend
cover lost acknowledgments/restarts. Foundation placement happens only on a
later fresh owned-land check. An attempted foundation is journaled before the
delegated mutation and cannot be automatically replayed after ambiguity.

Validation:59offline checks pass, including the actual purchase Lua in Lua5.1
against a simulated engine, observation building, need tiers, hidden/lost supply,
stage4 gating, native denials/stale quotes, real-command-shaped gold deduction
readback, restarts and purchase-before-placement sequencing. All profile civic
and venue identifiers match the archived native database. Existing same-type
foundation planner retains its independent12Lua checks. Output evidence is in
`Desktop/Codex/csc-service-aware-foundation-v1-20261022`.

This does not establish live AI-owner PURCHASE authority or unowned projected
site legality. The driver must still bind native world/price/need readers and
discover the live plot-purchase parameter; unknown facts block spending. No
native world collector or permanent mod event registration is installed. No
game was launched and no live gold was spent. Additional material preservation
weights were not changed in this version. Native integration and natural-game
performance must be measured separately before promotion.


## Authorized first native game

Human requested “run a game” after closing the previous study. One separate
Ancient1→250 Online/Prince Small Continents-script (`Continents.lua`) world uses
830203/940207 and the Pachacuti/Saladin/Sejong/Elizabeth/Matthias/Kristina roster.
The installed mod is a newer510-file build, archived unchanged; the old528-file
art overlay is not reused. Actual native1 and5 are verified. This is a new
descriptive test, not a continuation or a matched causal comparison.

Live collector reads five AI cities at5, and the native purchase parameter is
-780910418. Gameplay owns exact venue locations; UI supplies operations/costs.
The bridge is refreshed before purchasing. Service readiness includes current
production delay and requires improved Base (and Specialty for stage4) for an
aggressive purchase. Uncertain setup remains a general/watch opportunity.
No gold grants, ownership setters, forced orders or extra research overlays.
Actual AI purchase authority remains pending a qualifying transaction; no ACK
or offline fixture is counted as real gold spending. Plans/actions/rejections,
raw facts, research, Builders, placement0%-proof and process evidence are saved
under Desktop/Codex/csc-service-aware-foundation-v1-20261022/run-01.


### First native game stopped18 before first commitment

The generated UI preflight passed CanProduce's native boolean+reason-table
returns directly into Civ's typed assert, which rejects a non-string message.
It stopped before any zero-progress commit/purchase. Native18save and full
failure exports are preserved, settings/current510 restored; no native crash
observed. After independently verifying controller exits, changed the adapter
to local booleans with explicit messages and relative package imports. Actual
generated-code regression reproduces the old failure and passes both repaired
true/false checks;63offline checks pass. Continuation of the same18world awaits
human choice under the explicit no-automatic-recovery rule. No rerun/load/new
world has been executed. See run-01/independent-turn18-preflight-review.json.


### Explicit same-world18 continuation

Human chose “Continue the same world from turn 18”. New output branch
run-01/resume-018-preflight-v2 preserves the ended original. It loads the exact
archived18save once, uses the repaired maintained adapter and canonical finite
controller, and checks physical/research/nativeDB/current510 and all recorded
production/timing/treasury parity before action. No sites are reconstructed or
earlier AIturns replayed.85research rows1..17 and observer prefixes are inherited
once; policy cache is freshly built at18. Original raw UI queue arrays were
never captured and cannot be claimed equal.9offline continuation/identity
checks pass alongside63policy checks. Startup is not proof of native progress.


### Same18 parity passed; human FireTuner handoff

The approved continuation passed source18/full archived world/nativeDB/current
510 and recorded production/treasury parity. Before the first commitment it
failed the next native legality preflight. Zero commit/purchase/autoplay19
commands were sent. The adapter had put X/Y into the target-enumeration query;
the validated collector enumerates with district-only args and adds coordinates
only for CanStartOperation. This parameter order is now corrected after the
owners retired; stronger generated-Lua tests pass64checks. Native confirmation
of the correction is still pending, with found/exact flags now captured.

Human opened FireTuner to watch and chose to launch the T18save manually.
Assistant paused between ACKed commands and retired only the two failed Python
owners, preventing pending Menu cleanup from running into a manually loaded
game. Civ was untouched and no native client opened. Await the explicit
FireTuner-closed signal, then validate/attach the manually loaded18world in a
new branch; do not reload it again or resume the old cleanup process. New
branch cleanup/preferences restoration remains pending; earlier root receipt
does not prove current Menu preferences after the later attempt.


### Human closed T18; explicitly requested a new world

Human closed Civ and instructed “let go of that T18 game, just start a new one
and let that run”. Run01 and both turn18 attempts are permanently closed;
the manual interval is unobserved, with no further recovery authorized. The
new run02 uses map830304/game940310, Tomyris0;Amanitore,Tamar,Genghis_Khan,
Joao_III,Hojo, Ancient1→250 Online/Prince Small Continents.lua, current build
archived unchanged. Corrected shared adapter64checks pass. New trueDX12 Menu
and144original preferences/autostartfalse verified before hosting. Startup is
not a gameplay result; actual current status is in run02 artifacts.

As an independent compatibility check, all16 archived successful Game2 native
foundation transactions preserved queue contents/size/current production hash,
supporting that unchanged-queue condition in the current transaction guard.
No new native test world or command was used for this archival check.

The proposed AI metrics scorecard remains a proposal; existing telemetry covers
many components, but this launch does not claim every proposed metric is newly
instrumented. Real purchase/placement and eventual250 outcome require actual
native receipts and an independent offline audit.


### Agreed benchmark baseline: stock AI, shared resource pass only

Human accepted the scorecard/paired comparison with an explicit baseline
correction: NO AI intervention in the baseline. The shared resource pass is
the sole common experimental intervention. Normal CSC gameplay remains equal.
Older private placement/material/improvement signals, Builder/pseudo-yield
tuning and research preferences/callbacks must all be excluded from baseline,
along with the new external planner/purchases. Audit all loaded actions and
verify stock runtime AI values; merely disabling the new planner is inadequate.
Current run02 continues as a tuned pilot, unchanged. Full contract/metrics:
[CSC AI benchmark](csc-ai-benchmark-metrics-20261022.md). No extra game launched.
