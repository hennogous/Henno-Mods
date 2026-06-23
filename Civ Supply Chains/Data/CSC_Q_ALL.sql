-- CSC_Q_ALL
-- Author: Shadow
-- DateCreated: 2026-06-10 16:57:32
--------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Vocabularies
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Vocabularies

		(    Vocabulary			)
VALUES	(	'DISTRICT_CLASS'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Shared CSC modifier types
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Types

		(	Type,													Kind				)
VALUES	(	'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',		'KIND_MODIFIER'		),
		(	'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',		'KIND_MODIFIER'		),
		(	'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',		'KIND_MODIFIER'		);

INSERT OR IGNORE INTO DynamicModifiers

		(	ModifierType,										    CollectionType,					EffectType				)
VALUES	(	'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',		'COLLECTION_PLAYER_DISTRICTS',		'EFFECT_ATTACH_MODIFIER'	),
		(	'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',		'COLLECTION_PLAYER_IMPROVEMENTS',	'EFFECT_ATTACH_MODIFIER'	),
		(	'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',		'COLLECTION_OWNER',					'EFFECT_ADJUST_DISTRICT_EXTRA_ENTERTAINMENT'	);


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC processor config tables
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Quarter files declare how their material TypeTags become Ruivo/MAB adjacency rows.
-- CSC_Ruivo_AdjacencyProcessor.sql consumes this table after Quarter and ModSupport files have loaded.
CREATE TABLE IF NOT EXISTS CSC_QuarterMaterialAdjacencyConfig
    (
    QuarterKey      TEXT NOT NULL,
    SourceTag       TEXT NOT NULL,
    SourceFilter    TEXT NOT NULL DEFAULT '',
    YieldType       TEXT NOT NULL DEFAULT 'YIELD_PRODUCTION',
    YieldChange     REAL NOT NULL DEFAULT 1,
    AdjacencyType   TEXT NOT NULL,
    PRIMARY KEY
        (
        QuarterKey,
        SourceTag,
        SourceFilter,
        YieldType,
        AdjacencyType
        )
    );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC_PopulationLevels
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Shared ladder used to generate reusable city-population gates. Quarter files can
-- reference REQSET_CSC_CITY_HAS_POPULATION_5, _10, etc. without rebuilding the
-- same requirement boilerplate in every Quarter.
CREATE TABLE IF NOT EXISTS CSC_PopulationLevels
    (
    Pop TEXT
    );

INSERT OR IGNORE INTO CSC_PopulationLevels
		(Pop)
VALUES	('5'), ('10'), ('15'), ('20'), ('25'), ('30'), ('35'), ('40'), ('45'), ('50');

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Shared city population requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSets (
	RequirementSetId,
	RequirementSetType
)
SELECT
	'REQSET_CSC_CITY_HAS_POPULATION_' || Pop,
	'REQUIREMENTSET_TEST_ALL'
FROM CSC_PopulationLevels
WHERE Pop > 0;

INSERT OR IGNORE INTO RequirementSetRequirements (
	RequirementSetId,
	RequirementId
)
SELECT
	'REQSET_CSC_CITY_HAS_POPULATION_' || Pop,
	'REQ_CSC_CITY_HAS_POPULATION_' || Pop
FROM CSC_PopulationLevels
WHERE Pop > 0;

INSERT OR IGNORE INTO Requirements (
	RequirementId,
	RequirementType
)
SELECT
	'REQ_CSC_CITY_HAS_POPULATION_' || Pop,
	'REQUIREMENT_CITY_HAS_X_POPULATION'
FROM CSC_PopulationLevels
WHERE Pop > 0;

INSERT OR IGNORE INTO RequirementArguments (
	RequirementId,
	Name,
	Value
)
SELECT
	'REQ_CSC_CITY_HAS_POPULATION_' || Pop,
	'Amount',
	Pop
FROM CSC_PopulationLevels
WHERE Pop > 0;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Shared bit helper tables
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Civ SQL requirements cannot compare arbitrary numeric property values directly.
-- Lua therefore decomposes a count/amount into binary property flags, and SQL
-- creates one modifier per bit. Active bits add together into the final yield.

-- Route/export stack bits used when Lua writes route-count properties. The +1
-- route bit is handled by the base modifier in Quarter SQL; this table starts at
-- +2 for the extra stack rows.
CREATE TABLE IF NOT EXISTS CSC_RouteStackBits
    (
    Bit INTEGER PRIMARY KEY
    );

INSERT OR IGNORE INTO CSC_RouteStackBits
        (   Bit )
VALUES  (   2   ), (   4   ), (   8   ), (   16  );

-- Scaled amount bits used for fractional per-population yields. Lua stores
-- amount * 10000 as an integer so SQL can reconstruct small decimal values with
-- deterministic bit modifiers.
CREATE TABLE IF NOT EXISTS CSC_ScaledAmountBits
    (
    Bit INTEGER PRIMARY KEY
    );

INSERT OR IGNORE INTO CSC_ScaledAmountBits
        (   Bit )
VALUES  (   1       ), (   2       ), (   4       ), (   8       ), (   16      ), (   32      ), (   64      ), (   128     ),
        (   256     ), (   512     ), (   1024    ), (   2048    ), (   4096    ), (   8192    ), (   16384   ), (   32768   ),
        (   65536   ), (   131072  ), (   262144  ), (   524288  );

-- Stage/customer return stack bits used by thresholded customer-building effects,
-- where the game-facing amount is an integer such as +1 per 5 customer Citizens.
CREATE TABLE IF NOT EXISTS CSC_Stage4StackBits
    (
    Bit INTEGER PRIMARY KEY
    );

INSERT OR IGNORE INTO CSC_Stage4StackBits
        (   Bit )
VALUES  (   1   ), (   2   ), (   4   ), (   8   ), (   16  ), (   32  ), (   64  ), (   128 );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- CSC_AbilityAttachModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS CSC_AbilityAttachModifiers(
		ModifierId TEXT PRIMARY KEY NOT NULL,
		AbilityEffectModifierId TEXT DEFAULT NULL,
		AbilityArgumentAmount INTEGER DEFAULT 0,
		AbilityDesc TEXT DEFAULT NULL,
		AbilityNewDesc TEXT DEFAULT NULL,
		AbilityIncreasedDesc TEXT DEFAULT NULL,
		AbilityDecreasedDesc TEXT DEFAULT NULL,
		AbilityRemovedDesc TEXT DEFAULT NULL,
		AbilityIcon TEXT DEFAULT NULL,
		AbilityIconTarget TEXT DEFAULT NULL
);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- CSC_SpecialistAttachModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS CSC_SpecialistAttachModifiers(
		ModifierId TEXT PRIMARY KEY NOT NULL,
		SpecialistGrantModifierId TEXT DEFAULT NULL,
		ModifierNewDesc TEXT DEFAULT NULL
);
