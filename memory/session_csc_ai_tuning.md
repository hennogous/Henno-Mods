# CSC AI tuning â€” 17 October 2026

User requested Astra review of RomanHoliday, parent implementation and background test. Then clarified strong pseudoyield adjacency between Quarters/materials/sales, beyond builder preference alone. Astra `/root/astra_ai_plan` reviewed v4.34 local RHAI-reference commit91584816e88f458461ae132e30d6860adba97eed. No RH enabled.

Current source after user simplification: sales10 reciprocal, bonus-class resource12 per neighbor, native river4, improvement50, globaldefault3. B/T+directunique replacements only. Broad proxy includes wrong/disabled materials; actual Service rules unchanged. Old conditional modifiers and marker approach remain removed. No markertech; AI action3500 afterLGD2005. UI context-local GameInfo facade leaves native read-only cache intact. Durable doc project/docs/integrations/csc-ai-tuning.md.

COMPLETE: tuning_trial.py unifiedexec79624 exited successfully. No active Tuner owner. Output Desktop/Codex/csc-ai-placement-v1-20261017/trial. Online/Prince/Standard seedpair1/leaders, natural1â†’250, unchangedv3observer. Eleven snapshots,1370events,121installedfiles/sourcepins/twosaves verified. Native preferences restored141uniqueIDs/autostartfalse, Civ mainmenu. Installed115baseline initiallyexact; allowed6newfiles+manifest+3UIwrappers. NativeSQL/UI checks passed; no gameplayDB/Luaruntimeerrors. OfficialCurrentClickoutsduplicateLOCerrorsunrelated.

Earlier narrow setup csc-ai-v1-20261017 superseded before autoplay. Expanded initialsmoke parent csc-ai-placement-v1-20261017 stoppedturn1 for readonlyGameInfo assignment. Both excluded, prefsrestored. Correctedfacade offlineLua covers readonlycache, othermods/index/reentry. Currentnativepreflight asserts filters in PlotInfo/PlotToolTip/ReportScreen/Pedia and gameplay still sees privateyield before autoplay. Civ launchedhidden.

Results: project/docs/research/mods/csc-ai-tuning-v1-20261017.md, comparison.json+CSVs/report in trial. Sales strong: Quarter choices B31/46â†’54/54,T2/8â†’22/23; later sales B9/28â†’49/51,T12/25â†’27/32. Base B14/25â†’16/28,T1/1â†’1/4. Completed B45â†’49,T22â†’29; total67â†’78. EndpointBase B8â†’6,T1â†’0; supportingBdepositscovered5â†’10. Improvedplots223â†’331 butcities48â†’57,pop551â†’686. ServicesGrowth1â†’2,Housing0â†’3. Singlecombinedtreatment exploratory; no causalattribution/general superiority.

Probe afterarchive: 7/7completeunpillagedAI Bwithmaterialshow total minus nativePlotAdj=12Baseor4Spec. CompletedGetAdjacencyYieldincludesmaterialtoo; prospectivePlotcallomitsit. 540AIcandidates/43material,72legal/2material. CannotinferAIignoresbaseyieldfromadjAPI; completedactivationalsodoesnotproveplanning. NoTailormaterialendpoint. Nativegeographicsalescountoverpredictsonecompletedsiteby10; useactualnativePlotAdjforsignalcomparison. Nextusefuldiagnostic identicalpredecisionmaterial0vs12/4withsales/improvementfixed, mirroredcandidatepositions; separatelyaddressresourcedestruction. Do not claim materials AI tuning solved.

Benchmarkfirstactivation250has78complete; settledsaveafterdisasterplaybackclosedhas79 becauseVasterasexistingBcompletes+noriverflagwithoutturnadvance. Keepbenchmark/settledseparate; probeuseslatter. Probe finalizedduringrun outsideinitialpins, read-onlypostarchive; sourcehash06fc3656e65c82e1fe6bc452fd177cf202eb585e8401dab1812dfff5eebcef9b+exactcommandretained. Do notrerunfullgameorredeployabsentnewneed.

Autoplayp0remainshumanflagtrue; materialAIownercheckexcludesit. Primarytablesall6likebaseline; nonhumanonlymaterialcountscomparison.json: BBase12/21â†’12/23,BBaseSales10/19â†’12/21,TBase0/0â†’0/3. Noevidenceofmaterialimprovementinthissubseteither. Nativeprobeexcludedp0already.


Marker experiment REJECTED at user request (too many tradeoffs). Durable report:
project/docs/research/mods/csc-ai-markers-rejected-20261017.md. Native feature adjacency
reached prospective Plot:GetAdjacencyYield (BBase+12, BSpec+8/two, TBase+12, TSpec+4),
but removable markers caused repeated native AI clear/re-add loops at Maize1717 and
Cattle1617. Nonremovable candidate blocked districts on bonus resources. UnitPanel
hiding did not affect AI. Controlled20 fixture not natural efficacy trial. Revision3
Builder guard hotloaded after20, no further AI turns, unvalidated; do not resume.

Cleanup complete: live66markers removed, original141unique mod IDs + autostartfalse
restored/verified, Civ exited, no active Tuner/controller. Removed marker SQL/action/
Content/module from production; source archived unregistered under tools/ai_baseline/
experiments and Desktop/Codex/csc-ai-markers-v2-20261017/rejected-source. Original CSC
UnitPanel restored exactSHA98f3376123e04a0136ff76f6252273d6b4c6ba6dccbf7ed811b3264fb36a47cb.
Private-yield UI facade retained, feature filter removed. Focused installed rollback
SDKmanifest successful; retired module removed afterbackup, unrelatedactions preserved.
CurrentSQL memory-copy validation33sales/material0/oldmods0/idempotent/default3;
UI filter+shippedReportScreen pass. No additional game launched. Evidence root above,
rollback/ and native/marker-summary.json pin tested revision2 separately from untested3.


Next authorized candidate (same day, after rejection): user requested all-bonus
native adjacency, native rivers and stronger improvement value. Implemented in
CSC_AI.sql: shared CSC_AI_BONUS_RESOURCE AdjacentResourceClass RESOURCECLASS_BONUS,
12/TilesRequired1; CSC_AI_RIVER AdjacentRiver1,4/TilesRequired1 (Commercial Hub
predicate). Attach both to B/T+directunique variants. All modded bonus-class
resources automatically included; exact mappings/improvement/animal setting not
expressed in proxy. No new features/resources, no Specialty signal, no future
Quarter scaffolding. Future feature-based Quarters should score existing features.
Improvement own major-civ list25->50 (not twice as many improvements; no global
DefaultValue change). SQL reapplication explicitly updates old own preference.
Validated nativeDB memorycopy:33sales/fourguidance, idempotent, only privateadjacency
and AiFavoredItems changes. Evidence Desktop/Codex/csc-ai-native-bonus-river-20261017.
Focused backed-up SDK deployment successful, unrelated installed actions preserved.
No game/autoplay launched. Integration doc updated; experimental efficacy caveat.


ACTIVE natural v3 trial authorized by user after implementation: native_tuning_trial.py,
exec session16979 (only Tuner owner), output Desktop/Codex/csc-ai-native-bonus-river-20261017/trial.
Civ launched Hidden; no CUA. Same seed1 Online/Prince/Standard 250 endpoint as baseline/v1.
Initialmap3404tiles13fields exact, realmechanicsbaselineidentical. LoadedSQL validation37
private attachments(33sales+4bonus/river), improvement50, legacy/materialmarkersabsent.
Primary paired_observer.lua v3 unchanged. New read-only native_guidance_probe.lua initial
has0cities so detailed prospective probe deferred to archive-endpoint. Finalcontroller
restores141modflags/autostart. New analyze_native_tuning.py comparesBaseline+V1+Native,
actualbase,riveralternatives,improvements,retention,services and endpointbonusproxy.
Resourcecatalog/mechanicscomparison archived. Do not use V1 analyze_tuning.py CLI for
newprobe formulas; new analyzer imports only its established summarize(). Marker20
fixture excluded as noncomparable. Until controller exits, do not open a secondTuner.


First v3 natural trial native-crashed aroundturn94 (lastTuner92, latestautosave94),
user confirmed FiraxisCrashReporter screenshot. Pythoncontroller21300 stopped;
onlycrashedCiv1272+itsReporter21564 closed after evidencearchive. Firsttrialexcluded,
crash-logs andcrash-autosaves94/93/92/91 retained, no observerdataafter1ondisk.
Causeunknown; no gameplaysqlerrorreported. UnchangedseedretryACTIVE execsession42029,
outputroot/retry-01; original141preferencescopiedfromfirsttrialbeforeconfigso final
restore must use those, nottemporaryCSC-only flags. CurrentTunerowner42029 only.
New analysisCLI --trial retry-01 ifcomplete, resourcecatalogcopied. Historicalruns
untouched. Do not claim testcomplete or infercausalityfromcrash.

Retry passed firstfailurepoint. Archived frozen25/50/75/100 via briefcontroller
reconnect (no gameplaychanges); continuednativeautoplay unchanged --resume-running.
ACTIVEsoleTunerexecsession50309, previous42029stoppedforread-onlycheckpointarchive.
At100actualBBase17/18 vsbaseline9/17,v1 12/17; T2/2vs0/0,1/1; provisionalonly.
Finalcomparisonstillrequires250,retention/improvement/Services andprefrestore.

RetrystillACTIVE: secondcheckpointarchive125/150/175/200 succeeded, identicalfrozen
observerdata no gameplaychanges; monitoringresumed --resume-running execsession1095
soleTunerowner. Through200zeroobservererrors. First100and200ondisk preserved.
At200Bcompleted44/Base12/adjacentresources17/improved10;T29/Base3/adjres3/improved1;
GrowthServicecities7vsbaseline2/v1 3, Housing2vs0/4. Provisionalonly.
Newanalyzer also retains nonhuman-onlyBasechoices toaccountv1 p0AIownerexclusion.
Full250+save+nativeprobe+prefsrestore+comparison/docupdate stillpending.


COMPLETE native bonus/river v3 retry at250. Solecontroller1095 exited after missing
restoreack; separate--restore-only35664 completedrestore+freshverify141IDs/autostartfalse.
Finalofflineverify passes11snapshots/1431events/2saves/121installedfiles+allsourcepins.
No activeTuner/controller; Civbackgroundmainmenu. Batchmarkedcomplete afterverified
cleanup, completion-recovery.json retainsackissue. Save-state250identicalbenchmark.
Mainreport project/docs/research/mods/csc-ai-native-bonus-river-20261017.md.
Output root/retry-01 comparison.json+CSVs/report. Firstnativecrashroot/trialexcluded.
BactualBase14/25->16/28->24/27, nonhuman12/21->12/23->20/22. Base+sales11/21->16/26->21/24.
River10/22->13/23->20/27. TBase1/1->1/4->5/5,nonhuman0/0->0/3->4/4 small.
Completed B51/T33, Baseendpoint13/2, Baseimproved6/15 B,0/2 T. Growthsources6,Housing3,
noTailorService. SalesQuarterB49/55belowv1 54/54 butlaterSales56/57. Improvedplots357,
cities61,pop735;percity5.85vs5.81v1, per100pop48.6vs48.3: no distinctbuildergain.
BSupplieslostunderdistricts10/28vs5/14baseline10/19v1. WrongbonusendpointB8/21,T10/12.
Nativeprospectiveisolated29/29match,14positivebonusrows,0isolatedrivers so do not claim
standaloneRivernativeAPIverification. No gameplaysqlerrors/observererrors.
Two controllerreconnects frozenarchives100/200 changedno gameplay. Diagnostic/analyzer
sourcehashes separatelyrecorded; originalobserver unchanged. Next moreseeds before
calibration, actualremaininggapsBuilderimprovementsandpreservation. No auto followup.


UserclarifiesgoalMOREBUILDERS. VerifiedprimaryInfixoPseudoYieldswiki: testedbiases
percentage; documentedmodelbase3*(1+.25)=3.75 to3*(1+.50)=4.5 beforeotherbiases,
not3->50 or2xeffectiveweight. Nocompletenativeeffectiveweightreadbackclaimed.
RHAI localLAI_Main.sql9 changesbase3->90; Ops/Ops.sql47 UNIT_BUILDER priority900.
StockUnitPriorityBoostsmajortraitSystemUnits. CSCnoneBuilderUnitPrioritycurrently.
Improvementdemand/contracts andunitproductionpriorityseparatelevers; Infixowarns
unitprioritydoesnotautomaticallymoreimprovements. Existingobserverdoesnotcapture
Builderproduction, so no production-rateconclusionfromimprovementdensity. Next
experimentshouldinstrumentbuildercreation/training/purchase/charges. No change
orlaunchduringexplanation. New integrationsectiondocumentsprimarysource/math.


## RH Builder values v4 — background job launched 17 October 13:56 CEST

User explicitly requested matching both RH Builder-related settings and sparse
assistant involvement (50-turn/15-minute checks). `CSC_AI.sql` now sets global
improvement base90 and native major-civ UnitPriorityBoosts Builder900; former
own +50% list removed. Bonus12/river4/sales10 unchanged; RH remains disabled.
SQL read-only memory validation/idempotence passed; focused deploy changed only
Data/CSC_AI.sql and generated modinfo. Completed v3 sources/results preserved.

New output: C:/Users/Shadow/Desktop/Codex/csc-ai-rh-builders-20261017
Hidden Civ PID18900; autonomous wrapper PID8884 (verify current status, PIDs can
expire). `run_builder_job.py` runs one matched seed1 Online/Prince/Standard game
to250 via `builder_tuning_trial.py`, then four-run offline analysis.
Supplemental Builder observer records unit additions/training/charges; raw
purchases retained if native unit subtype absent. Historical production counts
are unavailable. Primary observer is unchanged. Python polls20s, archives at
50-turn intervals, retains primary25-turn censuses, bounds stalls10min and
connection failures3, archives failure logs/autosaves, restores preferences.

Native heartbeat `csc-builder-test-progress` ACTIVE every15min, recorded in
output heartbeat.json. Read job-status/live-status/log tails only while running;
DO NOT compete for Tuner or keep model waiting. Report new50-turn milestone or
15min progress briefly. At completion verify validation/preferences/nativeDB,
read report.md/comparison.json, promote durable results, update this note/index
and delete heartbeat. At failure inspect once, cleanup when feasible, preserve
incomplete output outside comparisons, report and delete heartbeat. No blind
restarts or extra games. User cares about usage: end normal turns promptly.

Preflight correction: the supplemental observer initially referenced a JSON
module private to a different Lua context. This failed only its turn1 export;
autoplay had not begun. Added builder_export.lua using the established observer
serializer, configured UTF-8 stdout/stderr so cleanup errors cannot be masked
by Windows console encoding, and resumed the same untouched turn1 world with
--resume-prepared. Original failure/log/source-pin evidence is in
preflight-failure/, command transcripts retained. Current controller PID3576,
actual Civ PID5564 (Steam replaced the initial launch process). No map restart.
New tuning sources pinned before autoplay. Read current files for progress.
Native v4 preflight passed: loaded DB improvement90, Builder900, own layer absent; 33 sales edges/four resource-river attachments unchanged; exact starting world verified; UI filters passed. Scheduled monitoring owns subsequent progress.


## v4 interrupted — 17 October scheduled follow-up

Both Civ and wrapper/controller processes absent. Status stale since14:30:03
CEST, second connection failure, last confirmed230; Lua log records232, latest
autosave named234. Cause unknown: no fatal traceback or diagnostic proof of
crash. Nine primary snapshots1/25...200 and Builder200 have zero observer
errors; tuning hashes still match. No225/250, no completed comparison.
Failure logs/status originals and autosaves232/233/234 archived in trial.
job-status nowfailed and batchinterrupted; keep outside completed comparisons.
No game restart/rerun. Heartbeat csc-builder-test-progress DELETED.
Main-menu-only cleanup restoring original141modflags/autostartfalse is being
verified; read preferences-restored.json for actual success before claiming it.
Durable report: project/docs/research/mods/csc-ai-rh-builders-20261017.md.

Cleanup COMPLETE15:45 CEST:141original mod flags and autostartfalse freshly
verified, close command accepted. Heartbeat deleted. No controller/new game.

## v4 partial200 is usable — user confirmed Shadow died

User correctly asked to use the preserved progress. Offline analyzer
analyze_checkpoint_tuning.py compares all four real200snapshots with historical
metrics preserved and no source-pin edits. Outputs at experiment/partial-turn-200;
durable report csc-ai-rh-builders-20261017-turn200.md. Initial map/leader/research,
zeroerrors/eventprefix checked; future timeline excluded; exposure uses200.
Baseline/v1/v3/v4 improvedplots145/237/266/380; percity3.37/4.65/5.22/7.76;
per100pop34.0/41.7/45.6/59.9. v4 vs v3 +48.7%city/+31.4%population, all6
players higher/city. Cities43/51/51/49. Baker mappedBaseimproved4/11,4/8,8/15,
12/16. Basechoice13/22,16/26,20/22,22/26 (new slightlylower thanv3).
Service Growth2/3/7/7, Housing0/4/2/2: no v3-to-v4 Servicegain. TailorBase
0/1,0/0,1/3,1/1 tiny; Tcompletions19/25/29/23. Bcompletions37/45/44/44.
Buildernewonly200:145trained58purchased26alive55charges230adds. No historic
productiontelemetry; addedcounts includecapture/grant. Promising improvement
outcomes; one combined two-setting treatment, no generalcausalcalibration yet.
No additional tuning/native game; prefs restored and heartbeat deleted.


## ACTIVE latest setup250 game — 17 October16:50 CEST

User requested one game to250 with limited assistant checks for crashes.
Output Desktop/Codex/csc-ai-density-v4-20261017/trial; supervisor PID23804,
launch metadata parentroot/launch.json. Civ launchedhidden (Steamreplaceslaunch
PID; check actualimage ratherthanparent6372). NativeStandard/Online/Prince/
SmallContinents/6major9CS; originalAIseed830102/game940104/roster reused.
Resourcepass4 density and AIimprovement90/Builder900 plusnative12/4/10;
animalsOn, TAR/RH/M&Coff. InstalledCore/adapter/definitions/AI match source.

New density_game_trial.py uses unchangedprimaryobserver andBuildertelemetry,
allows intentionalresource differences whileasserting terrain/roster/research.
density_game_methods.py archives every25 immediately (incl225), Builder50;
uniqueCiv6saveprefix avoids oldtrial saves. run_density_job.py owns worker and
processwatchdog: tasklist30s, missingCivilizationVI twice stopsworker, preserves
logs/latest3autosaves, noautoRestart. Worker boundedstalls/consolefails, native
restorationoncompletion. Allnewsourcepins included; oldcontrollers unchanged.
analysis_density_game.py (actual filename analyze_density_game.py) auto generates
250summary and common200comparison to oldRHbuildertrial (oldresourcepass3).
No matchedold250 becauseoldhostdied; differences resources intentional.

Heartbeat csc-density-ai-run-progress ACTIVE15minutes, recordedheartbeat.json.
Userusagepreference: read ONLY job-status/live-status/shortlogtails, report
briefnewmilestone/currentturn thenEND, no competingTuner whilejobruns, no
modelwaiting/busypoll. Oncomplete checkvalidation/preferences/nativeDB then
smallreport/summaryJSON, savedurablehumanreport, updatememory, deleteheartbeat.
Onfailure preservepartial and latestautosaves, restoreprefswherefeasible,
reportlatestarchivedturn andcauseuncertainty once, deleteheartbeat; no blind
newgame/rerun. IfShadowhostdies jobstatusmaystale: check supervisor/Civprocess
before claimingalive. Common partialcheckpoints arestilluseful peruser.

Startup at16:51:47 generatingmap. Noactive execsessions (hiddenprocesses
independent). Nativepreflight/autoplayconfirmation stillpending.

Startup confirmed: native preflight passed (original terrain/roster/research; resource pass4; improvement90/Builder900). At final launch check, live-status reports active autoplay turn19/250. Worker and supervisor own FireTuner; heartbeat csc-density-ai-run-progress will perform sparse follow-ups. No further connection or game launch while this run is active.


## Latest setup native game: turn250 observations, final save failed (17 October)

Run Desktop/Codex/csc-ai-density-v4-20261017/trial reached250. Worker failed only at final named save confirmation (native call returned no Lua error, expected file absent); gameplay crash is not evidenced. Supervisor/worker exited. All11 snapshots1..250 and6 Builder censuses preserved; independent snapshot-validation.json passes event prefixes, zero observer errors, unchanged primary observer,36 source pins, initial save SHA, native90/900/12/4/10 DB validation, and zero Gameplay SQL errors. Settled250 snapshot identical. Original failed job/batch files untouched; no full validation.json fabricated. Autosaves248/249/250 preserved, not load-tested. Preferences141mods/autostartfalse verified restored; no cleanup-required. No game restarted. Heartbeat csc-density-ai-run-progress DELETED after analysis.

Report project/docs/research/mods/csc-ai-density-v4-20261017-turn250.md; compact comparison.json/report.md/snapshot-validation.json in trial. Resource pass4 adds16 changed tiles over original pass3 world; same initial terrain/roster/research, unchanged AI, one seed, not causal AI comparison.

Common200 previous=>latest: cities49=>47,pop634=>537,improved380=>315,percity7.76=>6.70,per100pop59.9=>58.7. BakerBaseimproved12/16=>10/16, Tailor1/1=>0/1; Service Growth7=>7,Housing2=>1, no Tailor. Builder trained145=>144,purchased58=>44,alive26=>39,charges55=>101.

Latest250:57cities,pop702,370improved(6.49/city,52.7/100pop). Bakers46/Tailors25completed; Base12/46 and2/25; both0/46 and0/25. BBaseimproved7/13,Spec2/2; TBase1/2,Spec0/0. Sales45/46 and22/25; later-sales choices33/40 and40/51. Active Service sources4BakerGrowth/2Housing,zeroTailor. Supporting material plots covered10/22B,3/5T. TailorBase alternative decisions5/9 chosen (common2003/7 versus previous1/1);9of11Tailors near bonus types only have unmapped bonuses. More map opportunities alone did not solve native proxy placement/preservation. Builder161trained69purchased,33alive88charges;280add events (captures/grants possible).

IMPORTANT offline telemetry correction: original analyze_density_game.builders filters cumulative events by CURRENT alive-player census. Player0 dies before250, incorrectly reducing cumulative trained144=>143. Postmortem correctly uses initial six-major cohort; result161trained69purchased. Alive/charges still endpoint living units. Pinned analyzer source unchanged, so its generic main must be corrected before a future trial, with new pins. No native engine calls during postmortem. Temporary postmortem script remains in visualization working directory; durable report records cohort definition.


## Improvement base20 —17 October user follow-up
User requested90=>20 (PSEUDOYIELD_IMPROVEMENT base), keeping separate Builder900.
Source+installed Data/CSC_AI.sql changed; current SQL validator expected20.
Native placement12/4/10 unchanged. No new game. Dedicated historical90/900
preflight remains hardcoded90; update before next run, do not blindly rerun.
Tailor discrepancy traced exactly:27placements,9cached-owned-legalBaseoptions,
5selectedBase,4passedover;18withoutBaseoption. Endpoint25completed and2Base.
All5Basechoices complete: Cologne46 plot1234 lostSheep1233 toHolySite;
Kerma60 plot2525 lostFlax2451 toWonder; ElKurru236 plot3130 lostFlax3056
toTheater. Meroe58 plot2676 retainedFlax2602; SaiGon222 plot2772 retainedFlax2846.
Thus5placement successes minus3later resource losses=2endpoint Base quarters.


## User correction: improvement90, Builder100 (17October)
Supersedes immediately prior20/900 change: CURRENT source+installed improvement
base90 and UnitPriorityBoosts Builder100. Native12/4/10 unchanged. Validator
checks90/100. No game launched. Vanilla shipped Base/DLC search has no Builder
UnitPriorityBoosts item; Leaders.xml246 onlySettler1, schemaValue default0.
Stock therefore0 additional Builder boost in that list; internal native base
score is not known.100 is not a unit-count or percentage promise. Historical
trial preflight hardcoded900 must be updated before any new authorized run.


## RH improvement review / preservation hypothesis (17October)
RH separate Improvements-system typebiases in Ops128+:Mine40,Pasture9,Quarry-8;
growthtraitFarm90. Also CityEventImprovement Value1(LAI_Main2:644), AIBuilder+2
friendlyterritory startmovement(Main3:437+), virtual improvement yield modifiers
(Yields3FarmFoodExt/Yields5MineEndTech). Active files/SQL comments checked. No
explicit general improved-resource protection found; MC harvest restriction custom
monopolyunits, not ordinaryBuilders. Prefer type-bias experiment vs more supply;
exact CSC tileconditional prediction remainsunproven, same limitation asoldmodifiers.
User's improved=>lessdestroyed theory not established: lostSheep gotPasture46,
pillaged125,HolySite135; lostFlax2451Farm60 intact100 Wonder113; lostFlax3056
Farm122 alreadyabsent225 before Tailor236/Theater240. Do not sayall3were intact
at removal, or that earlier improving surely protects. Need immediate preloss
state + matched loss denominators nexttelemetry. No code/gameplaychanges.


## New installed RH v5.097 research (18October)
User supplied Workshop3792072489, authorized Astra help; Astra reviewed native
adj/modifiers/microstrategies. Full report project/docs/research/mods/csc-rh-v5097-ai-review-20261018.md; sourceinventorySHA15files adjacentJSON. No games/Tuner/codechanges.
LatestRH improvementbase30, oldglobalBuilder900 absentRH_Ops, movement+1(notold+2).
AutoPurchase1473+ scores cityjobs resourceclasses/unlockdata/slack, buysnearwork
withcaps/cooldowns, scriptCreatesunit+deductscost; notactualjobdispatcher. GatedMP0or4.
Scorer counts pillagedimprovementalreadyimproved, notfulltile/pathfeasibility, no
nearbycharges/jobreservation. ResourceSupplies canmatterevenwhenunworked.
RH CallLuaFunctionstrategy+GameEventsbool usefulforboundedresourcebacklogsignal,
notexacttileassignment. No generalBuilderBUILD_IMPROVEMENT/REPAIR dispatchfound.
Native reciprocalprivateyieldadjacencyconfirmspresentCSCpattern;Observatory
luxuryclass/terrainproxy showsnoexactresourceownership/ANDsolution. Rawresource
privateyield strategic/lux(noBonus) possiblepreservationprobe butNOmarginalreward
forimprovingtile. LateBBG/StartBiasNegatives removesrows. MineGPP etc modifiers
normallyinactive impossibleAncient/beforeMedieval+FutureCivicgate, notproofplanner
readsvalidconditionalCSCeffects. KoreaFarmdefinednotattached, Mineattached.
Userrejectstypebias, wantsanyresourceimproved includingfutureMines/LumberMills.
Proposed firstresourceworkdiagnostic thennativeprospectivescoring/repairmicroprobe;
separaterawresourcepreservationprobe; adaptivedemandifnativeworks; helperexisting
Buildersonlyifnativecannotreadsignal andnativeoperationAPIvalidated. No more
Buildersasfirstresponse. Keep90/100untilnewauthorization;30comparisonlaterisolated.
Read-onlyreviewonly; noRHsourcecopied; licensesreusepermissionneededforactualcopy.


## ACTIVE Quarter-owned resource modifier trial (18October)
User authorized lower Builder incentive + strong matching Quarter-owned resource
modifiers plus extra improvement bonus; then corrected endpoint200=>250.
Implemented independently after rechecking latestRH native Pantheons133+.
CURRENTsource+installed90/50, present40/extra80 privateyield, native12/4/10 retained.
ExactmaterialTypes from liveBase/Spec tags per implementedQuarter; PLAYERPLOT
collection + sourceowneradj1 +resourcevisibility +AIownergate; native improved
resourceclasscondition. SQLofflinevalidation passes/idempotent; native fixture
and untouchedsave reload gate autoplay (not yet confirmed at this note).
Root Desktop/Codex/csc-ai-quarter-resources-20261018, supervisor9520; game launch2364
maybeSteamreplacedPID. Worker ownsTuner. Do NOT open another connection whilealive.
Statusstarting firstcheck. 25turnsnapshots/50Builderandsignalchecks; target250.
Newquarter_resource_trial/probe/fixture/analyze/job files inai_baseline; old historical
controllersunchanged. Comparepreviousdensity-v4 at200/250 exactinitialresource4world.
AnalysisBuilder cumulativeevents retain original6cohort. Finalsavewarning doesn't
throwawayvalidatedsnapshot; autosavesbackup. No blindrestart. Originalprefsrestore.
Heartbeat csc-quarter-resource-incentive-test ACTIVEevery15min (destinationthread);
quiethealthy, completion/failureonly. Readstatusesandshorttails; no modelwaitloop.
Oncomplete checkvalidation/fixture/nativeDB/prefs thenreport/compactcomparison,
savedurablehumandoc,updatememory,deleteheartbeat. Onfailureboundedlogs/cleanup,
restoreprefswhenpossible,preservepartial,reportonce,deleteheartbeat. Noautomatic
improvement-ownedfallback; reviewfirst. Userasksusageeconomy; finishturnwhen
startup/nativefixture/autoplay isconfirmed, thenleavecontrollerandheartbeat.


## Scope extension: FIVE additional tests after T0 (18October)
User explicitly authorized five additional250-turn experiments after analyzingT0,
with exactcodeversion notes, overallCSC AI objectives. Updated existingheartbeat
csc-quarter-resource-incentive-test to carryseries throughall6; DO NOT deleteafter
T0 unlessrealunresolvedblocker. Sparsequiethealthy15min. Ledgerroot/series.json,
durableproject/docs/research/mods/csc-ai-experiment-series-20261018.md. T0actual
repository sourcepins +allinstalledgameplaytexts archivedtrial/source-version/;
code_version quarter-owned-resource40-plus80-builder50-v1. Do noteditlivepins.
ChoosefiveusefulcontrolledvariantsafterT0evidence; improvement-ownermarginal,
preservation, nativeforecastingcalibration, adaptivebacklog/Serviceuptake options.
No arbitrarytypeskew, markerfeatures, free supplies or RHcopy. One gameatime;
no competingTuner. Userauthorizationpersists, no needaskagain. Keepcompleted,
partialfailed,fixture-only evidence distinct. Finalreportall6+candidate.


### Native fixture diagnosis and Workshop-pattern control

T0 v1 failed before autoplay: expected private40 on adjacent Flax read0; both fixture Quarters were complete and AI-owner gates passed. No natural run/checkpoint should be counted. Original turn1 save and v1 exact source archive remain intact. Original preferences were restored after that failure.

Subsequent disposable diagnostics ruled out local-player visibility (revealed map and researched Flax, still0). Saved-game Gold control rows appeared in GameInfo but no native Gold modifier instances were created, including AttachModifierByID. This does not establish that private yields cannot work; save/native-definition caching or scope still needs separation. Gameplay and UI reads both gave0. Native adjacent-to-owner source position is not yet established. Do not claim city-center anchoring proven.

Henno suggested using the Textile Workshop pattern attached to the Quarter. Its existing production chain uses COLLECTION_PLAYER_IMPROVEMENTS / EFFECT_ATTACH_MODIFIER and a MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS child. Testing that exact improvement chain plus a corresponding plot-collection attach for the unimproved40 signal, with disposable Gold4/+8 controls, in a fresh same-seed native game. Hidden diagnostic PID7500, root/diagnostic-06; active-stage.json is authoritative. Controller at visualization/diagnose_workshop_pattern.py, archived diagnostic-06/controller.py. It owns Tuner while alive. Source SQL remains v1; temporary installed SQL is diagnostic only and controller finally restores source SQL, returns menu and verifies original142 mod preferences. Do not start natural autoplay with Gold controls. Original natural controller is dead; no simultaneous Tuner. Check diagnostic status/results before repairing T0 and creating a distinct source-version archive. Five additional250-turn tests remain authorized. Heartbeat prompt updated to follow diagnostic ownership.


User steering: run only ONE250-turn game now. Defer T1-T5 until tomorrow; no automatic launch or new schedule for them. Existing follow-up now limited to completing single T0 and deleting itself afterward. Diagnostic06 completed all present/improved/pillaged private/Gold reads0; preferences142/auto_startfalse verified restored, temporary installedSQL restored. Need a discriminating known-working native effect control before autoplay, no repeated identical fixtures.


Native diagnostic07 now runs hidden (PID17216; active-stage.json): independent unconditional PlayerGold2, QuarterCityGold3, QuarterSelfGold5, Quarter-to-improvement Gold7, plus actual existing Textile Workshop production wrapper attached directly to Tailors Quarter. It asserts new controls exist, captures native DB before preference restoration, compares immediate and settled gameplay/UI after exactly ONE disposable native turn. No natural autoplay. Distinguishes native effect/source scope from resource requirements, private yields and delayed fixture refresh. Script restores original142preferences and installedsourceSQL in cleanup. No competing Tuner. Previous reporter8416 began21:30:30 alongside Civ6216, predates diagnostics, not evidence of new crash; process reads require escalation. One250naturalgame only; T1-T5 remain deferred.


Diagnostic07 completed after one disposable native turn: all queried Gold/private yields0; critically GameEffects showed NONE of the new unconditional controls, although GameInfo assertions for their rows passed. Original v1 SUPPLY effects did exist. Therefore do not conclude effect/Quarter scoping/private yield unsupported from these zeros. New hypothesis: native definitions retained across same-process game loads (GameInfo changes without native modifier-instantiation refresh). Diagnostic07 native-debug.sqlite captured before preference restoration. Original142preferences/auto_startfalse and installedsource restored.

Cold diagnostic08 launched: installed diagnostic SQL before stopping known test Civ6216 at menu and relaunching executable hidden (-skip-intro), no played natural game lost. PID19836 diagnostic owns Tuner; new Civ launchPID in active-stage.json. Source controller visualization/diagnose_cold_native.py archives into diagnostic08. Same independent Player/City/Self/Improvement Gold controls, actual existing Workshop production wrapper on TailorQuarter, plus improved SUPPLY modifiers changed to Workshop player-improvement attach + single-plot private80 child. Present40 remains original direct native method. Query before/after one native turn. Script finally restores sourceSQL and prefs. If cold control works, implement/validate source candidate and use cold launch for natural test, keeping exact archives; same-process pristine reload alone may not update native definitions. Only ONE natural250game authorized now, later5deferred. If this discriminating control fails, bound diagnosis and report honestly, not endless identical map generation. Heartbeat reads active-stage.json first.


Cold diagnostic08 did NOT reach a game: direct executable launch exited before menu, diagnostic30sec wait timed out. No native control result, no natural data. Preferences were untouched from verified restored142set; sourceSQL finally restored. Diagnostic09 repairs startup through Steam -applaunch289070 -skip-intro, hidden launch, waits up to300sec forMainMenu. ControllerPID11056, active-stage.json authoritative. Same native control SQL installed BEFORE processlaunch, plus Workshop private80child. No competingTuner. Script cleanup restoresSQL/prefs; no extra5games authorized. After success inspect results and native-db snapshot, then implement cold-launched candidate/natural250; if blocked report honestly.

Steam spawned CivilizationVI_DX12 PID4288 (22:49:20), unlike prior DX11 CivilizationVI.exe. Diagnostic only: record renderer/version if natural later uses this. Existing quarter_resource_job.py watchdog checks ONLY CivilizationVI.exe and MUST support both executables before a DX12 natural run, or it will incorrectly stop a healthy worker. Prefer matching prior DX11 if practical; don't launch competing game now.


IMPORTANT CORRECTION (23:04): Diagnostic09 native-debug.sqlite revealed controls existed ONLY in Modifiers; their ModifierArguments and DistrictModifiers were absent. Database.log shows exact cause: diagnostic INSERT INTO ModifierArguments VALUES used3values against native6columns. Earlier diagnostic06 also had Types3columns vs2values. These setup SQL defects invalidate diagnostic02/06/07/09 zeros as tests of those controls and DO NOT support the native-cache hypothesis. No natural run happened. Error was ours; user informed. Original v1 source uses explicit column lists and is unaffected by this diagnostic defect. Diagnostic10 fixes ALL argument/attachment INSERTs with explicit column lists, runs complete SQL against captured native schema in memory (passed11argumentrows/6Quarterattachments), AND asserts native11/6 rows before fixture. ControllerPID4692, active-stage.json/root/diagnostic10. Same new production readouts, before/immediate/settled core/UI controls and Workshop private80chain. No competingTuner while alive. All runtime control diagnoses must first prove native DB rows/args/attachments and check Gameplay ERROR lines, rather than trust GameInfo modifier-row presence. Source/installed cleanup automatic; ONE250naturalgame only, five laterdeferred.


Diagnostic10 native controls successfully instantiated (native11argumentrows/6attachments asserted), so prior cache hypothesis rejected. City/Player plot-yield controls track7plots each; chosen manually-owned ring2 materials are outside their tracked collection and give0 even for unconditional Gold. Next fixture tests resources on original city ring1 plots that already have native yield objects, avoiding WorldBuilder acquisition. Diagnostic11 PID17916 ownsTuner; native_owned_fixture.lua intersects City+Quarter neighbors, asserts original ownership, adds farFlax on a city-ring1 plot distance2fromQuarter to distinguish Quarter vs citycenter anchoring. Same validated Gold/Workshop controls. Automatic SQL/prefs cleanup. Actual natural game not started. Staged only CSC_AI_workshop_v2_staged.sql in visualization (not installed/source): present40 originaldirect, extra80 moved to Workshop improvement-attach/singleplotchild. Native-schema tested21marginalwrappers/replayidentical, pending diagnostic11 evidence before applying. Future natural runner fixture must use originalownedplots, farcontrol and pristine reload; watchdog must accept DX12. One250naturalgame only.


### Resolved native fixture and single v2 launch

Diagnostic11 PASSED mechanism evidence: UI adjacent improved Flax private120, unrelated Stone0 and farFlax0 for BOTH Quarters; unconditional Gold12 improved /5 on other ownedplots also applied. Gameplay Plot:GetYield reads omit these modifier additions (returned0), whereas PlotInfo UI returns them. Native source requirements select exactly one adjacentFlax; farFlaxdistance2 stays0, so source position works as desired. Original-ring1 fixture fixes previous off-collection WorldBuilder-owned ring2 targets. No native-cache explanation needed. Diagnostic11 sourceSQL/preferences restored verified.

Applied v2 source CSC_AI.sql: present40 direct native matching plot effect retained; extra80 now uses the exact Textile Workshop mechanism (Quarter-owned player-improvement attach -> single-plot private-yield child). Existing AI90/Builder50/native12/4/10 remain. Native-schema validator passed42wrappers + child/replay. Fixture uses original-owned targets plus farcontrol; tests UI40/120/pillaged40/unmapped0/far0, then reloads original saved start and requires identical census. No Gold controls in source/installed candidate. Live UI mismatches are recorded for audit, do not abort/discard natural run. Supervisor watchdog corrected to accept DX11 AND DX12. Current render executableDX12 versus historicalDX11 is an explicit comparison limitation.

Single natural run supervisor19932 launched at root/trial-v2 (active-stage.json authoritative), initially native preflight then250autoplay. Target250 only; T1-T5 deferred, not scheduled. Exact new archive trial-v2/source-version contains41current pinned source copies and121installed gameplay text files, index/version/hashes, archived before controller start. Code_version quarter-owned-workshop80-builder50-v2, sourceSQL SHA237b6d344bf92603d289d53a8ebc38ac8ed480c1099107c392f3bc71fb81f995. Prior trial/source-version v1 untouched. Args captures=csc-implemented-native-20261016, baseline=csc-ai-paired-standard-20261016, previous=csc-ai-density-v4-20261017/trial. Worker/supervisor ownTuner; no competingconnection or source edits while pinned. Sparse followup reads trial-v2/job-status.json/live-status.json and short root/trial-v2 stdout/stderr. Once finished validate nativefixture/pristine/DB/preferences/snapshots, analyze200/250 and save durable results. Delete schedule after this ONE game; don't launch later5.


v2 setup stopped before fixture/autoplay: native validator inventory hashed rowid order. Reapplying native CSC_AI reordered ModifierArguments but preserved exact7781rows/value multiset; no duplicate or behavioral delta. Validator fixed to canonical sorted full-row multisets (still detects duplicates/counts/value changes). Loaded native validation now passed with changed_tables[]. Gameplay source/install hash remains237b6d...f995. Full logs contain earlier diagnostic errors from same Civ session; controller now snapshots byteoffset+prefix before starting map, validates run-only sliced logs, preserves full-session logs separately. v2 original output/source archive preserved, prefs142/auto_startfalse verified restored.

Single corrected setup v2b launched supervisor14072 at root/trial-v2b, active-stage.json authoritative. Same exact gameplay/source settings/seed, new41source/121installed file archive before play. Only validator/log scoping controller repairs; code_version quarter-owned-workshop80-builder50-v2b. Native preflight->fixture40/120/pillage40/far0->pristine reload->natural250. No natural turn progress yet at launch. Read trial-v2b/job-status/live-status and parent logs; worker ownsTuner, no source edits/competingclient. T1-T5 remain deferred; delete heartbeat after singlegame. Source same driverDX12limitation, previousdensity-v4 DX11. Preserve partial progress on failure, don't blindly rerun crashed games.


Natural game v2b DID run after all native gates passed: fixture UI40/120/pillaged40/unmapped0/far0 and pristine-census identical. Native snapshot25/50 archived. Controller stopped at an OPTIONAL read-only UI probe at50: UI city:GetDistricts():GetNumDistricts missing (gameplay-only API). No Civ crash. It continued natively to63 during cleanup, archived autosaves60-63, returnedmenu and restored142prefs/autostartfalse. Do not call this a failed gameplay experiment or restart its map.

Resuming SAME game from archived AutoSave0063 via new source quarter_resource_resume.py, supervisor3980/root/trial-v2c-resume, active-stage.json. Gameplay hash/settings unchanged. Source-version archives42current files/121installed plus earlier segment reference, resume-save hash. UI probe rewritten to Map plots and tech/civic visibility; optional probe errors now recorded nonfatally. New resume controller loads existing save, freezes immediately, records actualresumeTurn(63..70), reinjects readonly observers, prepends preserved <=50 event prefix OFFLINE to later snapshots, continues to250. Explicit observation gap51..resumeTurn; NOT reconstructed. Turn50 Builder census/private sample not exported. Builder training/purchase/addition comparisons use COMMON observed window resumeTurn+1 onward for prior and new games; alive/charges endpoints complete. Final city/pop/improvement/Quarter/Services state counts complete; placement-choice/event statistics observedsubset with gap. No fake missing50 data. Validation allows missing50 Builder only with gapmanifest, still requires real75..250 snapshots/100..250Builder andsource/native/prefs. Originalv2b output/archives preserved. No source edits or competingTuner while continuationalive. OnlyONEgame still; other5deferred. Probe/native logic application doesn't prove nativeAI forecasting. After250 validate/report compact metrics withgap+DX12limits, durable notes, delete schedule.


v2c recovery did not load: LoadGameViewState.log shows GAMECORE_LOAD_SAVEFILE begin/end in0.0002sec thenbackfrontend, before any deserialization. No additional natural turns; prefs142/autostartfalse restored verified. One FINAL bounded same-autosave attempt now root/trial-v2d-resume supervisor14704. Resume code copies archived63 save byte-identically to normal native Saves/Single/CSC_QR_Resume_0063_20261019.Civ6Save, verifiesSHA, uses standard Network.LeaveGame +LoadGame and logs return. No newmap/gameplay changes. active-stage.json bounded_last_resume_attempt=true. If load fails again, STOP recovery, preserve50checkpoints/63autosave, write partial report andDELETEheartbeat; user already informed bounded last attempt. If successful, same250continuation withexplicitgap and matchedBuilderwindow. New42source/121installed archive records pathrepair; originaldata intact.

Compact actualturn50 comparison preserved root/partial-turn50-summary.json: previous14cities63pop36improved(2.57/city), current15cities78pop61improved(4.07/city). Bakers previous10complete/5base/4of6adjacentBaseimproved; current11complete/7base/3of9improved. Tailors previous3complete/0base; current6complete/1base/1of1improved. No activeServices either at50. Preliminaryearlystate, not requested250result; cannotisolate private signal vsBuilder50/900 orrendererDX12vsDX11. Full source/nativefixture successes remain valid despiteharness/loadfailure. Do not discard savedprogress.


CORRECTION / successful save recovery: v2d DID load the unchanged turn63 save from normal Saves/Single (resume-saveSHA e2a4fd41b9e514749bfb9db4c5badea97937c8ffcb51e2100540b9ac862c983b). Failure was then observer-only: GameCurrent advanced while observers were injected; requesting stale checkpoint63 raised Historical checkpoint missing. It was NOT another loadfailure/corruptsave or gameplaycrash. User informed. Normal-save-directory copy +standard Network.LeaveGame/LoadGame is proven route; archived sourceunchanged. Prefs restored after v2d verified.

v2e fixes exact known race: after observer injection, one native call freezes CSCBASE.capture and Builder.Capture at the ACTUAL GameCurrent turn, prints thatturn, and subsequently exports frozen checkpoints. Records actualgap51..frozenTurn and matched Builder comparison window. Supervisor4204/root/trial-v2e-resume; active-stage.json updated, new42source/121installed archive before continuation, sourceSQL unchanged237b6d..f995. Same original63autosave, no newworld. Bounded final LOAD succeeded; this is correcting subsequent observer timing, not blindly retryingfailedload. If this continuation fails again, STOP and summarizepreservedpartialresults ratherthan keeprepairingovernight. StillonlyONE250game authorized;5laterdeferred. All previousnativefixture40/120/pillage40/far0/pristineproof valid, early50statsavailable. Worker ownsTuner/pinnedsource, no concurrentclient. Heartbeat nextcheck currentjob/live/stdout/stderr only unlessterminal.
