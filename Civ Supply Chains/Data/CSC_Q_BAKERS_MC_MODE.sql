-- CSC_MC_MODE
-- Author: Henno
-- DateCreated: 2025-06-15 11:57:14
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	INDUSTRIES & CORPORATIONS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ImprovementModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------	

INSERT INTO ImprovementModifiers

        (	ImprovementType,				ModifierId												)	VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

-- +2 Food to the Water Mill from a base materials Industry
		(	'IMPROVEMENT_INDUSTRY',			'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WATER'		),

-- +2 Food to the Wind Mill from a base materials Industry
		(	'IMPROVEMENT_INDUSTRY',			'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WIND'		),

-- +3 Food to the Water Mill from a base materials Corporation
		(	'IMPROVEMENT_CORPORATION',		'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WATER'	),

-- +3 Food to the Wind Mill from a base materials Corporation
		(	'IMPROVEMENT_CORPORATION',		'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WIND'	),

-- 	CAFE --------------------------------------------------------------------------

-- +2 Food to the Cafe from a specialty materials Industry
		(	'IMPROVEMENT_INDUSTRY',			'MOD_CSC_BAKERS_SPEC_INDUSTRY_ATTACH_QUARTER'			),

-- +3 Food to the Cafe from a specialty materials Corporation
		(	'IMPROVEMENT_CORPORATION',		'MOD_CSC_BAKERS_SPEC_CORPORATION_ATTACH_QUARTER'		);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO BuildingModifiers

        (	BuildingType,		            			ModifierId											)	VALUES

--	WIND / WATER MILL -------------------------------------------------------------------

-- +2 Production to adjacent base materials Industries
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE_PROD'	),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE_PROD'	),

-- +3 Production to adjacent base materials Corporations
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE_PROD'	),
		(	'BUILDING_CSC_BAKERS_WIND_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE_PROD'	),

--	CAFE --------------------------------------------------------------------------

-- +2 Production to adjacent specialty materials Industries
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IND_SPEC_PROD'		),

-- +3 Production to adjacent specialty materials Corporations
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_CORP_SPEC_PROD'		);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO Modifiers

		(	ModifierId,														ModifierType,										OwnerRequirementSetId,				SubjectRequirementSetId,					SubjectStackLimit	)	VALUES	

--	FLOUR MILL --------------------------------------------------------------------------

-- +2 Food to the Water Mill from a base materials Industry
		(	'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WATER',			'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_BASE',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WATER_MILL',			'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				),

-- +2 Food to the Wind Mill from a base materials Industry
		(	'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WIND',				'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_BASE',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WIND_MILL',			'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				),

-- +3 Food to the Water Mill from a base materials Corporation
		(	'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WATER',			'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_BASE',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WATER_MILL',		'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				),

-- +3 Food to the Wind Mill from a base materials Corporation
		(	'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WIND',			'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_BASE',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WIND_MILL',		'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				),

-- +2/+3 Production to adjacent base materials Industry/Corporation improvements
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE_PROD',			'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',	NULL,								'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',	NULL				),
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE_PROD',			'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',	NULL,								'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',	NULL				),
		(	'MOD_CSC_BAKERS_PROD_TO_ADJ_IND',								'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',			NULL,								NULL,										NULL				),
		(	'MOD_CSC_BAKERS_PROD_TO_ADJ_CORP',								'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',			NULL,								NULL,										NULL				),

--  +2/+3 Production to adjacent specialty materials Industry/Corporation improvements
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IND_SPEC_PROD',					'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',	NULL,								'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',	NULL				),
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_CORP_SPEC_PROD',				'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',	NULL,								'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',	NULL				),

-- 	CAFE --------------------------------------------------------------------------

-- +2 Food to the Cafe from a specialty materials Industry
		(	'MOD_CSC_BAKERS_SPEC_INDUSTRY_ATTACH_QUARTER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_SPEC_INDUSTRY_FOOD_TO_ADJ_CAFE',				'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				),

-- +3 Food to the Cafe from a specialty materials Corporation
		(	'MOD_CSC_BAKERS_SPEC_CORPORATION_ATTACH_QUARTER',				'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_SPEC_CORPORATION_FOOD_TO_ADJ_CAFE',				'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		
INSERT OR IGNORE INTO ModifierArguments
		
        (	ModifierId,			                      							Name,                       Value		                									)	VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

-- +2 Food to the Water Mill from a base materials Industry
		(  	'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WATER',				'ModifierId',         		'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WATER_MILL'     		),
        (  	'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WATER_MILL',				'BuildingType',           	'BUILDING_CSC_BAKERS_WATER_MILL'								),
        (  	'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WATER_MILL',				'YieldType',           		'YIELD_FOOD'                                                    ),
        ( 	'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WATER_MILL',				'Amount',             		2                                                               ),

-- +2 Food to the Wind Mill from a base materials Industry
		(  	'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WIND',					'ModifierId',         		'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WIND_MILL'     		),
        (  	'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WIND_MILL',				'BuildingType',           	'BUILDING_CSC_BAKERS_WIND_MILL'									),
        (  	'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WIND_MILL',				'YieldType',           		'YIELD_FOOD'                                                    ),
        ( 	'MOD_CSC_BAKERS_BASE_INDUSTRY_FOOD_TO_ADJ_WIND_MILL',				'Amount',             		2                                                               ),

-- +3 Food to the Water Mill from a base materials Corporation
		(  	'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WATER',				'ModifierId',         		'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WATER_MILL'		),
        (  	'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WATER_MILL',			'BuildingType',           	'BUILDING_CSC_BAKERS_WATER_MILL'								),
        (  	'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WATER_MILL',			'YieldType',           		'YIELD_FOOD'                                                    ),
        ( 	'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WATER_MILL',			'Amount',             		3                                                               ),

-- +3 Food to the Wind Mill from a base materials Corporation
		(  	'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WIND',				'ModifierId',         		'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WIND_MILL'			),
        (  	'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WIND_MILL',			'BuildingType',           	'BUILDING_CSC_BAKERS_WIND_MILL'									),
        (  	'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WIND_MILL',			'YieldType',           		'YIELD_FOOD'                                                    ),
        ( 	'MOD_CSC_BAKERS_BASE_CORPORATION_FOOD_TO_ADJ_WIND_MILL',			'Amount',             		3                                                               ),

-- +2 Production to adjacent base materials Industries
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE_PROD',				'ModifierId',				'MOD_CSC_BAKERS_PROD_TO_ADJ_IND'								),
		(	'MOD_CSC_BAKERS_PROD_TO_ADJ_IND',    								'YieldType',	            'YIELD_PRODUCTION'                								),
		(	'MOD_CSC_BAKERS_PROD_TO_ADJ_IND',    								'Amount',		            1		                    									),

-- +3 Production to adjacent base materials Corporations
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE_PROD',				'ModifierId',				'MOD_CSC_BAKERS_PROD_TO_ADJ_CORP'								),
		(	'MOD_CSC_BAKERS_PROD_TO_ADJ_CORP',    								'YieldType',	            'YIELD_PRODUCTION'                								),
		(	'MOD_CSC_BAKERS_PROD_TO_ADJ_CORP',    								'Amount',		            2		                    									),

-- +2 Production to adjacent specialty materials Industries
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IND_SPEC_PROD',						'ModifierId',				'MOD_CSC_BAKERS_PROD_TO_ADJ_IND'								),

-- +3 Production to adjacent specialty materials Corporations
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_CORP_SPEC_PROD',					'ModifierId',				'MOD_CSC_BAKERS_PROD_TO_ADJ_CORP'								),

-- 	CAFE --------------------------------------------------------------------------

-- +2 Food to the Cafe from a specialty materials Industry
		(  	'MOD_CSC_BAKERS_SPEC_INDUSTRY_ATTACH_QUARTER',						'ModifierId',         		'MOD_CSC_BAKERS_SPEC_INDUSTRY_FOOD_TO_ADJ_CAFE'     			),
        (  	'MOD_CSC_BAKERS_SPEC_INDUSTRY_FOOD_TO_ADJ_CAFE',					'BuildingType',           	'BUILDING_CSC_BAKERS_CAFE'										),
        (  	'MOD_CSC_BAKERS_SPEC_INDUSTRY_FOOD_TO_ADJ_CAFE',					'YieldType',           		'YIELD_FOOD'                                                    ),
        ( 	'MOD_CSC_BAKERS_SPEC_INDUSTRY_FOOD_TO_ADJ_CAFE',					'Amount',             		2                                                               ),

-- +3 Food to the Cafe from a specialty materials Corporation
		(  	'MOD_CSC_BAKERS_SPEC_CORPORATION_ATTACH_QUARTER',					'ModifierId',         		'MOD_CSC_BAKERS_SPEC_CORPORATION_FOOD_TO_ADJ_CAFE'				),
        (  	'MOD_CSC_BAKERS_SPEC_CORPORATION_FOOD_TO_ADJ_CAFE',					'BuildingType',           	'BUILDING_CSC_BAKERS_CAFE'										),
        (  	'MOD_CSC_BAKERS_SPEC_CORPORATION_FOOD_TO_ADJ_CAFE',					'YieldType',           		'YIELD_FOOD'                                                    ),
        ( 	'MOD_CSC_BAKERS_SPEC_CORPORATION_FOOD_TO_ADJ_CAFE',					'Amount',             		3                                                               );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSets

        (	RequirementSetId,								RequirementSetType              )	VALUES

-- 	+2 Production to adjacent base materials Industries
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',		'REQUIREMENTSET_TEST_ALL'       ),

-- 	+3 Production to adjacent base materials Corporations
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',		'REQUIREMENTSET_TEST_ALL'       ),

-- 	+2 Production to adjacent specialty materials Industries
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',		'REQUIREMENTSET_TEST_ALL'       ),

-- 	+3 Production to adjacent specialty materials Corporations
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',		'REQUIREMENTSET_TEST_ALL'       );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSetRequirements

        (	RequirementSetId,								RequirementId	                               	)	VALUES

-- 	+2 Production to adjacent base materials Industries
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',		'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',		'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'			),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',		'REQ_CSC_PLOT_HAS_INDUSTRY'						),

-- 	+3 Production to adjacent base materials Corporations
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',		'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',		'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'			),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',		'REQ_CSC_PLOT_HAS_CORPORATION'					),

-- 	+2 Production to adjacent specialty materials Industries
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',		'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',		'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'			),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',		'REQ_CSC_PLOT_HAS_INDUSTRY'						),

-- 	+3 Production to adjacent specialty materials Corporations
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',		'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',		'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'			),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',		'REQ_CSC_PLOT_HAS_CORPORATION'					);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Requirements

        (	RequirementId,							RequirementType,									Inverse         )	VALUES

		(	'REQ_CSC_PLOT_HAS_INDUSTRY',			'REQUIREMENT_PLOT_IMPROVEMENT_TYPE_MATCHES',		0               ),
		(	'REQ_CSC_PLOT_HAS_CORPORATION',			'REQUIREMENT_PLOT_IMPROVEMENT_TYPE_MATCHES',		0               );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementArguments

        (	RequirementId,							Name,					Value						)	VALUES

		(	'REQ_CSC_PLOT_HAS_INDUSTRY',			'ImprovementType',		'IMPROVEMENT_INDUSTRY'		),
		(	'REQ_CSC_PLOT_HAS_CORPORATION',			'ImprovementType',		'IMPROVEMENT_CORPORATION'	);

-- Specialty Products were moved to the Taxes And Politics project for later revisit.
-- Keep this file scoped to actual Monopolies & Corporations Industry/Corporation integration.
