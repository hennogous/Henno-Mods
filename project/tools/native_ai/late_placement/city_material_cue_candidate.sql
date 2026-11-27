-- Isolated Workshop-interface probe. The normal benchmark never attaches
-- these definitions. The probe attaches at most one to a disposable city.
-- Its city-center property lets us test both activation and withdrawal.
INSERT OR IGNORE INTO Types
        (   Type,   Kind   )
VALUES  (   'MODIFIER_CSC_AI_PROBE_CITY_TERRAIN',   'KIND_MODIFIER'   );

INSERT OR IGNORE INTO DynamicModifiers
        (   ModifierType,   CollectionType,   EffectType   )
VALUES  (   'MODIFIER_CSC_AI_PROBE_CITY_TERRAIN',   'COLLECTION_OWNER',   'EFFECT_TERRAIN_ADJACENCY'   );

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
VALUES  (   'REQ_CSC_AI_LOCAL_CUE_PROBE',   'REQUIREMENT_PLOT_PROPERTY_MATCHES'   );
INSERT OR IGNORE INTO RequirementArguments (RequirementId, Name, Value) VALUES
        ('REQ_CSC_AI_LOCAL_CUE_PROBE', 'PropertyName', 'CSC_AI_LOCAL_CUE_PROBE'),
        ('REQ_CSC_AI_LOCAL_CUE_PROBE', 'PropertyMinimum', 1);
INSERT OR IGNORE INTO RequirementSets (RequirementSetId, RequirementSetType)
VALUES ('REQSET_CSC_AI_LOCAL_CUE_PROBE', 'REQUIREMENTSET_TEST_ALL');
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId, RequirementId)
VALUES ('REQSET_CSC_AI_LOCAL_CUE_PROBE', 'REQ_CSC_AI_LOCAL_CUE_PROBE');

CREATE TEMP TABLE CSC_AI_ProbeCityRules AS
SELECT DISTINCT d.DistrictType AS Quarter, t.TerrainType AS Terrain,
       'MOD_CSC_AI_LOCAL_CUE_' || d.DistrictType || '__' || t.TerrainType AS ModifierId
FROM CSC_QuarterMaterialAdjacencyConfig m
JOIN Districts d ON d.DistrictType = 'DISTRICT_CSC_' || m.QuarterKey || '_QUARTER'
CROSS JOIN Terrains t
WHERE t.Water = 0 AND t.Impassable = 0;

INSERT OR IGNORE INTO Modifiers (ModifierId, ModifierType, SubjectRequirementSetId)
SELECT ModifierId, 'MODIFIER_CSC_AI_PROBE_CITY_TERRAIN', 'REQSET_CSC_AI_LOCAL_CUE_PROBE'
FROM CSC_AI_ProbeCityRules;
INSERT OR IGNORE INTO ModifierArguments (ModifierId, Name, Value)
SELECT ModifierId, 'DistrictType', Quarter FROM CSC_AI_ProbeCityRules UNION ALL
SELECT ModifierId, 'TerrainType', Terrain FROM CSC_AI_ProbeCityRules UNION ALL
SELECT ModifierId, 'YieldType', 'YIELD_CSC_AI_PLACEMENT' FROM CSC_AI_ProbeCityRules UNION ALL
SELECT ModifierId, 'Amount', 7 FROM CSC_AI_ProbeCityRules UNION ALL
SELECT ModifierId, 'Description', 'LOC_CSC_AI_PLACEMENT_NAME' FROM CSC_AI_ProbeCityRules;
-- Positive control isolates the city/terrain effect from its property gate.
INSERT OR IGNORE INTO Modifiers (ModifierId, ModifierType)
SELECT ModifierId || '_ALWAYS', 'MODIFIER_CSC_AI_PROBE_CITY_TERRAIN' FROM CSC_AI_ProbeCityRules;
INSERT OR IGNORE INTO ModifierArguments (ModifierId, Name, Value)
SELECT r.ModifierId || '_ALWAYS', a.Name, a.Value
FROM CSC_AI_ProbeCityRules r JOIN ModifierArguments a ON a.ModifierId = r.ModifierId;
-- One private point per complete group. The probe chooses the smallest
-- count that excludes every candidate lacking mapped Base in this city.
CREATE TEMP TABLE CSC_AI_ProbeCutoffs AS
WITH Counts(N) AS (VALUES (1),(2),(3),(4),(5),(6))
SELECT r.ModifierId, n.N, r.ModifierId || '_COUNT_' || n.N AS ThresholdId
FROM CSC_AI_ProbeCityRules r CROSS JOIN Counts n;
INSERT OR IGNORE INTO Modifiers (ModifierId, ModifierType)
SELECT ThresholdId, 'MODIFIER_CSC_AI_PROBE_CITY_TERRAIN' FROM CSC_AI_ProbeCutoffs;
INSERT OR IGNORE INTO ModifierArguments (ModifierId, Name, Value)
SELECT r.ThresholdId, a.Name, CASE WHEN a.Name = 'Amount' THEN '1' ELSE a.Value END
FROM CSC_AI_ProbeCutoffs r JOIN ModifierArguments a ON a.ModifierId = r.ModifierId
UNION ALL
SELECT ThresholdId, 'TilesRequired', N FROM CSC_AI_ProbeCutoffs;
DROP TABLE CSC_AI_ProbeCutoffs;
DROP TABLE CSC_AI_ProbeCityRules;
