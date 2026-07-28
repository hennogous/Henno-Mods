-- ModSupport_SR
-- Author: Henno
-- DateCreated: 2025-06-17 09:25:40
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	RESOURCES */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Tags

	    (   Tag,                                Vocabulary          )
VALUES	(	'CLASS_CSC_TAILORS_SPEC',	        'RESOURCE_CLASS'	),
        (	'CLASS_CSC_APOTHECARIES_SPEC',      'RESOURCE_CLASS'	),
        (	'CLASS_CSC_STONEMASONS_SPEC',       'RESOURCE_CLASS'	),
        (	'CLASS_CSC_BLACKSMITHS_SPEC',	    'RESOURCE_CLASS'	),
        (	'CLASS_CSC_GOLDSMITHS_BASE',	    'RESOURCE_CLASS'	),

        (	'CLASS_CSC_GOLDSMITHS_SPEC',	    'RESOURCE_CLASS'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- TAILORS' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,				        Tag     )
SELECT	ResourceType,			    'CLASS_CSC_TAILORS_SPEC'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_GOLD'             );

-------------------------------------------------------------------------------------

-- Apothecaries' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,			    'CLASS_CSC_APOTHECARIES_SPEC'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_GOLD'             );

-------------------------------------------------------------------------------------

-- Stonemasons' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,			    'CLASS_CSC_STONEMASONS_SPEC'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_SUK_OBSIDIAN'     );

-------------------------------------------------------------------------------------

-- Blacksmiths' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,			    'CLASS_CSC_BLACKSMITHS_SPEC'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_GOLD'             );

-------------------------------------------------------------------------------------

-- Goldsmiths' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,			    'CLASS_CSC_GOLDSMITHS_BASE'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_GOLD',
        'RESOURCE_SUK_OBSIDIAN'     );
