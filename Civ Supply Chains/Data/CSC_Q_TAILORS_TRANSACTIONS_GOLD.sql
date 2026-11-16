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
