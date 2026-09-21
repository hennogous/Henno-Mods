-- ModSupport
-- Author: Henno
-- DateCreated: 2025-06-16 20:13:30
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	RESOURCES */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Tags

		(   Tag,							    Vocabulary			)
VALUES	(	'CLASS_CSC_BAKERS_BASE',	        'RESOURCE_CLASS'	),
        (	'CLASS_CSC_APOTHECARIES_BASE',      'RESOURCE_CLASS'	),
        (	'CLASS_CSC_BREWERS_BASE',           'RESOURCE_CLASS'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--	Bakers' Quarter base materials
INSERT OR IGNORE INTO TypeTags

	(	Type,							Tag			        )
SELECT	ResourceType,					'CLASS_CSC_BAKERS_BASE'
FROM	Resources
WHERE	ResourceType 					IN
	(	'RESOURCE_LEU_P0K_QUINOA'		);

-------------------------------------------------------------------------------------

--	Apothecaries' Quarter base materials
INSERT OR IGNORE INTO TypeTags

	(	Type,							Tag			        )
SELECT	ResourceType,					'CLASS_CSC_APOTHECARIES_BASE'
FROM	Resources
WHERE	ResourceType 					IN
	(	'RESOURCE_LEU_P0K_COCA',
		'RESOURCE_LEU_P0K_YERBAMATE'	);

-------------------------------------------------------------------------------------

--	Brewers' Quarter base materials
INSERT OR IGNORE INTO TypeTags

	(	Type,							Tag			        )
SELECT	ResourceType,					'CLASS_CSC_BREWERS_BASE'
FROM	Resources
WHERE	ResourceType 					IN
	(	'RESOURCE_LEU_P0K_POTATOES'		);