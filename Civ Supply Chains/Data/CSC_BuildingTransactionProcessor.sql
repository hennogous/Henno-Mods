-- Run after Quarter/ModSupport declarations, before customer adjacency readers.
-- This is a gameplay processor: it runs whether AI guidance/CE is enabled or not.
-- Native attachments and property requirements retain their existing identities;
-- this migration generates their economic arguments and public read-models.

-- Reject declarations that the supported population patterns cannot execute.
-- These two leg identities are the compatibility projection's entry points;
-- extra ordinary legs are legal, but each requires a bound native consumer.
-- Checked bindings retain the existing requirements as implementation inputs.
-- Generating their gate templates is a later, separately qualified migration.
CREATE TEMP TABLE CSC_TransactionContractCheck (Valid INTEGER CHECK (Valid = 1));

INSERT INTO CSC_TransactionContractCheck
        (   Valid   )
SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM CSC_BuildingTransactions T
    WHERE NOT EXISTS (SELECT 1 FROM Buildings WHERE BuildingType = T.SourceBuildingType)
        OR NOT EXISTS (SELECT 1 FROM Buildings WHERE BuildingType = T.PartnerBuildingType)
        OR NOT EXISTS (SELECT 1 FROM CSC_QuarterFlowBuildings F
            WHERE F.QuarterKey = T.QuarterKey AND F.BuildingType = T.SourceBuildingType
                AND F.Stage = CASE T.QuantityKind WHEN 'FIXED' THEN 2 WHEN 'PARTNER_POPULATION' THEN 3 ELSE 4 END)
        OR NOT EXISTS (SELECT 1 FROM CSC_BuildingTransactionYields Y
            WHERE Y.TransactionId = T.TransactionId AND Y.LegKey = 'SOURCE_PRODUCTION'
                AND Y.Recipient = 'SOURCE' AND (T.QuantityKind = 'FIXED' OR Y.AmountProperty IS NOT NULL))
        OR NOT EXISTS (SELECT 1 FROM CSC_BuildingTransactionYields Y
            WHERE Y.TransactionId = T.TransactionId AND Y.LegKey = 'PARTNER_RETURN'
                AND Y.Recipient = 'PARTNER' AND (T.QuantityKind = 'FIXED' OR Y.AmountProperty IS NOT NULL))
        OR (T.QuantityKind = 'PARTNER_POPULATION' AND T.SellerPopulationProperty IS NULL)
) THEN 1 ELSE 0 END;

INSERT INTO CSC_TransactionContractCheck
        (   Valid   )
SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM CSC_BuildingTransactionYields Y
    JOIN CSC_BuildingTransactions T ON T.TransactionId = Y.TransactionId
    WHERE (T.QuantityKind <> 'FIXED' AND NOT EXISTS (SELECT 1 FROM CSC_BuildingTransactionBindings B
        WHERE B.TransactionId = Y.TransactionId AND B.LegKey = Y.LegKey))
        OR (T.QuantityKind = 'FIXED' AND NOT EXISTS (SELECT 1 FROM CSC_BuildingTransactionFixedBindings B
        WHERE B.TransactionId = Y.TransactionId AND B.LegKey = Y.LegKey))
) THEN 1 ELSE 0 END;

INSERT INTO CSC_TransactionContractCheck
        (   Valid   )
SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM CSC_BuildingTransactionBindings B
    JOIN CSC_BuildingTransactionYields Y ON Y.TransactionId = B.TransactionId AND Y.LegKey = B.LegKey
    JOIN CSC_BuildingTransactions T ON T.TransactionId = B.TransactionId
    JOIN CSC_Stage4StackBits Bits ON B.BindingKind = 'BUILDING_STACK_BITS' OR Bits.Bit <= 16384
    WHERE (B.BindingKind = 'CITY_RATE_BITS') <> (T.QuantityKind = 'PARTNER_POPULATION')
        OR NOT EXISTS (SELECT 1 FROM DistrictModifiers D
            WHERE D.DistrictType = 'DISTRICT_CITY_CENTER' AND D.ModifierId = B.ModifierPrefix || Bits.Bit)
        OR NOT EXISTS (SELECT 1 FROM Modifiers M
            WHERE M.ModifierId = B.ModifierPrefix || Bits.Bit
                AND M.ModifierType = CASE B.BindingKind WHEN 'CITY_RATE_BITS'
                    THEN 'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION' ELSE 'MODIFIER_BUILDING_YIELD_CHANGE' END
                AND M.OwnerRequirementSetId IS NULL AND M.SubjectRequirementSetId = B.RequirementSetPrefix || Bits.Bit)
        OR NOT EXISTS (SELECT 1 FROM RequirementSets R
            WHERE R.RequirementSetId = B.RequirementSetPrefix || Bits.Bit AND R.RequirementSetType = 'REQUIREMENTSET_TEST_ALL')
        OR (SELECT COUNT(*) FROM RequirementSetRequirements R
            WHERE R.RequirementSetId = B.RequirementSetPrefix || Bits.Bit) <> 1
        OR NOT EXISTS (
            SELECT 1 FROM RequirementSetRequirements S
            JOIN Requirements R ON R.RequirementId = S.RequirementId
            JOIN RequirementArguments P ON P.RequirementId = R.RequirementId AND P.Name = 'PropertyName'
            JOIN RequirementArguments V ON V.RequirementId = R.RequirementId AND V.Name = 'PropertyMinimum'
            WHERE S.RequirementSetId = B.RequirementSetPrefix || Bits.Bit
                AND R.RequirementType = 'REQUIREMENT_PLOT_PROPERTY_MATCHES' AND R.Inverse = 0
                AND P.Value = Y.AmountProperty || '_BIT_' || Bits.Bit AND CAST(V.Value AS REAL) = 1.0
        )
) THEN 1 ELSE 0 END;

DROP TABLE CSC_TransactionContractCheck;

-- Compatibility read-model for existing Stage3 gameplay/UI/census consumers.
-- Its rows are generated, never separately authored. Shared Production/Gold
-- properties select the Production leg once, avoiding doubled quantities.
INSERT OR REPLACE INTO CSC_Stage3CustomerTransactions
    (
        TransactionId,
        SellerDistrictType,
        SellerBuildingType,
        CustomerDistrictType,
        CustomerBuildingType,
        SellerPopulationProperty,
        SellerReturnAmountProperty,
        CustomerYieldAmountProperty,
        EngineAmountPerPopulation
    )
SELECT
        T.TransactionId,
        S.PrereqDistrict,
        T.SourceBuildingType,
        P.PrereqDistrict,
        T.PartnerBuildingType,
        T.SellerPopulationProperty,
        SY.AmountProperty,
        PY.AmountProperty,
        T.QuantityAmount
FROM CSC_BuildingTransactions T
JOIN Buildings S ON S.BuildingType = T.SourceBuildingType
JOIN Buildings P ON P.BuildingType = T.PartnerBuildingType
JOIN CSC_BuildingTransactionYields SY ON SY.TransactionId = T.TransactionId AND SY.LegKey = 'SOURCE_PRODUCTION'
JOIN CSC_BuildingTransactionYields PY ON PY.TransactionId = T.TransactionId AND PY.LegKey = 'PARTNER_RETURN'
WHERE T.QuantityKind = 'PARTNER_POPULATION';

-- External venue projections for existing UI/native partner-graph readers.
-- Wonder partners retain their actual building identity and plot semantics.
-- Stage3 stays in its compatibility registry; fixed Stage2 remains unmigrated.
INSERT OR IGNORE INTO CSC_QuarterCustomerBuildings
        (   QuarterKey,   DistrictType,   BuildingType,   ProducerStage   )
SELECT T.QuarterKey, B.PrereqDistrict, T.PartnerBuildingType, F.Stage
FROM CSC_BuildingTransactions T
JOIN CSC_QuarterFlowBuildings F ON F.QuarterKey = T.QuarterKey AND F.BuildingType = T.SourceBuildingType
JOIN Buildings B ON B.BuildingType = T.PartnerBuildingType
WHERE T.SpatialRule = 'ADJACENT_OWNED' AND T.QuantityKind IN ('FIXED', 'PARTNER_POPULATION_STEPS')
    AND B.IsWonder = 0;

INSERT OR IGNORE INTO CSC_QuarterWonderSales
        (   QuarterKey,   BuildingType,   ProducerStage,   CustomerYieldType   )
SELECT T.QuarterKey, T.PartnerBuildingType, F.Stage, Y.YieldType
FROM CSC_BuildingTransactions T
JOIN CSC_QuarterFlowBuildings F ON F.QuarterKey = T.QuarterKey AND F.BuildingType = T.SourceBuildingType
JOIN Buildings B ON B.BuildingType = T.PartnerBuildingType
JOIN CSC_BuildingTransactionYields Y ON Y.TransactionId = T.TransactionId AND Y.LegKey = 'PARTNER_RETURN'
WHERE T.SpatialRule = 'ADJACENT_OWNED' AND B.IsWonder = 1;

-- Multiple transactions can feed one city/property consumer. Build DISTINCT
-- arguments in a constrained temporary table: identical sharing is legal;
-- conflicting declarations fail loading instead of last-writer-wins payouts.
CREATE TEMP TABLE CSC_TransactionNativeArguments
    (
    ModifierId TEXT NOT NULL,
    Name TEXT NOT NULL,
    Value TEXT NOT NULL,
    PRIMARY KEY (ModifierId, Name)
    );

INSERT INTO CSC_TransactionNativeArguments
        (   ModifierId,   Name,   Value   )
SELECT DISTINCT B.ModifierPrefix || Bits.Bit, 'YieldType', Y.YieldType
FROM CSC_BuildingTransactionBindings B
JOIN CSC_BuildingTransactionYields Y ON Y.TransactionId = B.TransactionId AND Y.LegKey = B.LegKey
JOIN CSC_Stage4StackBits Bits ON B.BindingKind = 'BUILDING_STACK_BITS' OR Bits.Bit <= 16384;

INSERT INTO CSC_TransactionNativeArguments
        (   ModifierId,   Name,   Value   )
SELECT DISTINCT B.ModifierPrefix || Bits.Bit, 'Amount',
    CASE
        WHEN B.BindingKind = 'CITY_RATE_BITS' THEN Bits.Bit * Y.AmountPerUnit / 256.0
        WHEN Bits.Bit * Y.AmountPerUnit = CAST(Bits.Bit * Y.AmountPerUnit AS INTEGER)
            THEN CAST(Bits.Bit * Y.AmountPerUnit AS INTEGER)
        ELSE Bits.Bit * Y.AmountPerUnit
    END
FROM CSC_BuildingTransactionBindings B
JOIN CSC_BuildingTransactionYields Y ON Y.TransactionId = B.TransactionId AND Y.LegKey = B.LegKey
JOIN CSC_Stage4StackBits Bits ON B.BindingKind = 'BUILDING_STACK_BITS' OR Bits.Bit <= 16384;

INSERT INTO CSC_TransactionNativeArguments
        (   ModifierId,   Name,   Value   )
SELECT DISTINCT B.ModifierPrefix || Bits.Bit, 'BuildingType',
    CASE Y.Recipient WHEN 'SOURCE' THEN T.SourceBuildingType ELSE T.PartnerBuildingType END
FROM CSC_BuildingTransactionBindings B
JOIN CSC_BuildingTransactionYields Y ON Y.TransactionId = B.TransactionId AND Y.LegKey = B.LegKey
JOIN CSC_BuildingTransactions T ON T.TransactionId = B.TransactionId
CROSS JOIN CSC_Stage4StackBits Bits
WHERE B.BindingKind = 'BUILDING_STACK_BITS';

INSERT OR REPLACE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT ModifierId, Name, Value FROM CSC_TransactionNativeArguments;

DROP TABLE CSC_TransactionNativeArguments;
