-- This action is enabled by the CE package with supplier exclusion support.
-- One private adjacency step gives native placement a small customer-side
-- co-location signal. It grants no ordinary currency conversion. The yield
-- itself is global, so its effects on automatic human allocation still need
-- separate qualification. No material plot receives the private yield.
INSERT OR IGNORE INTO Types
        (   Type,                       Kind   )
VALUES  (   'YIELD_CSC_AI_PLACEMENT',   'KIND_YIELD'   );

INSERT OR IGNORE INTO Yields
        (   YieldType,                  Name,                          IconString,   OccupiedCityChange,   DefaultValue   )
VALUES  (   'YIELD_CSC_AI_PLACEMENT',   'LOC_CSC_AI_PLACEMENT_NAME',   '',           0,                    1   );

INSERT INTO AiFavoredItems
        (   ListType,   Item,   Favored,   Value   )
SELECT 'DefaultYieldBias', 'YIELD_CSC_AI_PLACEMENT', 0, 25
WHERE NOT EXISTS (
    SELECT 1 FROM AiFavoredItems
    WHERE ListType = 'DefaultYieldBias' AND Item = 'YIELD_CSC_AI_PLACEMENT'
);

CREATE TEMP TABLE CSC_AI_CustomerEdges (
    Customer TEXT NOT NULL,
    Quarter TEXT NOT NULL,
    PRIMARY KEY (Customer, Quarter)
);

-- City Centers are settlement decisions. Other mapped Stage 2 customers
-- can use normal district placement, including direct unique replacements.
INSERT OR IGNORE INTO CSC_AI_CustomerEdges
        (   Customer,   Quarter   )
SELECT m.DistrictType, q.DistrictType
FROM CSC_QuarterCustomerBuildings m
JOIN Districts q ON q.DistrictType = 'DISTRICT_CSC_' || m.QuarterKey || '_QUARTER'
WHERE m.ProducerStage = 2 AND m.DistrictType <> 'DISTRICT_CITY_CENTER';

INSERT OR IGNORE INTO CSC_AI_CustomerEdges
        (   Customer,   Quarter   )
SELECT r.CivUniqueDistrictType, e.Quarter
FROM CSC_AI_CustomerEdges e
JOIN DistrictReplaces r ON r.ReplacesDistrictType = e.Customer;

INSERT OR IGNORE INTO Adjacency_YieldChanges
        (   ID,   Description,   YieldType,   YieldChange,   TilesRequired,   AdjacentDistrict   )
SELECT
    'CSC_AI_CUSTOMER_' || Customer || '__' || Quarter,
    'LOC_CSC_AI_PLACEMENT_NAME',
    'YIELD_CSC_AI_PLACEMENT',
    1,
    1,
    Quarter
FROM CSC_AI_CustomerEdges;

INSERT OR IGNORE INTO District_Adjacencies
        (   DistrictType,   YieldChangeId   )
SELECT Customer, 'CSC_AI_CUSTOMER_' || Customer || '__' || Quarter
FROM CSC_AI_CustomerEdges;

DROP TABLE CSC_AI_CustomerEdges;

-- A small native recruitment preference. Existing tuning mods keep their
-- own Builder value. Job selection and movement remain native.
INSERT INTO AiFavoredItems
        (   ListType,   Item,   Favored,   Value   )
SELECT 'UnitPriorityBoosts', 'UNIT_BUILDER', 1, 10
WHERE EXISTS (SELECT 1 FROM AiLists WHERE ListType = 'UnitPriorityBoosts' AND System = 'Units')
AND NOT EXISTS (
    SELECT 1 FROM AiFavoredItems WHERE ListType = 'UnitPriorityBoosts' AND Item = 'UNIT_BUILDER'
);

-- Build City Improvement can ask more than one city to train a Builder.
-- Definition slot 2 is the native Required City input for the Build Unit node.
INSERT INTO TreeData
        (   DefnId,   NodeId,   TreeName,   DefaultData   )
SELECT 2, n.NodeId, n.TreeName, '-1'
FROM BehaviorTreeNodes n
WHERE n.TreeName = 'Build City Improvement' AND n.NodeType = 'Build Unit'
AND NOT EXISTS (
    SELECT 1 FROM TreeData t
    WHERE t.TreeName = n.TreeName AND t.NodeId = n.NodeId AND t.DefnId = 2
);

UPDATE TreeData SET DefaultData = '-1'
WHERE DefnId = 2 AND TreeName = 'Build City Improvement'
AND NodeId IN (
    SELECT NodeId FROM BehaviorTreeNodes
    WHERE TreeName = 'Build City Improvement' AND NodeType = 'Build Unit'
);
