-- Experimental stock city adjacency. The lightweight city review opens one
-- center-plot gate per missing Quarter with no prospective Base supplier.
-- Civ consumes the rule on its own district comparison; real payouts use
-- the separate gameplay adjacency definitions.
INSERT OR IGNORE INTO Types (Type, Kind)
VALUES ('MODIFIER_CSC_AI_NO_BASE_TERRAIN', 'KIND_MODIFIER');
INSERT OR IGNORE INTO DynamicModifiers (ModifierType, CollectionType, EffectType)
VALUES ('MODIFIER_CSC_AI_NO_BASE_TERRAIN', 'COLLECTION_OWNER', 'EFFECT_TERRAIN_ADJACENCY');

CREATE TEMP TABLE CSC_AI_NoBaseRules AS
SELECT DISTINCT q.DistrictType AS Quarter, t.TerrainType AS Terrain,
       'CSC_AI_NO_BASE_' || q.DistrictType AS Gate,
       'CSC_AI_NO_BASE_' || q.DistrictType || '__' || t.TerrainType AS Rule
FROM CSC_QuarterMaterialAdjacencyConfig m
JOIN Districts q ON q.DistrictType = 'DISTRICT_CSC_' || m.QuarterKey || '_QUARTER'
CROSS JOIN Terrains t
WHERE m.SourceTag = 'CLASS_CSC_' || m.QuarterKey || '_BASE'
  AND m.SourceFilter = '' AND m.AdjacencyType = 'FROM_RINGS_TYPETAG_RESOURCE';

INSERT OR IGNORE INTO Requirements (RequirementId, RequirementType)
SELECT DISTINCT Gate, 'REQUIREMENT_PLOT_PROPERTY_MATCHES' FROM CSC_AI_NoBaseRules;
INSERT OR IGNORE INTO RequirementArguments (RequirementId, Name, Value)
SELECT DISTINCT Gate, 'PropertyName', Gate FROM CSC_AI_NoBaseRules UNION ALL
SELECT DISTINCT Gate, 'PropertyMinimum', 1 FROM CSC_AI_NoBaseRules;
INSERT OR IGNORE INTO RequirementSets (RequirementSetId, RequirementSetType)
SELECT DISTINCT Gate, 'REQUIREMENTSET_TEST_ALL' FROM CSC_AI_NoBaseRules;
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId, RequirementId)
SELECT DISTINCT Gate, Gate FROM CSC_AI_NoBaseRules;
INSERT OR IGNORE INTO Modifiers (ModifierId, ModifierType, SubjectRequirementSetId)
SELECT Rule, 'MODIFIER_CSC_AI_NO_BASE_TERRAIN', Gate FROM CSC_AI_NoBaseRules;
-- Each neighbor contributes once, across all terrain types. The proposed
-- discouragement is six private yield units on a six-neighbor site.
INSERT OR IGNORE INTO ModifierArguments (ModifierId, Name, Value)
SELECT Rule, 'DistrictType', Quarter FROM CSC_AI_NoBaseRules UNION ALL
SELECT Rule, 'TerrainType', Terrain FROM CSC_AI_NoBaseRules UNION ALL
SELECT Rule, 'TilesRequired', 1 FROM CSC_AI_NoBaseRules UNION ALL
SELECT Rule, 'Amount', -1 FROM CSC_AI_NoBaseRules UNION ALL
SELECT Rule, 'YieldType', 'YIELD_CSC_AI_PLACEMENT' FROM CSC_AI_NoBaseRules UNION ALL
SELECT Rule, 'Description', 'LOC_CSC_AI_PLACEMENT_NAME' FROM CSC_AI_NoBaseRules;
DROP TABLE CSC_AI_NoBaseRules;
