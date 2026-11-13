# Placement-time investigation — 13 November

## REA outcome (no new game/native code/tuning change)

Fullreport csc-ai-reservation-write-gap-20261113.md; newAI-C174. Actualhotfix
SHA092abfbb independentlydecompiledREA/Ghidra, notjustoldannotatedreference.
GetBest3e4a50: reservedlive→prioritythreshold, staleFind4019f0missing→default
floor, no positivegate. ReservePlotUpdate55ef10 priorityinteger<<8, TryReserve
3ea040 liveotherclaimrequiresnew>old+5120Q8(20utility), verifieddirectconstant
b65580=00140000. Release3e97e0 clearsonlymatchingID. Nativefloorb66cb0=00f1d8ff.

ExistingAIBT COMPLETE readableeventlinesgiveSinopeexacttimeline:
165 FarmtriggerValue163,ReservePlot26,14SUCCESS;
166 QuartertriggerValue1736,ReservePlot26,14SUCCESS,Accepted1736;
166 actualnativebest444512Q8vsouraccepted-15437Q8. Physicalfoundation169+1,
completion172+1. CE resolve_late_cell rejectsALLnonemptyIDs beforeFinaltrace.
Confirmedsource-levelcoveragebug; builderreservationstronginferenceforactual
miss, rawID/rejectreasonnotcaptured. Preservealias/prevalid/matrix/calleralts.
Same-packet10/20othercitywrites showcapabilityworkedelsewhere, cannotprove
orderrelativetoBest asdeduplogdoesnotretaincrosscellnativeordinal.

Secondindependentgap: UI.GetLegalDistrictTargets usesCanProduce+currentBuild
operationadmission; ownedcompletebidsfromthatlist. Nativeplotjob3e2aa0loops
futureunlocks/prereqETAsbeforeNetValue52a440. So ownedfuturecandidatescanhave
NOoffer; differsfromSinope explicitofferunwritten. Don'tassignallmissingbids
toonecausewithouttrace.

Freshstoppedprefixfinalcounts(originalAI1–5):18foundations(15below3;7x+2,
7x+1,1x+0,2x+3,1x+4 prospectiveMill).42Bestevents,18withbid,17mismatch.
TwoDEFERRED,0FAULT. No finaljournaldrain, notcomplete250measurement. Parser
nowobserverFaultFree separatefrommeasurementComplete (requiresDRAINEDmarker),
17offlineobserver/integrationchecksPASS. Allgameownersgone/exit0/preferences
restored; onlycheckpoint150 existslatest, notsave160. Stopuserinstructionholds.

REA34recordbundle4,022,356bytes Desktop/Codex/.../rea/native-selector-and-reservations-final.json
SHA02d9529c885d5f4cbbd4ed389e64d7a55ca59c1e40d77811b6ff5b579605189d.
REAclosedaftersafeexport. No Frida/nativeprobe/newgameused. Proposednextsteps:
boundedexactskipreasons+reservationmetadata, aligncompletewriter/nativeadmission
withoutclearingclaims, coherentfutureownedcoverage, verifyactualoperandBEFORE
moreoutcomegames orpenaltycalibration. No nativechangesimplemented.

Updatedskilldistrict-choice/findingsAI-N124(cleangitrepopre-edit). Needscoped
commit/pushskill+repo, thenfinishuserwithactualmechanismandlimits. No Quartz.

USER STOPPED ALL GAME TESTS, then explicitly requested REA to understand actual
native behavior. fresh250 stoppedat160 via source-update-request.json to own
worker; closureverified nativeexit0/ownersabsent/preferencesrestored/packages
retired. Worker99392 exit1 is deliberate SourceUpdateHandoff, notnativecrash.
Lastsave150 SHA ed599084d04dfbbb84015c1e08bea976710dbff7d7043a4a9436aa578b343c92.
No furtheroutcomegames or policychanges. MAIN CSC+CE source stillunchanged.

Beforestop, 17 AI foundations:14below3, one4/two3/six2/seven1/one0 (prospective
Millgeometry).41Bestevents,17withpublishedfinal,16mismatch. Notdistinctconstructions.
2DEFERRED lifecycleevents,zeroFAULT. Initialmap/starts/units/roles EXACTparity.
Incompletefreshrun preserves allrawlogs/checkpoints, notqualificationcomplete.

REA actualcurrentSteamXP2opened providerghidra SHA092abfbb..., firstautoanalysis
ready. GetBestDistrict0x1803e4a50 parentdossier
ev_49575d181044b9b03810d26e24bcb69da5aec49fb7c420eac9a1547a40e08e49.
Use inspect_analysis_view native/pseudocode. All detailedresults infunctions
store reaBestParsed/reaOpenParsed (maynot survivecompaction excepttoolsstore).
Do notprintfullREAmetadata: binary_sessionreturned42k hugecapabilities; parse
JSONcontent then emitonlyrelevantnormalized_result.data/keys. No REAstaticclaims
aboutwhichSinopeguardactuallyfailedwithoutrowstate. Currentlyonlyhypotheses.

ExistingGhidraMCP separatelyopenreference324c51e9 byte-matchedtext. Thisturn
decompiled DoTurnActivate3e2820: CalcDistrictValues onlyifparam3fullactivation,
thenAnalyzeTerrain/AnalyzeCityPlots (latter don'trewrite districtscorematrix),
then CheckForDistrict3e0ee0 evenwhenparam3false. Calc3dfee0 updatesmatrixFAuto+508,
onlyaddsbuildingpremiumtoalreadypositivecells. PlotEvaluator3e2aa0 NetValue
at3e30be writesrow+20; row+70/+74 are evaluationcitykey viaEditCity, notactual
tileowner (frontierrowownflag+5a comparesactualowner tokey). New meaningful
lead: CE resolve_late_cell rejectsALLnonemptyreservationIDs; GetBestDistrict
checks Control::Find; staleIDs treatedunreserved, liveones threshold, so our
writeguard stricterthanactualnativeeligibility. Needactualrowmetadata atmiss.
Sinope SAMEpacket17 has10otherFinalwrites; p2c458757packet4 has20others. Thus
notwholecity/callergate/matrixidentityfailure inthoseevents; candidate-specific
reservation/alias/eligibilityguards remainpossible. Beforevalidgate unlikely
afterpositive asCalc onlyadds topositive; runtimefactsstillneeded.

IfcontrolledREAFridaprobe becomesneeded, no outcome game. Be careful:
attachingtoCalculateDistrictValues entry alreadyMinHooked maychange _ReturnAddress
and BREAKourcaller==3e2941guard. Prefer readonly post-callsite3e2941 observation
and selectorpostcallsite, with verifiedliveRBX/RSIthisregister, no relocationof
the CALLitself. Don't claimreadonlyobserverneutralwithoutthatcheck. No probe
prepared/started. REAFrida available perbinary_session; pythondefaultnofrida.
Originaloldautomaticgoalremainspaused. No nativechangesorPRs.

User requests getting to bottom of poor placement and recording Quarter
adjacency at placement in a new run. Active Problems1.6/1.8; all1+2 remain
the architecture scope. Original automatic goal remains paused.

Completed250 outcome: Desktop/Codex/csc-ai-economy-250-20261113/run-continents,
all639+6files pinned, exit0/preferences restored/temporary mods retired.
26Q,8>=3,4>=4;23Base,5Both,18improvedBase,2Bothimproved. B14/T12, active
Stage2B1/T0; oneBchain112 native active turns138..249. See new report, not
a placement success. Five sampled site wins all had zero same-window writes;
cannot infer bypass vs retained plan. Citystates outside Lua/CE cohort but
static SQL/global Builder controls do affect them and autoplay p0.

Added test-only quarter_placement_watch.lua. Transparent bridge.Publish wrapper
reads previous CE journal before reset, records actual Best operand and last
preceding final write, last accepted bid; no score/property/order/RNG changes.
Events record foundation/completion, current eligible geometry and prospective
Mill separately, live Base/Spec/working supply and six neighbors/rule sources.
Existing loaded Quarters labelled loaded; duplicates suppressed; polling fallback
labels first-observed, not foundation. Observer failures don't stop publisher
but invalidate the measurement. Foundation may follow footprint clearing;
bidAdjacency preserves previous accepted planner value, not a pre-clear tile scan.
4 meaningful observer tests+8 full-observation checks PASS (escalated existing
Desktop/Codex/.../test-temp; sandbox tempfile denied). Main CSC/native code
unchanged. Full future driver installs observer and final-drains journal.

Short replay COMPLETED worker29516 using quarter_placement_replay.py, exact
archived packages, 150..175, no new game/world edits/test policy. Root
Desktop/Codex/csc-ai-placement-time-20261113/replay150-175-01. Target original
Sinope Tailors owner1 city327684 plot1062, request166/complete171. Starting150
SHA e951c015f0d551946fb2a9ea8275db8d202aa7b9ec1129f61221340b753d48a3.
Don't open second FireTuner client, edit pinned packages or touch protected saves.
Replay reached175/saved/closedexit0/preferencesrestored/ownersabsent. Global
measurement FAILED: stale DistrictAdded callbacks163 lacked currentdistrictID,
twoFAULTs. Partial parser explicit --partial preserves measurementComplete=false.
Fournewfoundations allpoor (two+2,two+1). SinopeactualBest444512 vsbid-15437packet17,
foundation169+1/completion172+1; laterfoundationbid26378 mustnotreplacechoicebid.
P2c458757Tailors2021 Best471871vsbid20909(+2), foundation158+2.
P3c524295Bakers1012 Best17765==bid17765(+3), precedingFinalwritepacket22.
Rootcauseofmissedreplacement remainsunresolved (notjustpenaltystrength).

Revisedobserver tested16checks: handles staleeventidentity via DEFERRED rawrow,
seedsallaliveincludingminors, catchesrebuilt/instantcompletequarter separately,
ownershipchangesprecedeinstancechanges. Doesnot invent foundationifidentitymissing.
Fresh250NOWRUNNING worker99392 rootDesktop/Codex/csc-ai-placement-time-20261113/fresh250,
samefrozen639+6packages/seeds18461107/29461107; newREADONLYobservation only.
No policy/native changes. Check~15min; lastcheck10:57UTC thenfreshlaunch11:00-ish.
Needinitialparity/footer/faults atfirstcheck. NOsecondconsoleorpackageedits.
full_game_observation.py/watcher alreadycopiedatreplayfreshinstall; do notedit
workerimportedfunctions untilitfinishes. Canfinishdocs/memory/sourceparser/tests.

Static native hypotheses (not verified causes): resolve_late_cell rejects any
reservationID !=-1 but GetBestDistrict treats missing Control request as unreserved
and live request as score threshold. Late capture also requires same matrix
identity and valid BEFORE value although whole-value policy logically prices
valid AFTER candidates. Need actual native traces before changing guards.
Existing CE journal Best already records matrix operand; no new binary needed
for first observation. CE source Desktop/Codex/csc-ai-economy-20261113/ce-source,
branch codex/quarter-economy-forecast, code6f53037/docs3421b37, no PR.

Pending docs: finish new250 report (fix any remaining unassisted citystate wording),
addAI-C172, update architecture results link, scoped commits/pushes. Massive
unrelated SQL/UI/art dirty changes must remain untouched. New diagnostic files,
full_game_observation.py and its test are ours. No new native finding yet.
