# Material-first foundation and acquisition test —22October2026

## Agreed broader mission —22October2026

Enable the AI to discover, acquire, establish, develop and sustain productive
CSC supply chains around cities it already has. Success means functioning,
durable chains delivering goods and Services; foundation counts are a diagnostic.

1. Discover good Quarter opportunities throughout the potential three-tile range
   of existing cities, including revealed land outside current borders.
2. Responsibly acquire worthwhile sites and necessary materials with real gold,
   including a legal sequence of purchases when a direct purchase is unavailable.
3. Establish suitable foundations when ownership and native legality permit.
4. Encourage native AI development of material improvements, Quarter production
   buildings and compatible sales/customer developments. The sales district can
   come later; its absence does not invalidate the opportunity. Preserve the
   purpose of future-sales pseudo-adjacency incentives.
5. Maintain the chain: retain needed material resources, improve and repair them,
   and respond when supply or customer conditions change.

Once these fundamentals are demonstrated, strategy weighting can prioritize
which viable chains best serve longer-term player needs. Defer transient strategy
heuristics until then. Settlement guidance is outside the present scope.

Delta/event-driven updates with occasional broad reconciliation are a possible
efficiency approach, not the mission itself. Current code already narrows reads
to marked footprints between broad scans; it is not a complete delta engine or
an integrated development/maintenance controller. Actual AI gold purchases are
still unproven. Existing material/sales incentives are inputs to evaluate, not
proof of a completed end-to-end system. Keep the running test's executable pins
unchanged; this mission records direction, not additional game authorization.


Henno requested removal of strategy matching for now: naval-unit production is
too transient, and Quarters may precede their eventual sales district. The
immediate goal is to establish broad opportunity discovery, marked-site ownership
conversion and real-gold acquisition of Base+Specialty sites. Service-to-strategy
matching is deferred until these fundamentals are strong.

The preceding Service-first pilot run02 is closed by the explicit request
“skip current game”. Last archived inactive native35; two zero-progress placements
were verified at18/20, no purchase. Its original status files remain historical.
Civ and both owners were already absent before the stop helper's process
precheck; absence cause is undetermined. No crash or normal-exit claim is made.
Its current510 installed package was independently unchanged. Original mod
preferences will be verified in native Menu before the fresh host.


The latest authorized test uses `Policy.material_first()` and
`NativeAdapter(..., material_first=True)` with `adapter.planner` bound to the
coordinator. Strategy/need/Service matching is disabled in this mode. Sales
buildings and Service civics are not required. Normal installed CSC gameplay,
including its future-sales pseudo-adjacency signals, is unchanged.

Broad scans run every five turns and for new cities, across revealed possible
source tiles within three tiles of a city, including unowned land. Adjacent
resource observations extend into ring four. Mark one preferred site/chain per
city/Quarter: Both Base+Specialty first, then Base count, then Specialty count,
then fewer/cheaper missing tiles and deterministic ties. An owned Base-only
fallback cannot consume the same Quarter slot while a better Both site is marked.
Every turn, refresh only the marked source/neighbor footprints and check native
ownership and legality. Events mark state dirty; they never execute mutations.

Acquire up to three missing source/material tiles toward a Both site, one native
purchase at a time, source first. No Service, customer or chain-build readiness
gate. The known remaining chain must fit 50% of treasury above the reserve,
capped at300 gold; reserve is max(150, emergency reserve,10 deficit turns).
Confirmed spending in the rolling five-turn window consumes that allowance.
At most three buys/player/five turns and one/city/turn; one pending/player.
Unknown costs, unsafe/foreign/unrevealed plots, imminent natural acquisition and
missing native purchase reach defer the plan. Base-only sites receive no
scripted purchases. Native district prerequisites and all legality checks remain.

After each real-gold/ownership receipt, collect fresh facts; place only when
the source and its selected Base/Specialty resources are actually owned and the
native UI permits construction. Zero-progress, unchanged positive cost and queue,
and native incomplete-district proof remain mandatory. No forced build orders,
grants, harvest/improvement orders, research guidance or ownership setters are
introduced by this mode. Buying materials does not prove the AI will improve or
retain them; measure that separately.

21 material-specific tests plus64 compatibility tests pass, including actual
Lua5.1 collector footprint and purchase-command fixtures. These are offline
fixtures. Live AI purchase authority requires exact owner+treasury evidence;
no success is claimed from a command acknowledgment. Current live test records
and actual outcomes are in the material-first research document.

The Service-first mode below is retained for provenance and future work. It is
not selected by the new material-first test driver.


## Native test contract

One fresh Ancient1→250 Online/Prince/ContinentsSmall world, seeds830304/940310,
Tomyris0; Amanitore,Tamar,Genghis_Khan,Joao_III,Hojo. The current510-file build and
resource pass are archived unchanged. This is a tuned pilot with existing CSC
AI signals; it is not the future zero-intervention vanilla baseline. No extra
world or recovery is authorized automatically after an ambiguous mutation.

Output: `Desktop/Codex/csc-material-first-foundations-v1-20261022/run-01`.
Use the maintained shared full_game_controller and service_planner material mode.
Pin all dependencies and freeze them for the worker; one FireTuner owner.
Log broad-vs-focused scans, marked plans, every selected/deferred action,
source/material ownership transitions, native purchase receipts, zero-progress
placement proofs, completion events, physical retention, research, Builders and
primary censuses. Completion requires actual250 and worker/supervisor completion,
then an independent offline audit. Report real purchases and material retention
separately from Service activation, structural customer links or projected value.
Restore saved preferences and verify the current510 build unchanged; exit normally.
No old528/F package restoration, prior-study recovery or deployment.

Implementation status:85 offline tests pass; native test launch pending.

## Native launch verified

New trueDX12 PID18716; supervisor10992, worker9668. Actual fresh1 and later native3 with material-first per-turn decisions are archived. Original144preferences/autostartfalse verified before host; current510 build unchanged. All42executed pins match and are frozen. Full250, real-gold acquisition and final audit remain pending until actual evidence. Existing85offlinechecks passed in both staged and maintained code.

### First native placements —19:43UTC

Native30 healthy. Two owned Base-only foundations verified: Hojo Bakers18/1845 and Tailors20/1993. Both have0%before/after,positive unchanged30cost,unchangedqueues/nativeincomplete. These demonstrate the placement path; they do not establish a Base+Specialty acquisition or real-gold purchase. No purchase request or gold spent yet. First-placement notification recorded separately; current42pins and exactcontroller/nativeidentities verified unchanged.

## Failed partial67 —22October20:28UTC


The fresh game reached67 and stopped trying68 after ten minutes without progress.
Both Python owners exited1; no automatic restart or save reload was attempted.
Archived diplomacy telemetry records player2 warning player0 about nearby troops.
The shared cosmetic Close handler hid the view (event526882), but did not restore
turn progress. The underlying blocker remains unresolved. No new exact-PID
exception/exit or archived renderer PSO match was observed; do not call this an
art/native crash or a placement-caused failure.

Seven foundations were independently verified at zero progress with positive
unchanged cost and queue. All seven remain at their original plots/owners;
four physically complete, three pending. All placements were Base-only. Both
opportunities were marked, but no scripted purchase was issued and no scripted
gold was spent. Live AI purchase authority and Both acquisition remain unproven.
330 unique AI research rows cover turns1..66 without gaps. This partial does
not satisfy the endpoint250 test or prove chain-wide effectiveness.

All42executed source pins and the current510-file installed build match. Native
Menu verified144 saved mod preferences and autostartfalse. Supported ExitOK
requested once; all Civ and controller owners then independently absent. No old
528/F art was installed. The exact67 save is preserved; its native reload/whole-
world parity has not been tested. Earlier studies/T18/Service run02 stay closed.

Detailed evidence: independent-turn67-partial-review.json and terminal-cleanup/.
No automatic recovery or new world. Further native testing needs a new explicit
instruction; diplomatic responses must not be silently substituted for AI choices.

Monitor csc-service-planner-v1-game DELETED confirmed after terminal partial review and restoration; exact returned receipt is run-01/monitor.json. No automatic replay or new world.

## Recovery policy corrected; same67 continuation

Human explicitly: “there is never a prohibition to recovery unless I explicitly say there is”, and requires improving the reusable controller and gathering metric data. The prior permission gate was the assistant’s mistaken policy. The failed parent branch remains archived; this same world is continuing from its exact67save in resume-067-diagnostics-v2. No extra world or reconstructed foundation is planned. Strict archived world/7physical+UIproduction/nativeDB/current510 parity gates precede advancement. The initial validated inactive source identity may be observer; later shared handoffs are unchanged.

Maintained controller now gathers read-only native diplomacy/session/context diagnostics before cosmetic teardown. The finite play command is AST-identical. Maintained continuation.py restores only whitelisted observer records. New perturn chain metrics record AI city population/yields/buildings, Quarter supply and improvement/pillage state, native recipient Service properties, treasury and research. Broad opportunity catalogues include alternatives and raw native purchase target/approval lists. Existing placement/purchase journals, research/events, primary/Builder histories remain. Perturn metric coverage before67 is UNOBSERVED; inherited historical snapshots/events are preserved. Metrics record structural links separately from native Service properties; no invented sales transactions. Offline checks:24controllerPython+26Lua51guards+64plannercompatibility+21material+4newcontinuation/diagnostic/metrics checks pass. Native recovery progress is pending actual readback.

New monitor csc-material-first-recovery ACTIVE; old deleted monitor stays deleted. Recover reasonedly by default; do not terminate useful monitoring on first recoverable failure. Preserve exact-state provenance and avoid repeating ambiguous mutations or replacing native AI diplomatic decisions.


## Same-world session recovery confirmed —22 October

The exact67 continuation validated the archived world, native database, current510 package and all seven physical/production states. The old cosmetic handler hid the leader view but left the native warning conversation open. After retiring its Python owners at an acknowledged read-only command, the maintained shared controller gained an opt-in guarded standard conversation dismissal for a verified troop warning to observer0. It checks current Core phase/budget and exact native open-session participants, calls CloseSession once, and records the intervention. This is not merely cosmetic and does not select a diplomatic response, treaty option or extra turn budget.

resume-067-session-v3 attached to the SAME Civ21332 and the already-active67->68 operation. No save reload, observer reinjection, recreated sites or second activation occurred. One guarded session2 dismissal was followed by native68 and three separated inactive/human0 readbacks. Independent confirmation is in independent-session-release-confirmation.json. Shared24Python+26Lua checks and seven added Lua phase/session cases plus existing-operation/no-second-activation checks passed. Current worker3232/supervisor5772 exclusively owns Tuner; all49 executed sources are frozen. This is direct local warning-dismissal→progress evidence, not universal reliability/full250.

Fresh perturn chain-metrics68 and opportunity-catalogue68/decision68 are actually present and validated, recording AI city population/buildings/yields/native Service recipient properties, Quarter supply/improvement/pillage state, full broad alternatives when scanned, raw native purchase target lists, marks/deferrals. Earlier fine-grained coverage before67 remains UNOBSERVED; prior checkpoints/events/research are retained. No sales transaction observation is claimed. The game continues toward250 and real-gold acquisition remains unproven until an ownership+gold receipt.

CSV semantics follow-up: DiplomacyManager.csv column4 is labelled Initiator, not SessionID. In this observed case its2 matched independently verified native session2 and the exact-session guard passed; the handler safely declines mismatches. After the current worker ends, resolve session IDs from native FindOpenSessionID using log-verified From/To/statement rather than treating the CSV Initiator column as a session ID, and add a fixture with different initiator/session IDs. Do not edit current frozen sources to do this.


## Overnight mechanism work —22 October

Human goal: “during the night, try to get to a version of the tile purchasing mechanism that fits our mission. harden controller on the way”. Continue reasoned same-world recovery by default; improve maintained reusable code and retain metric evidence. Mission remains discover -> responsibly acquire -> establish -> develop -> sustain, within existing cities' potential working radius, with strategy weighting deferred. This is a development pilot, not the official zero-intervention baseline experiment.

The session fix advanced67->68 on the same existing operation, and the game reached70. An empty renderer log delta caused a false harness stop: a missing compressed segment yielded None, which the driver compared to zero. The maintained renderer_evidence module now recognizes closed zero-byte deltas as observed intervals with zero new errors, leaves genuinely missing evidence UNOBSERVED, and still stops for positive native renderer failures. Session IDs are now resolved natively from log-verified participants rather than inferred from CSV Initiator.29Python+33actualLua51 checks pass. The exact70 world and all7production states passed before native71. A planned safe operator pause at71 allowed the purchase input to be corrected; raw driver human_stopped_partial terminology does not close the world.

Archived purchasing diagnosis:536city-turn observations returned zero command targets using UI-mode value -780910418;58Both evaluations deferred for native purchase reach. Local native QA purchase examples supply boolean true for PARAM_PLOT_PURCHASE. Maintained collector/adapter/purchase guard now use that boolean independent of current UI mode and preserve both canonical/legacy query target lists.86offline checks (64compatibility+22material including actual Lua, numeric sentinel rejection and canonical-vs-legacy target fixture) pass. Native effect remains a hypothesis until actual query output, and AI purchase authority remains unproven until exact real ownership and gold readback. No spending limit was loosened to mask a collector problem.

An independent affordability calculation shows none of those58earlier Both plans fit the current full-chain allowance;19had fully known prices. The fixed150reserve and half-surplus/all-known-chain rule are additional constraints, not evidence there are no geometric opportunities. After proving the native path, calibrate responsible acquisition against actual balances, income, necessary reserves, known/unknown chain steps and outcome delays. Source-first v1 cannot buy an intervening connector; consider deterministic legal routes only with explicit costs/budgets and per-step native revalidation. Do not fabricate gold/ownership or force production to obtain a positive result.

Current accepted continuation is resume-071-purchase-flag-v5: exact71save,350unique research1..70,all7sites and histories, no earlier turn replay/recreated sites/new world. The previously unexecuted71 cycle runs once, then72onward. New root monitor-context is authoritative. Once worker owns Tuner all imported source/test/driver pins stay frozen; inspect artifacts only. Resolve new blockers after owner exit. Perturn chain metrics/opportunity records begin67; earlier fine coverage remains unobserved. Preserve phase/continuation provenance and distinguish structural links from native Service properties and transactions. Keep monitor csc-material-first-recovery active while this overnight goal is useful; do not close it on the first recoverable failure.


## 23 October: own-wallet-first funding with continuing shortfall fallback

Human requested own funding when affordable, donation fallback initially for the
first100turns, then explicitly extended fallback past100. The new opt-in
`FundedDiagnostic` evaluates each next tile against the ordinary stepwise wallet
gate. Own contribution is min(price, floor80% of current surplus after reserve);
only the remaining shortfall is donated. Rich wallets receive no donation. Full
quoted cost still counts toward rolling/site300 caps; donation does not override
cash-flow evidence, cooldowns, pending transactions, route or native legality.
No whole-route advance funding or promise to finish. One step/player/turn, fresh
native ownership/price/wallet before the next step. Both-only foundation placement
waits until the required owned materials and source satisfy native checks.

Native staged assisted acquisition persists before grant, assignment and debit;
verified finalgold=original+donation-price and ownspent=price-donation. It uses the
already authorized Gameplay city-ownership writer and exact gold debit, not a
proven native AI PURCHASE command. No role switching or production/research/
improvement grants. The permanent one-shot token blocks ambiguous repeat effects.
Partial paid routes and mixed-funded receipts survive warm inheritance without
replaying ownership or clearing pending state. Metrics separate own gold,
donations and full acquisition cost; old full-donation observations stay original.

Radius answer verified against collectors/planner/native bridge and a boundary
fixture: Quarter source<=3, resource observation ring4. Existing owned ring4
material can count, but unowned ring4 cannot be purchased for this city's route.
The current rule therefore does not require all owned Base+Spec to be inside3.
User did not request a radius change; this boundary remains unchanged.

258 offline checks+35 actualLua51 fixtures pass, including no rich-wallet grants,
shortfall-only assistance after100, treasury/price drift and exact debit checks,
lagged ownership without resend, two successive turns with diminishing own funds,
and refusal to inherit an open transaction. Current same-world root is
`Desktop/Codex/csc-donated-both-diagnostic-20261023/run-01/resume-188-own-first-v12`.
Oldv11 clean inactive188 handoff before evaluation; all98pins matched/owners
absent before installation. Warm no load/newworld/replay/reconstruction. Actual
native outcomes/full250/final audit/restoration remain pending until observed.

## 23 October: one-step acquisition gate

Human requested advancing toward Both locations one tile at a time, checking
actual prices and reserves rather than requiring an upfront route quote. The
maintained `Policy.material_first_v2()` now removes both former admission gates:
known route total versus ten-turn capacity, and the one-resource-only exception
for unknown later quotes. Each source/material/declared connector must instead
pass its fresh current price and real-wallet allowance. Future quotes remain
unknown where unobserved and future income does not count as current funds.
After confirmed ownership and debit, collect again. An expensive or invalid next
step waits; prior spending does not authorize further spending.

Both geometry/reveal/safety/native reach and source projection, observed cash
flow, reserves=max(25, emergency reserve,10 deficit turns), 80% current surplus,
300 rolling/site caps, 3 buys/player/5 turns, one/city/turn and unresolved-purchase
protection remain. Existing bounded route is at most3 required+2 connector tiles.
No changes to placement, strategy matching, installed signals or native backend.
The legacy non-stepwise policy is retained for historical reproducibility.

243 offline checks and35 actual Lua51 fixtures pass. The running donated diagnostic
handed off inactive168 before evaluation, with five foundations/nine acquired
tiles/645 donated and charged/835 unique research rows. All95 original pins matched
and owners exited before source installation. The v10 warm attempt then stopped
before actions because bundled census adds gold fields absent from plain census;
offline review proves the world/research unchanged. V11 compares shared identity
fields plus the existing full-world/research checks; three continuation fixtures
exercise schema variation and reject world/queue/research/ledger mismatches.

Same live world/process, no reload/replay/reconstruction. Donation mode remains
unchanged: the revised ordinary policy is recorded as a shadow budget decision,
not an ordinary purchase trial. Original raw decisions/pins remain archived;
earlier “would have passed” results are not silently rewritten. Active root:
`Desktop/Codex/csc-donated-both-diagnostic-20261023/run-01/resume-168-stepwise-price-v11`.
Full250/audit/restoration remain pending. Earlier sections retain dated policy history.

##23October: maintained stepwise acquisition + metric instrumentation (earlier version)

The human's recovery policy is explicit: recover unless explicitly forbidden,
while improving the reusable controller and recording the agreed AI metrics.
The same world reached95 after one guarded warning dismissal92->93 with no
reload or second activation. A later log gate stopped on an earlier read-only
inspection traceback; the exact failed ACK was independently associated with
that probe. The native game remains intact. Previous owners exited; source
versions, raw failed receipts and live-state evidence are archived.

Current branch is `run-01/resume-095-stepwise-v8`, same DX12 process21332.
Supervisor20832; worker13048. Validate actual95 parity before96; startup is not
progress. Preserve all12 physically assisted sites, research/event prefixes,
native database and current510-file installed build. No new world/load/site
reconstruction. Shared source/driver/tests are frozen during ownership.

`Policy.material_first_v2()` explicitly opts into stepwise wallet budgeting and
support for the missing materials of existing natural/assisted Quarters. Strategy,
Service, civic and customer-readiness matching remains disabled. Broad scanning
still covers revealed source locations within3 of existing cities, neighbors in
ring4; per-turn focused checks include established Quarter sources. Rank Both,
then Base count, then Specialty. Buy useful resources before an empty source when
native reach allows; do not buy the naturally imminent border step if another
needed resource is available. Once the source+Base are owned and native-legal,
place0% without waiting for the Specialty; continue its acquisition afterwards.
Do not duplicate a Quarter. Improvements, sales development and maintenance
remain native AI choices influenced by the unchanged installed CSC AI signals.
This update does not claim to implement every development/retention incentive.

Finances now separate actual treasury, gross yield, maintenance and net=gross
minus upkeep. Missing cash-flow evidence blocks stepwise spending. Reserve is
max25, twice maintenance and10 turns of current deficit. A next buy must fit80%
of current surplus; rolling5-turn spend and lifetime physical-site spend each
cap300,3 buys/player/5turns,1/city/turn, one pending/player. A known chain can be
viable within current available money plus10 positive net-income turns, but each
immediate buy is cash-funded. Unknown future quotes allow one bounded useful
resource investment <=75 and40%surplus; repeated unknown exposure and empty
source speculation are refused. This is experimental calibration, not a proven
optimal economy. No connector routing yet; up to3 required acquisitions.

Native visibility reach is separate from execution permission. One globally
bounded first unproven native RequestCommand is permitted only for a useful,
funded plan; success still requires same-turn ownership AND exact actual gold
deduction. ACKs and simulated Lua fixtures are not proof. Uncertain requests stay
durably pending and are never blindly repeated. No actual purchase is claimed
from dispatch.69 compatibility +22 material +18 new policy/Lua tests pass.

Metric points now retain raw physical source/material identities, owned and
improved Base/Spec, pillage, Quarter and producer completion, stage4, treasury
gross/upkeep/net, actual yields/population and native Service-property flags.
Ratios include their numerators/denominators; empty denominators are censored.
Per-turn histories support conversion delays, unused commitments and material
retention/loss cohorts; purchase journals retain real cost and site identities.
Structural sales neighbors are not transactions or fully verified functioning
customer links; Service flags still lack exact source attribution. Strategy
usefulness is deferred. The common formal benchmark evaluator remains incomplete;
this changing pilot is not a vanilla baseline or a causal comparison. Data before
fine instrumentation began at67 remains unobserved; diagnostic planner76 omission
is explicit. Native full250, purchase authority and chain benefit remain pending.



## Native v8 confirmation96

Actual same world96 observed after exact95/world/all12site/UI/nativeDB/current510
parity; all executed pins independently equal. All five AI treasury records now
contain native gross, maintenance and exact net difference.19cities/26physical
Quarters are represented in the first metric point. No native purchase confirmed.
Metric names such as functioning_producers are provisional structural proxies:
completed/unpillaged Quarter + producer + an improved owned Base. The raw
improvement identity is retained, but exact per-resource Stage1/producer/customer
requirements still need the independent benchmark evaluator. Do not present
these proxies as verified payments or fully functioning supply-chain counts.


## Native version9 — kudos release and focused collection confirmed

Same native101->102 resumed without reload/second activation/reconstruction after
world/all13site/UI/nativeDB/current510/research parity. One standard CloseSession
request for the exact log-verified DIPLOMATIC_KUDO2->0/session2 preceded three
stable102 inactive/local0/humantrue readbacks; no response or treaty choice.
All pinned sources independently unchanged. Version9 adds bounded2-connector
acquisition routes (118planner/nativeLua fixtures), observed passive-kudos
handling, and a read-only active-operation source handoff (41Python+35Lua).
Native103 focused plot checks are smaller than the61-plot broad footprints;
cached geography avoids repeated full-map iteration. Source1752 is natively
water and fails Quarter potential; its loose Both geometry is not a missed
funded legal opportunity. Another Base-only foundation is verified;13total.
Real native buying remains unconfirmed, so mechanism goal remains active.

CanProduce's secondary native result is preserved raw. The current JSON field
`reason_details` is not a decoded rejection reason: live successful queries
return hashed native result tables too. Queue the narrow rename/documentation
to `secondary_result` after source ownership ends; do not alter pinned code.
Metric functioning fields remain structural proxies, not verified transactions.

## Version12: exact124 preservation and native purchase capability result

Current SAME-world `run-01/resume-124-capability-v12`, supervisor18704/worker3684,
DX12Civ21332. Read Desktop/Codex/csc-material-first-foundations-v1-20261022/
active-run.json and the current monitor-context.md first. Exact124 attach passed
full world/native DB/current510/all17 physical+UI/615 research observation parity.
Its planner cycle124 ran once and the ordinary124→125 operation is in progress;
dispatch/ACK does not prove125. All61 executed source pins now FROZEN.

The main world was saved at exact124, SHA194b6bcfd7acc76e381c4d2e48021b185fbb212547a5a4de356ffb7672fb8a57.
A reversible SAME-world45 diagnostic found a genuinely funded Both Tailors plan:
player1/city65536/source1100, owned Specialty1026, unowned Base1173 price55,
gold106.2421875. ONE native UI RequestCommand produced no immediate ownership or
gold change in three same-turn readbacks. No AI turns advanced in that diagnostic.
This is unconfirmed execution, not a successful purchase or proof every native
API is unusable. Diagnostic outcomes/spending are EXCLUDED from the accepted main
timeline. Exact124 world/gold/all17 production/research prefixes were restored
and independently verified. Final helper reporter used the wrong export filename;
actual preserved research was correct, verified OFFLINE without a native rerun.

Canonical continuation.read_research_export now resolves actual-turn exports and
rejects conflicts/duplicates. Canonical checkpoint uses unique one-shot supported
SaveGame/SaveComplete/hash receipts, no overwrite/resend, closed file handles and
callback cleanup. Main v12 saves after every25-turn planner cycle so committed
foundations are included. Coordinator accepts reviewed purchase_capability=false:
records unavailable purchase opportunities before city arbitration, creates no
pending mutation, and permits independently legal owned-land foundations. This
is a guard on an unconfirmed UI execution path, not completion of the acquisition
mechanism. Material/budget/connector rules unchanged.179 installed checks plus35
Lua guard fixtures and3 actual driver handler integration fixtures PASS.

Recovery allowed by default while hardening maintained code and gathering metrics.
Goal+monitor csc-material-first-recovery remain ACTIVE; real AI purchasing and full
250 outcome still unproven. Need another supported native execution path, never
blindly repeat the same ambiguous request or fabricate gold/ownership. Strategy/
Service matching deferred. Existing material/sales incentives retained, no new
weights. Perturn chain/material retention/raw treasury/opportunity/deferral metrics
continue; exact Service fulfillment/transactions and the full common benchmark
remain incomplete. Old studies/T18/Service pilots CLOSED. Preserve current510;
never old528/F. No Computer Use/subagents/general QA/deployment.


## Version14 — role route rejected, exact131 restored, offline cohorts

Current SAME-world `run-01/resume-131-actor-rejected-v14`, supervisor19912/
worker11220/DX12Civ21332. Read active-run.json/current monitor-context first.
Exact131 attach PASSED all19 physical+UI/fullworld/nativeDB/current510/650research
parity; accepted131→132 operation completed and133 is in progress. Sources FROZEN.

The across-frame command actor experiment proved UI can follow actor1, unlike
an instantaneous query. However restoring humancontrol0 advanced131→132 despite
ZERO autoplay/purchase requests. It is UNSAFE/rejected as purchase backend.
Canonical command_actor defaults to disabled; its only purpose is an explicitly
opted-in unsafe diagnostic. This is a technical guard, not a general recovery
permission rule. Original roles restored. Exact pre-probe131 save
SHA bed45b4cb67ef15a6fd8f02dca52475c0242e28a5ed2cb43e2b7fff8f1cf69ff
was loadedONCE; all19/world/gold/production/650research+observer prefixes match.
Raw diagnostic interval131→132 is discarded and replayed in the accepted timeline;
do NOT claim no raw replay. Preserve both branches and count accepted turns once.
No foundation reconstruction. Role query/failure/restore evidence remains archived.

Native tile purchase remains unconfirmed; current capability=false records
unavailable buys without consuming another legal foundation choice or retrying
an ambiguous command. Same material-first v2/realwallet/net/reserve/connector
policy, no strategy/Service/customer matching, newweights or gameplay assets.
Exact post-cycle25-turn saves preserve committed sites. No ownership setters in
current run. A human design choice is pending in P/acquisition-backend-choice.json:
keep native command only, or test paid assisted acquisition(native quote + real
negative treasury change + direct city assignment).12 actualLua offline fixtures
pass in H/paid-acquisition-proposal; it is NOT installed or invoked natively.
Do not ask the question again. Recovery/current game continue without waiting.

Reusable service_planner.benchmark_report adds assisted/natural physical-site
cohorts(captures remain assisted), observed improved material-link endpoint and
sampled-checkpoint retention, coverage/missingness, accepted purchase ledger,
and excludes privateYIELD_CSC_AI_* from economic yield totals.193 installedchecks,
35 Lua guardfixtures and3 actual driver handlerfixturesPASS, not nativebuy or
fullgameproof. Through130:19assisted/12complete/9producerbuilt/15ownedBase/0Both;
25natural/24complete/16producerbuilt/5ownedBase/0Both. ImprovedBase producer proxy
4of9 vs3of16; different ages/interventions, NOT causal gain.96..13035checkpoints:
9of9 initially improved-owned links present at endpoint,8of9 present at every
observed checkpoint; this small cohort does NOT mean all materials are secured.
Exact Service gates/transactions and common baseline benchmark remain incomplete.

Current510 unchanged neverold528/F. Old studies/T18/Servicepilots CLOSED. Recovery
authorized by default, no routine permissiongate; never blind-repeat ambiguous
mutations or rejected role switching. Goal+monitor csc-material-first-recovery
ACTIVE; paid acquisition and250/audit/final restoration still outstanding. No
ComputerUse/subagents/generalQA/deployment. Finepre67coverage missing and76
planner omission explicit. Future matched baseline has normal CSC+resourcepass
ONLY, remove all AI interventions; current changing-policy pilot is not baseline.

