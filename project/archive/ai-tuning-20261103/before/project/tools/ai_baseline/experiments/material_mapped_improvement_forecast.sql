-- DIAGNOSTIC: complete the early improvement incentive for every currently
-- mapped Bakers/Tailors material, including enabled compatibility resources.
-- Resolve BOTH the live CSC tags and native Improvement_ValidResources: a
-- resource name alone never authorizes an improvement or creates a mapping.
-- Preserve the tested direct Pasture/Camp/Plantation80 and resource-Farm80
-- paths. Add conditional80 only for uncovered native improvement/resource pairs.
-- In the current build these are Salt/Silver Mines. No blanket Mine bonus:
-- terrain-only Mines and unrelated resources receive no new incentive.
-- Existing adjacent-Quarter improvement80, presence40 and material care remain
-- additive and unchanged. These are private planning units, not economic yields.
-- Like the existing early diagnostic, the new signal is all-owner; native
-- hypothetical job consumption/citizen spillover need independent observation.

DELETE FROM ImprovementModifiers WHERE ModifierId GLOB 'MOD_CSC_AI_MAPPED_IMPROVEMENT_*';
DELETE FROM ModifierArguments WHERE ModifierId GLOB 'MOD_CSC_AI_MAPPED_IMPROVEMENT_*';
DELETE FROM Modifiers WHERE ModifierId GLOB 'MOD_CSC_AI_MAPPED_IMPROVEMENT_*';
DELETE FROM RequirementSetRequirements WHERE RequirementSetId GLOB 'REQSET_CSC_AI_MAPPED_IMPROVEMENT_*';
DELETE FROM RequirementSets WHERE RequirementSetId GLOB 'REQSET_CSC_AI_MAPPED_IMPROVEMENT_*';
DELETE FROM RequirementArguments WHERE RequirementId GLOB 'REQ_CSC_AI_MAPPED_IMPROVEMENT_*';
DELETE FROM Requirements WHERE RequirementId GLOB 'REQ_CSC_AI_MAPPED_IMPROVEMENT_*';

CREATE TEMP TABLE CSC_AI_MappedImprovementForecast (
    ImprovementType TEXT NOT NULL,
    ResourceType TEXT NOT NULL,
    PRIMARY KEY (ImprovementType, ResourceType)
);
INSERT OR IGNORE INTO CSC_AI_MappedImprovementForecast
        (   ImprovementType,   ResourceType   )
SELECT v.ImprovementType, v.ResourceType
FROM Improvement_ValidResources v
JOIN Resources r ON r.ResourceType=v.ResourceType
JOIN TypeTags t ON t.Type=r.ResourceType
WHERE t.Tag IN ('CLASS_CSC_BAKERS_BASE', 'CLASS_CSC_BAKERS_SPEC',
                'CLASS_CSC_TAILORS_BASE', 'CLASS_CSC_TAILORS_SPEC')
  AND NOT EXISTS (
      SELECT 1 FROM Improvement_YieldChanges y
      WHERE y.ImprovementType=v.ImprovementType
        AND y.YieldType='YIELD_CSC_AI_PLACEMENT' AND y.YieldChange=80
  )
  AND NOT EXISTS (
      SELECT 1 FROM ImprovementModifiers i
      JOIN Modifiers m ON m.ModifierId=i.ModifierId
      JOIN RequirementSetRequirements s ON s.RequirementSetId=m.OwnerRequirementSetId
      JOIN RequirementArguments a ON a.RequirementId=s.RequirementId
      WHERE i.ImprovementType=v.ImprovementType
        AND i.ModifierId='MOD_CSC_AI_FARM_RESOURCE_FORECAST'
        AND a.Name='ResourceType' AND a.Value=v.ResourceType
  );

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT DISTINCT 'REQ_CSC_AI_MAPPED_IMPROVEMENT_' || ResourceType,
       'REQUIREMENT_PLOT_RESOURCE_TYPE_MATCHES'
FROM CSC_AI_MappedImprovementForecast;
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT DISTINCT 'REQ_CSC_AI_MAPPED_IMPROVEMENT_' || ResourceType, 'ResourceType', ResourceType
FROM CSC_AI_MappedImprovementForecast;
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT DISTINCT 'REQSET_CSC_AI_MAPPED_IMPROVEMENT_' || ImprovementType, 'REQUIREMENTSET_TEST_ANY'
FROM CSC_AI_MappedImprovementForecast;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_AI_MAPPED_IMPROVEMENT_' || ImprovementType,
       'REQ_CSC_AI_MAPPED_IMPROVEMENT_' || ResourceType
FROM CSC_AI_MappedImprovementForecast;
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId   )
SELECT DISTINCT 'MOD_CSC_AI_MAPPED_IMPROVEMENT_' || ImprovementType,
       'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',
       'REQSET_CSC_AI_MAPPED_IMPROVEMENT_' || ImprovementType
FROM CSC_AI_MappedImprovementForecast;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT DISTINCT 'MOD_CSC_AI_MAPPED_IMPROVEMENT_' || ImprovementType, 'YieldType', 'YIELD_CSC_AI_PLACEMENT'
FROM CSC_AI_MappedImprovementForecast
UNION ALL
SELECT DISTINCT 'MOD_CSC_AI_MAPPED_IMPROVEMENT_' || ImprovementType, 'Amount', '80'
FROM CSC_AI_MappedImprovementForecast;
INSERT OR IGNORE INTO ImprovementModifiers
        (   ImprovementType,   ModifierId   )
SELECT DISTINCT ImprovementType, 'MOD_CSC_AI_MAPPED_IMPROVEMENT_' || ImprovementType
FROM CSC_AI_MappedImprovementForecast;
DROP TABLE CSC_AI_MappedImprovementForecast;
