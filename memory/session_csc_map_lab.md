# CSC map viewer and offline resource replay

16 October 2026. User requested a viewer of all 15 native maps, followed by a
way to iterate map/mod scripts outside Civ or without disruptive foreground
restarts. Preserve the map-driven asymmetry preferences in
`feedback_csc_ai_map_setup.md`.

## Delivered implementation

- Follow-up packaging fix: user opened `project/tools/map_lab/viewer.html`, which
  had been the unbuilt template and therefore displayed no styles or map data.
  Renamed the layout to `viewer.template.html`; `viewer.html` is now a local
  redirect to the generated `project/snapshots/map-lab/index.html`. Builder and
  README updated. The same browser tab can be refreshed to reach the viewer.

- Source: `project/tools/map_lab/`; README is the durable tool/fidelity reference.
- Generated output: `project/snapshots/map-lab/` (ignored by Git; writable workspace
  used because Desktop Codex was not writable under the active sandbox).
- `index.html`: self-contained offline browser viewer of exactly the 15 native
  maps. All 8 Quarters; Base/Specialty/opportunity/resource/feature layers;
  geographic/common-clearing/loaded-harvest filters; distinct supporting tiles;
  zoom/pan/search/pinned support inspection; imports packaged map JSON.
- `experiments.html`: separate viewer with the native maps plus 4 labelled
  emulated replays on landscape 2: TAR 4/5/6 luxury types, and 6 plus Oceans.
- `build.py`, `demo.py` rebuild these. Native tile-data hashes unchanged for all15.
- Local HTTP server was started on 127.0.0.1:8766 (exec session87798), then stopped
  after the embedded preview was blocked; native
  viewer also opens directly as a file, no server required. Codex browser opening
  was queued, not confirmed displayed. Later CUA inspection was explicitly
  blocked by browser URL policy; no further browser actions or alternate-surface
  workarounds were attempted after that rejection. Browser tests had already
  passed using local file URLs before the rejection. Deliver the standalone files.

## Offline execution scope

`offline.py` reads installed TAR/stock ResourceGenerator and Oceans' actual Lua
includes, executes them using existing Lupa Lua5.1 dependency at
`C:/Users/Shadow/Desktop/Codex/csc-adjacencies/test-deps`, and an explicit native
DebugGameplay.sqlite rule profile cloned in memory. No game or Workshop files are
modified; no Civ sessions launched for this work. Demo freezes a local SQLite
profile in its ignored generated output.

Real source execution is NOT engine parity. Native map APIs are emulated. The old
15 exports lack named continent IDs, river/lake flags: explicit --approximate
required, connected landmasses substitute for continents, rivers assumed absent,
lakes inferred. Native eligibility is only partially modelled; RNG is Python
MT19937, not native Civ seed reproduction. Start normalization is absent. Full
terrain generation / YnAMP pipeline is unsupported; Fractal, AreaBuilder and
StartPositioner fail explicitly, never return invented native results.

TAR runs roughly 1second and TAR+Oceans roughly1.5seconds on one landscape in this
environment. Repeated runs deterministic. Oceans emits actual kelp and its custom
resources after fixing g_FEATURE_NONE in adapter. Lua5.1 needed for source's
implicit `arg` varargs compatibility; Lua5.4 did not run unchanged Select helper.

The supplied DB profile carries all SQL from that native capture. Selecting stock
Lua does NOT remove TAR SQL; do not call that a clean vanilla baseline. Installed
Oceans feature/resource SQL is added if absent, not other Oceans gameplay logic.

## Validation

- Browser Playwright + installed Chrome, headless: all120 Quarter/map rows x3
  filters =360matches;120 distinct-source matches; source counts; toggles,
  selection/zoom/search;390px no overflow;4 experiment imports;zero browser errors.
- `test_offline.py`: actual TAR/Oceans source integration, repeatability, terrain
  and native-neighbour preservation, custom output, source hashes/input unchanged,
  explicit approximation requirement and unsupported-engine failure. No live
  native parity test.
- Screenshots and validation JSON in generated output.
- `map_survey/dump.lua` additively updated for future captures: continent/river/
  lake/wrap/map-size fields. Native exporter change has NOT been live tested.

## Outstanding user objective

### 16 October follow-up feasibility research

User explicitly asks what full TAR/YnAMP/Oceans generation outside Civ would take.
Inspected installed stock utility dependencies and primary YnAMP source. Key
scope distinction: YnAMP GiantEarth.lua GetMap() stores actual terrain, features,
named continent IDs, river-edge flow, resources/counts and cliffs in a Lua table;
GenerateMap delegates to GenerateImportedMap in its override. Supporting authored
YnAMP import paths can avoid a native fractal reimplementation and a prior live
capture, but that does not generate new random landforms or reproduce all starts.
Primary source:
https://raw.githubusercontent.com/Gedemon/Civ6-YnAMP/master/Maps/GiantEarth/GiantEarth.lua

YnAMP's procedural TerraMap.lua directly calls Fractal.Create/CreateRifts and
calls shared ResourceGenerator followed by AssignStartingPlots. Installed stock
mountain utility additionally uses fractal BuildRidges/GetHeight; feature generator
uses native GenerateFloodplains/AddIce, continent stamping/chokepoint analysis is
native, start helper uses native StartPositioner partitioning/fertility. A generic
noise implementation would produce new worlds but would not establish fidelity.
Primary source:
https://raw.githubusercontent.com/Gedemon/Civ6-YnAMP/master/Maps/TerraMap/TerraMap.lua

Proper standalone runtime needs modinfo/action criteria/load-order/VFS resolution,
configuration and matching gameplay database, full world state/derived properties,
validated placement predicates, phase ordering including gameplay init, and RNG
contract. Exact same-seed parity is a separate harder objective from original Lua
running over behaviorally compatible APIs. Do not equate successful script runs
or no crashes with native parity. No supported standalone native host identified;
inspected installed SDK tools and binary string indicators do not prove one cannot
exist. Loading GameCore alone is not an established solution.

Proposed phased route: validated world/eligibility API + mod loader; authored YnAMP
imports + TAR/Oceans; procedural generator port; starting-position reproduction
if required. Preserve actual stack's incompatibilities too: Oceans author warns
YnAMP compatibility varies. These are proposals; no full generator implemented
and no further native games launched during this research.

Direction changed after the feasibility discussion: Henno proposed using the full
game backgrounded or while the machine is not in use. Standalone engine-porting
work is parked, not a pending implementation commitment. Keep the completed
viewer and treat native generation as authoritative. Next operational check is
whether minimized native generation progresses without focus stealing; this has
not been verified. Otherwise arrange batches while Henno is away. No schedule,
idle-monitoring automation, or foreground batch has been agreed or started.

## Completed native 4/5/6 comparison — 16 October

- Supersedes the background-untested and exporter-untested notes above. Henno
  confirmed Civ was backgrounded while he worked. FireTuner generated all fifteen
  requested turn-1 versions on the original five seeds/rosters, CSC plus vanilla
  Abundant, Online, Small-size Continents script. No native saves or turns needed.
- `project/tools/map_survey/luxury_study.py` creates a private map copy and passes
  only LuxuriesPerRegion as the behavioural intervention. Absolute map-script
  paths work; no test mod installation, game/Workshop edit or CSC change needed.
- Five four-type controls match all 3,404 terrain/feature/resource tiles of each
  original vanilla map. All fifteen maps verify (51,060 plots); terrain and named
  continent IDs match across paired variants, zero gameplay SQL errors, 111
  installed CSC source files unchanged. `verify_study_preferences.py` freshly
  verified all 141 community-mod flags and original auto-start=false; deselected
  the private script in favour of stock Continents.lua. Civ remains at the menu.
- Raw evidence: `project/snapshots/map-lab/luxury-study`; viewer has original
  fifteen plus fifteen native comparison entries. Continent selection/table,
  Base versus both-class supply, coverage and connected candidate clusters added.
  Source-level viewer geometry tests pass 4,680 comparisons over 30 entries.
- All-eight Base coverage across 15 named continents: 4 types 5/15, 5 types 7/15,
  6 types 12/15. Mean covered industries: Base 7.27/7.47/7.80, both 4.73/5.07/5.40.
  Mean land luxury copies/continent 22.8/22.6/22.0; diversity 4/5/6. Six broadens
  regional Base coverage; Goldsmiths have zero both-class sites across all five
  six-type maps. Do not automatically repair Stage 4 scarcity.
- Durable native report: `project/docs/research/mods/csc-native-luxury-diversity-20261016.md`.
- Henno requested offline calibration during the batch. Eleven cases have phase
  captures; later ones add eligibility/placement/adjacency/sort traces. The old
  emulator shuffle was wrong; now loads installed MapUtilities helper. Main
  calibration agrees on 44,002 sampled eligibility decisions and 40,002 adjacency
  counts. 246/255 placement-score sort orders differ; recorded RNG alone does
  not establish parity. Native-sort replay extends a tested placement prefix,
  then still diverges. Full new-terrain generation/RNG remain unsupported.
- A diagnostic table.sort wrapper caused startup errors because Civ's standard
  library table is read-only. Those attempts counted no maps. Henno closed the
  popup; replacement observes Lua-owned generator methods. `test_capture.py`
  verifies read-only-library compatibility, unchanged RNG state and all tiles.
  `LuxurySurvey.cmd` now retries safe transient console reload failures, and
  `--resume-current` recovered the already-loaded six-type map without regenerating.
- Calibrations and frozen vanilla-CSC DB: `project/snapshots/map-lab/native-calibration`.
  Terrain target profiles count the five landscapes once; metadata is still
  missing full river flow/cliffs/lowlands/start database. Durable calibration doc:
  `project/docs/research/mods/csc-offline-generation-calibration-20261016.md`.
- Finished user package copied and read-back verified at
  `C:/Users/Shadow/Desktop/Codex/csc-luxury-diversity-20261016/`: standalone
  `viewer.html`, `results.md`, `offline-calibration.md`, native-study evidence and
  offline calibration fixtures/profile. Existing project viewer redirect also
  reaches the updated 30-entry standalone build.

## Continental helper preview — 16 October 2026

- Henno approved trying the proposed sparse helper on the five four-type maps
  and adding exact placements and coverage comparison to the viewer before Civ
  tests. No native batch or production helper has been run/installed.
- `project/tools/map_lab/assist.py`: immutable native inputs, calibrated SQL
  habitat interpretation, seeded soft continental resource palettes, one-shot
  missing-industry selection, site-first Base/Spec/pair repair, per-continent/map
  caps 4/10, shared gains, last Base/both opportunity and reserved-center
  protection. Fixed seed 20261016 was not selected by outcome.
- Added 16 deposits across maps (5,2,1,3,5). Both-class continental coverage:
  Bakers 12->12, Tailors 3->11, Apothecaries 9->9, Stonemasons 4->8,
  Carpenters 15->15, Blacksmiths 15->15, Goldsmiths 2->6, Brewers 11->11.
  All six missing Apothecaries cases failed the one-shot selection draw.
  Targets remain approximate hypotheses, not five-map quotas.
- Viewer now has 35 entries, default helper group, original/proposed toggle,
  orange numbered additions, green gained sites/red lost candidate tiles,
  continental palettes, exact deposit/center navigation and all-industry
  coverage. Ordinary clearing is the default for the helper.
- Four existing both-class candidate tiles become blocked (Carpenters Map1;
  Tailors/Carpenters/Blacksmiths Map4); none was its continent's last. All
  accepted proposals preserve original resources, terrain and features.
- `test_assist.py`: 108 checks, all16 habitat checks against Python and Lua
  adapter, repeatability, coverage, pairs/budgets. Actual viewer geometry passes
  6120 checks; full DOM fixture passes 1920 before/after controls/counts plus
  deposit navigation. No new native or browser visual validation claimed.
- Durable report: `project/docs/research/mods/csc-continental-resource-helper-preview-20261016.md`.
  Generated results: `project/snapshots/map-lab/helper-preview/` and the main
  map-lab bundle. Main viewer retains all30 prior native entries.

## Native helper comparison — 16 October 2026

- Henno authorized native tests on the same five seeds, backgrounded, with
  original/preview/Civ comparison in the viewer. Civ was not running; launched
  with Start-Process -WindowStyle Hidden (no window manipulation). Henno
  explicitly confirmed it stayed backgrounded. All game operations used tuner.
- `native_assist.py` regenerates stock four-type Abundant controls, then runs
  the **shared Python** helper with live native eligibility tables. Accepted
  additions go through actual CanHaveResource rechecks, SetResourceType and
  exact native readback. This is a post-initialization turn1 API test, **not**
  an installed Lua helper/startup-order test. That boundary was stated before
  running and is visible in the viewer/report.
- All five fresh controls exactly match original 3404-tile geometry/resources,
  continents, rivers/lakes, ownership/districts/neighbours. Native material
  definitions match. All16 additions accepted; original resources/terrain/
  features and last Base/both coverage preserved; no turns advanced.
- Coverage matches previews in every Quarter: 12,11,9,8,15,15,6,11 /15.
  Map1 four deposits moved; Map4/5 one each moved (12 differing resource tiles
  total); Maps2/3 identical to preview. Resource types unchanged. All16 original
  preview locations are also legal natively; candidate filtering changes which
  random location is selected.
- Live CanHaveResource:126588 checks,533 offline disagreements, all native
  rejections. Added top-level `starting_plots` export during Map3. Maps3–5:
  all318 mismatches are on native reserved starting plots (15 each), zero
  unexplained elsewhere. Maps1–2:215 mismatches on15 tiles each, same pattern,
  but no direct flag capture; describe as consistent/inferred, not proven.
  Improvement diagnostics on maps2–5 exclude goody huts at additions and show
  they do not explain the eligibility discrepancies.
- Outputs: `C:/Users/Shadow/Desktop/Codex/csc-helper-native-20261016/`.
  `verify_native_assist.py` passes5maps17020native tiles, native decision replay,
  setters, preservation and coverage. All111 installedCSC source files match;
  fresh native preferences verify141modflags +auto_startfalse, game at menu.
- Viewer40entries defaultCivhelper, original/offline/native selector with same
  viewport, all-industry three-way coverage and per-continent/site comparisons.
  Actual geometry7560checks; fullDOM fixture4800checks passed. No browser visual
  review claimed. Durable report:
  `project/docs/research/mods/csc-continental-helper-native-20261016.md`.

## Installed automatic Lua helper — 16 October 2026

- Henno explicitly authorized actual CSC Lua integration and five automatic
  background native games on the same seeds. Completed and left installed.
- Source: `Civ Supply Chains/Lua_UI/MapGeneration/CSC_MaterialMap{,Core,Definitions}.lua`.
  AddGameplayScripts999901, imports999900. Runs immediately during loading,
  after native starts and before InGameUI; all5native logs showinitialturn1,
  exactly1completion. No ResourceGenerator/map-script replacement.
- Setup option `CSC_MATERIAL_MAP_ASSISTANCE`, Additional industry materials,
  default1; current scope new Abundant3 maps. Saved/late/disabled/nonAbundant
  games skip. Persistent DONE/AUDIT guards; all additions rolled back if a
  native setter/recheck fails. Existing improvements excluded from additions.
- Pure planner owns Park-Miller48271 RNG, hashed versioned mapseed +4warmups;
  no engine RNG API. Probabilities unchanged7/12,6/11,1/6,3/13; exact draws
  differ from Python. Arrays sorted, percontinent soft palettes, max4/continent
  and10/map, singles preferred then pairs, last Base/both/centers protected.
- Bakers/Tailors runtime class tags; other6design rules +nonofficial loaded
  tag extras. Official type list avoids inheriting incomplete vanilla stub
  mappings. Optional mappings +Pearls design boundary tested offline.
- Source action JSON edited +civ6proj patched via tool; Content entries added.
  Focused deployment copied3Lua+2settings and generated manifest with Firaxis
  Civ6.Tasks.GenerateModInfo SDK task (DLL under ModBuddy/Extensions/Application).
  Existing actions/dependencies/references/art/otherinstalledsource preserved.
  No Clean/fullbuild/assetcook; project remains wired for normal ModBuddybuild.
- Civ restarted gracefully from verifiedmenu (UserConfirmedClose), then hidden
  launch. Existing background method/user authorization retained; no mouse/
  keyboard/foreground manipulation. Controller only setups/exports, no planner
  or resource setters. `automatic_assist.py` reads startup debug/audit, checks
  exact original controls and actualLua offline replay usingnativeeligibility.
- All5games complete,17020tiles,122298nativeeligibilityqueries,0turnsadvanced.
  Additions4,5,3,3,3=18; allsingle-deposit repairs in native sample.
  Bothcoverage original→Lua: Bakers12→13,Tailors3→9,Apothecaries9→10,
  Stonemasons4→11,Carpenters15→15,Blacksmiths15→15,Goldsmiths2→5,Brewers11→11.
  Exact offline Lua addition/palette/count replay onall5.
- ActualLua entrypoint fixture tests:determinism, independent census,
  reentry/scriptreload, saved/disabled/nonAbundant/late guards, rollback,
  forced two-resource path, modded resources/design boundary, zeroengineRNG.
  Native verifier proves1automaticcompletion beforeUI, controller0writes,
  unchangedoriginalresources/terrain/features, lastcoverage; all114installed
  filesmatchdeployment. Fresh141modflags+autoStartfalse restored; diagnostics
  configfalse; Civleftmenu.
- Viewer45entries, default automaticLua, 4-way original/Pythonpreview/PythonAPI/
  Lua selector and coverage. Geometry9000checks, fullDOM8640checks passed.
  No new browser visual review claimed. OriginalPythonresults preserved.
- Evidence/deploymentbackups: `C:/Users/Shadow/Desktop/Codex/csc-helper-lua-20261016/`.
  Durable integration `project/docs/integrations/csc-material-map-assistance.md`;
  results `project/docs/research/mods/csc-continental-helper-lua-20261016.md`.
  Remaining validation:othermap sizes/scripts, actual optionalmodpacks,
  multiplayer, native save/reload. Full offline terrain/YnAMP still unsupported.


## Resource-abundance scaling, 16 October 2026

Henno requested removal of Goldsmith from the option tooltip and assistance at all vanilla/TAR resource levels. Implemented planner v2 with nominal-density / 33 scaling of approximate continental coverage aims and deposit budgets. Stock density 27/30/33; TAR 26/29/32/54/74 (Sparse/Standard/Abundant/Plentiful/Truly Abundant). Random has private native roll, so uses expected Standard density with explicit audit flag; no additional engine RNG. Coverage is continent presence, capped at 100%, not target district-tile counts. Goldsmith baseline remains 5/15; other aims 10/15. Existing abundance is never removed. Missing-industry probabilities recomputed from scaled desired and estimated natural coverage; original Abundant settings preserved. Class shares/distribution differ across TAR and stock, so nominal ratios are not realized deposit guarantees.

TAR detected through exact ModInUse criterion and new conditional ModSupport_TAR_MAP.sql (GlobalParameters baseline 29); no Workshop/map-generator override. Source action JSON regenerated via civ6proj_actions, Content include wired. Focused SDK-generated delta deployment preserves unrelated installed files/actions; backups and proof at Desktop/Codex/csc-helper-scaling-20261016/deploy.

Two new native smoke maps, original seed 830102, backgrounded: vanilla Sparse adds 2 with density27/budgets3+8; TAR Plentiful adds8 with density54/budgets7+16. Both turn1 before UI, exact offline Lua replay, resources and last Base/both-class coverage preserved. 115 installed files unchanged. Original141 mod flags/autostart=false freshly restored, diagnosticsfalse, Civmainmenu. Native proof at Desktop/Codex/csc-helper-scaling-20261016 and compact project/snapshots/map-lab/native-helper-scaling-validation.json. Initial harness count failure was cumulative Lua logs; corrected by scoping latest Generating Continents Map marker and verifying existing captures, no repeated games needed.

Viewer reads optional assistance.abundance profile for targets/help; historical45 entries unchanged (v1 five-seed auto results remain distinct). New native smoke fixtures are not appended as comparison groups. Existing automatic runner now forwards captured profile during offline replay. Tests include all10 resource profiles and original5; exact v1 replay must use original automatic-debug eligibility, not older Python-API native eligibility (timing/empty/improvement candidates differ). test_abundance_native.py --verify-only rechecks native captures without Civ. test_assistance_viewer.cjs --controls-only checks profile-dependent UI quickly; full mode retains complete control coverage.

Durable detail: project/docs/research/mods/csc-material-abundance-scaling-20261016.md; runtime integration doc updated.


## Eight-setup offline study, 16 October 2026

Henno authorized10 offline instances per8 presets then5 native each, but immediately steered to reflection on offline stats first. **Do not start the40 native follow-up until review/authorization continues.** No Civ process/API/mod/config activity in this study.

Completed80 offline layouts in173.5s (plus first-case preflight): five historical luxuries-4 native terrains, two resource seeds per terrain, paired across8 setups. First replicate originalmapseed; second +1000003. This is five independent terrains and30 repeated continent instances per setup, not10 independent native maps. Actualstock/TAR ResourceGenerator Lua + CSC v2 core, PythonMT19937 resourceRNG, emulated habitat/sorting, no native start adjustment.15 fixed startingplots imported from matching original automatic-debug captures. Separate frozenstocknative-calibration DB and actualTAR DebugGameplay.sqlite(profilebaseline29/fursgrass) have identical59CSCtags; profile captures immutable.

Source runner project/tools/map_lab/abundance_study.py; generateddata Desktop/Codex/csc-offline-abundance-20261016. Frozeninputs, before/after80maps, audits, CSVs, analysisJSON, standaloneviewer. Sourceslocked at output/sources.json; change outputdir after source edits. Allinputs/helpersourcesleftunchanged; no policy tuning. Mainviewer now125entries, historical45exactlypreserved, defaultofflineVanillaAbundant. UpdatedexistingDesktopviewers too. Abundancepanelcompares8setups forselectedQuarter/filter with resourcecosts, coverage, sites/clusters; offline clearlylabelled; selectedversion before reconstructs unchangedgeneratedresources by removinghelperadditions.

FinalBoth-class coverage out30(Tailors,Stones,Gold,Apo): VanillaSparse19,17,8,15; Standard19,19,10,19; Abundant18,19,10,17; TARSparse18,17,9,16; Standard18,19,11,15; Abundant19,19,11,19; Plentiful30,30,17,30; Truly30,30,21,30. NaturalStones9/30 at EVERYlevel despite149→426rawsites, demonstrating quantityvscontinentaltypeallocation. Sixquarters(B,T,Stones,Carp,Black,Brew)haveBase30/30 throughout;Apo24–27before,Gold8–30.276helperdeposits total(avg3.45,max8), normal2.4–2.9/map; rich5.4/5.9;0.59–0.80%ofpre-helperresourcetiles. Zero selectedrepairbudget/habitat failures offline. Normalpresetsnearcalibration; highTAR100%Tailors/Stones/Apo meritsdesignreviewbefore native. ApoAbundant17/30nohelperincreasefixedprobabilitydrawsample, notbudgetfailure.

Checks: all80Luaauditmatchesindependentcensus, safeemptyeligibleplacements/budgets/resources/lastBaseBothpreserved. FreshfullrepeatVanillaSparse,VanillaAbundant,TARTrulyinstance1exactresource+helper+aftermaps.23,040geometrycomparisons pass. FunctionalUI80maps/8setups/8quarters,1,792aggregate+beforeafterchecks pass(no newbrowservisualreview). Native followupnotrun. Durablehumanreport project/docs/research/mods/csc-offline-abundance-study-20261016.md.


## ACTIVE native v3 implemented-only batch — 16 October 2026

Latest user supersedes deferred40map plan: restrict production to implemented Bakers/Tailors, then real maps. Initial10maps -> user vanillaStandard -> latest **five each at vanilla Sparse/Standard/Abundant =15realmaps**, same originalfive seed/rosterpairs. Backgrounded. Individual resource copies/tiles requested. Current runtimev3C.Quarters={'BAKERS','TAILORS'}, Assisted={'TAILORS'}, unchanged7/12Abundantchance; Bakersalreadyaboveaim so no direct repair, as explained to user. Sixdesign-onlyQuarters donotenter runtime protection/targets/palettes. StaticD.Design retainedresearchreference; nativeviewer mergesold6definitions onlyobservationally.

Core additions nowquantity=1; adapter capturesp:GetResourceCount before, assertsnativequantityreadback==1afterSetResourceType. dump.luaexportsnativequantityalltiles. Bothsourceandinstalled3Luafilesmatch. SourcequantityAPIverifiedinofficialPlotToolTip. Scopedunitall5fixtures+10profiles passed, rollback/reentry/two-resourceTailor/optionalmod mapping checks. FocusedSDKdelta deployment at Desktop/Codex/csc-implemented-native-20261016/deploy, preservesunrelatedinstalledfiles/actions. RestartedCivhiddenfromverifiedmainmenu.

NEWrunner project/tools/map_lab/implemented_study.py: configonly+readsinstalledautomaticpass, nevercontrollerplanner/setter. before/afterresourcecountsallplots exactpreservation, addedcopies==addedtiles, pureLuaexactreplay, independentB/Tcensus, beforeUIonceRuntime/SQLchecks. ProducesCSVmap-stats/coverage/added-resource-copies, fullaudit/debug/before/map, verifiedmarkers. Nativekind='implemented-native', all8viewerdefs withonlyB/Ttargets. --first-onlypreflightSparsemap1completed; preferencesrestoredbetweenpreflight/fullbatch. Mainviewercombinedonev3case=>126entries, old125preserved. Fullbatchnowrunning **exec session2120**, command Python-Xutf8 implemented_study.py --output C:/Users/Shadow/Desktop/Codex/csc-implemented-native-20261016 --bundle project/snapshots/map-lab/maps.json --lua-dependencies C:/Users/Shadow/Desktop/Codex/csc-adjacencies/test-deps. No needrestart; skipverifiedmarkersautomatically. Finallyrestoresmods+autostartanddiagnosticsfalse, thencombineall15mainviewer140andstandalone15. Needfinishfullbatch, freshverify_study_preferences.py, native --verify-only ifneeded, checksourcepins/installed115hashes, UI+geoall15, finalstats/report/memoryupdate.

As of20:24local: Sparse1..4verifiedadds1,1,2,1(total5copies; eachquantity1); map5next. Sparse1Dyes,2Silver. Morecompletedmayexistlater, readprogress.log/verifiedmarkers. FirstSparse1BakersBoth2→2/Tailors0→1; Sparse2Bakers3→3/Tailors0→1. SomeBakerBaseSITEScanfallby1asluxuryoccupiescandidate; lastcoveragepreserved, donotclaimallsitespreserved.

UIupdatednativev3labels/targetdashessixdesignonly, Copiescolumnlastindex7, nativebeforequantity0whenreconstructaddedtile. ExistingabundancePanelnowalsohandles3nativegroups; nativehelpdoesnotclaimemulation. test_assistance_viewer.cjs --implemented validatescountsall8before/after,scope/quantities; firstmap16checks+geometry288passed. --controls-onlymain126passed. GeohelpernowstripsCRLFsourcebeforeregex(nativePythonwrite_textWindowsCRLFhadbrokenflagsregex). NoactualgameUIaccessused(noComputerUsepermission). ExistingbrowserUIdeniedearlier; donotbypass. FunctionalfixturetestsnotvisualrenderQA.

Nativeprocessgeneratesabout100sec/map +25sec/export/menu. Keepworking/pollingandcommentaryeach~minute. No subagents authorized. No goalscreated. Do not run oldv1/v2native verifiers oncurrentv3scope. Existingv2offline/sourcehashlockedhistoricaloutputnotrecomputedwithv3. UpdatedcurrentintegrationdocB/Tscope andhistoricalv2reportbanners. Stillneednewnative15humanreportfinalstats+updatedmemoryentry140.


### v3 native batch COMPLETE — 20:45 local

All15 native maps verified, originals141flags/autostartfalse freshly restored, diagnosticfalsefreshcheck, Civmainmenu. No pending exec sessions. Finalbatch Desktop/Codex/csc-implemented-native-20261016/batch.json complete15; --verify-only replayedall15 withoutnewgames.115installedfilesunchanged; native-study-source-hashes.json allmatch. BeforeAbundantallfiveexactoldluxuries4controls. final-verification.json records51060plotpairs, allresources/quantitiespreserved, runtimeQ2only, actualCopies17. Viewerstandalone15 andmain140 rebuilt, old125preserved; oldDesktopcsc-luxury-diversity andcsc-helper-lua viewer.html updatedmain140.

FinalSparse/Standard/Abundant copies5/6/6. PerMap [1,1,2,1,0], [1,1,3,1,0], [1,2,2,1,0]. Resource totalsDyes7 Silver6 Silk3 Sheep1, quantity1each=>17tiles17copies. SparseDyes2Silver2Silk1;Standard2/2/1+Sheep1;AbundantDyes3Silver2Silk1. Standardmap3pairSilver(plot591)+Sheep738 aroundcenter665, plusDyes1282forcenter1209. Mapsresourcebeforetotals1734/1991/2186=>5911, additions0.29%overall.

BakersBasecoverage15/15alllevels;Both11→11,11→11,12→12; Bothsites120→120,121→121,158→158. BasecandidateSITESdrop3/3/2(no coverage loss). TailorsBase15→15,14→15,15→15; Both1→6,4→9,3→9of15. Bothsites1→11,6→17,9→20; connectedclusters1→9,5→11,7→15. Standard/Abundantnearcalibration; Sparselowerstartingbaseline/probabilitysample, donottuneorforcequotaunasked.

Checks allscopedunit5fixtures+10profiles; native15exactreplay/quantitychecks; viewergeometry4320andDOM240beforeAfterchecks+quantity/active-targetchecks pass, oldmaincontrols-onlypasses. No browservisualQA(nativewindowpermissionsremainasbefore). Sourcefingerprints/controllerboundaryverified. Durablecurrentreport project/docs/research/mods/csc-implemented-materials-native-20261016.md. Currentintegration/README/researchindex/memoryupdated. Usergoalfullyachieved; no furthernative40mapsauthorizedbycurrentrequest. FinalreplyshouldleadB/Tscope,15maps,small3-rowcoverage/copytable,17breakdown,viewerlinkandprefsrestored.


## Tailor density v4 — source/offline validation 17 October

After AI trial map counts (Bakers305Base-only17both, Tailors71Base-only2both),
Henno explicitly requested **2x Base-only and4x both** Tailor sites while only
two Quarters exist. CoreVersion4 retains oldv3 continental repair, then applies
map-wide targets against post-v3 geography. C.SiteMultipliers Tailors2/4 is
the central future reduction knob. Assistant added small abundance-scaled
both-floor4 atAbundant (Sparse3/Standard4), announced during work, to avoid
0x4=0 on empty maps; this floor was not separately specified by user.

Separate owned RNG, native-eligible empty tiles only, exact starts/reserved
centers excluded, same continental palettes/actual mapped resources. Both
connections filled first, then Base-only; Baker Base/both counts cannot fall
in any continent during density stage. Shared Flax can help Bakers. No
futureQuarter influence. Density safety caps5%passableland*scale global/8%
continental, min8/2, separate from legacy caps. Audit site_density has
reference/targets/minimum/met/counts/caps; partial target failure explicit.

ActualLua preview on15existing native landscapes (five eachvanillaSparse/
Standard/Abundant), captured nativeeligibility, all15targets met. Testmap1
Standard71->142Base-only,2->8both, totalBase73->150;16extra copies overv3
(6Sheep5Flax2Cotton+1eachDyes/Silk/Silver),17totalCSCcopies. FiveStandard
Base-only[71,75,140,82,94]->[142,150,281,164,189];Both[2,6,5,4,0]->
[8,24,21,16,5]; densitycopies[16,21,35,19,18]. Across15 extra15..41/map.

Output Desktop/Codex/csc-tailor-density-20261017/candidate-02 withplans/maps/
resultsCSVJSON/entrypoint-validation/legacy-core-v3.lua. Parent exploratory
run had tighter caps/no floor and is superseded. preview_tailor_density.py
checks exact legacy additions, independentcensus/nativeeligibility/quantities/
starts/Baker coverage/caps/repeatability. Actualentry tests pass5fixtures+
10vanilla/TARprofiles inclsaveguards/rollback/twocopy/optionalmods/noengineRNG.
Use frozen full-expansion DB Desktop/Codex/csc-qa-fixes-20261015/
fixed-DebugGameplay.sqlite; live cache resetbasegame atmainmenu caused initial
testmissingfeature failure, notplannerbug.

SourceLuaCore/adapter (+data.starting_plots) andSettings tooltip updated,
build wiring unchanged. NOT deployed/native-tested v4; installedCorev3
confirmed unchanged. No new Civ launch. Existing implemented_study.py and
matched-AI controllers expectv3 and oldworldidentity: adapt before v4 native
baseline. Historical15map/nativeAI evidence unchanged. Durable report
project/docs/research/mods/csc-tailor-density-20261017.md, integrationdocupdated.

## ACTIVE v4 native six-map batch — 17 October

User requested5 new maps, then superseded with3vanillaStandard +3vanilla
Abundant. Fresh paired map indices6/7/8: mapseeds830607/830708/830809;
gameseeds940619/940722/940825. Same old1/2/3leader rosters, Online/Prince/
SmallContinents/6major9CS/animalsOn/M&coff/CSC onlycommunity mod. Noautoplay,
noCiv6saves. New tailor_density_native.py controller autoobserves v4, verifies
nativecopies/eligibility/starts/nootherchanges/exactLuaofflineReplay/independent
BTcensus and perresourceinventories; restores141flags/autostart/diagnostics.
Fullinstalled/sourcefingerprints and noObserverResourceWrites verifiedatend.

Focused6fileSDKdeploy done at Desktop/Codex/csc-tailor-density-native-20261017/
deploy; oldbuildbackedup/unrelatedactions preserved. Civ hidden launched;
ACTIVE execsession65769 runs controller --output sameDesktopfolder --rosters
csc-implemented-native-20261016/implemented-vanilla-standard --lua-dependencies
csc-adjacencies/test-deps. Source+installed nowv4 (oldnotdeployed status
superseded). Waitfor6verified maps thenreportbothQuarterresources(base/spec
copies,+added)andBase-only/BothsitesbyMapandlevel. Finalresource-statsJSON/CSV
willhave12rows, batchcomplete6native. Do notuseoldv3verifiers/controllers.
Noautomation created. NoComputerUse/nativewindowaccess. Poll progress sparsely
andkeepuserinformedatmap milestones. Needcompletedstats/durablereport/memory
update/currentintegrationnativevalidation.

### v4 six fresh native maps COMPLETE — 17 October16:33 CEST

3Standard+3Abundant, pairedfreshseeds830607/830708/830809, turn1. Source
v4 now deployed/native validated, supersedes notdeployed note. NativeCopy/
initializationbeforeUI/independentcensus/exactLuaReplay/targets all6 pass.
Landscape all3pairs identical terrain/features/continents/rivers/lakes/neighbors.
121installedfiles+runtimecore/adapter pins unchanged, controller resourcewrites0.
Prefs141flags/autostartfalse+diagnosticsfalse restored/freshverified.

Std BBaseonly/Both344/38,366/20,307/39; T200/12,208/28,198/12. Added23/29/21.
Abund B317/62,347/33,347/36; T199/24,232/24,172/44. Added31/34/29.
Std B Base/Spec copies99/25,104/21,85/21; T46/10,50/13,42/13.
Abund B104/30,111/22,104/23; T50/15,55/14,45/19.
Total167copies across6maps(73Std94Abund), allsingle-copydeposits. SharedFlax
means perQuarter resourcecounts overlap; don'tsum asdistinctmaterials.

Session65769stoppedfirstAbund on transientdebugloadingdisconnect; Civlive,
resumedunchangedturn1 via --resume-current in88841. Bothsessionsnowended.
Allmapsverified, finalpairedcomparison usedp['feature'] onmissingoptionalkey;
corrected to.get offline, no regeneration. Oldcontroller/status/pins archived
connection-reload; runtimeplanner/adapter/buildunchanged; source hashesphase
finalizationrecorded. Sixresults+CSV+validation in Desktop/Codex/
csc-tailor-density-native-20261017. Durable report
project/docs/research/mods/csc-tailor-density-native-20261017.md includes
fullinventory/percontinent coverage/recoverynotes. Main140-entryviewerunchanged.
No further native work authorized/needed this request. NativeMenu willbeclosed
afterfinalcleanupverification toreleaseRAM; no activecontroller/heartbeat.

## Setting rename — 20 October 2026

Henno renamed the setup option to `CSC_RESOURCE_MAP_ASSISTANCE` / Additional Quarter resources (bool, default 1, SortIndex 305; notifications 306). Updated gameplay reader and nine map-lab/AI tool consumers; current integration docs reflect the new name. Keep `CSC_MATERIAL_MAP_ASSISTANCE_DONE` / `_AUDIT`, diagnostics, Lua filenames and action IDs unchanged: those are internal persistence/implementation identities. Canonical actions and generated civ6proj already match and register both setting files; no action edit was needed. Installed the three changed setting/Lua files and regenerated installed modinfo through Firaxis SDK, preserving unrelated actions/metadata (SDK omits the old empty CustomProperties node). Actual Lua 5.1 entry-point smoke checks passed for false/0, true/1/default and re-entry. No game launched. Deployment backup/logs: `C:/Users/Shadow/Desktop/Codex/csc-resource-map-setting-20261020/`.

### Native On/Off follow-up — 20 October 2026

User explicitly resumed native tests and requested closing FireTuner; GUI closed. New `test_setting_native.py` completed exactly two fresh same-seed Small/Continents/Abundant/Online maps (830102/940104), no autoplay/turn advance. Off skipped disabled/0 additions; On completed once at turn1/23 additions. All3404Off plots exactly equal On debug pre-pass; only23audited resources/quantity1 differ afterward; starts/terrain/original deposits preserved. Existing turn3 game saved as `CSC before resource setting test 20261020-212102.Civ6Save` (hash130312fc368000f1241c6ba6149b66e43d748805447fcca250570745ddcfef15). Initial read-only preflight needed a local variable for zero-return/unset config values; no map/game mutation occurred in that failed attempt. Native results+restoration passed; original mod flags/autostart/assistance+diagnostic values restored,122installed files unchanged. Controller exited0; Civ at main menu, FireTuner remains closed. Evidence `Desktop/Codex/csc-resource-setting-native-20261020/`; no monitoring scheduled.
