-- Automatic CSC extension for supported RomanHoliday releases. The action runs
-- after the subscribed beta's final database override. CSC_AI.sql contributes
-- only its own Quarter/customer/material signal and Service research namespace.
-- Do not replace RH global pseudo-yields, UnitPriorityBoosts, movement modifiers
-- or replace behavior trees here. The same bounded CSC acquisition/foundation host is
-- used in both modes, with a separate user-controlled subsidy switch.
UPDATE CSC_AI_Profile SET Mode='RH' WHERE Id='ACTIVE';

-- RH's own tooltips, Pedia and report support consult this public database
-- registry by Yields.Name. Register CSC's private channel rather than copying
-- or replacing those screens. A future RH ID/schema must be reviewed first.
INSERT OR IGNORE INTO RHAITags
        (   YieldName   )
VALUES  (   'LOC_CSC_AI_PLACEMENT_NAME'   );

-- Supply the documented any-city production parameter only when RH has not
-- explicitly authored one. Existing values, tree nodes and contract structure
-- remain authoritative; this is not a replacement tree or a Builder order.
INSERT INTO TreeData
        (   DefnId,   NodeId,   TreeName,   DefaultData   )
SELECT 2,n.NodeId,n.TreeName,'-1' FROM BehaviorTreeNodes n
WHERE n.TreeName='Build City Improvement' AND n.NodeType='Build Unit'
 AND NOT EXISTS (SELECT 1 FROM TreeData t WHERE t.TreeName=n.TreeName
                 AND t.NodeId=n.NodeId AND t.DefnId=2);

-- BEGIN CSC RH PRODUCTION CANDIDATE V1
-- CSC RH compatibility candidate v1: native production preference input only.
-- Evidence: native RH pilot's completed Aomori Tailors Quarter117 had Textile
-- Workshop proposals124/205/130 at118/132/139 and no Workshop at150. Native
-- database has no CSC Buildings preferences. Test real production selection,
-- not merely this row's presence. Native Value semantics are not presumed.
-- 90 matches the reviewed RH major-civilization Market preference. Stage4 is
-- lower at60 because these costly buildings need a more developed chain.
-- No RH list, global weight, contract, movement or economic rule is overwritten.
INSERT OR IGNORE INTO AiListTypes
        (   ListType   )
SELECT 'CSC_RH_ChainBuildings' WHERE EXISTS
 (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH');
INSERT OR IGNORE INTO AiLists
        (   ListType,   LeaderType,   System   )
SELECT 'CSC_RH_ChainBuildings','TRAIT_LEADER_MAJOR_CIV','Buildings'
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH');
CREATE TEMP TABLE CSC_RH_ProductionCandidate (BuildingType TEXT PRIMARY KEY, Priority INTEGER);
INSERT INTO CSC_RH_ProductionCandidate VALUES
 ('BUILDING_CSC_BAKERS_WIND_MILL',90),
 ('BUILDING_CSC_BAKERS_WATER_MILL',90),
 ('BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',90),
 ('BUILDING_CSC_BAKERS_BAKERY',90),
 ('BUILDING_CSC_TAILORS_TAILOR',90),
 ('BUILDING_CSC_BAKERS_CAFE',60),
 ('BUILDING_CSC_TAILORS_FASHION_HOUSE',60);
INSERT INTO AiFavoredItems
        (   ListType,   Item,   Favored,   Value   )
SELECT 'CSC_RH_ChainBuildings',b.BuildingType,1,c.Priority
FROM CSC_RH_ProductionCandidate c JOIN Buildings b ON b.BuildingType=c.BuildingType
WHERE b.Cost>0 AND COALESCE(b.MustPurchase,0)=0
 AND b.PrereqDistrict IN ('DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER')
 AND EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH')
 AND NOT EXISTS (SELECT 1 FROM AiFavoredItems a WHERE a.ListType='CSC_RH_ChainBuildings' AND a.Item=b.BuildingType);
DROP TABLE CSC_RH_ProductionCandidate;

-- END CSC RH PRODUCTION CANDIDATE V1

-- BEGIN CSC RH CUSTOMER FORECAST CANDIDATE V2
-- DRAFT CSC RH customer forecast v2. Not installed during frozen references.
-- Eight working Bakers sources in production-v1 had an adjacent City Center
-- but no Granary; all had Feudalism. Their city-name logs contained no Granary
-- proposal/selection. This is an observed bottleneck, not scorer-cause proof.
--
-- A FUNCTIONING Mill owns the forecast before the Granary exists. It attaches
-- one private building-yield input to adjacent OWNED City Centers, following
-- the same native owner -> player-district -> building path as Mill sales.
-- Attaching only to Granary would risk not existing until after its decision.
-- No real Food/Gold, purchase, free building, civic gate or Builder rule changes.
-- Forty is a trial planning amount matching CSC's existing presence input;
-- native potential-yield application and production response still need tests.
CREATE TEMP TABLE CSC_RH_CustomerForecast (
    SourceBuilding TEXT PRIMARY KEY,
    Key TEXT
);
INSERT INTO CSC_RH_CustomerForecast
        (   SourceBuilding,   Key   )
SELECT BuildingType,
       CASE BuildingType WHEN 'BUILDING_CSC_BAKERS_WIND_MILL' THEN 'WIND' ELSE 'WATER' END
FROM Buildings
WHERE BuildingType IN ('BUILDING_CSC_BAKERS_WIND_MILL', 'BUILDING_CSC_BAKERS_WATER_MILL')
  AND EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH');
-- Expand direct unique replacements exactly once, as CSC's sales routes do.
-- Each child adjusts one building; never attach two ModifierId arguments to
-- the same wrapper or let a replacement inherit a duplicate reward.
CREATE TEMP TABLE CSC_RH_CustomerForecastTargets (BuildingType TEXT PRIMARY KEY);
INSERT OR IGNORE INTO CSC_RH_CustomerForecastTargets
        (   BuildingType   )
SELECT 'BUILDING_GRANARY' WHERE EXISTS (SELECT 1 FROM CSC_RH_CustomerForecast);
INSERT OR IGNORE INTO CSC_RH_CustomerForecastTargets
        (   BuildingType   )
SELECT CivUniqueBuildingType FROM BuildingReplaces
WHERE ReplacesBuildingType='BUILDING_GRANARY'
  AND EXISTS (SELECT 1 FROM CSC_RH_CustomerForecast);

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT 'REQ_CSC_RH_CUSTOMER_FORECAST_' || Key, 'REQUIREMENT_CITY_HAS_BUILDING'
FROM CSC_RH_CustomerForecast;
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_RH_CUSTOMER_FORECAST_' || Key, 'BuildingType', SourceBuilding
FROM CSC_RH_CustomerForecast;
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_RH_CUSTOMER_FORECAST_' || Key, 'MustBeFunctioning', 1
FROM CSC_RH_CustomerForecast;
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_RH_CUSTOMER_FORECAST_' || Key, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_RH_CustomerForecast;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_RH_CUSTOMER_FORECAST_' || Key, 'REQ_CSC_AI_SUPPLY_AI'
FROM CSC_RH_CustomerForecast;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_RH_CUSTOMER_FORECAST_' || Key, 'REQ_CSC_RH_CUSTOMER_FORECAST_' || Key
FROM CSC_RH_CustomerForecast;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_RH_CUSTOMER_FORECAST_ADJ_CENTER', 'REQUIREMENTSET_TEST_ALL'
WHERE EXISTS (SELECT 1 FROM CSC_RH_CustomerForecast);
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_RH_CUSTOMER_FORECAST_ADJ_CENTER', 'REQ_CSC_DISTRICT_IS_CITY_CENTER'
WHERE EXISTS (SELECT 1 FROM CSC_RH_CustomerForecast);
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_RH_CUSTOMER_FORECAST_ADJ_CENTER', 'REQ_CSC_AI_SUPPLY_ADJ'
WHERE EXISTS (SELECT 1 FROM CSC_RH_CustomerForecast);

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_RH_CUSTOMER_FORECAST_ATTACH_' || Key || '__' || t.BuildingType,
       'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',
       'REQSET_CSC_RH_CUSTOMER_FORECAST_' || Key,
       'REQSET_CSC_RH_CUSTOMER_FORECAST_ADJ_CENTER'
FROM CSC_RH_CustomerForecast CROSS JOIN CSC_RH_CustomerForecastTargets t;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_RH_CUSTOMER_FORECAST_ATTACH_' || Key || '__' || t.BuildingType,
       'ModifierId', 'MOD_CSC_RH_CUSTOMER_FORECAST_VALUE_' || t.BuildingType
FROM CSC_RH_CustomerForecast CROSS JOIN CSC_RH_CustomerForecastTargets t;
INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,   ModifierId   )
SELECT SourceBuilding, 'MOD_CSC_RH_CUSTOMER_FORECAST_ATTACH_' || Key || '__' || t.BuildingType
FROM CSC_RH_CustomerForecast CROSS JOIN CSC_RH_CustomerForecastTargets t;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType   )
SELECT 'MOD_CSC_RH_CUSTOMER_FORECAST_VALUE_' || BuildingType, 'MODIFIER_BUILDING_YIELD_CHANGE'
FROM CSC_RH_CustomerForecastTargets;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_RH_CUSTOMER_FORECAST_VALUE_' || BuildingType, 'BuildingType', BuildingType
FROM CSC_RH_CustomerForecastTargets;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_RH_CUSTOMER_FORECAST_VALUE_' || BuildingType, 'YieldType', 'YIELD_CSC_AI_PLACEMENT'
FROM CSC_RH_CustomerForecastTargets;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_RH_CUSTOMER_FORECAST_VALUE_' || BuildingType, 'Amount', 40
FROM CSC_RH_CustomerForecastTargets;
DROP TABLE CSC_RH_CustomerForecastTargets;
DROP TABLE CSC_RH_CustomerForecast;

-- END CSC RH CUSTOMER FORECAST CANDIDATE V2

-- BEGIN CSC RH CUSTOMER FORECAST SCOPE CORRECTION V3
-- Stable configured-role gate for the RH Granary forecast only. A native
-- autoplay trial returned a human Granary with actual private40 despite the
-- inverse IsHuman requirement. The RH-only role script stamps source Quarter
-- plots using the original configured-human identities. Missing property is
-- ineligible; retain the functioning Mill and current AI gates as well.
INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT 'REQ_CSC_RH_CUSTOMER_FORECAST_CONFIGURED_AI', 'REQUIREMENT_PLOT_PROPERTY_MATCHES'
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH');
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_RH_CUSTOMER_FORECAST_CONFIGURED_AI', 'PropertyName', 'CSC_RH_CUSTOMER_CONFIGURED_AI'
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH');
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_RH_CUSTOMER_FORECAST_CONFIGURED_AI', 'PropertyMinimum', 1
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH');
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT RequirementSetId, 'REQ_CSC_RH_CUSTOMER_FORECAST_CONFIGURED_AI'
FROM RequirementSets
WHERE RequirementSetId IN ('REQSET_CSC_RH_CUSTOMER_FORECAST_WIND', 'REQSET_CSC_RH_CUSTOMER_FORECAST_WATER')
  AND EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH');

-- END CSC RH CUSTOMER FORECAST SCOPE CORRECTION V3



-- BEGIN CSC RH MATERIAL-BACKED WORKSHOP FORECAST V6
-- Native future Workshop input: 80 private planning units for an adjacent owned,
-- visible, improvable Base resource, plus40 when Specialty is also present.
-- Existence flags do not multiply the reward by resource count. The RH-only role
-- bridge mirrors six-neighbour facts onto THIS Tailors source plot; SQL applies
-- the planning effect before the Workshop exists. No real Culture is added.
--
-- V5's native whole-empire collection counter failed a supplied Heh source even
-- while its configured-role gate was Met and its purchased Flax was in the city
-- plot registry, revealed and farmed. The cache/collection cause was not isolated.
-- Bounded fact properties replace that counter; amounts, production preferences,
-- RH/global/Basic/Builder policy and purchase economics remain unchanged.
CREATE TEMP TABLE CSC_RH_WorkshopForecast (Key TEXT PRIMARY KEY, Amount INTEGER);
INSERT INTO CSC_RH_WorkshopForecast
        (   Key,   Amount   )
SELECT 'BASE',80
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH')
  AND EXISTS (SELECT 1 FROM Buildings WHERE BuildingType='BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP')
  AND EXISTS (SELECT 1 FROM Districts WHERE DistrictType='DISTRICT_CSC_TAILORS_QUARTER');
INSERT INTO CSC_RH_WorkshopForecast
        (   Key,   Amount   )
SELECT 'BOTH_EXTRA',40 WHERE EXISTS (SELECT 1 FROM CSC_RH_WorkshopForecast);

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT 'REQ_CSC_RH_WORKSHOP_FACT_BASE', 'REQUIREMENT_PLOT_PROPERTY_MATCHES' WHERE EXISTS (SELECT 1 FROM CSC_RH_WorkshopForecast)
UNION SELECT 'REQ_CSC_RH_WORKSHOP_FACT_SPEC', 'REQUIREMENT_PLOT_PROPERTY_MATCHES' WHERE EXISTS (SELECT 1 FROM CSC_RH_WorkshopForecast);
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_RH_WORKSHOP_FACT_BASE', 'PropertyName', 'CSC_RH_WORKSHOP_BASE_PRESENT' WHERE EXISTS (SELECT 1 FROM CSC_RH_WorkshopForecast)
UNION SELECT 'REQ_CSC_RH_WORKSHOP_FACT_SPEC', 'PropertyName', 'CSC_RH_WORKSHOP_SPEC_PRESENT' WHERE EXISTS (SELECT 1 FROM CSC_RH_WorkshopForecast)
UNION SELECT 'REQ_CSC_RH_WORKSHOP_FACT_BASE', 'PropertyMinimum', '1' WHERE EXISTS (SELECT 1 FROM CSC_RH_WorkshopForecast)
UNION SELECT 'REQ_CSC_RH_WORKSHOP_FACT_SPEC', 'PropertyMinimum', '1' WHERE EXISTS (SELECT 1 FROM CSC_RH_WorkshopForecast);
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_RH_WORKSHOP_OWNER_' || Key, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_RH_WorkshopForecast;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_RH_WORKSHOP_OWNER_' || Key, 'REQ_CSC_RH_CUSTOMER_FORECAST_CONFIGURED_AI' FROM CSC_RH_WorkshopForecast
UNION SELECT 'REQSET_CSC_RH_WORKSHOP_OWNER_' || Key, 'REQ_CSC_AI_SUPPLY_AI' FROM CSC_RH_WorkshopForecast
UNION SELECT 'REQSET_CSC_RH_WORKSHOP_OWNER_' || Key, 'REQ_CSC_RH_WORKSHOP_FACT_BASE' FROM CSC_RH_WorkshopForecast
UNION SELECT 'REQSET_CSC_RH_WORKSHOP_OWNER_' || Key, 'REQ_CSC_RH_WORKSHOP_FACT_SPEC' FROM CSC_RH_WorkshopForecast WHERE Key='BOTH_EXTRA';
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId   )
SELECT 'MOD_CSC_RH_WORKSHOP_FORECAST_' || Key, 'MODIFIER_BUILDING_YIELD_CHANGE', 'REQSET_CSC_RH_WORKSHOP_OWNER_' || Key
FROM CSC_RH_WorkshopForecast;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_RH_WORKSHOP_FORECAST_' || Key, 'BuildingType', 'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP' FROM CSC_RH_WorkshopForecast
UNION SELECT 'MOD_CSC_RH_WORKSHOP_FORECAST_' || Key, 'YieldType', 'YIELD_CSC_AI_PLACEMENT' FROM CSC_RH_WorkshopForecast
UNION SELECT 'MOD_CSC_RH_WORKSHOP_FORECAST_' || Key, 'Amount', Amount FROM CSC_RH_WorkshopForecast;
INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CSC_TAILORS_QUARTER', 'MOD_CSC_RH_WORKSHOP_FORECAST_' || Key
FROM CSC_RH_WorkshopForecast;
DROP TABLE CSC_RH_WorkshopForecast;
-- END CSC RH MATERIAL-BACKED WORKSHOP FORECAST V6

-- BEGIN CSC RH STRATEGY BUILDING COVERAGE V7
-- CSC counterparts for RH's existing economic investment strategies. Native
-- AI_Victories logs showed development Following for players1/4 at5 and
-- industrial Following for all five AI by124. Their Buildings lists reward
-- vanilla industry buildings500/600, but omit CSC industry buildings.
-- These are preference inputs, not guaranteed production or a score formula.
--
-- Preserve RH's strategy activation, weights, difficulty bounds and authored
-- entries. Add CSC items only where the source preference and native strategy
-- binding actually exist. Stage2 producers follow Workshop investment; later
-- eras carry them alongside Factory so an unfinished prerequisite chain is not
-- forgotten. Stage3 consumer production follows Factory. Stage4 venues follow
-- Broadcast Center only in RH's development strategy. No leader/minor list is
-- copied indiscriminately, and no native building purchase is requested.
CREATE TEMP TABLE CSC_RH_StrategyTemplates (
    ListType TEXT,
    Stage INTEGER,
    TemplateBuilding TEXT,
    PRIMARY KEY (ListType, Stage)
);
INSERT INTO CSC_RH_StrategyTemplates
        (   ListType,                 Stage,   TemplateBuilding   )
VALUES  (   'RHDevZoneBuildings',     2,       'BUILDING_WORKSHOP'   ),
        (   'RHDevZoneBuildings',     3,       'BUILDING_FACTORY'   ),
        (   'RHDevZoneBuildings',     4,       'BUILDING_BROADCAST_CENTER'   ),
        (   'IndustrialBuildings',    2,       'BUILDING_WORKSHOP'   ),
        (   'IndustrialBuildings',    3,       'BUILDING_FACTORY'   ),
        (   'ModernBuildings',        2,       'BUILDING_FACTORY'   ),
        (   'ModernBuildings',        3,       'BUILDING_FACTORY'   ),
        (   'AtomicBuildings',        2,       'BUILDING_FACTORY'   ),
        (   'AtomicBuildings',        3,       'BUILDING_FACTORY'   ),
        (   'InformationBuildings',   2,       'BUILDING_FACTORY'   ),
        (   'InformationBuildings',   3,       'BUILDING_FACTORY'   );
CREATE TEMP TABLE CSC_RH_StrategyCounterparts (
    BuildingType TEXT PRIMARY KEY,
    Stage INTEGER,
    QuarterType TEXT
);
INSERT INTO CSC_RH_StrategyCounterparts
        (   BuildingType,                              Stage,   QuarterType   )
VALUES  (   'BUILDING_CSC_BAKERS_WATER_MILL',          2,       'DISTRICT_CSC_BAKERS_QUARTER'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',           2,       'DISTRICT_CSC_BAKERS_QUARTER'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   2,       'DISTRICT_CSC_TAILORS_QUARTER'   ),
        (   'BUILDING_CSC_BAKERS_BAKERY',              3,       'DISTRICT_CSC_BAKERS_QUARTER'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             3,       'DISTRICT_CSC_TAILORS_QUARTER'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',                4,       'DISTRICT_CSC_BAKERS_QUARTER'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',      4,       'DISTRICT_CSC_TAILORS_QUARTER'   );
INSERT INTO AiFavoredItems
    (
        ListType,
        Item,
        Favored,
        Value,
        StringVal,
        MinDifficulty,
        MaxDifficulty,
        TooltipString
    )
SELECT DISTINCT
        a.ListType,
        c.BuildingType,
        a.Favored,
        a.Value,
        a.StringVal,
        a.MinDifficulty,
        a.MaxDifficulty,
        a.TooltipString
FROM CSC_RH_StrategyTemplates t
JOIN CSC_RH_StrategyCounterparts c ON c.Stage=t.Stage
JOIN AiFavoredItems a ON a.ListType=t.ListType AND a.Item=t.TemplateBuilding
JOIN AiLists l ON l.ListType=a.ListType AND l.System='Buildings'
JOIN Buildings b ON b.BuildingType=c.BuildingType AND b.PrereqDistrict=c.QuarterType
JOIN Types k ON k.Type=b.BuildingType AND k.Kind='KIND_BUILDING'
WHERE b.Cost>0 AND COALESCE(b.MustPurchase,0)=0 AND COALESCE(b.InternalOnly,0)=0
  AND EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH')
  AND EXISTS (SELECT 1 FROM Strategy_Priorities p WHERE p.ListType=t.ListType)
  AND NOT EXISTS (SELECT 1 FROM AiFavoredItems old WHERE old.ListType=a.ListType AND old.Item=c.BuildingType);
DROP TABLE CSC_RH_StrategyCounterparts;
DROP TABLE CSC_RH_StrategyTemplates;
-- END CSC RH STRATEGY BUILDING COVERAGE V7


-- BEGIN CSC RH FOUNDATION PRIORITY V8
-- A confirmed, still-owned incomplete assisted foundation activates only its
-- Quarter's native Districts preference. Lua reads the persisted assistance
-- journal and exact original city/plot/type; it never changes queues or grants
-- production. Completed, captured, missing and ambiguous sites fail closed.
-- Native preferences are player-wide: other cities can also prefer this Quarter
-- type while the backlog exists. Extra placements are an explicit test outcome.
-- Value 300 matches RH's DevZone Industrial Zone preference, not a known score
-- formula. Native callback use, strategy adoption and completion bids must be
-- observed separately; these definitions alone do not establish an effect.
CREATE TEMP TABLE CSC_RH_FinishTypes (Quarter TEXT PRIMARY KEY);
INSERT INTO CSC_RH_FinishTypes VALUES ('BAKERS'), ('TAILORS');
INSERT OR IGNORE INTO Types (Type, Kind)
SELECT 'STRATEGY_CSC_RH_FINISH_'||Quarter, 'KIND_VICTORY_STRATEGY' FROM CSC_RH_FinishTypes;
INSERT OR IGNORE INTO Strategies (StrategyType, VictoryType, NumConditionsNeeded)
SELECT 'STRATEGY_CSC_RH_FINISH_'||Quarter, NULL, 1 FROM CSC_RH_FinishTypes;
INSERT OR IGNORE INTO StrategyConditions (StrategyType, ConditionFunction, Disqualifier)
SELECT 'STRATEGY_CSC_RH_FINISH_'||Quarter, 'Is Not Major', 1 FROM CSC_RH_FinishTypes f
WHERE NOT EXISTS (SELECT 1 FROM StrategyConditions c WHERE c.StrategyType='STRATEGY_CSC_RH_FINISH_'||f.Quarter AND c.ConditionFunction='Is Not Major');
INSERT OR IGNORE INTO StrategyConditions (StrategyType, ConditionFunction, StringValue, ThresholdValue)
SELECT 'STRATEGY_CSC_RH_FINISH_'||Quarter, 'Call Lua Function', 'CSC_RH_Finish_'||Quarter, 0
FROM CSC_RH_FinishTypes f
WHERE NOT EXISTS (SELECT 1 FROM StrategyConditions c WHERE c.StrategyType='STRATEGY_CSC_RH_FINISH_'||f.Quarter AND c.ConditionFunction='Call Lua Function');
INSERT OR IGNORE INTO AiListTypes (ListType)
SELECT 'CSC_RH_Finish_'||Quarter FROM CSC_RH_FinishTypes;
INSERT OR IGNORE INTO AiLists (ListType, System)
SELECT 'CSC_RH_Finish_'||Quarter, 'Districts' FROM CSC_RH_FinishTypes f
WHERE NOT EXISTS (SELECT 1 FROM AiLists a WHERE a.ListType='CSC_RH_Finish_'||f.Quarter);
INSERT OR IGNORE INTO Strategy_Priorities (StrategyType, ListType)
SELECT 'STRATEGY_CSC_RH_FINISH_'||Quarter, 'CSC_RH_Finish_'||Quarter FROM CSC_RH_FinishTypes f
WHERE NOT EXISTS (SELECT 1 FROM Strategy_Priorities p WHERE p.StrategyType='STRATEGY_CSC_RH_FINISH_'||f.Quarter AND p.ListType='CSC_RH_Finish_'||f.Quarter);
INSERT OR IGNORE INTO AiFavoredItems (ListType, Item, Favored, Value)
SELECT 'CSC_RH_Finish_'||Quarter, 'DISTRICT_CSC_'||Quarter||'_QUARTER', 1, 300
FROM CSC_RH_FinishTypes f
WHERE NOT EXISTS (SELECT 1 FROM AiFavoredItems a WHERE a.ListType='CSC_RH_Finish_'||f.Quarter AND a.Item='DISTRICT_CSC_'||f.Quarter||'_QUARTER');
DROP TABLE CSC_RH_FinishTypes;
-- END CSC RH FOUNDATION PRIORITY V8


