-- DIAGNOSTIC ONLY. Farms on their actual resource get80 private planning units.
-- A flat Improvement_YieldChanges Farm row would reward terrain-only Farms and
-- could encourage harvesting a material before replacing its improvement. This
-- resource predicate instead uses Farm's native valid-resource vocabulary.
-- No Quarter adjacency/building/Service/strategy prerequisite: value potential
-- supply early. Existing Pasture/Camp/Plantation80 rows remain unchanged.
-- This modifier's projection into a future AI job is UNPROVEN until native logs.
INSERT OR IGNORE INTO Requirements
        (RequirementId, RequirementType)
SELECT 'REQ_CSC_AI_FARM_FORECAST_' || ResourceType,
       'REQUIREMENT_PLOT_RESOURCE_TYPE_MATCHES'
FROM Improvement_ValidResources WHERE ImprovementType='IMPROVEMENT_FARM';
INSERT OR IGNORE INTO RequirementArguments
        (RequirementId, Name, Value)
SELECT 'REQ_CSC_AI_FARM_FORECAST_' || ResourceType, 'ResourceType', ResourceType
FROM Improvement_ValidResources WHERE ImprovementType='IMPROVEMENT_FARM';
INSERT OR IGNORE INTO RequirementSets
        (RequirementSetId, RequirementSetType)
VALUES  ('REQSET_CSC_AI_FARM_RESOURCE_FORECAST', 'REQUIREMENTSET_TEST_ANY');
INSERT OR IGNORE INTO RequirementSetRequirements
        (RequirementSetId, RequirementId)
SELECT 'REQSET_CSC_AI_FARM_RESOURCE_FORECAST', 'REQ_CSC_AI_FARM_FORECAST_' || ResourceType
FROM Improvement_ValidResources WHERE ImprovementType='IMPROVEMENT_FARM';
INSERT OR IGNORE INTO Modifiers
        (ModifierId, ModifierType, OwnerRequirementSetId)
VALUES  ('MOD_CSC_AI_FARM_RESOURCE_FORECAST', 'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS', 'REQSET_CSC_AI_FARM_RESOURCE_FORECAST');
INSERT OR REPLACE INTO ModifierArguments
        (ModifierId, Name, Value)
VALUES  ('MOD_CSC_AI_FARM_RESOURCE_FORECAST', 'YieldType', 'YIELD_CSC_AI_PLACEMENT'),
        ('MOD_CSC_AI_FARM_RESOURCE_FORECAST', 'Amount', 80);
INSERT OR IGNORE INTO ImprovementModifiers
        (ImprovementType, ModifierId)
VALUES  ('IMPROVEMENT_FARM', 'MOD_CSC_AI_FARM_RESOURCE_FORECAST');
