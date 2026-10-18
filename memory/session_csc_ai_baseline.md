# CSC AI baseline — 15 October 2026

User authorized five natural autoplay games to turn 200 before any AI tuning.
Explicit setup answer: CSC + standard game AI. This resumes automation despite
the earlier manual-QA pause. No gameplay source/AI weights are to be changed.

User correction: material-return issues were FALSE REPORTS; material returns
work. Added correction notices to old Tailors QA report/fix report and memory.
Installed SQL/Lua/XML files matched current source before the baseline.

Source tools: `project/tools/ai_baseline/{run.py,observer.lua,analyze.py}`.
Output: `C:/Users/Shadow/Desktop/Codex/csc-ai-baseline-20261015/`.
Current batch process is the Python `ai_baseline/run.py` command, unified exec
session 54102. Inspect progress.log and batch.json before taking action; do not
connect a second tuner while the runner is active. Port 4318 is responsive;
4319 is a separate nonresponsive debugger listener, not a fallback tuner.
Native FireTuner2 GUI was closed to free the single-client tuner.

Original active game was turn1/no cities. Preserved completed save:
`CSC before AI baseline 20261015.Civ6Save`, copied into output by runner.
Original mod preferences and native auto-start flag are in original-preferences.json.
Runner restores them at final menu. No process killing of Civ was needed.

Settings: Small Continents (verified 74x46), six random major civs, nine city
states, Standard speed, Prince, standard modes (M&C false). Map seeds
830001+i*101 and game seeds 940001+i*103 for i=1..5. Native map/speed/difficulty
setters are required: setting string MAP_SIZE via SetValue silently generated
Duel. Pilot Duel run excluded in pilot-duel-excluded. Another menu dispatch
attempt used nonexistent UpdatePlayerCounts; removed before valid games.
Observer originally iterated Cities:Members incorrectly with one variable;
fixed before valid Small game. Valid game1 starts at progress 20:44:16,
turn1 snapshot20:45:32. All valid checkpoints so far have zero recorder errors.

Read-only Lua observer records district placement events and improvements,
player-turn-start owned native-plot-legal Quarter/customer candidates, 25-turn
snapshots, source activation properties, hidden Service buildings, major cities,
districts/buildings, tech/civic completion and owned/resource plots with yields.
No terrain/debug fixtures, grants, forced refreshes or gameplay properties.
Final saves/logs archived per game. Major civs are primary sample; city-state
events are retained but excluded from major-choice statistics.

Analyzer removes repeated DistrictAddedToMap appearances of the same plot/type
(capture triggers these). Candidate caches are at most one turn old; these are
owned terrain-valid sites, not complete production/affordability checks. Do not
claim causal AI understanding from the observational baseline. Source/venue/
material/civic gates are separated for Service interpretation. Python odd-row
distance verified against all native sales neighbors in game1 turn175.

Game1 at turn175: 32 major cities, 34 completed Quarters (26 Bakers, 8 Tailors).
Zero recorder errors. Bakers24/26 adjacent sales, 7 base,2 spec,0 both; 22 mills,
3 Bakeries,0 Cafes. Tailors0/8 materials,1 sales,0 Textile Workshops. Two Bakers
growth source cities. Four original owned adjacent materials later replaced by
Campus/Preserve/Thanh/Commercial Hub. These are INTERIM game1 observations, not
five-game conclusions. Waiting for all five completions before final report.

Runner invocation:
`python project/tools/ai_baseline/run.py --output <output>`.
On a stopped checkpoint, updated source supports --resume-current --first N
--last 5; it requires live observer and inactive autoplay. This option was added
after current process loaded, so current process uses its original main loop.
Current batch.json was manually reset from stale excluded-pilot error to running;
the live original main loop writes completion or an actual failure at the end.

Next: finish five games; run analyze.py --output <output>; verify saves/snapshot
coverage/build consistency and zero observer errors; review raw choices for
aggregate claims; publish durable report under project/docs/research/mods and
update its index. Raw artifacts stay Desktop/Codex. Leave no AI tuning changes.

## Continuation update 21:02

Game1 COMPLETE at turn200, save/logs/9 snapshots verified, 36 major cities,
30 completed Bakers and9 Tailors. Growth source3, no other Services. Materials:
0 Quarters retain both owned classes at200. Installed database has zero CSC AI
preference entries and zero native CSC adjacency rows. Runtime unlock/reference
data pinned by capture_reference.py to output/mechanics-reference.json.

Current live runner is unified session43534, resumed game2 at turn25 using
`--resume-current --first 2 --last 5`. Native IsActive briefly cleared at24 before
the pending tick advanced to25; initial runner stopped without changing the game.
Added up to3 settling polls; source supports resumes and writes all completed
games into final batch.json. Game2 at75 as of21:02, zero recorder errors. New
leader roster (Pachacuti/Saladin/Sejong/Elizabeth/Matthias/Kristina) and map74x46
verified. Do not use old session54102 or connect concurrently to live runner.

analyze.py now generates analysis.json, seven CSVs and report.md in output, and
can preview a partial checkpoint via analyze(folder,turn). Report is partial
until all five complete. Building unlocks read exact runtime metadata, not stale
public docs. Source/venue/civic/material gates split. Material retention counts
resource loss beneath later districts. Final report still needs human-facing
interpretation after five games, then copy/promote to project research docs.

## Continuation update 21:23

Games1–3 COMPLETE with 9 snapshots, completed save, logs and zero observer errors.
Game3 final41cities,34 completedBakers/10Tailors; Tailors2 Workshops and2 Fashion
Houses (no Tailors), so do not generalize first two games' zero Workshop result.
Batch still running in unifiedsession43534; game4 starts next. analysis.json and
report.md currently contain3 completed games. Source activated Service stages are
not the same count as actual hidden Service buildings (which can persist).
Report header 'Service source cities' sums city-stage flags, not unique cities;
rename it to 'Active supply stages' in final report. Material count optimum should
also be shown only for cases where at least one material site existed (fields
material_opportunity / max_material_with_opportunity). Added non_center_sales to
separate ordinary City Center adjacency. No need to change the recorder.

## Continuation update 21:45

Games1–4 COMPLETE and independently verified:36 snapshots, saves, zero observer/
gameplay SQL errors,111 installed files unchanged. Game5 player0 was eliminated
between100/125. Autoplay returned to dead player0, leaving LocalPlayer=-1 and all
AIs advancing despite IsActive=false. Snapshot request125 returned real126 and
runner correctly stopped; recovered full126JSON from command transcript, labelled
turn-126.json. checkpoint-exceptions.json records125->126 forgame5, not a fake125.
Returned control via1-turn autoplay to first survivingplayer1, paused at140.
Runner now uses first surviving return player. Resumed5in unifiedsession65873
(`--resume-current --first 5 --last 5`). Stable150snapshot passed21:45:10. Remaining
175/200 then save/menu/restore. All final endpoints must still be exactly200.

Analyzer now also includes improvement_comparison.csv (adjacent vs other owned
materials, workable-radius stratification and relevant source buildings) and
strategy_profiles.csv (last monotonic native AI_Victories log segment, latest
Following flags, overlapping groups). Dead players excluded from final active
strategy groups. Four-game aggregates:115 completedBakers,33Tailors,3both owned
material classes,108Bakers sales ofwhich106CC and5nonCC. Sourcebuildings2Tailors
Workshops/2FashionHouses. Materialreturns false report correction remains in QA
docs only, removed from baseline report as irrelevant conversational history.

## Final outcome

COMPLETE: all five games ended exactlyturn200. Batch status complete for1..5.
Independent verify.py:45labelled snapshots,5validsaveSHA256s,zero observer errors,
zero gameplaySQLerrors,111 installedSQL/Lua/XML/manifestfiles unchanged. Same
observer script throughout. Game5onlycheckpoint exception125->126 documented;
all5endpoints200. Native mainmenu,original142modpreferences andauto-start restored
and verified at21:49:15. Original userturn1game preserved in separate completedsave.

Durable report: project/docs/research/mods/csc-ai-baseline-20261015.md, indexed
in researchREADME. Raw evidence and final-report.md remain at the Desktop output.
ToolsREADME + run.py/observer.lua/analyze.py/capture_reference.py/verify.py retained
under project/tools/ai_baseline. No gameplay/AI tuning changes made.

Five-game census:30civilization starts,29survivors,175majorcity observations,
211placedQuarters ofwhich188complete (145Bakers,43Tailors). Bothowned material
classes5Bakers/0Tailors; non-CC sales9Bakers/8Tailors. Mills130/Bakeries14/Cafes0;
Workshops4/Tailors0/FashionHouses2. Improved adjacent materials38/78Bakers,2/6Tailors.
12distinct original ownedmaterialplots laterreplacedbydistricts. Nativeflags show
onlyGrowthsourceactive12city observations;15Storekeeperbuildings, no otherServices.
All29survivors lackNavalTradition/Urbanization/OperaBallet (explicitlychecked).
Materialbearing owned alternatives existed in108Bakers/13Tailors placementsets;
zero-material chosen38/108 and8/13. Latercustomers choseQuarteradjacency9/25Bakers,
3/18Tailors where anownednativeplot-legal option existed. These areobservations,
not causal proof of AI custom-adjacency scoring or intentions.

## Turn 400 continuation — 16 October 2026

User explicitly authorized continuing all five archived worlds to400 and using
that as the baseline. Original200 archive remains intact. All111 installed
files matched before starting. Civ was closed; launched via Steam. New output:
C:/Users/Shadow/Desktop/Codex/csc-ai-baseline-turn400-20261016/.
Continuation runner: project/tools/ai_baseline/continue_saved.py, unified exec
session46400. Do not query tuner concurrently. Game1 reloaded200; city/district/
building/population and every recorded plot identical to archived200 snapshot.
Observer is re-injected; each new snapshot concatenates original200 event
prefix and fresh observer history. Original checkpoints copied byte-identically.
Targets225/250/275/300/325/350/375/400. New400saves/logs archived separately.
Original preference snapshot is captured again for this run; restore at end.
Source scripts analyze.py/verify.py support --turn400; longitudinal.py exports
200vs400 summary, decision periods, civic and building exposure. No gameplay or
AI tuning changes. Materialreturns false reports remain resolved.
Computer-use skill loaded to inspect loading state; @oai/sky via node_repl.
Gamewindowid1573238 (refresh on stale). Native4318 temporarily disappeared
while load finished, then recovered; no observation gap. Runner ready200 at
06:18:04, began autoplay; game1turn216 at06:19:14. No failures so far.

06:40:43: Game1 COMPLETE at400 (56cities,70completedQuarters=46B/24T).
verify --turn400 --allow-partial PASS:17snapshots,saveSHA,unchanged111files,
zeroobserver/SQLerrors. Full five-game validation remains pending. Game2 next.
Newloop still unifiedsession46400. Partialanalysisfiles correctlycontain1game.
07:06: Game2 reached400 (58cities), save/archive next; batch continues in session46400. No recorder errors. Game1 fully verified. Recheck partialvalidation gamecount before claiming Game2 verified.
07:06:29 partial verify PASS for BOTH completed games,34snapshots, unchanged111files,zero recorder/SQL errors. Analyze/longitudinal regenerated for2games. Game3 next.

07:13 user asked how many both-material opportunities actually on first2 maps.
Answered while game3 continued: geometric LAND upperbounds game1 B18/T0,
game2B25knownland+2unknownterrain/T1. These are NOT full placement legality:
Tea on one game1site; geothermal fissure game2site; ownership/reach/tech etc
not all eligible. Actual distinct owned native-plot-legal both sites recorded
at Quarter placement decisions: game1B3/T0, game2B6/T0. Nine Bakers decisions
with both option, chosen2; neitherconnection retainsboth at400. Tailors no
such placementdecision opportunity. Tailors game2sole geometric siteplot2538
(22,34) betweenSheep2463/Dyes2612. Bothownedplayer4at200, but sitewasnever
recordedeligiblewhenplacingQuarter; Sheep laterreplacedWonderby400.
New map_opportunities.py outputs map-opportunities.json + siteCSV offline,
first2maps allrawhexB21/28, T0/1; game1water1mountain2, game2water1knownland25
unknown2. Unknownterrainplotsgame2:2431,2504. If useful after batch, read full
terrain census from saved400worlds to resolve these2 (requires reload first2;
do NOT interrupt currentrunner). Mapcounts upperbounds exclude none of the
remaining luxury/feature blockers yet. Include geography denominators in final
report. Allmappositions use initialturn1resources, terrainfromearliestrecord.
Currentgame3at250snap07:12:38,43cities,zeroerrors; session46400stillrunning.
07:15: Game3stalled250 withnative disasteranimationview. Inspected viaSky (StickyKeysOSdialogbrieflyvisiblethenvanishedwithoutouraction). ClickednativecloseXat1906,18; autoplayresumed252at07:15:39 before180sstalltimeout. Observerintact,noforcedturnsorAI/gameplaychanges. Recoveryrecordin game-03/disaster-view-recovery.json.
07:23: Game3sameUIpauseat300, droughtanimation. SkycloseX1906,18 dismissedview; nativegame302confirmedUI. No additionalinputs/gameplaychanges. Recordforfinalmethodnotes.
07:32: Prepared census_saved.py to run ONLY AFTER runner46400 finishes/restoresmenu. It reloads original200saves, readsall3404terrainplots with noadvances, returnsmenu/restoresprefs. Proposed output400root/map-census; map_opportunities.py automaticallyusesfullcensus whenpresent. Resolvesunknownterrainfor all5mapgeographydenominators. Not launchedyet.

07:34 useraskedmap3-5both-materialopportunities. Answeredpendingfullcensus:
LANDgeographiccandidatesB/T: game3 15-17/2; game4 18-29/1-4; game5 21-38/0.
Ranges areunrecordedterrain,NOTalllegalownedbuildsites. Rawallhexgeometry
B/T game3 19/3 (Bwater1mountain1unknown2;Twater1);game4 30/4
(Bwater1unknown11,Tunknown3);game5 38/0(Bunknown17). Fullcensusneededafter
batchtoresolve ranges, planned toolpreparedbutnotrun. Currentgame3turn367
at07:33:46, runner46400active. Keeporiginal5worldsto400goal active.

SCOPE CHANGE07:39: Usercancelled400continuationforgames4/5 (leave200).
Onlygames1/2/3to400. StoppedvalidatedPythoncontrollerPID12952beforeitcould
launch4; nativegame3continueditslastinterval. Newresumecontroller75619
--resume-current --first3 --last3saved3at40007:41:04, restoredoriginalmods/
auto-start07:41:29, batchcompletegames[1,2,3]. Source4/5saves200intact.
NEW TASK: generate5freshmaps vanillaAbundant plus5TARenabledAbundant plus
5TARenabledTrulyAbundantpreset. UserexplicitlyselectedkeepAbundantforTAR
isolation, thenADDED5moreTrulyAbundant. UserexplicitlyselectedCSCenabled
inALLgroups. FuturepreferredspeedOnline. SameSmallContinents6major9CS,
pairedfiveoriginalmap/game seedpairs andleaderrosters sensiblecomparison.
TARsubscribedworkshop901009089,modID960c7ce4-c961-43c8-90bf-282eb7b260ea.
Presetvalues resources3Abundant,25Plentiful,45TrulyAbundant;lowercaseMap
configurationkey"resources" perContinents.lua. TARResourceGeneratorbaseline
TargetPercentage29+3or+45; placement/validterrainsfeatures/harvestsmodifyeven3.
MapanalysisALL8Quarters: B/Tactualruntimeclasses,6unimplementeduseindividual
canonicaldocs/content/quarters/*.md. HillsBASEStonemasons+Blacksmiths;
Forest/JungleBASECarpenters. IndividualCarpenterspagealsoCopper/IronBASE,
Aluminium/Amber/Dyes/Silk/SilverSPEC (overview/stubolder). Goldsmithsindividual
pageDiamonds/JadeSPEC,overviewalsoPearls; preferindividualpageanddocument.
DefaultCSC_ANIMALsettingactually1inliveSettings.xml,notoldAGENTSoff;B/T
runtimeexactmappingssnapshotneeded(defaultBakersCattle/Honey,SHEEPalwaysT).
NewoutputplanDesktop/Codex/csc-map-material-opportunities-20261016,tools
project/tools/map_survey. NeedcompletefulltileJSONforall15,metadata+mapsaves,
sourcehashes,all8counts&groupcomparisons,rawCSV+durablereport. Noautoplay
neededfornewmapgames: snapshotturn1thenreturnmenu. Mustrestoreoriginal
modprefs/autostartafter. ExistingSkygamewindow1573238sameprocess.
DoNOTlauncholdcensus_saved.pynow;new15mapspriority. Old3verified400report
canbeupdatedbrieflyincompletion,butmainrequestnowmapresourcecomparison.
CORRECTION: Game3verifyfailedbecauseIresumedat400butresume-currentskippedcurrentendpoint snapshotbeforemenu. Game3finalsave400verifiedexists, butfinalstateJSONnotexported and375-400eventhistorylostuponexit. Mustrecoverendpointfrom400savewithfreshobserver+prefix375,andexplicitlymarkeventgap. DoNOTclaimcompletehistoryorzeroerrorsfullvalidation3. Userinformed. Othergames1/2fullyvalid.

07:50: Newmaprunner launched unifiedsession63664 (exclusiveTunerowner).
project/tools/map_survey/{run.py,dump.lua,materials.json,analyze.py,verify.py,README.md}.
OutputDesktop/Codex/csc-map-material-opportunities-20261016. 3groups x5:
vanilla-abundant(falseTAR,resources3),tar-abundant(true,3),tar-truly-abundant(true,45).
CSCexplicitlyENABLEDall,ANIMALresources1(currentdefault),unusedmodsremoved1,
MCfalse. SmallContinents74x46,6majors9CS,OnlinePrince,pairedoriginal5seeds+
recordedleaderrosters. NativeMapConfigurationlowercase"resources"required.
Mapdumpsfull3404tileswithNATIVEneighborlists,water/hills/impassable,resource,
terrain/feature,loadedmetadatatags/harvestdefs; nocustomworldwrites/noadvances.
SavesnativeconfirmedSHApermap;startupCSC/TAR/code/docsha. Restoreatmenuend.
Useanalyze.py+verify.pyaftercompletedmaps(final15); partialsupportedverifyflag.
Maincountsallpassablelandneighborboth, pluscommonclearablefilterandTARharvest
aware. All8designs, B/Tactualruntime,Carpentersindividualpagecopperiron +forest/
junglebase;specaluminumambersilkdyessilver. Goldsmithsindividualdiamondsjade;
overviewPearlssensitivityinmapsummary. HillsbaseStonemasons+Blacksmiths.
Sourcehashlocksanalysis.pyalreadycreatedbeforelaunch, verify.pycreatedafter
so notlocked. Avoidchanginglockedsourceunlessneededanddocumentversionchange.
Oldgame3RECOVEREDendpoint400state07:48:30,event_history_gap375-400explicit.
Oldprefrestored07:48:53. Oldcensus_saved.pyNOTtorun:new15mapspriority.

07:53 Newmaps1/2vanillaAbundantcomplete,6808tiles,16Quarter-maprows partial
verifyPASSsavesSQLsources. FoundfirstdumpMap.GetAdjacentPlots+ipairs truncates
sparseboundaryarrays. Fixeddump.lua07:52:31tofor directions0..5Map.GetAdjacentPlot.
Map2+allfutureusefullnativeedges. normalize_neighbors.py normalizedfirstmap's
148edge-neighborlistsfromnativeidentical3404-coordinategridmap2. Originaldump
retainedmap-original-neighbor-enumeration.json;allnon-neighborfieldsunchanged,
normalizationmetadata+beforeSHAstored. observer-revision.json before/afterhash
explicitlypermitsonlythissourcechange. verifychecksnormalizationandsourcehash.
Currentrunner63664stillactive; no extraTunerqueries. Map3loadingnext.

07:54 userrequestednumbers-only,nofurthernative mapsavesneeded. Stopped
validatedcontrollerPID18380whilemap3loadedturn1(noevents/turnslost).
Updatedrun.pydefaultsave_mapsfalse,optional--save-maps, --resume-current/
--resume-group/--resume-map; restartedcurrentvanilla-map3using61715at07:55:31.
NoTunerconcurrentclients. Old63664killed,noinjectedSaveGameforfuturemaps.
Originalmaps1/2savesretained;newmapsnativefulltileJSON+numbers/logsonly.
controller-revision.jsonbefore/afterhashaccountsforuser-requestedchange;
initialsource-hashes.jsonpreservedandcurrentlockedversioninsource-hashes-current.
verifyacceptsno-savecompleteflags, stillchecksalltiledata/edgegraph/SQL/hash.
READMEupdated. SourceMap3Nativeworldneveradvanced;newobserverreadsfullstate.

07:59 vanillaAbundantgroupDONE5maps allturn1,17020tiles,40Quarter-maprows,
partialverifyPASSunchangedCSC/TAR/lockedsources,zeroSQLerrors. Bgeography
map1..5=22,40,13,41,42; Tailors=0,2,4,3,0. All8inquarter-opportunities.csv.
NowTARenabledAbundantgroupnext;5TrulyAbundant45afterthat. Nativecontroller
61715active. Numbers-onlyfuturemaps, originalnative2savesretained.
08:00:34TAR-Abundantmap1done. Pairedfirstmapterrain/features/landwaterALL3404identical, resourcesdifferent675tiles. NativeTARdatabasefingerprintIronharvestfalsevanilla,trueTAR. Additionalverifycheckadded(noobservationcodechanges). TARfirstmapB24,T0,Apoth2,Stone15,Carp65,Black25,Gold2,Brew14. Sixmaps partialanalyzed.
08:07:10mapscompletepartialverifyPASS34040tiles80rows. TAR-AbundantB=24,36,19,37,50 T=0,1,3,2,0. VanillaB22,40,13,41,42 T0,2,4,3,0. All5TARpairedterrain+featuresidentical3404each. TrulyAbundantgroup45started08:06:57;61715active. No manualmapsavesafterfirst2.

08:13 maps14/15complete, lasttar-truly-abundantmap5generating08:12:58,
runner61715exclusiveTunerowner. Sourcegroup120rowsafterfinalanalyseneeded.
At12mappartialverifyPASS40848tiles96rows. Trulyfirst2B83/166,T0/6.
Importantfinding: vanilla/TAR-Abundantmap1&5haveZEROTailorsSPECsource
resources(entiremapsnodyes/silk/silver), notmerelybadadjacency. Trulymap1
alsoSPEC0. Userinformed; checklastmap5future. All8defsreport. Needfinal
analyze+verify(noallowpartial),all15r.restoremenu,publishdurablelocalreport
+CSVlink,includeall120countsfinaltable,sourceavailabilityinsight,optional
GoldsmithsPearlsvariation. Userwantsnumbers,no furthernativegame saves.

FINAL OUTCOME08:14:34: New15mapsurveyCOMPLETE. r.restoreverifiedoriginalmods/
auto-startatmainmenu; runner61715exit0. All15turn1,noadvances,51060tiles,
120Quarter-maprows. FullverifyPASSunchanged111CSCfiles+TAR+lockedinputs,
zeroGameplaySQLerrors. All5pairedterrain/featuremapsidentical3404x3; only
resourceplacementchanged. Onecanonicalnativecoordinategraphall15exports.
Durable reportproject/docs/research/mods/csc-map-material-opportunities-20261016.md
indexedresearchREADME; rawDesktop/Codex/csc-map-material-opportunities-20261016.
Reportsourcehelperpublish_report.py; rawcompact-table.mdreadyforfinal120nums.
No furthermapsavesafterfirst2 peruserinstruction. Numbers+tileJSONretained.
MissingSPECclassespersistALL3settings:Tailorsmaps1/5(noDyes/Silk/Silver),
Stonemasonsmap5(noGypsum/Marble),Goldsmithsmap4(noDiamonds/Jade;Pearls
sensitivityTrulygives3). IndividualGoldpageexcludesPearls;altcountsreport.
Maincounts tablefinal:
B22,40,13,41,42 |24,36,19,37,50 |83,166,69,115,153
T0,2,4,3,0 |0,1,3,2,0 |0,6,10,37,0
A1,6,1,11,5 |2,8,1,12,1 |14,38,15,23,17
S13,29,15,38,0 |15,13,22,35,0 |32,61,42,65,0
C69,85,122,102,68 |65,67,111,106,63 |133,94,218,220,151
BL20,32,28,34,29 |25,29,29,46,17 |58,47,51,93,44
G0,2,1,0,0 |2,1,5,0,3 |3,1,8,0,13
BR27,21,11,25,22 |14,9,17,26,19 |109,74,70,71,88
Primarygeographybeforeownership/research/clearability;commonclearablefilter
andTARharvestawarevariantsCSV/report. HillsbaseStone/Black,Forest/JungleCarp.
Savedfeedback_csc_ai_map_setup.md Online/Abundantfuturepref,nativeSavesnotneeded
map-only surveys. Old200reportfollowupnote3saved400,4/5stop200,game3eventgap.
NoAI/gameplaytuningchanged. Needfinaluserdeliverytable+report/CSVlinks.

## 16 October 2026: resource distribution intervention research

User asked whether CSC could intervene in map generation and remain compatible with map scripts. Research only; no implementation selected or authorized yet.

- Native GS Maps/Utility/ResourceGenerator.lua defaults LuxuriesPerRegion to 4; __GetLuxuryResources selects land luxury types by continent from a shuffled pool. TAR (Workshop 901009089) retains that structure, so higher density does not ensure all CSC classes exist.
- TAR imports its own Utility/ResourceGenerator.lua. A CSC replacement of the same common generator would introduce a direct replacement conflict; avoid as the broad compatibility approach.
- Verified additive gameplay-initialization precedent in Sukritact's Oceans (Workshop 2542898147): modinfo AddGameplayScripts loads Lua/Suk_OceansMapGen.lua, which includes uniquely named Suk_ResourceGenerator.lua. It uses a saved Game property guard and ResourceBuilder.CanHaveResource/SetResourceType to redistribute resources. This demonstrates resource editing without replacing each map script; CSC timing and coexistence still need live tests.
- Recommended proposal: optional, bounded one-time audit/repair after generation; score legal empty resource plots by new usable base+specialty Quarter opportunities, recognize hill/forest sources, keep Quarter sites clear, count spatially independent clusters, respect existing resource placement and regional specialization. Coverage repair and local pairing are separate targets.
- Compatibility caveat: gameplay pass follows native starting-position assignment (GS Continents generates resources then starts), so it cannot improve original start scoring; protect initial starts and test balance. Other mods with later resource edits need ordering tests, authored/TSL maps need opt-out. No universal map-mod compatibility claimed.
- Next useful experiment: simulate candidate repair budgets against the retained 15 native map snapshots before changing live map generation. No extra native saves needed.

### Follow-up: map-generation flow and compatibility evidence

Read stock GS Continents.GenerateMap plus AssignStartingPlots. World sequence: base geography/continents -> rivers/lakes/features/cliffs/wonders/lowlands -> ResourceGenerator.Create -> AssignStartingPlots.Create -> goodies. Start placement itself can add/remove resources, including Balanced/Legendary normalization; a pass inside the resource generator is not necessarily the final resource layout.

Compared TAR ResourceGenerator against installed GS stock using difflib: same interface/overall flow, new setting values 25/45, adjusted allocation/spacing formulas; land luxury selection remains same default-four-per-continent approach. TAR SQL adds terrain/feature eligibility, sea variety/frequency, harvesting. Workshop author lists PerfectWorld6, YnAMP, Detailed Worlds, Got Lakes and Fantastical. Clarify replacement conflicts mean competing for the same shared generator, not automatic incompatibility with all custom map scripts.

Checked primary YnAMP master TerraMap.lua (GitHub Gedemon/Civ6-YnAMP): lines 646-654 call shared ResourceGenerator.Create unless importing resources/no-resources. Confirms compatibility can depend on resource-generation options. Got Lakes Workshop 916614621 author explicitly lists TAR and Sukritact's Oceans compatible, and documents selective override interactions for other mods.

Oceans: AddGameplayScripts -> Suk_OceansMapGen -> kelp then uniquely named resource script. Saved Game property guards; uses active DB sea-resource types, derived coastal continent regions, heat maps of existing resources; removes water luxuries, keeps bonus resources, picks up to two luxury types per derived region then replaces luxuries on eligible empty tiles. Reads standard and TAR 25/45 abundance values explicitly. Later pass supersedes some earlier sea-luxury choices; no common ResourceGenerator.lua replacement. Workshop description cautions YnAMP compatibility varies. Research is source inspection, not a new live compatibility test.

## New paired Online baseline — 16 October 2026, 21:02 local

User authorized ten full250 games: use the five latest vanilla Standard maps,
plus five with TAR enabled but still vanilla Standard resources. Online/Prince,
Continents.lua Small74x46,6majors9CS, samefive seeds/leaderrosters from nativev3
implemented-Quarter study, CSCv3 assistance on, animals1cleanup1,M&Coff,standardAI.
Captured maps were numbers-only: regenerate initial vanilla maps and require
exact equality of13tilefields includingresourcequantities/ownership/neighbours.
No AI/gameplay tuning. Baseline observer v2 fixes sparseboundary neighbourloops.
Source project/tools/ai_baseline/{paired_standard.py,paired_observer.lua,
paired_analysis.py}; inheritedrun.py/Surveyconfigurationtransport. Initial/final
saves,25turncheckpoints,fullread-onlyeventhistory,candidatedecisions,pinnedsources.
OutputDesktop/Codex/csc-ai-paired-standard-20261016. ACTIVE unifiedexec11488,
exclusiveTunerowner; DO NOT connect anotherclient while it runs. Main CivPID7240
alreadybackgrounded; attemptedhiddenlaunch21872exited(singleinstance),original
untouched. Game1generating21:01:44. Inspectprogress.log/batch.json before acting.
10gamesnotyetcompleted. Needfinish,verifyall110snapshots,saves,unchangedsources,
restoredprefs;analyzebygroup/individualmaps andpublishdurablereport. Runner closes
an alreadyopendisasterpopup via nativegameUIcontext OnClose beforeautoplay,
neverOSwindowcontrols. OriginalcomputeruseCivdenialstillrespected.
21:06:35: Active controller now unifiedsession53670 (11488stoppedatturn1before
autoplayduetransientNoresponsivetunerstates). Added inventory-readretryonly;
controller-revisions.json recordold/newhash/reason, updatedpinhash. Observer and
gameplayunchanged; resumedturn1withfullhistory. Game1turn25,8cities83events,
zeroobservererrors;all13initialmapfieldsexactmatch. Originalprefsnotyetrestored.
21:22: Continuous controller unifiedsession53761 now ACTIVE/exclusiveTunerowner.
Game1firsttrialstalled50: nativeDiplomacyActionViewvisible, localplayer-1,
autoplaytrue, pausedflagsfalse, sessionFindOpen(0,3)=3. PureUI.Closehidviewand
releasedUIeventbutpendingsessionremainedfrozen; NOAddResponse/CloseSessionused.
ExitToMainMenu succeeded. Entire game-01archivedtoexcluded-checkpoint-trial-game-01;
no completedgames yet. Restartsameinitialmapexactly; observerv3 nowB.capture freezes
25turnsnapshotsinmemoryduringcontinuous1->250autoplay. All exportsatendpoint,
nohumancontrolreturnsatintermediatecheckpoints. This removesdiplomaticintervention.
Controller/observerrevisionchainrecordedincontroller-revisions.json; original
controller/TARhashesupdatedonlyexplicitrevisedfiles. Observerv3prefixcopiesare
shallowarrays ofimmutableeventobjects; freshcity/plot/optiontableseachcheckpoint.
Finalvalidationchecksactualeventprefixandfrozenhistory. Needfinish10,restoreprefs.
21:39:34: Valid continuous game1turn229, stillnativeautoplay. Activecontroller
nowunifiedsession74215; DO NOT connectotherTunerclient. Previous53761stopped
21:37:34 dueblank1secpollresponseunderheavyAIturn~215; gamecontinueduninterrupted.
Addedread-onlycmdretry(poll/snapshot/dump/ready/actual),pre-dispatchonlyretryfor
mutations. --resume-current --resume-running reconnectswithoutresettingnative
remainingturncount. Observerv3unchanged; revisionsrecordedexplicitcontrollerhash.
Resumeacceptsmidintervalcurrentifv3observeralive; retainedallfrozen25turncheckpoints.
Needfinishall10,verify110snapshots,eventprefixes,saves,installed115sources,prefs.
Durablerunningmethoddocproject/docs/research/mods/csc-ai-paired-standard-20261016.md.
21:47: First validgame1 COMPLETE250,48cities1137events,all11snapshots/saves/
115installedfiles/errorchecksPASSED. Analysispartial1gamegenerated. Stopped
validatedcontrollerPID8108afterarchive+verificationasgame2wasloading, notCiv.
AddeddriverPlayerDefeat/pollalive-returnguardtocounterhistoricaldead-returnoverrun;
observerv3remainsread-onlyandunchanged. Explicitcontrollerrevisionchainupdated.
--resume-map --first2continuesexistinguntouchedturn1world2withoutregeneration.
ACTIVErunnerunifiedsession41003exclusiveTunerowner. Game2resumed21:47:06.
NootherTunerclients. Needremaining9games thenall110verify,prefsrestoration/report.
22:12:39: Games1and2 COMPLETE/exact250,22snapshotsvalidated,saves,fullprefixes,
zeroobserver/GameplaySQLerrors,115installedfilesunchanged. Game2final58cities,
1088events. Game3generating830304. Activecontroller41003exclusiveTunerowner.
Remaininggames3..10; preferencesNOTyetrestored. Partialanalysisrefreshed2games.
22:40:21: Games1–3 COMPLETE250/validated33snapshots,saves,eventprefixes,
zeroobserver/GameplaySQLerrors,115installedfilesunchanged. Game3final64cities,
1132events. Game4generating830405. Controller41003activeexclusiveTunerowner.
Analysisrefreshed3games. Remaining4..10; originalpreferencesstillNOTrestored.
23:05:26: Games1–4 COMPLETE250,44snapshotsverified,saves/eventprefixes,zero
observer/GameplaySQLerrors,115installedfilesunchanged. Game4final64cities1128events.
Game5(vanillalast)generating830506. Controller41003activeexclusiveTunerowner.
Partialanalysisrefreshed4games. After5runTARStandard6..10 pairedsame5seeds.
OriginalpreferencesNOTrestoreduntilfinalbatchend. NoAIweights/worldwriteschanged.
23:33:21: VANILLA GROUP COMPLETE:games1–5exact250,55snapshotsvalidated,
initial/finalsaves,eventprefixes,zeroobserver/GameplaySQLerrors,115installedfiles
unchanged. All5initialmaps13fieldsexactmatchoriginalStandardcaptures. Game5final
62cities1310events. TARgroupgame6pairedmap1generating830102,res2Standard,Online.
Controller41003active/exclusiveTunerowner. Needremaining6..10 thenfinalverification,
preferencesrestoration+durablereport. Partialanalysisrefreshed5games. Added
base_placement_choices.csv comparingBaseavailable/chosen/Base+Sales (Basealone
supportsS2/3); paired_analysis.pyindependentderivedanalysis,observerunchanged.
17Oct00:03: Games1–6 COMPLETE250/validated66snapshots,saves,prefixes,zeroobserver/
GameplaySQLerrors,115installedfilesunchanged. Game6TARfirst58cities1058events.
41003stopped23:57SaveNotConfirmed afterall11exports: NaturalDisasterPopupvisible
atreturn250human0blockednativeSerializationreason3. NativeOnCloseclearedpopup;
onecapital(player0city65536)autogrew10->11andCityYieldsupdatedsame250. ALLplots,
players/research,districts/buildings,serviceproperties,events/errorsidentical.
Keepstandardizedfirst-major-activationturn250original; endpoint-after-playback.json,
save-state-turn-250.json,andcomparison/recoveryJSONretainsettledsavephase.
Manualrecovery69104savedat00:02:51,returnedmenu,verify6passed. NoAIaction/newturn.
Newsave_checkpointclearsonlyvisibleweather/diplopureUIbeforefinalsaveandcaptures
settledcensuswithoutreplacingfrozenbenchmark. Explicitcontrollerhashrevisionlogged;
observerv3unchanged. New ACTIVEcontroller unifiedsession8180, --first7,
exclusiveTunerowner. Remaining7..10.
Needall110snapshots/finalnativeprefsrestored/report. Source docs statusrunning.
17Oct00:35:15: Games1–7 COMPLETE250/validated77snapshots,initial/finalsaves,
fullprefixes,zeroobserver/GameplaySQLerrors,115installedfilesunchanged. Game7TAR
pair2final61cities1285events; patchedendpointsaveprepworked. Game8TARpair3
nowgenerating830304.Standardresources2/Online/Prince/CSC+TAR/stockAI.
ACTIVEcontrollerunifiedsession8180exclusiveTunerowner. Nootherconsoleclients.
Remaining8..10 thenfull110verify,finalanalysis,durableReport/index,memoryupdate,
freshnativeoriginalmodflags/autostartrestorationverification. PreferencesNOTyet
restored. Primarymetricsusefrozenfirst-major-activation snapshots consistently;
settledsave-stateJSONs(6onward)separateautomaticturn250citygrowthafterplayback.
17Oct01:02:34: Games1–8 COMPLETE250/validated88snapshots,saves,prefixes,zero
observer/GameplaySQLerrors,115installedfilesunchanged. Game8TARpair3final68cities,
1051events. Game9TARpair4generating830405. ACTIVEcontroller8180exclusiveTuner.
Remaining9and10only thenfullverify110,restorenativepreferences/autostart,fresh
restorationcheck,finalstats/report/index/memory. Allbenchmarkobserverv3 unchanged.
NoTunerconcurrentclients. Derivedanalysisrefreshed8. OriginalprefsNOTyetrestored.
17Oct01:27:02: Games1–9 COMPLETE250/validated99snapshots,saves/fullprefixes,
zeroobserver/GameplaySQLerrors,115installedfilesunchanged. Game9TARpair4final60cities
1097events. FINALGAME10TARpair5generating830506resources2OnlinePrince. Active8180
exclusiveTunerowner. Needonly10finishthenfull110verify,freshnativeprefs/autostart
restorationconfirmation,finalanalysis/durableResearchReport/index,memoryupdate.
NoAIweightschanged.Observerv3sameallvalidgames;driverrevisionsrecordedexplicitly.
DoNOTstopatpartial9orclaimcompleteuntil10andrestorationdone. Partialanalysis9.

## FINAL COMPLETE — 17 October 2026, 01:54–02:03 local

ALL10exactturn250, fivevanillaStandard +fiveTAR-enabledStandard(noTrulypreset),
OnlinePrince,CSC productionv3B/T/stockAI,fivepairedseeds/leaderrosters. All5vanilla
initialworlds13fieldsx3404tilesexactoriginalcaptures. Game10final55cities1222events.
Runner8180EXITED0. Noactivecontroller/noTunerowner. Civ atbackgroundMAINMENU.
Independentverify-onlyPASS110snapshots,fullmonotonicprefixes,20initial/finalsave
SHAchecks,zeroobserver/GameplaySQLerrors,115installedfilesunchanged. Observerv3
sameallvalidgames. Controllertransport/return/save revisions explicitlylogged;
excludedfirst50turncontrollertrialnotinanyresults. Game6endpointweatherblocked
save;NativeOnClosereleasedit,automaticcapital10->11same250onlypop/yields,
plots/quarter/district/research/service/eventsunchanged. Frozenfirstactivation
censuspreservedconsistentall10,settledsavecensus6onward retainedseparately.
FreshNativeMainMenucheck1551PASS141uniqueoriginalmodflags,142nativeentries
(oneIDduplicate),auto-startfalse. Firststrictcountrecheckfailedonlybecauseit
countedentriesinsteaduniqueIDs;ALLflagsalwaysmatched,noactualrestoreproblem.
preferences-restored.json fresh_native_checktrue. Final-verification.json complete.

OutputDesktop/Codex/csc-ai-paired-standard-20261016, analysis.json/CSV/final-report.md.
Durablecurrentreportproject/docs/research/mods/csc-ai-paired-standard-20261016.md,
indexedresearchREADME; original15OctAIStandard-speedstudy nowHistorical.
Source paired_standard.py/paired_observer.lua/paired_analysis.py/publish_paired.py
+README; noAIweights/gameplayedits thisrun. DoNOTrestartbatchoroldcontrollers.

Vanilla5:296majorcityobservations,29survivors,259completeBakers132Tailors.
BakersBase56(includesBoth1);TailorsBase8(includesBoth1). TAR5:302cities28survivors,
252Bakers133Tailors;Base52(includesBoth4)B,Base11Both0T. Total776completeQ/598cities,
Both6. WhenownednativeplotlegalBasealternativeobserved: B80/144vanilla73/143TAR
=153/28753%;T11/28vanilla13/34TAR=24/6239%. Base+SalesavailablechosenB60/125+59/138,
T1/10+0/9. Baseimproved18/61+14/54B=32/11528%;T2/8+2/11=4/1921%. Specialtymuchhigher.
LaterSalesadjwhenavailableB47/151+36/129;T47/125+42/111. 61distinctoriginaladjacent
materialplotslaterreplacedbydistricts(same-owner-survivingQrelationships).
Stage2/3/4buildingsvanillaB239/105/52,T114/68/40;TARB237/96/31,T102/55/29.
NativeendpointSourceFlags:vanillaGrowth6Housing1,TARGrowth8Housing1;noBakerTourism
orTailorSourcesat250. Earlyactivationpossible:retainall25turnhistories. Tailor
NavalTraditiongateavailableonly11/132vanilla25/133TARQcases;material/venuegates
alsoincomplete. DiagnosticserviceCSVisnotfullnativeeligibilityengine(unique
venue/replacementgatesmaynotallbemodeled);nativepropertiesauthoritative.
Quarterswithoutmaterialscanprofitthroughsales;candidatecountsarenotproofbest
planorAIinternalweights. Base-onlysupportsS2/3,BothrarityforS4intentional.

FINALPENDINGUSERRESPONSE: taskactuallycomplete. Presentconcisesummaryandreport
link, optionallygroupQtotalsandBasechoice53%/39%. Noapprovalneeded. NoPRrequested.
