-- Shared ordinary-economy compiler: Quarter declarations -> native gameplay
-- modifiers/requirements and derived partner registries. Runs at load2500 after
-- core, Gold, M&C and supported venue declarations. No CE dependency or turn loop.
-- Sections run in dependency order: materials, fixed buildings, population.
-- Native IDs stay stable; INSERT/UPDATE preserves shared Service references.
-- Edit economic terms in Quarter SQL, not in these common implementation rules.

-- ============================================================================
-- Material exchanges
-- ============================================================================

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

-- ============================================================================
-- Fixed building exchanges
-- ============================================================================

-- Fixed native exchanges: gameplay-owned headers/legs -> existing modifiers.
-- This runs before the common transaction processor and has no CE dependency.
-- BuildingModifiers owns activation, a wrapper selects adjacent owned districts,
-- and BUILDING_YIELD_CHANGE pays the receiving building (with native replacement
-- handling). Local effects use the same city scope as the original implementation.
-- A source and partner can own different legs; never infer OwnerSide from Recipient.

CREATE TEMP TABLE CSC_FixedContractCheck (Valid INTEGER CHECK (Valid = 1));
INSERT INTO CSC_FixedContractCheck
        (   Valid   )
SELECT CASE WHEN NOT EXISTS (
    SELECT 1 FROM CSC_BuildingTransactionFixedBindings B
    LEFT JOIN CSC_BuildingTransactions T ON T.TransactionId = B.TransactionId
    LEFT JOIN CSC_BuildingTransactionYields Y ON Y.TransactionId = B.TransactionId AND Y.LegKey = B.LegKey
    WHERE T.TransactionId IS NULL OR Y.LegKey IS NULL OR T.QuantityKind <> 'FIXED'
        OR Y.AmountProperty IS NOT NULL
        OR (T.SpatialRule = 'SAME_CITY') <> (B.RootModifierId = B.ChildModifierId)
) THEN 1 ELSE 0 END;
DROP TABLE CSC_FixedContractCheck;

CREATE TEMP TABLE CSC_FixedNativeRules AS
SELECT T.TransactionId, B.LegKey,
    CASE B.OwnerSide WHEN 'SOURCE' THEN T.SourceBuildingType ELSE T.PartnerBuildingType END AS OwnerBuilding,
    CASE B.OwnerSide WHEN 'SOURCE' THEN T.PartnerBuildingType ELSE T.SourceBuildingType END AS OtherBuilding,
    CASE Y.Recipient WHEN 'SOURCE' THEN T.SourceBuildingType ELSE T.PartnerBuildingType END AS RecipientBuilding,
    B.RootModifierId, B.ChildModifierId, B.SubjectRequirementSetId,
    B.AdjacencyRequirementId, B.DistrictRequirementId, B.BuildingRequirementId,
    Y.YieldType, T.QuantityAmount * Y.AmountPerUnit AS Amount
FROM CSC_BuildingTransactionFixedBindings B
JOIN CSC_BuildingTransactions T ON T.TransactionId = B.TransactionId
JOIN CSC_BuildingTransactionYields Y ON Y.TransactionId = B.TransactionId AND Y.LegKey = B.LegKey;

-- Constrained DISTINCT projections permit identical shared native leaves/gates,
-- but reject conflicting declarations instead of whichever row happens to win.
CREATE TEMP TABLE CSC_FixedNativeModifiers
    (
    ModifierId TEXT PRIMARY KEY,
    ModifierType TEXT NOT NULL,
    SubjectRequirementSetId TEXT
    );
INSERT INTO CSC_FixedNativeModifiers
        (   ModifierId,   ModifierType,   SubjectRequirementSetId   )
SELECT DISTINCT ChildModifierId, 'MODIFIER_BUILDING_YIELD_CHANGE', NULL
FROM CSC_FixedNativeRules;
INSERT INTO CSC_FixedNativeModifiers
        (   ModifierId,   ModifierType,   SubjectRequirementSetId   )
SELECT DISTINCT RootModifierId, 'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER', SubjectRequirementSetId
FROM CSC_FixedNativeRules WHERE RootModifierId <> ChildModifierId;

CREATE TEMP TABLE CSC_FixedNativeArguments
    (
    ModifierId TEXT NOT NULL,
    Name TEXT NOT NULL,
    Value TEXT NOT NULL,
    PRIMARY KEY (ModifierId, Name)
    );
INSERT INTO CSC_FixedNativeArguments
        (   ModifierId,   Name,   Value   )
SELECT DISTINCT ChildModifierId, 'BuildingType', RecipientBuilding FROM CSC_FixedNativeRules;
INSERT INTO CSC_FixedNativeArguments
        (   ModifierId,   Name,   Value   )
SELECT DISTINCT ChildModifierId, 'YieldType', YieldType FROM CSC_FixedNativeRules;
INSERT INTO CSC_FixedNativeArguments
        (   ModifierId,   Name,   Value   )
SELECT DISTINCT ChildModifierId, 'Amount', CAST(Amount AS INTEGER) FROM CSC_FixedNativeRules;
INSERT INTO CSC_FixedNativeArguments
        (   ModifierId,   Name,   Value   )
SELECT DISTINCT RootModifierId, 'ModifierId', ChildModifierId
FROM CSC_FixedNativeRules WHERE RootModifierId <> ChildModifierId;

-- The narrow wrapper template owns adjacency, target district family and the
-- optional functioning-building check. Reverse customer->Quarter wrappers have
-- no explicit target-building check in the original rules. Native leaf semantics
-- remain responsible for the receiving building's payout and replacement family.
CREATE TEMP TABLE CSC_FixedNativeRequirements
    (
    RequirementId TEXT PRIMARY KEY,
    RequirementType TEXT NOT NULL
    );
INSERT INTO CSC_FixedNativeRequirements
        (   RequirementId,   RequirementType   )
SELECT DISTINCT AdjacencyRequirementId, 'REQUIREMENT_PLOT_ADJACENT_TO_OWNER'
FROM CSC_FixedNativeRules WHERE AdjacencyRequirementId IS NOT NULL;
INSERT INTO CSC_FixedNativeRequirements
        (   RequirementId,   RequirementType   )
SELECT DISTINCT DistrictRequirementId, 'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES'
FROM CSC_FixedNativeRules WHERE DistrictRequirementId IS NOT NULL;
INSERT INTO CSC_FixedNativeRequirements
        (   RequirementId,   RequirementType   )
SELECT DISTINCT BuildingRequirementId, 'REQUIREMENT_CITY_HAS_BUILDING'
FROM CSC_FixedNativeRules WHERE BuildingRequirementId IS NOT NULL;
INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT RequirementId, RequirementType, 0 FROM CSC_FixedNativeRequirements;
UPDATE Requirements SET
    RequirementType = (SELECT N.RequirementType FROM CSC_FixedNativeRequirements N WHERE N.RequirementId = Requirements.RequirementId),
    Inverse = 0
WHERE RequirementId IN (SELECT RequirementId FROM CSC_FixedNativeRequirements);

CREATE TEMP TABLE CSC_FixedNativeRequirementArguments
    (
    RequirementId TEXT NOT NULL,
    Name TEXT NOT NULL,
    Value TEXT NOT NULL,
    PRIMARY KEY (RequirementId, Name)
    );
INSERT INTO CSC_FixedNativeRequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT DISTINCT R.DistrictRequirementId, 'DistrictType', B.PrereqDistrict
FROM CSC_FixedNativeRules R JOIN Buildings B ON B.BuildingType = R.OtherBuilding
WHERE R.DistrictRequirementId IS NOT NULL;
INSERT INTO CSC_FixedNativeRequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT DISTINCT BuildingRequirementId, 'BuildingType', OtherBuilding
FROM CSC_FixedNativeRules WHERE BuildingRequirementId IS NOT NULL;
INSERT INTO CSC_FixedNativeRequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT DISTINCT BuildingRequirementId, 'MustBeFunctioning', '1'
FROM CSC_FixedNativeRules WHERE BuildingRequirementId IS NOT NULL;
DELETE FROM RequirementArguments
WHERE RequirementId IN (SELECT RequirementId FROM CSC_FixedNativeRequirements);
INSERT INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT RequirementId, Name, Value FROM CSC_FixedNativeRequirementArguments;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT DISTINCT SubjectRequirementSetId, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_FixedNativeRules WHERE SubjectRequirementSetId IS NOT NULL;
UPDATE RequirementSets SET RequirementSetType = 'REQUIREMENTSET_TEST_ALL'
WHERE RequirementSetId IN (SELECT SubjectRequirementSetId FROM CSC_FixedNativeRules);

DELETE FROM RequirementSetRequirements
WHERE RequirementSetId IN (SELECT SubjectRequirementSetId FROM CSC_FixedNativeRules);
INSERT INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT DISTINCT SubjectRequirementSetId, AdjacencyRequirementId
FROM CSC_FixedNativeRules WHERE AdjacencyRequirementId IS NOT NULL
UNION
SELECT DISTINCT SubjectRequirementSetId, DistrictRequirementId
FROM CSC_FixedNativeRules WHERE DistrictRequirementId IS NOT NULL
UNION
SELECT DISTINCT SubjectRequirementSetId, BuildingRequirementId
FROM CSC_FixedNativeRules WHERE BuildingRequirementId IS NOT NULL;

-- Native parent definitions use INSERT/UPDATE, never REPLACE. Civ's actual
-- foreign keys use ON DELETE CASCADE; replacing a shared Requirement/Set could
-- remove unrelated material/Service modifiers or memberships. Retain row identity
-- and flags, then attach generated effects after their prerequisite rows exist.
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT ModifierId, ModifierType, NULL, SubjectRequirementSetId FROM CSC_FixedNativeModifiers;

UPDATE Modifiers SET
    ModifierType = (SELECT N.ModifierType FROM CSC_FixedNativeModifiers N WHERE N.ModifierId = Modifiers.ModifierId),
    OwnerRequirementSetId = NULL,
    SubjectRequirementSetId = (SELECT N.SubjectRequirementSetId FROM CSC_FixedNativeModifiers N WHERE N.ModifierId = Modifiers.ModifierId)
WHERE ModifierId IN (SELECT ModifierId FROM CSC_FixedNativeModifiers);

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT ModifierId, Name, Value FROM CSC_FixedNativeArguments;
UPDATE ModifierArguments SET Value = (SELECT A.Value FROM CSC_FixedNativeArguments A
    WHERE A.ModifierId = ModifierArguments.ModifierId AND A.Name = ModifierArguments.Name)
WHERE EXISTS (SELECT 1 FROM CSC_FixedNativeArguments A
    WHERE A.ModifierId = ModifierArguments.ModifierId AND A.Name = ModifierArguments.Name);

-- Explicit owner expansion is required for BuildingModifiers. Native target
-- BUILDING_YIELD_CHANGE already inherits direct replacements, so target leaves
-- are never duplicated for uniques. NOT EXISTS also protects fixtures without
-- a unique constraint on native attachment rows.
INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,   ModifierId   )
SELECT DISTINCT R.OwnerBuilding, R.RootModifierId
FROM CSC_FixedNativeRules R
WHERE NOT EXISTS (SELECT 1 FROM BuildingModifiers B
    WHERE B.BuildingType = R.OwnerBuilding AND B.ModifierId = R.RootModifierId);
INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,   ModifierId   )
SELECT DISTINCT U.CivUniqueBuildingType, R.RootModifierId
FROM CSC_FixedNativeRules R
JOIN BuildingReplaces U ON U.ReplacesBuildingType = R.OwnerBuilding
JOIN Buildings B ON B.BuildingType = U.CivUniqueBuildingType
WHERE NOT EXISTS (SELECT 1 FROM BuildingModifiers A
    WHERE A.BuildingType = U.CivUniqueBuildingType AND A.ModifierId = R.RootModifierId);

DROP TABLE CSC_FixedNativeRequirementArguments;
DROP TABLE CSC_FixedNativeRequirements;
DROP TABLE CSC_FixedNativeArguments;
DROP TABLE CSC_FixedNativeModifiers;
DROP TABLE CSC_FixedNativeRules;

-- ============================================================================
-- Population building exchanges
-- ============================================================================

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
-- Stage3 keeps its compatibility registry; fixed and threshold venues share this projection.
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
