-- ModSupport_LGD
-- Author: Henno
-- DateCreated: 2025-08-09 09:41:30
--------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Districts
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

UPDATE Districts SET Description = '{LOC_DISTRICT_LEU_GARDEN_DESC}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SERVICE_GARDEN}' WHERE DistrictType='DISTRICT_LEU_GARDEN';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  Garden acts as a Bakers sales/customer district and receives Culture in return.
INSERT OR IGNORE INTO TypeTags

		(	Type,					Tag							) VALUES
		(	'DISTRICT_LEU_GARDEN',	'CLASS_CSC_BAKERS_SALES'			),
		(	'DISTRICT_LEU_GARDEN',	'CLASS_CSC_BAKERS_SALES_CULTURE'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Types

		(	Type,																Kind					)
VALUES	(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN',                    'KIND_BUILDING'			);

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
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_DESCRIPTION',
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
UPDATE Buildings SET Description = '{LOC_BUILDING_LEU_CONSERVATORY_DESC}' || '{LOC_CSC_BAKERS_STAGE_4_EFFECT_GARDEN}' WHERE BuildingType='BUILDING_LEU_CONSERVATORY';

/*
INSERT INTO CivilopediaPageExcludes
		(	SectionId,			PageId	) VALUES
		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN'				);
*/

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings_XP2
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Buildings_XP2

		(	BuildingType,									    Pillage		)
VALUES	(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN',		0			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Building_CitizenYieldChanges
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Building_CitizenYieldChanges

		(	BuildingType,								            YieldType,							YieldChange		)
VALUES	(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN',			'YIELD_CULTURE',					2				),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN',			'YIELD_GOLD',						2				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Culture and +1 Production for every 5 Citizens in the city for each adjacent Conservatory (+1 Gold return in ModSupport_LGD_GOLD.sql)

-- Stage 4 Conservatory threshold yields are handled by the customer-population Lua bridge.

INSERT OR IGNORE INTO DistrictModifiers
		(	DistrictType,					ModifierId	)
SELECT	'DISTRICT_CITY_CENTER',				'MOD_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BUILDING_LEU_CONSERVATORY_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT INTO BuildingModifiers

--  With Urbanization, +2 Tourism to a Garden for each adjacent Cafe
        (	BuildingType,						ModifierId										    	)	VALUES
		(	'BUILDING_CSC_BAKERS_CAFE',			'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_GARDEN'	    	),
--  Mirror the adjacent Conservatory transaction back onto Cafe cities for alternate Cafe art
		(	'BUILDING_LEU_CONSERVATORY',		'MOD_CSC_BAKERS_STAGE_4_PROP_ATTACH_BAKERS_CAFE_ENTER'	),

-- 	+1 Citizen slot (Horticulturist) to a Garden with a Conservatory
		(	'BUILDING_CSC_BAKERS_CAFE',			'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_GARDEN'			),

--  +1 Great Engineer point
		(	'BUILDING_CSC_BAKERS_CAFE',			'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_GARDEN'				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Culture and +1 Production for every 5 Citizens in the city for each adjacent Conservatory (+1 Gold return in ModSupport_LGD_GOLD.sql)

-- Replaced by Stage 4 customer-population city-center property consumers.

INSERT OR IGNORE INTO Modifiers
		(	ModifierId,																			ModifierType,						OwnerRequirementSetId,	SubjectRequirementSetId									)
SELECT	'MOD_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BUILDING_LEU_CONSERVATORY_BIT_' || Bit,	'MODIFIER_BUILDING_YIELD_CHANGE',	NULL,					'REQSET_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

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

--  Art bridge: Conservatories set the existing Stage 4 tourism source property on adjacent Cafe transaction cities
-- CONSOLIDATED: (	'MOD_CSC_BAKERS_STAGE_4_PROP_ATTACH_BAKERS_CAFE_GARDEN',
-- CONSOLIDATED: 	'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',
-- CONSOLIDATED: 	NULL,
-- CONSOLIDATED: 	'REQSET_CSC_ADJ_CAFE_STAGE_4_ART'		),

-- CONSOLIDATED: (	'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_GARDEN',
-- CONSOLIDATED: 	'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',
-- CONSOLIDATED: 	NULL,
-- CONSOLIDATED: 	NULL		),

-- 	+1 Citizen slot (Horticulturist) to a Garden with a Conservatory
(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_GARDEN',
    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',
    'REQSET_CSC_STAGE_4_EFFECT_PREREQ',
    'REQSET_CSC_ADJ_CONSERVATORY'     ),

(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_GARDEN',
    'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',
    NULL,
    NULL    ),

--  +1 Great Engineer point
(	'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_GARDEN',
	'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',
	'REQSET_CSC_STAGE_4_EFFECT_PREREQ',
	'REQSET_CSC_ADJ_CONSERVATORY'			),

(	'MOD_CSC_BAKERS_STAGE_4_GPP_GARDEN',
	'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',
	NULL,
	NULL			);



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Conservatory

-- Replaced by Stage 4 customer-population city-center property consumers.

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,																			Name,				Value							)
SELECT	'MOD_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BUILDING_LEU_CONSERVATORY_BIT_' || Bit,	'BuildingType',		'BUILDING_LEU_CONSERVATORY'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,																			Name,				Value							)
SELECT	'MOD_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BUILDING_LEU_CONSERVATORY_BIT_' || Bit,	'YieldType',		'YIELD_CULTURE'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,																			Name,				Value							)
SELECT	'MOD_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BUILDING_LEU_CONSERVATORY_BIT_' || Bit,	'Amount',			Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments

		(	ModifierId,													Name,					Value										)	VALUES
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_CONSERVATORY',				'BuildingType',			'BUILDING_LEU_CONSERVATORY'					),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_CONSERVATORY',				'YieldType',			'YIELD_CULTURE'								),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_CONSERVATORY',				'Amount',				1											),

--  With Urbanization, +2 Tourism to a Garden for each adjacent Cafe
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_GARDEN',				'ModifierId',			'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_GARDEN'		),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_GARDEN',				'Amount',				2													),
--  Source property consumed by Lua, then exposed to GamePropertyRanges for Cafe SelectionRules
-- CONSOLIDATED: 		(	'MOD_CSC_BAKERS_STAGE_4_PROP_ATTACH_BAKERS_CAFE_GARDEN',	'ModifierId',			'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM'		),
-- CONSOLIDATED: 		(	'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_GARDEN',				'Key',					'CSC_BAKERS_STAGE_4_EFFECT_TOURISM'					),
-- CONSOLIDATED: 		(	'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_GARDEN',				'Amount',				1													),
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_GARDEN',          	'ModifierId',           'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_GARDEN'		),
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_GARDEN',           	'BuildingType',         'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN'		),

--  +1 Great Artist point
		(	'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_GARDEN',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_4_GPP_GARDEN'				),
		(	'MOD_CSC_BAKERS_STAGE_4_GPP_GARDEN',						'GreatPersonClassType',		'GREAT_PERSON_CLASS_ARTIST'						),
		(	'MOD_CSC_BAKERS_STAGE_4_GPP_GARDEN',						'Amount',					'1'												);



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Conservatory

INSERT OR IGNORE INTO RequirementSets

        (	RequirementSetId,					RequirementSetType              )	VALUES
		(	'REQSET_CSC_ADJ_GARDEN',			'REQUIREMENTSET_TEST_ALL'		),
        (   'REQSET_CSC_ADJ_CONSERVATORY',      'REQUIREMENTSET_TEST_ALL'       );

INSERT OR IGNORE INTO RequirementSets
		(	RequirementSetId,															RequirementSetType	)
SELECT	'REQSET_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BIT_' || Bit,		'REQUIREMENTSET_TEST_ALL'
FROM CSC_Stage4StackBits;

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

INSERT OR IGNORE INTO RequirementSetRequirements
		(	RequirementSetId,															RequirementId										)
SELECT	'REQSET_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BIT_' || Bit,		'REQ_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Conservatory

INSERT OR IGNORE INTO Requirements

        (	RequirementId,						RequirementType									)	VALUES
		(	'REQ_CSC_DISTRICT_IS_GARDEN',		'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES'		),
        (   'REQ_CSC_CITY_HAS_CONSERVATORY',    'REQUIREMENT_CITY_HAS_BUILDING'                 );

INSERT OR IGNORE INTO Requirements
		(	RequirementId,															RequirementType,					Inverse	)
SELECT	'REQ_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BIT_' || Bit,		'REQUIREMENT_PLOT_PROPERTY_MATCHES',	0
FROM CSC_Stage4StackBits;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Conservatory

INSERT OR IGNORE INTO RequirementArguments

        (	RequirementId,						Name,					Value					)	VALUES
		(	'REQ_CSC_DISTRICT_IS_GARDEN',		'DistrictType',			'DISTRICT_LEU_GARDEN'	),
        (   'REQ_CSC_CITY_HAS_CONSERVATORY',    'BuildingType',         'BUILDING_LEU_CONSERVATORY' );

INSERT OR IGNORE INTO RequirementArguments
		(	RequirementId,															Name,				Value	)
SELECT	'REQ_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BIT_' || Bit,		'PropertyName',		'CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
		(	RequirementId,															Name,				Value	)
SELECT	'REQ_CSC_BAKERS_STAGE_4_CONSERVATORY_CULTURE_RETURN_BIT_' || Bit,		'PropertyMinimum',	1
FROM CSC_Stage4StackBits;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- CSC_AbilityAttachModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO CSC_AbilityAttachModifiers
		(	ModifierId,											AbilityIcon,										AbilityIconTarget		)
VALUES	(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_GARDEN',		'ICON_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN',	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- CSC_SpecialistAttachModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO CSC_SpecialistAttachModifiers
		(	ModifierId		)
VALUES	(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_GARDEN'		);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- ModifierStrings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO ModifierStrings
	(	ModifierId,                                			Context,			'Text'			)	VALUES
	(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_GARDEN',		'Preview',			'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_GARDEN'		),
	(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_GARDEN',		'Preview',			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN_NAME'	);

-- Garden service messaging is folded into the main Stage 4 effect notification.
