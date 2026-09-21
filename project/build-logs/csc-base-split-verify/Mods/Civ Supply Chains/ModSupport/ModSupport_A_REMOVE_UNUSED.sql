-- ModSupport_LAR_ANIMALS_REMOVE_UNUSED
-- Author: Henno
-- DateCreated: 2025-06-20 07:57:30
--------------------------------------------------------------

CREATE TABLE ResourcesToRemove (
    ResourceType TEXT NOT NULL PRIMARY KEY
);

INSERT INTO ResourcesToRemove

        (   ResourceType                    )
VALUES  (   'RESOURCE_P0K_PENGUINS'         ),      -- CR
        (   'RESOURCE_P0K_PAPYRUS'          ),

        (   'RESOURCE_LEU_P0K_CAPYBARAS'    ),      -- LAR

        (   'RESOURCE_SALMON'               ),      -- R2
        (   'RESOURCE_CAVIAR'               ),
        (   'RESOURCE_OXEN'                 ),
        (   'RESOURCE_HAM'                  ),
        (   'RESOURCE_COD'                  ),
        (   'RESOURCE_MACKEREL'             ),
        (   'RESOURCE_SEA_URCHIN'           ),
        (   'RESOURCE_MUSSELS'              ),
        (   'RESOURCE_ORCA'                 ),
        (   'RESOURCE_WOLF'                 ),
        (   'RESOURCE_TIGER'                ),
        (   'RESOURCE_LION'                 ),
        (   'RESOURCE_TOXINS'               ),

        (   'RESOURCE_SUK_SQUID'            ),      -- SO
        (   'RESOURCE_SUK_SEALS'            ),
        (   'RESOURCE_SUK_LOBSTER'          ),
        (   'RESOURCE_SUK_RAYS'             ),
        (   'RESOURCE_SUK_ABALONE'          ),
        (   'RESOURCE_SUK_CAVIAR'           ),

        (   'RESOURCE_SUK_CHEESE'           ),      -- SR
        (   'RESOURCE_SUK_CAMEL'            ),
        (   'RESOURCE_SUK_SHARK'            ),
        (   'RESOURCE_DLV_BISON'            );

DELETE FROM Types
WHERE Type IN (SELECT ResourceType FROM ResourcesToRemove);

DELETE FROM TypeTags
WHERE Type IN (SELECT ResourceType FROM ResourcesToRemove);

DELETE FROM Resources
WHERE ResourceType IN (SELECT ResourceType FROM ResourcesToRemove);

DELETE FROM Resource_ValidTerrains
WHERE ResourceType IN (SELECT ResourceType FROM ResourcesToRemove);

DELETE FROM Resource_ValidFeatures
WHERE ResourceType IN (SELECT ResourceType FROM ResourcesToRemove);

DELETE FROM Resource_YieldChanges
WHERE ResourceType IN (SELECT ResourceType FROM ResourcesToRemove);

DELETE FROM Improvement_ValidResources
WHERE ResourceType IN (SELECT ResourceType FROM ResourcesToRemove);

DROP TABLE ResourcesToRemove;