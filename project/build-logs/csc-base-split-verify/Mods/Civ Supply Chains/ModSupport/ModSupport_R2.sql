-- ModSupport_R2
-- Author: Henno
-- DateCreated: 2025-06-17 09:24:58
--------------------------------------------------------------

--===========================================================================================================================================================================--
/*	RESOURCES */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Tags

	(       Tag,                                    Vocabulary          )
VALUES	(	'CLASS_CSC_BAKERS_BASE',                'RESOURCE_CLASS'	),
        (	'CLASS_CSC_BAKERS_SPEC',	            'RESOURCE_CLASS'	),
        (	'CLASS_CSC_TAILORS_BASE',	            'RESOURCE_CLASS'	),
        (	'CLASS_CSC_TAILORS_SPEC',	            'RESOURCE_CLASS'	),
        (	'CLASS_CSC_APOTHECARIES_BASE',          'RESOURCE_CLASS'	),
        (	'CLASS_CSC_APOTHECARIES_SPEC',          'RESOURCE_CLASS'	),        
        (	'CLASS_CSC_STONEMASONS_BASE',           'RESOURCE_CLASS'	),
        (	'CLASS_CSC_STONEMASONS_SPEC',           'RESOURCE_CLASS'	),
        (	'CLASS_CSC_CARPENTERS_BASE',            'RESOURCE_CLASS'	),
        (	'CLASS_CSC_CARPENTERS_SPEC',	        'RESOURCE_CLASS'	),
        (	'CLASS_CSC_BLACKSMITHS_BASE',           'RESOURCE_CLASS'	),
        (	'CLASS_CSC_BLACKSMITHS_SPEC',           'RESOURCE_CLASS'	),
        (	'CLASS_CSC_GOLDSMITHS_BASE',	        'RESOURCE_CLASS'	),
        (	'CLASS_CSC_GOLDSMITHS_SPEC',	        'RESOURCE_CLASS'	), 
        (	'CLASS_CSC_BREWERS_BASE',               'RESOURCE_CLASS'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Bakers' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                           Tag			        )
SELECT	ResourceType,			'CLASS_CSC_BAKERS_BASE'
FROM	Resources
WHERE	ResourceType 			IN
    (	'RESOURCE_BARLEY',
        'RESOURCE_SORGHUM'              );

-- Bakers' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,				Tag			        )
SELECT	ResourceType,			'CLASS_CSC_BAKERS_SPEC'
FROM	Resources
WHERE	ResourceType 			IN
    (	'RESOURCE_BERRIES',
        'RESOURCE_DATES',
        'RESOURCE_POPPIES',
        'RESOURCE_SAFFRON',
        'RESOURCE_STRAWBERRY',
        'RESOURCE_MAPLE',
        'RESOURCE_TOMATO'               );

-------------------------------------------------------------------------------------

-- TAILORS' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,			    'CLASS_CSC_TAILORS_BASE'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_BAMBOO'           );

-- TAILORS' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,			    'CLASS_CSC_TAILORS_SPEC'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_GOLD2'            );

-------------------------------------------------------------------------------------

-- Apothecaries' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,               'CLASS_CSC_APOTHECARIES_BASE'
FROM	Resources
WHERE	ResourceType                IN
    (	'RESOURCE_ALGAE',
        'RESOURCE_ALOE',
        'RESOURCE_MEDIHERBS',
        'RESOURCE_MUSHROOMS',
        'RESOURCE_POPPIES',
        'RESOURCE_SANDALWOOD',
        'RESOURCE_SEASHELLS'        );

-- Apothecaries' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,			    'CLASS_CSC_APOTHECARIES_SPEC'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_GOLD2'            );

-------------------------------------------------------------------------------------

-- Stonemasons' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,               'CLASS_CSC_STONEMASONS_BASE'
FROM	Resources
WHERE	ResourceType                IN
    (	'RESOURCE_GRANITE',
        'RESOURCE_LIMESTONE',
        'RESOURCE_TRAVERTINE'       );

-- Stonemasons' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,			    'CLASS_CSC_STONEMASONS_SPEC'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_ALABASTER',
        'RESOURCE_QUARTZ'           );

-------------------------------------------------------------------------------------

-- Carpenters' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,               'CLASS_CSC_CARPENTERS_BASE'
FROM	Resources
WHERE	ResourceType                IN
    (	'RESOURCE_BAMBOO',
        'RESOURCE_OAK',
        'RESOURCE_PINE',
        'RESOURCE_MAPLE'            );

-- Carpenters' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,			    'CLASS_CSC_CARPENTERS_SPEC'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_SAKURA',
        'RESOURCE_EBONY',
        'RESOURCE_RUBBER',
        'RESOURCE_SANDALWOOD'       );

-------------------------------------------------------------------------------------

-- Blacksmiths' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,               'CLASS_CSC_BLACKSMITHS_BASE'
FROM	Resources
WHERE	ResourceType                IN
    (	'RESOURCE_LEAD',
        'RESOURCE_TIN'              );

-- Blacksmiths' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,			    'CLASS_CSC_BLACKSMITHS_SPEC'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_GOLD2',
        'RESOURCE_PLATINUM'         );

-------------------------------------------------------------------------------------

-- Goldsmiths' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,               'CLASS_CSC_GOLDSMITHS_BASE'
FROM	Resources
WHERE	ResourceType                IN
    (	'RESOURCE_ALABASTER',
        'RESOURCE_GOLD2',
        'RESOURCE_QUARTZ',
        'RESOURCE_SEASHELLS'        );

-- Goldsmiths' Quarter specialty materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,			    'CLASS_CSC_GOLDSMITHS_SPEC'
FROM	Resources
WHERE	ResourceType 			    IN
    (	'RESOURCE_LAPIS',
        'RESOURCE_RUBY'             );

-------------------------------------------------------------------------------------

-- Brewers' Quarter base materials
INSERT OR IGNORE INTO TypeTags

    (	Type,                       Tag     )
SELECT	ResourceType,               'CLASS_CSC_BREWERS_BASE'
FROM	Resources
WHERE	ResourceType                IN
    (	'RESOURCE_BARLEY',
        'RESOURCE_SORGHUM'          );
