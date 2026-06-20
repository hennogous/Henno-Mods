-- CSC_Q_BAKERS_GOLD.sql
-- Author: Henno
-- Gold modifiers for the Bakers' Quarter.
-- Loaded always unless Taxes & Politics (T&P) is active.
-- TODO: Add CSC_NO_TP criterion to the civ6proj action when T&P ships.
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	GOLD MODIFIERS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO BuildingModifiers

		(	BuildingType,		            			ModifierId											)	VALUES

--	WIND / WATER MILL -------------------------------------------------------------------

--	+1 Gold to adjacent base materials improvements
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE'		),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE'		),

-- 	+1 Gold return from an adjacent Granary
		(	'BUILDING_GRANARY',							'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER'		),
		(	'BUILDING_GRANARY',							'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND'			),

--	BAKERY ------------------------------------------------------------------------------

-- 	+1 Gold to the Flour Mill in the Quarter
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL'					),
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL'					),

--  +0.1 Gold per Citizen to the city for each adjacent Market
		(	'BUILDING_MARKET',							'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER'		),
		(	'BUILDING_SUKIENNICE',						'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER'		),

--	CAFE --------------------------------------------------------------------------

--	+1 Gold to adjacent specialty materials improvements
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC'			),

-- 	+1 Gold to the Flour Mill in the Quarter
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL'					),
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL'					);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	DistrictModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

DROP TABLE IF EXISTS CSC_BakersRouteStackBits;

CREATE TEMPORARY TABLE CSC_BakersRouteStackBits
		(	Bit INTEGER PRIMARY KEY	);

INSERT INTO CSC_BakersRouteStackBits
		(	Bit	)
VALUES	(	2	), (	4	), (	8	), (	16	);

INSERT OR IGNORE INTO DistrictModifiers

		(	DistrictType,							ModifierId										)	VALUES

--  +1 Gold return from eligible import routes to supplied Bakers buildings
		(	'DISTRICT_CITY_CENTER',					'MOD_CSC_BAKERS_EXPORT_BAKERY_GOLD'				),
		(	'DISTRICT_CITY_CENTER',					'MOD_CSC_BAKERS_EXPORT_CAFE_GOLD'				);

--  Extra export-return stacks. The base modifier handles the +1 bit; these generated
--  rows add +2, +4, +8, and +16 when Lua sets the matching route-count bit.
INSERT OR IGNORE INTO DistrictModifiers
		(	DistrictType,							ModifierId										)
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_EXPORT_BAKERY_GOLD_BIT_' || Bit
FROM CSC_BakersRouteStackBits;

INSERT OR IGNORE INTO DistrictModifiers
		(	DistrictType,							ModifierId										)
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_EXPORT_CAFE_GOLD_BIT_' || Bit
FROM CSC_BakersRouteStackBits;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Modifiers

		(	ModifierId,															ModifierType,													OwnerRequirementSetId,						SubjectRequirementSetId								)	VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

-- 	+1 Gold to adjacent base materials improvements
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE',					'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE'				),
		(	'MOD_CSC_ALL_GOLD_TO_PLOT',											'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',						NULL,										NULL												),

-- 	+1 Gold return from an adjacent Granary
		(  	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERS_QUARTER'						),
		(  	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERS_QUARTER'						),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.1 Gold per Citizen to the city for each adjacent Market
		(	'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERY_STAGE_3_RETURN'				),
		(	'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY',								'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',		NULL,										NULL												),

-- 	CAFE --------------------------------------------------------------------------

--	+1 Gold to adjacent specialty materials improvements
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC',							'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC'				),

--  +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel
		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

-- 	SHARED ------------------------------------------------------------------------------

-- 	+1 Gold to the Flour Mill in the Quarter
		(	'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL',								'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),
		(	'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL',									'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

--  +1 Gold return from eligible import routes to supplied Bakers buildings
		(	'MOD_CSC_BAKERS_EXPORT_BAKERY_GOLD',								'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1'		),
		(	'MOD_CSC_BAKERS_EXPORT_CAFE_GOLD',									'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1'			);

INSERT OR IGNORE INTO Modifiers
		(	ModifierId,															ModifierType,												OwnerRequirementSetId,	SubjectRequirementSetId									)
SELECT	'MOD_CSC_BAKERS_EXPORT_BAKERY_GOLD_BIT_' || Bit,						'MODIFIER_BUILDING_YIELD_CHANGE',							NULL,					'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_' || Bit
FROM CSC_BakersRouteStackBits;

INSERT OR IGNORE INTO Modifiers
		(	ModifierId,															ModifierType,												OwnerRequirementSetId,	SubjectRequirementSetId									)
SELECT	'MOD_CSC_BAKERS_EXPORT_CAFE_GOLD_BIT_' || Bit,							'MODIFIER_BUILDING_YIELD_CHANGE',							NULL,					'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_' || Bit
FROM CSC_BakersRouteStackBits;



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ModifierArguments

		(	ModifierId,			                      							Name,                       Value		                									)	VALUES

-- 	BAKERS QUARTER ----------------------------------------------------------------------

-- 	+1 Gold to adjacent base materials improvements
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE',					'ModifierId',				'MOD_CSC_ALL_GOLD_TO_PLOT'										),
		(	'MOD_CSC_ALL_GOLD_TO_PLOT',    										'YieldType',				'YIELD_GOLD'                									),
		(	'MOD_CSC_ALL_GOLD_TO_PLOT',    										'Amount',					1		                    									),

-- 	+1 Gold return from an adjacent Granary
		(	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER',						'ModifierId',				'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL'								),
		(	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND',						'ModifierId',				'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL'								),

--  +0.1 Gold per Citizen to the city for each adjacent Market
		(	'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER',						'ModifierId',				'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY'							),
		(	'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY',								'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY',								'Amount',					0.1																),

--	+1 Gold to adjacent specialty materials improvements
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC',							'ModifierId',				'MOD_CSC_ALL_GOLD_TO_PLOT'										),

--  +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel
		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'BuildingType',				'BUILDING_CSC_BAKERS_CAFE'										),
		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'Amount',					1																),

-- 	+1 Gold to the Flour Mill in the Quarter
		(	'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL',								'BuildingType',				'BUILDING_CSC_BAKERS_WATER_MILL'								),
		(	'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL',								'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL',								'Amount',					1																),
		(	'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL',									'BuildingType',				'BUILDING_CSC_BAKERS_WIND_MILL'									),
		(	'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL',									'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL',									'Amount',					1																),

--  +1 Gold return from eligible import routes to supplied Bakers buildings
		(	'MOD_CSC_BAKERS_EXPORT_BAKERY_GOLD',								'BuildingType',				'BUILDING_CSC_BAKERS_BAKERY'									),
		(	'MOD_CSC_BAKERS_EXPORT_BAKERY_GOLD',								'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_EXPORT_BAKERY_GOLD',								'Amount',					1																),
		(	'MOD_CSC_BAKERS_EXPORT_CAFE_GOLD',									'BuildingType',				'BUILDING_CSC_BAKERS_CAFE'										),
		(	'MOD_CSC_BAKERS_EXPORT_CAFE_GOLD',									'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_EXPORT_CAFE_GOLD',									'Amount',					1																);

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,															Name,						Value															)
SELECT	'MOD_CSC_BAKERS_EXPORT_BAKERY_GOLD_BIT_' || Bit,						'BuildingType',				'BUILDING_CSC_BAKERS_BAKERY'
FROM CSC_BakersRouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,															Name,						Value															)
SELECT	'MOD_CSC_BAKERS_EXPORT_BAKERY_GOLD_BIT_' || Bit,						'YieldType',				'YIELD_GOLD'
FROM CSC_BakersRouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,															Name,						Value															)
SELECT	'MOD_CSC_BAKERS_EXPORT_BAKERY_GOLD_BIT_' || Bit,						'Amount',					Bit
FROM CSC_BakersRouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,															Name,						Value															)
SELECT	'MOD_CSC_BAKERS_EXPORT_CAFE_GOLD_BIT_' || Bit,							'BuildingType',				'BUILDING_CSC_BAKERS_CAFE'
FROM CSC_BakersRouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,															Name,						Value															)
SELECT	'MOD_CSC_BAKERS_EXPORT_CAFE_GOLD_BIT_' || Bit,							'YieldType',				'YIELD_GOLD'
FROM CSC_BakersRouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,															Name,						Value															)
SELECT	'MOD_CSC_BAKERS_EXPORT_CAFE_GOLD_BIT_' || Bit,							'Amount',					Bit
FROM CSC_BakersRouteStackBits;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------


--===========================================================================================================================================================================--
/*	POPULATION-SCALING RETURNS */
--===========================================================================================================================================================================--

--  +1 Gold for every 5 Citizens in the city for each adjacent Zoo, Thermal Bath, or Ferris Wheel

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO BuildingModifiers (BuildingType, ModifierId)
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
    'MOD_CSC_BAKERS_GOLD_TO_CAFE_AT_POP_' || Pop || '_ATTACH',
    'ModifierId',
    'MOD_CSC_BAKERS_GOLD_TO_CAFE'
FROM CSC_PopulationLevels
WHERE Pop > 0;
