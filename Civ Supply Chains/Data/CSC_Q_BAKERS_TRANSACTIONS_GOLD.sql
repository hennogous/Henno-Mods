-- Gold is an additive companion to the ordinary transaction catalogue.
-- Register each source payout once. The scanner aggregates quantities by
-- property, so Production and Gold sharing that property cannot double sales.
INSERT INTO CSC_BuildingTransactionYields
        (   TransactionId,   LegKey,   Recipient,   YieldType,   AmountPerUnit,   AmountProperty   )
SELECT TransactionId, 'SOURCE_GOLD', Recipient, 'YIELD_GOLD', AmountPerUnit, AmountProperty
FROM CSC_BuildingTransactionYields
WHERE LegKey = 'SOURCE_PRODUCTION'
    AND TransactionId IN (SELECT TransactionId FROM CSC_BuildingTransactions WHERE QuarterKey = 'BAKERS');

INSERT INTO CSC_BuildingTransactionBindings
        (   TransactionId,   LegKey,   ModifierPrefix,   RequirementSetPrefix,   BindingKind   )
SELECT B.TransactionId, 'SOURCE_GOLD',
    CASE T.QuantityKind WHEN 'PARTNER_POPULATION' THEN 'MOD_CSC_BAKERS_MARKET_RETURN_GOLD_AMOUNT_BIT_' ELSE 'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_GOLD_BIT_' END,
    B.RequirementSetPrefix, B.BindingKind
FROM CSC_BuildingTransactionBindings B
JOIN CSC_BuildingTransactions T ON T.TransactionId = B.TransactionId
WHERE T.QuarterKey = 'BAKERS' AND B.LegKey = 'SOURCE_PRODUCTION';

-- Fixed Gold legs are created by the shared SOURCE_GOLD projection above.
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
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER',
        'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL',
        'REQSET_CSC_ADJ_BAKERS_QUARTER',
        'REQ_CSC_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_BAKERY',
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL',
        'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_CAFE',
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL',
        'MOD_CSC_BAKERS_GOLD_TO_WATER_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_GRANARY',
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND',
        'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL',
        'REQSET_CSC_ADJ_BAKERS_QUARTER',
        'REQ_CSC_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_BAKERY',
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL',
        'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_CAFE',
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL',
        'MOD_CSC_BAKERS_GOLD_TO_WIND_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    );
