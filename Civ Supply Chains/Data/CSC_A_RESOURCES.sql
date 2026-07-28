-- CSC_ANIMALS
-- Author: Henno
-- DateCreated: 2025-06-20 07:58:11
--------------------------------------------------------------

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Tags

	    (   Tag,                                    Vocabulary              )
VALUES	(	'CLASS_CSC_BAKERS_BASE',	        'RESOURCE_CLASS'	),
        (	'CLASS_CSC_BAKERS_SPEC',	        'RESOURCE_CLASS'	),
        (	'CLASS_CSC_APOTHECARIES_BASE',          'RESOURCE_CLASS'	),
        (	'CLASS_CSC_CARPENTERS_SPEC',            'RESOURCE_CLASS'	),
        (       'CLASS_CSC_GOLDSMITHS_SPEC',            'RESOURCE_CLASS'        ),
        (	'CLASS_CSC_BREWERS_SPEC',               'RESOURCE_CLASS'	);

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
INSERT OR IGNORE INTO TypeTags

        (   Type,                  Tag                                  )
VALUES  (   'RESOURCE_CATTLE',     'CLASS_CSC_BAKERS_BASE'              ),
        (   'RESOURCE_HONEY',      'CLASS_CSC_BAKERS_SPEC'              ),
        (   'RESOURCE_HONEY',      'CLASS_CSC_APOTHECARIES_BASE'        ),
        (   'RESOURCE_SILK',       'CLASS_CSC_CARPENTERS_SPEC'          ),
        (   'RESOURCE_PEARLS',     'CLASS_CSC_GOLDSMITHS_SPEC'          ),
        (   'RESOURCE_HONEY',      'CLASS_CSC_BREWERS_SPEC'             );
