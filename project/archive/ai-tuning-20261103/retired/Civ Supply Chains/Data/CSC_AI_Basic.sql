-- CSC standalone baseline. This component is NEVER loaded with supported RH.
-- Shared Quarter/customer/resource guidance is in CSC_AI.sql. Generic weights,
-- Builder movement and native production-contract changes belong only here.
UPDATE CSC_AI_Profile SET Mode='BASIC' WHERE Id='ACTIVE';
DELETE FROM AiFavoredItems WHERE ListType='CSC_AI_ImprovementPriorities';
DELETE FROM AiLists WHERE ListType='CSC_AI_ImprovementPriorities';
DELETE FROM AiListTypes WHERE ListType='CSC_AI_ImprovementPriorities';
UPDATE PseudoYields SET DefaultValue=30
WHERE PseudoYieldType='PSEUDOYIELD_IMPROVEMENT';
INSERT INTO AiFavoredItems
        (   ListType,   Item,   Favored,   Value   )
SELECT 'UnitPriorityBoosts','UNIT_BUILDER',1,50
WHERE EXISTS (SELECT 1 FROM AiLists WHERE ListType='UnitPriorityBoosts' AND System='Units')
 AND NOT EXISTS (SELECT 1 FROM AiFavoredItems WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER');
UPDATE AiFavoredItems SET Favored=1,Value=50
WHERE ListType='UnitPriorityBoosts' AND Item='UNIT_BUILDER';

-- One additional movement point for major AI Builders. The owner gate excludes
-- humans; the subject gate excludes other units. RH supplies its own movement
-- policy, so its compatibility path never attaches this modifier.
INSERT OR IGNORE INTO Requirements
        (   RequirementId,                RequirementType   )
VALUES  (   'REQ_CSC_AI_BASIC_BUILDER',   'REQUIREMENT_UNIT_TYPE_MATCHES'   );
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,                Name,         Value   )
VALUES  (   'REQ_CSC_AI_BASIC_BUILDER',   'UnitType',   'UNIT_BUILDER'   );
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,                RequirementSetType   )
VALUES  (   'REQSET_CSC_AI_BASIC_BUILDER',   'REQUIREMENTSET_TEST_ALL'   );
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,                RequirementId   )
VALUES  (   'REQSET_CSC_AI_BASIC_BUILDER',   'REQ_CSC_AI_BASIC_BUILDER'   );
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                            ModifierType,                              OwnerRequirementSetId,       SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_AI_BASIC_BUILDER_MOVEMENT',   'MODIFIER_PLAYER_UNITS_ADJUST_MOVEMENT',   'REQSET_CSC_AI_SUPPLY_AI',   'REQSET_CSC_AI_BASIC_BUILDER'   );
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                            Name,       Value   )
VALUES  (   'MOD_CSC_AI_BASIC_BUILDER_MOVEMENT',   'Amount',   1   );
INSERT OR IGNORE INTO TraitModifiers
        (   TraitType,                  ModifierId   )
VALUES  (   'TRAIT_LEADER_MAJOR_CIV',   'MOD_CSC_AI_BASIC_BUILDER_MOVEMENT'   );

-- Native documented Required City=-1: a production contract may find a Builder
-- in another city. Select by node type rather than assuming immutable node IDs.
-- This is not a direct unit assignment or a guarantee that a unit can reach it.
INSERT INTO TreeData
        (   DefnId,   NodeId,   TreeName,   DefaultData   )
SELECT 2,n.NodeId,n.TreeName,'-1' FROM BehaviorTreeNodes n
WHERE n.TreeName='Build City Improvement' AND n.NodeType='Build Unit'
 AND NOT EXISTS (SELECT 1 FROM TreeData t WHERE t.TreeName=n.TreeName
                 AND t.NodeId=n.NodeId AND t.DefnId=2);
UPDATE TreeData SET DefaultData='-1'
WHERE DefnId=2 AND TreeName='Build City Improvement'
 AND NodeId IN (SELECT NodeId FROM BehaviorTreeNodes
                WHERE TreeName='Build City Improvement' AND NodeType='Build Unit');
