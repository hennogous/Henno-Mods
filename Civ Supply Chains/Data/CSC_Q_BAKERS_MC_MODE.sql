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



--===========================================================================================================================================================================--
/*	SPECIALTY PRODUCTS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Civics
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

UPDATE Civics SET Description = '{LOC_CSC_BAKERS_STAGE_4_CIVIC}' || '{LOC_CSC_BAKERS_CAFE_DESCRIPTION_COMMISSION}' WHERE CivicType = 'CIVIC_URBANIZATION';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC_ProductReference
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

CREATE TABLE IF NOT EXISTS CSC_ProductReference
    (
    Copy TEXT
    );

INSERT OR IGNORE INTO CSC_ProductReference
		(Copy)
VALUES	('0'), ('1'), ('2'), ('3'), ('4'), ('5'), ('6'), ('7'), ('8'), ('9');

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Types
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Types

		(	Type,																Kind					)
VALUES	(	'RESOURCE_CSC_BAKERS_SPECIALTY',									'KIND_RESOURCE'			),
		(	'PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY',						'KIND_PROJECT'			);
		
---

INSERT OR IGNORE INTO Types

		(	Type,											Kind				)
SELECT		'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_' || Copy,		'KIND_GREATWORK'
FROM	CSC_ProductReference WHERE Copy > 0;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Resources
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Resources

		(	ResourceType,							ResourceClassType,			Happiness,	Frequency,	Name										)
VALUES	(	'RESOURCE_CSC_BAKERS_SPECIALTY',		'RESOURCECLASS_LUXURY',		4,			0,			'LOC_RESOURCE_CSC_BAKERS_SPECIALTY_NAME'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	GreatWorks
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO GreatWorks

	(	GreatWorkType,	GreatWorkObjectType,				Name	)
SELECT	Type,			'GREATWORKOBJECT_PRODUCT',		    'LOC_GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_X_NAME'
FROM	Types
WHERE	Type LIKE 'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_%';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	GreatWorks_ImprovementType
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO GreatWorks_ImprovementType

		(	GreatWorkType,	ResourceType						)
SELECT	Type,				'RESOURCE_CSC_BAKERS_SPECIALTY'
FROM	Types
WHERE	Type LIKE 'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_%';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	GreatWork_YieldChanges
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO GreatWork_YieldChanges

		(	GreatWorkType,	YieldType,				YieldChange		)
SELECT	Type,				'YIELD_CULTURE',		'3'
FROM	Types
WHERE	Type LIKE 'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_%';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	GreatWorkModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

/*
INSERT OR IGNORE INTO GreatWorkModifiers

		(GreatWorkType,	ModifierId								)
SELECT	Type,			'MOD_CSC_BAKERS_SPECIALTY_HOUSING'
FROM	Types
WHERE	Type LIKE 'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_%';

----

INSERT OR IGNORE INTO GreatWorkModifiers

		(GreatWorkType,	ModifierId								)
SELECT	Type,			'MOD_CSC_BAKERS_SPECIALTY_SLOT_ATTACH'
FROM	Types
WHERE	Type LIKE 'GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_%';
*/

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Projects
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Projects

		(	ProjectType,										PrereqDistrict,						RequiredBuilding,				PrereqTech,				PrereqCivic,				Cost,	AdvisorType,		Name,														ShortName,															Description		)
VALUES	(	'PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY',		'DISTRICT_CSC_BAKERS_QUARTER',		'BUILDING_CSC_BAKERS_CAFE',		NULL,					'CIVIC_URBANIZATION',		500,	'ADVISOR_GENERIC',	'LOC_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_NAME',		'LOC_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_SHORT_NAME',		'LOC_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY_DESCRIPTION'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ProjectCompletionModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ProjectCompletionModifiers

		(	ProjectType,										ModifierId																)
VALUES	(	'PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY',		'MOD_CSC_PROJECT_COMPLETION_CREATE_BAKERS_SPECIALTY'					);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Modifiers

		(	ModifierId,													ModifierType											)
VALUES	(	'MOD_CSC_PROJECT_COMPLETION_CREATE_BAKERS_SPECIALTY',		'MODIFIER_PLAYER_GRANT_RANDOM_RESOURCE_PRODUCT'			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ModifierArguments

		(	ModifierId,													Name,				Value								)
VALUES	(	'MOD_CSC_PROJECT_COMPLETION_CREATE_BAKERS_SPECIALTY',		'ResourceType',		'RESOURCE_CSC_BAKERS_SPECIALTY'		);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC_ProductReference
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

DROP TABLE CSC_ProductReference;

INSERT INTO CivilopediaPageExcludes
		(	SectionId,			PageId	) VALUES	
		(	'RESOURCES',		'RESOURCE_CSC_BAKERS_SPECIALTY');
