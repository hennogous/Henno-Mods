-- TAP_SPECIALTY_PRODUCTS_ICONS
-- Parked Specialty Products icons moved out of Civ Supply Chains.
--------------------------------------------------------------

INSERT OR IGNORE INTO IconTextureAtlases
        (   Name,                                   IconSize,        IconsPerRow,    IconsPerColumn,        Filename                )
VALUES  (   'ICON_ATLAS_CSC_ARISTOCRAT',            256,            1,              1,                      'Aristocrat_256'        ),
        (   'ICON_ATLAS_CSC_ARISTOCRAT',            128,            1,              1,                      'Aristocrat_128'        ),
        (   'ICON_ATLAS_CSC_ARISTOCRAT',            80,             1,              1,                      'Aristocrat_80'         ),
        (   'ICON_ATLAS_CSC_ARISTOCRAT',            70,             1,              1,                      'Aristocrat_70'         ),
        (   'ICON_ATLAS_CSC_ARISTOCRAT',            50,             1,              1,                      'Aristocrat_50'         ),
        (   'ICON_ATLAS_CSC_ARISTOCRAT',            38,             1,              1,                      'Aristocrat_38'         ),
        (   'ICON_ATLAS_CSC_ARISTOCRAT',            32,             1,              1,                      'Aristocrat_32'         ),
        (   'ICON_ATLAS_CSC_GREATWORKS',            256,            4,              4,                      'CSC_GreatWorks_256'   ),
        (   'ICON_ATLAS_CSC_GREATWORKS',            64,             4,              4,                      'CSC_GreatWorks_64'    ),
        (   'ICON_ATLAS_CSC_GREATWORKS',            50,             4,              4,                      'CSC_GreatWorks_50'    ),
        (   'ICON_ATLAS_CSC_GREATWORKS',            38,             4,              4,                      'CSC_GreatWorks_38'    ),
        (   'ICON_ATLAS_CSC_GREATWORKS',            32,             4,              4,                      'CSC_GreatWorks_32'    );

INSERT OR IGNORE INTO IconTextureAtlases
        (   Name,                                   Baseline,    IconSize,    IconsPerRow,    IconsPerColumn,        Filename            )
VALUES  (   'ICON_ATLAS_CSC_GREATWORKS',            6,           22,          4,              4,                      'CSC_GreatWorks_22' );

INSERT OR IGNORE INTO IconDefinitions
        (   Name,                                                           Atlas,                          'Index' )
VALUES  (   'ICON_BUILDING_CSC_ARISTOCRAT',                                 'ICON_ATLAS_CSC_ARISTOCRAT',     0       ),
        (   'ICON_GREATWORKOBJECT_PRODUCT',                                 'ICON_ATLAS_CSC_GREATWORKS',     0       ),
        (   'RESOURCE_CSC_BAKERS_SPECIALTY',                                'ICON_ATLAS_CSC_GREATWORKS',     0       ),
        (   'ICON_RESOURCE_CSC_BAKERS_SPECIALTY',                           'ICON_ATLAS_CSC_GREATWORKS',     0       ),
        (   'ICON_RESOURCE_CSC_BAKERS_SPECIALTY_FOW',                       'ICON_ATLAS_CSC_GREATWORKS',     1       ),
        (   'ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_BAKERS_SPECIALTY',      'ICON_ATLAS_CSC_GREATWORKS',     0       ),
        (   'ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_BAKERS_SPECIALTY_FOW',  'ICON_ATLAS_CSC_GREATWORKS',     1       ),
        (   'ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_BAKERS_SPECIALTY_',     'ICON_ATLAS_CSC_GREATWORKS',     0       ),
        (   'ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_BAKERS_SPECIALTY__FOW', 'ICON_ATLAS_CSC_GREATWORKS',     1       ),
        (   'ICON_PROJECT_CREATE_PRODUCT_CSC_BAKERS_SPECIALTY',             'ICON_ATLAS_CSC_GREATWORKS',     0       );
