-- ============================================================================
-- CSC Wonder-hosted Service multi-Wonder spike
--
-- Every Wonder receives a distinct hidden Service building type. Gameplay Lua
-- creates each variant with the host Wonder's explicit plot ID; there are no SQL
-- grant modifiers because those always select the city's first Wonder district.
-- Oracle remains a laboratory-only host so the existing test save stays useful.
-- ============================================================================

INSERT OR IGNORE INTO Types
        (   Type,                                                       Kind   )
VALUES  (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE',                'KIND_BUILDING'   ), -- Oracle/save-compatible laboratory variant
        (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BOLSHOI',        'KIND_BUILDING'   ),
        (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BROADWAY',       'KIND_BUILDING'   ),
        (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_SYDNEY',         'KIND_BUILDING'   );

INSERT OR IGNORE INTO Buildings
        (   BuildingType,                                               Name,                                                   Description,                                                   Cost,   PrereqDistrict,      PurchaseYield,   Maintenance,   CitizenSlots,   AdvisorType   )
VALUES  (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE',                'LOC_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_NAME',       'LOC_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_DESCRIPTION',   0,      'DISTRICT_WONDER',   NULL,            0,             0,              'ADVISOR_CULTURE'   ),
        (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BOLSHOI',        'LOC_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_NAME',       'LOC_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_DESCRIPTION',   0,      'DISTRICT_WONDER',   NULL,            0,             0,              'ADVISOR_CULTURE'   ),
        (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BROADWAY',       'LOC_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_NAME',       'LOC_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_DESCRIPTION',   0,      'DISTRICT_WONDER',   NULL,            0,             0,              'ADVISOR_CULTURE'   ),
        (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_SYDNEY',         'LOC_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_NAME',       'LOC_BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_DESCRIPTION',   0,      'DISTRICT_WONDER',   NULL,            0,             0,              'ADVISOR_CULTURE'   );

UPDATE Buildings
SET MustPurchase = 1
WHERE BuildingType IN (
    'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE',
    'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BOLSHOI',
    'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BROADWAY',
    'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_SYDNEY'
);

INSERT OR IGNORE INTO Buildings_XP2
        (   BuildingType,                                               Pillage   )
VALUES  (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE',                0   ),
        (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BOLSHOI',        0   ),
        (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_BROADWAY',       0   ),
        (   'BUILDING_CSC_WONDER_SERVICE_HOSTING_SPIKE_SYDNEY',         0   );
