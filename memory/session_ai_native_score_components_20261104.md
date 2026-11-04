# Native score components, cache timing and purchases —4 November2026

Henno asked6architecturequestions after the weak-site test: cachecoverage of
locked types/land, potentialfutureland, refresh, laterpositiveuplift, production
competition, and plotpurchases. Then directed us toward understanding fullnative
score factors and adding CSC corrections for missing/misestimated mechanics,
not blindlypenalizingfinalaggregate. This pass stayedoffline/read-only: no new
game/load/attach, tuning, installedcontent or settings changes.

Maintained article:`project/docs/civ6-ai/topics/native/district-score-anatomy.md`.
Full datedreport:`project/docs/research/mods/civ6-district-cache-timing-and-purchases-20261104.md`.
NewfindingsAI-N066..069. NativeexactSHA324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c recheckedGhidra.

Keyfacts:
- MatrixallDistrictDefs x37cityplots includingcenter/radius3, invalidslotsnotvalidscores.
  CanEverZone mapping, plotgates andmax(techETA,civicETA)+construction+horizon
  allowfuturelockedtypes. Revealedunownedrowscanbeevaluated; winnerrequires
  district-capable +owned ORadjacent-ownfrontier. Foreign/othercityrejected.
  NativeNetValuedeductsunownedplotcost; broaderthanourowned-onlyscanner.
- StartTurn3d98f0 resetdone/jobflags; readiness5gates DoOffTurn3e2590 submitsonce
  percycle; job3e2a40 evaluatesallrows. Fullmatchingactivation3e2820 aggregates
  futurebuildings/checksopportunities. NotestablishedslowN-turnrefresh. Fullflag's
  exactouterschedulercalendarmeaningnotexhaustivelytraced.
- GetBestDistrict newproposal waitsforfreesingledistricteventtreeslot.
  NormalQueueNextBuild whenqueueempty; contractsvalidate/update/max, compete
  withbestunit-256Q8/project;buildingonlyfallback. Threatinterruptseparate.
  Retainedrequestmax(old,current) meansnegativefreshnotoldrequestrollback.
- Q8=256storedunits/utility,notyield/Gold norprecisionaccuracy. Districtvalue
  includesyieldweights,pseudoyields, timing/discount, maintenance, purchase/
  harvest/lostimprovement,alternativelanduse,preferences andbuildingforecasts.
  Buildingaggregationcity/typepositive-qualifiedsum ->positivepairvalues.
- NEW52b900prerequisiteheuristic: followFIRSTprerequisitechain depthd; early
  benefitsubtotal*(1+2d)-normalizedmaintenance thenincome discount;lateramenity,
  housing,power,modifieradditionsseparate. SQLloaderproves+1f8/+200vector.
  CSC hiddenRiverAccess->WaterMill andMills->Bakery/Cafe mayaffectheuristic;
  firstpointer/order/subtotalinDelhi/Majapahit NOTcaptured. Noactual3x/5x
  attributionclaimed. Productioncostthroughbuildtime, notinventedflatPdeduction.
- Delhi66743-65536=1207 ->1358358; Maj228808-196608=32200 ->1623830.
  Latergains1,357,151/1,591,630 includepost-hookprocessing. Priorobserverdidnot
  captureper-building/helpervector;cannotnameexactdominantbuilding/effect.
  OrdinaryBakersfamilyWind/WaterMill,Bakery,Cafe; amenities/regionalavailable,
  notprovenactualcontribution. Genericmodifierinterpretercanomitgates/collections
  orlackplotcontext, solegitbenefitsandmispricingmustbeseparated.
- Twoacquisitionroutes: targetedPurchasePlotContract(exactsite;cheapestpositive
  cityquote thennativelegality) andopportunisticEconomicPurchasePlots(citycachedfrontier
  resourcepoint, improvementforecast+FEATUREheuristic/order-sensitive).
  row+4=FeatureNOTimprovement; HasImprovement+50. Plot/slushsavingsgates:
  routineC<P+S &fixed(C/2)<P; targetGold<=floor((P+S)/256) &fixed(C/4)<=P.
  Nativelegality/treasurychecksremain. DefaultweightsS3units4plots1GP1;
  noN-turncountdowninsideinspectedroutines/fullactivationguarded.
- ActualHague74/Pokrovka92logs saySUCCESS PurchasePlot NotBuyinganything.
  DoNOTinferthoseescapeswerepurchases. Exactpre-scanexclusionstillunknown.

Twoindependentread-only agents supportedcache/scheduling andproduction/buying;
root tracedbuildingvalue/depthheuristic, recheckedfreshGhidra/currentSQLiterows.
Focusedexports/constants/thunksandSHAmanifest storedDesktop/Codex/csc-district-decisions-20261104.
Currentdirection: componentledgernativecounted/nativeapproximation/CSCmissing/
unmeasured; preservegenuinevalueandavoidcountingtwice. Noautomaticnewgameor
blanketfinal-scorecap. Oldbroadcampaignremainspaused.15minfuturegameupdatespersist.
