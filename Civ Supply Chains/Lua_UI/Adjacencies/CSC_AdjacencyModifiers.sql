-- Compile declarative CSC rules to plot-property-gated modifiers.
-- Generic rules keep the signed ten-bit encoding. Local Mill rules explicitly
-- use bounded +1 thresholds, so they never contain large encoding weights.
INSERT OR IGNORE INTO CSC_AdjacencyRules
    (
        ID,
        DistrictType,
        ProvideType,
        YieldType,
        CustomArgumentValue,
        YieldChange,
        AdjacencyType,
        CustomAdjacentObject,
        Rings,
        MinRings,
        MaxRings,
        MustOwn,
        DistrictModifiers,
        NewMethod,
        ApplyForUniqueDistricts,
        TraitType,
        ModifierOwner,
        WhoIsTheOwner,
        CollectionType,
        Only,
        FreeCompose
    )
SELECT
        D.CivUniqueDistrictType || '_' || R.ID,
        D.CivUniqueDistrictType,
        R.ProvideType,
        R.YieldType,
        R.CustomArgumentValue,
        R.YieldChange,
        R.AdjacencyType,
        R.CustomAdjacentObject,
        R.Rings,
        R.MinRings,
        R.MaxRings,
        R.MustOwn,
        R.DistrictModifiers,
        R.NewMethod,
        0,
        U.TraitType,
        R.ModifierOwner,
        R.WhoIsTheOwner,
        R.CollectionType,
        R.Only,
        R.FreeCompose
FROM CSC_AdjacencyRules R JOIN DistrictReplaces D ON D.ReplacesDistrictType=R.DistrictType
JOIN Districts U ON U.DistrictType=D.CivUniqueDistrictType
WHERE R.ApplyForUniqueDistricts=1 AND R.TraitType IS NULL;

UPDATE CSC_AdjacencyRules SET Rings=MinRings WHERE Rings>0 AND Rings<MinRings;
UPDATE CSC_AdjacencyRules SET MaxRings=MinRings WHERE MaxRings>0 AND MaxRings<MinRings;

INSERT OR IGNORE INTO Types
        (   Type,   Kind   )
SELECT 'MODIFIER_CSC_ADJ_' || P.ProvideType, 'KIND_MODIFIER'
FROM CSC_AdjacencyProviders P WHERE EXISTS (SELECT 1 FROM Types WHERE Type=P.EffectType);
INSERT OR IGNORE INTO DynamicModifiers
        (   ModifierType,   CollectionType,   EffectType   )
SELECT 'MODIFIER_CSC_ADJ_' || P.ProvideType,P.CollectionType,P.EffectType
FROM CSC_AdjacencyProviders P WHERE EXISTS (SELECT 1 FROM Types WHERE Type=P.EffectType);

INSERT OR IGNORE INTO Types
        (   Type,                               Kind   )
VALUES  (   'MODIFIER_CSC_ADJ_ATTACH_CITY',     'KIND_MODIFIER'   ),
        (   'MODIFIER_CSC_ADJ_ATTACH_PLAYER',   'KIND_MODIFIER'   ),
        (   'MODIFIER_CSC_ADJ_ATTACH_ALL',      'KIND_MODIFIER'   );
INSERT OR IGNORE INTO DynamicModifiers
        (   ModifierType,                       CollectionType,                  EffectType   )
VALUES  (   'MODIFIER_CSC_ADJ_ATTACH_CITY',     'COLLECTION_CITY_DISTRICTS',     'EFFECT_ATTACH_MODIFIER'   ),
        (   'MODIFIER_CSC_ADJ_ATTACH_PLAYER',   'COLLECTION_PLAYER_DISTRICTS',   'EFFECT_ATTACH_MODIFIER'   ),
        (   'MODIFIER_CSC_ADJ_ATTACH_ALL',      'COLLECTION_ALL_DISTRICTS',      'EFFECT_ATTACH_MODIFIER'   );

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,            RequirementSetType   )
VALUES  (   'REQSET_CSC_ADJ_NEIGHBOR',   'REQUIREMENTSET_TEST_ALL'   );
INSERT OR IGNORE INTO Requirements
        (   RequirementId,            RequirementType   )
VALUES  (   'REQ_CSC_ADJ_NEIGHBOR',   'REQUIREMENT_PLOT_ADJACENT_TO_OWNER'   );
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,            RequirementId   )
VALUES  (   'REQSET_CSC_ADJ_NEIGHBOR',   'REQ_CSC_ADJ_NEIGHBOR'   );
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,            Name,            Value   )
VALUES  (   'REQ_CSC_ADJ_NEIGHBOR',   'MaxDistance',   1   );

-- Fail an unsupported step declaration rather than dropping it or silently
-- assigning an arbitrary range. Current contracts are exactly the one-city,
-- building-owned hills predicate and half-per-edge river count.
CREATE TEMP TABLE CSC_AdjacencyUnitStepValidation (
    Valid INTEGER NOT NULL CHECK (Valid = 1)
);
INSERT INTO CSC_AdjacencyUnitStepValidation
        (   Valid   )
SELECT CASE WHEN R.ID IS NOT NULL
    AND R.ProvideType = 'SelfBonus' AND R.FreeCompose = 0
    AND R.ModifierOwner = 'BuildingModifiers' AND R.CollectionType = 'COLLECTION_CITY_DISTRICTS'
    AND B.PrereqDistrict = R.DistrictType AND D.OnePerCity = 1
    AND (
        (R.AdjacencyType = 'FROM_RINGS_CAO_TERRAIN_SETS' AND R.CustomAdjacentObject = 'IsHills'
            AND R.Rings = 0 AND R.MinRings = 0 AND COALESCE(R.MaxRings, 0) = 0
            AND R.YieldChange = 1 AND S.MaxAmount = 1)
        OR
        (R.AdjacencyType = 'FROM_RIVER_CROSSING' AND R.YieldChange = 0.5 AND S.MaxAmount = 3)
    ) THEN 1 ELSE 0 END
FROM CSC_AdjacencyUnitSteps AS S
LEFT JOIN CSC_AdjacencyRules AS R ON R.ID = S.ID
LEFT JOIN Buildings AS B ON B.BuildingType = R.WhoIsTheOwner
LEFT JOIN Districts AS D ON D.DistrictType = R.DistrictType;
DROP TABLE CSC_AdjacencyUnitStepValidation;

-- Reprocessing an old rules cache must retire only the two configured rules'
-- numeric-bit building attachments. Their unused definitions may remain, but
-- they no longer enter the building's modifier vector. Saved plot bit flags
-- are separately cleared by the Lua writer when each site is reconciled.
DELETE FROM BuildingModifiers
WHERE EXISTS (
    SELECT 1
    FROM CSC_AdjacencyUnitSteps AS S
    JOIN CSC_AdjacencyRules AS R ON R.ID = S.ID
    CROSS JOIN CSC_AdjacencyBits AS B
    WHERE BuildingModifiers.BuildingType = R.WhoIsTheOwner
        AND BuildingModifiers.ModifierId = 'ATTACH_MOD_CSC_ADJ_' || R.ID || '_' || B.Bit
);

CREATE TEMP TABLE CSC_AdjacencyCompile AS
WITH RECURSIVE UnitSteps (Step) AS (
    SELECT 1
    UNION ALL
    SELECT Step + 1 FROM UnitSteps
    WHERE Step < (SELECT MAX(MaxAmount) FROM CSC_AdjacencyUnitSteps)
), Encodings AS (
    -- Retain the old numeric IDs as disconnected compatibility definitions,
    -- including on a fresh database. An older save can still name those IDs.
    SELECT R.*,B.Bit,CAST(B.Bit AS TEXT) AS KeySuffix,
        CASE WHEN EXISTS (SELECT 1 FROM CSC_AdjacencyUnitSteps AS S WHERE S.ID = R.ID)
            THEN 0 ELSE 1 END AS ActiveAttachment
    FROM CSC_AdjacencyRules AS R CROSS JOIN CSC_AdjacencyBits AS B
    WHERE R.FreeCompose = 0
    UNION ALL
    SELECT R.*,1 AS Bit,'STEP_' || U.Step AS KeySuffix,1 AS ActiveAttachment
    FROM CSC_AdjacencyRules AS R
    JOIN CSC_AdjacencyUnitSteps AS S ON S.ID = R.ID
    JOIN UnitSteps AS U ON U.Step <= S.MaxAmount
    WHERE R.FreeCompose = 0
)
SELECT E.*,'MOD_CSC_ADJ_' || E.ID || '_' || E.KeySuffix AS ModifierId,
    'REQSET_CSC_ADJ_' || E.ID || '_' || E.KeySuffix AS RequirementSetId,
    'REQ_CSC_ADJ_' || E.ID || '_' || E.KeySuffix AS RequirementId
FROM Encodings AS E;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT RequirementSetId,'REQUIREMENTSET_TEST_ALL' FROM CSC_AdjacencyCompile;
INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT RequirementId,'REQUIREMENT_PLOT_PROPERTY_MATCHES' FROM CSC_AdjacencyCompile;
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT RequirementSetId,RequirementId FROM CSC_AdjacencyCompile;
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT RequirementId,'PropertyName','CSC_ADJ_' || ID || '_' || KeySuffix FROM CSC_AdjacencyCompile
UNION ALL SELECT RequirementId,'PropertyMinimum',1 FROM CSC_AdjacencyCompile;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT C.ModifierId,D.ModifierType,C.RequirementSetId,
    CASE WHEN C.ProvideType='ProvideToADJ' THEN 'REQSET_CSC_ADJ_NEIGHBOR' END
FROM CSC_AdjacencyCompile C JOIN DynamicModifiers D ON D.ModifierType='MODIFIER_CSC_ADJ_' || C.ProvideType;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT ModifierId,'Amount',CASE WHEN YieldChange<0 THEN -Bit ELSE Bit END FROM CSC_AdjacencyCompile
UNION ALL SELECT ModifierId,'YieldType',YieldType FROM CSC_AdjacencyCompile;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT C.ModifierId,P.ArgumentName,
    CASE WHEN P.ArgumentName='SourceType' THEN 'FREE_POWER_SOURCE_MISC'
         WHEN P.ArgumentName IN ('Key','ResourceType','GreatPersonClassType') THEN C.YieldType
         ELSE C.CustomArgumentValue END
FROM CSC_AdjacencyCompile C JOIN CSC_AdjacencyProviders P USING (ProvideType)
WHERE P.ArgumentName IS NOT NULL;

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT C.DistrictType,C.ModifierId FROM CSC_AdjacencyCompile C
JOIN Districts D USING (DistrictType) WHERE C.ModifierOwner='DistrictModifiers' AND C.NewMethod=0;

-- Retain the declared collection for generic owners. Local Mill parents use
-- CITY_DISTRICTS; their child property key is written only on Bakers plots.
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType   )
SELECT 'ATTACH_' || ModifierId,
    CASE CollectionType WHEN 'COLLECTION_CITY_DISTRICTS' THEN 'MODIFIER_CSC_ADJ_ATTACH_CITY'
         WHEN 'COLLECTION_ALL_DISTRICTS' THEN 'MODIFIER_CSC_ADJ_ATTACH_ALL'
         ELSE 'MODIFIER_CSC_ADJ_ATTACH_PLAYER' END
FROM CSC_AdjacencyCompile WHERE ModifierOwner<>'DistrictModifiers' OR NewMethod=1;
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'ATTACH_' || ModifierId,'ModifierId',ModifierId FROM CSC_AdjacencyCompile
WHERE ModifierOwner<>'DistrictModifiers' OR NewMethod=1;
INSERT OR IGNORE INTO TraitModifiers
        (   TraitType,   ModifierId   )
SELECT 'TRAIT_LEADER_MAJOR_CIV','ATTACH_' || ModifierId FROM CSC_AdjacencyCompile
WHERE ModifierOwner='DistrictModifiers' AND NewMethod=1
UNION ALL SELECT WhoIsTheOwner,'ATTACH_' || ModifierId FROM CSC_AdjacencyCompile WHERE ModifierOwner='TraitModifiers';
INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,   ModifierId   )
SELECT WhoIsTheOwner,'ATTACH_' || ModifierId FROM CSC_AdjacencyCompile
WHERE ModifierOwner='BuildingModifiers' AND ActiveAttachment=1;
INSERT OR IGNORE INTO PolicyModifiers
        (   PolicyType,   ModifierId   )
SELECT WhoIsTheOwner,'ATTACH_' || ModifierId FROM CSC_AdjacencyCompile WHERE ModifierOwner='PolicyModifiers';
INSERT OR IGNORE INTO TechnologyModifiers
        (   TechnologyType,   ModifierId   )
SELECT WhoIsTheOwner,'ATTACH_' || ModifierId FROM CSC_AdjacencyCompile WHERE ModifierOwner='TechnologyModifiers';
INSERT OR IGNORE INTO CivicModifiers
        (   CivicType,   ModifierId   )
SELECT WhoIsTheOwner,'ATTACH_' || ModifierId FROM CSC_AdjacencyCompile WHERE ModifierOwner='CivicModifiers';
INSERT OR IGNORE INTO GovernmentModifiers
        (   GovernmentType,   ModifierId   )
SELECT WhoIsTheOwner,'ATTACH_' || ModifierId FROM CSC_AdjacencyCompile WHERE ModifierOwner='GovernmentModifiers';
INSERT OR IGNORE INTO BeliefModifiers
        (   BeliefType,   ModifierId   )
SELECT WhoIsTheOwner,'ATTACH_' || ModifierId FROM CSC_AdjacencyCompile WHERE ModifierOwner='BeliefModifiers';
INSERT OR IGNORE INTO GovernorPromotionModifiers
        (   GovernorPromotionType,   ModifierId   )
SELECT WhoIsTheOwner,'ATTACH_' || ModifierId FROM CSC_AdjacencyCompile WHERE ModifierOwner='GovernorPromotionModifiers';
DROP TABLE CSC_AdjacencyCompile;
