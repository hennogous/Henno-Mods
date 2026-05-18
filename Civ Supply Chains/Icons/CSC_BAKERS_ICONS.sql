-- CSC_ICONS
-- Author: Henno
-- DateCreated: 2025-07-06 10:07:55
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	QUARTERS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	IconTextureAtlases
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO IconTextureAtlases

		(   Name,                                   IconSize,		IconsPerRow,	IconsPerColumn,		Filename				)
VALUES  (   'ICON_ATLAS_CSC_BAKERS',				256,			4,				4,					'CSC_BAKERS_256'		),
		(   'ICON_ATLAS_CSC_BAKERS',				128,			4,				4,					'CSC_BAKERS_128'		),
		(   'ICON_ATLAS_CSC_BAKERS',				80,				4,				4,					'CSC_BAKERS_80'			),
		(   'ICON_ATLAS_CSC_BAKERS',				70,				4,				4,					'CSC_BAKERS_70'			),
		(   'ICON_ATLAS_CSC_BAKERS',				50,				4,				4,					'CSC_BAKERS_50'			),
		(   'ICON_ATLAS_CSC_BAKERS',				38,				4,				4,					'CSC_BAKERS_38'			),
		(   'ICON_ATLAS_CSC_BAKERS',				32,				4,				4,					'CSC_BAKERS_32'			),

		(	'ICON_ATLAS_CSC_GREATWORKS',			256,	 		4,				4,					'CSC_GreatWorks_256'	),
		(	'ICON_ATLAS_CSC_GREATWORKS',			64,	 			4,				4,					'CSC_GreatWorks_64'		),
		(	'ICON_ATLAS_CSC_GREATWORKS',			50,	 			4,				4,					'CSC_GreatWorks_50'		),
		(	'ICON_ATLAS_CSC_GREATWORKS',			38,	 			4,				4,					'CSC_GreatWorks_38'		),
		(	'ICON_ATLAS_CSC_GREATWORKS',			32,	 			4,				4,					'CSC_GreatWorks_32'		),

		(	'ICON_ATLAS_CSC_EFFECTS_NOTIFICATIONS',	100,	 		8,				8,					'CSC_Effect_Notifications_100'	),
		(	'ICON_ATLAS_CSC_EFFECTS_NOTIFICATIONS',	40,	 			8,				8,					'CSC_Effect_Notifications_40'	);

INSERT OR IGNORE INTO IconTextureAtlases
		(	Name,									IconSize,		IconsPerRow,	IconsPerColumn,		Filename,				Baseline	)
VALUES  (	'ICON_ATLAS_CSC_BAKERS',				22,	 			4,				4,					'CSC_BAKERS_22',		6			),
		(	'ICON_ATLAS_CSC_GREATWORKS',			22,	 			4,				4,					'CSC_GreatWorks_22',	6			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	IconDefinitions
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO IconDefinitions

		(   Name,															Atlas, 									'Index'		)
VALUES  (   'ICON_DISTRICT_CSC_BAKERS_QUARTER',								'ICON_ATLAS_CSC_BAKERS',				0			),
		(   'ICON_DISTRICT_CSC_BAKERS_QUARTER_FOW',							'ICON_ATLAS_CSC_BAKERS',				1			),
		(	'ICON_BUILDING_CSC_BAKERS_RIVER_ACCESS',						'ICON_ATLAS_CSC_BAKERS',				2			),
		(	'ICON_BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',						'ICON_ATLAS_CSC_BAKERS',				3			),
		(   'ICON_BUILDING_CSC_BAKERS_WATER_MILL',							'ICON_ATLAS_CSC_BAKERS',				4			),
		(   'ICON_BUILDING_CSC_BAKERS_WIND_MILL',							'ICON_ATLAS_CSC_BAKERS',				5			),
		(   'ICON_BUILDING_CSC_BAKERS_BAKERY',								'ICON_ATLAS_CSC_BAKERS',				6			),
		(   'ICON_BUILDING_CSC_BAKERS_CAFE',								'ICON_ATLAS_CSC_BAKERS',				7			),
		(   'ICON_BUILDING_CSC_BAKERS_STAGE_3_SPECIALIST',					'ICON_ATLAS_CSC_BAKERS',				8			),
		(   'ICON_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_ENTER',			'ICON_ATLAS_CSC_BAKERS',				9			),
		(   'ICON_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_WATER',			'ICON_ATLAS_CSC_BAKERS',				9			),
		(	'ICON_BUILDING_CSC_BAKERS_STAGE_4_SPECIALIST_GARDEN',			'ICON_ATLAS_CSC_BAKERS',				9			),
		(	'ICON_BUILDING_CSC_ARISTOCRAT',									'ICON_ATLAS_CSC_BAKERS',				12			),
		(	'ICON_EFFECT_CSC_BAKERS_STAGE_2',								'ICON_ATLAS_CSC_BAKERS',				13			),
		(	'ICON_EFFECT_CSC_BAKERS_STAGE_3',								'ICON_ATLAS_CSC_BAKERS',				14			),
		(	'ICON_EFFECT_CSC_BAKERS_STAGE_4',								'ICON_ATLAS_CSC_BAKERS',				15			),	
		(   'BAKERS',														'ICON_ATLAS_CSC_BAKERS',				0			),

		(	'RESOURCE_CSC_BAKERS_SPECIALTY',								'ICON_ATLAS_CSC_GREATWORKS',			0			),
		(	'ICON_RESOURCE_CSC_BAKERS_SPECIALTY',							'ICON_ATLAS_CSC_GREATWORKS',			0			),
		(	'ICON_RESOURCE_CSC_BAKERS_SPECIALTY_FOW',						'ICON_ATLAS_CSC_GREATWORKS',			1			),
		(	'ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_BAKERS_SPECIALTY',		'ICON_ATLAS_CSC_GREATWORKS',			0			),
		(	'ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_BAKERS_SPECIALTY_FOW',	'ICON_ATLAS_CSC_GREATWORKS',			1			),
		(	'ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_BAKERS_SPECIALTY_',		'ICON_ATLAS_CSC_GREATWORKS',			0			),
		(	'ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_BAKERS_SPECIALTY__FOW',	'ICON_ATLAS_CSC_GREATWORKS',			1			),
		(	'ICON_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY',				'ICON_ATLAS_CSC_GREATWORKS',			0			);



--===========================================================================================================================================================================--
/*	RESOURCES */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	IconTextureAtlases
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO IconTextureAtlases

		(	Name,									IconSize,	IconsPerRow,	IconsPerColumn,		Filename				)
VALUES  (	'ICON_ATLAS_CSC_RESOURCES',				256,	 	2,				2,					'CSC_Resources_256'		),
		(	'ICON_ATLAS_CSC_RESOURCES',				64,	 		2,				2,					'CSC_Resources_64'		),
		(	'ICON_ATLAS_CSC_RESOURCES',				50,	 		2,				2,					'CSC_Resources_50'		),
		(	'ICON_ATLAS_CSC_RESOURCES',				38,	 		2,				2,					'CSC_Resources_38'		),
		(	'ICON_ATLAS_CSC_RESOURCES',				32,	 		2,				2,					'CSC_Resources_32'		),
		(	'ICON_ATLAS_CSC_RESOURCES_FOW',			256,	 	2,				2,					'CSC_Resources_256_FOW'	),
		(	'ICON_ATLAS_CSC_RESOURCES_FOW',			64,	 		2,				2,					'CSC_Resources_64_FOW'	);

INSERT INTO IconTextureAtlases
		(	Name,									Baseline,	IconSize,	IconsPerRow,	IconsPerColumn,		Filename			)
VALUES  (	'ICON_ATLAS_CSC_RESOURCES',				6,			22,	 		2,				2,					'CSC_Resources_22'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	IconDefinitions
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR REPLACE INTO IconDefinitions

		(	Name,									Atlas, 									'Index'		)
VALUES  (	'ICON_RESOURCE_CSC_FLAX',				'ICON_ATLAS_CSC_RESOURCES',				0			),
		(	'RESOURCE_CSC_FLAX',					'ICON_ATLAS_CSC_RESOURCES',				0			),
		(	'ICON_RESOURCE_CSC_FLAX_FOW',			'ICON_ATLAS_CSC_RESOURCES_FOW',			0			);