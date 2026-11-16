-- Gameplay-owned directional material terms -> native effects. Runs after the
-- Quarter/Gold/M&C declarations, before fixed/population projections. Core and
-- compatibility files retain early native owner registrations for FK ordering;
-- their economic arguments are generated here. The late800010 host pass derives
-- missing ordinary input attachments after CL/R2 mappings finish loading.
--
-- These finite templates reproduce the existing graph. No worked/pillage gate
-- is invented in SQL. Native owner/recipient lifecycle and observed workers are
-- separate facts for the economic reader. Services keep their original gates.
CREATE TEMP TABLE CSC_MaterialLeafProjection (
    ModifierId TEXT PRIMARY KEY NOT NULL,
    ModifierType TEXT NOT NULL,
    BuildingType TEXT,
    YieldType TEXT NOT NULL,
    Amount REAL NOT NULL
);

INSERT INTO CSC_MaterialLeafProjection
SELECT DISTINCT b.ChildModifierId,
    CASE WHEN y.Recipient = 'PRODUCER' THEN 'MODIFIER_BUILDING_YIELD_CHANGE'
        ELSE 'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS' END,
    CASE WHEN y.Recipient = 'PRODUCER' THEN t.ProducerBuildingType END,
    y.YieldType, y.Amount
FROM CSC_MaterialTransactions t
JOIN CSC_MaterialTransactionYields y USING (TransactionId)
JOIN CSC_MaterialTransactionBindings b USING (TransactionId, LegKey);

-- Café Food is shared with a local fixed exchange. Check the combined meaning
-- before either processor writes native arguments; never let load order silently
-- select one of two conflicting amounts, recipients or yield types.
CREATE TEMP TABLE CSC_MaterialConsistency (Valid INTEGER NOT NULL CHECK (Valid = 1));
-- An incomplete declaration must fail instead of leaving an old native payment
-- running while the model loses its corresponding leg. Gate roles form one of
-- the supported positive AND templates; arbitrary condition graphs need review.
INSERT INTO CSC_MaterialConsistency
SELECT CASE WHEN EXISTS (
    SELECT 1 FROM CSC_MaterialTransactionYields y
    LEFT JOIN CSC_MaterialTransactionBindings b USING (TransactionId, LegKey)
    WHERE b.RootModifierId IS NULL OR b.RootModifierId = b.ChildModifierId
        OR (y.Recipient = 'PRODUCER' AND b.OwnerRequirementSetId IS NULL)
        OR (y.Recipient = 'IMPROVEMENT' AND b.OwnerRequirementSetId IS NOT NULL)
        OR (SELECT COUNT(*) FROM CSC_MaterialTransactionGateBindings g
            WHERE g.TransactionId = y.TransactionId AND g.LegKey = y.LegKey)
            <> CASE WHEN y.Recipient = 'IMPROVEMENT' AND y.ImprovementScope = 'ANY_PLAYER_IMPROVEMENT' THEN 2 ELSE 3 END
) THEN 0 ELSE 1 END;
INSERT INTO CSC_MaterialConsistency
SELECT CASE WHEN EXISTS (
    SELECT 1 FROM CSC_MaterialTransactionGateBindings g
    JOIN CSC_MaterialTransactionBindings b USING (TransactionId, LegKey)
    JOIN CSC_MaterialTransactionYields y USING (TransactionId, LegKey)
    WHERE (g.GateRole = 'MATERIAL_TAG' AND g.RequirementSetId <>
        CASE WHEN y.Recipient = 'PRODUCER' THEN b.OwnerRequirementSetId ELSE b.SubjectRequirementSetId END)
        OR (g.GateRole <> 'MATERIAL_TAG' AND g.RequirementSetId <> b.SubjectRequirementSetId)
        OR (g.GateRole = 'QUARTER_TYPE' AND y.Recipient <> 'PRODUCER')
        OR (g.GateRole = 'IMPROVEMENT_TYPE' AND (y.Recipient <> 'IMPROVEMENT' OR y.ImprovementScope <> 'EXACT_IMPROVEMENT'))
) THEN 0 ELSE 1 END;
INSERT INTO CSC_MaterialConsistency
SELECT CASE WHEN EXISTS (
    SELECT 1 FROM CSC_MaterialTransactionBindings b
    JOIN CSC_MaterialTransactionYields y USING (TransactionId, LegKey)
    WHERE (SELECT COUNT(DISTINCT g.GateRole) FROM CSC_MaterialTransactionGateBindings g
        WHERE g.TransactionId = b.TransactionId AND g.LegKey = b.LegKey)
        <> CASE WHEN y.Recipient = 'IMPROVEMENT' AND y.ImprovementScope = 'ANY_PLAYER_IMPROVEMENT' THEN 2 ELSE 3 END
) THEN 0 ELSE 1 END;
-- Exact input hosts and existing return owners are native identity bindings.
-- Reject unsupported identity migrations rather than silently retaining old
-- attachments alongside a newly advertised host/producer. Ordinary host growth
-- remains additive through the late valid-resource reconciliation.
INSERT INTO CSC_MaterialConsistency
SELECT CASE WHEN EXISTS (
    SELECT 1 FROM CSC_MaterialTransactionYields y
    JOIN CSC_MaterialTransactionBindings b USING (TransactionId, LegKey)
    JOIN ImprovementModifiers i ON i.ModifierId = b.RootModifierId
    WHERE y.Recipient = 'PRODUCER' AND y.ImprovementScope = 'EXACT_IMPROVEMENT'
        AND i.ImprovementType <> y.ImprovementType
) OR EXISTS (
    SELECT 1 FROM BuildingModifiers bm
    WHERE bm.ModifierId IN (SELECT b.RootModifierId FROM CSC_MaterialTransactionBindings b
        JOIN CSC_MaterialTransactionYields y USING (TransactionId, LegKey) WHERE y.Recipient = 'IMPROVEMENT')
        AND NOT EXISTS (SELECT 1 FROM CSC_MaterialTransactions t
            JOIN CSC_MaterialTransactionBindings b USING (TransactionId)
            WHERE b.RootModifierId = bm.ModifierId AND t.ProducerBuildingType = bm.BuildingType)
) THEN 0 ELSE 1 END;
INSERT INTO CSC_MaterialConsistency
SELECT CASE WHEN EXISTS (
    SELECT 1 FROM CSC_MaterialLeafProjection m
    JOIN CSC_BuildingTransactionFixedBindings b ON b.ChildModifierId = m.ModifierId
    JOIN CSC_BuildingTransactions t USING (TransactionId)
    JOIN CSC_BuildingTransactionYields y USING (TransactionId, LegKey)
    WHERE m.Amount <> t.QuantityAmount * y.AmountPerUnit OR m.YieldType <> y.YieldType
        OR m.ModifierType <> 'MODIFIER_BUILDING_YIELD_CHANGE'
        OR m.BuildingType <> CASE WHEN y.Recipient = 'SOURCE' THEN t.SourceBuildingType ELSE t.PartnerBuildingType END
) THEN 0 ELSE 1 END;

CREATE TEMP TABLE CSC_MaterialGateProjection (
    RequirementId TEXT PRIMARY KEY NOT NULL,
    RequirementType TEXT NOT NULL,
    ArgumentName TEXT,
    ArgumentValue TEXT
);
INSERT INTO CSC_MaterialGateProjection
SELECT DISTINCT g.RequirementId,
    CASE g.GateRole
        WHEN 'MATERIAL_TAG' THEN 'REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES'
        WHEN 'QUARTER_TYPE' THEN 'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES'
        WHEN 'ADJACENCY' THEN 'REQUIREMENT_PLOT_ADJACENT_TO_OWNER'
        WHEN 'IMPROVEMENT_TYPE' THEN 'REQUIREMENT_PLOT_IMPROVEMENT_TYPE_MATCHES' END,
    CASE g.GateRole WHEN 'MATERIAL_TAG' THEN 'Tag' WHEN 'QUARTER_TYPE' THEN 'DistrictType'
        WHEN 'IMPROVEMENT_TYPE' THEN 'ImprovementType' END,
    CASE g.GateRole WHEN 'MATERIAL_TAG' THEN t.MaterialClass
        WHEN 'QUARTER_TYPE' THEN 'DISTRICT_CSC_' || t.QuarterKey || '_QUARTER'
        WHEN 'IMPROVEMENT_TYPE' THEN y.ImprovementType END
FROM CSC_MaterialTransactions t
JOIN CSC_MaterialTransactionYields y USING (TransactionId)
JOIN CSC_MaterialTransactionGateBindings g USING (TransactionId, LegKey);

-- Stable identities preserve unrelated Service memberships and native flags.
INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT RequirementId, RequirementType FROM CSC_MaterialGateProjection;
UPDATE Requirements SET RequirementType = (
    SELECT p.RequirementType FROM CSC_MaterialGateProjection p WHERE p.RequirementId = Requirements.RequirementId
) WHERE RequirementId IN (SELECT RequirementId FROM CSC_MaterialGateProjection);
UPDATE Requirements SET Inverse = 0
WHERE RequirementId IN (SELECT RequirementId FROM CSC_MaterialGateProjection);
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT DISTINCT RequirementSetId, 'REQUIREMENTSET_TEST_ALL' FROM CSC_MaterialTransactionGateBindings;
UPDATE RequirementSets SET RequirementSetType = 'REQUIREMENTSET_TEST_ALL'
WHERE RequirementSetId IN (SELECT RequirementSetId FROM CSC_MaterialTransactionGateBindings);
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT DISTINCT RequirementSetId, RequirementId FROM CSC_MaterialTransactionGateBindings;
-- Preserve unrelated sets using shared requirement identities. An unexpected
-- member inside a bound finite set requires an explicit compatibility decision.
INSERT INTO CSC_MaterialConsistency
SELECT CASE WHEN EXISTS (
    SELECT 1 FROM RequirementSetRequirements r
    WHERE r.RequirementSetId IN (SELECT RequirementSetId FROM CSC_MaterialTransactionGateBindings)
        AND NOT EXISTS (SELECT 1 FROM CSC_MaterialTransactionGateBindings g
            WHERE g.RequirementSetId = r.RequirementSetId AND g.RequirementId = r.RequirementId)
) THEN 0 ELSE 1 END;
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT RequirementId, ArgumentName, ArgumentValue FROM CSC_MaterialGateProjection WHERE ArgumentName IS NOT NULL;
UPDATE RequirementArguments SET Value = (
    SELECT p.ArgumentValue FROM CSC_MaterialGateProjection p
    WHERE p.RequirementId = RequirementArguments.RequirementId AND p.ArgumentName = RequirementArguments.Name
) WHERE EXISTS (
    SELECT 1 FROM CSC_MaterialGateProjection p
    WHERE p.RequirementId = RequirementArguments.RequirementId AND p.ArgumentName = RequirementArguments.Name
);

CREATE TEMP TABLE CSC_MaterialRootProjection (
    ModifierId TEXT PRIMARY KEY NOT NULL,
    ModifierType TEXT NOT NULL,
    OwnerRequirementSetId TEXT,
    SubjectRequirementSetId TEXT NOT NULL,
    ChildModifierId TEXT NOT NULL
);
INSERT INTO CSC_MaterialRootProjection
SELECT DISTINCT b.RootModifierId,
    CASE WHEN y.Recipient = 'PRODUCER' THEN 'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER'
        ELSE 'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER' END,
    b.OwnerRequirementSetId, b.SubjectRequirementSetId, b.ChildModifierId
FROM CSC_MaterialTransactionBindings b JOIN CSC_MaterialTransactionYields y USING (TransactionId, LegKey);
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT ModifierId, ModifierType, OwnerRequirementSetId, SubjectRequirementSetId FROM CSC_MaterialRootProjection;
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType   )
SELECT ModifierId, ModifierType FROM CSC_MaterialLeafProjection;
UPDATE Modifiers SET ModifierType = (
    SELECT p.ModifierType FROM CSC_MaterialRootProjection p WHERE p.ModifierId = Modifiers.ModifierId
), OwnerRequirementSetId = (
    SELECT p.OwnerRequirementSetId FROM CSC_MaterialRootProjection p WHERE p.ModifierId = Modifiers.ModifierId
), SubjectRequirementSetId = (
    SELECT p.SubjectRequirementSetId FROM CSC_MaterialRootProjection p WHERE p.ModifierId = Modifiers.ModifierId
) WHERE ModifierId IN (SELECT ModifierId FROM CSC_MaterialRootProjection);
UPDATE Modifiers SET ModifierType = (
    SELECT p.ModifierType FROM CSC_MaterialLeafProjection p WHERE p.ModifierId = Modifiers.ModifierId
), OwnerRequirementSetId = NULL, SubjectRequirementSetId = NULL
WHERE ModifierId IN (SELECT ModifierId FROM CSC_MaterialLeafProjection);

CREATE TEMP TABLE CSC_MaterialArgumentProjection (
    ModifierId TEXT NOT NULL,
    Name TEXT NOT NULL,
    Value TEXT NOT NULL,
    PRIMARY KEY (ModifierId, Name)
);
INSERT INTO CSC_MaterialArgumentProjection
SELECT ModifierId, 'ModifierId', ChildModifierId FROM CSC_MaterialRootProjection
UNION ALL SELECT ModifierId, 'YieldType', YieldType FROM CSC_MaterialLeafProjection
UNION ALL SELECT ModifierId, 'Amount', CAST(CAST(Amount AS INTEGER) AS TEXT) FROM CSC_MaterialLeafProjection
UNION ALL SELECT ModifierId, 'BuildingType', BuildingType FROM CSC_MaterialLeafProjection WHERE BuildingType IS NOT NULL;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT ModifierId, Name, Value FROM CSC_MaterialArgumentProjection;
UPDATE ModifierArguments SET Value = (
    SELECT p.Value FROM CSC_MaterialArgumentProjection p
    WHERE p.ModifierId = ModifierArguments.ModifierId AND p.Name = ModifierArguments.Name
) WHERE EXISTS (
    SELECT 1 FROM CSC_MaterialArgumentProjection p
    WHERE p.ModifierId = ModifierArguments.ModifierId AND p.Name = ModifierArguments.Name
);

-- Building-owned returns stack by producer/material relationship; shared aliases
-- attach once. Inputs keep their registered native hosts, including valid legacy
-- host types whose pairing is not in Improvement_ValidResources.
INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,   ModifierId   )
SELECT DISTINCT t.ProducerBuildingType, b.RootModifierId
FROM CSC_MaterialTransactions t JOIN CSC_MaterialTransactionYields y USING (TransactionId)
JOIN CSC_MaterialTransactionBindings b USING (TransactionId, LegKey)
WHERE y.Recipient = 'IMPROVEMENT';

DROP TABLE CSC_MaterialArgumentProjection;
DROP TABLE CSC_MaterialRootProjection;
DROP TABLE CSC_MaterialGateProjection;
DROP TABLE CSC_MaterialConsistency;
DROP TABLE CSC_MaterialLeafProjection;
