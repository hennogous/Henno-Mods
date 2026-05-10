-- CSC_Q_BAKERS_MC_MODE_GOLD
-- Author: Henno
-- DateCreated: 2026-05-01
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	INDUSTRIES & CORPORATIONS — GOLD MODIFIERS (extracted for T&P compatibility) */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO BuildingModifiers

        (	BuildingType,		            			ModifierId											)	VALUES

--	WIND / WATER MILL -------------------------------------------------------------------

--	+2 Gold to adjacent base materials Industries
		(	'BUILDING_CSC_BAKERS_WIND_MILL',       		'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE'		),
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE'		),

--	+3 Gold to adjacent base materials Corporations
		(	'BUILDING_CSC_BAKERS_WIND_MILL',       		'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE'	),
		(	'BUILDING_CSC_BAKERS_WATER_MILL',			'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE'	),

-- 	CAFE --------------------------------------------------------------------------

--	+2 Gold to adjacent specialty materials Industries
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IND_SPEC'			),

--	+3 Gold to adjacent specialty materials Corporations
		(	'BUILDING_CSC_BAKERS_CAFE',					'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_CORP_SPEC'			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Modifiers

		(	ModifierId,												ModifierType,										OwnerRequirementSetId,	SubjectRequirementSetId,					SubjectStackLimit	)	VALUES

-- 	+2 Gold to adjacent base materials Industries
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE',		'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',	NULL,					'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',	NULL				),
		(	'MOD_CSC_BAKERS_GOLD_TO_ADJ_IND',						'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',			NULL,					NULL,										NULL      			),

-- 	+3 Gold to adjacent base materials Corporations
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE',		'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',	NULL,					'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',	NULL				),
		(	'MOD_CSC_BAKERS_GOLD_TO_ADJ_CORP',						'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',			NULL,					NULL,										NULL      			),

-- 	CAFE --------------------------------------------------------------------------

--	+2 Gold to adjacent specialty materials Industries
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IND_SPEC',				'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',	NULL,					'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',	NULL				),

--	+3 Gold to adjacent specialty materials Corporations
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_CORP_SPEC',				'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',	NULL,					'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',	NULL				);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ModifierArguments

        (	ModifierId,											Name,					Value									)	VALUES

-- 	+2 Gold to adjacent base materials Industries (already at +1 from base Quarter)
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IND_BASE',	'ModifierId',			'MOD_CSC_BAKERS_GOLD_TO_ADJ_IND'		),
		(	'MOD_CSC_BAKERS_GOLD_TO_ADJ_IND',    				'YieldType',	        'YIELD_GOLD'                			),
        (	'MOD_CSC_BAKERS_GOLD_TO_ADJ_IND',    				'Amount',		        1		                    			),

-- 	+3 Gold to adjacent base materials Corporations (already at +1 from base Quarter)
		(	'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_CORP_BASE',	'ModifierId',			'MOD_CSC_BAKERS_GOLD_TO_ADJ_CORP'		),
		(	'MOD_CSC_BAKERS_GOLD_TO_ADJ_CORP',					'YieldType',	        'YIELD_GOLD'                			),
        (	'MOD_CSC_BAKERS_GOLD_TO_ADJ_CORP',					'Amount',		        2		                    			),

-- 	CAFE --------------------------------------------------------------------------

-- 	+2 Gold to adjacent specialty materials Industries (already at +1 from base Quarter)
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IND_SPEC',			'ModifierId',			'MOD_CSC_BAKERS_GOLD_TO_ADJ_IND'		),

-- 	+3 Gold to adjacent specialty materials Corporations (already at +1 from base Quarter)
		(	'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_CORP_SPEC',			'ModifierId',			'MOD_CSC_BAKERS_GOLD_TO_ADJ_CORP'		);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSets

        (	RequirementSetId,								RequirementSetType              )	VALUES

-- 	+2 Gold to adjacent base materials Industries
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',		'REQUIREMENTSET_TEST_ALL'       ),

-- 	+3 Gold to adjacent base materials Corporations
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',		'REQUIREMENTSET_TEST_ALL'       ),

-- 	+2 Gold to adjacent specialty materials Industries
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',		'REQUIREMENTSET_TEST_ALL'       ),

-- 	+3 Gold to adjacent specialty materials Corporations
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_SPEC',		'REQUIREMENTSET_TEST_ALL'       );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSetRequirements

        (	RequirementSetId,								RequirementId	                               	)	VALUES

-- 	+2 Gold to adjacent base materials Industries
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',		'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',		'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'			),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_BASE',		'REQ_CSC_PLOT_HAS_INDUSTRY'						),

-- 	+3 Gold to adjacent base materials Corporations
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',		'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',		'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'			),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_CORP_BASE',		'REQ_CSC_PLOT_HAS_CORPORATION'					),

-- 	+2 Gold to adjacent specialty materials Industries
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',		'REQ_CSC_PLOT_ADJ_TO_OWNER'						),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',		'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'			),
        (	'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_IND_SPEC',		'REQ_CSC_PLOT_HAS_INDUSTRY'						),

-- 	+3 Gold to adjacent specialty materials Corporations
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
