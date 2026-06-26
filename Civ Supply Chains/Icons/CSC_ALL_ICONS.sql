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
VALUES  (	'ICON_ATLAS_CSC_EFFECTS_NOTIFICATIONS',	100,	 		8,				8,					'CSC_Effect_Notifications_100'	),
		(	'ICON_ATLAS_CSC_EFFECTS_NOTIFICATIONS',	40,	 			8,				8,					'CSC_Effect_Notifications_40'	);

INSERT OR IGNORE INTO IconTextureAtlases
		(	Name,									IconSize,		IconsPerRow,	IconsPerColumn,		Filename,				Baseline	)
VALUES  (	'ICON_ATLAS_CSC_TEXTICONS',				22,	 			2,				2,					'CSC_TextIcons',	    6			),
        (	'ICON_ATLAS_CSC_TOOLTIPS',				22,	 			1,				1,					'CSC_Tooltip_Arrow',	6			);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	IconDefinitions
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO IconDefinitions

		(   Name,						Atlas, 									'Index'		)
VALUES  (	'CSC_BASE',					'ICON_ATLAS_CSC_TEXTICONS',				0			),
        (	'CSC_SPEC',					'ICON_ATLAS_CSC_TEXTICONS',				1			),
        (	'CSC_SALES',			    'ICON_ATLAS_CSC_TEXTICONS',				2			),
        (	'CSC_GOODS',			    'ICON_ATLAS_CSC_TEXTICONS',				3			),
        
        (	'ARROW',					'ICON_ATLAS_CSC_TOOLTIPS',				0			);



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
