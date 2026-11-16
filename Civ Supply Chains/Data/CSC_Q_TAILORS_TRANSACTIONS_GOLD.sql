-- Gold is an additive companion to the ordinary transaction catalogue.
-- Register each source payout once. The scanner aggregates quantities by
-- property, so Production and Gold sharing that property cannot double sales.
INSERT INTO CSC_BuildingTransactionYields
        (   TransactionId,   LegKey,   Recipient,   YieldType,   AmountPerUnit,   AmountProperty   )
SELECT TransactionId, 'SOURCE_GOLD', Recipient, 'YIELD_GOLD', AmountPerUnit, AmountProperty
FROM CSC_BuildingTransactionYields
WHERE LegKey = 'SOURCE_PRODUCTION'
    AND TransactionId IN (SELECT TransactionId FROM CSC_BuildingTransactions WHERE QuarterKey = 'TAILORS');

INSERT INTO CSC_BuildingTransactionBindings
        (   TransactionId,   LegKey,   ModifierPrefix,   RequirementSetPrefix,   BindingKind   )
SELECT B.TransactionId, 'SOURCE_GOLD',
    CASE T.QuantityKind WHEN 'PARTNER_POPULATION' THEN 'MOD_CSC_TAILORS_CUSTOMER_RETURN_GOLD_AMOUNT_BIT_' ELSE 'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_GOLD_BIT_' END,
    B.RequirementSetPrefix, B.BindingKind
FROM CSC_BuildingTransactionBindings B
JOIN CSC_BuildingTransactions T ON T.TransactionId = B.TransactionId
WHERE T.QuarterKey = 'TAILORS' AND B.LegKey = 'SOURCE_PRODUCTION';

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
        'CSC_TAILORS_TEXTILE_WORKSHOP_LIGHTHOUSE',
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_GOLD',
        'MOD_CSC_TAILORS_LIGHTHOUSE_GOLD_TO_WORKSHOP',
        'REQSET_CSC_ADJ_TAILORS_QUARTER',
        'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_TAILORS_TAILOR_GOLD_TO_WORKSHOP',
        'MOD_CSC_TAILORS_TAILOR_GOLD_TO_WORKSHOP',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',
        'SOURCE_GOLD',
        'PARTNER',
        'MOD_CSC_TAILORS_FASHION_HOUSE_GOLD_TO_WORKSHOP',
        'MOD_CSC_TAILORS_FASHION_HOUSE_GOLD_TO_WORKSHOP',
        NULL,
        NULL,
        NULL,
        NULL
    );
