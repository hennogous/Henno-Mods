-- Compile declarative CSC rules to plot-property-gated modifiers.
-- The signed ten-bit encoding preserves MAB's 1023 magnitude limit.
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

CREATE TEMP TABLE CSC_AdjacencyCompile AS
SELECT R.*,B.Bit,'MOD_CSC_ADJ_' || R.ID || '_' || B.Bit AS ModifierId,
    'REQSET_CSC_ADJ_' || R.ID || '_' || B.Bit AS RequirementSetId,
    'REQ_CSC_ADJ_' || R.ID || '_' || B.Bit AS RequirementId
FROM CSC_AdjacencyRules R CROSS JOIN CSC_AdjacencyBits B WHERE R.FreeCompose=0;

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
SELECT RequirementId,'PropertyName','CSC_ADJ_' || ID || '_' || Bit FROM CSC_AdjacencyCompile
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

-- Building ownership intentionally retains the authoring CollectionType.
-- Current mill rules select PLAYER_DISTRICTS; do not narrow this to one city.
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
SELECT WhoIsTheOwner,'ATTACH_' || ModifierId FROM CSC_AdjacencyCompile WHERE ModifierOwner='BuildingModifiers';
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
