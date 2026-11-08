-- Static CSC inputs to the stock AI. The mod action is gated on the CE
-- package with supplier exclusion support. These rows load once with the
-- database and complement the per-turn offers in Lua_UI/AI.
--
-- The private yield gives a customer district a co-location signal. It
-- grants no ordinary currency conversion. The yield itself is global, so its
-- effects on automatic human allocation still need separate qualification.
INSERT OR IGNORE INTO Types
        (   Type,                       Kind   )
VALUES  (   'YIELD_CSC_AI_PLACEMENT',   'KIND_YIELD'   );

INSERT OR IGNORE INTO Yields
        (   YieldType,                  Name,                          IconString,   OccupiedCityChange,   DefaultValue   )
VALUES  (   'YIELD_CSC_AI_PLACEMENT',   'LOC_CSC_AI_PLACEMENT_NAME',   '',           0,                    1   );

-- 25 is the native yield bias for this yield, distinct from a Q8 bid.
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

-- Attach +1 private yield per adjacent mapped Quarter to the customer
-- district's score input. Critical material plots are handled by the
-- separate native supplier protections that accompany the Lua policy.
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

-- Add 10 to the Builder unit request priority if no other rule already
-- specifies it. This affects recruitment. The Lua supplier bid affects the
-- improvement job, and Civ still assigns the worker and routes it.
INSERT INTO AiFavoredItems
        (   ListType,   Item,   Favored,   Value   )
SELECT 'UnitPriorityBoosts', 'UNIT_BUILDER', 1, 10
WHERE EXISTS (SELECT 1 FROM AiLists WHERE ListType = 'UnitPriorityBoosts' AND System = 'Units')
AND NOT EXISTS (
    SELECT 1 FROM AiFavoredItems WHERE ListType = 'UnitPriorityBoosts' AND Item = 'UNIT_BUILDER'
);

-- Build City Improvement can consider other cities when recruiting a Builder.
-- Definition slot 2 is the native Required City input for the Build Unit node.
-- The sentinel -1 relaxes the city ID match. Ordinary eligibility still
-- applies when Civ evaluates which city can recruit for the request.
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
