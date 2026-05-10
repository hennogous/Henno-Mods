-- ModSupport_LGD
-- Author: Henno
-- DateCreated: 2025-08-09 09:41:30
--------------------------------------------------------------



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Adjacency_YieldChanges
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO Adjacency_YieldChanges

		(	ID,										Description,                                YieldType,				YieldChange,	AdjacentDistrict						)
VALUES	(	'CSC_GARDEN_GOLD_TO_BAKERS',			'LOC_CSC_GARDEN_GOLD_TO_BAKERS',			'YIELD_GOLD',			1,				'DISTRICT_LEU_GARDEN'					);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Districts
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

UPDATE Districts SET Description = '{LOC_DISTRICT_LEU_GARDEN_DESC}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN}' WHERE DistrictType='DISTRICT_LEU_GARDEN';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	District_Adjacencies
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO District_Adjacencies

		(	DistrictType,							YieldChangeId								)
VALUES	(	'DISTRICT_LEU_GARDEN',					'CSC_BAKERS_CULTURE_TO_ADJACENT_DISTRICT'	),
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'CSC_GARDEN_GOLD_TO_BAKERS'					);

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
--	Buildings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO Types

		(	Type,																Kind					)
VALUES	(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN',                    'KIND_BUILDING'			),
		(	'NOTIFICATION_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_GARDEN',			'KIND_NOTIFICATION'		);

INSERT OR IGNORE INTO Buildings

		(	BuildingType,
			Name,
			Description,
			PrereqTech,
			PrereqCivic,
			Cost,
			PrereqDistrict,
			PurchaseYield,
			Maintenance,
			CitizenSlots,
			Entertainment,
			AdvisorType,
            MustPurchase	)
VALUES	(
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN_DESCRIPTION',
		/*  PrereqTech, */			NULL,
		/*  PrereqCivic, */			NULL,
		/*  Cost, */				0,
		/*  PrereqDistrict, */		'DISTRICT_LEU_GARDEN',
		/*  PurchaseYield, */		NULL,
		/*  Maintenance, */			0,
		/*	CitizenSlots */			1,
		/*  Entertainment */		0,
		/*  AdvisorType */			'ADVISOR_GENERIC',
        /*  MustPurchase */         1
									);

UPDATE Buildings SET Description='LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION_GARDEN' WHERE BuildingType='BUILDING_CSC_BAKERS_CAFE';

INSERT INTO CivilopediaPageExcludes
		(	SectionId,			PageId	) VALUES	
		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN'				);
		
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings_XP2
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

INSERT OR IGNORE INTO Buildings_XP2

		(	BuildingType,									    Pillage		)
VALUES	(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN',	0			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Building_CitizenYieldChanges
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO Building_CitizenYieldChanges

		(	BuildingType,								                YieldType,							YieldChange		)
VALUES	(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN',			'YIELD_CULTURE',					2				),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN',			'YIELD_GOLD',						2				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Conservatory

INSERT OR IGNORE INTO BuildingModifiers (BuildingType, ModifierId)
SELECT
    'BUILDING_CSC_BAKERS_CAFE',
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_CONSERVATORY_AT_POP_' || Pop || '_ATTACH'
FROM CSC_PopulationLevels
WHERE Pop > 0;

INSERT INTO BuildingModifiers

--  With Urbanization, +2 Tourism to a Garden for each adjacent Cafe
        (	BuildingType,						ModifierId										    )	VALUES
		(	'BUILDING_CSC_BAKERS_CAFE',			'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_GARDEN'	    ),

-- 	+1 Citizen slot (Groundskeeper) to a Garden with a Conservatory
		(	'BUILDING_CSC_BAKERS_CAFE',			'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_GARDEN'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Conservatory

INSERT OR IGNORE INTO Modifiers (
    ModifierId,
    ModifierType,
    OwnerRequirementSetId,
    SubjectRequirementSetId
)
SELECT
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_CONSERVATORY_AT_POP_' || Pop || '_ATTACH',
    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',
    'REQSET_CSC_CITY_HAS_POPULATION_' || Pop,
    'REQSET_CSC_ADJ_GARDEN'
FROM CSC_PopulationLevels
WHERE Pop > 0;

INSERT OR IGNORE INTO Modifiers	(
	ModifierId,
	ModifierType,
	OwnerRequirementSetId,
	SubjectRequirementSetId
)
VALUES
(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_CONSERVATORY',
	'MODIFIER_BUILDING_YIELD_CHANGE',
	NULL,
	NULL	),

--  With Urbanization, +2 Tourism to a Garden for each adjacent Cafe
(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_GARDEN',
	'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',
	'REQSET_CSC_STAGE_4_EFFECT_PREREQ',
	'REQSET_CSC_ADJ_CONSERVATORY'		),

(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_GARDEN',
	'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',
	NULL,
	NULL		),

-- 	+1 Citizen slot (Groundskeeper) to a Garden with a Conservatory
(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_GARDEN',
    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',
    'REQSET_CSC_STAGE_4_EFFECT_PREREQ',
    'REQSET_CSC_ADJ_CONSERVATORY'     ),

(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_GARDEN',
    'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',
    NULL,
    NULL    );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Conservatory

INSERT OR IGNORE INTO ModifierArguments (
    ModifierId,
    Name,
    Value
)
SELECT
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_CONSERVATORY_AT_POP_' || Pop || '_ATTACH',
    'ModifierId',
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_CONSERVATORY'
FROM CSC_PopulationLevels
WHERE Pop > 0;

INSERT OR IGNORE INTO ModifierArguments

		(	ModifierId,													Name,					Value										)	VALUES
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_CONSERVATORY',				'BuildingType',			'BUILDING_LEU_CONSERVATORY'					),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_CONSERVATORY',				'YieldType',			'YIELD_CULTURE'								),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_CONSERVATORY',				'Amount',				1											),

--  With Urbanization, +2 Tourism to a Garden for each adjacent Cafe
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_GARDEN',				'ModifierId',			'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_GARDEN'		),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_GARDEN',				'Amount',				2													),
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_GARDEN',          'ModifierId',           'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_GARDEN'	),
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_GARDEN',           'BuildingType',         'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN'		);


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Conservatory

INSERT OR IGNORE INTO RequirementSets 
		
        (	RequirementSetId,					RequirementSetType              )	VALUES
		(	'REQSET_CSC_ADJ_GARDEN',			'REQUIREMENTSET_TEST_ALL'		),
        (   'REQSET_CSC_ADJ_CONSERVATORY',      'REQUIREMENTSET_TEST_ALL'       );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Conservatory

INSERT OR IGNORE INTO RequirementSetRequirements
		
        (	RequirementSetId,					RequirementId					)	VALUES
		(	'REQSET_CSC_ADJ_GARDEN',			'REQ_CSC_PLOT_ADJ_TO_OWNER'		),
		(	'REQSET_CSC_ADJ_GARDEN',			'REQ_CSC_DISTRICT_IS_GARDEN'	),

        (	'REQSET_CSC_ADJ_CONSERVATORY',      'REQ_CSC_PLOT_ADJ_TO_OWNER'		),
		(	'REQSET_CSC_ADJ_CONSERVATORY',      'REQ_CSC_DISTRICT_IS_GARDEN'	),
        (   'REQSET_CSC_ADJ_CONSERVATORY',      'REQ_CSC_CITY_HAS_CONSERVATORY' );


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Conservatory

INSERT OR IGNORE INTO Requirements
        
        (	RequirementId,						RequirementType									)	VALUES
		(	'REQ_CSC_DISTRICT_IS_GARDEN',		'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES'		),
        (   'REQ_CSC_CITY_HAS_CONSERVATORY',    'REQUIREMENT_CITY_HAS_BUILDING'                 );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Conservatory

INSERT OR IGNORE INTO RequirementArguments 

        (	RequirementId,						Name,					Value					)	VALUES
		(	'REQ_CSC_DISTRICT_IS_GARDEN',		'DistrictType',			'DISTRICT_LEU_GARDEN'	),
        (   'REQ_CSC_CITY_HAS_CONSERVATORY',    'BuildingType',         'BUILDING_LEU_CONSERVATORY' );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC_PopulationLevels
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

DROP TABLE CSC_PopulationLevels;

----------------------
-- CSC_AbilityAttachModifiers
----------------------

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

INSERT INTO CSC_AbilityAttachModifiers
		(	ModifierId,													AbilityIcon,						AbilityIconTarget		)
VALUES	(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_GARDEN',				'ICON_EFFECT_CSC_BAKERS_STAGE_4',	'BUILDING_LEU_CONSERVATORY'	);

----------------------
-- CSC_SpecialistAttachModifiers
----------------------

CREATE TABLE IF NOT EXISTS CSC_SpecialistAttachModifiers(
		ModifierId TEXT PRIMARY KEY NOT NULL, 
		SpecialistGrantModifierId TEXT DEFAULT NULL,
		ModifierNewDesc TEXT DEFAULT NULL
);

INSERT INTO CSC_SpecialistAttachModifiers
		(	ModifierId		)
VALUES	(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_GARDEN'		);

INSERT INTO ModifierStrings
	(	ModifierId,                                			Context,			'Text'			)	VALUES
	(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_GARDEN',		'Preview',			'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN'		),
	(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_GARDEN',	'Preview',			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN_NAME'	);

INSERT INTO Notifications
		(	NotificationType,											SeverityType,	ExpiresEndOfTurn,		AutoNotify	)
VALUES	(	'NOTIFICATION_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_GARDEN',	'HIGH',			0,						0			);
