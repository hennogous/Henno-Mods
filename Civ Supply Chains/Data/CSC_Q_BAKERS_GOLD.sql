-- CSC_Q_BAKERS_GOLD.sql
-- Author: Henno
-- Gold modifiers for the Bakers' Quarter.
-- Loaded always unless Taxes & Politics (T&P) is active.
-- TODO: Add CSC_NO_TP criterion to the civ6proj action when T&P ships.
-- NOTE: Adjacency_YieldChanges and District_Adjacencies remain in the main file.
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	GOLD MODIFIERS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	DistrictModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO DistrictModifiers

		(	DistrictType,							ModifierId										)	VALUES

--  +1 Gold to each adjacent base or specialty materials resource from this supply chain
		(	'DISTRICT_CSC_BAKERS_QUARTER',			'MOD_CSC_BAKERS_GOLD_TO_ADJ_MATERIAL_ANY'		);



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Modifiers

		(	ModifierId,															ModifierType,													OwnerRequirementSetId,						SubjectRequirementSetId								)	VALUES

-- 	BAKERS QUARTER ----------------------------------------------------------------------

--  +1 Gold to each adjacent base or specialty materials resource from this supply chain
		(	'MOD_CSC_BAKERS_GOLD_TO_ADJ_MATERIAL_ANY',							'MODIFIER_PLAYER_ADJUST_PLOT_YIELD',							NULL,										'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_MATERIAL_ANY'		),

-- 	FLOUR MILL --------------------------------------------------------------------------

-- 	+1 Gold to adjacent base materials improvements
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE',					'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE'				),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_GOLD_TO_ADJ_IMP_BASE',					'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',						NULL,										NULL												),

-- 	+1 Gold return from an adjacent Granary
		(  	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERS_QUARTER'						),
		(  	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WATER_MILL',    				'MODIFIER_BUILDING_YIELD_CHANGE',  								NULL,                           			NULL												),
		(  	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERS_QUARTER'						),
		(  	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WIND_MILL',    					'MODIFIER_BUILDING_YIELD_CHANGE',  								NULL,                           			NULL												),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.2 Gold per Citizen to the city for each adjacent Market
		(	'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER',						'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_ADJ_BAKERY'								),
		(	'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY',								'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',		NULL,										NULL												),

-- 	CAFE --------------------------------------------------------------------------

--	+1 Gold to adjacent specialty materials improvements
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC',							'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',				NULL,										'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC'				),

--  +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel
		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

-- 	SHARED ------------------------------------------------------------------------------

-- 	+1 Gold to the Flour Mill in the Quarter
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL',						'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL',						'MODIFIER_BUILDING_YIELD_CHANGE',								NULL,										NULL												),

-- 	+1 Gold from trade routes
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

-- 	+1 Gold to adjacent base materials improvements
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE',					'ModifierId',				'MOD_CSC_BAKERS_FLOUR_MILL_GOLD_TO_ADJ_IMP_BASE'				),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_GOLD_TO_ADJ_IMP_BASE',    				'YieldType',	            'YIELD_GOLD'                									),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_GOLD_TO_ADJ_IMP_BASE',    				'Amount',		            1		                    									),

-- 	+1 Gold return from an adjacent Granary
		(	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER',						'ModifierId',				'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WATER_MILL'					),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WATER_MILL',					'BuildingType',				'BUILDING_CSC_BAKERS_WATER_MILL'								),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WATER_MILL',					'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WATER_MILL',					'Amount',					1																),
		(	'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND',						'ModifierId',				'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WIND_MILL'					),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WIND_MILL',						'BuildingType',				'BUILDING_CSC_BAKERS_WIND_MILL'									),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WIND_MILL',						'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_GRANARY_GOLD_TO_ADJ_WIND_MILL',						'Amount',					1																),

--  +0.2 Gold per Citizen to the city for each adjacent Market
		(	'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER',						'ModifierId',				'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY'							),
		(	'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY',								'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_MARKET_GOLD_TO_BAKERY',								'Amount',					0.21															),

--	+1 Gold to adjacent specialty materials improvements
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC',							'ModifierId',				'MOD_CSC_BAKERS_FLOUR_MILL_GOLD_TO_ADJ_IMP_BASE'				),

--  +1 Gold for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel
		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'BuildingType',				'BUILDING_CSC_BAKERS_CAFE'										),
		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_GOLD_TO_CAFE',										'Amount',					1																),

-- 	+1 Gold to the Flour Mill in the Quarter
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL',						'BuildingType',				'BUILDING_CSC_BAKERS_WATER_MILL'								),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL',						'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL',						'Amount',					1																),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL',						'BuildingType',				'BUILDING_CSC_BAKERS_WIND_MILL'									),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL',						'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL',						'Amount',					1																),

-- 	+1 Gold from trade routes
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD',									'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD',									'Amount',					1																),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD',									'Domestic',					1																),

		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD_EXTRA',							'YieldType',				'YIELD_GOLD'													),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD_EXTRA',							'Amount',					2																),
		(	'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD_EXTRA',							'Domestic',					1																);



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
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL'		),
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL'			),

--  +0.2 Gold per Citizen to the city for each adjacent Market
		(	'BUILDING_MARKET',							'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER'		),
		(	'BUILDING_SUKIENNICE',						'MOD_CSC_BAKERS_MARKET_ATTACH_BAKERS_QUARTER'		),

--	CAFE --------------------------------------------------------------------------

--	+1 Gold to adjacent specialty materials improvements
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC'			),

-- 	+1 Gold to the Flour Mill in the Quarter
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WATER_MILL'		),
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_INTERNAL_GOLD_TO_WIND_MILL'			),

--	SHARED ------------------------------------------------------------------------------

-- 	+1 Gold from trade routes
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD'					),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD'					),
		(	'BUILDING_CSC_BAKERS_BAKERY',				'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD'					),
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_TRADE_ROUTES_GOLD_EXTRA'			);



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSets

		(	RequirementSetId,                              			RequirementSetType              )	VALUES

-- 	BAKERS QUARTER ----------------------------------------------------------------------

--  +1 Gold to each adjacent base or specialty materials resource from this supply chain
		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_MATERIAL_ANY',			'REQUIREMENTSET_TEST_ALL'		),
		(	'REQSET_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY',				'REQUIREMENTSET_TEST_ANY'		),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.2 Gold per Citizen to the city for each adjacent Market
		(	'REQSET_CSC_ADJ_BAKERY',								'REQUIREMENTSET_TEST_ALL'		);



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSetRequirements

		(	RequirementSetId,		                      			RequirementId	                               	)	VALUES

-- 	BAKERY ------------------------------------------------------------------------------

		(	'REQSET_CSC_ADJ_BAKERY',								'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'			),
		(	'REQSET_CSC_ADJ_BAKERY',								'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_ADJ_BAKERY',								'REQ_CSC_CITY_HAS_BAKERY'						),

-- 	SHARED ------------------------------------------------------------------------------

		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_MATERIAL_ANY',			'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
		(	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_MATERIAL_ANY',			'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY'			),
		(	'REQSET_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY',				'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'			),
		(	'REQSET_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY',				'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'			);



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Requirements

		(	RequirementId,		                          			RequirementType,	                                Inverse         )	VALUES

-- 	BAKERY ------------------------------------------------------------------------------

		(	'REQ_CSC_CITY_HAS_BAKERY',								'REQUIREMENT_CITY_HAS_BUILDING',					0				),

-- 	SHARED ------------------------------------------------------------------------------

		(	'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY',					'REQUIREMENT_REQUIREMENTSET_IS_MET',				0				);



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementArguments

		(	RequirementId,				               				Name,                           Value		                    				)	VALUES

-- 	BAKERY ------------------------------------------------------------------------------

		(	'REQ_CSC_CITY_HAS_BAKERY',								'BuildingType',					'BUILDING_CSC_BAKERS_BAKERY'					),

-- 	SHARED ------------------------------------------------------------------------------

		(	'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY',					'RequirementSetId',				'REQSET_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY'		);



--===========================================================================================================================================================================--
/*	POPULATION-SCALING GOLD */
--===========================================================================================================================================================================--

--  +1 Gold for every 5 Citizens in the city for each adjacent Zoo, Thermal Bath, or Ferris Wheel

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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC_PopulationLevels
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

DROP TABLE CSC_PopulationLevels;
