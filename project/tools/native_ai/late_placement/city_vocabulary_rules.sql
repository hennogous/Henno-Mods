-- Experimental no-CE placement. Each city-center property activates one
-- signed private-yield rule for one missing Quarter. Static resource-class
-- and named customer adjacencies continue to come from the shipping SQL.
CREATE TEMP TABLE CSC_VocabKinds(Kind TEXT PRIMARY KEY, Argument TEXT);
INSERT INTO CSC_VocabKinds VALUES
    ('TERRAIN','TerrainType'),('FEATURE','FeatureType'),('IMPROVEMENT','ImprovementType'),
    ('DISTRICT',NULL),('RIVER',NULL);
INSERT OR IGNORE INTO Types(Type,Kind)
SELECT 'MODIFIER_CSC_VOC_' || Kind,'KIND_MODIFIER' FROM CSC_VocabKinds;
INSERT INTO DynamicModifiers(ModifierType,CollectionType,EffectType)
SELECT 'MODIFIER_CSC_VOC_' || Kind,'COLLECTION_OWNER','EFFECT_' || Kind || '_ADJACENCY'
FROM CSC_VocabKinds;

CREATE TEMP TABLE CSC_VocabRules AS
WITH Quarters(District) AS (
    SELECT DISTINCT 'DISTRICT_CSC_' || QuarterKey || '_QUARTER'
    FROM CSC_QuarterMaterialAdjacencyConfig
    WHERE SourceTag='CLASS_CSC_' || QuarterKey || '_BASE' AND SourceFilter=''
      AND AdjacencyType='FROM_RINGS_TYPETAG_RESOURCE'
), Clues(Kind,Clue) AS (
    SELECT 'TERRAIN', TerrainType FROM Terrains UNION ALL
    SELECT 'FEATURE', FeatureType FROM Features UNION ALL
    SELECT 'IMPROVEMENT', ImprovementType FROM Improvements UNION ALL
    SELECT 'DISTRICT','ANY_DISTRICT' UNION ALL SELECT 'RIVER','RIVER'
), Signs(Sign,Amount) AS (VALUES ('P',6),('N',-6),('F',-1),('U',5),('D',-7))
SELECT 'CSC_AI_VOC_' || District || '__' || Sign || '_' || Clue AS Rule,
       District, Kind, Argument, Clue, Amount
FROM Quarters CROSS JOIN Clues JOIN CSC_VocabKinds USING(Kind) CROSS JOIN Signs
WHERE Sign IN ('P','N') OR Kind='TERRAIN';
INSERT INTO Requirements(RequirementId,RequirementType)
SELECT Rule,'REQUIREMENT_PLOT_PROPERTY_MATCHES' FROM CSC_VocabRules;
INSERT INTO RequirementArguments(RequirementId,Name,Value)
SELECT Rule,'PropertyName',Rule FROM CSC_VocabRules UNION ALL
SELECT Rule,'PropertyMinimum',1 FROM CSC_VocabRules;
INSERT INTO RequirementSets(RequirementSetId,RequirementSetType)
SELECT Rule,'REQUIREMENTSET_TEST_ALL' FROM CSC_VocabRules;
INSERT INTO RequirementSetRequirements(RequirementSetId,RequirementId)
SELECT Rule,Rule FROM CSC_VocabRules;
INSERT INTO Modifiers(ModifierId,ModifierType,SubjectRequirementSetId)
SELECT Rule,'MODIFIER_CSC_VOC_' || Kind,Rule FROM CSC_VocabRules;
INSERT INTO ModifierArguments(ModifierId,Name,Value)
SELECT Rule,'DistrictType',District FROM CSC_VocabRules UNION ALL
SELECT Rule,'YieldType','YIELD_CSC_AI_PLACEMENT' FROM CSC_VocabRules UNION ALL
SELECT Rule,'Description','LOC_CSC_AI_PLACEMENT_NAME' FROM CSC_VocabRules UNION ALL
SELECT Rule,'Amount',Amount FROM CSC_VocabRules UNION ALL
SELECT Rule,Argument,Clue FROM CSC_VocabRules WHERE Argument IS NOT NULL;
DROP TABLE CSC_VocabRules;
DROP TABLE CSC_VocabKinds;
