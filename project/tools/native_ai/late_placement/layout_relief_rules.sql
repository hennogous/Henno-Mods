-- Trial-only positive partner to no_base_city_rules.sql. The driver supplies
-- one private-yield weight for the replay. Each city attaches at most one
-- of these independently gated terrain records for each missing Quarter.
CREATE TEMP TABLE CSC_AI_Relief AS
SELECT m.ModifierId AS Original,
       'CSC_AI_PAIR_' || d.Value || '__R_' || t.Value AS Rule
FROM Modifiers m
JOIN ModifierArguments d ON d.ModifierId=m.ModifierId AND d.Name='DistrictType'
JOIN ModifierArguments t ON t.ModifierId=m.ModifierId AND t.Name='TerrainType'
WHERE m.ModifierType='MODIFIER_CSC_AI_NO_BASE_TERRAIN';
INSERT INTO Requirements (RequirementId,RequirementType)
SELECT Rule,'REQUIREMENT_PLOT_PROPERTY_MATCHES' FROM CSC_AI_Relief;
INSERT INTO RequirementArguments (RequirementId,Name,Value)
SELECT Rule,'PropertyName',Rule FROM CSC_AI_Relief UNION ALL
SELECT Rule,'PropertyMinimum',1 FROM CSC_AI_Relief;
INSERT INTO RequirementSets (RequirementSetId,RequirementSetType)
SELECT Rule,'REQUIREMENTSET_TEST_ALL' FROM CSC_AI_Relief;
INSERT INTO RequirementSetRequirements (RequirementSetId,RequirementId)
SELECT Rule,Rule FROM CSC_AI_Relief;
INSERT INTO Modifiers (ModifierId,ModifierType,SubjectRequirementSetId)
SELECT Rule,'MODIFIER_CSC_AI_NO_BASE_TERRAIN',Rule FROM CSC_AI_Relief;
INSERT INTO ModifierArguments (ModifierId,Name,Value)
SELECT r.Rule,a.Name,CASE WHEN a.Name='Amount' THEN w.Amount ELSE a.Value END
FROM CSC_AI_Relief r JOIN ModifierArguments a ON a.ModifierId=r.Original
CROSS JOIN CSC_AI_ReliefWeight w;
DROP TABLE CSC_AI_Relief;
DROP TABLE CSC_AI_ReliefWeight;
