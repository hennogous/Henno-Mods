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
		(   'ICON_ATLAS_CSC_BAKERS',				32,				4,				4,					'CSC_BAKERS_32'			);

INSERT OR IGNORE INTO IconTextureAtlases
		(	Name,									IconSize,		IconsPerRow,	IconsPerColumn,		Filename,				Baseline	)
VALUES  (	'ICON_ATLAS_CSC_BAKERS',				22,	 			4,				4,					'CSC_BAKERS_22',		6			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	IconDefinitions
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO IconDefinitions

		(   Name,															Atlas, 									'Index'		)
VALUES  (   'ICON_DISTRICT_CSC_BAKERS_QUARTER',								'ICON_ATLAS_CSC_BAKERS',				0			),
		(   'DISTRICT_CSC_BAKERS_QUARTER',									'ICON_ATLAS_CSC_BAKERS',				0			),
		(   'ICON_DISTRICT_CSC_BAKERS_QUARTER_FOW',							'ICON_ATLAS_CSC_BAKERS',				1			),
		(	'ICON_BUILDING_CSC_BAKERS_RIVER_ACCESS',						'ICON_ATLAS_CSC_BAKERS',				2			),
		(	'ICON_BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',						'ICON_ATLAS_CSC_BAKERS',				3			),
		(   'ICON_BUILDING_CSC_BAKERS_WATER_MILL',							'ICON_ATLAS_CSC_BAKERS',				4			),
		(   'ICON_BUILDING_CSC_BAKERS_WIND_MILL',							'ICON_ATLAS_CSC_BAKERS',				5			),
		(   'ICON_BUILDING_CSC_BAKERS_BAKERY',								'ICON_ATLAS_CSC_BAKERS',				6			),
		(   'ICON_BUILDING_CSC_BAKERS_CAFE',								'ICON_ATLAS_CSC_BAKERS',				7			),
		(   'ICON_BUILDING_CSC_BAKERS_STAGE_2_SERVICE',						'ICON_ATLAS_CSC_BAKERS',				8			),
		(   'ICON_BUILDING_CSC_BAKERS_STAGE_3_SERVICE',						'ICON_ATLAS_CSC_BAKERS',				9			),
		(   'ICON_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',				'ICON_ATLAS_CSC_BAKERS',				10			),
		(   'ICON_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',				'ICON_ATLAS_CSC_BAKERS',				11			),
		(	'ICON_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_GARDEN',				'ICON_ATLAS_CSC_BAKERS',				12			);