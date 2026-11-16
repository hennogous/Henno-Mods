-- Read-only projection of native route payouts and supply gates. Run after all
-- Quarter/Gold declarations. These writes affect CSC metadata only: the already
-- QAed native modifiers, attachments and requirements remain byte-for-byte rows.
-- Reject an unrecognised template instead of inventing an approximate route.
CREATE TEMP TABLE CSC_TradeReadChecks (Valid INTEGER NOT NULL CHECK (Valid = 1));
-- These are finite native interfaces, not names from which to infer arbitrary
-- effects. A compatibility change to their scope/effect/lifecycle needs an
-- explicit model extension before its read-model can be used.
CREATE TEMP TABLE CSC_TradeReadRoles (ModifierType TEXT PRIMARY KEY, CollectionType TEXT, EffectType TEXT);
INSERT INTO CSC_TradeReadRoles VALUES
    ('MODIFIER_SINGLE_CITY_ADJUST_PROPERTY', 'COLLECTION_OWNER', 'EFFECT_ADJUST_CITY_PROPERTY'),
    ('MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE', 'COLLECTION_OWNER', 'EFFECT_ADJUST_CITY_YIELD_CHANGE'),
    ('MODIFIER_BUILDING_YIELD_CHANGE', 'COLLECTION_OWNER', 'EFFECT_ADJUST_BUILDING_YIELD_CHANGE'),
    ('MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY', 'COLLECTION_OWNER', 'EFFECT_ADJUST_DISTRICT_EXTRA_ENTERTAINMENT');
INSERT INTO CSC_TradeReadChecks
SELECT NOT EXISTS (
    SELECT 1 FROM CSC_TradeReadRoles R LEFT JOIN DynamicModifiers D USING (ModifierType)
    WHERE D.ModifierType IS NULL OR D.CollectionType <> R.CollectionType OR D.EffectType <> R.EffectType
);
CREATE TEMP TABLE CSC_TradeReadBits (Bit INTEGER PRIMARY KEY);
INSERT INTO CSC_TradeReadBits VALUES (1);
INSERT INTO CSC_TradeReadBits SELECT Bit FROM CSC_RouteStackBits;
INSERT INTO CSC_TradeReadChecks
SELECT COUNT(*) = 5 AND MIN(Bit) = 1 AND MAX(Bit) = 16 FROM CSC_TradeReadBits;

DELETE FROM CSC_TradeRoutePayouts;
DELETE FROM CSC_TradeRouteChannelFacts;
DELETE FROM CSC_TradeRouteSupplyRequirements;

INSERT INTO CSC_TradeRouteChannelFacts
        (   ChannelId,   SupplyProperty,   OriginDistrictType,   ProducerStage   )
SELECT C.ChannelId, A.Value, B.PrereqDistrict, F.Stage
FROM CSC_TradeRouteChannels C
JOIN Buildings B ON B.BuildingType = C.ProducerBuildingType
JOIN CSC_QuarterFlowBuildings F
    ON F.QuarterKey = C.QuarterKey AND F.BuildingType = C.ProducerBuildingType
JOIN Modifiers M ON M.ModifierId = C.SupplyModifierId
    AND M.ModifierType = 'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY'
    AND M.SubjectRequirementSetId IS NULL
    AND M.RunOnce = 0 AND M.Permanent = 0 AND M.NewOnly = 0 AND COALESCE(M.Repeatable, 0) = 0
    AND M.OwnerStackLimit IS NULL AND M.SubjectStackLimit IS NULL
JOIN BuildingModifiers BM ON BM.BuildingType = C.ProducerBuildingType AND BM.ModifierId = M.ModifierId
JOIN ModifierArguments A ON A.ModifierId = M.ModifierId AND A.Name = 'Key'
JOIN ModifierArguments V ON V.ModifierId = M.ModifierId AND V.Name = 'Amount'
WHERE CAST(V.Value AS REAL) > 0 AND TRIM(A.Value) <> '';
INSERT INTO CSC_TradeReadChecks
SELECT (SELECT COUNT(*) FROM CSC_TradeRouteChannelFacts) = COUNT(*) FROM CSC_TradeRouteChannels;

-- Supported supplied-property template: AND of improvement-count requirements.
-- Each collection is owned improvements, filtered by adjacency to its owner
-- and one gameplay material tag. It has no worker, legal-input-host, civic or
-- functioning-Quarter gate. Keep the actual count/tag, not a Base/Spec default.
CREATE TEMP VIEW CSC_TradeReadSupply AS
SELECT C.ChannelId, R.RequirementId, N.Value AS MinimumCount,
       S.RequirementSetId AS FilterSet, T.Value AS MaterialClass
FROM CSC_TradeRouteChannels C
JOIN Modifiers M ON M.ModifierId = C.SupplyModifierId
JOIN RequirementSets O ON O.RequirementSetId = M.OwnerRequirementSetId
    AND O.RequirementSetType = 'REQUIREMENTSET_TEST_ALL'
JOIN RequirementSetRequirements L ON L.RequirementSetId = O.RequirementSetId
JOIN Requirements R ON R.RequirementId = L.RequirementId
    AND R.RequirementType = 'REQUIREMENT_COLLECTION_COUNT_ATLEAST' AND R.Inverse = 0
JOIN RequirementArguments K ON K.RequirementId = R.RequirementId
    AND K.Name = 'CollectionType' AND K.Value = 'COLLECTION_PLAYER_IMPROVEMENTS'
JOIN RequirementArguments N ON N.RequirementId = R.RequirementId AND N.Name = 'Count'
JOIN RequirementArguments I ON I.RequirementId = R.RequirementId AND I.Name = 'RequirementSetId'
JOIN RequirementSets S ON S.RequirementSetId = I.Value AND S.RequirementSetType = 'REQUIREMENTSET_TEST_ALL'
JOIN RequirementSetRequirements F ON F.RequirementSetId = S.RequirementSetId
JOIN Requirements Q ON Q.RequirementId = F.RequirementId
    AND Q.RequirementType = 'REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES' AND Q.Inverse = 0
JOIN RequirementArguments T ON T.RequirementId = Q.RequirementId AND T.Name = 'Tag'
WHERE CAST(N.Value AS INTEGER) = N.Value AND CAST(N.Value AS INTEGER) > 0
    AND (SELECT COUNT(*) FROM RequirementArguments A WHERE A.RequirementId = R.RequirementId) = 3
    AND (SELECT COUNT(*) FROM RequirementArguments A WHERE A.RequirementId = Q.RequirementId) = 1
    AND (SELECT COUNT(*) FROM RequirementSetRequirements A WHERE A.RequirementSetId = S.RequirementSetId) = 2
    AND EXISTS (
        SELECT 1 FROM RequirementSetRequirements A JOIN Requirements B USING (RequirementId)
        WHERE A.RequirementSetId = S.RequirementSetId
            AND B.RequirementType = 'REQUIREMENT_PLOT_ADJACENT_TO_OWNER' AND B.Inverse = 0
            AND NOT EXISTS (SELECT 1 FROM RequirementArguments X WHERE X.RequirementId = B.RequirementId)
    );
INSERT INTO CSC_TradeRouteSupplyRequirements
        (   ChannelId,   RequirementId,   MaterialClass,   MinimumCount   )
SELECT ChannelId, RequirementId, MaterialClass, CAST(MinimumCount AS INTEGER) FROM CSC_TradeReadSupply;
INSERT INTO CSC_TradeReadChecks
SELECT NOT EXISTS (
    SELECT 1 FROM CSC_TradeRouteChannels C JOIN Modifiers M ON M.ModifierId = C.SupplyModifierId
    WHERE (SELECT COUNT(*) FROM CSC_TradeRouteSupplyRequirements R WHERE R.ChannelId = C.ChannelId) = 0
        OR (SELECT COUNT(*) FROM CSC_TradeRouteSupplyRequirements R WHERE R.ChannelId = C.ChannelId)
            <> (SELECT COUNT(*) FROM RequirementSetRequirements S WHERE S.RequirementSetId = M.OwnerRequirementSetId)
);

-- Bit1 is the unsuffixed native modifier; the four companions carry their own
-- real amounts. Reading all five preserves compatibility edits to an individual
-- bit and the receiver's existing modulo32 encoding; no clamp is introduced.
CREATE TEMP VIEW CSC_TradeReadPayouts AS
SELECT B.ChannelId, B.LegKey, B.Recipient, X.Bit,
       CASE WHEN X.Bit = 1 THEN B.ModifierId ELSE B.ModifierId || '_BIT_' || X.Bit END AS ModifierId,
       CASE WHEN M.ModifierType = 'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY'
            THEN 'AMENITY' ELSE Y.Value END AS YieldType,
       A.Value AS RawAmount, H.Value AS BuildingType,
       CASE WHEN B.Recipient = 'ORIGIN' THEN C.ImportProperty ELSE C.ExportProperty END || '_BIT_' || X.Bit AS BitProperty,
       M.ModifierType, M.OwnerRequirementSetId, M.SubjectRequirementSetId
FROM CSC_TradeRoutePayoutBindings B
JOIN CSC_TradeRouteChannels C USING (ChannelId)
CROSS JOIN CSC_TradeReadBits X
LEFT JOIN Modifiers M ON M.ModifierId = CASE WHEN X.Bit = 1 THEN B.ModifierId ELSE B.ModifierId || '_BIT_' || X.Bit END
    AND M.RunOnce = 0 AND M.Permanent = 0 AND M.NewOnly = 0 AND COALESCE(M.Repeatable, 0) = 0
    AND M.OwnerStackLimit IS NULL AND M.SubjectStackLimit IS NULL
LEFT JOIN ModifierArguments A ON A.ModifierId = M.ModifierId AND A.Name = 'Amount'
LEFT JOIN ModifierArguments Y ON Y.ModifierId = M.ModifierId AND Y.Name = 'YieldType'
LEFT JOIN ModifierArguments H ON H.ModifierId = M.ModifierId AND H.Name = 'BuildingType';

INSERT INTO CSC_TradeReadChecks
SELECT NOT EXISTS (
    SELECT 1 FROM CSC_TradeReadPayouts P JOIN CSC_TradeRouteChannels C USING (ChannelId)
    WHERE P.RawAmount IS NULL OR CAST(P.RawAmount AS REAL) <> P.RawAmount
        OR P.YieldType IS NULL OR P.OwnerRequirementSetId IS NOT NULL
        OR NOT EXISTS (SELECT 1 FROM DistrictModifiers D WHERE D.DistrictType = 'DISTRICT_CITY_CENTER' AND D.ModifierId = P.ModifierId)
        OR (P.Recipient = 'ORIGIN' AND (P.ModifierType NOT IN ('MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE', 'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY') OR P.BuildingType IS NOT NULL))
        OR (P.Recipient = 'DESTINATION' AND (P.ModifierType <> 'MODIFIER_BUILDING_YIELD_CHANGE' OR P.BuildingType IS NULL OR P.BuildingType <> C.ProducerBuildingType))
        OR NOT EXISTS (
            SELECT 1 FROM RequirementSets S
            JOIN RequirementSetRequirements L USING (RequirementSetId)
            JOIN Requirements R USING (RequirementId)
            JOIN RequirementArguments N ON N.RequirementId = R.RequirementId AND N.Name = 'PropertyName'
            JOIN RequirementArguments V ON V.RequirementId = R.RequirementId AND V.Name = 'PropertyMinimum'
            WHERE S.RequirementSetId = P.SubjectRequirementSetId AND S.RequirementSetType = 'REQUIREMENTSET_TEST_ALL'
                AND R.RequirementType = 'REQUIREMENT_PLOT_PROPERTY_MATCHES' AND R.Inverse = 0
                AND N.Value = P.BitProperty AND CAST(V.Value AS REAL) = 1
                AND (SELECT COUNT(*) FROM RequirementSetRequirements X WHERE X.RequirementSetId = S.RequirementSetId) = 1
                AND (SELECT COUNT(*) FROM RequirementArguments X WHERE X.RequirementId = R.RequirementId) = 2
        )
);
INSERT INTO CSC_TradeRoutePayouts
    (
        ChannelId,
        LegKey,
        Recipient,
        Bit,
        ModifierId,
        YieldType,
        Amount,
        BuildingType
    )
SELECT
        ChannelId,
        LegKey,
        Recipient,
        Bit,
        ModifierId,
        YieldType,
        CAST(RawAmount AS REAL),
        BuildingType
FROM CSC_TradeReadPayouts;
INSERT INTO CSC_TradeReadChecks
SELECT COUNT(*) = (SELECT COUNT(*) * 5 FROM CSC_TradeRoutePayoutBindings) FROM CSC_TradeRoutePayouts;

DROP VIEW CSC_TradeReadPayouts;
DROP VIEW CSC_TradeReadSupply;
DROP TABLE CSC_TradeReadBits;
DROP TABLE CSC_TradeReadRoles;
DROP TABLE CSC_TradeReadChecks;
