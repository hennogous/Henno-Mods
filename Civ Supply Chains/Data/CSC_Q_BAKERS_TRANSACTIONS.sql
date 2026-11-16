-- Ordinary Bakers population exchanges, shared by gameplay, UI and AI.
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
        'CSC_BAKERS_BAKERY_MARKET',
        'BAKERS',
        'BUILDING_CSC_BAKERS_BAKERY',
        'BUILDING_MARKET',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION',
        0.101,
        NULL,
        0,
        'CSC_BAKERS_STAGE_3_MARKET_CUSTOMER_POP'
    ),
    (
        'CSC_BAKERS_CAFE_ZOO',
        'BAKERS',
        'BUILDING_CSC_BAKERS_CAFE',
        'BUILDING_ZOO',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        0,
        NULL
    ),
    (
        'CSC_BAKERS_CAFE_FERRIS_WHEEL',
        'BAKERS',
        'BUILDING_CSC_BAKERS_CAFE',
        'BUILDING_FERRIS_WHEEL',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        0,
        NULL
    );

INSERT INTO CSC_BuildingTransactionYields
        (   TransactionId,                    LegKey,                Recipient,   YieldType,            AmountPerUnit,   AmountProperty   )
VALUES  (   'CSC_BAKERS_BAKERY_MARKET',       'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_BAKERS_STAGE_3_MARKET_RETURN_AMOUNT_Q8'   ),
        (   'CSC_BAKERS_BAKERY_MARKET',       'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               'CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT_Q8'   ),
        (   'CSC_BAKERS_CAFE_ZOO',            'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_BAKERS_STAGE_4_CAFE_RETURN'   ),
        (   'CSC_BAKERS_CAFE_ZOO',            'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_BAKERS_STAGE_4_ZOO_CULTURE_RETURN'   ),
        (   'CSC_BAKERS_CAFE_FERRIS_WHEEL',   'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_BAKERS_STAGE_4_CAFE_RETURN'   ),
        (   'CSC_BAKERS_CAFE_FERRIS_WHEEL',   'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_BAKERS_STAGE_4_FERRIS_CULTURE_RETURN'   );

-- Native aliases preserve the already-QAed property-bit consumers.
INSERT INTO CSC_BuildingTransactionBindings
        (   TransactionId,                    LegKey,                ModifierPrefix,                                                              RequirementSetPrefix,                                     BindingKind   )
VALUES  (   'CSC_BAKERS_BAKERY_MARKET',       'SOURCE_PRODUCTION',   'MOD_CSC_BAKERS_MARKET_RETURN_PROD_AMOUNT_BIT_',                             'REQSET_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_',            'CITY_RATE_BITS'   ),
        (   'CSC_BAKERS_BAKERY_MARKET',       'PARTNER_RETURN',      'MOD_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_',                                    'REQSET_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_',              'CITY_RATE_BITS'   ),
        (   'CSC_BAKERS_CAFE_ZOO',            'SOURCE_PRODUCTION',   'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_PRODUCTION_BIT_',                        'REQSET_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_',             'BUILDING_STACK_BITS'   ),
        (   'CSC_BAKERS_CAFE_ZOO',            'PARTNER_RETURN',      'MOD_CSC_BAKERS_STAGE_4_ZOO_CULTURE_RETURN_BUILDING_ZOO_BIT_',               'REQSET_CSC_BAKERS_STAGE_4_ZOO_CULTURE_RETURN_BIT_',      'BUILDING_STACK_BITS'   ),
        (   'CSC_BAKERS_CAFE_FERRIS_WHEEL',   'SOURCE_PRODUCTION',   'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_PRODUCTION_BIT_',                        'REQSET_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_',             'BUILDING_STACK_BITS'   ),
        (   'CSC_BAKERS_CAFE_FERRIS_WHEEL',   'PARTNER_RETURN',      'MOD_CSC_BAKERS_STAGE_4_FERRIS_CULTURE_RETURN_BUILDING_FERRIS_WHEEL_BIT_',   'REQSET_CSC_BAKERS_STAGE_4_FERRIS_CULTURE_RETURN_BIT_',   'BUILDING_STACK_BITS'   );

-- Fixed ordinary exchanges. Local building yields are city-scoped natively.
-- Native aliases below preserve each leg's owner and asymmetric adjacency gates.
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
        'CSC_BAKERS_WATER_MILL_GRANARY',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WATER_MILL',
        'BUILDING_GRANARY',
        'ADJACENT_OWNED',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_BAKERY',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WATER_MILL',
        'BUILDING_CSC_BAKERS_BAKERY',
        'SAME_CITY',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_CAFE',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WATER_MILL',
        'BUILDING_CSC_BAKERS_CAFE',
        'SAME_CITY',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_GRANARY',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WIND_MILL',
        'BUILDING_GRANARY',
        'ADJACENT_OWNED',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_BAKERY',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WIND_MILL',
        'BUILDING_CSC_BAKERS_BAKERY',
        'SAME_CITY',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_CAFE',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WIND_MILL',
        'BUILDING_CSC_BAKERS_CAFE',
        'SAME_CITY',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    );

INSERT INTO CSC_BuildingTransactionYields
        (   TransactionId,                               LegKey,                Recipient,   YieldType,            AmountPerUnit,   AmountProperty   )
VALUES  (   'CSC_BAKERS_WATER_MILL_GRANARY',             'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WATER_MILL_GRANARY',             'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_BAKERS_WATER_MILL_CSC_BAKERS_BAKERY',   'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WATER_MILL_CSC_BAKERS_BAKERY',   'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_BAKERS_WATER_MILL_CSC_BAKERS_CAFE',     'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WATER_MILL_CSC_BAKERS_CAFE',     'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_GRANARY',              'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_GRANARY',              'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_CSC_BAKERS_BAKERY',    'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_CSC_BAKERS_BAKERY',    'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_CSC_BAKERS_CAFE',      'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_CSC_BAKERS_CAFE',      'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   );

INSERT INTO CSC_BuildingTransactionFixedBindings
    (
        TransactionId,
        LegKey,
        OwnerSide,
        RootModifierId,
        ChildModifierId,
        SubjectRequirementSetId,
        AdjacencyRequirementId,
        DistrictRequirementId,
        BuildingRequirementId
    )
VALUES
    (
        'CSC_BAKERS_WATER_MILL_GRANARY',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',
        'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',
        'REQ_CSC_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_DISTRICT_IS_CITY_CENTER',
        'REQ_CSC_CITY_HAS_GRANARY'
    ),
    (
        'CSC_BAKERS_WATER_MILL_GRANARY',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER_PROD',
        'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
        'REQSET_CSC_ADJ_BAKERS_QUARTER',
        'REQ_CSC_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_BAKERY',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_BAKERY',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
        'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_CAFE',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FOOD_TO_CAFE',
        'MOD_CSC_BAKERS_FOOD_TO_CAFE',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_CAFE',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
        'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_GRANARY',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',
        'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',
        'REQ_CSC_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_DISTRICT_IS_CITY_CENTER',
        'REQ_CSC_CITY_HAS_GRANARY'
    ),
    (
        'CSC_BAKERS_WIND_MILL_GRANARY',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND_PROD',
        'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',
        'REQSET_CSC_ADJ_BAKERS_QUARTER',
        'REQ_CSC_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_BAKERY',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_BAKERY',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',
        'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_CAFE',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FOOD_TO_CAFE',
        'MOD_CSC_BAKERS_FOOD_TO_CAFE',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_CAFE',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',
        'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    );
