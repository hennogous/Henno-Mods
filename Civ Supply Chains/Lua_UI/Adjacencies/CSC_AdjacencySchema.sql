-- CSC's bundled adjacency engine. Architecture informed by Ruivo's MAB;
-- implemented independently for CSC. See project/docs/integrations/csc-adjacencies.md.
CREATE TABLE IF NOT EXISTS CSC_AdjacencyRules (
    ID TEXT PRIMARY KEY,
    DistrictType TEXT NOT NULL,
    ProvideType TEXT NOT NULL DEFAULT 'SelfBonus',
    YieldType TEXT NOT NULL DEFAULT 'YIELD_PRODUCTION',
    CustomArgumentValue TEXT NOT NULL DEFAULT 'NONE',
    YieldChange REAL NOT NULL DEFAULT 1,
    AdjacencyType TEXT NOT NULL,
    CustomAdjacentObject TEXT NOT NULL DEFAULT 'NONE',
    Rings INTEGER NOT NULL DEFAULT 1 CHECK (Rings >= 0),
    MinRings INTEGER NOT NULL DEFAULT 1 CHECK (MinRings >= 0),
    MaxRings INTEGER CHECK (MaxRings >= 0),
    MustOwn INTEGER NOT NULL DEFAULT 0 CHECK (MustOwn IN (0,1)),
    DistrictModifiers INTEGER NOT NULL DEFAULT 0,
    NewMethod INTEGER NOT NULL DEFAULT 0,
    ApplyForUniqueDistricts INTEGER NOT NULL DEFAULT 0,
    TraitType TEXT,
    ModifierOwner TEXT NOT NULL DEFAULT 'DistrictModifiers',
    WhoIsTheOwner TEXT,
    CollectionType TEXT NOT NULL DEFAULT 'COLLECTION_PLAYER_DISTRICTS',
    Only TEXT NOT NULL DEFAULT 'Human&AI',
    FreeCompose INTEGER NOT NULL DEFAULT 0
);
CREATE TABLE IF NOT EXISTS CSC_AdjacencyObjects (
    CustomAdjacentObject TEXT PRIMARY KEY, Name TEXT, ArtdefOverlayEntry TEXT
);
CREATE TABLE IF NOT EXISTS CSC_AdjacencySources (
    AdjacencyType TEXT PRIMARY KEY, Name TEXT NOT NULL, ArtdefOverlayEntry TEXT
);
CREATE TABLE IF NOT EXISTS CSC_AdjacencyProviders (
    ProvideType TEXT PRIMARY KEY, EffectType TEXT NOT NULL, CollectionType TEXT NOT NULL,
    ArgumentName TEXT, Icon TEXT, Percent INTEGER NOT NULL DEFAULT 0
);
INSERT OR IGNORE INTO CSC_AdjacencyProviders
    (ProvideType, EffectType, CollectionType, ArgumentName, Icon, Percent) VALUES
    ('SelfBonus', 'EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE', 'COLLECTION_OWNER', NULL, NULL, 0),
    ('ProvideToADJ', 'EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE', 'COLLECTION_PLAYER_DISTRICTS', NULL, NULL, 0),
    ('SelfMultiplier', 'EFFECT_ADJUST_DISTRICT_YIELD_MODIFIER', 'COLLECTION_OWNER', NULL, NULL, 1),
    ('SelfTourism', 'EFFECT_ADJUST_DISTRICT_TOURISM_CHANGE', 'COLLECTION_OWNER', NULL, 'ICON_Tourism', 0),
    ('SelfPower', 'EFFECT_ADJUST_CITY_FREE_POWER', 'COLLECTION_OWNER', 'SourceType', 'ICON_Power', 0),
    ('SelfPowerModifier', 'EFFECT_ADJUST_MODIFIED_FREE_POWER_IN_CITY', 'COLLECTION_OWNER_CITY', NULL, 'ICON_Power', 1),
    ('SelfAmenity', 'EFFECT_ADJUST_DISTRICT_AMENITY', 'COLLECTION_OWNER', NULL, 'ICON_Amenities', 0),
    ('SelfHousing', 'EFFECT_ADJUST_DISTRICT_HOUSING', 'COLLECTION_OWNER', NULL, 'ICON_Housing', 0),
    ('SelfLoyalty', 'EFFECT_ADJUST_CITY_IDENTITY_PER_TURN', 'COLLECTION_OWNER_CITY', NULL, 'ICON_PressureUp', 0),
    ('SelfInfluence', 'EFFECT_ADJUST_INFLUENCE_POINTS_PER_TURN', 'COLLECTION_OWNER', NULL, 'ICON_InfluencePerTurn', 0),
    ('SelfFavor', 'EFFECT_ADJUST_PLAYER_EXTRA_FAVOR_PER_TURN', 'COLLECTION_OWNER', NULL, 'ICON_Favor', 0),
    ('SelfTradeRoute', 'EFFECT_ADJUST_TRADE_ROUTE_CAPACITY', 'COLLECTION_OWNER', NULL, 'ICON_TradeRoute', 0),
    ('GreatPersonPoints', 'EFFECT_ADJUST_GREAT_PERSON_POINTS', 'COLLECTION_OWNER', 'GreatPersonClassType', 'ICON_GreatPerson', 0),
    ('GreatPersonMultiplier', 'EFFECT_ADJUST_GREAT_PERSON_POINTS_PERCENT', 'COLLECTION_OWNER', 'GreatPersonClassType', 'ICON_GreatPerson', 1),
    ('SelfExtractResource', 'EFFECT_GRANT_FREE_RESOURCE_EXTRACTED', 'COLLECTION_OWNER', 'ResourceType', 'ICON_Resource', 0),
    ('SelfExtraDistrictSlot', 'EFFECT_ADJUST_CITY_EXTRA_DISTRICTS', 'COLLECTION_OWNER', NULL, 'ICON_District', 0),
    ('SelfCivicBoost', 'EFFECT_ADJUST_CIVIC_BOOST', 'COLLECTION_OWNER', NULL, 'ICON_Culture', 1),
    ('SelfTechnologyBoost', 'EFFECT_ADJUST_TECHNOLOGY_BOOST', 'COLLECTION_OWNER', NULL, 'ICON_Science', 1),
    ('SelfCityGrowth', 'EFFECT_ADJUST_CITY_GROWTH', 'COLLECTION_OWNER', NULL, 'ICON_Food', 1),
    ('SelfAirSlots', 'EFFECT_ADJUST_PLAYER_DISTRICT_AIR_SLOTS', 'COLLECTION_OWNER', NULL, 'ICON_Air', 0),
    ('SelfDistrictProperty', 'EFFECT_ADJUST_DISTRICT_PROPERTY', 'COLLECTION_OWNER', 'Key', NULL, 0),
    ('SelfCityProperty', 'EFFECT_ADJUST_CITY_PROPERTY', 'COLLECTION_OWNER_CITY', 'Key', NULL, 0),
    ('SelfPlayerProperty', 'EFFECT_ADJUST_PLAYER_PROPERTY', 'COLLECTION_OWNER', 'Key', NULL, 0),
    ('SelfGameProperty', 'EFFECT_ADJUST_GAME_PROPERTY', 'COLLECTION_OWNER', 'Key', NULL, 0);
CREATE TABLE IF NOT EXISTS CSC_AdjacencyBits (Bit INTEGER PRIMARY KEY);
INSERT OR IGNORE INTO CSC_AdjacencyBits VALUES (1),(2),(4),(8),(16),(32),(64),(128),(256),(512);
