-- CSC AI tuning: native bonus-resource, river and reciprocal sales placement.
-- Broad material guidance uses existing map objects; no marker features.
-- See project/docs/integrations/csc-ai-tuning.md for evidence and limits.

-- File map: three different AI inputs
-- 1. Native placement adjacencies value nearby sales districts, broad bonus
--    resources and rivers using a private planning yield.
-- 2. Exact-material plot modifiers reward owned visible supplies and matching
--    improvements. PseudoYield/Builder priorities are separate production inputs.
-- 3. Strategy/list declarations describe Service research preferences and invoke
--    CSC_AI_ServiceResearchReady from CSC_AI_Research.lua.
--
-- The planning yield has no Gold/Science/etc conversion. These weights are not
-- player-facing yields. A preference declaration alone does not prove a native
-- research choice or reliable strategy restart; see the investigation evidence.
-- Keep the RH improvement base90; Builder priority reduced to50 for the Quarter-resource trial.
-- Remove CSC's former +50% layer before setting the base.
-- Remove the retired CSC percentage-bias list before applying the improvement
-- base. Delete dependent items/list before its type registration, so replay
-- cannot leave two different CSC mechanisms biasing improvement demand.
DELETE FROM AiFavoredItems WHERE ListType='CSC_AI_ImprovementPriorities';
DELETE FROM AiLists WHERE ListType='CSC_AI_ImprovementPriorities';
DELETE FROM AiListTypes WHERE ListType='CSC_AI_ImprovementPriorities';
UPDATE PseudoYields SET DefaultValue=90
WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT';

-- Stock major-civ Units list, also used directly by RH's Ops.sql.
-- Builder preference and improvement valuation are different levers. This row
-- changes a Units-system list; DefaultValue=90 above changes the improvement
-- pseudo-yield. The values do not share one scale and are not Builder counts.
-- Insert only if the native list exists, then also update an existing Builder row.
INSERT INTO AiFavoredItems
        (   ListType,   Item,   Favored,   Value   )
SELECT 'UnitPriorityBoosts','UNIT_BUILDER',1,50
WHERE EXISTS (SELECT 1 FROM AiLists WHERE ListType='UnitPriorityBoosts' AND System='Units')
 AND NOT EXISTS (SELECT 1 FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER');
UPDATE AiFavoredItems SET Favored=1,Value=50
WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER';

-- A virtual yield, following RomanHoliday's native placement technique. This
-- is not Gold/Production/etc. UI integrations omit only this CSC signal.
-- Register the private yield's type before its Yields definition. Empty icon
-- and CSC UI filters keep planning rows out of ordinary yield presentation;
-- this registration defines no conversion into a real economic yield.
INSERT OR IGNORE INTO Types
        (   Type,                       Kind   )
VALUES  (   'YIELD_CSC_AI_PLACEMENT',   'KIND_YIELD'   );
INSERT OR IGNORE INTO Yields
        (   YieldType,                  Name,                          IconString,   OccupiedCityChange,   DefaultValue   )
VALUES  (   'YIELD_CSC_AI_PLACEMENT',   'LOC_CSC_AI_PLACEMENT_NAME',   '',           0,                    1   );
-- This is a DefaultYieldBias preference for the private channel, separate from
-- the local adjacency magnitudes below. NOT EXISTS preserves an existing bias
-- item when replaying the source against a populated database.
INSERT INTO AiFavoredItems
        (   ListType,   Item,   Favored,   Value   )
SELECT 'DefaultYieldBias', 'YIELD_CSC_AI_PLACEMENT', 0, 25
WHERE NOT EXISTS (SELECT 1 FROM AiFavoredItems WHERE ListType='DefaultYieldBias' AND Item='YIELD_CSC_AI_PLACEMENT');

-- The private yield has no conversion into real currency. Sales signals are
-- inert for human economies too, so no dummy technology is needed. This avoids
-- changing technology counts and cost progression merely to gate a signal.

-- Use the live sales tags and expand direct unique replacements on both sides.
-- Deliberately exclude City Centers from the reverse placement rule. No generic
-- Wonder rule: it would reward unrelated Wonders rather than eligible customers.
-- Directed placement graph
-- Candidate is the district being considered; Neighbor is already adjacent.
-- Live SALES tags let Quarters value customers and customer districts value
-- Quarters. These edges guide co-location, not real bilateral transaction amounts.
CREATE TEMP TABLE CSC_AI_SalesPairs (Quarter TEXT, Sales TEXT, PRIMARY KEY (Quarter, Sales));
INSERT OR IGNORE INTO CSC_AI_SalesPairs
SELECT d.DistrictType, t.Type FROM Districts d JOIN TypeTags t
ON t.Tag=CASE d.DistrictType WHEN 'DISTRICT_CSC_BAKERS_QUARTER' THEN 'CLASS_CSC_BAKERS_SALES'
                           WHEN 'DISTRICT_CSC_TAILORS_QUARTER' THEN 'CLASS_CSC_TAILORS_SALES' END
JOIN Districts s ON s.DistrictType=t.Type
WHERE d.DistrictType IN ('DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER');
-- Include each base district itself plus direct one-level unique replacements.
-- Pair/edge primary keys collapse overlapping paths so shared tags or replacement
-- rows cannot duplicate the same district adjacency attachment.
CREATE TEMP TABLE CSC_AI_DistrictVariants (Original TEXT, Variant TEXT, PRIMARY KEY (Original, Variant));
INSERT OR IGNORE INTO CSC_AI_DistrictVariants SELECT DistrictType, DistrictType FROM Districts;
INSERT OR IGNORE INTO CSC_AI_DistrictVariants SELECT ReplacesDistrictType, CivUniqueDistrictType FROM DistrictReplaces;
-- Generate both directions explicitly. City Center remains a Quarter neighbor,
-- but is excluded as a reverse candidate because cities are not built through
-- the ordinary district-placement choice.
CREATE TEMP TABLE CSC_AI_Edges (Candidate TEXT, Neighbor TEXT, PRIMARY KEY (Candidate, Neighbor));
INSERT OR IGNORE INTO CSC_AI_Edges SELECT q.Variant,s.Variant FROM CSC_AI_SalesPairs p
JOIN CSC_AI_DistrictVariants q ON q.Original=p.Quarter JOIN CSC_AI_DistrictVariants s ON s.Original=p.Sales;
INSERT OR IGNORE INTO CSC_AI_Edges SELECT s.Variant,q.Variant FROM CSC_AI_SalesPairs p
JOIN CSC_AI_DistrictVariants q ON q.Original=p.Quarter JOIN CSC_AI_DistrictVariants s ON s.Original=p.Sales
WHERE p.Sales<>'DISTRICT_CITY_CENTER';
-- Each edge adds 10 planning units per matching adjacent district. Ordinary
-- Adjacency_YieldChanges make this visible to native placement. Real Quarter
-- Gold/Production/Culture exchanges remain in the Quarter gameplay rules.
INSERT OR IGNORE INTO Adjacency_YieldChanges
        (   ID,   Description,   YieldType,   YieldChange,   TilesRequired,   AdjacentDistrict   )
SELECT 'CSC_AI_SALES_'||Candidate||'__'||Neighbor, 'LOC_CSC_AI_PLACEMENT_NAME',
 'YIELD_CSC_AI_PLACEMENT',10,1,Neighbor FROM CSC_AI_Edges;
INSERT OR IGNORE INTO District_Adjacencies
        (   DistrictType,   YieldChangeId   )
SELECT Candidate,'CSC_AI_SALES_'||Candidate||'__'||Neighbor FROM CSC_AI_Edges;

-- A deliberately broad Base-material proxy for the implemented Quarters.
-- All bonus-class resources count, including modded ones and resources not
-- mapped to this Quarter. Real Service eligibility still uses CSC material tags
-- and improved supplies. No resource, feature or improvement is changed here.
-- The broad proxy accepts the whole BONUS resource class, so it can value a
-- resource belonging to the wrong industry. The exact tagged-material modifiers
-- below are a separate additional input; this row is not a Service supply test.
CREATE TEMP TABLE CSC_AI_QuarterGuidance (Quarter TEXT PRIMARY KEY);
INSERT INTO CSC_AI_QuarterGuidance
SELECT DistrictType FROM Districts
WHERE DistrictType IN ('DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER');
INSERT OR IGNORE INTO Adjacency_YieldChanges
        (   ID,   Description,   YieldType,   YieldChange,   TilesRequired,   AdjacentResourceClass   )
SELECT 'CSC_AI_BONUS_RESOURCE','LOC_CSC_AI_PLACEMENT_NAME',
 'YIELD_CSC_AI_PLACEMENT',12,1,'RESOURCECLASS_BONUS'
WHERE EXISTS (SELECT 1 FROM Resources WHERE ResourceClassType='RESOURCECLASS_BONUS');
-- Use the native Commercial Hub river predicate, with a smaller guidance value.
-- Both implemented Quarters receive the native river adjacency preference.
-- This does not grant fresh water or unlock a Mill: terrain/building rules still
-- determine those gameplay effects.
INSERT OR IGNORE INTO Adjacency_YieldChanges
        (   ID,               Description,                   YieldType,                  YieldChange,   TilesRequired,   AdjacentRiver   )
VALUES  (   'CSC_AI_RIVER',   'LOC_CSC_AI_PLACEMENT_NAME',   'YIELD_CSC_AI_PLACEMENT',   4,             1,               1   );
INSERT OR IGNORE INTO District_Adjacencies
        (   DistrictType,   YieldChangeId   )
SELECT v.Variant,y.ID FROM CSC_AI_QuarterGuidance q
JOIN CSC_AI_DistrictVariants v ON v.Original=q.Quarter
CROSS JOIN Adjacency_YieldChanges y
WHERE y.ID IN ('CSC_AI_BONUS_RESOURCE','CSC_AI_RIVER');

-- Replace the earlier material base-yield modifiers, including on SQL replay.
-- Remove only the obsolete CSC material-modifier family during replay.
-- Temporary graph tables are build-time scaffolding; the generated adjacency
-- rows remain after those tables are dropped.
DELETE FROM DistrictModifiers WHERE ModifierId LIKE 'MOD_CSC_AI_MATERIAL_%';
DELETE FROM ModifierArguments WHERE ModifierId LIKE 'MOD_CSC_AI_MATERIAL_%';
DELETE FROM Modifiers WHERE ModifierId LIKE 'MOD_CSC_AI_MATERIAL_%';

DROP TABLE CSC_AI_Edges;
DROP TABLE CSC_AI_QuarterGuidance;
DROP TABLE CSC_AI_DistrictVariants;
DROP TABLE CSC_AI_SalesPairs;


-- Quarter-owned presence valuation experiment. Standard native plot-yield effects,
-- exact live resource mappings and owner-relative adjacency; no map markers.
-- RH's plot-yield/pantheon examples informed the native mechanism, not copied code.
-- Unimproved supplies gain40; matching improvements add80 (total120 for one Quarter).
-- The private yield has no economic conversion and is filtered by CSC's UI.
-- Exact material signal
-- Resolve live BASE/SPEC tags into (Quarter,Resource) keys. A resource in both
-- classes is deduplicated within that industry, but may serve both industries.
-- The native ResourceClass is recorded; CSC tags decide membership here.
CREATE TEMP TABLE CSC_AI_Supplies (Quarter TEXT, Resource TEXT, Class TEXT,
 PRIMARY KEY (Quarter,Resource));
INSERT OR IGNORE INTO CSC_AI_Supplies
SELECT d.DistrictType,r.ResourceType,r.ResourceClassType FROM Districts d
JOIN TypeTags t ON t.Tag IN (
 CASE d.DistrictType WHEN 'DISTRICT_CSC_BAKERS_QUARTER' THEN 'CLASS_CSC_BAKERS_BASE' ELSE 'CLASS_CSC_TAILORS_BASE' END,
 CASE d.DistrictType WHEN 'DISTRICT_CSC_BAKERS_QUARTER' THEN 'CLASS_CSC_BAKERS_SPEC' ELSE 'CLASS_CSC_TAILORS_SPEC' END)
JOIN Resources r ON r.ResourceType=t.Type
WHERE d.DistrictType IN ('DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER');
-- Presence is AI-only, one hex from the owning Quarter, and resource-visible.
-- OwnerRequirementSet gates the AI owner; SubjectRequirementSet chooses visible
-- matching plots. Undiscovered resource deposits do not qualify.
INSERT OR IGNORE INTO Requirements
        (   RequirementId,                 RequirementType,                        Inverse   )
VALUES  (   'REQ_CSC_AI_SUPPLY_AI',        'REQUIREMENT_PLAYER_IS_HUMAN',          1   ),
        (   'REQ_CSC_AI_SUPPLY_ADJ',       'REQUIREMENT_PLOT_ADJACENT_TO_OWNER',   0   ),
        (   'REQ_CSC_AI_SUPPLY_VISIBLE',   'REQUIREMENT_PLOT_RESOURCE_VISIBLE',    0   );
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,             Name,            Value   )
VALUES  (   'REQ_CSC_AI_SUPPLY_ADJ',   'MinDistance',   1   ),
        (   'REQ_CSC_AI_SUPPLY_ADJ',   'MaxDistance',   1   );
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,            RequirementSetType   )
VALUES  (   'REQSET_CSC_AI_SUPPLY_AI',   'REQUIREMENTSET_TEST_ALL'   );
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,            RequirementId   )
VALUES  (   'REQSET_CSC_AI_SUPPLY_AI',   'REQ_CSC_AI_SUPPLY_AI'   );
-- Share the native ResourceType predicate across Quarters, while modifier IDs
-- retain Quarter identity. Reusing a test must not merge independent industry
-- contributions from the same material.
INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT DISTINCT 'REQ_CSC_AI_SUPPLY_'||Resource,'REQUIREMENT_PLOT_RESOURCE_TYPE_MATCHES' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT DISTINCT 'REQ_CSC_AI_SUPPLY_'||Resource,'ResourceType',Resource FROM CSC_AI_Supplies;
-- Preserve the40 presence signal on Quarters; move ONLY the marginal80 to
-- ImprovementModifiers. Remove previous CSC trial attachments on cache replay.
DELETE FROM DistrictModifiers WHERE ModifierId LIKE 'MOD_CSC_AI_SUPPLY_%_IMPROVED';
DELETE FROM ModifierArguments WHERE ModifierId LIKE 'MOD_CSC_AI_SUPPLY_%_IMPROVED';
DELETE FROM Modifiers WHERE ModifierId LIKE 'MOD_CSC_AI_SUPPLY_%_IMPROVED';
DELETE FROM ModifierArguments WHERE ModifierId='MOD_CSC_AI_SUPPLY_IMPROVED_VALUE';
DELETE FROM Modifiers WHERE ModifierId='MOD_CSC_AI_SUPPLY_IMPROVED_VALUE';
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_AI_SUPPLY_'||Resource||'_PRESENT','REQUIREMENTSET_TEST_ALL'
 FROM (SELECT DISTINCT Resource FROM CSC_AI_Supplies);
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_AI_SUPPLY_'||Resource||'_PRESENT','REQ_CSC_AI_SUPPLY_'||Resource
 FROM (SELECT DISTINCT Resource FROM CSC_AI_Supplies);
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_AI_SUPPLY_'||Resource||'_PRESENT','REQ_CSC_AI_SUPPLY_ADJ'
 FROM (SELECT DISTINCT Resource FROM CSC_AI_Supplies);
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_AI_SUPPLY_'||Resource||'_PRESENT','REQ_CSC_AI_SUPPLY_VISIBLE'
 FROM (SELECT DISTINCT Resource FROM CSC_AI_Supplies);
-- Quarter-owned presence adds 40 planning units on a matching adjacent resource.
-- Improvement is unnecessary: unimproved supplies are potential industry sites.
-- Several adjacent Quarters may each contribute their own presence signal.
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_AI_SUPPLY_'||Quarter||'__'||Resource||'_PRESENT',
 'MODIFIER_PLAYER_ADJUST_PLOT_YIELD','REQSET_CSC_AI_SUPPLY_AI',
 'REQSET_CSC_AI_SUPPLY_'||Resource||'_PRESENT' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_AI_SUPPLY_'||Quarter||'__'||Resource||'_PRESENT','YieldType','YIELD_CSC_AI_PLACEMENT' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_AI_SUPPLY_'||Quarter||'__'||Resource||'_PRESENT','Amount',40 FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT Quarter,'MOD_CSC_AI_SUPPLY_'||Quarter||'__'||Resource||'_PRESENT' FROM CSC_AI_Supplies;

-- Improvement owns the marginal signal. The player-district collection enforces
-- ownership; its subjects must be the matching Quarter adjacent to THIS plot.
-- One80 bonus per resource/industry, even beside multiple Quarters of that industry.
-- Unlike Quarter-owned presence, this may encourage work while a Quarter builds.
-- The marginal improvement signal reverses ownership: the improvement owns it.
-- First identify the matching adjacent player district, then ask whether at least
-- one exists. Two Quarters of one industry must not repeat the marginal +80.
INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT DISTINCT 'REQ_CSC_AI_IMPROVE_QUARTER_'||Quarter,'REQUIREMENT_DISTRICT_TYPE_MATCHES' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT DISTINCT 'REQ_CSC_AI_IMPROVE_QUARTER_'||Quarter,'DistrictType',Quarter FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT DISTINCT 'REQSET_CSC_AI_IMPROVE_ADJ_'||Quarter,'REQUIREMENTSET_TEST_ALL' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT DISTINCT 'REQSET_CSC_AI_IMPROVE_ADJ_'||Quarter,'REQ_CSC_AI_IMPROVE_QUARTER_'||Quarter FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT DISTINCT 'REQSET_CSC_AI_IMPROVE_ADJ_'||Quarter,'REQ_CSC_AI_SUPPLY_ADJ' FROM CSC_AI_Supplies;
-- COLLECTION_PLAYER_DISTRICTS enforces ownership; the nested set adds Quarter
-- identity and adjacency relative to THIS improvement. Count=1 is an existence
-- threshold, not the number of copies of the reward to attach.
INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT DISTINCT 'REQ_CSC_AI_IMPROVE_HAS_QUARTER_'||Quarter,'REQUIREMENT_COLLECTION_COUNT_ATLEAST' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT DISTINCT 'REQ_CSC_AI_IMPROVE_HAS_QUARTER_'||Quarter,'CollectionType','COLLECTION_PLAYER_DISTRICTS' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT DISTINCT 'REQ_CSC_AI_IMPROVE_HAS_QUARTER_'||Quarter,'Count',1 FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT DISTINCT 'REQ_CSC_AI_IMPROVE_HAS_QUARTER_'||Quarter,'RequirementSetId','REQSET_CSC_AI_IMPROVE_ADJ_'||Quarter FROM CSC_AI_Supplies;
-- The final improvement gate combines AI owner, exact material, visibility and
-- an adjacent matching Quarter. One Quarter gives 40 + 80 on improved supply.
-- Extra same-industry Quarters can add presence, but do not repeat the +80
-- improvement-owned signal.
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_AI_IMPROVE_'||Quarter||'__'||Resource,'REQUIREMENTSET_TEST_ALL' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_AI_IMPROVE_'||Quarter||'__'||Resource,'REQ_CSC_AI_SUPPLY_AI' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_AI_IMPROVE_'||Quarter||'__'||Resource,'REQ_CSC_AI_SUPPLY_'||Resource FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_AI_IMPROVE_'||Quarter||'__'||Resource,'REQ_CSC_AI_SUPPLY_VISIBLE' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_AI_IMPROVE_'||Quarter||'__'||Resource,'REQ_CSC_AI_IMPROVE_HAS_QUARTER_'||Quarter FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId   )
SELECT 'MOD_CSC_AI_IMPROVE_'||Quarter||'__'||Resource,'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',
 'REQSET_CSC_AI_IMPROVE_'||Quarter||'__'||Resource FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_AI_IMPROVE_'||Quarter||'__'||Resource,'YieldType','YIELD_CSC_AI_PLACEMENT' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_AI_IMPROVE_'||Quarter||'__'||Resource,'Amount',80 FROM CSC_AI_Supplies;
-- Improvement_ValidResources selects improvements that support this exact
-- resource. This is a native modifier attachment, not a Lua plot writer or a
-- resource/feature marker that changes the map for planning purposes.
INSERT OR IGNORE INTO ImprovementModifiers
        (   ImprovementType,   ModifierId   )
SELECT v.ImprovementType,'MOD_CSC_AI_IMPROVE_'||s.Quarter||'__'||s.Resource
 FROM CSC_AI_Supplies s JOIN Improvement_ValidResources v ON v.ResourceType=s.Resource;
DROP TABLE CSC_AI_Supplies;

-- Native AI research preferences, activated by a Lua callback in RH's pattern.
-- Materials are potential supplies: no requirement to have improved them yet.
-- Service research plans
-- These tables persist for CSC_AI_Research.lua, unlike the temporary graph tables.
-- Id goes to the callback as ThresholdValue. Stage/SourceBuilding identify the
-- upstream producer chain; CivicType identifies the target Service civic, which
-- need not be the producer building's own unlock.
CREATE TABLE IF NOT EXISTS CSC_AI_ServiceResearch (
 Id INTEGER PRIMARY KEY, QuarterKey TEXT NOT NULL, Stage INTEGER NOT NULL,
 CivicType TEXT NOT NULL, SourceBuilding TEXT NOT NULL);
INSERT OR IGNORE INTO CSC_AI_ServiceResearch
        (   Id,   QuarterKey,   Stage,   CivicType,                 SourceBuilding   )
VALUES  (   1,    'BAKERS',     2,       'CIVIC_FEUDALISM',         'BUILDING_CSC_BAKERS_WIND_MILL'   ),
        (   2,    'BAKERS',     3,       'CIVIC_MEDIEVAL_FAIRES',   'BUILDING_CSC_BAKERS_BAKERY'   ),
        (   3,    'BAKERS',     4,       'CIVIC_URBANIZATION',      'BUILDING_CSC_BAKERS_CAFE'   ),
        (   4,    'TAILORS',    2,       'CIVIC_NAVAL_TRADITION',   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   5,    'TAILORS',    3,       'CIVIC_DIVINE_RIGHT',      'BUILDING_CSC_TAILORS_TAILOR'   ),
        (   6,    'TAILORS',    4,       'CIVIC_OPERA_BALLET',      'BUILDING_CSC_TAILORS_FASHION_HOUSE'   );
-- Plans can request both Civics and Technologies. Insert the Service civic,
-- then collect prerequisites from earlier producer stages in that Quarter.
-- The composite primary key deduplicates a shared unlock within each plan.
CREATE TABLE IF NOT EXISTS CSC_AI_ResearchItems (
 PlanId INTEGER NOT NULL, System TEXT NOT NULL, Item TEXT NOT NULL,
 PRIMARY KEY (PlanId,System,Item));
INSERT OR IGNORE INTO CSC_AI_ResearchItems
        (   PlanId,   System,   Item   )
SELECT Id,'Civics',CivicType FROM CSC_AI_ServiceResearch;
-- Include the producer chain's unlocks, not unrelated improvement-type biases.
INSERT OR IGNORE INTO CSC_AI_ResearchItems
        (   PlanId,   System,   Item   )
SELECT p.Id,'Civics',b.PrereqCivic FROM CSC_AI_ServiceResearch p
 JOIN CSC_AI_ServiceResearch earlier ON earlier.QuarterKey=p.QuarterKey AND earlier.Stage<=p.Stage
 JOIN Buildings b ON b.BuildingType=earlier.SourceBuilding WHERE b.PrereqCivic IS NOT NULL;
INSERT OR IGNORE INTO CSC_AI_ResearchItems
        (   PlanId,   System,   Item   )
SELECT p.Id,'Technologies',b.PrereqTech FROM CSC_AI_ServiceResearch p
 JOIN CSC_AI_ServiceResearch earlier ON earlier.QuarterKey=p.QuarterKey AND earlier.Stage<=p.Stage
 JOIN Buildings b ON b.BuildingType=earlier.SourceBuilding WHERE b.PrereqTech IS NOT NULL;
-- Register the native strategy type, create its row, then bind Call Lua Function
-- to CSC_AI_ServiceResearchReady using this plan ID. The callback reports a
-- readiness signal; it does not select or complete research. A separate native
-- disqualifier excludes non-major players.
INSERT OR IGNORE INTO Types
        (   Type,   Kind   )
SELECT 'STRATEGY_CSC_AI_SERVICE_'||Id,'KIND_VICTORY_STRATEGY' FROM CSC_AI_ServiceResearch;
INSERT OR IGNORE INTO Strategies
        (   StrategyType,   VictoryType,   NumConditionsNeeded   )
SELECT 'STRATEGY_CSC_AI_SERVICE_'||Id,NULL,1 FROM CSC_AI_ServiceResearch;
INSERT OR IGNORE INTO StrategyConditions
        (   StrategyType,   ConditionFunction,   StringValue,   ThresholdValue   )
SELECT 'STRATEGY_CSC_AI_SERVICE_'||Id,'Call Lua Function','CSC_AI_ServiceResearchReady',Id FROM CSC_AI_ServiceResearch;
INSERT OR IGNORE INTO StrategyConditions
        (   StrategyType,   ConditionFunction,   Disqualifier   )
SELECT 'STRATEGY_CSC_AI_SERVICE_'||Id,'Is Not Major',1 FROM CSC_AI_ServiceResearch;
-- Rebuild only CSC's Service preference items/lists from the current plans.
-- Each list name includes its research system so Civics and Technologies cannot
-- be mixed into one native list even when they belong to the same plan.
DELETE FROM AiFavoredItems WHERE ListType LIKE 'CSC_AI_SERVICE_%';
DELETE FROM AiLists WHERE ListType LIKE 'CSC_AI_SERVICE_%';
INSERT OR IGNORE INTO AiListTypes
        (   ListType   )
SELECT DISTINCT 'CSC_AI_SERVICE_'||PlanId||'_'||System FROM CSC_AI_ResearchItems;
INSERT OR IGNORE INTO AiLists
        (   ListType,   System   )
SELECT DISTINCT 'CSC_AI_SERVICE_'||PlanId||'_'||System,System FROM CSC_AI_ResearchItems;
-- Strategy_Priorities connects those lists to their conditional strategy.
-- Favored=1 requests a preference; the authored Value=0 is not proof of no
-- preference or of a particular multiplier. Native list consumption and strategy
-- activation/restart behavior still require the recorded engine tests.
INSERT OR IGNORE INTO Strategy_Priorities
        (   StrategyType,   ListType   )
SELECT DISTINCT 'STRATEGY_CSC_AI_SERVICE_'||PlanId,'CSC_AI_SERVICE_'||PlanId||'_'||System FROM CSC_AI_ResearchItems;
INSERT OR IGNORE INTO AiFavoredItems
        (   ListType,   Item,   Favored,   Value   )
SELECT 'CSC_AI_SERVICE_'||PlanId||'_'||System,Item,1,0 FROM CSC_AI_ResearchItems;
