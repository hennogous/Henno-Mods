# ACTIVE goal: Astra investigations, fixes and fresh250

RUNNING22:42: fresh250-02 passed actual DB audit25/25materialhosts and14/14
provideredgesexactlyonce, advancedthrough6 andcontinues250. Sharedcontroller
worker13888 / Civ8360 creation134391658049716989 / execsession60762. Watch20hooks
installedzeroFaults inclqualifiedfactoryentry. MainCSCpolicyonly; protocol
external_policy=false/gameplay_interventions=false. MainHEAD e843d611 pushed,
skill6aef0be pushed. Nextmanualcheck~22:57 (15min); useownhandle60762/readartifacts.
No secondconsole/runtime-source edits whileowned. Frozen02 source/mainAI policy
andSQL800010 alreadycaptured. Fullreport/physicalnewpayoutqualificationpending.
Do notmarkcompleteatlaunch. GoalACTIVE, noPR, noCUA. Earlier"Nextlaunch"below
is historical. Newstartup andfutureoutcomes mustreconcilefirstfailedattempt.

UPDATE22:36: fresh250-01 FAILED at1 startup audit;14provideredgesloaded but
8materialhosts missing (R2Sawmill created799990/800000,CLvalidlinks9999 AFTER479).
Closed/restored/ownersabsent verified,handle73401exit1. Noautoplay. FIX action
LoadOrder800010 inmainJSON/project/freezer;37SQL/econtests+deploymentPASS.
Preservefrozen01andfailedrun. Nextfreeze02+fresh250-02 sameseeds. Do NOT launch
untilclosure (alreadyverified). Mainrepoownscopecommitforthisfixpending.

CURRENT14Nov22:28: Lingapura component replay150–200 COMPLETED exit0/saved/
closed/restored/ownersabsent;6,266native rows zero faults. No footprint debit in
either site (workers0). Site2917 gainedownedBase2916 at157→directProduction+1,
total3→4. Mill60outside50horizon at155/prod1.199;160/prod2.398 Mill30Granary44.
Astra retainsformula; no forcedqueue/timeouts. AcquisitionpriorAI-C162/163
closureacceptedaftercurrent6supplier+6publisherfixtures and rebuiltCE243checks.
NewSpec/sharedresourcecasespass. Skill6aef0be pushedAI-N131nativecadence.
Maincommits0e10e175/1dddf91c pushedcoverage+packaging+invariantregressions.
frozen01prepared fromcampaignfrozen02 +mainAI/UI +newmaterialSQL/connectorSQL;
explicitruntimeaction479+Fileentry. ActualoldDB25expectedhosts/10missing,
14provideredges/allmissing;SQLappliedofflineclonequalifiesall25+14exactlyonce.
Newcoverage_preflight auditsrealgameDB onfreshload. Qualifiedfactory-entry
capture enabledplanningfresh justasnoCSCcontrols.12+19observer/deploymenttestsPASS.
NEXT launchfresh250-01 ContinentsSmallOnline18461107/29461107 CL/R2/Suk.
Usecurrentmainpolicyonly. Then qualifyphysicalnewpayouts/providerandcompare.
NoPR. FullgoalACTIVE. Donotstopatfreshlaunch; collect250outcomeandremaining
coverageevidence. Historicalnotesbelowpreparereplayalreadycompleted.

Henno explicitly activated the full goal. get_goal confirms ACTIVE; older paused
memory is historical. Do not mark complete until all three priorities, review,
targeted qualification, fresh250 comparison and documentation/delivery are done.
No native game/Tuner/controller worker was active when inspected this session.

Current report: project/docs/research/mods/csc-ai-astra-gap-investigation-20261114.md.
Goal artifact root Desktop/Codex/csc-ai-astra-gaps-20261114. New source changes
are ready for a scoped commit. Preserve the large unrelated dirty art/SQL/UI
worktree. New Data/CSC_MaterialTransactions.sql registers at479 independently
of CE; project/.ai-test-tmp/material-transactions-manifest.patch contains only
our JSON/action/project-Content edits against HEAD. Apply it to INDEX only;
do not stage the whole already-dirty manifest/project. Working files retain
all user changes. Check cached paths before committing.

Completed this goal turn:
- Found missed geometry.upper<3 pre-screen despite new2floor. Shared
  E.MinimumAdjacency2 used in both economic gates; full owned/frontier regression.
- Same-city future-customer helper now gets the central economic snapshot and
  checks known two-free-slot capacity. One/unknown slot keeps Quarter offer but
  omits extra16customer signal; cross-city/exempt unaffected. Real scanner tests.
- Generic incoming transaction repair attaches five existing ordinary roots
  using resource tags+Improvement_ValidResources, dedups and excludes Industry/
  Corporation. New unconditional gameplay action479 added via JSON generator.
- Actual loaded CL providers7 perQuarter have ZERO current connector edges;
  connector SQL now uses provider tags+sameedgePK and expands unique replacements.
-37econ/SQL,6publisher,10scannergroups and11continuation/component tests pass.

1.6 closed evidence: Lingapura p4/c393221 founded153, pop1/prod2.4.154Quarter42
plot2992 wins28831Q8=112.62 (4255econ+96premium), request3171 admitted. Builder
3172value120 selected155, runs156–177; Quartertree waits1..15 of15 and expires
169/170. Settler3552value212 selected177. Existing ownedplot2917 initially
154direct1/upper3/unoffered;158direct2/upper4/61538Q8positive. Precise geometry
change needs targeted live read (do not call it newly acquired land).
No evidence of a broken lifecycle; keep native expiry, do not force Quarter.

Fresh Ghidra324c51e9/current092abfbb full-body parity verified5functions:
Update3fa5e0(531),CheckForDistrict3e0ee0(610),QueueNextBuild3e8190(2450),
UpdateWorkingContract3ea990(293),ReconsiderDistrictConstruction3e9630(161).
Queue returns with currentproduction; waiting requests validate/update at an
empty queue before comparisons. Existing CE RequestValue logs only changes.
Reconsider helper cancels pendingdistricts outside executing5; NOTinvoked.
Raw native JSON/parity in goalroot. functions.exec stores also retained but use
disk artifacts. Native paths from original loaded-modules verified unchanged.

Astra followup review COMPLETE (same consultant task). No double production
cost or Q8 conversion bug. Concrete asymmetry: Site subtracts all worked-tile
yields incl terrain, without displaced citizen reallocation; native improvement
debit excludes terrain. Building durations also freeze today's production;
missing shared customer buildings incur time/upkeep but omit standalone benefit.
Next component audit on2992/2917, plus mature successful control later. Keep
nativeweights/horizon50/discount fixed; diagnose one change at a time. Do not
multiply all bids or extend timeouts. Coverage repair code is already in place.

Prepared read-only component probe .lua/.py and test; planning_continue optional
--component-target PLAYER CITY PLOT QUARTER, repeated<=8, invokes snapshots at
inactive boundaries via new full_game_observation.play(observe_boundary=None).
Frozen original Pangaea package remains control. At150 city doesn't exist yet,
emits city_absent; by155 captures Site/quote/terrain/workers and a no-unimproved-
footprint counterfactual (only when improvement==-1, original Site retained).
No native game orders, no extra policy.11tests pass incl continuation lifecycle.
Ready to launch original Pangaea150→200 with two targets after committing.
Use Python312/PYTHONPATH known paths and shared controller only. No CUA.

Before replay, git ls-remote checked WildW develop2986a746b396eb93aad14f9afffb043a09c2c489,
mastere59b5aa910c8a0fcab9b31973ffa477443de0e09. Web fetch cachemiss; CLI succeeded.
Keep pinned qualified ownAPI DLL400e6755; no upstream PR/merge. Goal native data
requires this experimental facade. Desktop write/launch tools need escalation.
