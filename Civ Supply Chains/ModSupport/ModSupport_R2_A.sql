-- ModSupport_R2_ANIMALS
-- Author: Henno
-- DateCreated: 2025-06-20 07:58:37
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	RESOURCES */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Tags

		(   Tag,							    Vocabulary			)
VALUES	(	'CLASS_CSC_TAILORS_SPEC',	        'RESOURCE_CLASS'	),
        (   'CLASS_CSC_APOTHECARIES_BASE',      'RESOURCE_CLASS'    ),
        (   'CLASS_CSC_GOLDSMITHS_BASE',        'RESOURCE_CLASS'    );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

--	TAILORS' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

	(	Type,							Tag			        )
SELECT	ResourceType,					'CLASS_CSC_TAILORS_SPEC'
FROM	Resources
WHERE	ResourceType 					IN
	(	'RESOURCE_CASHMERE'		        );

-------------------------------------------------------------------------------------

-- Apothecaries' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,               'CLASS_CSC_APOTHECARIES_BASE'
FROM	Resources
WHERE	ResourceType                IN
    (	'RESOURCE_CORAL',
        'RESOURCE_SPONGE'           );

-------------------------------------------------------------------------------------

-- Apothecaries' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,               'CLASS_CSC_GOLDSMITHS_BASE'
FROM	Resources
WHERE	ResourceType                IN
    (	'RESOURCE_CORAL'            );
