--- CSC_TEST_AdjacentIcons.sql
--- Test file: one Ruivo adjacency entry per icon-bearing adjacency type.
--- District: DISTRICT_CAMPUS  |  Yield: +1 Science each  |  MinRings=1 MaxRings=1 (edge-icon eligibility)
--- Purpose: verify tile-edge overlay icons fire correctly for every type during Campus placement.
--- Remove this file before shipping.
---------------------------------------------------------------


---------------------------------------------------------------
--  NON-CAO TYPES — icon comes from Ruivo_AdjacencyType.ArtdefOverlayEntry
---------------------------------------------------------------

INSERT OR IGNORE INTO Ruivo_New_Adjacency (
    ID,
    DistrictType,
    ProvideType,
    YieldType,
    YieldChange,
    AdjacencyType,
    MinRings,
    MaxRings    ) VALUES

--  FROM_RIVER_CROSSING → Terrain_River ... doesn't work
(   'CSC_TEST_ICON_RIVER_CROSSING',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_CULTURE',
    1,
    'FROM_RIVER_CROSSING',
    1,
    1   );
/*
--  FROM_ADJACENT_RESOURCE → Terrain_Generic_Resource ... works
(   'CSC_TEST_ICON_ADJ_RESOURCE',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_FOOD',
    1,
    'FROM_ADJACENT_RESOURCE',
    1,
    1   ),

--  FROM_RINGS_RESOURCE → Terrain_Generic_Resource ... works
(   'CSC_TEST_ICON_RINGS_RESOURCE',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_FAITH',
    1,
    'FROM_RINGS_RESOURCE',
    1,
    1   ),

--  FROM_ADJACENT_LAKE → Terrain_Coast ... works
(   'CSC_TEST_ICON_ADJ_LAKE',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_GOLD',
    1,
    'FROM_ADJACENT_LAKE',
    1,
    1   ),

--  FROM_RINGS_LAKE → Terrain_Coast ... works
(   'CSC_TEST_ICON_RINGS_LAKE',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_PRODUCTION',
    1,
    'FROM_RINGS_LAKE',
    1,
    1   ),

--  FROM_ADJACENT_WONDERS → Generic_Wonder ... works, but without an arrow, will require an artef override
(   'CSC_TEST_ICON_ADJ_WONDERS',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_SCIENCE',
    1,
    'FROM_ADJACENT_WONDERS',
    1,
    1   ),

--  FROM_RINGS_WONDERS → Generic_Wonder ... works, but without an arrow, will require an artef override
(   'CSC_TEST_ICON_RINGS_WONDERS',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_GOLD',
    1,
    'FROM_RINGS_WONDERS',
    1,
    1   ),

--  FROM_ADJACENT_DISTRICT → Districts_Generic_District ... works
(   'CSC_TEST_ICON_ADJ_DISTRICT',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_FAITH',
    1,
    'FROM_ADJACENT_DISTRICT',
    1,
    1   ),

--  FROM_RINGS_DISTRICT → Districts_Generic_District ... works
(   'CSC_TEST_ICON_RINGS_DISTRICT',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_CULTURE',
    1,
    'FROM_RINGS_DISTRICT',
    1,
    1   ),

--  FROM_ADJACENT_DISTRICT_AND_WONDER → Districts_Generic_District ... works
(   'CSC_TEST_ICON_ADJ_DIST_WONDER',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_PRODUCTION',
    1,
    'FROM_ADJACENT_DISTRICT_AND_WONDER',
    1,
    1   ),

--  FROM_RINGS_DISTRICT_AND_WONDER → Districts_Generic_District ... works
(   'CSC_TEST_ICON_RINGS_DIST_WONDER',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_FOOD',
    1,
    'FROM_RINGS_DISTRICT_AND_WONDER',
    1,
    1   );


---------------------------------------------------------------
--  CAO TERRAIN-SETS — icon comes from Ruivo_CAO.ArtdefOverlayEntry
--  AdjacencyType: FROM_RINGS_CAO_TERRAIN_SETS
---------------------------------------------------------------

INSERT OR IGNORE INTO Ruivo_New_Adjacency (
    ID,
    DistrictType,
    ProvideType,
    YieldType,
    YieldChange,
    AdjacencyType,
    CustomAdjacentObject,
    MinRings,
    MaxRings    ) VALUES

--  IsMountain → Terrain_Mountain ... doesn't work
(   'CSC_TEST_ICON_MOUNTAIN',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_SCIENCE',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsMountain',
    1,
    1   ),

--  IsHills → Terrain_Plains_Hills
(   'CSC_TEST_ICON_HILLS',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_GOLD',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsHills',
    1,
    1   ),

--  IsFlatlands → Terrain_Plains
(   'CSC_TEST_ICON_FLATLANDS',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_CULTURE',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsFlatlands',
    1,
    1   ),

--  IsWater → Terrain_Ocean
(   'CSC_TEST_ICON_WATER',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_FOOD',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsWater',
    1,
    1   ),

--  IsShallowWater → Terrain_Sea
(   'CSC_TEST_ICON_SHALLOW_WATER',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_FAITH',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsShallowWater',
    1,
    1   ),

--  IsCoastalLand → Terrain_Coast
(   'CSC_TEST_ICON_COASTAL_LAND',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_PRODUCTION',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsCoastalLand',
    1,
    1   ),

--  IsLake → Terrain_Coast
(   'CSC_TEST_ICON_LAKE_TERRAIN',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_SCIENCE',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsLake',
    1,
    1   ),

--  IsRiverCrossing → Terrain_River
(   'CSC_TEST_ICON_RIVER_TERRAIN',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_SCIENCE',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsRiverCrossing',
    1,
    1   ),

--  IsOpenGround → Terrain_Grass
(   'CSC_TEST_ICON_OPEN_GROUND',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_SCIENCE',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsOpenGround',
    1,
    1   ),

--  IsRoughGround → Terrain_Plains_Hills
(   'CSC_TEST_ICON_ROUGH_GROUND',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_SCIENCE',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsRoughGround',
    1,
    1   ),

--  IsCanyon → NULL (no icon — included to confirm it stays blank)
(   'CSC_TEST_ICON_CANYON',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_SCIENCE',
    1,
    'FROM_RINGS_CAO_TERRAIN_SETS',
    'IsCanyon',
    1,
    1   );


---------------------------------------------------------------
--  CAO RESOURCE CLASSES — icon comes from Ruivo_CAO.ArtdefOverlayEntry
--  AdjacencyType: FROM_RINGS_CAO_RESOURCE_CLASS
--  All → Terrain_Generic_Resource_Class
---------------------------------------------------------------

INSERT OR IGNORE INTO Ruivo_New_Adjacency (
    ID,
    DistrictType,
    ProvideType,
    YieldType,
    YieldChange,
    AdjacencyType,
    CustomAdjacentObject,
    MinRings,
    MaxRings    ) VALUES

(   'CSC_TEST_ICON_RES_BONUS',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_SCIENCE',
    1,
    'FROM_RINGS_CAO_RESOURCE_CLASS',
    'RESOURCECLASS_BONUS',
    1,
    1   ),

(   'CSC_TEST_ICON_RES_LUXURY',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_CULTURE',
    1,
    'FROM_RINGS_CAO_RESOURCE_CLASS',
    'RESOURCECLASS_LUXURY',
    1,
    1   ),

(   'CSC_TEST_ICON_RES_STRATEGIC',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_GOLD',
    1,
    'FROM_RINGS_CAO_RESOURCE_CLASS',
    'RESOURCECLASS_STRATEGIC',
    1,
    1   ),

(   'CSC_TEST_ICON_RES_ARTIFACT',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_FAITH',
    1,
    'FROM_RINGS_CAO_RESOURCE_CLASS',
    'RESOURCECLASS_ARTIFACT',
    1,
    1   );


---------------------------------------------------------------
--  CAO RESOURCE TYPE-TAGS — icon comes from Ruivo_CAO.ArtdefOverlayEntry
--  AdjacencyType: FROM_RINGS_TYPETAG_RESOURCE
---------------------------------------------------------------

INSERT OR IGNORE INTO Ruivo_New_Adjacency (
    ID,
    DistrictType,
    ProvideType,
    YieldType,
    YieldChange,
    AdjacencyType,
    CustomAdjacentObject,
    MinRings,
    MaxRings    ) VALUES

--  CLASS_FOOD → Terrain_Generic_Resource
(   'CSC_TEST_ICON_TAG_FOOD',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_FOOD',
    1,
    'FROM_RINGS_TYPETAG_RESOURCE',
    'CLASS_FOOD',
    1,
    1   ),

--  CLASS_SEA → Terrain_Sea
(   'CSC_TEST_ICON_TAG_SEA',
    'DISTRICT_CAMPUS',
    'SelfBonus',
    'YIELD_PRODUCTION',
    1,
    'FROM_RINGS_TYPETAG_RESOURCE',
    'CLASS_SEA',
    1,
    1   );
