-- Candidate for ordinary Workshop CSC. A city attaches only a rule selected
-- for its own material layout. Its center plot property enables or withdraws
-- the rule. Unattached definitions have no recipients and pay no yields.
INSERT OR IGNORE INTO Types (Type, Kind)
VALUES ('MODIFIER_CSC_AI_CITY_MATERIAL_TERRAIN', 'KIND_MODIFIER');
INSERT OR IGNORE INTO DynamicModifiers (ModifierType, CollectionType, EffectType)
VALUES ('MODIFIER_CSC_AI_CITY_MATERIAL_TERRAIN', 'COLLECTION_OWNER', 'EFFECT_TERRAIN_ADJACENCY');

CREATE TEMP TABLE CSC_AI_LocalMaterialRules AS
WITH Counts(N) AS (VALUES (1),(2),(3),(4),(5),(6))
SELECT DISTINCT q.DistrictType AS Quarter, t.TerrainType AS Terrain, c.N AS Required,
       'CSC_AI_SITE_' || q.DistrictType || '__' || t.TerrainType || '_' || c.N AS Rule
FROM CSC_QuarterMaterialAdjacencyConfig m
JOIN Districts q ON q.DistrictType = 'DISTRICT_CSC_' || m.QuarterKey || '_QUARTER'
CROSS JOIN Terrains t CROSS JOIN Counts c
WHERE m.SourceTag = 'CLASS_CSC_' || m.QuarterKey || '_BASE'
  AND m.SourceFilter = '' AND m.AdjacencyType = 'FROM_RINGS_TYPETAG_RESOURCE'
  AND t.Water = 0 AND t.Impassable = 0;

INSERT OR IGNORE INTO Requirements (RequirementId, RequirementType)
SELECT Rule, 'REQUIREMENT_PLOT_PROPERTY_MATCHES' FROM CSC_AI_LocalMaterialRules;
INSERT OR IGNORE INTO RequirementArguments (RequirementId, Name, Value)
SELECT Rule, 'PropertyName', Rule FROM CSC_AI_LocalMaterialRules UNION ALL
SELECT Rule, 'PropertyMinimum', 1 FROM CSC_AI_LocalMaterialRules;
INSERT OR IGNORE INTO RequirementSets (RequirementSetId, RequirementSetType)
SELECT Rule, 'REQUIREMENTSET_TEST_ALL' FROM CSC_AI_LocalMaterialRules;
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId, RequirementId)
SELECT Rule, Rule FROM CSC_AI_LocalMaterialRules;
INSERT OR IGNORE INTO Modifiers (ModifierId, ModifierType, SubjectRequirementSetId)
SELECT Rule, 'MODIFIER_CSC_AI_CITY_MATERIAL_TERRAIN', Rule FROM CSC_AI_LocalMaterialRules;
-- Civ sums Amount per matching neighbor and divides each record separately.
-- Amount 1 preserves a zero below the chosen minimum number of neighbors.
INSERT OR IGNORE INTO ModifierArguments (ModifierId, Name, Value)
SELECT Rule, 'DistrictType', Quarter FROM CSC_AI_LocalMaterialRules UNION ALL
SELECT Rule, 'TerrainType', Terrain FROM CSC_AI_LocalMaterialRules UNION ALL
SELECT Rule, 'TilesRequired', Required FROM CSC_AI_LocalMaterialRules UNION ALL
SELECT Rule, 'Amount', 1 FROM CSC_AI_LocalMaterialRules UNION ALL
SELECT Rule, 'YieldType', 'YIELD_CSC_AI_PLACEMENT' FROM CSC_AI_LocalMaterialRules UNION ALL
SELECT Rule, 'Description', 'LOC_CSC_AI_PLACEMENT_NAME' FROM CSC_AI_LocalMaterialRules;
DROP TABLE CSC_AI_LocalMaterialRules;
