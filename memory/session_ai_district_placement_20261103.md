# District type, site choice and incentives — 3 November 2026

User asked (1) how district placement is evaluated, (2) custom/arbitrary incentives,
then explicitly added district TYPE choice and current empire needs. Completed
offline research with prepared Ghidra, existing binary evidence, source/API audit
and REA saved-SQLite schema inspection. No game/FireTuner/deployment/tuning/native
target mutation. Old broad campaign and failed high-fan-out observer stay paused.

Durable report: `project/docs/research/mods/civ6-district-choice-placement-and-incentives-20261103.md`.
Evidence: Desktop/Codex/csc-district-placement-20261103, staged in chat's allowed
visualizations root with same basename. Candidate-choice audit, data/API audit,
current exports, static-pointer/flag proof and source snapshots retained.
DLL324c51e9...46c2e98c, Ghidra12.2. 3111 instruction bytes in six scoring/needs
functions verified pristine; 24 source/API files pinned. Independent native and
source reviews. REA schema Evidenceev_a95d61ba66b63a70f0164a048a7e353701c4b4e874689a50d6003c7aa9b65e2c
is old quiescentNov1 DB e1a73e2d...40d60, not new loaded mod runtime. One-record
bundle exported; REA closed openfalse/cleanupfalse. No new native database clone.

Key result: GetBestDistrict3e4a50 scans all admitted plot/type cached scores;
joint district+site max, randomized ties, live reservation threshold. NO >0 test
there: initial sentinelQ8-9999. Up to37 city plot records (3 rings inclcenter),
reveal/owner/city assignment/purchasable-adjacent-land/type/geography gates. Forecast
admission permissive; immediate CanZone only at BuildDistrict3df220 execution.
GetBestLocationFor3e5550 instead fixes a type and selects its best site.

CityEvaluation3e2aa0 ->Net52a440 ->DistrictValue52d500; timing includes maxtech/civic
ETA+buildtime. Dynamic normalized native adjacency, owned/direct terms, fullmax
alternativeSTATICadjacency deduction if chosenstatic<max and NOT Aqueduct
(defe0mask04, provenquery/loader), maintenance/landpurchase/clearance/opportunity,
district/pseudo effects, housing, coverage and unit/resource enabling. Preference
CityPlanner+40: negativeexclude, zero neutral, positive*1.5 net beforelatercache
buildingpropagation3dfee0. Don't assume rawcue==finalscore or 1.5 always improves
negative score. Futurebuilding+explicitprereqs limits retained fromIZ work.

Empire-needs answer YES bounded: activeVictoryStrategy536530/Start538fb0 applies
lists; GrandStrategic4b1540 computescatchup usingown+metplayers yieldmax/gap/stddev
for positivecoefficient+468, writesyieldSensitivityBoostwrapper380/payload390.
GlobalInitialize49c7c0 registersYieldSensitivities +22b8; lambdaa04990/invoke4a2580
rawPE movrax,[rdx+670];addrax468;ret provescoefficientaddress. ShippedXP2
Expansion1_Victories strategies Science/Culture10/25; distinct fromYields25percent.
YieldBonus4b6d70 includesboost among5sources ->Normalize52b110. Housing5298e0 reads
actualhousing/foodsurplus and projectedgrowth. No completeempireportfoliooptimizer
or universalshortfallrule proved; unknownconditionformulas/actualFollowing separate.

Winner CheckForDistrict3e0ee0 creates persistenttree onlyifnoneoutstanding. Tree
research/purchase/reserve/Builderclearance->districtUnitRequest. Reservations own
city/control/value+marginchecks. Queue3e8190 contractscompete withunit/project/
defaultbuilding; bestdistrict !=nextproduction. Physicalcompletion/benefitunmeasured.

Incentives: nativeAdjacency_YieldChanges+D_Adjacencies supports customordinaryYield,
signedamounts/TilesRequired/Self/research gates/nativepredicates. Actualfield
AdjacentResourceClass (NOT...Type), oneclass, noResourceType/TypeTag/plotproperty/
arbitraryLua/AIOnly. Seowon shipped Self+4 anddistrictadjacency-1. CSCprivate
10forward/30reverse/river4 establishedroute, notcalibratedrecommendations.
DynamicYields weighting DefaultValue+actualaggregatepercentbias; PseudoYields
differentconsumer; newpseudonamealonenoroute. Districtfavored sign notlinearvalue.
Lua CallLuaFunction playerId/thresholdBoolean can arbitrarylivecondition gate
globaltype/yieldstrategy, notpercandidatecity/plot/numericalscore. Scriptoperation
targets havecoords butnotordinarydistrictscore. Properties/customUIpreviews don't
proveprospectiveC++consumer; prior3Novemptyplot/skippedpropertyrules retainlimits.
Nativeextension atscore/cacheboundary couldinprinciple supplyarbitraryF(player,
city,type,plot,state), butnoimplementation/testhere; requestpresentvalue/priority
mustagree withcachewinner. Explicitorders/planner areseparatecontrolmechanism.
Privateyields NO automaticAI-only/economicallyinert scope; stale integrationdoc
inertness wording explicitlysuperseded bycurrentcode/nativevalidation/report.

Remaining gaps: actualnewQuarterwhole-scoredecomposition/marginalincentiveeffect,
ordinaryLua numericalperplotinterface, completion/economicbenefit. No thirdretry
ofoldobserver or liveweight changes; a newruntimeobservation must solvefanout
and scientificcoverage beforedispatch. Nextdesignchoice is type-levelmotivation
versussite-levelforecastbridge, notblindlylargerweights.
