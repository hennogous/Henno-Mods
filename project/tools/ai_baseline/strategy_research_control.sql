-- Disposable common control. Never shipped as CSC gameplay.
-- Remove the research lists themselves, not merely their strategy links.
DELETE FROM AiFavoredItems WHERE ListType LIKE 'CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_FIXED_SERVICE_%' OR ListType='CSC_TEST_RESEARCH_LIST';
DELETE FROM Strategy_Priorities WHERE StrategyType LIKE 'STRATEGY_CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_FIXED_SERVICE_%' OR ListType='CSC_TEST_RESEARCH_LIST';
DELETE FROM AiLists WHERE ListType LIKE 'CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_FIXED_SERVICE_%' OR ListType='CSC_TEST_RESEARCH_LIST';
DELETE FROM AiListTypes WHERE ListType LIKE 'CSC_AI_SERVICE_%' OR ListType LIKE 'CSC_AI_FIXED_SERVICE_%' OR ListType='CSC_TEST_RESEARCH_LIST';

INSERT OR IGNORE INTO Types (Type,Kind) VALUES ('STRATEGY_CSC_TEST_RESEARCH','KIND_VICTORY_STRATEGY');
INSERT OR IGNORE INTO Strategies (StrategyType,VictoryType,NumConditionsNeeded) VALUES ('STRATEGY_CSC_TEST_RESEARCH',NULL,1);
UPDATE Strategies SET NumConditionsNeeded=1 WHERE StrategyType IN ('STRATEGY_NAVAL','STRATEGY_CSC_TEST_RESEARCH');
DELETE FROM StrategyConditions WHERE StrategyType IN ('STRATEGY_NAVAL','STRATEGY_CSC_TEST_RESEARCH');
INSERT INTO StrategyConditions (StrategyType,ConditionFunction,StringValue,ThresholdValue) VALUES
 ('STRATEGY_NAVAL','Call Lua Function','CSC_TestResearchAlways',1),
 ('STRATEGY_CSC_TEST_RESEARCH','Call Lua Function','CSC_TestResearchAlways',2);
-- Both strategies have identical activation in all arms. Existing unrelated
-- stock Naval lists remain identical. Python appends a list ONLY for treatments.
