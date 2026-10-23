-- Experimental material care v2: native preferences, never Builder orders.
-- Lua identifies exact owned, revealed supplies beside Bakers/Tailors foundations
-- or completed Quarters. A raw-material signal remains while pillaged; the
-- existing improvement-owned +80 remains the separate development/repair payoff.
-- These amounts are private planning values, not real economic yields.
CREATE TABLE IF NOT EXISTS CSC_AI_MaterialCareSignals (
    Name TEXT PRIMARY KEY, Amount INTEGER NOT NULL
);
INSERT OR REPLACE INTO CSC_AI_MaterialCareSignals
        (   Name,          Amount   )
VALUES  (   'LAST_BASE',   160   ),
        (   'LAST_SPEC',   80   ),
        (   'REDUNDANT',   20   );
INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT 'REQ_CSC_AI_CARE_' || Name, 'REQUIREMENT_PLOT_PROPERTY_MATCHES'
FROM CSC_AI_MaterialCareSignals;
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_AI_CARE_' || Name, 'PropertyName', 'CSC_AI_CARE_' || Name
FROM CSC_AI_MaterialCareSignals
UNION ALL
SELECT 'REQ_CSC_AI_CARE_' || Name, 'PropertyMinimum', 1
FROM CSC_AI_MaterialCareSignals;
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_AI_CARE_' || Name, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_AI_MaterialCareSignals;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_AI_CARE_' || Name, 'REQ_CSC_AI_CARE_' || Name
FROM CSC_AI_MaterialCareSignals;
-- Lua marks choose last/redundant supply, but native predicates own tile-state
-- validity. A stale mark must not preserve value on a removed resource or a
-- district tile. This also exposes those conditions to native hypothetical
-- evaluations; whether the district planner prices that loss remains unproven.
INSERT OR IGNORE INTO RequirementSets
        (RequirementSetId, RequirementSetType)
VALUES ('REQSET_CSC_AI_CARE_RESOURCE', 'REQUIREMENTSET_TEST_ANY');
INSERT OR IGNORE INTO Requirements (RequirementId, RequirementType)
SELECT DISTINCT 'REQ_CSC_AI_CARE_RESOURCE_' || r.ResourceType,
       'REQUIREMENT_PLOT_RESOURCE_TYPE_MATCHES'
FROM Resources r JOIN TypeTags t ON t.Type=r.ResourceType
WHERE t.Tag IN ('CLASS_CSC_BAKERS_BASE','CLASS_CSC_BAKERS_SPEC',
                'CLASS_CSC_TAILORS_BASE','CLASS_CSC_TAILORS_SPEC');
INSERT OR IGNORE INTO RequirementArguments (RequirementId, Name, Value)
SELECT DISTINCT 'REQ_CSC_AI_CARE_RESOURCE_' || r.ResourceType,
       'ResourceType', r.ResourceType
FROM Resources r JOIN TypeTags t ON t.Type=r.ResourceType
WHERE t.Tag IN ('CLASS_CSC_BAKERS_BASE','CLASS_CSC_BAKERS_SPEC',
                'CLASS_CSC_TAILORS_BASE','CLASS_CSC_TAILORS_SPEC');
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId, RequirementId)
SELECT DISTINCT 'REQSET_CSC_AI_CARE_RESOURCE', 'REQ_CSC_AI_CARE_RESOURCE_' || r.ResourceType
FROM Resources r JOIN TypeTags t ON t.Type=r.ResourceType
WHERE t.Tag IN ('CLASS_CSC_BAKERS_BASE','CLASS_CSC_BAKERS_SPEC',
                'CLASS_CSC_TAILORS_BASE','CLASS_CSC_TAILORS_SPEC');
INSERT OR IGNORE INTO Requirements (RequirementId, RequirementType, Inverse)
VALUES ('REQ_CSC_AI_CARE_RESOURCE_PRESENT','REQUIREMENT_REQUIREMENTSET_IS_MET',0),
       ('REQ_CSC_AI_CARE_NO_DISTRICT','REQUIREMENT_PLOT_HAS_ANY_DISTRICT',1);
INSERT OR IGNORE INTO RequirementArguments (RequirementId, Name, Value)
VALUES ('REQ_CSC_AI_CARE_RESOURCE_PRESENT','RequirementSetId','REQSET_CSC_AI_CARE_RESOURCE');
INSERT OR IGNORE INTO RequirementSetRequirements (RequirementSetId, RequirementId)
SELECT 'REQSET_CSC_AI_CARE_' || Name, 'REQ_CSC_AI_CARE_RESOURCE_PRESENT'
FROM CSC_AI_MaterialCareSignals
UNION ALL
SELECT 'REQSET_CSC_AI_CARE_' || Name, 'REQ_CSC_AI_CARE_NO_DISTRICT'
FROM CSC_AI_MaterialCareSignals;
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_AI_CARE_' || Name, 'MODIFIER_PLAYER_ADJUST_PLOT_YIELD',
       'REQSET_CSC_AI_SUPPLY_AI', 'REQSET_CSC_AI_CARE_' || Name
FROM CSC_AI_MaterialCareSignals;
INSERT OR REPLACE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_AI_CARE_' || Name, 'YieldType', 'YIELD_CSC_AI_PLACEMENT'
FROM CSC_AI_MaterialCareSignals
UNION ALL
SELECT 'MOD_CSC_AI_CARE_' || Name, 'Amount', Amount
FROM CSC_AI_MaterialCareSignals;
INSERT OR IGNORE INTO TraitModifiers
        (   TraitType,                ModifierId   )
SELECT 'TRAIT_LEADER_MAJOR_CIV', 'MOD_CSC_AI_CARE_' || Name
FROM CSC_AI_MaterialCareSignals;

-- State-sensitive WORK demand, separately from Builder production. The stopped
-- pilot had many Builders while native jobs failed to find an available unit or
-- move one. Empire-wide charges are not job availability. Lua activates this only
-- for a sustained, presently actionable material backlog; unsafe, locked and
-- unknown-legality tiles do not qualify. +100% temporarily makes base30 reach60,
-- below the previous blanket90. It is player-wide, not a plot-specific contract
-- or a guaranteed repair forecast. The general Builder preference50 is unchanged.
INSERT OR IGNORE INTO Types
        (   Type,                                Kind   )
VALUES  (   'STRATEGY_CSC_AI_MATERIAL_BACKLOG',   'KIND_VICTORY_STRATEGY'   );
INSERT OR IGNORE INTO Strategies
        (   StrategyType,                        VictoryType,   NumConditionsNeeded   )
VALUES  (   'STRATEGY_CSC_AI_MATERIAL_BACKLOG',   NULL,          1   );
DELETE FROM StrategyConditions
WHERE StrategyType='STRATEGY_CSC_AI_MATERIAL_BACKLOG'
  AND ConditionFunction IN ('Call Lua Function', 'Is Not Major');
INSERT INTO StrategyConditions
        (   StrategyType,                        ConditionFunction,    StringValue,                   ThresholdValue   )
VALUES  (   'STRATEGY_CSC_AI_MATERIAL_BACKLOG',   'Call Lua Function',   'CSC_AI_MaterialWorkReady',   1   );
-- Retire the capacity-only condition on replay; otherwise either old or new
-- callback could activate this strategy because NumConditionsNeeded is one.
DELETE FROM StrategyConditions
WHERE StrategyType='STRATEGY_CSC_AI_MATERIAL_BACKLOG'
  AND ConditionFunction='Call Lua Function' AND StringValue='CSC_AI_MaterialCareShortage';
INSERT OR IGNORE INTO StrategyConditions
        (   StrategyType,                        ConditionFunction,   Disqualifier   )
VALUES  (   'STRATEGY_CSC_AI_MATERIAL_BACKLOG',   'Is Not Major',      1   );
INSERT OR IGNORE INTO AiListTypes
        (   ListType   )
VALUES  (   'CSC_AI_MATERIAL_BACKLOG_UNITS'   ),
        (   'CSC_AI_MATERIAL_BACKLOG_PSEUDOS'   );
-- Native AiLists/AiFavoredItems do not uniquely key every authored field.
-- Remove only this candidate's list rows so SQL replay cannot duplicate demand.
DELETE FROM AiFavoredItems WHERE ListType IN ('CSC_AI_MATERIAL_BACKLOG_UNITS', 'CSC_AI_MATERIAL_BACKLOG_PSEUDOS');
DELETE FROM AiLists WHERE ListType IN ('CSC_AI_MATERIAL_BACKLOG_UNITS', 'CSC_AI_MATERIAL_BACKLOG_PSEUDOS');
INSERT OR IGNORE INTO AiLists
        (   ListType,                            System   )
VALUES  (   'CSC_AI_MATERIAL_BACKLOG_UNITS',     'Units'   ),
        (   'CSC_AI_MATERIAL_BACKLOG_PSEUDOS',   'PseudoYields'   );
DELETE FROM Strategy_Priorities WHERE StrategyType='STRATEGY_CSC_AI_MATERIAL_BACKLOG';
INSERT INTO Strategy_Priorities
        (   StrategyType,   ListType   )
SELECT 'STRATEGY_CSC_AI_MATERIAL_BACKLOG', ListType FROM AiLists
WHERE ListType='CSC_AI_MATERIAL_BACKLOG_PSEUDOS';
-- No extra Builder-production bias in v2. Keep the old list declaration empty
-- for safe SQL replay, and explicitly remove its former strategy attachment.
DELETE FROM Strategy_Priorities
WHERE StrategyType='STRATEGY_CSC_AI_MATERIAL_BACKLOG'
  AND ListType='CSC_AI_MATERIAL_BACKLOG_UNITS';
INSERT OR REPLACE INTO AiFavoredItems
        (   ListType,                            Item,                         Favored,   Value   )
VALUES  (   'CSC_AI_MATERIAL_BACKLOG_PSEUDOS',   'PSEUDOYIELD_IMPROVEMENT',     1,         100   );

-- AI+ production-contract flexibility: Required City=-1 lets native production
-- find a Builder elsewhere. It does not assign a Builder, perform a repair,
-- remove costs, or alter the separate native improvement-job selection nodes.
INSERT INTO TreeData
        (   DefnId,   NodeId,   TreeName,                  DefaultData   )
SELECT 2, 13, 'Build City Improvement', '-1'
WHERE NOT EXISTS (SELECT 1 FROM TreeData WHERE DefnId=2 AND NodeId=13 AND TreeName='Build City Improvement');
INSERT INTO TreeData
        (   DefnId,   NodeId,   TreeName,                  DefaultData   )
SELECT 2, 23, 'Build City Improvement', '-1'
WHERE NOT EXISTS (SELECT 1 FROM TreeData WHERE DefnId=2 AND NodeId=23 AND TreeName='Build City Improvement');
UPDATE TreeData SET DefaultData='-1'
WHERE DefnId=2 AND NodeId IN (13,23) AND TreeName='Build City Improvement';
