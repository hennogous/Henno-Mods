-- CSC AI tuning: native bonus-resource, river and reciprocal sales placement.
-- Broad material guidance uses existing map objects; no marker features.
-- See project/docs/integrations/csc-ai-tuning.md for evidence and limits.

-- Keep the RH improvement base90; Builder priority reduced to50 for the Quarter-resource trial.
-- Remove CSC's former +50% layer before setting the base.
DELETE FROM AiFavoredItems WHERE ListType='CSC_AI_ImprovementPriorities';
DELETE FROM AiLists WHERE ListType='CSC_AI_ImprovementPriorities';
DELETE FROM AiListTypes WHERE ListType='CSC_AI_ImprovementPriorities';
UPDATE PseudoYields SET DefaultValue=90
WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT';

-- Stock major-civ Units list, also used directly by RH's Ops.sql.
INSERT INTO AiFavoredItems (ListType,Item,Favored,Value)
SELECT 'UnitPriorityBoosts','UNIT_BUILDER',1,50
WHERE EXISTS (SELECT 1 FROM AiLists WHERE ListType='UnitPriorityBoosts' AND System='Units')
 AND NOT EXISTS (SELECT 1 FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER');
UPDATE AiFavoredItems SET Favored=1,Value=50
WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER';

-- A virtual yield, following RomanHoliday's native placement technique. This
-- is not Gold/Production/etc. UI integrations omit only this CSC signal.
INSERT OR IGNORE INTO Types (Type, Kind)
VALUES ('YIELD_CSC_AI_PLACEMENT', 'KIND_YIELD');
INSERT OR IGNORE INTO Yields (YieldType, Name, IconString, OccupiedCityChange, DefaultValue)
VALUES ('YIELD_CSC_AI_PLACEMENT', 'LOC_CSC_AI_PLACEMENT_NAME', '', 0, 1);
INSERT INTO AiFavoredItems (ListType, Item, Favored, Value)
SELECT 'DefaultYieldBias', 'YIELD_CSC_AI_PLACEMENT', 0, 25
WHERE NOT EXISTS (SELECT 1 FROM AiFavoredItems WHERE ListType='DefaultYieldBias' AND Item='YIELD_CSC_AI_PLACEMENT');

-- The private yield has no conversion into real currency. Sales signals are
-- inert for human economies too, so no dummy technology is needed. This avoids
-- changing technology counts and cost progression merely to gate a signal.

-- Use the live sales tags and expand direct unique replacements on both sides.
-- Deliberately exclude City Centers from the reverse placement rule. No generic
-- Wonder rule: it would reward unrelated Wonders rather than eligible customers.
CREATE TEMP TABLE CSC_AI_SalesPairs (Quarter TEXT, Sales TEXT, PRIMARY KEY (Quarter, Sales));
INSERT OR IGNORE INTO CSC_AI_SalesPairs
SELECT d.DistrictType, t.Type FROM Districts d JOIN TypeTags t
ON t.Tag=CASE d.DistrictType WHEN 'DISTRICT_CSC_BAKERS_QUARTER' THEN 'CLASS_CSC_BAKERS_SALES'
                           WHEN 'DISTRICT_CSC_TAILORS_QUARTER' THEN 'CLASS_CSC_TAILORS_SALES' END
JOIN Districts s ON s.DistrictType=t.Type
WHERE d.DistrictType IN ('DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER');
CREATE TEMP TABLE CSC_AI_DistrictVariants (Original TEXT, Variant TEXT, PRIMARY KEY (Original, Variant));
INSERT OR IGNORE INTO CSC_AI_DistrictVariants SELECT DistrictType, DistrictType FROM Districts;
INSERT OR IGNORE INTO CSC_AI_DistrictVariants SELECT ReplacesDistrictType, CivUniqueDistrictType FROM DistrictReplaces;
CREATE TEMP TABLE CSC_AI_Edges (Candidate TEXT, Neighbor TEXT, PRIMARY KEY (Candidate, Neighbor));
INSERT OR IGNORE INTO CSC_AI_Edges SELECT q.Variant,s.Variant FROM CSC_AI_SalesPairs p
JOIN CSC_AI_DistrictVariants q ON q.Original=p.Quarter JOIN CSC_AI_DistrictVariants s ON s.Original=p.Sales;
INSERT OR IGNORE INTO CSC_AI_Edges SELECT s.Variant,q.Variant FROM CSC_AI_SalesPairs p
JOIN CSC_AI_DistrictVariants q ON q.Original=p.Quarter JOIN CSC_AI_DistrictVariants s ON s.Original=p.Sales
WHERE p.Sales<>'DISTRICT_CITY_CENTER';
INSERT OR IGNORE INTO Adjacency_YieldChanges
 (ID,Description,YieldType,YieldChange,TilesRequired,AdjacentDistrict)
SELECT 'CSC_AI_SALES_'||Candidate||'__'||Neighbor, 'LOC_CSC_AI_PLACEMENT_NAME',
 'YIELD_CSC_AI_PLACEMENT',10,1,Neighbor FROM CSC_AI_Edges;
INSERT OR IGNORE INTO District_Adjacencies (DistrictType,YieldChangeId)
SELECT Candidate,'CSC_AI_SALES_'||Candidate||'__'||Neighbor FROM CSC_AI_Edges;

-- A deliberately broad Base-material proxy for the implemented Quarters.
-- All bonus-class resources count, including modded ones and resources not
-- mapped to this Quarter. Real Service eligibility still uses CSC material tags
-- and improved supplies. No resource, feature or improvement is changed here.
CREATE TEMP TABLE CSC_AI_QuarterGuidance (Quarter TEXT PRIMARY KEY);
INSERT INTO CSC_AI_QuarterGuidance
SELECT DistrictType FROM Districts
WHERE DistrictType IN ('DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER');
INSERT OR IGNORE INTO Adjacency_YieldChanges
 (ID,Description,YieldType,YieldChange,TilesRequired,AdjacentResourceClass)
SELECT 'CSC_AI_BONUS_RESOURCE','LOC_CSC_AI_PLACEMENT_NAME',
 'YIELD_CSC_AI_PLACEMENT',12,1,'RESOURCECLASS_BONUS'
WHERE EXISTS (SELECT 1 FROM Resources WHERE ResourceClassType='RESOURCECLASS_BONUS');
-- Use the native Commercial Hub river predicate, with a smaller guidance value.
INSERT OR IGNORE INTO Adjacency_YieldChanges
 (ID,Description,YieldType,YieldChange,TilesRequired,AdjacentRiver)
VALUES ('CSC_AI_RIVER','LOC_CSC_AI_PLACEMENT_NAME','YIELD_CSC_AI_PLACEMENT',4,1,1);
INSERT OR IGNORE INTO District_Adjacencies (DistrictType,YieldChangeId)
SELECT v.Variant,y.ID FROM CSC_AI_QuarterGuidance q
JOIN CSC_AI_DistrictVariants v ON v.Original=q.Quarter
CROSS JOIN Adjacency_YieldChanges y
WHERE y.ID IN ('CSC_AI_BONUS_RESOURCE','CSC_AI_RIVER');

-- Replace the earlier material base-yield modifiers, including on SQL replay.
DELETE FROM DistrictModifiers WHERE ModifierId LIKE 'MOD_CSC_AI_MATERIAL_%';
DELETE FROM ModifierArguments WHERE ModifierId LIKE 'MOD_CSC_AI_MATERIAL_%';
DELETE FROM Modifiers WHERE ModifierId LIKE 'MOD_CSC_AI_MATERIAL_%';

DROP TABLE CSC_AI_Edges;
DROP TABLE CSC_AI_QuarterGuidance;
DROP TABLE CSC_AI_DistrictVariants;
DROP TABLE CSC_AI_SalesPairs;


-- Quarter-owned supply valuation experiment. Standard native plot-yield effects,
-- exact live resource mappings and owner-relative adjacency; no map markers.
-- RH's plot-yield/pantheon examples informed the native mechanism, not copied code.
-- Unimproved supplies gain40; improved supplies gain a further80 (total120).
-- The private yield has no economic conversion and is filtered by CSC's UI.
CREATE TEMP TABLE CSC_AI_Supplies (Quarter TEXT, Resource TEXT, Class TEXT,
 PRIMARY KEY (Quarter,Resource));
INSERT OR IGNORE INTO CSC_AI_Supplies
SELECT d.DistrictType,r.ResourceType,r.ResourceClassType FROM Districts d
JOIN TypeTags t ON t.Tag IN (
 CASE d.DistrictType WHEN 'DISTRICT_CSC_BAKERS_QUARTER' THEN 'CLASS_CSC_BAKERS_BASE' ELSE 'CLASS_CSC_TAILORS_BASE' END,
 CASE d.DistrictType WHEN 'DISTRICT_CSC_BAKERS_QUARTER' THEN 'CLASS_CSC_BAKERS_SPEC' ELSE 'CLASS_CSC_TAILORS_SPEC' END)
JOIN Resources r ON r.ResourceType=t.Type
WHERE d.DistrictType IN ('DISTRICT_CSC_BAKERS_QUARTER','DISTRICT_CSC_TAILORS_QUARTER');
INSERT OR IGNORE INTO Requirements (RequirementId,RequirementType,Inverse) VALUES
 ('REQ_CSC_AI_SUPPLY_AI','REQUIREMENT_PLAYER_IS_HUMAN',1),
 ('REQ_CSC_AI_SUPPLY_ADJ','REQUIREMENT_PLOT_ADJACENT_TO_OWNER',0),
 ('REQ_CSC_AI_SUPPLY_VISIBLE','REQUIREMENT_PLOT_RESOURCE_VISIBLE',0);
INSERT OR IGNORE INTO RequirementArguments (RequirementId,Name,Value) VALUES
 ('REQ_CSC_AI_SUPPLY_ADJ','MinDistance',1),('REQ_CSC_AI_SUPPLY_ADJ','MaxDistance',1);
INSERT OR IGNORE INTO RequirementSets (RequirementSetId,RequirementSetType)
 VALUES ('REQSET_CSC_AI_SUPPLY_AI','REQUIREMENTSET_TEST_ALL');
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId,RequirementId)
 VALUES ('REQSET_CSC_AI_SUPPLY_AI','REQ_CSC_AI_SUPPLY_AI');
INSERT OR IGNORE INTO Requirements (RequirementId,RequirementType)
 SELECT DISTINCT 'REQ_CSC_AI_SUPPLY_'||Resource,'REQUIREMENT_PLOT_RESOURCE_TYPE_MATCHES' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementArguments (RequirementId,Name,Value)
 SELECT DISTINCT 'REQ_CSC_AI_SUPPLY_'||Resource,'ResourceType',Resource FROM CSC_AI_Supplies;
-- The native improved-resource-class predicate is used by God of Craftsmen.
-- Its pillage behavior is checked by the disposable native fixture before play.
INSERT OR IGNORE INTO Requirements (RequirementId,RequirementType)
 SELECT DISTINCT 'REQ_CSC_AI_SUPPLY_IMPROVED_'||Class,'REQUIREMENT_PLOT_IMPROVED_RESOURCE_CLASS_TYPE_MATCHES' FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO RequirementArguments (RequirementId,Name,Value)
 SELECT DISTINCT 'REQ_CSC_AI_SUPPLY_IMPROVED_'||Class,'ResourceClassType',Class FROM CSC_AI_Supplies;
CREATE TEMP TABLE CSC_AI_SupplyStages (Stage TEXT PRIMARY KEY, Amount INTEGER);
INSERT INTO CSC_AI_SupplyStages VALUES ('PRESENT',40),('IMPROVED',80);
INSERT OR IGNORE INTO RequirementSets (RequirementSetId,RequirementSetType)
 SELECT 'REQSET_CSC_AI_SUPPLY_'||Resource||'_'||Stage,'REQUIREMENTSET_TEST_ALL'
 FROM (SELECT DISTINCT Resource FROM CSC_AI_Supplies) CROSS JOIN CSC_AI_SupplyStages;
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId,RequirementId)
 SELECT 'REQSET_CSC_AI_SUPPLY_'||Resource||'_'||Stage,'REQ_CSC_AI_SUPPLY_'||Resource
 FROM (SELECT DISTINCT Resource FROM CSC_AI_Supplies) CROSS JOIN CSC_AI_SupplyStages;
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId,RequirementId)
 SELECT 'REQSET_CSC_AI_SUPPLY_'||Resource||'_'||Stage, 'REQ_CSC_AI_SUPPLY_ADJ'
 FROM (SELECT DISTINCT Resource FROM CSC_AI_Supplies) CROSS JOIN CSC_AI_SupplyStages;
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId,RequirementId)
 SELECT 'REQSET_CSC_AI_SUPPLY_'||Resource||'_'||Stage, 'REQ_CSC_AI_SUPPLY_VISIBLE'
 FROM (SELECT DISTINCT Resource FROM CSC_AI_Supplies) CROSS JOIN CSC_AI_SupplyStages;
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId,RequirementId)
 SELECT DISTINCT 'REQSET_CSC_AI_SUPPLY_'||Resource||'_IMPROVED','REQ_CSC_AI_SUPPLY_IMPROVED_'||Class FROM CSC_AI_Supplies;
INSERT OR IGNORE INTO Modifiers (ModifierId,ModifierType,OwnerRequirementSetId,SubjectRequirementSetId)
 SELECT 'MOD_CSC_AI_SUPPLY_'||Quarter||'__'||Resource||'_'||Stage,
 'MODIFIER_PLAYER_ADJUST_PLOT_YIELD','REQSET_CSC_AI_SUPPLY_AI',
 'REQSET_CSC_AI_SUPPLY_'||Resource||'_'||Stage FROM CSC_AI_Supplies CROSS JOIN CSC_AI_SupplyStages;
INSERT OR IGNORE INTO ModifierArguments (ModifierId,Name,Value)
 SELECT 'MOD_CSC_AI_SUPPLY_'||Quarter||'__'||Resource||'_'||Stage,'YieldType','YIELD_CSC_AI_PLACEMENT'
 FROM CSC_AI_Supplies CROSS JOIN CSC_AI_SupplyStages;
INSERT OR IGNORE INTO ModifierArguments (ModifierId,Name,Value)
 SELECT 'MOD_CSC_AI_SUPPLY_'||Quarter||'__'||Resource||'_'||Stage,'Amount',Amount
 FROM CSC_AI_Supplies CROSS JOIN CSC_AI_SupplyStages;
INSERT OR IGNORE INTO DistrictModifiers (DistrictType,ModifierId)
 SELECT Quarter,'MOD_CSC_AI_SUPPLY_'||Quarter||'__'||Resource||'_'||Stage
 FROM CSC_AI_Supplies CROSS JOIN CSC_AI_SupplyStages;
DROP TABLE CSC_AI_SupplyStages;
DROP TABLE CSC_AI_Supplies;

-- Workshop-pattern marginal improvement signal, attached from the Quarter.
INSERT OR IGNORE INTO Modifiers (ModifierId,ModifierType) VALUES
 ('MOD_CSC_AI_SUPPLY_IMPROVED_VALUE','MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS');
INSERT OR IGNORE INTO ModifierArguments (ModifierId,Name,Value) VALUES
 ('MOD_CSC_AI_SUPPLY_IMPROVED_VALUE','YieldType','YIELD_CSC_AI_PLACEMENT'),
 ('MOD_CSC_AI_SUPPLY_IMPROVED_VALUE','Amount',80);
UPDATE Modifiers SET ModifierType='MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER'
WHERE ModifierId LIKE 'MOD_CSC_AI_SUPPLY_DISTRICT_%_IMPROVED';
DELETE FROM ModifierArguments WHERE ModifierId LIKE 'MOD_CSC_AI_SUPPLY_DISTRICT_%_IMPROVED' AND Name IN ('YieldType','Amount');
INSERT OR REPLACE INTO ModifierArguments (ModifierId,Name,Value)
SELECT ModifierId,'ModifierId','MOD_CSC_AI_SUPPLY_IMPROVED_VALUE' FROM Modifiers
WHERE ModifierId LIKE 'MOD_CSC_AI_SUPPLY_DISTRICT_%_IMPROVED';
