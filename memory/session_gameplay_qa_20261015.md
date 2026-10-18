# Gameplay QA — 15 October 2026

**Henno's subsequent correction (15 October, AI baseline task): the material
return issues were false reports. The material returns work.** The unresolved
material-return conclusions below are historical failed-test observations, not
current gameplay defects or limitations. Do not carry them into the AI baseline.

Henno authorized the first native QA slice, then explicitly changed scope to
**report bugs only; do not fix gameplay code yet**. Respect that instruction for
follow-up QA work unless Henno later authorizes fixes.

Durable evidence/report: `project/docs/workflows/gameplay-qa-findings-20261015.md`.
Runner/workflow: `project/tools/qa/`, `project/tests/qa/`,
`project/docs/workflows/gameplay-qa.md`.
Generated output: `C:/Users/Shadow/Desktop/Codex/csc-gameplay-qa-20261015/`.

Confirmed CSC-QA-001: native tile purchase fires CityTileOwnershipChanged, while
adjacency gameplay subscribes to nonexistent PlotOwnershipChanged. Tailors
Production stays +2 instead of +3 after purchasing a third adjacent material.
Native purchase reproduced with the original subscription; forced refresh
corrects it. A temporary live subscription confirmed the event path. The sole
gameplay source edit was restored; `CSC_AdjacencyGameplay.lua` has no Git diff.

Native auto-start was verified: set Automation.SetAutoStartEnabled(true) before
hosting, use ServerType.SERVER_TYPE_NONE (0) and normal frontend parameter setup.
No click needed. Sky captured Civ but activation/click failed with `failed to
activate captured window`. Do not claim Computer Use succeeded on Shadow.

WorldBuilder.SetPlotOwner silently mutates ownership. Its stale-yield outcome
alone is not a gameplay regression; use a real CityManager purchase command to
test normal event handling. Initial bad harness attempt used debug.traceback in
frontend, where debug is nil; the current error handler uses tostring.

Current snapshot built/installed using native manifest task (488 files), previous
installed package backed up under output/build/installed-mab-backed-backup.
Test package is retained. Native stacking 0/1/2/3 passed; full pipeline remains
failed/incomplete. Do not call save/reload, resource removal or broader Quarter
tests passed. A completed failure fixture save is copied into output/run, with
path/hash recorded. Original mod preferences and original native auto-start flag
are captured under output/run for cleanup/restoration.

Cleanup completed: returned to the main menu with Events.ExitToMainMenu(),
restored/verified original mod preferences and native auto-start flag. UI.ExitGame
is nil in PlotInfo on this host; do not copy the old launcher assumption. No
gameplay source edit remains. Full pipeline stays failed/incomplete intentionally.

## Expanded Tailors run and Shadow recovery

Durable result: `project/docs/workflows/tailors-qa-report-20261015.md`.
Expanded output: `C:/Users/Shadow/Desktop/Codex/csc-tailors-qa-20261015/`.
Five confirmed defects: 001 ownership as above; 002 notification saved cache
hashes string keys (effect IDs AND StackAmount), refresh crashes at line209 after
reload; 003 normal Tailor purchase gives seller returns but customer Culture0
until population pulse (C10 intended2, afterpulse2.03125; F6afterpulse.60764);
004 Base Industry/Corporation yield3/3 and4/4 from one Workshop, intended2/2 and3/3;
005 Specialty plot gets0P/0G from Fashion House at ordinary/Industry/Corporation,
and no implementing source attachment exists.

Native radius6 regionalAmenity0 reproduced with actual Fashion purchase (r2/r5+1,
r7zero), but keep provisional pending ordinary settlement test. Debug SetPillaged
stale returns are provisional; normal pillage event not reproduced. Do not count
forced Broadway pillage as normal gameplay (Wonders not ordinary pillage targets).
GPP immediate deltas0 were NOT proved bugs: vanilla Writer and other rates0,
turn stayed1 after bounded autoplay, vanilla Minimap nil table errors appeared
after artificial terrain setup/autoplay. No actual turn accrual validation.

39 offline tests pass. Native Stage4 pop4/5/9/10/55 for four venues passes with
measured vanilla baselines. Real domestic route two-stage Culture/Amenity/exports
passes; Trader removal clears flags. Tourism supply and multiseller stacking
pass. Faith10%passes. Citizen slot totals: QA2, Harbor2 (includes Lighthouse),
HolySite3 (Shrine/Temple), Theater2 (Amphitheater). Earlier expected1 service
totals were WRONG. E Theater outofrange fixture0 is not bug; final legal A Theater
slot check passes after explicitly restoring both supplies. R6 creation cleans
nearby resources, so don't reuse A supply assumptions after regional setup.

Shadow crash recovered from completed saved checkpoint, original SHA recorded
in report/run/save.json. Beware reusing a fixture after failed setup: mutation
can succeed while asynchronous notification errors make strict runner fail.
Matrix now permits own PASS token with separately logged event errors; never
claim command pass equals gameplay pass. Source .lua commands saved beside logs.
Full acceptance runner still needs state validation and interruption journaling.

Popup event locks from Corporation/Wonders caused initial stale UI samples;
scripted OnClose drains them without CU (only when visible). Native Begin/Continue
auto-start remains true during tests and bypasses Computer Use. Actual CU click
has never succeeded on Shadow. Avoid querying native tuner concurrently.

Cleanup after expanded run COMPLETE: snapshot logs, main menu, original142 mod
preferences restored, original auto-start false restored/verified. Autoplay stopped.
Installed CSC test package retained. 53 installed SQL/Lua files hash-match source;
retired unregistered Ruivo processor absent as expected. No gameplay fix retained;
pre-existing user source changes preserved. Stages3/4 phase validator still blocked
by Bakers localization locked-source hash mismatch; gates untouched.


## Fix authorization and scope clarification

User subsequently authorized fixing all five issues and rerunning tests, plus
contracts/validators and project-wide applicability checks. Supersedes the
initial report-only scope. Henno then clarified not to over-engineer where the
existing Bakers pattern plus stronger contracts/validators suffices. Removed
experimental material registry/compiler and restored Bakers gameplay unchanged.
Current approach and verification status: project/docs/workflows/tailors-qa-fixes-20261015.md.


## Verified fix rerun and outstanding material checks

127 offline tests and implemented phase validators pass. Native 001 tile
purchase, 002 original saved hashed-cache refresh plus zero false notifications,
and 003 normal Tailor purchase/customer delivery/removal pass. Material source
corrections 004/005 follow Bakers but STILL FAIL native plot-yield checks:
zero deltas even with unchanged Bakers controls and real building purchases,
also in a small normally founded capital and after a native turn. Root selects
correct Improvement; Single Plot Yields child has zero subjects. Cause unknown;
do NOT call all five fixed or assume debug fixture is responsible. User explicitly
welcomes flagging testing limits for discussion. No new material engine remains.
Next control: normally builder-created improvement in an ordinary gameplay save.
Do not pursue another generic gameplay engine to work around unexplained QA.

Final cleanup: original mod preferences and auto-start=false restored; Civ at menu. Targeted CSC test package remains installed; material fixes still unaccepted.
