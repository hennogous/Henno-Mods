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

-- 25 is a +25% native yield-weight bias, not 25 score points or a Q8 bid.
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

-- Derive partner districts from the gameplay transaction definitions below.
-- The ordinary customer catalogue covers the fixed transactions; population-
-- scaled Stage3 transactions have their own gameplay registry and must also
-- participate. Neither registry is copied into a separately maintained AI map.
-- One signal per district/Quarter edge avoids
-- stacking +1 for every building stage. City Centers are settlement decisions;
-- Wonder placement has its own native consumer and is not covered by this row.
-- Existing future-footprint Lua guidance remains separate, with no yield from
-- an unbuilt customer in the Quarter economic ledger.
INSERT OR IGNORE INTO CSC_AI_CustomerEdges
        (   Customer,   Quarter   )
SELECT m.DistrictType, q.DistrictType
FROM CSC_QuarterCustomerBuildings m
JOIN Districts q ON q.DistrictType = 'DISTRICT_CSC_' || m.QuarterKey || '_QUARTER'
WHERE m.ProducerStage BETWEEN 2 AND 4
AND m.DistrictType NOT IN ('DISTRICT_CITY_CENTER', 'DISTRICT_WONDER');

-- Population-scaled sales (for example Bakery -> Market) are intentionally
-- absent from CSC_QuarterCustomerBuildings. Omitting this registry silently
-- removed the Commercial Hub and Holy Site incentives after that migration.
-- Use the defined seller/recipient districts, including future Quarters and
-- optional mod rows. The primary key merges overlap with other stages.
INSERT OR IGNORE INTO CSC_AI_CustomerEdges
        (   Customer,   Quarter   )
SELECT m.CustomerDistrictType, m.SellerDistrictType
FROM CSC_Stage3CustomerTransactions m
JOIN Districts q ON q.DistrictType = m.SellerDistrictType
JOIN Districts customer ON customer.DistrictType = m.CustomerDistrictType
WHERE m.CustomerDistrictType NOT IN ('DISTRICT_CITY_CENTER', 'DISTRICT_WONDER');

-- Gameplay sales tags also describe spatial customers without a specific
-- building transaction (for example City Lights urban districts). Derive the
-- Quarter key from its standard gameplay district name, so a new Quarter or
-- tag-only partner requires no parallel AI list. substr strips the13-character
-- DISTRICT_CSC_ prefix and8-character _QUARTER suffix. Only loaded districts enter;
-- missing optional-mod types therefore create no dangling native rules.
-- Providers use the reverse flow direction but share this co-location signal.
-- Their overlap with sales and transaction rows merges at the edge primary key.
INSERT OR IGNORE INTO CSC_AI_CustomerEdges
        (   Customer,   Quarter   )
SELECT t.Type, q.DistrictType
FROM Districts q
JOIN TypeTags t ON t.Tag IN (
    'CLASS_CSC_' || substr(q.DistrictType, 14, length(q.DistrictType) - 21) || '_SALES',
    'CLASS_CSC_' || substr(q.DistrictType, 14, length(q.DistrictType) - 21) || '_GOODS_PROVIDER'
)
JOIN Districts partner ON partner.DistrictType = t.Type
WHERE q.DistrictType GLOB 'DISTRICT_CSC_*_QUARTER'
AND t.Type NOT IN ('DISTRICT_CITY_CENTER', 'DISTRICT_WONDER');

INSERT OR IGNORE INTO CSC_AI_CustomerEdges
        (   Customer,   Quarter   )
SELECT r.CivUniqueDistrictType, e.Quarter
FROM CSC_AI_CustomerEdges e
JOIN DistrictReplaces r ON r.ReplacesDistrictType = e.Customer;

-- Attach +1 private yield per adjacent mapped Quarter to the partner
-- district's score input. Critical material plots are handled by the
-- separate native supplier protections that accompany the Lua policy.
-- AI-C168 isolates this SQL link after a saved-world load: it changes the
-- native final Harbor values and competing Water Entertainment values on
-- the same footprints. It is therefore not a fixed, purely additive bid;
-- native forecasts and alternative-land valuation still process the input.
-- SQL rows alone prove loading, not consumption or a changed choice. The
-- earlier Harbor case retains its Theater winner. The matched Commercial Hub
-- replay (16 November) switches to the adjacent site with the default +1;
-- increasing to +4/+8 raises its value but does not improve that site choice.
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
