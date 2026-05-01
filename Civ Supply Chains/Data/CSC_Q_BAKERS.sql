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

		(	'BUILDING_CSC_BAKERS_STAGE_3_SPECIALIST',							'KIND_BUILDING'			),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER',						'KIND_BUILDING'			),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER',						'KIND_BUILDING'			),

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

UPDATE Districts SET Description = '{LOC_DISTRICT_COMMERCIAL_HUB_EXPANSION1_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_3_SPECIALIST}' WHERE DistrictType='DISTRICT_COMMERCIAL_HUB';
UPDATE Districts SET Description = '{LOC_DISTRICT_ENTERTAINMENT_COMPLEX_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SPECIALIST_LAND}' WHERE DistrictType='DISTRICT_ENTERTAINMENT_COMPLEX';
UPDATE Districts SET Description = '{LOC_DISTRICT_STREET_CARNIVAL_EXPANSION2_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SPECIALIST_LAND}' WHERE DistrictType='DISTRICT_STREET_CARNIVAL';
UPDATE Districts SET Description = '{LOC_DISTRICT_HIPPODROME_EXPANSION2_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SPECIALIST_LAND}' WHERE DistrictType='DISTRICT_HIPPODROME';
UPDATE Districts SET Description = '{LOC_DISTRICT_WATER_ENTERTAINMENT_COMPLEX_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SPECIALIST_WATER}' WHERE DistrictType='DISTRICT_WATER_ENTERTAINMENT_COMPLEX';
UPDATE Districts SET Description = '{LOC_DISTRICT_WATER_STREET_CARNIVAL_EXPANSION2_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SPECIALIST_WATER}' WHERE DistrictType='DISTRICT_WATER_STREET_CARNIVAL';


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
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'MOD_CSC_BAKERS_NO_RIVER_ACCESS_FLAG'			),

--  +1 Gold to each adjacent base or specialty materials resource from this supply chain
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'MOD_CSC_BAKERS_GOLD_TO_ADJ_MATERIAL_ANY'		);



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
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_STAGE_3_SPECIALIST',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_STAGE_3_SPECIALIST_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_STAGE_3_SPECIALIST_DESCRIPTION',
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
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER_DESCRIPTION',
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
		/*  BuildingType, */		'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER',
		/*  Name, */				'LOC_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER_NAME',
		/*  Description, */			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER_DESCRIPTION',
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
    'BUILDING_CSC_BAKERS_STAGE_3_SPECIALIST',
    'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER',
    'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER'
);

INSERT INTO CivilopediaPageExcludes
		(	SectionId,			PageId	) VALUES	
		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_RIVER_ACCESS'				),
		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'			),
		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_STAGE_3_SPECIALIST'		),
		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER'	),
		(	'BUILDINGS',		'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER'	);

-- UPDATE Buildings SET Description = 'LOC_CSC_BAKERS_STAGE_2_EFFECT' WHERE BuildingType='BUILDING_GRANARY';
-- UPDATE Buildings SET Description = '{LOC_BUILDING_MARKET_EXPANSION1_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_3_EFFECT}' WHERE BuildingType='BUILDING_MARKET';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings_XP2
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

INSERT OR IGNORE INTO Buildings_XP2

		(	BuildingType,										Pillage		)
VALUES	(	'BUILDING_CSC_BAKERS_RIVER_ACCESS',					0			),
		(	'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',				0			),
		(	'BUILDING_CSC_BAKERS_STAGE_3_SPECIALIST',			0			),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER',		0			),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER',		0			);

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

		(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER',		'YIELD_CULTURE',	        			2		        	),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER',		'YIELD_GOLD',	        				2		        	),

		(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER',		'YIELD_CULTURE',	        			2		        	),
		(	'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER',		'YIELD_GOLD',	        				2		        	);
		
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT INTO BuildingModifiers

        (	BuildingType,		            			ModifierId											)	VALUES

--	WIND / WATER MILL -------------------------------------------------------------------

--	+1 Gold to adjacent base materials improvements
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE'		),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE'		),

--  +1 Food (with a -1 Gold maintenance cost)
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_WATER_MILL_SELF_FOOD'				),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_WIND_MILL_SELF_FOOD'				),

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER'		),
		(	'BUILDING_GRANARY',							'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER'		),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER'		),
		(	'BUILDING_GRANARY',							'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND'			),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER'	),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND'	),

--	BAKERY ------------------------------------------------------------------------------

--  +1 Production from the local Flour Mill
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY'			),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY'			),

-- 	+1 Gold to the Flour Mill in the Quarter
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL'		),
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL'			),

--  +2 Food (with a -2 Gold maintenance cost)
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_BAKERY_SELF_FOOD'					),

--  +0.2 Food and +0.2 Gold per Citizen to the city for each adjacent Market
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_BAKERY_ATTACH_COMMERCIAL_HUB'		),
		(	'BUILDING_MARKET',							'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER'		),
		(	'BUILDING_SUKIENNICE',						'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER'		),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
--  An adjacent Market provides +2 Housing
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB'		),

-- 	+1 Citizen slot (Merchant Guildhall) to a Commercial Hub with a Market
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_STAGE_3_SPECIALIST_ATTACH_COMHUB'	),

--	CAFE --------------------------------------------------------------------------

--	+1 Gold to adjacent specialty materials improvements
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC'		),

--  +1 Production from the local Flour Mill
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE'		),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE'		),

-- 	+1 Gold to the Flour Mill in the Quarter
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL'		),
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL'			),

--  +3 Food (with a -3 Gold maintenance cost)
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_CAFE_SELF_FOOD'				),

--  See end of file for: +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2 Tourism to an Entertainment Complex, Water Park
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT'),
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK'	),

-- 	+1 Citizen slot (Groundskeeper) to an Entertainment Complex with a Zoo, Water Park with a Ferris Wheel
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_ENTER'	),
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_WATER'	),

--	SHARED ------------------------------------------------------------------------------

-- 	+1 Food bonus to trade routes to the city, and +1 Gold in return (not working for domestic)
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD'					),
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD'					),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD'					),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD'					),
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD'					),
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD'					),
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD'					),
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD_EXTRA'			);



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

--  +1 Gold to each adjacent base or specialty materials resource from this supply chain
		(	'MOD_CSC_BAKERS_GOLD_TO_ADJ_MATERIAL_ANY',							'MODIFIER_PLAYER_ADJUST_PLOT_YIELD',							NULL,										'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_MATERIAL_ANY'		),

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

-- 	+1 Gold to adjacent base materials improvements
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE',					'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE'				),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_GOLD_TO_ADJ_IMP_BASE',					'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',						NULL,										NULL												),

--  +1 Food (with a -1 Gold maintenance cost)
		(	'MOD_CSC_BAKERS_WATER_MILL_SELF_FOOD',								'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),
		(	'MOD_CSC_BAKERS_WIND_MILL_SELF_FOOD',								'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL, 										'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'				),
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',    				'MODIFIER_BUILDING_YIELD_CHANGE',  								NULL,                           			NULL												),
        (  	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERS_QUARTER'						),
		(  	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WATER_MILL',    				'MODIFIER_BUILDING_YIELD_CHANGE',  								NULL,                           			NULL												),
        (  	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERS_QUARTER'						),
		(  	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WIND_MILL',    					'MODIFIER_BUILDING_YIELD_CHANGE',  								NULL,                           			NULL												),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_2_EFFECT_PREREQ',			'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'				),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER',						'MODIFIER_SINGLE_CITY_ADJUST_CITY_GROWTH',						NULL,										NULL												),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_2_EFFECT_PREREQ',			'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'				),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND',						'MODIFIER_SINGLE_CITY_ADJUST_CITY_GROWTH',						NULL,										NULL												),

--	BAKERY ------------------------------------------------------------------------------

--  +1 Production from the local Flour Mill
		(	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY',							'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

--  +2 Food (with a -2 Gold maintenance cost)
		(	'MOD_CSC_BAKERS_BAKERY_SELF_FOOD',									'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

--  +0.2 Food and +0.2 Gold per Citizen to the city for each adjacent Market
		(	'MOD_CSC_BAKERS_BAKERY_ATTACH_COMMERCIAL_HUB',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_MARKET'								),
		(	'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET',								'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',		NULL,										NULL												),
		(	'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERY'								),
		(	'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY',								'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',		NULL,										NULL												),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
--  An adjacent Market provides +2 Housing

		(	'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_3_EFFECT_PREREQ',			'REQSET_CSC_ADJ_MARKET'								),
		(	'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING',							'MODIFIER_SINGLE_CITY_ADJUST_BUILDING_HOUSING',					NULL,										NULL												),

-- 	+1 Citizen slot (Merchant Guildhall) to a Commercial Hub with a Market
		(	'MOD_CSC_BAKERS_STAGE_3_SPECIALIST_ATTACH_COMHUB',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_3_EFFECT_PREREQ',			'REQSET_CSC_ADJ_MARKET'								),
		(	'MOD_CSC_BAKERS_STAGE_3_SPECIALIST_GRANT',							'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',			NULL,										NULL												),
		
-- 	CAFE --------------------------------------------------------------------------

--  +1 Production to the Café from improved specialty materials
        (	'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',			'REQSET_CSC_ADJ_BAKERS_QUARTER'						),
        (  	'MOD_CSC_BAKERS_SPEC_IMPROV_PROD_TO_ADJ_CAFE',    					'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,                           			NULL												),

--	+1 Gold to adjacent specialty materials improvements
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC',							'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC'				),

--  +1 Production from the local Flour Mill
		(	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE',							'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

--  +3 Food (with a -3 Gold maintenance cost)
		(	'MOD_CSC_BAKERS_CAFE_SELF_FOOD',									'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',								'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),	
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',							'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),	
		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),	

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',				'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_4_EFFECT_PREREQ',			'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'			),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER',						'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',				NULL,										NULL												),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_4_EFFECT_PREREQ',			'REQSET_CSC_ADJ_WATER_PARK_FERRIS'					),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER',						'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',				NULL,										NULL												),

-- 	+1 Citizen slot (Groundskeeper) to an Entertainment Complex with a Zoo, Water Park with a Ferris Wheel
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_ENTER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_4_EFFECT_PREREQ',			'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'			),
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_ENTER',					'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',			NULL,										NULL												),
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_WATER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				'REQSET_CSC_STAGE_4_EFFECT_PREREQ',			'REQSET_CSC_ADJ_WATER_PARK_FERRIS'					),
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_WATER',					'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',			NULL,										NULL												),

-- 	SHARED ------------------------------------------------------------------------------

-- 	+1 Gold to the Flour Mill in the Quarter
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL',						'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL',						'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

-- 	+1 Food bonus to trade routes to the city, and +1 Gold in return (not working for domestic)
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD',									'MODIFIER_SINGLE_CITY_ADJUST_TRADE_ROUTE_YIELD_TO_OTHERS',		NULL,										NULL												),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD',									'MODIFIER_SINGLE_CITY_ADJUST_TRADE_ROUTE_YIELD_FROM_OTHERS',	NULL,										NULL												),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD_EXTRA',							'MODIFIER_SINGLE_CITY_ADJUST_TRADE_ROUTE_YIELD_FROM_OTHERS',	NULL,										NULL												);



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		
INSERT OR IGNORE INTO ModifierArguments
		
        (	ModifierId,			                      							Name,                       Value		                									)	VALUES

-- 	BAKERS QUARTER ----------------------------------------------------------------------

--  +1 Gold to each adjacent base or specialty materials resource from this supply chain
		(	'MOD_CSC_BAKERS_GOLD_TO_ADJ_MATERIAL_ANY',							'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_GOLD_TO_ADJ_MATERIAL_ANY',							'Amount',					1																),

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

-- 	+1 Gold to adjacent base materials improvements
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE',					'ModifierId',				'MOD_CSC_BAKERS_FLOUR_MILL_GOLD_TO_ADJ_IMP_BASE'				),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_GOLD_TO_ADJ_IMP_BASE',    				'YieldType',	            'YIELD_GOLD'                									),
        (	'MOD_CSC_BAKERS_FLOUR_MILL_GOLD_TO_ADJ_IMP_BASE',    				'Amount',		            1		                    									),

--  +1 Food (with a -1 Gold maintenance cost)
        (  	'MOD_CSC_BAKERS_WATER_MILL_SELF_FOOD',								'BuildingType',           	'BUILDING_CSC_BAKERS_WATER_MILL'								),
        (  	'MOD_CSC_BAKERS_WATER_MILL_SELF_FOOD',								'YieldType',           		'YIELD_FOOD'                                             		),
        ( 	'MOD_CSC_BAKERS_WATER_MILL_SELF_FOOD',								'Amount',             		1                                                               ),
        (  	'MOD_CSC_BAKERS_WIND_MILL_SELF_FOOD',								'BuildingType',           	'BUILDING_CSC_BAKERS_WIND_MILL'									),
        (  	'MOD_CSC_BAKERS_WIND_MILL_SELF_FOOD',								'YieldType',           		'YIELD_FOOD'                                              		),
        ( 	'MOD_CSC_BAKERS_WIND_MILL_SELF_FOOD',								'Amount',             		1                                                               ),

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER',						'ModifierId',				'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY'					),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',					'BuildingType',				'BUILDING_GRANARY'												),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',					'YieldType',				'YIELD_FOOD'													),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',					'Amount',					1																),
		(	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER',						'ModifierId',				'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WATER_MILL'					),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WATER_MILL',					'BuildingType',				'BUILDING_CSC_BAKERS_WATER_MILL'								),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WATER_MILL',					'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WATER_MILL',					'Amount',					1																),
		(	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND',						'ModifierId',				'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WIND_MILL'					),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WIND_MILL',						'BuildingType',				'BUILDING_CSC_BAKERS_WIND_MILL'									),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WIND_MILL',						'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WIND_MILL',						'Amount',					1																),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER'					),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER',						'Amount',					10																),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND'						),
		(	'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND',						'Amount',					10																),

--	BAKERY ------------------------------------------------------------------------------

--  +1 Production from the local Flour Mill
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY',							'BuildingType',           	'BUILDING_CSC_BAKERS_BAKERY'									),
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY',							'YieldType',           		'YIELD_PRODUCTION'                                             	),
        ( 	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_BAKERY',							'Amount',             		1                                                               ),

--  +2 Food (with a -2 Gold maintenance cost)
        (  	'MOD_CSC_BAKERS_BAKERY_SELF_FOOD',									'BuildingType',           	'BUILDING_CSC_BAKERS_BAKERY'									),
        (  	'MOD_CSC_BAKERS_BAKERY_SELF_FOOD',									'YieldType',           		'YIELD_FOOD'                                             		),
        ( 	'MOD_CSC_BAKERS_BAKERY_SELF_FOOD',									'Amount',             		2                                                               ),

--  +0.2 Food and +0.2 Gold per Citizen to the city for each adjacent Market
		(	'MOD_CSC_BAKERS_BAKERY_ATTACH_COMMERCIAL_HUB',						'ModifierId',				'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET'							),
		(	'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET',								'YieldType',				'YIELD_FOOD'													),
		(	'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET',								'Amount',					0.21															),
		(	'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER',						'ModifierId',				'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY'							),
		(	'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY',								'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY',								'Amount',					0.21															),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
--  An adjacent Market provides +2 Housing
		(	'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',						'ModifierId',				'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING'							),
		(	'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING',							'Amount',					2																),

-- 	+1 Citizen slot (Merchant Guildhall) to a Commercial Hub with a Market
		(	'MOD_CSC_BAKERS_STAGE_3_SPECIALIST_ATTACH_COMHUB',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_3_SPECIALIST_GRANT'						),
		(	'MOD_CSC_BAKERS_STAGE_3_SPECIALIST_GRANT',							'BuildingType',				'BUILDING_CSC_BAKERS_STAGE_3_SPECIALIST'						),

-- 	CAFE --------------------------------------------------------------------------

--  +1 Production to the Café from improved specialty materials
		(  	'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER',					'ModifierId',         		'MOD_CSC_BAKERS_SPEC_IMPROV_PROD_TO_ADJ_CAFE'     				),    
        (  	'MOD_CSC_BAKERS_SPEC_IMPROV_PROD_TO_ADJ_CAFE',						'BuildingType',           	'BUILDING_CSC_BAKERS_CAFE'										),
        (  	'MOD_CSC_BAKERS_SPEC_IMPROV_PROD_TO_ADJ_CAFE',						'YieldType',           		'YIELD_PRODUCTION'                                              ),
        ( 	'MOD_CSC_BAKERS_SPEC_IMPROV_PROD_TO_ADJ_CAFE',						'Amount',             		1                                                               ),

--	+1 Gold to adjacent specialty materials improvements
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC',							'ModifierId',				'MOD_CSC_BAKERS_FLOUR_MILL_GOLD_TO_ADJ_IMP_BASE'				),

--  +1 Production from the local Flour Mill
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE',							'BuildingType',				'BUILDING_CSC_BAKERS_CAFE'										),
        (  	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE',							'YieldType',           		'YIELD_PRODUCTION'                                             	),
        ( 	'MOD_CSC_BAKERS_FLOUR_MILL_PROD_TO_CAFE',							'Amount',             		1                                                               ),

--  +3 Food (with a -3 Gold maintenance cost)
        (  	'MOD_CSC_BAKERS_CAFE_SELF_FOOD',									'BuildingType',           	'BUILDING_CSC_BAKERS_CAFE'										),
        (  	'MOD_CSC_BAKERS_CAFE_SELF_FOOD',									'YieldType',           		'YIELD_FOOD'                                             		),
        ( 	'MOD_CSC_BAKERS_CAFE_SELF_FOOD',									'Amount',             		3                                                               ),

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',								'BuildingType',				'BUILDING_ZOO'													),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',								'YieldType',				'YIELD_CULTURE'													),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',								'Amount',					1																),

		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',							'BuildingType',				'BUILDING_FERRIS_WHEEL'											),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',							'YieldType',				'YIELD_CULTURE'													),
		(	'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',							'Amount',					1																),

		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'BuildingType',				'BUILDING_CSC_BAKERS_CAFE'										),
		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'Amount',					1																),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',				'ModifierId',				'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER'					),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER',						'Amount',					2																),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER'					),
		(	'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER',						'Amount',					2																),

-- 	+1 Citizen slot (Groundskeeper) to an Entertainment Complex with a Zoo, Water Park with a Ferris Wheel
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_ENTER',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_ENTER'					),
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_ENTER',					'BuildingType',				'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER'					),
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_ATTACH_WATER',					'ModifierId',				'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_WATER'					),
		(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_WATER',					'BuildingType',				'BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER'					),

-- 	SHARED ------------------------------------------------------------------------------

-- 	+1 Gold to the Flour Mill in the Quarter
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL',						'BuildingType',				'BUILDING_CSC_BAKERS_WATER_MILL'								),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL',						'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL',						'Amount',					1																),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL',						'BuildingType',				'BUILDING_CSC_BAKERS_WIND_MILL'									),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL',						'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL',						'Amount',					1																),

-- 	+1 Food bonus to trade routes to the city, and +1 Gold in return (not working for domestic)
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD',									'YieldType',				'YIELD_FOOD'													),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD',									'Amount',					1																),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_FOOD',									'Domestic',					1																),

		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD',									'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD',									'Amount',					1																),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD',									'Domestic',					1																),

		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD_EXTRA',							'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD_EXTRA',							'Amount',					2																),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD_EXTRA',							'Domestic',					1																);



--===========================================================================================================================================================================--
/*	REQUIREMENTS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		
INSERT OR IGNORE INTO RequirementSets 
		
        (	RequirementSetId,                              			RequirementSetType              )	VALUES

-- 	BAKERS QUARTER ----------------------------------------------------------------------

--  +1 Gold to each adjacent base or specialty materials resource from this supply chain
		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_MATERIAL_ANY',			'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY',				'REQUIREMENTSET_TEST_ANY'		),

-- 	FLOUR MILL --------------------------------------------------------------------------

--  Set flags for river access, used by Water Mill and Wind Mill variants
		(	'REQSET_CSC_PLOT_ADJ_TO_RIVER',							'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_PLOT_NOT_ADJ_TO_RIVER',						'REQUIREMENTSET_TEST_ALL'		),

-- 	+1 Production from each adjacent base materials improvement
		(	'REQSET_CSC_BAKERS_PLOT_HAS_BASE',						'REQUIREMENTSET_TEST_ALL'       ),

-- 	+1 Gold to adjacent base materials improvements
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE',					'REQUIREMENTSET_TEST_ALL'       ),

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
		(	'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',					'REQUIREMENTSET_TEST_ALL'		),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
-- 	+1 Citizen slot (Merchant Guildhall) to a Commercial Hub with a Market
		(	'REQSET_CSC_STAGE_2_EFFECT_PREREQ',						'REQUIREMENTSET_TEST_ALL'		),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.2 Food and +0.2 Gold per Citizen to the city for each adjacent Market
		(	'REQSET_CSC_ADJ_MARKET',								'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_ADJ_BAKERY',								'REQUIREMENTSET_TEST_ALL'		),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
--  An adjacent Market provides +2 Housing
		(	'REQSET_CSC_STAGE_3_EFFECT_PREREQ', 					'REQUIREMENTSET_TEST_ALL'		),

-- 	CAFE --------------------------------------------------------------------------

-- 	+1 Production from each adjacent speciality materials improvement
		(	'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',						'REQUIREMENTSET_TEST_ALL'       ),

-- 	+1 Gold to adjacent specialty materials improvements
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC',					'REQUIREMENTSET_TEST_ALL'       ),

--  +1 Food and +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel
		(	'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX',					'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_ADJ_WATER_PARK',							'REQUIREMENTSET_TEST_ALL'		),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
		(	'REQSET_CSC_STAGE_4_EFFECT_PREREQ',						'REQUIREMENTSET_TEST_ALL'		),

-- 	+1 Citizen slot (Groundskeeper) to an Entertainment Complex with a Zoo, Water Park with a Ferris Wheel
		(	'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',				'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_ADJ_WATER_PARK_FERRIS',						'REQUIREMENTSET_TEST_ALL'		),

-- 	SHARED ------------------------------------------------------------------------------

		(	'REQSET_CSC_DISTRICT_IS_BAKERS',						'REQUIREMENTSET_TEST_ALL'		),
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

-- 	+1 Gold to adjacent base materials improvements
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

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.2 Food and +0.2 Gold per Citizen to the city for each adjacent Market
		(	'REQSET_CSC_ADJ_MARKET',								'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_ADJ_MARKET',								'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB'			),
		(	'REQSET_CSC_ADJ_MARKET',								'REQ_CSC_CITY_HAS_MARKET'						),

		(	'REQSET_CSC_ADJ_BAKERY',								'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'			),
		(	'REQSET_CSC_ADJ_BAKERY',								'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_ADJ_BAKERY',								'REQ_CSC_CITY_HAS_BAKERY'						),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
--  An adjacent Market provides +2 Housing
		(	'REQSET_CSC_STAGE_3_EFFECT_PREREQ', 					'REQ_CSC_STAGE_3_EFFECT_TECH_OR_CIVIC'			),
		(	'REQSET_CSC_STAGE_3_EFFECT_PREREQ',						'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'		),

-- 	CAFE --------------------------------------------------------------------------

-- 	+1 Production from each adjacent specialty materials improvement
		(	'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',						'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'			),

-- 	+1 Gold to adjacent specialty materials improvements
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

-- 	+1 Citizen slot (Groundskeeper) to an Entertainment Complex with a Zoo, Water Park with a Ferris Wheel
		(	'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',				'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX'				),
		(	'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',				'REQ_CSC_CITY_HAS_ZOO'							),
		(	'REQSET_CSC_ADJ_WATER_PARK_FERRIS',						'REQ_CSC_ADJ_WATER_PARK'						),
		(	'REQSET_CSC_ADJ_WATER_PARK_FERRIS',						'REQ_CSC_CITY_HAS_FERRIS'						),

-- 	SHARED ------------------------------------------------------------------------------

		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_MATERIAL_ANY',			'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_MATERIAL_ANY',			'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY'			),
		(	'REQSET_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY',				'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'			),
		(	'REQSET_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY',				'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'			),
		(	'REQSET_CSC_DISTRICT_IS_BAKERS',						'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'			),
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

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.2 Food and +0.2 Gold per Citizen to the city for each adjacent Market
		(	'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB',					'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',			0				),
		(	'REQ_CSC_CITY_HAS_MARKET',								'REQUIREMENT_CITY_HAS_BUILDING',					0				),
		(	'REQ_CSC_CITY_HAS_BAKERY',								'REQUIREMENT_CITY_HAS_BUILDING',					0				),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
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

-- 	+1 Citizen slot (Groundskeeper) to an Entertainment Complex with a Zoo, Water Park with a Ferris Wheel
		(	'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX',					'REQUIREMENT_REQUIREMENTSET_IS_MET',				0				),
		(	'REQ_CSC_CITY_HAS_ZOO',									'REQUIREMENT_CITY_HAS_BUILDING',					0				),
		(	'REQ_CSC_ADJ_WATER_PARK',								'REQUIREMENT_REQUIREMENTSET_IS_MET',				0				),
		(	'REQ_CSC_CITY_HAS_FERRIS',								'REQUIREMENT_CITY_HAS_BUILDING',					0				),

-- 	SHARED ------------------------------------------------------------------------------

		(	'REQ_CSC_PLOT_ADJ_TO_OWNER',							'REQUIREMENT_PLOT_ADJACENT_TO_OWNER',              	0               ),
		(	'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY',					'REQUIREMENT_REQUIREMENTSET_IS_MET',				0				),
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

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.2 Food and +0.2 Gold per Citizen to the city for each adjacent Market
		(	'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB',					'DistrictType',					'DISTRICT_COMMERCIAL_HUB'						),
		(	'REQ_CSC_CITY_HAS_MARKET',								'BuildingType',					'BUILDING_MARKET'								),
		(	'REQ_CSC_CITY_HAS_BAKERY',								'BuildingType',					'BUILDING_CSC_BAKERS_BAKERY'					),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
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

-- 	+1 Citizen slot (Groundskeeper) to an Entertainment Complex with a Zoo, Water Park with a Ferris Wheel
		(	'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX',					'RequirementSetId',				'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX'			),
		(	'REQ_CSC_CITY_HAS_ZOO',									'BuildingType',					'BUILDING_ZOO'									),
		(	'REQ_CSC_ADJ_WATER_PARK',								'RequirementSetId',				'REQSET_CSC_ADJ_WATER_PARK'						),
		(	'REQ_CSC_CITY_HAS_FERRIS',								'BuildingType',					'BUILDING_FERRIS_WHEEL'							),

-- 	SHARED ------------------------------------------------------------------------------

		(	'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY',					'RequirementSetId',				'REQSET_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY'		),
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
WHERE Pop > 0
UNION ALL
SELECT
    'BUILDING_ZOO',
    'MOD_CSC_BAKERS_GOLD_TO_CAFE_AT_POP_' || Pop || '_ATTACH'
FROM CSC_PopulationLevels
WHERE Pop > 0
UNION ALL
SELECT
    'BUILDING_THERMAL_BATH',
    'MOD_CSC_BAKERS_GOLD_TO_CAFE_AT_POP_' || Pop || '_ATTACH'
FROM CSC_PopulationLevels
WHERE Pop > 0
UNION ALL
SELECT
    'BUILDING_FERRIS_WHEEL',
    'MOD_CSC_BAKERS_GOLD_TO_CAFE_AT_POP_' || Pop || '_ATTACH'
FROM CSC_PopulationLevels
WHERE Pop > 0;

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
WHERE Pop > 0
UNION ALL
SELECT
    'MOD_CSC_BAKERS_GOLD_TO_CAFE_AT_POP_' || Pop || '_ATTACH',
    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',
    'REQSET_CSC_CITY_HAS_POPULATION_' || Pop,
    'REQSET_CSC_ADJ_BAKERS_QUARTER'
FROM CSC_PopulationLevels
WHERE Pop > 0;

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
WHERE Pop > 0
UNION ALL
SELECT
    'MOD_CSC_BAKERS_GOLD_TO_CAFE_AT_POP_' || Pop || '_ATTACH',
    'ModifierId',
    'MOD_CSC_BAKERS_GOLD_TO_CAFE'
FROM CSC_PopulationLevels
WHERE Pop > 0;

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

	(	'MOD_CSC_BAKERS_STAGE_3_SPECIALIST_GRANT',			'Preview',			'LOC_BUILDING_CSC_BAKERS_STAGE_3_SPECIALIST_NAME'		),
	(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_ENTER',	'Preview',			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER_NAME'	),
	(	'MOD_CSC_BAKERS_STAGE_4_SPECIALIST_GRANT_WATER',	'Preview',			'LOC_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER_NAME'	);