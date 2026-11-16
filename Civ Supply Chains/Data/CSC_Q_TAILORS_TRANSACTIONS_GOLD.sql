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

-- Canonical directional material exchanges.
-- Native aliases retain existing gates; declared legs own payout amounts.
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
        'RETURN_GOLD_ORDINARY',
        'IMPROVEMENT',
        'YIELD_GOLD',
        1,
        'ANY_PLAYER_IMPROVEMENT',
        NULL
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_SPEC',
        'RETURN_GOLD_ORDINARY',
        'IMPROVEMENT',
        'YIELD_GOLD',
        1,
        'ANY_PLAYER_IMPROVEMENT',
        NULL
    );

INSERT INTO CSC_MaterialTransactionBindings
        (   TransactionId,                         LegKey,                   RootModifierId,                                             ChildModifierId,                      OwnerRequirementSetId,   SubjectRequirementSetId   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_GOLD_ORDINARY',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_GOLD',        'MOD_CSC_TAILORS_GOLD_TO_ADJ_BASE',   NULL,                    'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_GOLD_ORDINARY',   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IMP_SPEC_GOLD',   'MOD_CSC_TAILORS_GOLD_TO_ADJ_BASE',   NULL,                    'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC'   );

INSERT INTO CSC_MaterialTransactionGateBindings
        (   TransactionId,                         LegKey,                   RequirementSetId,                         RequirementId,                              GateRole   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_GOLD_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_GOLD_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_GOLD_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_GOLD_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC',   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   );
