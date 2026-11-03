-- Experimental append-only payload; NOT shipping content or a default option.
-- One local reviewed customer gap gates a PLAYER-WIDE Granary type preference.
-- Favored=true adds one signed preference contribution. Value=0 is metadata,
-- not a yield or proportional score. Existing private40/RH/Quarter rows stay as-is.
-- The default-nil private flag and all physical/role gates belong to the Lua
-- callback. Native callback truth, strategy adoption, preference and completion
-- are separate evidence; native strategy removal can lag a false predicate.
INSERT OR IGNORE INTO Types
        (   Type,   Kind   )
SELECT      'STRATEGY_CSC_AI_GRANARY_PRIORITY_V1',  'KIND_VICTORY_STRATEGY'
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH');

INSERT OR IGNORE INTO Strategies
        (   StrategyType,   VictoryType,   NumConditionsNeeded   )
SELECT      'STRATEGY_CSC_AI_GRANARY_PRIORITY_V1',  NULL,          1
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH');

INSERT OR IGNORE INTO StrategyConditions
        (   StrategyType,   ConditionFunction,   Disqualifier   )
SELECT      'STRATEGY_CSC_AI_GRANARY_PRIORITY_V1',  'Is Not Major',      1
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH')
  AND NOT EXISTS (SELECT 1 FROM StrategyConditions WHERE StrategyType='STRATEGY_CSC_AI_GRANARY_PRIORITY_V1' AND ConditionFunction='Is Not Major');

INSERT OR IGNORE INTO StrategyConditions
        (   StrategyType,   ConditionFunction,   StringValue,   ThresholdValue   )
SELECT      'STRATEGY_CSC_AI_GRANARY_PRIORITY_V1',  'Call Lua Function',  'CSC_AI_GranaryPriority_V1',   0
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH')
  AND NOT EXISTS (SELECT 1 FROM StrategyConditions WHERE StrategyType='STRATEGY_CSC_AI_GRANARY_PRIORITY_V1' AND ConditionFunction='Call Lua Function');

INSERT OR IGNORE INTO AiListTypes
        (   ListType   )
SELECT      'CSC_AI_GranaryPriority_V1'
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH');

INSERT OR IGNORE INTO AiLists
        (   ListType,   System   )
SELECT      'CSC_AI_GranaryPriority_V1',  'Buildings'
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH')
  AND NOT EXISTS (SELECT 1 FROM AiLists WHERE ListType='CSC_AI_GranaryPriority_V1');

INSERT OR IGNORE INTO Strategy_Priorities
        (   StrategyType,   ListType   )
SELECT      'STRATEGY_CSC_AI_GRANARY_PRIORITY_V1',  'CSC_AI_GranaryPriority_V1'
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH')
  AND NOT EXISTS (SELECT 1 FROM Strategy_Priorities WHERE StrategyType='STRATEGY_CSC_AI_GRANARY_PRIORITY_V1' AND ListType='CSC_AI_GranaryPriority_V1');

INSERT OR IGNORE INTO AiFavoredItems
        (   ListType,   Item,   Favored,   Value   )
SELECT      'CSC_AI_GranaryPriority_V1',  'BUILDING_GRANARY',    1,         0
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH')
  AND NOT EXISTS (SELECT 1 FROM AiFavoredItems WHERE ListType='CSC_AI_GranaryPriority_V1' AND Item='BUILDING_GRANARY');
