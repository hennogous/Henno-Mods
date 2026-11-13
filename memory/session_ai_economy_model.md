# Central Quarter economy implementation — 13 November 2026

COMPLETED: integrated candidate and architecture diagram pushed34fb0921 (initial
docde392005). CE API6f53037/docs3421b37 pushed, noPR; skillb8b384c pushed.
All finalsource8AI/UI hashes match frozen03; final3/preceding30 runtime evidence
andAstrareview pass. No activegame/worker, allpreferences/packages restored.
Next longer outcome qualification is follow-up, not an unfulfilled launch order.
Durable status: project/docs/civ6-ai/architecture.md and research report
csc-ai-central-economy-20261113.md. Earlier chronologicalnotes below retain their
historical meaning. All source/tests/docs own changes committed; unrelateddirty
work leftintact. Originalautomaticgoal remains paused.

ACTIVE USER TASK: integrate accurate recurring building transaction forecasts
and fulfil the already agreed central cross-Quarter model plus decision adapters.
Do not stop at a plan or claim early heuristic tuning implements that model.
User explicitly reminded us this was our/Astra's existing roadmap direction.

Recovered historical roadmap commit 057d4c5501fcc58b357771105fbf6d0aa2e73ca5
(6 November): shared evaluator across families, full CSC bid when surgical
corrections require most of that evaluator; revisit BEFORE broad native component
feed. Current roadmap had lost that prominence. Restore and follow it; no new
broad modifier-root observation subsystem for this implementation.

Previous task fixed RequiresPopulation=1 for Bakers/Tailors, source commits
e764bb9f (docs/test) and bc228892 (isolated two SQL hunks). Fresh native validation
pending. Tests execute actual INSERTs in SQLite. Other substantial SQL/art/UI
worktree changes are unrelated and must NOT be committed. Prior normal200 run
complete/closed, all settings/packages restored, no controller owns console.
Old automatic goal remains paused. No PRs. Shared controller only, NO Computer
Use on Shadow. Check autonomous games about15min. No new full game yet.

Initial architecture audit: only shared Stage2 chain snapshot in
CSC_AI_QuarterPlacement.lua. Main publisher still early-only, no dynamic late
transaction forecast. BakersAdjustment is diagnostic-only. Bridge validates only
early CE entries; CE existing LateEntry requires stale expected before/final
scores and cannot serve a general recurring model by itself.

Implementation direction under development:
- pure Lua central economic ledger (real amounts, gates, recipients, dependencies,
  costs and timing), live catalog/facts boundary, separate decision adapters;
- no future customer district yield, per12Nov. Future buildings in existing
  complete districts may support credible transactions; improvements/unlocks
  are remaining investments, not free existing supply;
- generic CE native income pricing using native NormalizeYields and
  DiscountTimedIncomeStream, plus native amenity pricing if qualified;
- generic guarded FINAL district-score entry, using live matrix/eligibility/
  reservation/generation guards, no pre-recorded expected score. Replaces the
  complete CSC-only Quarter bid after native building aggregation, avoiding
  double counting. Keep native other-district/unit/project competition;
- reuse central model for future building/job/repair adapters. Preserve known
  native protections while wiring integrations; explicitly report missing
  channels instead of claiming a perfect whole-economy valuation.

Native source current fork:
C:/Users/Shadow/Desktop/Codex/csc-gamecore-hotfix-20261106/ce-source
subdir CivilizationVI_CommunityExtension/AIDistrictScores.cpp, native/target_identity.h,
native/tests/district_score_checks.inl and selftest.cpp. Outside writable roots:
editing/build/git requires require_escalated. Read ordinary source directly.
Current feature already idiomatic C++20 Runtime::InstallHookGroup; follow it.
Do not use old csc-ce-develop-port source (old binary identity).

Ghidra get_program_info confirmed old reference SHA324c51e9...98c; known supported
hotfix SHA092abfbb...c41f has identical .text/layout (prior requalification).
No live instrumentation done in this task. REA/Ghidra tools available. Read
reverse-engineer-anything SKILL.md this turn; use available tool schemas.

Confirmed decompilation addresses (image base180000000):
- 3dfee0 CalculateDistrictValues: adds positive raw building sums to positive
  district matrix cells. Wrapper also propagates prerequisite building vectors.
- 52b110 NormalizeYields(out, amountQ8*, yieldIndex, nativePlayer*): multiplies
  Yield.DefaultValue and, when player!=null, GrandStrategic::YieldBonus capped
  at9*256; output Q8. Amount argument is mutable local copy.
- 528660 DiscountTimedIncomeStream(out, incomeQ8*, discountQ8*, ready, horizon),
  wraps528310. Same stream helper observed480 calls in old study.
- 5272a0 AmenityValue(out, player, city, count, discountQ8*, ready, horizon).
- 306b80 returns native player-registry global DAT_b8e140 (safe null check).
  Registry+20 points at player array, player pointer at[id*8].
- native player+6d0 is native cities; 2c4360(container, cityId) returns native city
  (verified via CManager::GetCity42d20, which then wraps in an export object).
  Validate returned city's owner+d8, id+a8 against API keys.
- 52af40 NormalizePseudoYields available if needed for actual GPP/Tourism.
Need ABI fingerprints/target identities and tests BEFORE adding native calls.
Existing CE policy lock must never span an HKS call or original native hook.

Existing module constants:4096 entries, Q8=256, negative floor -4096*256,
MaxDelta4096*256, original InvalidScore=-9999*256. Entry fields player/city/
district/plot/delta/expectedBefore/expectedFinal; hasLateEntries. resolve_late_cell
currently owned-only/unreserved, row>0, native matrix alias validated. Existing
early and late entries mutually exclusive per pair. Native worker never calls Lua.
LateBatch captures row and matchedBefore, then original_cache(), then guarded
apply. New final mode needs explicit mode/flag and capture/apply handling,
with early hook skipping it, validation, status/capability and receipts.

Native wrappers known from shipped UI: queue:GetBuildingCost(index),
GetDistrictCost(index). playerTechs:GetResearchCost(index)/GetResearchProgress;
playerCulture:GetCultureCost(index)/GetCulturalProgress. Paths Base/Assets/UI/
Screens/TechTree.lua and CivicsTree.lua. plot:GetWorkerCount() used by actual
CSC_AdjacencyCore.lua. Avoid inventing wrappers.

Gameplay metadata: CSC_QuarterFlowBuildings (QuarterKey,Stage,BuildingType),
CSC_QuarterCustomerBuildings (QuarterKey,DistrictType,BuildingType,ProducerStage),
CSC_Stage3CustomerTransactions with seller/customer building+district and actual
EngineAmountPerPopulation (.101 current worktree). Read replacements.
Amounts for ordinary Stage2/4 transfers live in actual ModifierArguments.
Do not assume future customer districts. No current code changes in this task
yet, beyond this carryover file; implementation still required.


USER STEERING: all Problems1 and2 of roadmap, i.e.1.1–1.8 and2.1–2.2,
are in scope for the combination of central model + decision adapters + native
systems. Not just a Quarter forecast add-on. Preserve working purchase, follow-
through/decline/customer SQL/material protection paths; integrate their fact
source/model and enumerate coverage. User explicitly requests Astra code review
WHEN DONE against original intent; do that before final delivery, fix findings.
Astra delegation now explicitly authorised; use fork_turns none/modelgpt-6-astra.

IMPLEMENTED SO FAR (unfinished, uncommitted):
- Main pure model CSC_AI_EconomyModel.lua (~200lines): emits direct, material,
  producer/local/Stage2–4 customer exchanges and amenity/upkeep streams. Exact
  Q8 per-population rounding. Chooses one Stage2 alternative (neverbothMills).
  Same-city customer builds serialised. Unknown ETA/price failsclosed. Marginal
  method available. Eight actualLua51 tests in project/tools/ai_economy pass.
- Correct CE base discovered: ce-source above was onlyoldhotfix! Use latest
  csc-gamecore-hotfix-20261106/ce-purchase-ownership-review, clean e4f3228,
  all9capabilities/166native checks, correctedCE03DLLa849eff8.
- New isolated CE worktree created FROM e4f3228 at
  Desktop/Codex/csc-ai-economy-20261113/ce-source,
  branch codex/quarter-economy-forecast. No PR.
- In that NEW CE worktree: Entry.finalReplacement; generic
  CE_AIDistrictScoresFinalEntry(player,city,district,plot,wholeBidQ8), mode
  exclusive with early/late; earlyhook skipsit; before/aftermatrix guards,
  invalidsentinel/reservation/generation/budget checks, signedfinal−4096..4096
  utility (Q8). Final trace kind/samples. Existing APIs preserved.
- Native/economy_pricing.inl provides CE_AIEconomyStatus,
  CE_AIYieldStreamValue(owner,city,yield,amountQ8,ready,horizon,discountQ8),
  CE_AIAmenityStreamValue(owner,city,count,ready,horizon,discountQ8).
  Uses actualNormalizeYields/TimedIncome/AmenityValue; nil on unavailable,
  notzero. Native registry global306b80 returnsnull wheninactive; actualplayer
  table+20, player+6d0cities pointer, Find2c4360, validatescityowner/id.
  Nativehelperprefixes added; BuildidentityalreadyfullSHAqualified.
- Buildtools C:/BuildTools/CE-v143, VsDevCmd.bat, MSBuild/Current/Bin/MSBuild.exe.
  Native-selftest/check.cmd undernewoutput compiles supported MSVC C++20 host.
  Initial compilefixedpush_json thirdlengthparam. Added14finalmode/quote guard
  fixtures (expected180native checks +shared4hookchecks+instructioncall).
  One fixture versionbug fixed (++begin version perrepublish); recompile
  CURRENT unifiedexecsession85957, pollresult. No native game launched.

STILL REQUIRED: livefacts/catalog module, decision adapters, mainpublisher and
bridge wiring/import registration, tests/adversarialcases, actualCE DLL build,
controlledsharedcontroller nativeacceptance (and freshcapacityflagvalidation),
all10coverageverification, documentation, scopedcommits/pushes, Astrafinishedcode
review with fixes. Cannotfinalclaimintegrationyet. No broad componentfeed.

Latest model quantities currentlydefaults1 perstandardCSCmechanics; bind them
or validate against actualModifierArguments before callingmodel accurate.
Stage3 rate reads actualloadedregistry(.101currentworktree), Stage4 pervenue
floor(customerpop/5). Source tags/rules capture both directions of district
adjacency; do NOT forget counterpartdistrict gains fromQuarter.
No speculative customer districts; onlycompletedcurrentdistricts support future
mappedbuildings. CityCenter countedcompleted. Wondercustomers onlyactualcorrect
Wonderfootprint, notanotherDISTRICT_WONDER. Resolveunique replacements/traits.
Researchcost API verified in shipped UI Screens/TechTree andCivicsTree:
GetResearchCost/Progress, GetCultureCost/GetCulturalProgress. Queuebuilding/
districtcost wrappers verified inProductionPanel. GetWorkerCount actualplotAPI.
Observepolicyomissions (Services/staffing/trade) explicitly; don'tdoublecount
nativebuildingpremium afterfullbidreplacement. OldcalibratedServicebuilding
nominationcanremainclearlyidentifiedadapterpolicy untilits modelvaluationscope
ispriced; all1+2mustnowusecentralobservationandbidmodelorjustifiednativeinput.


MID-TASK UPDATE (13Nov ~09:20):
User also explicitly requests architecture document with visual. DONE/pushed
`de392005`: project/docs/civ6-ai/architecture.md, linked index/STATUS/roadmap.
It maps ALL1.1–1.8+2.1–2.2 and marks candidate/live qualification separately.

Astra agent /root/astra_economy_review (gpt-6-astra, explicitly user requested)
reviewed twice, independently17Lua testsPASS. Fixed blockers: native pricing
qualification nevercalled; HKSintegers; serialpercityqueues+ORbuildingprereqs;
optional2/2+3/2+4/allplans+boundedcustomerpruning; propertyaggregatedpopulation
rounding+epsilon+otherworking-sellerrawbaseline; regionalamenitynonstack;
workedfootprintdisplacement; reciprocalmultipliers; quote-fault protectionfallback;
wholepublicationcapacityfallback (no partialmixedscale); wholeplayerfallbackif
anylegalquoteunknown; completefrontiercoverage beyondoldbestonly.
LastAstrafinding: oldUIGetPlotPurchaseQuote filters tied/cheaper buyers, so whole
frontier scan triggeredfallback. FIXED afterclosedsmoke03: newrawinvoicehelper,
plus newUIGetEconomyCityNumber/GetEconomyResearchNumbers/GetEconomyPlotFacts;
Facts caches nativeUI-only reads withinpublication. Added2cityrawvslegacytest.
Need FINAL Astrareview again aftersmoke30 and anyfixes. Do not claimclosedyet.

Nativeworktree Desktop/Codex/csc-ai-economy-20261113/ce-source branch
codex/quarter-economy-forecast FROMlatest e4f3228. Native184checks +4hookgroups
+instructionrestorationPASS. SupportedReleasebuildPASS; missing ignoredMinHook
lib copied from existingpinnedcsc-ce-develop-port environment/compat/Release,
SHAa94cd15f72cf84612e86b023c4e514d8b20d2afd62f88065d67e05f2213bc894.
NewDLLSHA09d51ddd0c471959b8f0ebece33b30bf0758201b79928696610cd82597bdcdc9.
Buildlog/outputunderDesktop/Codex/csc-ai-economy-20261113. NativeREADME API docs,
commit/push stillneeded. NoPR. Upstreamdeveloprecheckedunchanged2986a746.

Smoke03 sharedcontroller freshnormal3turns COMPLETEexit0, preferencesrestored,
allownersabsent. Read-onlyquoteproof5AIs: per1Production/50turns=6435Q8,
oneoff−70Gold=−10745 (P5−12530), amenity1=5148Q8. pricingReady/finalReady1.
NOeconomicfinalbids: everyQuarterreadinessunavailable, fallbackworks. Thuscan't
claimmainintegrationliveyet. SuspectGameplayonlycost/yieldmethods; addedUI
factwrappers above. preflightnowalsoexplicitflag==1/true andfactasserts.

CURRENT RUNNING worker unifiedexecsession18647: smoke30, newfrozen02 exact639CSC
+6CE (completecurrentmainpackagegeneratedFiraxismanifest; carrierA17/dependency),
only3overlaysvsfrozen03(EconomyFacts,Adapters,AdjacencyUI). FreshsameOnline seeds
18461107/29461107, through30, mainCSCpolicyONLY; --economy-preflight read-only
endpoint helpers/facts/capacity. NoFrida/forcedunlocks/probemode. Sharedcontroller
ce_bakers_fresh. Do notedit imported/pinnedcodewhileworkeractive. Need inspect
completion/faults/actualfinal>0+nativeFinalreceipts, ensureownership/preferences
restoration. IfUIbindingsstillbad, diagnosefromread-onlyfacts logs; don'tclaim
fallbacksuccessisintegration. Preservefirst03artifactnegative.

Testsuse Python312 python.exe with PYTHONPATH=C:/Windows/Temp/csc-ai-economy-python
(lupa2.8 isolatedinstall; defaultHermesPythonhasnopip/lupa). Testsnow18inclnew
UIrawinvoicefixture butlastexecuted17beforethat addition; existing12CEfrontendPASS.
Newmodulesregistered actionJSON &civ6projgeneratedactions+ContentIncludes. These
fileshaveunrelateddirtyedits: stageHEADreconstructedwithONLYour3imports/content
ratherthanwholeworktree. AllotherunrelatedSQL/UI/artdirtymustpreserve. Native
customerSQLextendedallmappedStage2–4ordinarydistricts; dedupedoneprivateyieldedge
perdistrict/Quarter, excludesCityCenter/Wonder. SQLfixtureexecutestwicePASS.

Stillrequired: successfulmainfinalbids/nativeconsumption, factsbindingsfixtures
andAstrafinalreview, nativeAPI docs, scopedsource/CEcommits+pushes(noPR), durable
report/statusaccurate. docsarchitecturerevisionstatuscurrentlyinprogress.

FINAL IMPLEMENTATION/ACCEPTANCE UPDATE:
- CE featureAPI committed/pushed6f53037, branchcodex/quarter-economy-forecast;
  NO PR. Reusable skilldocs AI-N123/district-score-anatomy b8b384c pushed.
- smoke30 COMPLETE30 exit0 allrestore.150playerplans144withfinalvalues;4628
  finalentriesacrossrefreshes, max304, unknown/omitted/faults0.448boundedexact
  receipts413withwrites,448cachereads49citycomparisons0sampledsitewins.3696
  aggregatepriorpacketmatched/changed(notlabelledallFinal). Version30endpoint
  freshunconsumedcounters0doesNOTnegatereceipts. Coarselogtimemax1s,notmaturetest.
  root/smoke30-audit.json reconstructsrawlogs. Revisionfrozen02 predatesfinalfixes.
- Postreviewfixes: mergepartialUIfactsindividually; cacheprice/exclusivequotes;
  positivefrontierbidscapped0unlessoldexclusivebuyerhelperqualifies(thisdoesNOT
  forceEconomicbuyer); marginalmateriallossrecomputessamedirectruleswithout
  deposit inclthresholds/multipliers. Structuralfloorsunchanged.
- Finalsourcefrozen03/smoke03-final COMPLETE3 exit0/restored. All8AI/UIfileshash
  matchcurrentmain(inclpublicPlotFactssnapshotreader).16exactreceipts16writes/
  cache/eligiblecomparisons, no sitewin. All5read-onlynativepricing+numericfacts
  pass;CraftsmanshipstilllockedETA22/22/22/13/23. Bothslotflags1loadedverified.
- Astra /root/astra_economy_review finalreadonlyreview: no remainingblockers,
  independently22economictestsPASS. Mainfrontend15PASS, scanner28PASS,
  actualSQLslotregression1PASS.184native+4groups+instructionrestorationPASS.
  Sourceonlylasttestsaddedpublisher4097capacityfallbackregression; noothergames.
- Durablearchitecturepushedde392005; laterupdateddoc/status/findingsAI-C171 plus
  project/docs/research/mods/csc-ai-central-economy-20261113.md nowawaitCSCcommit.
- STILL TO DO BEFORE FINAL: stageOWNCSCsource/tests/docs/memory and3module
  registrations ONLY. actionJSON/civ6projhaveOTHERdirtychanges; reconstructHEAD
  withonly3imports/contentforindex, preserveworktreeothers. Commit/pushscoped.
  Finaldiff/clean-ownscopecheck, repo-linksfinal. No sourcechangesneedednow.
  Do notclaimbetterplacement/fullgameoutcome;nextlonggameisonlyfollowup.

Final follow-up: source/docs committed34fb0921 and pushed; stage-only3module
registrations verified, allowncode clean. Finalcarryover/report wordingtouches
committed separately after this note. No requiredimplementationwork remains.
