# Combined Mill effects and CSC building forecasts — 5 November 2026

User authorized bundling focused native tests of the smaller/local Mill effects
with a probe of other CSC building/effect contributions to district-site scores.
REA, civ6-ai, CSC and gameplay skills applied. This is research, not new tuning,
CE API development, an upstream PR or an economic-benefit trial.

## Current run

Shared-controller driver `project/tools/native_ai/mill_building_study/driver.py`
is currently running as exec session77565. Evidence root:
`Desktop/Codex/csc-mill-building-study-20261105/run-02`.
One fresh Small Continents/Prince/Online world, fixed leaders and seeds, turn1
fixture then one ordinary AI turn to2. Second clean process loads the exact saved2
for read-only new-package persistence checks; no live instrumented module reload.
Maximum100 is retained; planned endpoint is2, no automatic extension/replay.

One host owns all Tuner and native work. Runtime files/spec and shared controller
sources are frozen/pinned; do not edit them or open FireTuner/another native client.
Offline analyzer/tests/ledger are deliberately excluded from executed-source pins
and may be completed while the sole controller runs. Check healthy autonomous
games no more often than15min; initial setup failures need prompt reconciliation.

## Isolated package and restoration

New local folder `Mods/CSC Mill Building Study`, GUID ending2a09,618 files.
Built from the unchanged human CSC plus the four reviewed adjacency files;
actual reference, overlay and copied hashes in packages/current-receipt.json.
staging.json status=staged. This study uses CSC only: stock CE and all score
policies are disabled by exact saved preference selection. Human CSC, stock CE
and earlier development packages remain untouched. After both sessions close and
verify preferences/content, move only the new study folder out of Mods into the
artifact root (checked absolute paths); do not delete or restore old unrelated data.

## Design and gates

Human0 (Cleopatra) gets two bare diagnostic cities/Quarters at separated sites.
The fixture has21 cases: Windflat/hill, Water0..6 edges, remote/local scope,
removal/pillage/repair, Quarter pillage/repair. Mutation phases are reserved once;
native baseline/post facts are sampled twice in separate commands,0.25s apart,
then compared with a fixed independent geometry oracle. No wait-until-expected.
Actual district Production, exact building location/health, unit flags and all
retired bits are checked. Forced inland Water tests its effect, not queue legality.

AI1/2 get matched population15/research unlocks and workable hill terrain, with
AI1 material/customer grants and AI2 bare. These are explicit fixtures bypassing
normal availability, not naturally developed cities or a clean causal rich/bare
counterfactual. Candidates are owned/empty and no Quarter exists at source.

Read-only Frida17.24.3 from existing isolated dependencies attaches AFTER yield
cases. Six qualified hooks: BuildingValue52b900, ModifierValue529ed0,
BaseYield4818c0, CalculateDistrictValues3dfee0, AnalyzeModifier48e9e0,
AmenityValue5272a0. Exact original XP2 SHA324c…e98c/timestamp/image/prefix guards.
No CE avoids overlapping3dfee0 hooks. Observer records exact modifier IDs, nested
ancestry, recipient contexts, handled/zero outcomes, direct amenities and distinct
raw/mutable building/district matrices. It changes no scores/returns/objects.
Retain Frida/session references until exact normal native exit; no live detach.

Source ledger:19 loaded buildings (7 ordinary Bakers/Tailors,12 hidden flags and
Service grants); other six Quarter projects inactive. Workshop20 roots are mostly
12 naval-production wrappers, not a ten-bit ladder. CityCenter population/export
consumers and specialist/residual attribution remain explicit coverage gaps.

## Offline checks

38 observer Node checks PASS. Root Python suite31 cases:30PASS/1optional full-DB
case skipped; collector agent separately ran its full cached-DB + actual Core
case successfully. Fixture12, setup7, world7 and driver5 checks cover actualLua5.1,
error injection, replay bounds, source mappings and chunk framing. World output
60,493 bytes/119chunks, largest print1,146bytes; CRC/length/order checked in host.
Independent driver lifecycle review PASS. Native execution is not yet qualified.

Agents: native component agent owns only new offline analyze.py/test_analyze.py
now; ledger/world and fixture/setup agents are finished/frozen. Original
bakers_components observer and CE sources unchanged. Existing unrelated lens
workspace changes must stay out of study commits. Regular verified docs/code
commits/pushes remain authorized; no upstream PR or maintainer message.

## Preserved first attempt and corrected continuation

Run01/session85060 closed normally at1 after20 passing cases. Final Quarter
repair failed: actual district Production delta0, expected+1, despite complete
healthy Quarter/healthy correctly located Wind, ACTUAL/ENCODED1 and STEP1=1.
This was NOT automatic building pillage. Raw commands0155–0162 preserve it.
The original case recreated Wind then pillaged its Quarter in one Lua command.
The corrected case21 keeps case20's existing Quarter/Mill and repairs that pair;
the+1 oracle is unchanged.15actualLua fixture tests now include deferred
attachment admission and no world changes during repair preparation. Native
attachment timing is a hypothesis, not a proven cause.

First attempt's late logger used a pre-launch log generation, causing a secondary
LogGenerationChanged after verified closure. A clearly labeled recovered
run01/result.json cites original receipts: nativeexit0, all153preferences and
autostartfalse restored,20passed, observer never reached. Raw failure unchanged.
Driver now starts log baselines after native configuration and preserves any
generation change explicitly instead of concealing the primary failure.

Run02 started only after owners were absent. If the known repair Production
assertion persists, its failed contract is preserved in a separately labeled
record-only row, allowing independent building attribution/reload to finish;
it NEVER becomes a passing Mill test and overall complete remains false.
Transport/other assertions still stop. This path has an independent host test.

Current root suite:50 cases,48PASS/2 optional full-DB tests skipped; both optional
full-DB cases separately PASS under agents with actual cached DB+Core.38Node
observer checks PASS. Analyzer completed15tests (including its full-DB case).
All study agents finished; all runtime sources now frozen for run02.
