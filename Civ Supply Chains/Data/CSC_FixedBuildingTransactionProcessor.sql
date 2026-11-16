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
