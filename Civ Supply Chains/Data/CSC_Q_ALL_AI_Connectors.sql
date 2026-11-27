-- Stock AI reads these district/site and Builder preferences with or without
-- CE. SQL generates them once from the final gameplay catalogues. The
-- advanced single-player planner can also supply site-specific economic bids.
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
-- district's score input. Only the advanced planner can quote the loss of
-- an exact supplier here. The lightweight run measures how often Civ
-- covers the last supplier when offered this co-location incentive.
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

-- The customer may already be standing when Civ first considers a Quarter.
-- Give the Quarter one location cue on that side as well. Each posted rule
-- describes one real partner family or loaded replacement. City Centers and
-- generic Wonder tiles are excluded by the edge table above. This modest
-- private yield does not assume a completed buyer, supplier or Service.
INSERT OR IGNORE INTO Adjacency_YieldChanges
        (   ID,   Description,   YieldType,   YieldChange,   TilesRequired,   AdjacentDistrict   )
SELECT  'CSC_AI_QUARTER_' || Quarter || '__' || Customer,
        'LOC_CSC_AI_PLACEMENT_NAME', 'YIELD_CSC_AI_PLACEMENT', 1, 1, Customer
FROM CSC_AI_CustomerEdges;

INSERT OR IGNORE INTO District_Adjacencies
        (   DistrictType,   YieldChangeId   )
SELECT  Quarter, 'CSC_AI_QUARTER_' || Quarter || '__' || Customer
FROM CSC_AI_CustomerEdges;

DROP TABLE CSC_AI_CustomerEdges;

-- The stock adjacency reader can recognize a neighboring improvement, but
-- cannot match our resource tags at a hypothetical district site. Prefer
-- improvement families that frequently work this Quarter's materials. Read
-- the actual resource/improvement mappings after optional mods have loaded.
-- Each family gets at most one signal even when it serves both material classes.
CREATE TEMP TABLE CSC_AI_MaterialSites AS
WITH MaterialKinds AS (
    SELECT DISTINCT m.QuarterKey, t.Type AS ResourceType,
           CASE WHEN m.SourceTag = 'CLASS_CSC_' || m.QuarterKey || '_BASE' THEN 1 ELSE 0 END AS IsBase
    FROM CSC_QuarterMaterialAdjacencyConfig m
    JOIN TypeTags t ON t.Tag = m.SourceTag
    WHERE m.SourceFilter = '' AND m.AdjacencyType = 'FROM_RINGS_TYPETAG_RESOURCE'
      AND m.SourceTag IN ('CLASS_CSC_' || m.QuarterKey || '_BASE', 'CLASS_CSC_' || m.QuarterKey || '_SPEC')
), Families AS (
    SELECT ImprovementType, COUNT(DISTINCT ResourceType) AS ResourceCount
    FROM Improvement_ValidResources
    GROUP BY ImprovementType
)
SELECT q.DistrictType AS Quarter, i.ImprovementType AS Improvement,
       CASE WHEN EXISTS (SELECT 1 FROM Improvement_ValidTerrains v WHERE v.ImprovementType = i.ImprovementType)
              OR EXISTS (SELECT 1 FROM Improvement_ValidFeatures v WHERE v.ImprovementType = i.ImprovementType)
            THEN 2 ELSE 1 END AS TilesRequired
FROM MaterialKinds m
JOIN Districts q ON q.DistrictType = 'DISTRICT_CSC_' || m.QuarterKey || '_QUARTER'
JOIN Improvement_ValidResources v ON v.ResourceType = m.ResourceType
JOIN Improvements i ON i.ImprovementType = v.ImprovementType
JOIN Families f ON f.ImprovementType = v.ImprovementType
WHERE i.Buildable = 1 AND i.Workable = 1
GROUP BY q.DistrictType, i.ImprovementType, f.ResourceCount
-- These are tuning thresholds on resource TYPES, not estimates of map
-- abundance. At least one Base must fit. One third Base admits Pastures;
-- one half Base or Spec combined admits a Bakers plantation. Farms can
-- stand on bare terrain, so they require a pair before awarding one point.
HAVING COUNT(DISTINCT CASE WHEN m.IsBase = 1 THEN m.ResourceType END) > 0
   AND (3 * COUNT(DISTINCT CASE WHEN m.IsBase = 1 THEN m.ResourceType END) >= f.ResourceCount
        OR 2 * COUNT(DISTINCT m.ResourceType) >= f.ResourceCount);

INSERT OR IGNORE INTO Adjacency_YieldChanges
        (   ID,   Description,   YieldType,   YieldChange,   TilesRequired,   AdjacentImprovement   )
SELECT 'CSC_AI_SUPPLIER_' || Quarter || '__' || Improvement,
       'LOC_CSC_AI_PLACEMENT_NAME', 'YIELD_CSC_AI_PLACEMENT', 1, TilesRequired, Improvement
FROM CSC_AI_MaterialSites;

INSERT OR IGNORE INTO District_Adjacencies
        (   DistrictType,   YieldChangeId   )
SELECT Quarter, 'CSC_AI_SUPPLIER_' || Quarter || '__' || Improvement
FROM CSC_AI_MaterialSites;

DROP TABLE CSC_AI_MaterialSites;

-- Before a Builder arrives, Civ can score the class of a neighboring raw
-- resource. Use each Quarter's actual Base tags to decide which classes
-- are informative. The private award enters the ordinary district-site
-- comparison and scales with the number of matching neighbors. On the two
-- Continental benchmark maps this improved supplied Bakers placements.
-- Tailors receive a weaker cue because most bonus resources cannot feed them.
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

-- On stock XP2, the two Build Unit nodes in Build City Improvement leave
-- Required City unbound. BuildFromCityNode already defaults to -1 when
-- reading that input. Keep any explicit city binding chosen by another mod.
