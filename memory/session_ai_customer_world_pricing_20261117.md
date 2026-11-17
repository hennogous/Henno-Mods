# Customer-world pricing, 17 November

Active goal was clarified: reasonable gameplay-defined economy for all Problems
1.1–1.8/2.1–2.2. Reuse completed work; no exact vanilla component parity or
exhaustive edge qualification. Prospective Services deferred. Three stock-AI
Online250 games follow integration; human QA is the final handoff. G8 later
Problems3–6 research removed from this goal. See maintained goal/status.

CustomerWorld/Facts/Model implementation and12 actual-SQL/Core/Facts tests were
uncommitted at turn start. New interval pricing fixes the0/8 customer quote
failure:8/8 now price in customer-world250-02,15 real pricing cases pass,
10,954 native rows preserved,22-chain smoke/population parity pass, exit0 and
restoration verified. Native249 + Runtime4 + instruction restoration pass.
Astra review finds no material issue.

CE external checkout csc-ai-native-valuation-20261115/ce-source; supported build
output release/Binaries/Win64/GameCore_XP2_CE_FinalRelease.dll SHA
3cdaf7a190f7b190cbc37059c7bd5981ac92b0a13364b8fcc62b91eaf6712b23.
New Interval APIs preserve raw Stream and Fixed; CSC requires the new APIs.
Upstream develop/master still2986a746/e59b5aa9. No PR.

New narrow native probe records CityBuild activation prevalues, postaggregation
values at3e2941 and actual candidate read at GetBestDistrict3e4b2c (ECX score,
EDI reservation threshold, EBX best-so-far, RSI row, R14 district). Avoid hooking
the aggregation CALL: its literal return address is part of CE's late guard.
Baseline customer-native-baseline250-01 completes/closed0. Two late arms skip
because actual IDs are nonempty;1083 hasID3538948 with effectivecomparison
threshold−2559744. NoFind-result/priority-field capture: don't assertstaleID
fromthresholdalone. Native selector's sentinel threshold does NOT
imply literalID−1, which the legacy guardedLate API requires.

Early arm customer-native-early250-01 (session47638, finished0) proves complete
native reception:605685+59110=664795 fresh NetValue; native125288 building uplift
retained; comparator reads790083 versuscontrol730973. Stronger1019221 stillwins.
Two ordinary turns, noobserverfaults, closed/restored0. No active game.

Astra recommends reuse existing early Entry for routine signed SAME-city/type
site differences from a stable ordinary-preferred reference. Keep custom CSC
receiving adjacency unless overlap actually demonstrated. Full59110 marginal is
transportfixture only. No new transientreaderAPI initially. Native applies its
own1.5 district need branch afterNetValue when appropriate (observedfactor1here).
Early permits validnegative rawscores (unlikeLatepositivefinal); must watch zero
crossing because aggregationaddsbuildingvalue only topositives. Existing
CE_AIDistrictSiteAdjustment returns netQ8/intrinsicQ8 for a cheap clamp check.
Bound shortlist reference+3/city/type and max64sites/player, merge earlyprefs/
protection bysamekey, measureheadroom4096writes/16384traces perpacket. Cached
scores changeonnativereevaluation; retainedrequestmaxima stillordinarylifecycle.
Next implement routinecustomer adapter +newQuarter jointworld/trade coverage,
warmperformance, then3freshOnline250integratedonlygames. No fullgamesstarted.

Source uncommitted art/UI/Pedia/Taxes work belongs to other work; preserve it.


## Integrated policy/performance checkpoint,17 November

Goal remains active Problems1.1–1.8/2.1–2.2, three fresh stock-AI Online250 games
next. Signed customer/reference deltas and newQuarter shared worlds integrated.
Local affected-plan search+16 customer worlds/player+128 route timeline memo.
123 economy/82 transaction/16 timing-controller-packaging tests pass. Astra
review passed; packet version guard added. CE native251+4 hook checks pass;
release SHA b7194a83569283033a7c9687ae6d92c33cef7b7d04daaf8e115c641077cd7da9
adds read-only CE_AIMonotonicSeconds. Mature zero-turn integrated-policy250-04
closed/restored0; precise planning passes across fiveAI3.851612/3.489519seconds.
Same Quarter/customer offers as optimized03. Main publisher logs fullwall/perAI
and prior native managed counters; controller samples terminal packet. Full
finish writes ai-processing-time.json averages/max/coverage, retries summed,
missing partial turns excluded. User specifically requests this nextfullgame.
See performance.md and customer-world report. No new gameplaychanges thisslice.
Freeze accepted gameplay+committed economy registry+currentAI+newCE; no unrelated
UI/art/Pedia WIP. planning_campaign supports explicit freeze/SHA/policyqualification;
serial seeds preselected Continents18461107/29461107,Pangaea18431267/28681391,
Fractal19672039/29812257, sharedcontroller15minchecks,mainCSCpolicyonly.


## Active full-game campaign

Main commits571f381f/1d7ecc0f pushed; CE39c5ebf pushed, noPR. Frozen01 at
Desktop/Codex/csc-ai-ordinary-economy-20261117 includes acceptedgameplay+
committed economicregistry+currentmainAI+CEb719. planning_campaign.py running
in execsession15789 (hostPython owns serial children). Continents250-01 is
initializing; initial mainmod turn1 logs two attempts17us and10834us, one
publication, zero policy/runtime errors. Clock works in real gameplay.
Campaignprogress.json records seeds/freeze/SHA. Three preselected maps run
serially, Online250, CL/R2/Suk, stockAI, no probe/test policy, sharedcontroller
15minchecks. Do not start a parallel game or mutate pinned inputs/frozen files.
Next goal continuation: monitor every15min, analyse each closedgame and timing,
fix recoverable failures, finish all3. Fullgame timer requested by user is
implemented/tested; result averages/maxima still pending livegame completion.


## 09:48UTC campaign check

Authoritative execsession15789 stilllive, CivPID20168 child6140/root4752. First
Continents game reaches165 (no fault). Full Lua timing coverage1–165, avg
1586.924ms/max3366.147ms, retriesincluded. Next scheduled checkabout10:03UTC,
then analyse onlywhenclosed. Campaign serialcontinues Pangaea/Fractal automatically.
Do not opena secondTunerconnection orrestartfromstaleartifacts. economy-preflight
json intentionallyproduced atterminal boundary,notstartup. Allnewpolicy in frozen01.
Astra finalarchitectureaudit passes; apparentjointEconomyflagissue retracted
because committed571f381f line580 alreadypropagatesflag. HumanQA consolidated in
csc-economic-integration-manual-qa-20261117.md, pushed dde45155. Offlinecampaign
reportnowincludes availabletimingtable anddropshistoricalPangaeareloadassumption;
8focusedanalysischecks pass. Noactualpolicychangeafterfreeze. Goal active.


## PAUSED by user,17 November10:39UTC

User first requested stopaftercurrentgame; Continents hadalreadyclosed and
Pangaea hadstarted, so scheduler4752 was suspended. Userclarified STOPPangaea
NOW, needmachine. OwnedCiv22484/controller12684/scheduler4752 stopped; nofuture
launch. Pangaea interrupted atlastverified75 (notqualification), Fractalunstarted.
Goalstatus alreadyPAUSED byuser; doNOTresume work/tests withoutuserresume.
Offlinecleanup restored147 original ModGroupItems flags inselectedgroup9,
archived onlyrecorded CSCBakersDevelopmentCE/Mod foldersintoPangaeaoutput,
backedupMods.sqlitefirst, copiedpartiallogs, andwroteinterrupted-by-user.json.
Campaignprogress activeNone,completedContinents,remainingPangaea/Fractal.
NoCiv/Tunerwasrelaunched. Preserveuser'smachine/session.

CompletedContinents250ordinary-economy-results.json:22foundations17B5T allBase,
20+3+,7+4+,5bothmaterials;82/82exactnativeBEST. Completeheld15B4T, improvedBase
15/4,bothimproved2/2; mappedcompletedcustomers13/2,Stage2producer13/4,
Stage2customerbuilding8/0.8Store2Inn,0Dock/Sacristan/Stage4;1101nativeStore
chainturns9sources. Economiccustomer1905sampledstagedwindows/1591attempts/
1587writes/19sitewins;9foundationsonpreviouslyevaluatedtargets (3lastnegative,
someoldproposals; not9attributablepositivewins). Zerojointbudget/unknown/overflow.
Wholepublisher250turnavg2027.657344ms,max4610.54ms; native-managedavg12.251316ms,
max26.4. Sourceworld/settingsparity with14NovContinents verifiedallinitialkeys,
old6vsnew22foundations historicalcontext. Firstanalysiscanonicalprivateoutput
Desktop/Codex/csc-ai-ordinary-economy-20261117/continents250-01. Astra reviewed
firstresults:goodplacement/nativeuptake/sustainedStore,butTailorscustomerfollow-
throughstillgap. Raw2resource-lossesnonlastMaizeWonder48/RiceSpaceport195;
lastownedclasslosseswerecapture/elimination. Firstreportnotyetpromoted beyond
thishandoff; onresume documentresults, runremaining2freshgames,completegoalaudit.
Newanalysiscode/tests76e91b20 pushed; no policychangeafterfrozen01.


## Continents offline analysis authorised/completed,17 November

Userrequestedcontinentsanalysisonly;goalremainsPAUSED,noCivlaunch/nativeconsole/
policychange. Report+compact162KBJSON csc-ai-ordinary-economy-continents-20261117
promoted,AI-C208,index/status/roadmapupdated. All22foundations tie bestgeometry
amongpositiveofferedcity/typepacket.2grade2/13grade3/4grade4/3grade5. Native
Quarter1123purchase30Gold23 followsselection22,foundation33,completion35.
Historicalsameworld14Nov6Q/3Store/0Inn/437chainturns ->22/8/2/1101. Native
slotdistricts158->162,cities48->54,pop602->705;totalProduction+26%,Gold+2.6%,
FoodSurplus+21.9%. Current19completedheldallBaseimproved,4bothimproved;22original
foundationsinclcapturelosses. TailorsTempleplot2159hasWorkshopbutnoTailor;other
3survivingTailorshaveTailorbutnoTemple;noneHarbor. DistinctadjHubs3/15.
Perfavg2.027657s,max4.61054;last50avg2.977s. Centralunknown0,customeradapterskips
153/11659forecastsatunavailable/nonpositivenativequote gate;13clamps. Important
scope:don'tdescribetheseaszeroallquoteunknowns. Noadditionaltests/gamesneeded
forreport;nativefixtureproofs/Astrareviewalreadyqualified. Remaininggamespaused.
