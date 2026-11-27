-- Controlled stock-AI experiment. A supplied Bakers beside a City Center
-- can still lack a Granary. Test whether ordinary early customer buildings
-- can close that gap through the same Buildings list Civ uses for Wonders.
-- The preference applies across a major leader's cities, so compare actual
-- Service activity and competing production before adopting it. The native
-- selector uses the accumulated Favored sign (+ = 2x in the traced branch).
-- Its Value field cannot provide a smaller percentage in this comparison.
INSERT OR IGNORE INTO AiListTypes
        (   ListType   )
VALUES  (   'CSC_AI_FIRST_CUSTOMER_BUILDINGS'   );

INSERT INTO AiLists
        (   ListType,   LeaderType,   System   )
SELECT 'CSC_AI_FIRST_CUSTOMER_BUILDINGS', 'TRAIT_LEADER_MAJOR_CIV', 'Buildings'
WHERE NOT EXISTS (
    SELECT 1 FROM AiLists WHERE ListType = 'CSC_AI_FIRST_CUSTOMER_BUILDINGS'
);

-- Generate the first customer investment for each implemented Quarter. A
-- building may serve multiple industries but gets one preference vote. Use
-- the loaded replacement family so unique customers receive the same vote.
WITH RECURSIVE Customer(BuildingType) AS (
    SELECT c.BuildingType
    FROM CSC_QuarterCustomerBuildings c
    JOIN Buildings b ON b.BuildingType = c.BuildingType
    WHERE c.ProducerStage = 2 AND b.IsWonder = 0
    UNION
    SELECT r.CivUniqueBuildingType
    FROM BuildingReplaces r JOIN Customer c ON r.ReplacesBuildingType = c.BuildingType
)
INSERT INTO AiFavoredItems
        (   ListType,   Item,   Favored,   Value   )
SELECT 'CSC_AI_FIRST_CUSTOMER_BUILDINGS', c.BuildingType, 1, 0
FROM Customer c
WHERE NOT EXISTS (
    SELECT 1 FROM AiFavoredItems f
    WHERE f.ListType = 'CSC_AI_FIRST_CUSTOMER_BUILDINGS' AND f.Item = c.BuildingType
)
ORDER BY c.BuildingType;
