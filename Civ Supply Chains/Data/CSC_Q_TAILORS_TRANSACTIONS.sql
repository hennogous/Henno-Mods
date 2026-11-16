-- Ordinary Tailors population exchanges, shared by gameplay, UI and AI.
-- Terms live here; Gold companions append Gold legs without redefining partners.
-- Do not add Service civic/material gates: these ordinary sales have none.

INSERT INTO CSC_BuildingTransactions
    (
        TransactionId,
        QuarterKey,
        SourceBuildingType,
        PartnerBuildingType,
        SpatialRule,
        QuantityKind,
        QuantityAmount,
        PopulationStep,
        PartnerDistrictMustFunction,
        SellerPopulationProperty
    )
VALUES
    (
        'CSC_TAILORS_TAILOR_MARKET',
        'TAILORS',
        'BUILDING_CSC_TAILORS_TAILOR',
        'BUILDING_MARKET',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION',
        0.101,
        NULL,
        0,
        'CSC_TAILORS_STAGE_3_CUSTOMER_POP'
    ),
    (
        'CSC_TAILORS_TAILOR_TEMPLE',
        'TAILORS',
        'BUILDING_CSC_TAILORS_TAILOR',
        'BUILDING_TEMPLE',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION',
        0.101,
        NULL,
        0,
        'CSC_TAILORS_STAGE_3_CUSTOMER_POP'
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_AMPHITHEATER',
        'TAILORS',
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'BUILDING_AMPHITHEATER',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        1,
        NULL
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_BOLSHOI_THEATRE',
        'TAILORS',
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'BUILDING_BOLSHOI_THEATRE',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        0,
        NULL
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_BROADWAY',
        'TAILORS',
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'BUILDING_BROADWAY',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        0,
        NULL
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_SYDNEY_OPERA_HOUSE',
        'TAILORS',
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'BUILDING_SYDNEY_OPERA_HOUSE',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        0,
        NULL
    );

INSERT INTO CSC_BuildingTransactionYields
        (   TransactionId,                                    LegKey,                Recipient,   YieldType,            AmountPerUnit,   AmountProperty   )
VALUES  (   'CSC_TAILORS_TAILOR_MARKET',                      'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT_Q8'   ),
        (   'CSC_TAILORS_TAILOR_MARKET',                      'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_3_MARKET_CULTURE_AMOUNT_Q8'   ),
        (   'CSC_TAILORS_TAILOR_TEMPLE',                      'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT_Q8'   ),
        (   'CSC_TAILORS_TAILOR_TEMPLE',                      'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_3_TEMPLE_CULTURE_AMOUNT_Q8'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_AMPHITHEATER',         'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_AMPHITHEATER',         'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BOLSHOI_THEATRE',      'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BOLSHOI_THEATRE',      'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BROADWAY',             'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BROADWAY',             'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SYDNEY_OPERA_HOUSE',   'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SYDNEY_OPERA_HOUSE',   'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN'   );

-- Native aliases preserve the already-QAed property-bit consumers.
INSERT INTO CSC_BuildingTransactionBindings
        (   TransactionId,                                    LegKey,                ModifierPrefix,                                                       RequirementSetPrefix,                                            BindingKind   )
VALUES  (   'CSC_TAILORS_TAILOR_MARKET',                      'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_',                   'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_',                'CITY_RATE_BITS'   ),
        (   'CSC_TAILORS_TAILOR_MARKET',                      'PARTNER_RETURN',      'MOD_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_',                       'REQSET_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_',               'CITY_RATE_BITS'   ),
        (   'CSC_TAILORS_TAILOR_TEMPLE',                      'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_',                   'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_',                'CITY_RATE_BITS'   ),
        (   'CSC_TAILORS_TAILOR_TEMPLE',                      'PARTNER_RETURN',      'MOD_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_',                       'REQSET_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_',               'CITY_RATE_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_AMPHITHEATER',         'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_',       'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_',          'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_AMPHITHEATER',         'PARTNER_RETURN',      'MOD_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_CULTURE_BIT_',   'REQSET_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_BIT_',   'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BOLSHOI_THEATRE',      'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_',       'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_',          'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BOLSHOI_THEATRE',      'PARTNER_RETURN',      'MOD_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_CULTURE_BIT_',        'REQSET_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_BIT_',        'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BROADWAY',             'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_',       'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_',          'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BROADWAY',             'PARTNER_RETURN',      'MOD_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_CULTURE_BIT_',       'REQSET_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_BIT_',       'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SYDNEY_OPERA_HOUSE',   'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_',       'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_',          'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SYDNEY_OPERA_HOUSE',   'PARTNER_RETURN',      'MOD_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_CULTURE_BIT_',         'REQSET_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_BIT_',         'BUILDING_STACK_BITS'   );
