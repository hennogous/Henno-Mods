--==========================================================================================================================
-- CSC: Late processor for Modular Adjacency Bonuses.
-- Quarter and ModSupport files tag objects/classes; this file owns the Ruivo_New_Adjacency generation.
--==========================================================================================================================

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Quarter material adjacencies
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Ruivo_New_Adjacency
    (
    ID,
    DistrictType,
    ProvideType,
    YieldType,
    YieldChange,
    AdjacencyType,
    CustomAdjacentObject,
    Rings,
    MustOwn,
    DistrictModifiers
    )
SELECT
    'CSC_' || C.QuarterKey || '_' ||
        CASE
            WHEN C.SourceTag LIKE '%_BASE' THEN 'PRODUCTION_FROM_BASE'
            WHEN C.SourceTag LIKE '%_SPEC' THEN 'PRODUCTION_FROM_SPEC'
            ELSE 'PRODUCTION_FROM_' || REPLACE(C.SourceTag, 'CLASS_CSC_', '')
        END ||
        CASE
            WHEN C.AdjacencyType = 'FROM_RINGS_TYPETAG_RESOURCE' THEN ''
            ELSE '_' || TT.Type
        END,
    'DISTRICT_CSC_' || C.QuarterKey || '_QUARTER',
    'SelfBonus',
    C.YieldType,
    C.YieldChange,
    C.AdjacencyType,
    CASE
        WHEN C.AdjacencyType = 'FROM_RINGS_TYPETAG_RESOURCE' THEN C.SourceTag
        ELSE TT.Type
    END,
    1,
    1,
    1
FROM CSC_QuarterMaterialAdjacencyConfig AS C
JOIN TypeTags AS TT
    ON TT.Tag = C.SourceTag
WHERE C.SourceFilter = ''
    OR TT.Type LIKE C.SourceFilter
GROUP BY
    C.QuarterKey,
    C.SourceTag,
    C.SourceFilter,
    C.YieldType,
    C.YieldChange,
    C.AdjacencyType,
    CASE
        WHEN C.AdjacencyType = 'FROM_RINGS_TYPETAG_RESOURCE' THEN C.SourceTag
        ELSE TT.Type
    END;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Sales/customer adjacencies
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  Base district tags propagate to unique replacement districts before typetag-driven rows are generated.
--  Keep this limited to district-facing CSC adjacency tags; material/resource tags are handled separately above.
INSERT OR IGNORE INTO TypeTags
    (
    Type,
    Tag
    )
SELECT DISTINCT
    DR.CivUniqueDistrictType,
    TT.Tag
FROM TypeTags AS TT
JOIN DistrictReplaces AS DR
    ON DR.ReplacesDistrictType = TT.Type
WHERE TT.Tag LIKE 'CLASS_CSC_%_SALES'
    OR TT.Tag LIKE 'CLASS_CSC_%_SALES_%'
    OR TT.Tag LIKE 'CLASS_CSC_%_GOODS_PROVIDER'
    OR TT.Tag LIKE 'CLASS_CSC_%_TO_QUARTER_%';

--  Quarters receive yields from adjacent districts tagged as quarter-facing source classes.
--  Supported tag shapes:
--      CLASS_CSC_<QUARTER>_SALES                              -> Gold to Quarter
--      CLASS_CSC_<QUARTER>_GOODS_PROVIDER                     -> Production to Quarter
--      CLASS_CSC_<QUARTER>_<SOURCE>_TO_QUARTER_<YIELD>        -> Yield to Quarter
WITH QuarterFacingAdjacencyTags AS
    (
    SELECT DISTINCT
        Tag,
        REPLACE(REPLACE(Tag, 'CLASS_CSC_', ''), '_SALES', '') AS QuarterKey,
        'SALES' AS SourceKey,
        'YIELD_GOLD' AS YieldType
    FROM TypeTags
    WHERE Tag LIKE 'CLASS_CSC_%_SALES'
        AND Tag NOT LIKE 'CLASS_CSC_%_SALES_%'

    UNION

    SELECT DISTINCT
        Tag,
        REPLACE(REPLACE(Tag, 'CLASS_CSC_', ''), '_GOODS_PROVIDER', '') AS QuarterKey,
        'GOODS_PROVIDER' AS SourceKey,
        'YIELD_PRODUCTION' AS YieldType
    FROM TypeTags
    WHERE Tag LIKE 'CLASS_CSC_%_GOODS_PROVIDER'

    UNION

    SELECT DISTINCT
        Tag,
        SUBSTR(Body, 1, INSTR(Body, '_') - 1) AS QuarterKey,
        SUBSTR(Body, INSTR(Body, '_') + 1, INSTR(Body, '_TO_QUARTER_') - INSTR(Body, '_') - 1) AS SourceKey,
        'YIELD_' || SUBSTR(Body, INSTR(Body, '_TO_QUARTER_') + 12) AS YieldType
    FROM
        (
        SELECT
            Tag,
            SUBSTR(Tag, 11) AS Body
        FROM TypeTags
        WHERE Tag LIKE 'CLASS_CSC_%_TO_QUARTER_%'
        )
    )
INSERT OR IGNORE INTO Ruivo_New_Adjacency
    (
    ID,
    DistrictType,
    ProvideType,
    YieldType,
    YieldChange,
    AdjacencyType,
    CustomAdjacentObject,
    Rings,
    MustOwn,
    DistrictModifiers
    )
SELECT
    CASE
        WHEN SourceKey = 'SALES' THEN 'CSC_CITY_ALL_SALES_GOLD_TO_' || QuarterKey
        ELSE 'CSC_' || QuarterKey || '_' || SourceKey || '_' || REPLACE(YieldType, 'YIELD_', '') || '_TO_QUARTER'
    END,
    'DISTRICT_CSC_' || QuarterKey || '_QUARTER',
    'SelfBonus',
    YieldType,
    1,
    'FROM_RINGS_TYPETAG_DISTRICT',
    Tag,
    1,
    1,
    1
FROM QuarterFacingAdjacencyTags
ORDER BY QuarterKey, SourceKey, YieldType;

--  Customer districts receive the appropriate return yield from adjacent Quarters.
--  Generate explicit rows for unique replacement districts so IDs stay readable, e.g.
--  CSC_BAKERS_WATER_STREET_CARNIVAL_CULTURE_FROM_QUARTER instead of MAB's cloned
--  DISTRICT_WATER_STREET_CARNIVAL_CSC_BAKERS_WATER_ENTERTAINMENT_COMPLEX_CULTURE_FROM_QUARTER.
WITH SalesReturnAdjacencyTags AS
    (
    SELECT DISTINCT
        Tag,
        REPLACE(SUBSTR(Tag, 11, INSTR(Tag, '_SALES_') - 11), 'CLASS_CSC_', '') AS QuarterKey,
        'YIELD_' || SUBSTR(Tag, INSTR(Tag, '_SALES_') + 7) AS YieldType
    FROM TypeTags
    WHERE Tag LIKE 'CLASS_CSC_%_SALES_%'
    ),
SalesReturnDistricts AS
    (
    SELECT DISTINCT
        TT.Type AS DistrictType,
        C.QuarterKey,
        C.YieldType
    FROM TypeTags AS TT
    JOIN SalesReturnAdjacencyTags AS C
        ON C.Tag = TT.Tag

    UNION

    SELECT DISTINCT
        DR.CivUniqueDistrictType AS DistrictType,
        C.QuarterKey,
        C.YieldType
    FROM TypeTags AS TT
    JOIN SalesReturnAdjacencyTags AS C
        ON C.Tag = TT.Tag
    JOIN DistrictReplaces AS DR
        ON DR.ReplacesDistrictType = TT.Type
    )
INSERT OR IGNORE INTO Ruivo_New_Adjacency
    (
    ID,
    DistrictType,
    ProvideType,
    YieldType,
    YieldChange,
    AdjacencyType,
    CustomAdjacentObject,
    Rings,
    MustOwn,
    DistrictModifiers
    )
SELECT
    'CSC_' || QuarterKey || '_' || REPLACE(DistrictType, 'DISTRICT_', '') || '_' || REPLACE(YieldType, 'YIELD_', '') || '_FROM_QUARTER',
    DistrictType,
    'SelfBonus',
    YieldType,
    1,
    'FROM_RINGS_CAO_DISTRICT',
    'DISTRICT_CSC_' || QuarterKey || '_QUARTER',
    1,
    1,
    1
FROM SalesReturnDistricts
ORDER BY QuarterKey, DistrictType, YieldType;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Bakers' building-specific terrain/river adjacencies
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Ruivo_New_Adjacency
    (
    ID,
    DistrictType,
    ProvideType,
    YieldType,
    YieldChange,
    AdjacencyType,
    CustomAdjacentObject,
    MinRings,
    Rings,
    DistrictModifiers,
    ModifierOwner,
    WhoIsTheOwner
    )
SELECT
    'CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS',
    'DISTRICT_CSC_BAKERS_QUARTER',
    'SelfBonus',
    'YIELD_PRODUCTION',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsHills',
    0,
    0,
    1,
    'BuildingModifiers',
    'BUILDING_CSC_BAKERS_WIND_MILL'
WHERE EXISTS
    (
    SELECT 1
    FROM Buildings
    WHERE BuildingType = 'BUILDING_CSC_BAKERS_WIND_MILL'
    );

INSERT OR IGNORE INTO Ruivo_New_Adjacency
    (
    ID,
    DistrictType,
    ProvideType,
    YieldType,
    YieldChange,
    AdjacencyType,
    Rings,
    DistrictModifiers,
    ModifierOwner,
    WhoIsTheOwner
    )
SELECT
    'CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER',
    'DISTRICT_CSC_BAKERS_QUARTER',
    'SelfBonus',
    'YIELD_PRODUCTION',
    0.5,
    'FROM_RIVER_CROSSING',
    1,
    1,
    'BuildingModifiers',
    'BUILDING_CSC_BAKERS_WATER_MILL'
WHERE EXISTS
    (
    SELECT 1
    FROM Buildings
    WHERE BuildingType = 'BUILDING_CSC_BAKERS_WATER_MILL'
    );

INSERT OR IGNORE INTO Ruivo_CAO
    (CustomAdjacentObject,                      Name,                                       ArtdefOverlayEntry      )     VALUES
    
--  Bakers' Quarter
    ('CLASS_CSC_BAKERS_BASE',                   'LOC_CLASS_CSC_BASE_NAME',                  'CSC_Base_Materials'    ),
    ('CLASS_CSC_BAKERS_SPEC',                   'LOC_CLASS_CSC_SPEC_NAME',                  'CSC_Spec_Materials'    ),
    ('CLASS_CSC_BAKERS_SALES',                  'LOC_CLASS_CSC_SALES_NAME',                 'CSC_Sales'             ),
    ('DISTRICT_CSC_BAKERS_QUARTER',             'LOC_DISTRICT_CSC_BAKERS_QUARTER_NAME',     'CSC_Goods'             ),
    ('CLASS_CSC_BAKERS_GOODS_PROVIDER',		    'LOC_CLASS_CSC_GOODS_PROVIDER_NAME',		'CSC_Goods_Provider'    );
