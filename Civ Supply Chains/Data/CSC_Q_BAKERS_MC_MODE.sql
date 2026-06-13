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

-- +2 Production to the Water Mill from a base materials Industry
		(	'IMPROVEMENT_INDUSTRY',			'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WATER'		),

-- +2 Production to the Wind Mill from a base materials Industry
		(	'IMPROVEMENT_INDUSTRY',			'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WIND'		),

-- +3 Production to the Water Mill from a base materials Corporation
		(	'IMPROVEMENT_CORPORATION',		'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WATER'	),

-- +3 Production to the Wind Mill from a base materials Corporation
		(	'IMPROVEMENT_CORPORATION',		'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WIND'	),

-- 	CAFE --------------------------------------------------------------------------

-- +2 Production to the Cafe from a specialty materials Industry
		(	'IMPROVEMENT_INDUSTRY',			'MOD_CSC_BAKERS_SPEC_INDUSTRY_ATTACH_QUARTER'			),

-- +3 Production to the Cafe from a specialty materials Corporation
		(	'IMPROVEMENT_CORPORATION',		'MOD_CSC_BAKERS_SPEC_CORPORATION_ATTACH_QUARTER'		);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------												

INSERT OR IGNORE INTO Modifiers

		(	ModifierId,														ModifierType,										OwnerRequirementSetId,				SubjectRequirementSetId,					SubjectStackLimit	)	VALUES	

--	FLOUR MILL --------------------------------------------------------------------------

-- +2 Production to the Water Mill from a base materials Industry
		(	'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WATER',			'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_BASE',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_BASE_INDUSTRY_PROD_TO_ADJ_WATER_MILL',			'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				),

-- +2 Production to the Wind Mill from a base materials Industry
		(	'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WIND',				'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_BASE',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_BASE_INDUSTRY_PROD_TO_ADJ_WIND_MILL',			'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				),

-- +3 Production to the Water Mill from a base materials Industry
		(	'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WATER',			'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_BASE',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_BASE_CORPORATION_PROD_TO_ADJ_WATER_MILL',		'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				),

-- +3 Production to the Wind Mill from a base materials Industry
		(	'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WIND',			'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_BASE',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_BASE_CORPORATION_PROD_TO_ADJ_WIND_MILL',		'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				),

-- 	CAFE --------------------------------------------------------------------------

-- +2 Production to the Cafe from a specialty materials Industry
		(	'MOD_CSC_BAKERS_SPEC_INDUSTRY_ATTACH_QUARTER',					'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_SPEC_INDUSTRY_PROD_TO_ADJ_CAFE',			'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				),

-- +3 Production to the Cafe from a specialty materials Corporation
		(	'MOD_CSC_BAKERS_SPEC_CORPORATION_ATTACH_QUARTER',				'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',	'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',	'REQSET_CSC_ADJ_BAKERS_QUARTER',			NULL				),
		(	'MOD_CSC_BAKERS_SPEC_CORPORATION_PROD_TO_ADJ_CAFE',		'MODIFIER_BUILDING_YIELD_CHANGE',					NULL,								NULL,										NULL				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
		
INSERT OR IGNORE INTO ModifierArguments
		
        (	ModifierId,			                      							Name,                       Value		                									)	VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

-- +2 Production to the Water Mill from a base materials Industry
		(  	'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WATER',				'ModifierId',         		'MOD_CSC_BAKERS_BASE_INDUSTRY_PROD_TO_ADJ_WATER_MILL'     		),    
        (  	'MOD_CSC_BAKERS_BASE_INDUSTRY_PROD_TO_ADJ_WATER_MILL',				'BuildingType',           	'BUILDING_CSC_BAKERS_WATER_MILL'								),
        (  	'MOD_CSC_BAKERS_BASE_INDUSTRY_PROD_TO_ADJ_WATER_MILL',				'YieldType',           		'YIELD_PRODUCTION'                                              ),
        ( 	'MOD_CSC_BAKERS_BASE_INDUSTRY_PROD_TO_ADJ_WATER_MILL',				'Amount',             		2                                                               ),

-- +2 Production to the Wind Mill from a base materials Industry
		(  	'MOD_CSC_BAKERS_BASE_INDUSTRY_ATTACH_QUARTER_WIND',					'ModifierId',         		'MOD_CSC_BAKERS_BASE_INDUSTRY_PROD_TO_ADJ_WIND_MILL'     		),    
        (  	'MOD_CSC_BAKERS_BASE_INDUSTRY_PROD_TO_ADJ_WIND_MILL',				'BuildingType',           	'BUILDING_CSC_BAKERS_WIND_MILL'									),
        (  	'MOD_CSC_BAKERS_BASE_INDUSTRY_PROD_TO_ADJ_WIND_MILL',				'YieldType',           		'YIELD_PRODUCTION'                                              ),
        ( 	'MOD_CSC_BAKERS_BASE_INDUSTRY_PROD_TO_ADJ_WIND_MILL',				'Amount',             		2                                                               ),

-- +3 Production to the Water Mill from a base materials Industry
		(  	'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WATER',				'ModifierId',         		'MOD_CSC_BAKERS_BASE_CORPORATION_PROD_TO_ADJ_WATER_MILL'		),    
        (  	'MOD_CSC_BAKERS_BASE_CORPORATION_PROD_TO_ADJ_WATER_MILL',			'BuildingType',           	'BUILDING_CSC_BAKERS_WATER_MILL'								),
        (  	'MOD_CSC_BAKERS_BASE_CORPORATION_PROD_TO_ADJ_WATER_MILL',			'YieldType',           		'YIELD_PRODUCTION'                                              ),
        ( 	'MOD_CSC_BAKERS_BASE_CORPORATION_PROD_TO_ADJ_WATER_MILL',			'Amount',             		3                                                               ),

-- +3 Production to the Wind Mill from a base materials Industry
		(  	'MOD_CSC_BAKERS_BASE_CORPORATION_ATTACH_QUARTER_WIND',				'ModifierId',         		'MOD_CSC_BAKERS_BASE_CORPORATION_PROD_TO_ADJ_WIND_MILL'			),    
        (  	'MOD_CSC_BAKERS_BASE_CORPORATION_PROD_TO_ADJ_WIND_MILL',			'BuildingType',           	'BUILDING_CSC_BAKERS_WIND_MILL'									),
        (  	'MOD_CSC_BAKERS_BASE_CORPORATION_PROD_TO_ADJ_WIND_MILL',			'YieldType',           		'YIELD_PRODUCTION'                                              ),
        ( 	'MOD_CSC_BAKERS_BASE_CORPORATION_PROD_TO_ADJ_WIND_MILL',			'Amount',             		3                                                               ),

-- 	CAFE --------------------------------------------------------------------------

-- +2 Production to the Cafe from a specialty materials Industry
		(  	'MOD_CSC_BAKERS_SPEC_INDUSTRY_ATTACH_QUARTER',						'ModifierId',         		'MOD_CSC_BAKERS_SPEC_INDUSTRY_PROD_TO_ADJ_CAFE'     		),    
        (  	'MOD_CSC_BAKERS_SPEC_INDUSTRY_PROD_TO_ADJ_CAFE',				'BuildingType',           	'BUILDING_CSC_BAKERS_CAFE'								),
        (  	'MOD_CSC_BAKERS_SPEC_INDUSTRY_PROD_TO_ADJ_CAFE',				'YieldType',           		'YIELD_PRODUCTION'                                              ),
        ( 	'MOD_CSC_BAKERS_SPEC_INDUSTRY_PROD_TO_ADJ_CAFE',				'Amount',             		2                                                               ),

-- +3 Production to the Cafe from a specialty materials Corporation
		(  	'MOD_CSC_BAKERS_SPEC_CORPORATION_ATTACH_QUARTER',					'ModifierId',         		'MOD_CSC_BAKERS_SPEC_CORPORATION_PROD_TO_ADJ_CAFE'		),    
        (  	'MOD_CSC_BAKERS_SPEC_CORPORATION_PROD_TO_ADJ_CAFE',			'BuildingType',           	'BUILDING_CSC_BAKERS_CAFE'								),
        (  	'MOD_CSC_BAKERS_SPEC_CORPORATION_PROD_TO_ADJ_CAFE',			'YieldType',           		'YIELD_PRODUCTION'                                              ),
        ( 	'MOD_CSC_BAKERS_SPEC_CORPORATION_PROD_TO_ADJ_CAFE',			'Amount',             		3                                                               );

-- Specialty Products were moved to the Taxes And Politics project for later revisit.
-- Keep this file scoped to actual Monopolies & Corporations Industry/Corporation integration.
