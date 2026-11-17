-- Shared CSC runtime types and helper data. Load after CSC_Q_ALL_Schema.sql.
-- Quarter definitions use these modifier types, population gates and bit ladders.
-- Native amounts are unchanged: route bits2..16 complement the base +1 consumer;
-- Stage3 rates use15 Q8 bits; Stage4 whole stacks retain the20-bit range.
-- This setup SQL runs when the gameplay database is assembled, never per turn.

INSERT OR IGNORE INTO Vocabularies
        (   Vocabulary   )
VALUES  (   'DISTRICT_CLASS'   );

INSERT OR IGNORE INTO Types
        (   Type,                                                 Kind   )
VALUES  (   'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',      'KIND_MODIFIER'   ),
        (   'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   'KIND_MODIFIER'   ),
        (   'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',     'KIND_MODIFIER'   );

INSERT OR IGNORE INTO DynamicModifiers
        (   ModifierType,                                         CollectionType,                     EffectType   )
VALUES  (   'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',      'COLLECTION_PLAYER_DISTRICTS',      'EFFECT_ATTACH_MODIFIER'   ),
        (   'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   'COLLECTION_PLAYER_IMPROVEMENTS',   'EFFECT_ATTACH_MODIFIER'   ),
        (   'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',     'COLLECTION_OWNER',                 'EFFECT_ADJUST_DISTRICT_EXTRA_ENTERTAINMENT'   );

INSERT OR IGNORE INTO CSC_PopulationLevels
        (   Pop   )
VALUES  (   '5'   ),
        (   '10'   ),
        (   '15'   ),
        (   '20'   ),
        (   '25'   ),
        (   '30'   ),
        (   '35'   ),
        (   '40'   ),
        (   '45'   ),
        (   '50'   );

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT
	'REQSET_CSC_CITY_HAS_POPULATION_' || Pop,
	'REQUIREMENTSET_TEST_ALL'
FROM CSC_PopulationLevels
WHERE Pop > 0;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT
	'REQSET_CSC_CITY_HAS_POPULATION_' || Pop,
	'REQ_CSC_CITY_HAS_POPULATION_' || Pop
FROM CSC_PopulationLevels
WHERE Pop > 0;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT
	'REQ_CSC_CITY_HAS_POPULATION_' || Pop,
	'REQUIREMENT_CITY_HAS_X_POPULATION'
FROM CSC_PopulationLevels
WHERE Pop > 0;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT
	'REQ_CSC_CITY_HAS_POPULATION_' || Pop,
	'Amount',
	Pop
FROM CSC_PopulationLevels
WHERE Pop > 0;

INSERT OR IGNORE INTO CSC_RouteStackBits
        (   Bit   )
VALUES  (   2   ),
        (   4   ),
        (   8   ),
        (   16   );

INSERT OR IGNORE INTO CSC_ScaledAmountBits
        (   Bit   )
VALUES  (   1   ),
        (   2   ),
        (   4   ),
        (   8   ),
        (   16   ),
        (   32   ),
        (   64   ),
        (   128   ),
        (   256   ),
        (   512   ),
        (   1024   ),
        (   2048   ),
        (   4096   ),
        (   8192   ),
        (   16384   ),
        (   32768   ),
        (   65536   ),
        (   131072   ),
        (   262144   ),
        (   524288   );

INSERT OR IGNORE INTO CSC_Stage3RateBits
        (   Bit   )
SELECT Bit FROM CSC_ScaledAmountBits WHERE Bit <= 16384;

INSERT OR IGNORE INTO CSC_Stage4StackBits
        (   Bit   )
VALUES  (   1   ),
        (   2   ),
        (   4   ),
        (   8   ),
        (   16   ),
        (   32   ),
        (   64   ),
        (   128   );

INSERT OR IGNORE INTO CSC_Stage4StackBits
        (   Bit   )
SELECT Bit FROM CSC_ScaledAmountBits WHERE Bit > 128;
