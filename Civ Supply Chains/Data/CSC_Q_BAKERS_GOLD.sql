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

DROP TABLE IF EXISTS CSC_BakersScaledAmountBits;

CREATE TEMPORARY TABLE CSC_BakersScaledAmountBits
		(	Bit INTEGER PRIMARY KEY	);

INSERT INTO CSC_BakersScaledAmountBits
		(	Bit	)
VALUES	(	1	), (	2	), (	4	), (	8	), (	16	), (	32	), (	64	), (	128	),
		(	256	), (	512	), (	1024	), (	2048	), (	4096	), (	8192	), (	16384	), (	32768	),
		(	65536	), (	131072	), (	262144	), (	524288	);

DROP TABLE IF EXISTS CSC_BakersStage4StackBits;

CREATE TEMPORARY TABLE CSC_BakersStage4StackBits
		(	Bit INTEGER PRIMARY KEY	);

INSERT INTO CSC_BakersStage4StackBits
		(	Bit	)
VALUES	(	1	), (	2	), (	4	), (	8	), (	16	), (	32	), (	64	), (	128	);

INSERT OR IGNORE INTO DistrictModifiers

		(	DistrictType,							ModifierId										)	VALUES

--  +1 Gold return from eligible import routes to supplied Bakers buildings
		(	'DISTRICT_CITY_CENTER',					'MOD_CSC_BAKERS_EXPORT_BAKERY_GOLD'				),
		(	'DISTRICT_CITY_CENTER',					'MOD_CSC_BAKERS_EXPORT_CAFE_GOLD'				);

--  Customer-population return stacks. Lua sums adjacent Market city population
--  and writes scaled per-population amount bits on the seller city's City
--  Center plot. This preserves +0.1 Gold per customer citizen while paying
--  the seller city.
INSERT OR IGNORE INTO DistrictModifiers
		(	DistrictType,							ModifierId										)
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_MARKET_RETURN_GOLD_AMOUNT_BIT_' || Bit
FROM CSC_BakersScaledAmountBits;

INSERT OR IGNORE INTO DistrictModifiers
		(	DistrictType,							ModifierId										)
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_GOLD_BIT_' || Bit
FROM CSC_BakersStage4StackBits;

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

INSERT OR IGNORE INTO Modifiers
		(	ModifierId,															ModifierType,												OwnerRequirementSetId,	SubjectRequirementSetId									)
SELECT	'MOD_CSC_BAKERS_MARKET_RETURN_GOLD_AMOUNT_BIT_' || Bit,					'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',	NULL,					'REQSET_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_BakersScaledAmountBits;

INSERT OR IGNORE INTO Modifiers
		(	ModifierId,															ModifierType,												OwnerRequirementSetId,	SubjectRequirementSetId									)
SELECT	'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_GOLD_BIT_' || Bit,					'MODIFIER_BUILDING_YIELD_CHANGE',							NULL,					'REQSET_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_' || Bit
FROM CSC_BakersStage4StackBits;



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

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,															Name,						Value															)
SELECT	'MOD_CSC_BAKERS_MARKET_RETURN_GOLD_AMOUNT_BIT_' || Bit,					'YieldType',				'YIELD_GOLD'
FROM CSC_BakersScaledAmountBits;

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,															Name,						Value															)
SELECT	'MOD_CSC_BAKERS_MARKET_RETURN_GOLD_AMOUNT_BIT_' || Bit,					'Amount',					Bit / 10000.0
FROM CSC_BakersScaledAmountBits;

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,															Name,						Value															)
SELECT	'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_GOLD_BIT_' || Bit,					'BuildingType',				'BUILDING_CSC_BAKERS_CAFE'
FROM CSC_BakersStage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,															Name,						Value															)
SELECT	'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_GOLD_BIT_' || Bit,					'YieldType',				'YIELD_GOLD'
FROM CSC_BakersStage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
		(	ModifierId,															Name,						Value															)
SELECT	'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_GOLD_BIT_' || Bit,					'Amount',					Bit
FROM CSC_BakersStage4StackBits;

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

-- Stage 4 Café Gold returns now come from the customer-population Lua bridge.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Replaced by MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_GOLD_BIT_* city-center property consumers.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Replaced by MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_GOLD_BIT_* city-center property consumers.
