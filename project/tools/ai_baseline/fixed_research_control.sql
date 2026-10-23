-- Disposable native research control; appended to installed CSC only during test.
-- Both arms disconnect the conditional preference route.
DELETE FROM Strategy_Priorities WHERE StrategyType LIKE 'STRATEGY_CSC_AI_SERVICE_%';
INSERT OR IGNORE INTO AiListTypes (ListType) VALUES ('CSC_AI_FIXED_SERVICE_CIVICS');
DELETE FROM AiFavoredItems WHERE ListType='CSC_AI_FIXED_SERVICE_CIVICS';
DELETE FROM AiLists WHERE ListType='CSC_AI_FIXED_SERVICE_CIVICS';
INSERT INTO AiLists (ListType,LeaderType,System)
 VALUES ('CSC_AI_FIXED_SERVICE_CIVICS','TRAIT_LEADER_MAJOR_CIV','Civics');
-- ON_ARM_ONLY
INSERT INTO AiFavoredItems (ListType,Item,Favored,Value)
 VALUES ('CSC_AI_FIXED_SERVICE_CIVICS','CIVIC_NAVAL_TRADITION',1,0);
