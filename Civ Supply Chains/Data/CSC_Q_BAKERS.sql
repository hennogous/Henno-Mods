-- CSC_Q_BAKERS
-- Author: Henno
-- DateCreated: 2025-07-13 14:34:41
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	TYPES */
--===========================================================================================================================================================================--

INSERT OR IGNORE INTO Types

		(	Type,																Kind					)
VALUES	( 	'DISTRICT_CSC_BAKERS_QUARTER',                              		'KIND_DISTRICT'         ),

		(	'BUILDING_CSC_BAKERS_RIVER_ACCESS',									'KIND_BUILDING'			),
		(	'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',								'KIND_BUILDING'			),

		(	'BUILDING_CSC_BAKERS_WIND_MILL',									'KIND_BUILDING'			),
		(	'BUILDING_CSC_BAKERS_WATER_MILL',									'KIND_BUILDING'			),
		(	'BUILDING_CSC_BAKERS_BAKERY',										'KIND_BUILDING'			),
		(	'BUILDING_CSC_BAKERS_CAFE',											'KIND_BUILDING'			),

		(	'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',								'KIND_BUILDING'			),
		(	'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',								'KIND_BUILDING'			),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',						'KIND_BUILDING'			),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',						'KIND_BUILDING'			),

		(	'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',					'KIND_MODIFIER'			),
		(	'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',					'KIND_MODIFIER'			);



--===========================================================================================================================================================================--
/*	RESOURCES */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Tags

		(   Tag,							    Vocabulary			)
VALUES	(	'CLASS_CSC_BAKERS_BASE',	        'RESOURCE_CLASS'	),
        (	'CLASS_CSC_BAKERS_SPEC',	        'RESOURCE_CLASS'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO TypeTags

		(	Type, 					Tag							)	VALUES
		
--	Bakers' Quarter base materials
		(	'RESOURCE_BANANAS',		'CLASS_CSC_BAKERS_BASE'		),
		(	'RESOURCE_MAIZE',		'CLASS_CSC_BAKERS_BASE'		),
		(	'RESOURCE_RICE',		'CLASS_CSC_BAKERS_BASE'		),
		(	'RESOURCE_WHEAT',		'CLASS_CSC_BAKERS_BASE'		),

--	Bakers' Quarter specialty materials
		(	'RESOURCE_COCOA',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_COFFEE',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_WINE',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_OLIVES',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_SALT',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_SPICES',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_SUGAR',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_TEA',			'CLASS_CSC_BAKERS_SPEC'		);



--===========================================================================================================================================================================--
/*	STAGE 1 - MATERIALS IMPROVEMENTS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ImprovementModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

INSERT INTO ImprovementModifiers

        (	ImprovementType,				ModifierId												)	VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

--  +1 Production to the Water Mill from improved base materials
		(	'IMPROVEMENT_FARM',				'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER'	),
        (	'IMPROVEMENT_PLANTATION',		'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER'	),
		(	'IMPROVEMENT_PASTURE',			'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER'	),

--  +1 Production to the Wind Mill from improved base materials
		(	'IMPROVEMENT_FARM',				'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND'	),
        (	'IMPROVEMENT_PLANTATION',		'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND'	),
		(	'IMPROVEMENT_PASTURE',			'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND'	),

-- 	CAFE --------------------------------------------------------------------------

--  +1 Production to the Café from improved specialty materials
        (	'IMPROVEMENT_CAMP',				'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'		),
		(	'IMPROVEMENT_MINE',				'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'		),
        (	'IMPROVEMENT_PLANTATION',		'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'		);



--===============================================================================================================================================================================--
/*	BAKERS' QUARTER */
--===============================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Districts
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Districts

		(  	DistrictType,
			Name,
			Description,
			PrereqTech,
			PrereqCivic,
			Cost,
			CostProgressionModel,
			CostProgressionParam1,
			MilitaryDomain,
			RequiresPlacement,
			Coast,
			RequiresPopulation,
			Aqueduct,
			InternalOnly,
			NoAdjacentCity,
			PlunderType,
			PlunderAmount,
			Appeal,
			OnePerCity,
			CaptureRemovesBuildings,
			CaptureRemovesCityDefenses,
			Maintenance,
			CityStrengthModifier,
			AdvisorType                     		)
VALUES	(
		/*  DistrictType, */						'DISTRICT_CSC_BAKERS_QUARTER',
		/*  Name, */								'LOC_DISTRICT_CSC_BAKERS_QUARTER_NAME',
		/*  Description, */							'LOC_DISTRICT_CSC_BAKERS_QUARTER_DESCRIPTION',
		/*  PrereqTech, */							NULL,
		/*  PrereqCivic, */							'CIVIC_CRAFTSMANSHIP',
		/*  Cost, */								60,
		/*  CostProgressionModel, */    			'COST_PROGRESSION_PREVIOUS_COPIES',
		/*  CostProgressionParam1, */				10,
		/*  MilitaryDomain, */						'NO_DOMAIN',
		/*  RequiresPlacement, */					1,
		/*  Coast, */								0,
		/*  RequiresPopulation, */	    			0,
		/*  Aqueduct, */							0,
		/*  InternalOnly, */						0,
		/*  NoAdjacentCity, */						0,
		/*  PlunderType, */							'PLUNDER_HEAL',
		/*  PlunderAmount, */						50,
		/*  Appeal, */								1,
		/*  OnePerCity, */							1,
		/*  CaptureRemovesBuildings, */	   			0,
		/*  CaptureRemovesCityDefenses, */			0,
		/*  Maintenance, */							1,
		/*  CityStrengthModifier */					2,
		/*  AdvisorType */							'ADVISOR_GENERIC'
													);

UPDATE Districts SET Description = '{LOC_DISTRICT_COMMERCIAL_HUB_EXPANSION1_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_3_SERVICE}' WHERE DistrictType='DISTRICT_COMMERCIAL_HUB';
UPDATE Districts SET Description = '{LOC_DISTRICT_ENTERTAINMENT_COMPLEX_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SERVICE_LAND}' WHERE DistrictType='DISTRICT_ENTERTAINMENT_COMPLEX';
UPDATE Districts SET Description = '{LOC_DISTRICT_STREET_CARNIVAL_EXPANSION2_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SERVICE_LAND}' WHERE DistrictType='DISTRICT_STREET_CARNIVAL';
UPDATE Districts SET Description = '{LOC_DISTRICT_HIPPODROME_EXPANSION2_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SERVICE_LAND}' WHERE DistrictType='DISTRICT_HIPPODROME';
UPDATE Districts SET Description = '{LOC_DISTRICT_WATER_ENTERTAINMENT_COMPLEX_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SERVICE_WATER}' WHERE DistrictType='DISTRICT_WATER_ENTERTAINMENT_COMPLEX';
UPDATE Districts SET Description = '{LOC_DISTRICT_WATER_STREET_CARNIVAL_EXPANSION2_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SERVICE_WATER}' WHERE DistrictType='DISTRICT_WATER_STREET_CARNIVAL';


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Adjacency_YieldChanges
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO Adjacency_YieldChanges

		(	ID,											Description,									YieldType,				YieldChange,	AdjacentDistrict						)
VALUES	(	'CSC_BAKERS_FOOD_TO_ADJACENT_DISTRICT',		'LOC_CSC_BAKERS_FOOD_TO_ADJACENT_DISTRICT',		'YIELD_FOOD',			1,				'DISTRICT_CSC_BAKERS_QUARTER'			),
		(	'CSC_BAKERS_CULTURE_TO_ADJACENT_DISTRICT',	'LOC_CSC_BAKERS_CULTURE_TO_ADJACENT_DISTRICT',	'YIELD_CULTURE',		1,				'DISTRICT_CSC_BAKERS_QUARTER'			),
		
		(	'CSC_CITY_CENTER_GOLD_TO_BAKERS',			'LOC_CSC_CITY_CENTER_GOLD_TO_BAKERS',			'YIELD_GOLD',			1,				'DISTRICT_CITY_CENTER'					),

		(	'CSC_COMMERCIAL_HUB_GOLD_TO_BAKERS',		'LOC_CSC_COMMERCIAL_HUB_GOLD_TO_BAKERS',		'YIELD_GOLD',			1,				'DISTRICT_COMMERCIAL_HUB'				),		
		(	'CSC_SUGUBA_GOLD_TO_BAKERS',				'LOC_CSC_SUGUBA_GOLD_TO_BAKERS',				'YIELD_GOLD',			1,				'DISTRICT_SUGUBA'						),

		(	'CSC_ENTERTAINMENT_GOLD_TO_BAKERS',			'LOC_CSC_ENTERTAINMENT_GOLD_TO_BAKERS',			'YIELD_GOLD',			1,				'DISTRICT_ENTERTAINMENT_COMPLEX'		),
		(	'CSC_STREET_CARNIVAL_GOLD_TO_BAKERS',		'LOC_CSC_STREET_CARNIVAL_GOLD_TO_BAKERS',		'YIELD_GOLD',			1,				'DISTRICT_STREET_CARNIVAL'				),
		(	'CSC_HIPPODROME_GOLD_TO_BAKERS',			'LOC_CSC_HIPPODROME_GOLD_TO_BAKERS',			'YIELD_GOLD',			1,				'DISTRICT_HIPPODROME'					),

		(	'CSC_WATER_PARK_GOLD_TO_BAKERS',			'LOC_CSC_WATER_PARK_GOLD_TO_BAKERS',			'YIELD_GOLD',			1,				'DISTRICT_WATER_ENTERTAINMENT_COMPLEX'	),
		(	'CSC_WATER_STREET_CARNIVAL_GOLD_TO_BAKERS',	'LOC_CSC_WATER_STREET_CARNIVAL_GOLD_TO_BAKERS',	'YIELD_GOLD',			1,				'DISTRICT_WATER_STREET_CARNIVAL'		);

--		(	'CSC_BREWERS_PRODUCTION_TO_BAKERS',			'LOC_CSC_BREWERS_PRODUCTION_TO_BAKERS',			'YIELD_PRODUCTION',		1,				'DISTRICT_CSC_BREWERS_QUARTER'			),
--		(	'CSC_BAKERS_GOLD_TO_BREWERS',				'LOC_CSC_BAKERS_GOLD_TO_BREWERS',				'YIELD_GOLD',			1,				'DISTRICT_CSC_BAKERS_QUARTER'			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	District_Adjacencies
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO District_Adjacencies

		(	DistrictType,							YieldChangeId								)
VALUES	(	'DISTRICT_CITY_CENTER',					'CSC_BAKERS_FOOD_TO_ADJACENT_DISTRICT'		),
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'CSC_CITY_CENTER_GOLD_TO_BAKERS'			),
		
		(	'DISTRICT_COMMERCIAL_HUB',				'CSC_BAKERS_FOOD_TO_ADJACENT_DISTRICT'		),
		(	'DISTRICT_SUGUBA',						'CSC_BAKERS_FOOD_TO_ADJACENT_DISTRICT'		),
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'CSC_COMMERCIAL_HUB_GOLD_TO_BAKERS'			),
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'CSC_SUGUBA_GOLD_TO_BAKERS'					),

		(	'DISTRICT_ENTERTAINMENT_COMPLEX',		'CSC_BAKERS_CULTURE_TO_ADJACENT_DISTRICT'	),
		(	'DISTRICT_STREET_CARNIVAL',				'CSC_BAKERS_CULTURE_TO_ADJACENT_DISTRICT'	),
		(	'DISTRICT_HIPPODROME',					'CSC_BAKERS_CULTURE_TO_ADJACENT_DISTRICT'	),
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'CSC_ENTERTAINMENT_GOLD_TO_BAKERS'			),
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'CSC_STREET_CARNIVAL_GOLD_TO_BAKERS'		),
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'CSC_HIPPODROME_GOLD_TO_BAKERS'				),

		(	'DISTRICT_WATER_ENTERTAINMENT_COMPLEX',	'CSC_BAKERS_CULTURE_TO_ADJACENT_DISTRICT'	),
		(	'DISTRICT_WATER_STREET_CARNIVAL',		'CSC_BAKERS_CULTURE_TO_ADJACENT_DISTRICT'	),
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'CSC_WATER_PARK_GOLD_TO_BAKERS'				),
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'CSC_WATER_STREET_CARNIVAL_GOLD_TO_BAKERS'	);

--		(	'DISTRICT_CSC_BAKERS_QUARTER',			'CSC_BREWERS_PRODUCTION_TO_BAKERS'			),
--		(	'DISTRICT_CSC_BREWERS_QUARTER',			'CSC_BAKERS_GOLD_TO_BREWERS'				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Ruivo_New_Adjacency
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO Ruivo_New_Adjacency (
    ID,
    DistrictType,
    ProvideType,
    YieldType,
    YieldChange,
    AdjacencyType,
    CustomAdjacentObject,
    Rings,
	MustOwn,
    DistrictModifiers	) VALUES

(	'CSC_BAKERS_PRODUCTION_FROM_BASE',
	'DISTRICT_CSC_BAKERS_QUARTER',
	'SelfBonus',
	'YIELD_PRODUCTION',
	1,
	'FROM_RINGS_TYPETAG_RESOURCE',
	'CLASS_CSC_BAKERS_BASE',
	1,
	1,
	1
),
(	'CSC_BAKERS_PRODUCTION_FROM_SPEC',
	'DISTRICT_CSC_BAKERS_QUARTER',
	'SelfBonus',
	'YIELD_PRODUCTION',
	1,
	'FROM_RINGS_TYPETAG_RESOURCE',
	'CLASS_CSC_BAKERS_SPEC',
	1,
	1,
	1
);

INSERT OR IGNORE INTO Ruivo_New_Adjacency (
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
	WhoIsTheOwner	) VALUES

(	'CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS',
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
);

INSERT OR IGNORE INTO Ruivo_New_Adjacency (
	ID,
	DistrictType,
	ProvideType,
	YieldType,
	YieldChange,
	AdjacencyType,
	Rings,
	DistrictModifiers,
	ModifierOwner,
	WhoIsTheOwner	) VALUES

(	'CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER',
	'DISTRICT_CSC_BAKERS_QUARTER',
	'SelfBonus',
	'YIELD_PRODUCTION',
	0.5,
	'FROM_RIVER_CROSSING',
	1,
	1,
	'BuildingModifiers',
	'BUILDING_CSC_BAKERS_WATER_MILL'
);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	DistrictModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO DistrictModifiers

		(	DistrictType,							ModifierId										)	VALUES

--  Set flags for river access, used by Water Mill and Wind Mill variants
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'MOD_CSC_BAKERS_RIVER_ACCESS_FLAG'				),
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'MOD_CSC_BAKERS_NO_RIVER_ACCESS_FLAG'			);

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to each adjacent base or specialty materials resource



--===========================================================================================================================================================================--
/*	STAGES 2-4 - BUILDINGS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
/*	WATER MILL & PALGUM */
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Remove the standard game Water Mill
DELETE FROM Buildings WHERE BuildingType='BUILDING_WATER_MILL';

-- Palgum no longer replaces the Water Mill
DELETE FROM BuildingReplaces WHERE CivUniqueBuildingType='BUILDING_PALGUM';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

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
			AdvisorType	)
VALUES	(
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_RIVER_ACCESS',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_RIVER_ACCESS_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_RIVER_ACCESS_DESCRIPTION',
		/*  PrereqTech, */			NULL,
		/*  PrereqCivic, */			NULL,
		/*  Cost, */				0,
		/*  PrereqDistrict, */		'DISTRICT_CSC_BAKERS_QUARTER',
		/*  PurchaseYield, */		NULL,
		/*  Maintenance, */			0,
		/*	CitizenSlots */			0,
		/*  Entertainment */		0,
		/*  AdvisorType */			'ADVISOR_GENERIC'
									),
		(
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_NO_RIVER_ACCESS_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_NO_RIVER_ACCESS_DESCRIPTION',
		/*  PrereqTech, */			NULL,
		/*  PrereqCivic, */			NULL,
		/*  Cost, */				0,
		/*  PrereqDistrict, */		'DISTRICT_CSC_BAKERS_QUARTER',
		/*  PurchaseYield, */		NULL,
		/*  Maintenance, */			0,
		/*	CitizenSlots */			0,
		/*  Entertainment */		0,
		/*  AdvisorType */			'ADVISOR_GENERIC'
									),
		(
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_WIND_MILL',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_WIND_MILL_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_WIND_MILL_DESCRIPTION',
		/*  PrereqTech, */			'TECH_THE_WHEEL',
		/*  PrereqCivic, */			NULL,
		/*  Cost, */				80,
		/*  PrereqDistrict, */		'DISTRICT_CSC_BAKERS_QUARTER',
		/*  PurchaseYield, */		'YIELD_GOLD',
		/*  Maintenance, */			1,
		/*	CitizenSlots */			0,
		/*  Entertainment */		0,
		/*  AdvisorType */			'ADVISOR_GENERIC'
									),
		(
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_WATER_MILL',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_WATER_MILL_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_WATER_MILL_DESCRIPTION',
		/*  PrereqTech, */			'TECH_THE_WHEEL',
		/*  PrereqCivic, */			NULL,
		/*  Cost, */				80,
		/*  PrereqDistrict, */		'DISTRICT_CSC_BAKERS_QUARTER',
		/*  PurchaseYield, */		'YIELD_GOLD',
		/*  Maintenance, */			1,
		/*	CitizenSlots */			0,
		/*  Entertainment */		0,
		/*  AdvisorType */			'ADVISOR_GENERIC'
									),
		(
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_BAKERY',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_BAKERY_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_BAKERY_DESCRIPTION',
		/*  PrereqTech, */			NULL,
		/*  PrereqCivic, */			'CIVIC_GUILDS',
		/*  Cost, */				160,
		/*  PrereqDistrict, */		'DISTRICT_CSC_BAKERS_QUARTER',
		/*  PurchaseYield, */		'YIELD_GOLD',
		/*  Maintenance, */			2,
		/*	CitizenSlots */			1,
		/*  Entertainment */		1,
		/*  AdvisorType */			'ADVISOR_GENERIC'
									),
		(
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_CAFE',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_CAFE_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION',
		/*  PrereqTech, */			NULL,
		/*  PrereqCivic, */			'CIVIC_HUMANISM',
		/*  Cost, */				250,
		/*  PrereqDistrict, */		'DISTRICT_CSC_BAKERS_QUARTER',
		/*  PurchaseYield, */		'YIELD_GOLD',
		/*  Maintenance, */			3,
		/*	CitizenSlots */			1,
		/*  Entertainment */		1,
		/*  AdvisorType */			'ADVISOR_GENERIC'
									),
		(
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_DESCRIPTION',
		/*  PrereqTech, */			NULL,
		/*  PrereqCivic, */			NULL,
		/*  Cost, */				0,
		/*  PrereqDistrict, */		'DISTRICT_CITY_CENTER',
		/*  PurchaseYield, */		NULL,
		/*  Maintenance, */			0,
		/*	CitizenSlots */			1,
		/*  Entertainment */		0,
		/*  AdvisorType */			'ADVISOR_GENERIC'
									),
		(
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_DESCRIPTION',
		/*  PrereqTech, */			NULL,
		/*  PrereqCivic, */			NULL,
		/*  Cost, */				0,
		/*  PrereqDistrict, */		'DISTRICT_COMMERCIAL_HUB',
		/*  PurchaseYield, */		NULL,
		/*  Maintenance, */			0,
		/*	CitizenSlots */			1,
		/*  Entertainment */		0,
		/*  AdvisorType */			'ADVISOR_GENERIC'
									),
		(
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_DESCRIPTION',
		/*  PrereqTech, */			NULL,
		/*  PrereqCivic, */			NULL,
		/*  Cost, */				0,
		/*  PrereqDistrict, */		'DISTRICT_ENTERTAINMENT_COMPLEX',
		/*  PurchaseYield, */		NULL,
		/*  Maintenance, */			0,
		/*	CitizenSlots */			1,
		/*  Entertainment */		0,
		/*  AdvisorType */			'ADVISOR_GENERIC'
									),
		(
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_DESCRIPTION',
		/*  PrereqTech, */			NULL,
		/*  PrereqCivic, */			NULL,
		/*  Cost, */				0,
		/*  PrereqDistrict, */		'DISTRICT_WATER_ENTERTAINMENT_COMPLEX',
		/*  PurchaseYield, */		NULL,
		/*  Maintenance, */			0,
		/*	CitizenSlots */			1,
		/*  Entertainment */		0,
		/*  AdvisorType */			'ADVISOR_GENERIC'
									);

UPDATE Buildings SET RegionalRange=6 WHERE BuildingType='BUILDING_CSC_BAKERS_CAFE';

UPDATE Buildings
SET MustPurchase = 1
WHERE BuildingType IN (
    'BUILDING_CSC_BAKERS_RIVER_ACCESS',
    'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',
	'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',
    'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',
    'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',
    'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER'
);

INSERT INTO CivilopediaPageExcludes
		(	SectionId,			PageId	) VALUES	
		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_RIVER_ACCESS'				),
		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'			);
--		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_STAGE_2_SERVICE'			),
--		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_STAGE_3_SERVICE'			),
--		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER'		),
--		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER'		);

UPDATE Buildings SET Description = '{LOC_BUILDING_GRANARY_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_2_EFFECT}' WHERE BuildingType='BUILDING_GRANARY';
UPDATE Buildings SET Description = '{LOC_BUILDING_MARKET_EXPANSION1_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_3_EFFECT}' WHERE BuildingType='BUILDING_MARKET';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings_XP2
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

INSERT OR IGNORE INTO Buildings_XP2

		(	BuildingType,										Pillage		)
VALUES	(	'BUILDING_CSC_BAKERS_RIVER_ACCESS',					0			),
		(	'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',				0			),
		(	'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',				0			),
		(	'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',				0			),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',		0			),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',		0			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingPrereqs
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

INSERT OR IGNORE INTO BuildingPrereqs

        (	Building,      		        				PrereqBuilding										)
VALUES	(	'BUILDING_CSC_BAKERS_WATER_MILL',			'BUILDING_CSC_BAKERS_RIVER_ACCESS'					),
		
		(	'BUILDING_CSC_BAKERS_BAKERY',				'BUILDING_CSC_BAKERS_WIND_MILL'						),
		(	'BUILDING_CSC_BAKERS_BAKERY',				'BUILDING_CSC_BAKERS_WATER_MILL'					),

		(	'BUILDING_CSC_BAKERS_CAFE',					'BUILDING_CSC_BAKERS_WIND_MILL'						),
		(	'BUILDING_CSC_BAKERS_CAFE',					'BUILDING_CSC_BAKERS_WATER_MILL'					);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	MutuallyExclusiveBuildings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

INSERT OR IGNORE INTO MutuallyExclusiveBuildings

        (	Building,      		        				MutuallyExclusiveBuilding							)
VALUES  (	'BUILDING_CSC_BAKERS_WATER_MILL',			'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'				),
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'BUILDING_CSC_BAKERS_WIND_MILL'						),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'BUILDING_CSC_BAKERS_WATER_MILL'					);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Building_GreatPersonPoints
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

INSERT INTO Building_GreatPersonPoints

        (	BuildingType,      		        			GreatPersonClassType,				PointsPerTurn	)
VALUES  (	'BUILDING_CSC_BAKERS_BAKERY',       		'GREAT_PERSON_CLASS_MERCHANT',		1				),
		(	'BUILDING_CSC_BAKERS_CAFE',       			'GREAT_PERSON_CLASS_MERCHANT',		1				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Building_CitizenYieldChanges
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

INSERT INTO Building_CitizenYieldChanges

        (	BuildingType,      		        					YieldType,       						YieldChange	        )
VALUES  (	'BUILDING_CSC_BAKERS_BAKERY',       				'YIELD_FOOD',	        				2		        	),
		(	'BUILDING_CSC_BAKERS_BAKERY',       				'YIELD_GOLD',	        				1		        	),

		(	'BUILDING_CSC_BAKERS_CAFE',       					'YIELD_FOOD',	        				1		        	),
		(	'BUILDING_CSC_BAKERS_CAFE',       					'YIELD_GOLD',	        				2		        	),

		(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',		'YIELD_CULTURE',	        			2		        	),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',		'YIELD_GOLD',	        				2		        	),

		(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',		'YIELD_CULTURE',	        			2		        	),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',		'YIELD_GOLD',	        				2		        	);
		
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT INTO BuildingModifiers

        (	BuildingType,		            			ModifierId											)	VALUES

--	WIND / WATER MILL -------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent base materials improvements

--  +1 Food (with a -1 Gold maintenance cost)
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_WATER_MILL_SELF_FOOD'				),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_WIND_MILL_SELF_FOOD'				),

-- 	+1 Food to an adjacent Granary (+1 Gold return moved to CSC_Q_BAKERS_GOLD.sql)
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER'		),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER'		),

--  Mirror the adjacent Granary transaction back onto Mill cities for alternate mill art
		(	'BUILDING_GRANARY',							'MOD_CSC_BAKERS_STAGE_2_PROP_ATTACH_BAKERS_WATER'	),
		(	'BUILDING_GRANARY',							'MOD_CSC_BAKERS_STAGE_2_PROP_ATTACH_BAKERS_WIND'	),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth, gains a Storekeeper service, and sets a city property for art selection
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER'	),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND'	),
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY_WATER'	),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY_WIND'	),

--	BAKERY ------------------------------------------------------------------------------

--  +1 Production from the local Flour Mill
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY'			),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY'			),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to the Flour Mill in the Quarter

--  +2 Food (with a -2 Gold maintenance cost)
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_BAKERY_SELF_FOOD'					),

--  +0.2 Food per Citizen to the city for each adjacent Market (+0.2 Gold moved to CSC_Q_BAKERS_GOLD.sql)
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_BAKERY_ATTACH_COMMERCIAL_HUB'		),

--  Mirror the adjacent Market transaction back onto the City of adjacent Bakeries for alternate Bakery art
		(	'BUILDING_MARKET',							'MOD_CSC_BAKERS_STAGE_3_PROP_ATTACH_BAKERS_QUARTER'	),
		(	'BUILDING_SUKIENNICE',						'MOD_CSC_BAKERS_STAGE_3_PROP_ATTACH_BAKERS_QUARTER'	),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
-- 	Grant the Stage 3 Service to a Commercial Hub with a Market
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_STAGE_3_SERVICE_ATTACH_COMHUB'		),
--  Each adjacent Bakery grants the Stage 3 Service +2 Housing
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB'		),

--	CAFE --------------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent specialty materials improvements

--  +1 Production from the local Flour Mill
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE'			),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE'			),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to the Flour Mill in the Quarter

--  +3 Food (with a -3 Gold maintenance cost)
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_CAFE_SELF_FOOD'						),

--  See end of file for: +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2 Tourism to an Entertainment Complex, Water Park
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT'),
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK'	),

--  Mirror the adjacent Zoo/Ferris Wheel transactions back onto Cafe cities for alternate Cafe art
		(	'BUILDING_ZOO',								'MOD_CSC_BAKERS_STAGE_4_PROP_ATTACH_BAKERS_CAFE_ENTER'	),
		(	'BUILDING_FERRIS_WHEEL',					'MOD_CSC_BAKERS_STAGE_4_PROP_ATTACH_BAKERS_CAFE_WATER'	),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_ENTER'		),
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_WATER'		),

--	SHARED ------------------------------------------------------------------------------

-- 	+1 Food bonus to trade routes to the city (+1 Gold return moved to CSC_Q_BAKERS_GOLD.sql)
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD'					),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD'					),
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD'					),
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD'					);



--===========================================================================================================================================================================--
/*	CIVICS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Civics
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

UPDATE Civics SET Description = '{LOC_CIVIC_FEUDALISM_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_2_CIVIC}' WHERE CivicType = 'CIVIC_FEUDALISM';
UPDATE Civics SET Description = '{LOC_CSC_BAKERS_STAGE_3_CIVIC}' WHERE CivicType = 'CIVIC_MEDIEVAL_FAIRES';
UPDATE Civics SET Description = '{LOC_CSC_BAKERS_STAGE_4_CIVIC}' WHERE CivicType = 'CIVIC_URBANIZATION';



--===========================================================================================================================================================================--
/*	MODIFIERS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	DynamicModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO DynamicModifiers

        ( 	ModifierType,                                                   	CollectionType,                         EffectType	                        			)	VALUES
		(	'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',					'COLLECTION_PLAYER_DISTRICTS',			'EFFECT_ATTACH_MODIFIER'						),
		(	'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',					'COLLECTION_PLAYER_IMPROVEMENTS',		'EFFECT_ATTACH_MODIFIER'						);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO Modifiers

		(	ModifierId,															ModifierType,													OwnerRequirementSetId,						SubjectRequirementSetId								)	VALUES	

-- 	BAKERS QUARTER ----------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to each adjacent base or specialty materials resource

--	FLOUR MILL --------------------------------------------------------------------------

--  Set flags for river access, used by Water Mill and Wind Mill variants
		(	'MOD_CSC_BAKERS_RIVER_ACCESS_FLAG',									'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',			NULL,										'REQSET_CSC_PLOT_ADJ_TO_RIVER'						),
		(	'MOD_CSC_BAKERS_NO_RIVER_ACCESS_FLAG',								'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',			NULL,										'REQSET_CSC_PLOT_NOT_ADJ_TO_RIVER'					),

--  +1 Production to the Water Mill from improved base materials
		(  	'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER',				'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_BAKERS_PLOT_HAS_BASE', 			'REQSET_CSC_ADJ_BAKERS_QUARTER'						),
        (  	'MOD_CSC_BAKERS_BASE_IMPROV_PROD_TO_ADJ_WATER_MILL',    			'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,                           			NULL												),

--  +1 Production to the Wind Mill from improved base materials
		(  	'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND',				'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_BAKERS_PLOT_HAS_BASE', 			'REQSET_CSC_ADJ_BAKERS_QUARTER'						),
        (  	'MOD_CSC_BAKERS_BASE_IMPROV_PROD_TO_ADJ_WIND_MILL',    				'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,                           			NULL												),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent base materials improvements

--  +1 Food (with a -1 Gold maintenance cost)
		(	'MOD_CSC_BAKERS_WATER_MILL_SELF_FOOD',								'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),
		(	'MOD_CSC_BAKERS_WIND_MILL_SELF_FOOD',								'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

-- 	+1 Food to an adjacent Granary (+1 Gold return moved to CSC_Q_BAKERS_GOLD.sql)
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL, 										'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'				),
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',    				'MODIFIER_BUILDING_YIELD_CHANGE',  								NULL,                           			NULL												),
--  Art bridge: Granaries set the source property on adjacent Water/Wind Mill transaction cities
		(	'MOD_CSC_BAKERS_STAGE_2_PROP_ATTACH_BAKERS_WATER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERS_STAGE_2_ART_WATER'			),
		(	'MOD_CSC_BAKERS_STAGE_2_PROP_WATER',								'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',							NULL,										NULL												),
		(	'MOD_CSC_BAKERS_STAGE_2_PROP_ATTACH_BAKERS_WIND',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERS_STAGE_2_ART_WIND'			),
		(	'MOD_CSC_BAKERS_STAGE_2_PROP_WIND',									'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',							NULL,										NULL												),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth, gains a Storekeeper service, and sets a city property for art selection
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_2_EFFECT_PREREQ',			'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'				),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER',						'MODIFIER_SINGLE_CITY_ADJUST_CITY_GROWTH',						NULL,										NULL												),
		(	'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY_WATER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_2_EFFECT_PREREQ',			'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'				),

		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_2_EFFECT_PREREQ',			'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'				),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND',						'MODIFIER_SINGLE_CITY_ADJUST_CITY_GROWTH',						NULL,										NULL												),
		(	'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY_WIND',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_2_EFFECT_PREREQ',			'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'				),
		(	'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT',								'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',			NULL,										NULL												),

--	BAKERY ------------------------------------------------------------------------------

--  +1 Production from the local Flour Mill
		(	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY',							'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

--  +2 Food (with a -2 Gold maintenance cost)
		(	'MOD_CSC_BAKERS_BAKERY_SELF_FOOD',									'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

--  +0.2 Food per Citizen to the city for each adjacent Market (+0.2 Gold moved to CSC_Q_BAKERS_GOLD.sql)
		(	'MOD_CSC_BAKERS_BAKERY_ATTACH_COMMERCIAL_HUB',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_MARKET'								),
		(	'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET',								'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',		NULL,										NULL												),
--  Art bridge: Markets set the source property on adjacent Bakery transaction cities
		(	'MOD_CSC_BAKERS_STAGE_3_PROP_ATTACH_BAKERS_QUARTER',				'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERY_STAGE_3_ART'					),
		(	'MOD_CSC_BAKERS_STAGE_3_PROP_HOUSING',								'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',							NULL,										NULL												),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:

-- 	Grant the Stage 3 Service to a Commercial Hub with a Market
		(	'MOD_CSC_BAKERS_STAGE_3_SERVICE_ATTACH_COMHUB',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_3_EFFECT_PREREQ',			'REQSET_CSC_ADJ_MARKET'								),
		(	'MOD_CSC_BAKERS_STAGE_3_SERVICE_GRANT',								'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',			NULL,										NULL												),
--  An adjacent Stage 3 Service provides +2 Housing
		(	'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_3_EFFECT_PREREQ',			'REQSET_CSC_ADJ_MARKET'								),
		(	'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING',							'MODIFIER_SINGLE_CITY_ADJUST_BUILDING_HOUSING',					NULL,										NULL												),
		
-- 	CAFE --------------------------------------------------------------------------

--  +1 Production to the Café from improved specialty materials
        (	'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',			'REQSET_CSC_ADJ_BAKERS_QUARTER'						),
        (  	'MOD_CSC_BAKERS_SPEC_IMPROV_PROD_TO_ADJ_CAFE',    					'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,                           			NULL												),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent specialty materials improvements

--  +1 Production from the local Flour Mill
		(	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE',							'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

--  +3 Food (with a -3 Gold maintenance cost)
		(	'MOD_CSC_BAKERS_CAFE_SELF_FOOD',									'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

--  +1 Culture for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel (+1 Gold moved to CSC_Q_BAKERS_GOLD.sql)
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',								'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',							'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),
--  Art bridge: Zoos and Ferris Wheels set the source property on adjacent Cafe transaction cities
		(	'MOD_CSC_BAKERS_STAGE_4_PROP_ATTACH_BAKERS_CAFE_ENTER',				'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_CAFE_STAGE_4_ART'					),
		(	'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_ENTER',						'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',							NULL,										NULL												),
		(	'MOD_CSC_BAKERS_STAGE_4_PROP_ATTACH_BAKERS_CAFE_WATER',				'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_CAFE_STAGE_4_ART'					),
		(	'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_WATER',						'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',							NULL,										NULL												),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',				'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_4_EFFECT_PREREQ',			'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'			),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER',						'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',				NULL,										NULL												),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_4_EFFECT_PREREQ',			'REQSET_CSC_ADJ_WATER_PARK_FERRIS'					),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER',						'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',				NULL,										NULL												),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_ENTER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_4_EFFECT_PREREQ',			'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'			),
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER',					'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',			NULL,										NULL												),
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_WATER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_4_EFFECT_PREREQ',			'REQSET_CSC_ADJ_WATER_PARK_FERRIS'					),
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER',					'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',			NULL,										NULL												),

-- 	SHARED ------------------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to the Flour Mill in the Quarter

-- 	+1 Food bonus to trade routes to the city (+1 Gold return moved to CSC_Q_BAKERS_GOLD.sql)
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD',									'MODIFIER_SINGLE_CITY_ADJUST_TRADE_ROUTE_YIELD_TO_OTHERS',		NULL,										NULL												);



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		
INSERT OR IGNORE INTO ModifierArguments
		
        (	ModifierId,			                      							Name,                       Value		                									)	VALUES

-- 	BAKERS QUARTER ----------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to each adjacent base or specialty materials resource

-- 	FLOUR MILL --------------------------------------------------------------------------

--  Set flags for river access, used by Water Mill and Wind Mill variants
		(	'MOD_CSC_BAKERS_RIVER_ACCESS_FLAG',									'BuildingType',				'BUILDING_CSC_BAKERS_RIVER_ACCESS'								),
		(	'MOD_CSC_BAKERS_NO_RIVER_ACCESS_FLAG',								'BuildingType',				'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'							),

--  +1 Production to the Water Mill from improved base materials
		(  	'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER',				'ModifierId',         		'MOD_CSC_BAKERS_BASE_IMPROV_PROD_TO_ADJ_WATER_MILL'     		),    
        (  	'MOD_CSC_BAKERS_BASE_IMPROV_PROD_TO_ADJ_WATER_MILL',				'BuildingType',           	'BUILDING_CSC_BAKERS_WATER_MILL'								),
        (  	'MOD_CSC_BAKERS_BASE_IMPROV_PROD_TO_ADJ_WATER_MILL',				'YieldType',           		'YIELD_PRODUCTION'                                              ),
        ( 	'MOD_CSC_BAKERS_BASE_IMPROV_PROD_TO_ADJ_WATER_MILL',				'Amount',             		1                                                               ),

--  +1 Production to the Wind Mill from improved base materials
		(  	'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND',				'ModifierId',         		'MOD_CSC_BAKERS_BASE_IMPROV_PROD_TO_ADJ_WIND_MILL'     			),    
        (  	'MOD_CSC_BAKERS_BASE_IMPROV_PROD_TO_ADJ_WIND_MILL',					'BuildingType',           	'BUILDING_CSC_BAKERS_WIND_MILL'									),
        (  	'MOD_CSC_BAKERS_BASE_IMPROV_PROD_TO_ADJ_WIND_MILL',					'YieldType',           		'YIELD_PRODUCTION'                                              ),
        ( 	'MOD_CSC_BAKERS_BASE_IMPROV_PROD_TO_ADJ_WIND_MILL',					'Amount',             		1                                                               ),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent base materials improvements

--  +1 Food (with a -1 Gold maintenance cost)
        (  	'MOD_CSC_BAKERS_WATER_MILL_SELF_FOOD',								'BuildingType',           	'BUILDING_CSC_BAKERS_WATER_MILL'								),
        (  	'MOD_CSC_BAKERS_WATER_MILL_SELF_FOOD',								'YieldType',           		'YIELD_FOOD'                                             		),
        ( 	'MOD_CSC_BAKERS_WATER_MILL_SELF_FOOD',								'Amount',             		1                                                               ),
        (  	'MOD_CSC_BAKERS_WIND_MILL_SELF_FOOD',								'BuildingType',           	'BUILDING_CSC_BAKERS_WIND_MILL'									),
        (  	'MOD_CSC_BAKERS_WIND_MILL_SELF_FOOD',								'YieldType',           		'YIELD_FOOD'                                              		),
        ( 	'MOD_CSC_BAKERS_WIND_MILL_SELF_FOOD',								'Amount',             		1                                                               ),

-- 	+1 Food to an adjacent Granary (+1 Gold return moved to CSC_Q_BAKERS_GOLD.sql)
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER',						'ModifierId',				'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY'					),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',					'BuildingType',				'BUILDING_GRANARY'												),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',					'YieldType',				'YIELD_FOOD'													),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',					'Amount',					1																),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth, gains a Storekeeper service, and sets a city property for art selection
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER'					),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER',						'Amount',					10																),
		(	'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY_WATER',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT'							),
--  Source property consumed by Lua, then exposed to GamePropertyRanges for mill SelectionRules
		(	'MOD_CSC_BAKERS_STAGE_2_PROP_ATTACH_BAKERS_WATER',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_2_PROP_WATER'								),
		(	'MOD_CSC_BAKERS_STAGE_2_PROP_WATER',								'Key',						'CSC_BAKERS_STAGE_2_EFFECT_GROWTH'								),
		(	'MOD_CSC_BAKERS_STAGE_2_PROP_WATER',								'Amount',					1																),

		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND'						),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND',						'Amount',					10																),
		(	'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY_WIND',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT'							),
		(	'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT',								'BuildingType',				'BUILDING_CSC_BAKERS_STAGE_2_SERVICE'							),
--  Same source property as Water Mill; these buildings are mutually exclusive in the Quarter
		(	'MOD_CSC_BAKERS_STAGE_2_PROP_ATTACH_BAKERS_WIND',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_2_PROP_WIND'								),
		(	'MOD_CSC_BAKERS_STAGE_2_PROP_WIND',									'Key',						'CSC_BAKERS_STAGE_2_EFFECT_GROWTH'								),
		(	'MOD_CSC_BAKERS_STAGE_2_PROP_WIND',									'Amount',					1																),

--	BAKERY ------------------------------------------------------------------------------

--  +1 Production from the local Flour Mill
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY',							'BuildingType',           	'BUILDING_CSC_BAKERS_BAKERY'									),
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY',							'YieldType',           		'YIELD_PRODUCTION'                                             	),
        ( 	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY',							'Amount',             		1                                                               ),

--  +2 Food (with a -2 Gold maintenance cost)
        (  	'MOD_CSC_BAKERS_BAKERY_SELF_FOOD',									'BuildingType',           	'BUILDING_CSC_BAKERS_BAKERY'									),
        (  	'MOD_CSC_BAKERS_BAKERY_SELF_FOOD',									'YieldType',           		'YIELD_FOOD'                                             		),
        ( 	'MOD_CSC_BAKERS_BAKERY_SELF_FOOD',									'Amount',             		2                                                               ),

--  +0.2 Food per Citizen to the city for each adjacent Market (+0.2 Gold moved to CSC_Q_BAKERS_GOLD.sql)
		(	'MOD_CSC_BAKERS_BAKERY_ATTACH_COMMERCIAL_HUB',						'ModifierId',				'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET'							),
		(	'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET',								'YieldType',				'YIELD_FOOD'													),
		(	'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET',								'Amount',					0.2																),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
-- 	Grant the Stage 3 Service to a Commercial Hub with a Market
		(	'MOD_CSC_BAKERS_STAGE_3_SERVICE_ATTACH_COMHUB',						'ModifierId',				'MOD_CSC_BAKERS_STAGE_3_SERVICE_GRANT'							),
		(	'MOD_CSC_BAKERS_STAGE_3_SERVICE_GRANT',								'BuildingType',				'BUILDING_CSC_BAKERS_STAGE_3_SERVICE'							),
--  An adjacent Market provides +2 Housing
		(	'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',						'ModifierId',				'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING'							),
		(	'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING',							'Amount',					2																),
--  Source property consumed by Lua, then exposed to GamePropertyRanges for Bakery SelectionRules
		(	'MOD_CSC_BAKERS_STAGE_3_PROP_ATTACH_BAKERS_QUARTER',				'ModifierId',				'MOD_CSC_BAKERS_STAGE_3_PROP_HOUSING'							),
		(	'MOD_CSC_BAKERS_STAGE_3_PROP_HOUSING',								'Key',						'CSC_BAKERS_STAGE_3_EFFECT_HOUSING'								),
		(	'MOD_CSC_BAKERS_STAGE_3_PROP_HOUSING',								'Amount',					1																),

-- 	CAFE --------------------------------------------------------------------------

--  +1 Production to the Café from improved specialty materials
		(  	'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER',					'ModifierId',         		'MOD_CSC_BAKERS_SPEC_IMPROV_PROD_TO_ADJ_CAFE'     				),    
        (  	'MOD_CSC_BAKERS_SPEC_IMPROV_PROD_TO_ADJ_CAFE',						'BuildingType',           	'BUILDING_CSC_BAKERS_CAFE'										),
        (  	'MOD_CSC_BAKERS_SPEC_IMPROV_PROD_TO_ADJ_CAFE',						'YieldType',           		'YIELD_PRODUCTION'                                              ),
        ( 	'MOD_CSC_BAKERS_SPEC_IMPROV_PROD_TO_ADJ_CAFE',						'Amount',             		1                                                               ),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent specialty materials improvements

--  +1 Production from the local Flour Mill
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE',							'BuildingType',				'BUILDING_CSC_BAKERS_CAFE'										),
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE',							'YieldType',           		'YIELD_PRODUCTION'                                             	),
        ( 	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE',							'Amount',             		1                                                               ),

--  +3 Food (with a -3 Gold maintenance cost)
        (  	'MOD_CSC_BAKERS_CAFE_SELF_FOOD',									'BuildingType',           	'BUILDING_CSC_BAKERS_CAFE'										),
        (  	'MOD_CSC_BAKERS_CAFE_SELF_FOOD',									'YieldType',           		'YIELD_FOOD'                                             		),
        ( 	'MOD_CSC_BAKERS_CAFE_SELF_FOOD',									'Amount',             		3                                                               ),

--  +1 Culture for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel (+1 Gold moved to CSC_Q_BAKERS_GOLD.sql)
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',								'BuildingType',				'BUILDING_ZOO'													),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',								'YieldType',				'YIELD_CULTURE'													),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',								'Amount',					1																),

		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',							'BuildingType',				'BUILDING_FERRIS_WHEEL'											),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',							'YieldType',				'YIELD_CULTURE'													),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',							'Amount',					1																),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',				'ModifierId',				'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER'					),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER',						'Amount',					2																),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER'					),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER',						'Amount',					2																),
--  Source property consumed by Lua, then exposed to GamePropertyRanges for Cafe SelectionRules
		(	'MOD_CSC_BAKERS_STAGE_4_PROP_ATTACH_BAKERS_CAFE_ENTER',				'ModifierId',				'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_ENTER'						),
		(	'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_ENTER',						'Key',						'CSC_BAKERS_STAGE_4_EFFECT_TOURISM'								),
		(	'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_ENTER',						'Amount',					1																),
		(	'MOD_CSC_BAKERS_STAGE_4_PROP_ATTACH_BAKERS_CAFE_WATER',				'ModifierId',				'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_WATER'						),
		(	'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_WATER',						'Key',						'CSC_BAKERS_STAGE_4_EFFECT_TOURISM'								),
		(	'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_WATER',						'Amount',					1																),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_ENTER',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER'					),
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER',					'BuildingType',				'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER'					),
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_WATER',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER'					),
		(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER',					'BuildingType',				'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER'					),

-- 	SHARED ------------------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to the Flour Mill in the Quarter

-- 	+1 Food bonus to trade routes to the city (+1 Gold return moved to CSC_Q_BAKERS_GOLD.sql)
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD',									'YieldType',				'YIELD_FOOD'													),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD',									'Amount',					1																),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD',									'Domestic',					1																);



--===========================================================================================================================================================================--
/*	REQUIREMENTS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		
INSERT OR IGNORE INTO RequirementSets 
		
        (	RequirementSetId,                              			RequirementSetType              )	VALUES

-- 	BAKERS QUARTER ----------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: REQSET_CSC_BAKERS_ADJ_PLOT_HAS_MATERIAL_ANY, REQSET_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY

-- 	FLOUR MILL --------------------------------------------------------------------------

--  Set flags for river access, used by Water Mill and Wind Mill variants
		(	'REQSET_CSC_PLOT_ADJ_TO_RIVER',							'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_PLOT_NOT_ADJ_TO_RIVER',						'REQUIREMENTSET_TEST_ALL'		),

-- 	+1 Production from each adjacent base materials improvement
		(	'REQSET_CSC_BAKERS_PLOT_HAS_BASE',						'REQUIREMENTSET_TEST_ALL'       ),

--  Helper set for improved adjacent base materials prerequisite
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE',					'REQUIREMENTSET_TEST_ALL'       ),

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
		(	'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',					'REQUIREMENTSET_TEST_ALL'		),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
-- 	+1 Citizen slot (Merchant Guildhall) to a Commercial Hub with a Market
		(	'REQSET_CSC_STAGE_2_EFFECT_PREREQ',						'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_ADJ_BAKERS_STAGE_2_ART_WATER',				'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_ADJ_BAKERS_STAGE_2_ART_WIND',				'REQUIREMENTSET_TEST_ALL'		),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.2 Food per Citizen to the city for each adjacent Market (REQSET_CSC_ADJ_BAKERY moved to CSC_Q_BAKERS_GOLD.sql)
		(	'REQSET_CSC_ADJ_MARKET',								'REQUIREMENTSET_TEST_ALL'		),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
-- UNUSED: no live modifier references this stricter Stage 3 service adjacency set; Stage 3 service/effect modifiers use REQSET_CSC_ADJ_MARKET.
--		(	'REQSET_CSC_ADJ_BAKERS_STAGE_3_SERVICE',				'REQUIREMENTSET_TEST_ALL'		),
--  An adjacent Market provides +2 Housing
		(	'REQSET_CSC_STAGE_3_EFFECT_PREREQ', 					'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_ADJ_BAKERY_STAGE_3_ART',					'REQUIREMENTSET_TEST_ALL'		),

-- 	CAFE --------------------------------------------------------------------------

-- 	+1 Production from each adjacent speciality materials improvement
		(	'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',						'REQUIREMENTSET_TEST_ALL'       ),

--  Helper set for improved adjacent specialty materials prerequisite
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC',					'REQUIREMENTSET_TEST_ALL'       ),

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel
		(	'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX',					'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_ADJ_WATER_PARK',							'REQUIREMENTSET_TEST_ALL'		),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
		(	'REQSET_CSC_STAGE_4_EFFECT_PREREQ',						'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_ADJ_CAFE_STAGE_4_ART',						'REQUIREMENTSET_TEST_ALL'		),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
		(	'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',				'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_ADJ_WATER_PARK_FERRIS',						'REQUIREMENTSET_TEST_ALL'		),

-- 	SHARED ------------------------------------------------------------------------------

-- UNUSED: wrapper set is not referenced by any modifier/nested requirement; keep REQ_CSC_DISTRICT_IS_BAKERS_QUARTER itself because active adjacency/art sets use it.
--		(	'REQSET_CSC_DISTRICT_IS_BAKERS',						'REQUIREMENTSET_TEST_ALL'		),
        (  	'REQSET_CSC_ADJ_BAKERS_QUARTER',          				'REQUIREMENTSET_TEST_ALL'       ),
		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',			'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',			'REQUIREMENTSET_TEST_ALL'		);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
				
INSERT OR IGNORE INTO RequirementSetRequirements
		
        (	RequirementSetId,		                      			RequirementId	                               	)	VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

--  Set flags for river access, used by Water Mill and Wind Mill variants
		(	'REQSET_CSC_PLOT_ADJ_TO_RIVER',							'REQ_CSC_PLOT_ADJ_TO_RIVER'						),
		(	'REQSET_CSC_PLOT_NOT_ADJ_TO_RIVER',						'REQ_CSC_PLOT_NOT_ADJ_TO_RIVER'					),

-- 	+1 Production from each adjacent base materials improvement
		(	'REQSET_CSC_BAKERS_PLOT_HAS_BASE',						'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'			),

--  Helper set for improved adjacent base materials prerequisite
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE',					'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE',					'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'			),

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
		( 	'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',					'REQ_CSC_PLOT_ADJ_TO_OWNER'              		),
        (  	'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',					'REQ_CSC_DISTRICT_IS_CITY_CENTER'           	),
		(	'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',					'REQ_CSC_CITY_HAS_GRANARY'						),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
-- 	+1 Citizen slot (Merchant Guildhall) to a Commercial Hub with a Market
		(	'REQSET_CSC_STAGE_2_EFFECT_PREREQ',						'REQ_CSC_STAGE_2_EFFECT_TECH_OR_CIVIC'			),
		(	'REQSET_CSC_STAGE_2_EFFECT_PREREQ',						'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'		),
		(	'REQSET_CSC_ADJ_BAKERS_STAGE_2_ART_WATER',				'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'			),
		(	'REQSET_CSC_ADJ_BAKERS_STAGE_2_ART_WATER',				'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_ADJ_BAKERS_STAGE_2_ART_WATER',				'REQ_CSC_CITY_HAS_WATER_MILL'					),
		(	'REQSET_CSC_ADJ_BAKERS_STAGE_2_ART_WIND',				'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'			),
		(	'REQSET_CSC_ADJ_BAKERS_STAGE_2_ART_WIND',				'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_ADJ_BAKERS_STAGE_2_ART_WIND',				'REQ_CSC_CITY_HAS_WIND_MILL'					),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.2 Food and +0.2 Gold per Citizen to the city for each adjacent Market
		(	'REQSET_CSC_ADJ_MARKET',								'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_ADJ_MARKET',								'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB'			),
		(	'REQSET_CSC_ADJ_MARKET',								'REQ_CSC_CITY_HAS_MARKET'						),

-- Shared with CSC_Q_BAKERS_GOLD.sql: inverse Market-to-Bakery adjacency requirements

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
-- UNUSED: no live modifier references REQSET_CSC_ADJ_BAKERS_STAGE_3_SERVICE.
--		(	'REQSET_CSC_ADJ_BAKERS_STAGE_3_SERVICE',				'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
--		(	'REQSET_CSC_ADJ_BAKERS_STAGE_3_SERVICE',				'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB'			),
--		(	'REQSET_CSC_ADJ_BAKERS_STAGE_3_SERVICE',				'REQ_CSC_CITY_HAS_BAKERS_STAGE_3_SERVICE'		),
--  An adjacent Market provides +2 Housing
		(	'REQSET_CSC_STAGE_3_EFFECT_PREREQ', 					'REQ_CSC_STAGE_3_EFFECT_TECH_OR_CIVIC'			),
		(	'REQSET_CSC_STAGE_3_EFFECT_PREREQ',						'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'		),
		(	'REQSET_CSC_ADJ_BAKERY_STAGE_3_ART',					'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'			),
		(	'REQSET_CSC_ADJ_BAKERY_STAGE_3_ART',					'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_ADJ_BAKERY_STAGE_3_ART',					'REQ_CSC_CITY_HAS_BAKERY'						),

-- 	CAFE --------------------------------------------------------------------------

-- 	+1 Production from each adjacent specialty materials improvement
		(	'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',						'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'			),

--  Helper set for improved adjacent specialty materials prerequisite
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC',					'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC',					'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'			),

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel
		(	'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX',					'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX',					'REQ_CSC_DISTRICT_IS_ENTERTAINMENT_COMPLEX'		),
		(	'REQSET_CSC_ADJ_WATER_PARK',							'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_ADJ_WATER_PARK',							'REQ_CSC_DISTRICT_IS_WATER_PARK'				),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
		(	'REQSET_CSC_STAGE_4_EFFECT_PREREQ',						'REQ_CSC_STAGE_4_EFFECT_TECH_OR_CIVIC'			),
		(	'REQSET_CSC_STAGE_4_EFFECT_PREREQ',						'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'		),
		(	'REQSET_CSC_STAGE_4_EFFECT_PREREQ',						'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC'		),
		(	'REQSET_CSC_ADJ_CAFE_STAGE_4_ART',						'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'			),
		(	'REQSET_CSC_ADJ_CAFE_STAGE_4_ART',						'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_ADJ_CAFE_STAGE_4_ART',						'REQ_CSC_CITY_HAS_CAFE'							),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
		(	'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',				'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX'				),
		(	'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',				'REQ_CSC_CITY_HAS_ZOO'							),
		(	'REQSET_CSC_ADJ_WATER_PARK_FERRIS',						'REQ_CSC_ADJ_WATER_PARK'						),
		(	'REQSET_CSC_ADJ_WATER_PARK_FERRIS',						'REQ_CSC_CITY_HAS_FERRIS'						),

-- 	SHARED ------------------------------------------------------------------------------
-- Moved to CSC_Q_BAKERS_GOLD.sql: REQSET_CSC_BAKERS_ADJ_PLOT_HAS_MATERIAL_ANY, REQSET_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY requirements
-- UNUSED: no live modifier/nested requirement references REQSET_CSC_DISTRICT_IS_BAKERS.
--		(	'REQSET_CSC_DISTRICT_IS_BAKERS',						'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'			),
        ( 	'REQSET_CSC_ADJ_BAKERS_QUARTER',						'REQ_CSC_PLOT_ADJ_TO_OWNER'              		),
        (  	'REQSET_CSC_ADJ_BAKERS_QUARTER',						'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'           	),

		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',			'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',			'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'			),
		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',			'REQ_CSC_PLOT_HAS_ANY_IMPROVEMENT'				),

		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',			'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',			'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'			),
		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',			'REQ_CSC_PLOT_HAS_ANY_IMPROVEMENT'				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Requirements
        
        (	RequirementId,		                          			RequirementType,	                                Inverse         )	VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

--  Set flags for river access, used by Water Mill and Wind Mill variants
		(	'REQ_CSC_PLOT_ADJ_TO_RIVER',							'REQUIREMENT_PLOT_ADJACENT_TO_RIVER',				0				),
		(	'REQ_CSC_PLOT_NOT_ADJ_TO_RIVER',						'REQUIREMENT_PLOT_ADJACENT_TO_RIVER',				1				),

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
		(	'REQ_CSC_DISTRICT_IS_CITY_CENTER',						'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',			0				),
		(	'REQ_CSC_CITY_HAS_GRANARY',								'REQUIREMENT_CITY_HAS_BUILDING',					0				),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
		(	'REQ_CSC_STAGE_2_EFFECT_TECH_OR_CIVIC',					'REQUIREMENT_PLAYER_HAS_CIVIC',						0				),
		(	'REQ_CSC_CITY_HAS_WATER_MILL',							'REQUIREMENT_CITY_HAS_BUILDING',					0				),
		(	'REQ_CSC_CITY_HAS_WIND_MILL',							'REQUIREMENT_CITY_HAS_BUILDING',					0				),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.2 Food and +0.2 Gold per Citizen to the city for each adjacent Market
		(	'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB',					'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',			0				),
		(	'REQ_CSC_CITY_HAS_MARKET',								'REQUIREMENT_CITY_HAS_BUILDING',					0				),
		(	'REQ_CSC_CITY_HAS_BAKERY',								'REQUIREMENT_CITY_HAS_BUILDING',					0				),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
-- UNUSED: only used by the orphan REQSET_CSC_ADJ_BAKERS_STAGE_3_SERVICE chain.
--		(	'REQ_CSC_CITY_HAS_BAKERS_STAGE_3_SERVICE',				'REQUIREMENT_CITY_HAS_BUILDING',					0				),
--  An adjacent Market provides +2 Housing
-- 	+1 Citizen slot (Merchant Guildhall) to a Commercial Hub with a Market
		(	'REQ_CSC_STAGE_3_EFFECT_TECH_OR_CIVIC',					'REQUIREMENT_PLAYER_HAS_CIVIC',						0				),

-- 	CAFE --------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel
		(	'REQ_CSC_DISTRICT_IS_ENTERTAINMENT_COMPLEX',			'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',			0				),
		(	'REQ_CSC_DISTRICT_IS_WATER_PARK',						'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',			0				),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
		(	'REQ_CSC_STAGE_4_EFFECT_TECH_OR_CIVIC',					'REQUIREMENT_PLAYER_HAS_CIVIC',						0				),
		(	'REQ_CSC_CITY_HAS_CAFE',									'REQUIREMENT_CITY_HAS_BUILDING',					0				),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
		(	'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX',					'REQUIREMENT_REQUIREMENTSET_IS_MET',				0				),
		(	'REQ_CSC_CITY_HAS_ZOO',									'REQUIREMENT_CITY_HAS_BUILDING',					0				),
		(	'REQ_CSC_ADJ_WATER_PARK',								'REQUIREMENT_REQUIREMENTSET_IS_MET',				0				),
		(	'REQ_CSC_CITY_HAS_FERRIS',								'REQUIREMENT_CITY_HAS_BUILDING',					0				),

-- 	SHARED ------------------------------------------------------------------------------

		(	'REQ_CSC_PLOT_ADJ_TO_OWNER',							'REQUIREMENT_PLOT_ADJACENT_TO_OWNER',              	0               ),
-- Moved to CSC_Q_BAKERS_GOLD.sql: REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY
		(	'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',				'REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES',			0				),
		(	'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC',				'REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES',			0				),
		(	'REQ_CSC_PLOT_HAS_ANY_IMPROVEMENT',            			'REQUIREMENT_PLOT_HAS_ANY_IMPROVEMENT',           	0               ),
		(   'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',					'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',          	0               ),
		(	'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',			'REQUIREMENT_COLLECTION_COUNT_ATLEAST',				0				),
		(	'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',			'REQUIREMENT_COLLECTION_COUNT_ATLEAST',				0				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementArguments 

        (	RequirementId,				               				Name,                           Value		                    				)	VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
		(	'REQ_CSC_DISTRICT_IS_CITY_CENTER',						'DistrictType',					'DISTRICT_CITY_CENTER'							),
		(	'REQ_CSC_CITY_HAS_GRANARY',								'BuildingType',					'BUILDING_GRANARY'								),
		(	'REQ_CSC_CITY_HAS_GRANARY',								'MustBeFunctioning',			1												),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
		(	'REQ_CSC_STAGE_2_EFFECT_TECH_OR_CIVIC',					'CivicType',					'CIVIC_FEUDALISM'								),
		(	'REQ_CSC_CITY_HAS_WATER_MILL',							'BuildingType',					'BUILDING_CSC_BAKERS_WATER_MILL'					),
		(	'REQ_CSC_CITY_HAS_WIND_MILL',							'BuildingType',					'BUILDING_CSC_BAKERS_WIND_MILL'					),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.2 Food and +0.2 Gold per Citizen to the city for each adjacent Market
		(	'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB',					'DistrictType',					'DISTRICT_COMMERCIAL_HUB'						),
		(	'REQ_CSC_CITY_HAS_MARKET',								'BuildingType',					'BUILDING_MARKET'								),
		(	'REQ_CSC_CITY_HAS_BAKERY',								'BuildingType',					'BUILDING_CSC_BAKERS_BAKERY'					),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
-- UNUSED: only used by the orphan REQSET_CSC_ADJ_BAKERS_STAGE_3_SERVICE chain.
--		(	'REQ_CSC_CITY_HAS_BAKERS_STAGE_3_SERVICE',				'BuildingType',					'BUILDING_CSC_BAKERS_STAGE_3_SERVICE'			),
--  An adjacent Market provides +2 Housing
-- 	+1 Citizen slot (Merchant Guildhall) to a Commercial Hub with a Market
		(	'REQ_CSC_STAGE_3_EFFECT_TECH_OR_CIVIC',					'CivicType',					'CIVIC_MEDIEVAL_FAIRES'							),

-- 	CAFE --------------------------------------------------------------------------

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel
		(	'REQ_CSC_DISTRICT_IS_ENTERTAINMENT_COMPLEX',			'DistrictType',					'DISTRICT_ENTERTAINMENT_COMPLEX'				),
		(	'REQ_CSC_DISTRICT_IS_WATER_PARK',						'DistrictType',					'DISTRICT_WATER_ENTERTAINMENT_COMPLEX'			),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
		(	'REQ_CSC_STAGE_4_EFFECT_TECH_OR_CIVIC',					'CivicType',					'CIVIC_URBANIZATION'							),
		(	'REQ_CSC_CITY_HAS_CAFE',									'BuildingType',					'BUILDING_CSC_BAKERS_CAFE'						),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
		(	'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX',					'RequirementSetId',				'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX'			),
		(	'REQ_CSC_CITY_HAS_ZOO',									'BuildingType',					'BUILDING_ZOO'									),
		(	'REQ_CSC_ADJ_WATER_PARK',								'RequirementSetId',				'REQSET_CSC_ADJ_WATER_PARK'						),
		(	'REQ_CSC_CITY_HAS_FERRIS',								'BuildingType',					'BUILDING_FERRIS_WHEEL'							),

-- 	SHARED ------------------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY arg
		(	'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',				'Tag',							'CLASS_CSC_BAKERS_BASE'							),
		(	'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC',				'Tag',							'CLASS_CSC_BAKERS_SPEC'							),
		( 	'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',					'DistrictType',                 'DISTRICT_CSC_BAKERS_QUARTER'     				),

		(	'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',			'CollectionType',				'COLLECTION_PLAYER_IMPROVEMENTS'				),
		(	'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',			'Count',						1												),
		(	'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',			'RequirementSetId',				'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE'			),

		(	'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',			'CollectionType',				'COLLECTION_PLAYER_IMPROVEMENTS'				),
		(	'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',			'Count',						1												),
		(	'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',			'RequirementSetId',				'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC'			);


--===========================================================================================================================================================================--
/*	CAFE */
--===========================================================================================================================================================================--

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel

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
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO BuildingModifiers (BuildingType, ModifierId)
SELECT
    'BUILDING_CSC_BAKERS_CAFE',
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO_AT_POP_' || Pop || '_ATTACH'
FROM CSC_PopulationLevels
WHERE Pop > 0
UNION ALL
SELECT
    'BUILDING_CSC_BAKERS_CAFE',
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS_AT_POP_' || Pop || '_ATTACH'
FROM CSC_PopulationLevels
WHERE Pop > 0;

-- Moved to CSC_Q_BAKERS_GOLD.sql: BUILDING_ZOO/THERMAL_BATH/FERRIS_WHEEL → MOD_CSC_BAKERS_GOLD_TO_CAFE_AT_POP_*

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Modifiers (
    ModifierId,
    ModifierType,
    OwnerRequirementSetId,
    SubjectRequirementSetId
)
SELECT
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO_AT_POP_' || Pop || '_ATTACH',
    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',
    'REQSET_CSC_CITY_HAS_POPULATION_' || Pop,
    'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX'
FROM CSC_PopulationLevels
WHERE Pop > 0
UNION ALL
SELECT
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS_AT_POP_' || Pop || '_ATTACH',
    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',
    'REQSET_CSC_CITY_HAS_POPULATION_' || Pop,
    'REQSET_CSC_ADJ_WATER_PARK'
FROM CSC_PopulationLevels
WHERE Pop > 0;

-- Moved to CSC_Q_BAKERS_GOLD.sql: MOD_CSC_BAKERS_GOLD_TO_CAFE_AT_POP_* modifiers

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ModifierArguments (
    ModifierId,
    Name,
    Value
)
SELECT
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO_AT_POP_' || Pop || '_ATTACH',
    'ModifierId',
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO'
FROM CSC_PopulationLevels
WHERE Pop > 0
UNION ALL
SELECT
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS_AT_POP_' || Pop || '_ATTACH',
    'ModifierId',
    'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS'
FROM CSC_PopulationLevels
WHERE Pop > 0;

-- Moved to CSC_Q_BAKERS_GOLD.sql: MOD_CSC_BAKERS_GOLD_TO_CAFE_AT_POP_* modifier arguments

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSetRequirements (
	RequirementSetId,
	RequirementId
)
SELECT
	'REQSET_CSC_CITY_HAS_POPULATION_' || Pop,
	'REQ_CSC_CITY_HAS_POPULATION_' || Pop
FROM CSC_PopulationLevels
WHERE Pop > 0;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Requirements (
	RequirementId,
	RequirementType
)
SELECT
	'REQ_CSC_CITY_HAS_POPULATION_' || Pop,
	'REQUIREMENT_CITY_HAS_X_POPULATION'
FROM CSC_PopulationLevels
WHERE Pop > 0;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
--	CSC_PopulationLevels
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

DROP TABLE CSC_PopulationLevels;


INSERT INTO ModifierStrings
	(	ModifierId,                                			Context,			'Text'			)	VALUES
	(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER',		'Preview',			'LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WATER'	),
	(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND',		'Preview',			'LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WIND'	),
	(	'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING',			'Preview',			'LOC_CSC_BAKERS_STAGE_3_EFFECT_DESCRIPTION'			),
	(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER',		'Preview',			'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_ENTER'	),
	(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER',		'Preview',			'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_WATER'	),

	(	'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT',			'Preview',			'LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME'		),
	(	'MOD_CSC_BAKERS_STAGE_3_SERVICE_GRANT',			'Preview',			'LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME'		),
	(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER',	'Preview',			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME'	),
	(	'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER',	'Preview',			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME'	);
