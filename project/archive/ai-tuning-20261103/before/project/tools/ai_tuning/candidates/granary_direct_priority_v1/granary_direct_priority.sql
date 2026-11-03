-- Experimental direct Buildings preference, NOT a conditional/player-local rule.
-- The reviewed native CityPlanner loader resolves AiLists.LeaderType as a trait.
-- This binding persists for any player with Genghis Khan's ability trait while
-- these candidate rows are loaded; original-human exclusion is NOT a SQL gate.
-- Favored=1 adds one signed contribution. Value=0 is metadata, not a yield/score.
-- Preserve all RH, old strategy, private40, economy and production-order rows.
INSERT OR IGNORE INTO AiListTypes
        (   ListType   )
SELECT 'CSC_AI_GranaryDirectPriority_V1'
WHERE EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH')
  AND EXISTS (SELECT 1 FROM Traits WHERE TraitType='TRAIT_LEADER_GENGHIS_KHAN_ABILITY')
  AND EXISTS (SELECT 1 FROM LeaderTraits WHERE LeaderType='LEADER_GENGHIS_KHAN' AND TraitType='TRAIT_LEADER_GENGHIS_KHAN_ABILITY');

INSERT OR IGNORE INTO AiLists
        (   ListType,   LeaderType,   System   )
SELECT 'CSC_AI_GranaryDirectPriority_V1', 'TRAIT_LEADER_GENGHIS_KHAN_ABILITY', 'Buildings'
WHERE EXISTS (SELECT 1 FROM AiListTypes WHERE ListType='CSC_AI_GranaryDirectPriority_V1')
  AND EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH')
  AND EXISTS (SELECT 1 FROM LeaderTraits WHERE LeaderType='LEADER_GENGHIS_KHAN' AND TraitType='TRAIT_LEADER_GENGHIS_KHAN_ABILITY')
  AND NOT EXISTS (SELECT 1 FROM AiLists WHERE ListType='CSC_AI_GranaryDirectPriority_V1');

INSERT OR IGNORE INTO AiFavoredItems
        (   ListType,   Item,   Favored,   Value   )
SELECT 'CSC_AI_GranaryDirectPriority_V1', 'BUILDING_GRANARY', 1, 0
WHERE EXISTS (SELECT 1 FROM AiLists WHERE ListType='CSC_AI_GranaryDirectPriority_V1' AND LeaderType='TRAIT_LEADER_GENGHIS_KHAN_ABILITY' AND System='Buildings')
  AND EXISTS (SELECT 1 FROM CSC_AI_Profile WHERE Id='ACTIVE' AND Mode='RH')
  AND NOT EXISTS (SELECT 1 FROM AiFavoredItems WHERE ListType='CSC_AI_GranaryDirectPriority_V1' AND Item='BUILDING_GRANARY');
