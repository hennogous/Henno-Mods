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
        'CSC_TAILORS_TEXTILE_WORKSHOP_LIGHTHOUSE',
        'TAILORS',
        'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',
        'BUILDING_LIGHTHOUSE',
        'ADJACENT_OWNED',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',
        'TAILORS',
        'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',
        'BUILDING_CSC_TAILORS_TAILOR',
        'SAME_CITY',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',
        'TAILORS',
        'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'SAME_CITY',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    );

INSERT INTO CSC_BuildingTransactionYields
        (   TransactionId,                                              LegKey,                Recipient,   YieldType,            AmountPerUnit,   AmountProperty   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_LIGHTHOUSE',                  'PARTNER_RETURN',      'PARTNER',   'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_LIGHTHOUSE',                  'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',          'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               NULL   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',          'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',   'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               NULL   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',   'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   );

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
        'CSC_TAILORS_TEXTILE_WORKSHOP_LIGHTHOUSE',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_TAILORS_WORKSHOP_ATTACH_HARBOR_LIGHTHOUSE',
        'MOD_CSC_TAILORS_WORKSHOP_PROD_TO_LIGHTHOUSE',
        'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE',
        'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_TAILORS_DISTRICT_IS_HARBOR',
        'REQ_CSC_TAILORS_CITY_HAS_LIGHTHOUSE'
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_LIGHTHOUSE',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_PROD',
        'MOD_CSC_TAILORS_LIGHTHOUSE_PROD_TO_WORKSHOP',
        'REQSET_CSC_ADJ_TAILORS_QUARTER',
        'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR',
        'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP',
        'MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE',
        'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP',
        'MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP',
        NULL,
        NULL,
        NULL,
        NULL
    );

-- Canonical directional material exchanges.
-- Native aliases retain existing gates; declared legs own payout amounts.
INSERT INTO CSC_MaterialTransactions
        (   TransactionId,                         QuarterKey,   ProducerBuildingType,                      MaterialClass   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'TAILORS',    'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'CLASS_CSC_TAILORS_BASE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'TAILORS',    'BUILDING_CSC_TAILORS_FASHION_HOUSE',      'CLASS_CSC_TAILORS_SPEC'   );

INSERT INTO CSC_MaterialTransactionYields
    (
        TransactionId,
        LegKey,
        Recipient,
        YieldType,
        Amount,
        ImprovementScope,
        ImprovementType
    )
VALUES
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',
        'INPUT_ORDINARY',
        'PRODUCER',
        'YIELD_CULTURE',
        1,
        'REGISTERED_INPUT',
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',
        'RETURN_PRODUCTION_ORDINARY',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        1,
        'ANY_PLAYER_IMPROVEMENT',
        NULL
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_SPEC',
        'INPUT_ORDINARY',
        'PRODUCER',
        'YIELD_CULTURE',
        1,
        'REGISTERED_INPUT',
        NULL
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_SPEC',
        'RETURN_PRODUCTION_ORDINARY',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        1,
        'ANY_PLAYER_IMPROVEMENT',
        NULL
    );

INSERT INTO CSC_MaterialTransactionBindings
        (   TransactionId,                         LegKey,                         RootModifierId,                                             ChildModifierId,                                     OwnerRequirementSetId,                SubjectRequirementSetId   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_ORDINARY',               'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER',          'MOD_CSC_TAILORS_BASE_IMPROV_CULTURE_TO_WORKSHOP',   'REQSET_CSC_TAILORS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_ORDINARY',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_PROD',        'MOD_CSC_TAILORS_PROD_TO_ADJ_BASE',                  NULL,                                 'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_ORDINARY',               'MOD_CSC_TAILORS_SPEC_IMPROVEMENT_ATTACH_QUARTER',          'MOD_CSC_TAILORS_SPEC_CULTURE_TO_FASHION_HOUSE',     'REQSET_CSC_TAILORS_PLOT_HAS_SPEC',   'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_ORDINARY',   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IMP_SPEC_PROD',   'MOD_CSC_TAILORS_PROD_TO_ADJ_BASE',                  NULL,                                 'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC'   );

INSERT INTO CSC_MaterialTransactionGateBindings
        (   TransactionId,                         LegKey,                         RequirementSetId,                         RequirementId,                              GateRole   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_ORDINARY',               'REQSET_CSC_TAILORS_PLOT_HAS_BASE',       'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_ORDINARY',               'REQSET_CSC_ADJ_TAILORS_QUARTER',         'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_ORDINARY',               'REQSET_CSC_ADJ_TAILORS_QUARTER',         'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_ORDINARY',               'REQSET_CSC_TAILORS_PLOT_HAS_SPEC',       'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_ORDINARY',               'REQSET_CSC_ADJ_TAILORS_QUARTER',         'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_ORDINARY',               'REQSET_CSC_ADJ_TAILORS_QUARTER',         'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC',   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   );
