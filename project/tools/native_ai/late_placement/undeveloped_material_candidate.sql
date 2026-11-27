-- Experimental stock-AI treatment for Quarter foundations that precede the
-- first Builder. Append to CSC's ordinary connector SQL for a matched replay.
-- Selection uses the final gameplay resource catalogue, including modded
-- resources. The stock adjacency reader matches one resource class per row.
CREATE TEMP TABLE CSC_AI_UndevelopedMaterialClasses AS
WITH Base AS (
    SELECT DISTINCT m.QuarterKey, r.ResourceType, r.ResourceClassType
    FROM CSC_QuarterMaterialAdjacencyConfig m
    JOIN TypeTags t ON t.Tag = m.SourceTag
    JOIN Resources r ON r.ResourceType = t.Type
    WHERE m.SourceFilter = '' AND m.AdjacencyType = 'FROM_RINGS_TYPETAG_RESOURCE'
      AND m.SourceTag = 'CLASS_CSC_' || m.QuarterKey || '_BASE'
), ClassSizes AS (
    SELECT ResourceClassType, COUNT(*) AS ClassSize
    FROM Resources GROUP BY ResourceClassType
), QuarterSizes AS (
    SELECT QuarterKey, COUNT(*) AS BaseSize
    FROM Base GROUP BY QuarterKey
)
SELECT q.DistrictType AS Quarter, b.ResourceClassType AS Class,
       CASE WHEN 2 * COUNT(*) >= c.ClassSize THEN 2 ELSE 1 END AS Amount
FROM Base b
JOIN Districts q ON q.DistrictType = 'DISTRICT_CSC_' || b.QuarterKey || '_QUARTER'
JOIN ClassSizes c ON c.ResourceClassType = b.ResourceClassType
JOIN QuarterSizes s ON s.QuarterKey = b.QuarterKey
GROUP BY q.DistrictType, b.ResourceClassType, c.ClassSize, s.BaseSize
-- A broad class is a useful proxy only if it contains multiple mapped Base
-- types and covers at least half the Quarter's Base catalogue. A minimum
-- one-in-six class share admits Flax/Sheep for Tailors on the standalone
-- map while rejecting the luxury class for a single Cotton mapping. These
-- fractions describe eligible resource types, not actual world abundance.
HAVING COUNT(*) >= 2 AND 2 * COUNT(*) >= s.BaseSize AND 6 * COUNT(*) >= c.ClassSize;

INSERT OR IGNORE INTO Adjacency_YieldChanges
        (   ID,   Description,   YieldType,   YieldChange,   TilesRequired,   AdjacentResourceClass   )
SELECT 'CSC_AI_DEPOSIT_' || Quarter || '__' || Class, 'LOC_CSC_AI_PLACEMENT_NAME',
       'YIELD_CSC_AI_PLACEMENT', Amount, 1, Class
FROM CSC_AI_UndevelopedMaterialClasses ORDER BY Quarter, Class;

INSERT OR IGNORE INTO District_Adjacencies
        (   DistrictType,   YieldChangeId   )
SELECT Quarter, 'CSC_AI_DEPOSIT_' || Quarter || '__' || Class
FROM CSC_AI_UndevelopedMaterialClasses ORDER BY Quarter, Class;

DROP TABLE CSC_AI_UndevelopedMaterialClasses;
