-- CSC_TAILORS_ICONS
-- Author: Henno
-- DateCreated: 2026-06-27
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	QUARTERS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	IconTextureAtlases
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO IconTextureAtlases

		(   Name,                                   IconSize,		IconsPerRow,	IconsPerColumn,		Filename				)
VALUES  (   'ICON_ATLAS_CSC_TAILORS',				256,			4,				4,					'CSC_TAILORS_256'		),
		(   'ICON_ATLAS_CSC_TAILORS',				128,			4,				4,					'CSC_TAILORS_128'		),
		(   'ICON_ATLAS_CSC_TAILORS',				80,				4,				4,					'CSC_TAILORS_80'		),
		(   'ICON_ATLAS_CSC_TAILORS',				70,				4,				4,					'CSC_TAILORS_70'		),
		(   'ICON_ATLAS_CSC_TAILORS',				50,				4,				4,					'CSC_TAILORS_50'		),
		(   'ICON_ATLAS_CSC_TAILORS',				38,				4,				4,					'CSC_TAILORS_38'		),
		(   'ICON_ATLAS_CSC_TAILORS',				32,				4,				4,					'CSC_TAILORS_32'		);

INSERT OR IGNORE INTO IconTextureAtlases
		(	Name,									IconSize,		IconsPerRow,	IconsPerColumn,		Filename,				Baseline	)
VALUES  (	'ICON_ATLAS_CSC_TAILORS',				22,	 			4,				4,					'CSC_TAILORS_22',		6			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	IconDefinitions
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO IconDefinitions

		(   Name,															Atlas, 									'Index'		)
VALUES  (   'ICON_DISTRICT_CSC_TAILORS_QUARTER',							'ICON_ATLAS_CSC_TAILORS',				0			),
		(   'DISTRICT_CSC_TAILORS_QUARTER',									'ICON_ATLAS_CSC_TAILORS',				0			),
		(   'TAILORS',														'ICON_ATLAS_CSC_TAILORS',				0			),
		(   'ICON_DISTRICT_CSC_TAILORS_QUARTER_FOW',						'ICON_ATLAS_CSC_TAILORS',				1			);
