-- CSC_Q_SETUP
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
		(	'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',		'KIND_MODIFIER'		);

INSERT OR IGNORE INTO DynamicModifiers

		(	ModifierType,										    CollectionType,					EffectType				)
VALUES	(	'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',		'COLLECTION_PLAYER_DISTRICTS',		'EFFECT_ATTACH_MODIFIER'	),
		(	'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',		'COLLECTION_PLAYER_IMPROVEMENTS',	'EFFECT_ATTACH_MODIFIER'	);

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
