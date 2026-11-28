-- Use a fixed private river cue for Quarters whose own gameplay awards
-- Production from river crossings. Building-owned mill bonuses depend on
-- the Mill choice and are evaluated separately in the paired layout trial.
INSERT OR IGNORE INTO Adjacency_YieldChanges
        (ID, Description, YieldType, YieldChange, TilesRequired, AdjacentRiver)
VALUES  ('CSC_AI_TRIAL_RIVER', 'LOC_CSC_AI_PLACEMENT_NAME', 'YIELD_CSC_AI_PLACEMENT', 1, 1, 1);
INSERT OR IGNORE INTO District_Adjacencies (DistrictType, YieldChangeId)
SELECT DISTINCT DistrictType, 'CSC_AI_TRIAL_RIVER' FROM CSC_AdjacencyRules
WHERE AdjacencyType = 'FROM_RIVER_CROSSING' AND YieldType = 'YIELD_PRODUCTION'
  AND COALESCE(WhoIsTheOwner,'') = '';
