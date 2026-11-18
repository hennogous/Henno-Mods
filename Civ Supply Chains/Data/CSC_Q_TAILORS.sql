-- CSC_Q_TAILORS
-- Author: Henno
-- Core implementation; Gold and M&C deltas remain in their companion files.
--
-- Read top to bottom:
-- 1. Types                       2. Resource and district classes
-- 3. Stage 1 material hosts      4. Quarter placement and adjacency
-- 5. Stage 2-4 economy/Services  6. Native bindings, effects and requirements
-- 7. UI and art
--
-- Section 5 owns ordinary economic terms. CSC_Q_ALL_TransactionProcessor.sql
-- compiles them at load2500, after core/Gold/mode/venue inputs. This file declares
-- that policy and its native consumers; SQL does no recurring per-turn work.
-- Population and route Lua publish the live amount properties.

--========================================================================================================================--
/*	1. TYPES */
--========================================================================================================================--

----------------------------------------------------------------------------------------------------------------------------
--	Types
----------------------------------------------------------------------------------------------------------------------------

-- Register every district, building, hidden Service, modifier type and notification
-- identifier before it is referenced. Notification behavior is configured in section 7.

INSERT OR IGNORE INTO Types
        (   Type,                                                                Kind   )
VALUES  (   'DISTRICT_CSC_TAILORS_QUARTER',                                      'KIND_DISTRICT'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',                             'KIND_BUILDING'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',                                       'KIND_BUILDING'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',                                'KIND_BUILDING'   ),
        (   'BUILDING_CSC_TAILORS_STAGE_2_SERVICE',                              'KIND_BUILDING'   ),
        (   'BUILDING_CSC_TAILORS_STAGE_3_SERVICE',                              'KIND_BUILDING'   ),
        (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE',                              'KIND_BUILDING'   ),
        (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',                      'KIND_BUILDING'   ),
        (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY',                     'KIND_BUILDING'   ),
        (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',                       'KIND_BUILDING'   ),
        (   'MODIFIER_CSC_TAILORS_SINGLE_CITY_ADJUST_UNIT_TAG_ERA_PRODUCTION',   'KIND_MODIFIER'   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_NEW',                               'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_INCREASED',                         'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_DECREASED',                         'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_REMOVED',                           'KIND_NOTIFICATION'   );

----------------------------------------------------------------------------------------------------------------------------
--	DynamicModifiers
----------------------------------------------------------------------------------------------------------------------------

-- Map the Quarter-specific modifier type onto its native collection/effect pair.
-- The Dockmaster uses city production with unit-class and era arguments.

INSERT OR IGNORE INTO DynamicModifiers
        (   ModifierType,                                                        CollectionType,       EffectType   )
VALUES  (   'MODIFIER_CSC_TAILORS_SINGLE_CITY_ADJUST_UNIT_TAG_ERA_PRODUCTION',   'COLLECTION_OWNER',   'EFFECT_ADJUST_UNIT_TAG_ERA_PRODUCTION'   );

--========================================================================================================================--
/*	2. RESOURCES */
--========================================================================================================================--

----------------------------------------------------------------------------------------------------------------------------
--	Tags
----------------------------------------------------------------------------------------------------------------------------

-- BASE and SPEC are material classes. District-class tags identify customer
-- and sales relationships; optional resource/mod mappings are added by ModSupport.

INSERT OR IGNORE INTO Tags
        (   Tag,                                    Vocabulary   )
VALUES  (   'CLASS_CSC_TAILORS_BASE',               'RESOURCE_CLASS'   ),
        (   'CLASS_CSC_TAILORS_SPEC',               'RESOURCE_CLASS'   ),
        (   'CLASS_CSC_TAILORS_SALES',              'DISTRICT_CLASS'   ),
        (   'CLASS_CSC_TAILORS_SALES_PRODUCTION',   'DISTRICT_CLASS'   ),
        (   'CLASS_CSC_TAILORS_SALES_CULTURE',      'DISTRICT_CLASS'   );

----------------------------------------------------------------------------------------------------------------------------
--	TypeTags
----------------------------------------------------------------------------------------------------------------------------

-- Map core resources and native districts into those classes. The other sections
-- consume the classes rather than maintaining another resource or district list.

INSERT OR IGNORE INTO TypeTags
        (   Type,                        Tag   )
VALUES  (   'RESOURCE_COTTON',           'CLASS_CSC_TAILORS_BASE'   ),
        (   'RESOURCE_SHEEP',            'CLASS_CSC_TAILORS_BASE'   ),
        (   'RESOURCE_CSC_FLAX',         'CLASS_CSC_TAILORS_BASE'   ),
        (   'RESOURCE_DYES',             'CLASS_CSC_TAILORS_SPEC'   ),
        (   'RESOURCE_SILK',             'CLASS_CSC_TAILORS_SPEC'   ),
        (   'RESOURCE_SILVER',           'CLASS_CSC_TAILORS_SPEC'   ),
        (   'DISTRICT_HARBOR',           'CLASS_CSC_TAILORS_SALES'   ),
        (   'DISTRICT_HARBOR',           'CLASS_CSC_TAILORS_SALES_PRODUCTION'   ),
        (   'DISTRICT_COMMERCIAL_HUB',   'CLASS_CSC_TAILORS_SALES'   ),
        (   'DISTRICT_COMMERCIAL_HUB',   'CLASS_CSC_TAILORS_SALES_CULTURE'   ),
        (   'DISTRICT_HOLY_SITE',        'CLASS_CSC_TAILORS_SALES'   ),
        (   'DISTRICT_HOLY_SITE',        'CLASS_CSC_TAILORS_SALES_CULTURE'   ),
        (   'DISTRICT_THEATER',          'CLASS_CSC_TAILORS_SALES'   ),
        (   'DISTRICT_THEATER',          'CLASS_CSC_TAILORS_SALES_CULTURE'   );

--========================================================================================================================--
/*	3. STAGE 1 - MATERIAL IMPROVEMENTS */
--========================================================================================================================--

----------------------------------------------------------------------------------------------------------------------------
--	ImprovementModifiers
----------------------------------------------------------------------------------------------------------------------------

-- Register the improvement-owned side of material exchanges. The improvement
-- finds an adjacent eligible Quarter; producer-owned reciprocal legs are declared
-- in section 5. Shared compilation supplies the detailed effects and gates.
-- Industry/Corporation hosts and optional improvements are added by later passes.

INSERT OR IGNORE INTO ImprovementModifiers
        (   ImprovementType,            ModifierId   )
VALUES  (   'IMPROVEMENT_PLANTATION',   'MOD_CSC_TAILORS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_MINE',         'MOD_CSC_TAILORS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   );

INSERT INTO ImprovementModifiers
        (   ImprovementType,            ModifierId   )
VALUES  (   'IMPROVEMENT_FARM',         'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_PLANTATION',   'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_PASTURE',      'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER'   );

--========================================================================================================================--
/*	4. QUARTER DEFINITION AND MODIFIERS */
--========================================================================================================================--

----------------------------------------------------------------------------------------------------------------------------
--	Districts
----------------------------------------------------------------------------------------------------------------------------

-- Define placement eligibility, unlock, cost and specialty-district capacity.
-- Buildings are defined in section 5; section 6 supplies the native effect details.

INSERT OR IGNORE INTO Districts
    (
        DistrictType,
        Name,
        Description,
        PrereqTech,
        PrereqCivic,
        Cost,
        CostProgressionModel,
        CostProgressionParam1,
        MilitaryDomain,
        RequiresPlacement,
        Coast,
        RequiresPopulation,
        Aqueduct,
        InternalOnly,
        NoAdjacentCity,
        PlunderType,
        PlunderAmount,
        Appeal,
        OnePerCity,
        CaptureRemovesBuildings,
        CaptureRemovesCityDefenses,
        Maintenance,
        CityStrengthModifier,
        AdvisorType
    )
VALUES
    (
        /* DistrictType,               */  'DISTRICT_CSC_TAILORS_QUARTER',
        /* Name,                       */  'LOC_DISTRICT_CSC_TAILORS_QUARTER_NAME',
        /* Description,                */  'LOC_DISTRICT_CSC_TAILORS_QUARTER_DESCRIPTION',
        /* PrereqTech,                 */  NULL,
        /* PrereqCivic,                */  'CIVIC_CRAFTSMANSHIP',
        /* Cost,                       */  60,
        /* CostProgressionModel,       */  'COST_PROGRESSION_PREVIOUS_COPIES',
        /* CostProgressionParam1,      */  10,
        /* MilitaryDomain,             */  'NO_DOMAIN',
        /* RequiresPlacement,          */  1,
        /* Coast,                      */  0,
        /* RequiresPopulation,         */  1,
        /* Aqueduct,                   */  0,
        /* InternalOnly,               */  0,
        /* NoAdjacentCity,             */  0,
        /* PlunderType,                */  'PLUNDER_HEAL',
        /* PlunderAmount,              */  50,
        /* Appeal,                     */  1,
        /* OnePerCity,                 */  1,
        /* CaptureRemovesBuildings,    */  0,
        /* CaptureRemovesCityDefenses, */  0,
        /* Maintenance,                */  1,
        /* CityStrengthModifier,       */  2,
        /* AdvisorType,                */  'ADVISOR_GENERIC'
    );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_QuarterMaterialAdjacencyConfig
----------------------------------------------------------------------------------------------------------------------------

-- Each matching adjacent Base or Spec resource contributes the declared
-- Production adjacency. The bundled adjacency processor expands these class rules.
-- Terrain and customer adjacency use the same bundled adjacency system.

INSERT OR IGNORE INTO CSC_QuarterMaterialAdjacencyConfig
        (   QuarterKey,   SourceTag,                  SourceFilter,   YieldType,            YieldChange,   AdjacencyType   )
VALUES  (   'TAILORS',    'CLASS_CSC_TAILORS_BASE',   '',             'YIELD_PRODUCTION',   1,             'FROM_RINGS_TYPETAG_RESOURCE'   ),
        (   'TAILORS',    'CLASS_CSC_TAILORS_SPEC',   '',             'YIELD_PRODUCTION',   1,             'FROM_RINGS_TYPETAG_RESOURCE'   );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_QuarterPolicyAdjacencyConfig
----------------------------------------------------------------------------------------------------------------------------

-- Tell the shared adjacency processor which native policy doubles a customer
-- district's reciprocal adjacency return. This is separate from Quarter Gold.

INSERT OR IGNORE INTO CSC_QuarterPolicyAdjacencyConfig
        (   QuarterKey,   DistrictType,                PolicyType   )
VALUES  (   'TAILORS',    'DISTRICT_HARBOR',           'POLICY_NAVAL_INFRASTRUCTURE'   ),
        (   'TAILORS',    'DISTRICT_HARBOR',           'POLICY_ECONOMIC_UNION'   ),
        (   'TAILORS',    'DISTRICT_COMMERCIAL_HUB',   'POLICY_TOWN_CHARTERS'   ),
        (   'TAILORS',    'DISTRICT_COMMERCIAL_HUB',   'POLICY_ECONOMIC_UNION'   ),
        (   'TAILORS',    'DISTRICT_HOLY_SITE',        'POLICY_SCRIPTURE'   ),
        (   'TAILORS',    'DISTRICT_THEATER',          'POLICY_AESTHETICS'   ),
        (   'TAILORS',    'DISTRICT_THEATER',          'POLICY_SPORTS_MEDIA'   );

--========================================================================================================================--
/*	5. STAGES 2-4 - BUILDINGS AND SERVICES */
--========================================================================================================================--

-- Stage 2: Textile Workshop, Base purchases and Lighthouse exchange; Dockmaster.
-- Stage 3: Tailor, local Workshop exchange and Market/Temple sales; Sacristan.
-- Stage 4: Fashion House, Spec purchases, Workshop exchange and stepped sales
--          to Amphitheaters/the three mapped Wonders; Stage Manager.
-- Ordinary exchanges work independently of the additional Service unlocks.

----------------------------------------------------------------------------------------------------------------------------
--	Buildings
----------------------------------------------------------------------------------------------------------------------------

-- Define Stage 2, 3 and 4 producers and their hidden Service buildings.
-- Column labels are retained beside every value. Hidden Service rows represent
-- recipient-side state; active benefit wrappers are attached below.

INSERT OR IGNORE INTO Buildings
    (
        BuildingType,
        Name,
        Description,
        PrereqTech,
        PrereqCivic,
        Cost,
        PrereqDistrict,
        PurchaseYield,
        Maintenance,
        CitizenSlots,
        Entertainment,
        AdvisorType
    )
VALUES
-- Stage 2
    (
        /* BuildingType,   */  'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',
        /* Name,           */  'LOC_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_DESCRIPTION',
        /* PrereqTech,     */  'TECH_CONSTRUCTION',
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  80,
        /* PrereqDistrict, */  'DISTRICT_CSC_TAILORS_QUARTER',
        /* PurchaseYield,  */  'YIELD_GOLD',
        /* Maintenance,    */  2,
        /* CitizenSlots,   */  0,
        /* Entertainment,  */  0,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_TAILORS_STAGE_2_SERVICE',
        /* Name,           */  'LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_DESCRIPTION',
        /* PrereqTech,     */  NULL,
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_HARBOR',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  1,
        /* Entertainment,  */  0,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
-- Stage 3
    (
        /* BuildingType,   */  'BUILDING_CSC_TAILORS_TAILOR',
        /* Name,           */  'LOC_BUILDING_CSC_TAILORS_TAILOR_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_TAILORS_TAILOR_DESCRIPTION',
        /* PrereqTech,     */  NULL,
        /* PrereqCivic,    */  'CIVIC_GUILDS',
        /* Cost,           */  160,
        /* PrereqDistrict, */  'DISTRICT_CSC_TAILORS_QUARTER',
        /* PurchaseYield,  */  'YIELD_GOLD',
        /* Maintenance,    */  2,
        /* CitizenSlots,   */  1,
        /* Entertainment,  */  1,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_TAILORS_STAGE_3_SERVICE',
        /* Name,           */  'LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_DESCRIPTION',
        /* PrereqTech,     */  NULL,
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_HOLY_SITE',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  1,
        /* Entertainment,  */  0,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    );

INSERT OR IGNORE INTO Buildings
    (
        BuildingType,
        Name,
        Description,
        PrereqCivic,
        Cost,
        PrereqDistrict,
        PurchaseYield,
        Maintenance,
        CitizenSlots,
        Entertainment,
        RegionalRange,
        MustPurchase,
        AdvisorType
    )
VALUES
-- Stage 4
    (
        /* BuildingType,   */  'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        /* Name,           */  'LOC_BUILDING_CSC_TAILORS_FASHION_HOUSE_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_TAILORS_FASHION_HOUSE_DESCRIPTION',
        /* PrereqCivic,    */  'CIVIC_HUMANISM',
        /* Cost,           */  250,
        /* PrereqDistrict, */  'DISTRICT_CSC_TAILORS_QUARTER',
        /* PurchaseYield,  */  'YIELD_GOLD',
        /* Maintenance,    */  3,
        /* CitizenSlots,   */  1,
        /* Entertainment,  */  1,
        /* RegionalRange,  */  6,
        /* MustPurchase,   */  0,
        /* AdvisorType,    */  'ADVISOR_CULTURE'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_TAILORS_STAGE_4_SERVICE',
        /* Name,           */  'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_DESCRIPTION',
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_THEATER',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  1,
        /* Entertainment,  */  0,
        /* RegionalRange,  */  0,
        /* MustPurchase,   */  1,
        /* AdvisorType,    */  'ADVISOR_CULTURE'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',
        /* Name,           */  'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_DESCRIPTION',
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_WONDER',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  0,
        /* Entertainment,  */  0,
        /* RegionalRange,  */  0,
        /* MustPurchase,   */  1,
        /* AdvisorType,    */  'ADVISOR_CULTURE'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY',
        /* Name,           */  'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_DESCRIPTION',
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_WONDER',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  0,
        /* Entertainment,  */  0,
        /* RegionalRange,  */  0,
        /* MustPurchase,   */  1,
        /* AdvisorType,    */  'ADVISOR_CULTURE'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',
        /* Name,           */  'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_DESCRIPTION',
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_WONDER',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  0,
        /* Entertainment,  */  0,
        /* RegionalRange,  */  0,
        /* MustPurchase,   */  1,
        /* AdvisorType,    */  'ADVISOR_CULTURE'
    );

----------------------------------------------------------------------------------------------------------------------------
--	BuildingAvailability
----------------------------------------------------------------------------------------------------------------------------

-- MustPurchase keeps internally granted Service records out of ordinary
-- production. Their state is maintained by native grants or exact-plot Lua.

UPDATE Buildings
SET MustPurchase = 1
WHERE BuildingType IN (
	'BUILDING_CSC_TAILORS_STAGE_2_SERVICE',
	'BUILDING_CSC_TAILORS_STAGE_3_SERVICE'
);

----------------------------------------------------------------------------------------------------------------------------
--	Buildings_XP2
----------------------------------------------------------------------------------------------------------------------------

-- Hidden flags and Service grant records cannot be pillaged. Their active
-- benefits still depend on the functioning chain through the Service gates.

INSERT OR IGNORE INTO Buildings_XP2
        (   BuildingType,                                      Pillage   )
VALUES  (   'BUILDING_CSC_TAILORS_STAGE_2_SERVICE',            0   ),
        (   'BUILDING_CSC_TAILORS_STAGE_3_SERVICE',            0   ),
        (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE',            0   ),
        (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',    0   ),
        (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY',   0   ),
        (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',     0   );

----------------------------------------------------------------------------------------------------------------------------
--	BuildingPrereqs
----------------------------------------------------------------------------------------------------------------------------

-- Keep the authored producer ladder and local prerequisites together.

INSERT OR IGNORE INTO BuildingPrereqs
        (   Building,                               PrereqBuilding   )
VALUES  (   'BUILDING_CSC_TAILORS_TAILOR',          'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   );

----------------------------------------------------------------------------------------------------------------------------
--	Building_CitizenYieldChanges
----------------------------------------------------------------------------------------------------------------------------

-- These are real yields from assigned Quarter specialists. They are separate
-- from material purchases, customer sales and conditional Service effects.

INSERT INTO Building_CitizenYieldChanges
        (   BuildingType,                    YieldType,         YieldChange   )
VALUES  (   'BUILDING_CSC_TAILORS_TAILOR',   'YIELD_CULTURE',   2   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',   'YIELD_GOLD',      1   );

INSERT OR IGNORE INTO Building_CitizenYieldChanges
        (   BuildingType,                           YieldType,         YieldChange   )
VALUES  (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'YIELD_CULTURE',   1   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'YIELD_GOLD',      2   );

----------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
----------------------------------------------------------------------------------------------------------------------------

-- Attach supplied-state properties and active Service wrappers to producers.
-- Ordinary exchange attachments are generated from the declarations below.
-- A Service has its own material/civic/customer gates in section 6; those gates
-- do not restrict an ordinary building sale unless its declaration says so.
-- Dockmaster supports Ancient through Renaissance naval-unit production.
-- Sacristan adds Faith and Great Prophet points through adjacent Temples.
-- Stage Manager adds Tourism and Great Artist points through mapped venues.

INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,                           ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_FASHION_HOUSE_SUPPLIED_PROPERTY'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE_PROPERTY'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_4_SERVICE_ATTACH_THEATER'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_CUSTOMER'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_CUSTOMER'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BOLSHOI'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BOLSHOI'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BROADWAY'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BROADWAY'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_SYDNEY'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_SYDNEY'   );

INSERT INTO BuildingModifiers
        (   BuildingType,                              ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_STAGE_2_SERVICE_ATTACH_HARBOR'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_DOCKMASTER_GPP_ATTACH_HARBOR'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_TAILOR_SUPPLIED_PROPERTY'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_STAGE_3_SERVICE_ATTACH_HOLY_SITE'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_SACRISTAN_FAITH_ATTACH_HOLY_SITE'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_SACRISTAN_GPP_ATTACH_HOLY_SITE'   );

INSERT INTO BuildingModifiers
        (   BuildingType,   ModifierId   )
SELECT 'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',
	'MOD_CSC_TAILORS_STAGE_2_DOCKMASTER_ATTACH_' || REPLACE(EraType, 'ERA_', '') || '_' || REPLACE(PromotionClass, 'PROMOTION_CLASS_', '')
FROM (
SELECT 'ERA_ANCIENT' AS EraType UNION ALL
SELECT 'ERA_CLASSICAL' UNION ALL
SELECT 'ERA_MEDIEVAL' UNION ALL
SELECT 'ERA_RENAISSANCE'
)
CROSS JOIN (
SELECT 'PROMOTION_CLASS_NAVAL_MELEE' AS PromotionClass UNION ALL
SELECT 'PROMOTION_CLASS_NAVAL_RANGED' UNION ALL
SELECT 'PROMOTION_CLASS_NAVAL_RAIDER'
);

----------------------------------------------------------------------------------------------------------------------------
--	CSC_QuarterFlowBuildings
----------------------------------------------------------------------------------------------------------------------------

-- Declare the exact building for each producer stage. Gameplay-derived readers,
-- AI and flow presentation reuse these stage identities.

INSERT OR IGNORE INTO CSC_QuarterFlowBuildings
        (   QuarterKey,   Stage,   BuildingType   )
VALUES  (   'TAILORS',    2,       'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   'TAILORS',    3,       'BUILDING_CSC_TAILORS_TAILOR'   ),
        (   'TAILORS',    4,       'BUILDING_CSC_TAILORS_FASHION_HOUSE'   );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_MaterialTransactions
----------------------------------------------------------------------------------------------------------------------------

-- Identify the producer and the Base/Spec class it purchases. Stage 2 buys Base;
-- Stage 4 buys Spec. Payout legs below state the direction and yield explicitly.

INSERT INTO CSC_MaterialTransactions
        (   TransactionId,                         QuarterKey,   ProducerBuildingType,                      MaterialClass   )
VALUES
-- Stage 2
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'TAILORS',    'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'CLASS_CSC_TAILORS_BASE'   ),
-- Stage 4
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'TAILORS',    'BUILDING_CSC_TAILORS_FASHION_HOUSE',      'CLASS_CSC_TAILORS_SPEC'   );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_MaterialTransactionYields
----------------------------------------------------------------------------------------------------------------------------

-- PRODUCER is income paid to the Quarter building; IMPROVEMENT is the supplier
-- return. Amounts are per qualifying exchange. Core declares non-Gold legs;
-- Gold adds its own legs, and M&C adds only its conditional delta.

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
-- Stage 2
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',
        'INPUT_ORDINARY',
        'PRODUCER',
        'YIELD_CULTURE',
        1,
        'REGISTERED_INPUT',
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',
        'RETURN_PRODUCTION_ORDINARY',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        1,
        'ANY_PLAYER_IMPROVEMENT',
        NULL
    ),
-- Stage 4
    (
        'CSC_TAILORS_FASHION_HOUSE_SPEC',
        'INPUT_ORDINARY',
        'PRODUCER',
        'YIELD_CULTURE',
        1,
        'REGISTERED_INPUT',
        NULL
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_SPEC',
        'RETURN_PRODUCTION_ORDINARY',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        1,
        'ANY_PLAYER_IMPROVEMENT',
        NULL
    );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_BuildingTransactions
----------------------------------------------------------------------------------------------------------------------------

-- One batch owns partner families, geometry and quantity across all three stages.
-- SAME_CITY is an upstream/downstream exchange; ADJACENT_OWNED allows adjacent
-- sites in different cities of the same player. PARTNER_POPULATION scales with
-- the customer city. PARTNER_POPULATION_STEPS uses whole PopulationStep groups,
-- rounded for each customer before summing. PartnerDistrictMustFunction preserves
-- the authored district-pillage distinction.

INSERT INTO CSC_BuildingTransactions
    (
        TransactionId,
        QuarterKey,
        SourceBuildingType,
        PartnerBuildingType,
        SpatialRule,
        QuantityKind,
        QuantityAmount,
        PopulationStep,
        PartnerDistrictMustFunction,
        SellerPopulationProperty
    )
VALUES
-- Stage 2
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_LIGHTHOUSE',
        'TAILORS',
        'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',
        'BUILDING_LIGHTHOUSE',
        'ADJACENT_OWNED',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
-- Stage 3
    (
        'CSC_TAILORS_TAILOR_MARKET',
        'TAILORS',
        'BUILDING_CSC_TAILORS_TAILOR',
        'BUILDING_MARKET',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION',
        0.101,
        NULL,
        0,
        'CSC_TAILORS_STAGE_3_CUSTOMER_POP'
    ),
    (
        'CSC_TAILORS_TAILOR_TEMPLE',
        'TAILORS',
        'BUILDING_CSC_TAILORS_TAILOR',
        'BUILDING_TEMPLE',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION',
        0.101,
        NULL,
        0,
        'CSC_TAILORS_STAGE_3_CUSTOMER_POP'
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',
        'TAILORS',
        'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',
        'BUILDING_CSC_TAILORS_TAILOR',
        'SAME_CITY',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
-- Stage 4
    (
        'CSC_TAILORS_FASHION_HOUSE_AMPHITHEATER',
        'TAILORS',
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'BUILDING_AMPHITHEATER',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        1,
        NULL
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_BOLSHOI_THEATRE',
        'TAILORS',
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'BUILDING_BOLSHOI_THEATRE',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        0,
        NULL
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_BROADWAY',
        'TAILORS',
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'BUILDING_BROADWAY',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        0,
        NULL
    ),
    (
        'CSC_TAILORS_FASHION_HOUSE_SYDNEY_OPERA_HOUSE',
        'TAILORS',
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'BUILDING_SYDNEY_OPERA_HOUSE',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        0,
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',
        'TAILORS',
        'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'SAME_CITY',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_BuildingTransactionYields
----------------------------------------------------------------------------------------------------------------------------

-- SOURCE receives producer-side income; PARTNER receives the reciprocal
-- customer/upstream benefit. AmountPerUnit multiplies the transaction quantity.
-- AmountProperty names the shared Lua amount, not a second independent exchange.
-- Gold appends legs to these same identities in the companion file.

INSERT INTO CSC_BuildingTransactionYields
        (   TransactionId,                                              LegKey,                Recipient,   YieldType,            AmountPerUnit,   AmountProperty   )
VALUES
-- Stage 2
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_LIGHTHOUSE',                  'PARTNER_RETURN',      'PARTNER',   'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_LIGHTHOUSE',                  'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
-- Stage 3
        (   'CSC_TAILORS_TAILOR_MARKET',                                'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT_Q8'   ),
        (   'CSC_TAILORS_TAILOR_MARKET',                                'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_3_MARKET_CULTURE_AMOUNT_Q8'   ),
        (   'CSC_TAILORS_TAILOR_TEMPLE',                                'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT_Q8'   ),
        (   'CSC_TAILORS_TAILOR_TEMPLE',                                'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_3_TEMPLE_CULTURE_AMOUNT_Q8'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',          'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               NULL   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',          'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
-- Stage 4
        (   'CSC_TAILORS_FASHION_HOUSE_AMPHITHEATER',                   'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_AMPHITHEATER',                   'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BOLSHOI_THEATRE',                'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BOLSHOI_THEATRE',                'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BROADWAY',                       'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BROADWAY',                       'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SYDNEY_OPERA_HOUSE',             'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SYDNEY_OPERA_HOUSE',             'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',   'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               NULL   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',   'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_TradeRouteChannels
----------------------------------------------------------------------------------------------------------------------------

-- Name supplied producers and the eligibility properties read by the route
-- scanner. These are ordinary goods-route channels, not Service grants.
-- Route payout identities are bound in section 6; the final shared route reader
-- publishes their effective native amounts after compatibility loading.

INSERT INTO CSC_TradeRouteChannels
    (
        ChannelId,
        QuarterKey,
        ProducerBuildingType,
        SupplyModifierId,
        RequireProducerBuilding,
        ImportField,
        ExportField,
        ImportProperty,
        ExportProperty
    )
VALUES
    (
        'TAILORS_TAILOR',
        'TAILORS',
        'BUILDING_CSC_TAILORS_TAILOR',
        'MOD_CSC_TAILORS_TAILOR_SUPPLIED_PROPERTY',
        1,
        'ImportTailorRoute',
        'ExportTailorRoute',
        'CSC_TAILORS_IMPORT_TAILOR_ROUTE',
        'CSC_TAILORS_EXPORT_TAILOR_ROUTE'
    ),
    (
        'TAILORS_FASHION_HOUSE',
        'TAILORS',
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'MOD_CSC_TAILORS_FASHION_HOUSE_SUPPLIED_PROPERTY',
        1,
        'ImportFashionHouseRoute',
        'ExportFashionHouseRoute',
        'CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE',
        'CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE'
    );

--========================================================================================================================--
/*	6. PLUMBING */
--========================================================================================================================--

----------------------------------------------------------------------------------------------------------------------------
--	Bindings
----------------------------------------------------------------------------------------------------------------------------

-- Connect section 5's gameplay declarations to stable native modifier,
-- requirement and property identities. These rows contain implementation links;
-- change partners, quantities and payout terms in section 5 instead. Building/
-- material bindings feed the load-order-2500 compiler. Route bindings identify
-- retained native consumers to the final route reader; they add no extra payout.

INSERT INTO CSC_BuildingTransactionBindings
        (   TransactionId,                                    LegKey,                ModifierPrefix,                                                       RequirementSetPrefix,                                            BindingKind   )
VALUES  (   'CSC_TAILORS_TAILOR_MARKET',                      'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_',                   'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_',                'CITY_RATE_BITS'   ),
        (   'CSC_TAILORS_TAILOR_MARKET',                      'PARTNER_RETURN',      'MOD_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_',                       'REQSET_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_',               'CITY_RATE_BITS'   ),
        (   'CSC_TAILORS_TAILOR_TEMPLE',                      'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_',                   'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_',                'CITY_RATE_BITS'   ),
        (   'CSC_TAILORS_TAILOR_TEMPLE',                      'PARTNER_RETURN',      'MOD_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_',                       'REQSET_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_',               'CITY_RATE_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_AMPHITHEATER',         'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_',       'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_',          'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_AMPHITHEATER',         'PARTNER_RETURN',      'MOD_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_CULTURE_BIT_',   'REQSET_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_BIT_',   'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BOLSHOI_THEATRE',      'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_',       'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_',          'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BOLSHOI_THEATRE',      'PARTNER_RETURN',      'MOD_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_CULTURE_BIT_',        'REQSET_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_BIT_',        'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BROADWAY',             'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_',       'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_',          'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_BROADWAY',             'PARTNER_RETURN',      'MOD_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_CULTURE_BIT_',       'REQSET_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_BIT_',       'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SYDNEY_OPERA_HOUSE',   'SOURCE_PRODUCTION',   'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_',       'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_',          'BUILDING_STACK_BITS'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SYDNEY_OPERA_HOUSE',   'PARTNER_RETURN',      'MOD_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_CULTURE_BIT_',         'REQSET_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_BIT_',         'BUILDING_STACK_BITS'   );

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
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_TAILORS_WORKSHOP_ATTACH_HARBOR_LIGHTHOUSE',
        'MOD_CSC_TAILORS_WORKSHOP_PROD_TO_LIGHTHOUSE',
        'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE',
        'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_TAILORS_DISTRICT_IS_HARBOR',
        'REQ_CSC_TAILORS_CITY_HAS_LIGHTHOUSE'
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_LIGHTHOUSE',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_PROD',
        'MOD_CSC_TAILORS_LIGHTHOUSE_PROD_TO_WORKSHOP',
        'REQSET_CSC_ADJ_TAILORS_QUARTER',
        'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR',
        'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_TAILOR',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP',
        'MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE',
        'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_TAILORS_TEXTILE_WORKSHOP_CSC_TAILORS_FASHION_HOUSE',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP',
        'MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP',
        NULL,
        NULL,
        NULL,
        NULL
    );

INSERT INTO CSC_MaterialTransactionBindings
        (   TransactionId,                         LegKey,                         RootModifierId,                                             ChildModifierId,                                     OwnerRequirementSetId,                SubjectRequirementSetId   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_ORDINARY',               'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER',          'MOD_CSC_TAILORS_BASE_IMPROV_CULTURE_TO_WORKSHOP',   'REQSET_CSC_TAILORS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_ORDINARY',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_PROD',        'MOD_CSC_TAILORS_PROD_TO_ADJ_BASE',                  NULL,                                 'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_ORDINARY',               'MOD_CSC_TAILORS_SPEC_IMPROVEMENT_ATTACH_QUARTER',          'MOD_CSC_TAILORS_SPEC_CULTURE_TO_FASHION_HOUSE',     'REQSET_CSC_TAILORS_PLOT_HAS_SPEC',   'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_ORDINARY',   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IMP_SPEC_PROD',   'MOD_CSC_TAILORS_PROD_TO_ADJ_BASE',                  NULL,                                 'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC'   );

INSERT INTO CSC_MaterialTransactionGateBindings
        (   TransactionId,                         LegKey,                         RequirementSetId,                         RequirementId,                              GateRole   )
VALUES  (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_ORDINARY',               'REQSET_CSC_TAILORS_PLOT_HAS_BASE',       'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_ORDINARY',               'REQSET_CSC_ADJ_TAILORS_QUARTER',         'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'INPUT_ORDINARY',               'REQSET_CSC_ADJ_TAILORS_QUARTER',         'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_TEXTILE_WORKSHOP_BASE',   'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_ORDINARY',               'REQSET_CSC_TAILORS_PLOT_HAS_SPEC',       'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_ORDINARY',               'REQSET_CSC_ADJ_TAILORS_QUARTER',         'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'INPUT_ORDINARY',               'REQSET_CSC_ADJ_TAILORS_QUARTER',         'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',        'ADJACENCY'   ),
        (   'CSC_TAILORS_FASHION_HOUSE_SPEC',      'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC',   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   );

INSERT INTO CSC_TradeRoutePayoutBindings
        (   ChannelId,                 LegKey,                Recipient,       ModifierId   )
VALUES  (   'TAILORS_TAILOR',          'IMPORT_YIELD',        'ORIGIN',        'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE'   ),
        (   'TAILORS_TAILOR',          'IMPORT_AMENITY',      'ORIGIN',        'MOD_CSC_TAILORS_IMPORT_TAILOR_AMENITY'   ),
        (   'TAILORS_TAILOR',          'EXPORT_PRODUCTION',   'DESTINATION',   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION'   ),
        (   'TAILORS_FASHION_HOUSE',   'IMPORT_YIELD',        'ORIGIN',        'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_CULTURE'   ),
        (   'TAILORS_FASHION_HOUSE',   'IMPORT_AMENITY',      'ORIGIN',        'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_AMENITY'   ),
        (   'TAILORS_FASHION_HOUSE',   'EXPORT_PRODUCTION',   'DESTINATION',   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION'   );

----------------------------------------------------------------------------------------------------------------------------
--	DistrictModifiers
----------------------------------------------------------------------------------------------------------------------------

-- Lua aggregates ordinary sales and routes before publishing city-center bits.
-- Attach each aggregate consumer once per receiving city, so multiple producers
-- do not multiply an already summed payment. Route bits use whole counts; Stage 3
-- amounts use Q8 rates, while Stage 4 uses whole per-customer population stacks.

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_CULTURE_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_CULTURE_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_CULTURE_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_CULTURE_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT INTO DistrictModifiers
        (   DistrictType,             ModifierId   )
VALUES  (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_CULTURE'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_AMENITY'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_1'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_IMPORT_TAILOR_AMENITY'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION'   );

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT  'DISTRICT_CITY_CENTER',       'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT  'DISTRICT_CITY_CENTER',       'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_' || Bit
FROM CSC_Stage3RateBits
WHERE Bit > 1;

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT  'DISTRICT_CITY_CENTER',       'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_Stage3RateBits;

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_Stage3RateBits;

----------------------------------------------------------------------------------------------------------------------------
--	Modifiers
----------------------------------------------------------------------------------------------------------------------------

-- Wrappers choose eligible recipients; leaves deliver the effect. Service
-- grants, active benefits, supplied properties and ordinary amount consumers keep
-- their separate identities. Generated ordinary exchange roots/leaves come from
-- the shared compiler and the bindings above.

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                                  ModifierType,                                            OwnerRequirementSetId,                          SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_FASHION_HOUSE_SUPPLIED_PROPERTY',           'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                  'REQSET_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ',     NULL   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE_PROPERTY',   'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                  'REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ',   NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_4_SERVICE_GRANT',                     'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_4_SERVICE_ATTACH_THEATER',            'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM',                     'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',        NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_CUSTOMER',     'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP',                         'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',   NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_CUSTOMER',         'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER'   ),
        (   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_CULTURE',              'MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE',              NULL,                                           'REQSET_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE_BIT_1'   ),
        (   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_AMENITY',              'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',        NULL,                                           'REQSET_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE_BIT_1'   ),
        (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION',           'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                           'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1'   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_ATTACH_HARBOR',             'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE'   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_GRANT',                     'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP_ATTACH_HARBOR',              'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE'   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP',                            'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',   NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_TAILOR_SUPPLIED_PROPERTY',                  'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                  'REQSET_CSC_TAILORS_STAGE_3_SUPPLY_PREREQ',     NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_ATTACH_HOLY_SITE',          'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE'   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_GRANT',                     'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH_ATTACH_HOLY_SITE',          'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH',                           'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_MODIFIER',       NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP_ATTACH_HOLY_SITE',            'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP',                             'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',   NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE',                     'MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE',              NULL,                                           'REQSET_CSC_TAILORS_IMPORT_TAILOR_ROUTE_BIT_1'   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_AMENITY',                     'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',        NULL,                                           'REQSET_CSC_TAILORS_IMPORT_TAILOR_ROUTE_BIT_1'   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION',                  'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                           'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BOLSHOI',             'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',        NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BOLSHOI',      'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_STAGE_4_BOLSHOI'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BOLSHOI',          'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_STAGE_4_BOLSHOI'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BROADWAY',            'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',        NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BROADWAY',     'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_STAGE_4_BROADWAY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BROADWAY',         'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_STAGE_4_BROADWAY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_SYDNEY',              'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',        NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_SYDNEY',       'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_STAGE_4_SYDNEY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_SYDNEY',           'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_STAGE_4_SYDNEY'   );

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_' || Bit, 'MODIFIER_BUILDING_YIELD_CHANGE', NULL, 'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'MODIFIER_BUILDING_YIELD_CHANGE', NULL, 'REQSET_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'MODIFIER_BUILDING_YIELD_CHANGE', NULL, 'REQSET_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'MODIFIER_BUILDING_YIELD_CHANGE', NULL, 'REQSET_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'MODIFIER_BUILDING_YIELD_CHANGE', NULL, 'REQSET_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION_BIT_' || Bit,
	'MODIFIER_BUILDING_YIELD_CHANGE', NULL,
	'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_' || Bit,
	'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION', NULL,
	'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION_BIT_' || Bit,
	'MODIFIER_BUILDING_YIELD_CHANGE', NULL,
	'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_STAGE_2_DOCKMASTER_ATTACH_' || REPLACE(EraType, 'ERA_', '') || '_' || REPLACE(PromotionClass, 'PROMOTION_CLASS_', ''),
	'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',
	'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',
	'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE'
FROM (
SELECT 'ERA_ANCIENT' AS EraType UNION ALL
SELECT 'ERA_CLASSICAL' UNION ALL
SELECT 'ERA_MEDIEVAL' UNION ALL
SELECT 'ERA_RENAISSANCE'
)
CROSS JOIN (
SELECT 'PROMOTION_CLASS_NAVAL_MELEE' AS PromotionClass UNION ALL
SELECT 'PROMOTION_CLASS_NAVAL_RANGED' UNION ALL
SELECT 'PROMOTION_CLASS_NAVAL_RAIDER'
);

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_' || REPLACE(EraType, 'ERA_', '') || '_' || REPLACE(PromotionClass, 'PROMOTION_CLASS_', ''),
	'MODIFIER_CSC_TAILORS_SINGLE_CITY_ADJUST_UNIT_TAG_ERA_PRODUCTION', NULL, NULL
FROM (
SELECT 'ERA_ANCIENT' AS EraType UNION ALL
SELECT 'ERA_CLASSICAL' UNION ALL
SELECT 'ERA_MEDIEVAL' UNION ALL
SELECT 'ERA_RENAISSANCE'
)
CROSS JOIN (
SELECT 'PROMOTION_CLASS_NAVAL_MELEE' AS PromotionClass UNION ALL
SELECT 'PROMOTION_CLASS_NAVAL_RANGED' UNION ALL
SELECT 'PROMOTION_CLASS_NAVAL_RAIDER'
);

INSERT INTO Modifiers
        (   ModifierId,   ModifierType,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION', 'REQSET_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_Stage3RateBits;

INSERT INTO Modifiers
        (   ModifierId,   ModifierType,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION', 'REQSET_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_Stage3RateBits;

----------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
----------------------------------------------------------------------------------------------------------------------------

-- Connect wrappers to leaves and supply yield, property or benefit parameters.
-- The shared compiler refreshes ordinary transaction amounts from section 5;
-- the bit consumers below implement the encoded amount.

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                                                  Name,                     Value   )
VALUES  (   'MOD_CSC_TAILORS_FASHION_HOUSE_SUPPLIED_PROPERTY',           'Key',                    'CSC_TAILORS_FASHION_HOUSE_SUPPLIED'   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_SUPPLIED_PROPERTY',           'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE_PROPERTY',   'Key',                    'CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE'   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE_PROPERTY',   'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_STAGE_4_SERVICE_GRANT',                     'BuildingType',           'BUILDING_CSC_TAILORS_STAGE_4_SERVICE'   ),
        (   'MOD_CSC_TAILORS_STAGE_4_SERVICE_ATTACH_THEATER',            'ModifierId',             'MOD_CSC_TAILORS_STAGE_4_SERVICE_GRANT'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM',                     'Amount',                 2   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_CUSTOMER',     'ModifierId',             'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP',                         'GreatPersonClassType',   'GREAT_PERSON_CLASS_ARTIST'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP',                         'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_CUSTOMER',         'ModifierId',             'MOD_CSC_TAILORS_STAGE_MANAGER_GPP'   ),
        (   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_CULTURE',              'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_CULTURE',              'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_AMENITY',              'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION',           'BuildingType',           'BUILDING_CSC_TAILORS_FASHION_HOUSE'   ),
        (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION',           'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION',           'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_ATTACH_HARBOR',             'ModifierId',             'MOD_CSC_TAILORS_STAGE_2_SERVICE_GRANT'   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_GRANT',                     'BuildingType',           'BUILDING_CSC_TAILORS_STAGE_2_SERVICE'   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP_ATTACH_HARBOR',              'ModifierId',             'MOD_CSC_TAILORS_DOCKMASTER_GPP'   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP',                            'GreatPersonClassType',   'GREAT_PERSON_CLASS_ADMIRAL'   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP',                            'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_TAILOR_SUPPLIED_PROPERTY',                  'Key',                    'CSC_TAILORS_TAILOR_SUPPLIED'   ),
        (   'MOD_CSC_TAILORS_TAILOR_SUPPLIED_PROPERTY',                  'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_ATTACH_HOLY_SITE',          'ModifierId',             'MOD_CSC_TAILORS_STAGE_3_SERVICE_GRANT'   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_GRANT',                     'BuildingType',           'BUILDING_CSC_TAILORS_STAGE_3_SERVICE'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH_ATTACH_HOLY_SITE',          'ModifierId',             'MOD_CSC_TAILORS_SACRISTAN_FAITH'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH',                           'YieldType',              'YIELD_FAITH'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH',                           'Amount',                 10   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP_ATTACH_HOLY_SITE',            'ModifierId',             'MOD_CSC_TAILORS_SACRISTAN_GPP'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP',                             'GreatPersonClassType',   'GREAT_PERSON_CLASS_PROPHET'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP',                             'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE',                     'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE',                     'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_AMENITY',                     'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION',                  'BuildingType',           'BUILDING_CSC_TAILORS_TAILOR'   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION',                  'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION',                  'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BOLSHOI',             'Amount',                 2   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BOLSHOI',      'ModifierId',             'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BOLSHOI'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BOLSHOI',          'ModifierId',             'MOD_CSC_TAILORS_STAGE_MANAGER_GPP'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BROADWAY',            'Amount',                 2   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BROADWAY',     'ModifierId',             'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BROADWAY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BROADWAY',         'ModifierId',             'MOD_CSC_TAILORS_STAGE_MANAGER_GPP'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_SYDNEY',              'Amount',                 2   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_SYDNEY',       'ModifierId',             'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_SYDNEY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_SYDNEY',           'ModifierId',             'MOD_CSC_TAILORS_STAGE_MANAGER_GPP'   );

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION_BIT_' || Bit, 'BuildingType', 'BUILDING_CSC_TAILORS_FASHION_HOUSE'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION_BIT_' || Bit, 'YieldType', 'YIELD_PRODUCTION'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION_BIT_' || Bit, 'Amount', Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION_BIT_' || Bit, 'BuildingType', 'BUILDING_CSC_TAILORS_TAILOR'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION_BIT_' || Bit, 'YieldType', 'YIELD_PRODUCTION'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION_BIT_' || Bit, 'Amount', Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_2_DOCKMASTER_ATTACH_' || REPLACE(EraType, 'ERA_', '') || '_' || REPLACE(PromotionClass, 'PROMOTION_CLASS_', ''),
	'ModifierId',
	'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_' || REPLACE(EraType, 'ERA_', '') || '_' || REPLACE(PromotionClass, 'PROMOTION_CLASS_', '')
FROM (
SELECT 'ERA_ANCIENT' AS EraType UNION ALL
SELECT 'ERA_CLASSICAL' UNION ALL
SELECT 'ERA_MEDIEVAL' UNION ALL
SELECT 'ERA_RENAISSANCE'
)
CROSS JOIN (
SELECT 'PROMOTION_CLASS_NAVAL_MELEE' AS PromotionClass UNION ALL
SELECT 'PROMOTION_CLASS_NAVAL_RANGED' UNION ALL
SELECT 'PROMOTION_CLASS_NAVAL_RAIDER'
);

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_' || REPLACE(EraType, 'ERA_', '') || '_' || REPLACE(PromotionClass, 'PROMOTION_CLASS_', ''), 'UnitPromotionClass', PromotionClass
FROM (
SELECT 'ERA_ANCIENT' AS EraType UNION ALL SELECT 'ERA_CLASSICAL' UNION ALL SELECT 'ERA_MEDIEVAL' UNION ALL SELECT 'ERA_RENAISSANCE'
)
CROSS JOIN (
SELECT 'PROMOTION_CLASS_NAVAL_MELEE' AS PromotionClass UNION ALL SELECT 'PROMOTION_CLASS_NAVAL_RANGED' UNION ALL SELECT 'PROMOTION_CLASS_NAVAL_RAIDER'
);

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_' || REPLACE(EraType, 'ERA_', '') || '_' || REPLACE(PromotionClass, 'PROMOTION_CLASS_', ''), 'EraType', EraType
FROM (
SELECT 'ERA_ANCIENT' AS EraType UNION ALL SELECT 'ERA_CLASSICAL' UNION ALL SELECT 'ERA_MEDIEVAL' UNION ALL SELECT 'ERA_RENAISSANCE'
)
CROSS JOIN (
SELECT 'PROMOTION_CLASS_NAVAL_MELEE' AS PromotionClass UNION ALL SELECT 'PROMOTION_CLASS_NAVAL_RANGED' UNION ALL SELECT 'PROMOTION_CLASS_NAVAL_RAIDER'
);

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_' || REPLACE(EraType, 'ERA_', '') || '_' || REPLACE(PromotionClass, 'PROMOTION_CLASS_', ''), 'Amount', 20
FROM (
SELECT 'ERA_ANCIENT' AS EraType UNION ALL SELECT 'ERA_CLASSICAL' UNION ALL SELECT 'ERA_MEDIEVAL' UNION ALL SELECT 'ERA_RENAISSANCE'
)
CROSS JOIN (
SELECT 'PROMOTION_CLASS_NAVAL_MELEE' AS PromotionClass UNION ALL SELECT 'PROMOTION_CLASS_NAVAL_RANGED' UNION ALL SELECT 'PROMOTION_CLASS_NAVAL_RAIDER'
);

----------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
----------------------------------------------------------------------------------------------------------------------------

-- Name the AND/OR gates referenced by native effects. Service gates combine
-- their unlock, functioning supplier/producer and appropriate customer conditions.
-- Ordinary transaction eligibility remains distinct from Service prerequisites.

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,                                        RequirementSetType   )
VALUES  (   'REQSET_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ',              'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ',            'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER',           'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',               'REQUIREMENTSET_TEST_ANY'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_CUSTOMER',               'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',              'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE',         'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1',   'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',              'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_MARKET',                         'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_TEMPLE',                         'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_SUPPLY_PREREQ',              'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',              'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE',               'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_IMPORT_TAILOR_ROUTE',                'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1',          'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BOLSHOI',                'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BROADWAY',               'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_SYDNEY',                 'REQUIREMENTSET_TEST_ALL'   );

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL' FROM CSC_Stage3RateBits;

INSERT INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL' FROM CSC_Stage3RateBits;

----------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
----------------------------------------------------------------------------------------------------------------------------

-- Compose each named gate from its requirement IDs. Bit gates select one
-- published amount bit; Service gates preserve full gameplay eligibility.

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,                                        RequirementId   )
VALUES  (   'REQSET_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ',              'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ',              'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_SPEC'   ),
        (   'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER',           'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER',           'REQ_CSC_TAILORS_DISTRICT_IS_THEATER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER',           'REQ_CSC_TAILORS_CITY_HAS_AMPHITHEATER'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',               'REQ_CSC_TAILORS_STAGE_4_THEATER_CUSTOMER'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',               'REQ_CSC_TAILORS_STAGE_4_BOLSHOI_READY'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',               'REQ_CSC_TAILORS_STAGE_4_BROADWAY_READY'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',               'REQ_CSC_TAILORS_STAGE_4_SYDNEY_READY'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_CUSTOMER',               'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_CUSTOMER',               'REQ_CSC_TAILORS_STAGE_4_CUSTOMER_ANY'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ',            'REQ_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ',            'REQ_CSC_TAILORS_PLAYER_HAS_OPERA_BALLET'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',              'REQ_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',              'REQ_CSC_TAILORS_HAS_ADJ_STAGE_4_SERVICE_CUSTOMER'   ),
        (   'REQSET_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE',         'REQ_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE'   ),
        (   'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1',   'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1'   ),
        (   'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',              'REQ_CSC_TAILORS_PLAYER_HAS_NAVAL_TRADITION'   ),
        (   'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',              'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',              'REQ_CSC_TAILORS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_MARKET',                         'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_MARKET',                         'REQ_CSC_TAILORS_DISTRICT_IS_COMMERCIAL_HUB'   ),
        (   'REQSET_CSC_TAILORS_ADJ_MARKET',                         'REQ_CSC_TAILORS_CITY_HAS_MARKET'   ),
        (   'REQSET_CSC_TAILORS_ADJ_TEMPLE',                         'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_TEMPLE',                         'REQ_CSC_TAILORS_DISTRICT_IS_HOLY_SITE'   ),
        (   'REQSET_CSC_TAILORS_ADJ_TEMPLE',                         'REQ_CSC_TAILORS_CITY_HAS_TEMPLE'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_SUPPLY_PREREQ',              'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',              'REQ_CSC_TAILORS_PLAYER_HAS_DIVINE_RIGHT'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',              'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',              'REQ_CSC_TAILORS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE',               'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE',               'REQ_CSC_TAILORS_DISTRICT_IS_HOLY_SITE'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE',               'REQ_CSC_TAILORS_CITY_HAS_TEMPLE'   ),
        (   'REQSET_CSC_TAILORS_IMPORT_TAILOR_ROUTE',                'REQ_CSC_TAILORS_IMPORT_TAILOR_ROUTE'   ),
        (   'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1',          'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BOLSHOI',                'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BOLSHOI',                'REQ_CSC_TAILORS_STAGE_4_BOLSHOI_READY'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BROADWAY',               'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BROADWAY',               'REQ_CSC_TAILORS_STAGE_4_BROADWAY_READY'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_SYDNEY',                 'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_SYDNEY',                 'REQ_CSC_TAILORS_STAGE_4_SYDNEY_READY'   );

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_' || Bit, 'REQ_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_BIT_' || Bit, 'REQ_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_BIT_' || Bit, 'REQ_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_BIT_' || Bit, 'REQ_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_BIT_' || Bit, 'REQ_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit,
	'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit,
	'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit,
	'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'REQ_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_Stage3RateBits;

INSERT INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'REQ_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_Stage3RateBits;

----------------------------------------------------------------------------------------------------------------------------
--	Requirements
----------------------------------------------------------------------------------------------------------------------------

-- Declare the native test and inversion for each condition. Ownership,
-- adjacency, building, supply and unlock tests are parameterized below.

INSERT OR IGNORE INTO Requirements
        (   RequirementId,                                        RequirementType,                            Inverse   )
VALUES  (   'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_TAILORS_PLAYER_HAS_OPERA_BALLET',            'REQUIREMENT_PLAYER_HAS_CIVIC',             0   ),
        (   'REQ_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ',              'REQUIREMENT_REQUIREMENTSET_IS_MET',        0   ),
        (   'REQ_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ',            'REQUIREMENT_REQUIREMENTSET_IS_MET',        0   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_THEATER',                'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_AMPHITHEATER',              'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_TAILORS_STAGE_4_THEATER_CUSTOMER',           'REQUIREMENT_REQUIREMENTSET_IS_MET',        0   ),
        (   'REQ_CSC_TAILORS_STAGE_4_BOLSHOI_READY',              'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_TAILORS_STAGE_4_BROADWAY_READY',             'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_TAILORS_STAGE_4_SYDNEY_READY',               'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',               'REQUIREMENT_REQUIREMENTSET_IS_MET',        0   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_4_SERVICE_CUSTOMER',   'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE',         'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1',   'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_TAILORS_PLAYER_HAS_NAVAL_TRADITION',         'REQUIREMENT_PLAYER_HAS_CIVIC',             0   ),
        (   'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE',         'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_COMMERCIAL_HUB',         'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_HOLY_SITE',              'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_MARKET',                    'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_TEMPLE',                    'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_TAILORS_PLAYER_HAS_DIVINE_RIGHT',            'REQUIREMENT_PLAYER_HAS_CIVIC',             0   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_TAILORS_IMPORT_TAILOR_ROUTE',                'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1',          'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   );

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT 'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT 'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT 'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT 'REQ_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES' FROM CSC_Stage3RateBits;

INSERT INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT 'REQ_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES' FROM CSC_Stage3RateBits;

----------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
----------------------------------------------------------------------------------------------------------------------------

-- Supply exact classes, building/district types, technologies/civics and property
-- thresholds for the tests above. This is the detailed wiring behind the readable
-- building/transaction declarations, not another source of economic terms.

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,                                        Name,                  Value   )
VALUES  (   'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'CollectionType',      'COLLECTION_PLAYER_IMPROVEMENTS'   ),
        (   'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'Count',               1   ),
        (   'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'RequirementSetId',    'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC'   ),
        (   'REQ_CSC_TAILORS_PLAYER_HAS_OPERA_BALLET',            'CivicType',           'CIVIC_OPERA_BALLET'   ),
        (   'REQ_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ',              'RequirementSetId',    'REQSET_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ'   ),
        (   'REQ_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ',            'RequirementSetId',    'REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ'   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_THEATER',                'DistrictType',        'DISTRICT_THEATER'   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_AMPHITHEATER',              'BuildingType',        'BUILDING_AMPHITHEATER'   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_AMPHITHEATER',              'MustBeFunctioning',   1   ),
        (   'REQ_CSC_TAILORS_STAGE_4_THEATER_CUSTOMER',           'RequirementSetId',    'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER'   ),
        (   'REQ_CSC_TAILORS_STAGE_4_BOLSHOI_READY',              'PropertyName',        'CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_READY'   ),
        (   'REQ_CSC_TAILORS_STAGE_4_BOLSHOI_READY',              'PropertyMinimum',     1   ),
        (   'REQ_CSC_TAILORS_STAGE_4_BROADWAY_READY',             'PropertyName',        'CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_READY'   ),
        (   'REQ_CSC_TAILORS_STAGE_4_BROADWAY_READY',             'PropertyMinimum',     1   ),
        (   'REQ_CSC_TAILORS_STAGE_4_SYDNEY_READY',               'PropertyName',        'CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_READY'   ),
        (   'REQ_CSC_TAILORS_STAGE_4_SYDNEY_READY',               'PropertyMinimum',     1   ),
        (   'REQ_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',               'RequirementSetId',    'REQSET_CSC_TAILORS_STAGE_4_CUSTOMER_ANY'   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_4_SERVICE_CUSTOMER',   'CollectionType',      'COLLECTION_PLAYER_DISTRICTS'   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_4_SERVICE_CUSTOMER',   'Count',               1   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_4_SERVICE_CUSTOMER',   'RequirementSetId',    'REQSET_CSC_TAILORS_ADJ_STAGE_4_CUSTOMER'   ),
        (   'REQ_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE',         'PropertyName',        'CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE'   ),
        (   'REQ_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE',         'PropertyMinimum',     1   ),
        (   'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1',   'PropertyName',        'CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1'   ),
        (   'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1',   'PropertyMinimum',     1   ),
        (   'REQ_CSC_TAILORS_PLAYER_HAS_NAVAL_TRADITION',         'CivicType',           'CIVIC_NAVAL_TRADITION'   ),
        (   'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE',         'CollectionType',      'COLLECTION_PLAYER_IMPROVEMENTS'   ),
        (   'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE',         'Count',               1   ),
        (   'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE',         'RequirementSetId',    'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE'   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'CollectionType',      'COLLECTION_PLAYER_DISTRICTS'   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'Count',               1   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'RequirementSetId',    'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE'   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_COMMERCIAL_HUB',         'DistrictType',        'DISTRICT_COMMERCIAL_HUB'   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_HOLY_SITE',              'DistrictType',        'DISTRICT_HOLY_SITE'   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_MARKET',                    'BuildingType',        'BUILDING_MARKET'   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_MARKET',                    'MustBeFunctioning',   1   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_TEMPLE',                    'BuildingType',        'BUILDING_TEMPLE'   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_TEMPLE',                    'MustBeFunctioning',   1   ),
        (   'REQ_CSC_TAILORS_PLAYER_HAS_DIVINE_RIGHT',            'CivicType',           'CIVIC_DIVINE_RIGHT'   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'CollectionType',      'COLLECTION_PLAYER_DISTRICTS'   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'Count',               1   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'RequirementSetId',    'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE'   ),
        (   'REQ_CSC_TAILORS_IMPORT_TAILOR_ROUTE',                'PropertyName',        'CSC_TAILORS_IMPORT_TAILOR_ROUTE'   ),
        (   'REQ_CSC_TAILORS_IMPORT_TAILOR_ROUTE',                'PropertyMinimum',     1   ),
        (   'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1',          'PropertyName',        'CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1'   ),
        (   'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1',          'PropertyMinimum',     1   );

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_' || Bit, 'PropertyName', 'CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_BIT_' || Bit, 'PropertyName', 'CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_BIT_' || Bit, 'PropertyName', 'CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_BIT_' || Bit, 'PropertyName', 'CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_BIT_' || Bit, 'PropertyName', 'CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit, 'PropertyName',
	'CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'PropertyName',
	'CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT_Q8_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit, 'PropertyName',
	'CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'PropertyName', 'CSC_TAILORS_STAGE_3_MARKET_CULTURE_AMOUNT_Q8_BIT_' || Bit FROM CSC_Stage3RateBits;

INSERT INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'PropertyMinimum', 1 FROM CSC_Stage3RateBits;

INSERT INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'PropertyName', 'CSC_TAILORS_STAGE_3_TEMPLE_CULTURE_AMOUNT_Q8_BIT_' || Bit FROM CSC_Stage3RateBits;

INSERT INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'PropertyMinimum', 1 FROM CSC_Stage3RateBits;

----------------------------------------------------------------------------------------------------------------------------
--	RouteImports
----------------------------------------------------------------------------------------------------------------------------

-- Expand the existing origin-side consumers for whole route counts. The route
-- scanner publishes bits; base +1 consumers and these 2/4/8/16 consumers pay the
-- same total without multiplying by producer count. Keep temporary channel/effect
-- setup, all dependent SELECTs and teardown together.

CREATE TEMP TABLE CSC_TailorsImportChannels (Channel TEXT PRIMARY KEY);

INSERT INTO CSC_TailorsImportChannels
        (   Channel   )
VALUES  (   'TAILOR'   ),
        (   'FASHION_HOUSE'   );

CREATE TEMP TABLE CSC_TailorsImportEffects (Effect TEXT PRIMARY KEY, ModifierType TEXT);

INSERT INTO CSC_TailorsImportEffects
        (   Effect,      ModifierType   )
VALUES  (   'CULTURE',   'MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE'   ),
        (   'AMENITY',   'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY'   );

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_IMPORT_' || Channel || '_' || Effect || '_BIT_' || Bit
FROM CSC_TailorsImportChannels CROSS JOIN CSC_TailorsImportEffects CROSS JOIN CSC_RouteStackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_IMPORT_' || Channel || '_' || Effect || '_BIT_' || Bit,
       ModifierType, 'REQSET_CSC_TAILORS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit
FROM CSC_TailorsImportChannels CROSS JOIN CSC_TailorsImportEffects CROSS JOIN CSC_RouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_IMPORT_' || Channel || '_' || Effect || '_BIT_' || Bit, 'Amount', Bit
FROM CSC_TailorsImportChannels CROSS JOIN CSC_TailorsImportEffects CROSS JOIN CSC_RouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_IMPORT_' || Channel || '_CULTURE_BIT_' || Bit, 'YieldType', 'YIELD_CULTURE'
FROM CSC_TailorsImportChannels CROSS JOIN CSC_RouteStackBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT 'REQ_CSC_TAILORS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES'
FROM CSC_TailorsImportChannels CROSS JOIN (SELECT 1 AS Bit UNION ALL SELECT Bit FROM CSC_RouteStackBits);

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_TailorsImportChannels CROSS JOIN (SELECT 1 AS Bit UNION ALL SELECT Bit FROM CSC_RouteStackBits);

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit,
       'REQ_CSC_TAILORS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit
FROM CSC_TailorsImportChannels CROSS JOIN (SELECT 1 AS Bit UNION ALL SELECT Bit FROM CSC_RouteStackBits);

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit,
       'PropertyName', 'CSC_TAILORS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit
FROM CSC_TailorsImportChannels CROSS JOIN (SELECT 1 AS Bit UNION ALL SELECT Bit FROM CSC_RouteStackBits);

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_TailorsImportChannels CROSS JOIN (SELECT 1 AS Bit UNION ALL SELECT Bit FROM CSC_RouteStackBits);

DROP TABLE CSC_TailorsImportEffects;

DROP TABLE CSC_TailorsImportChannels;

--========================================================================================================================--
/*	7. UI AND ART */
--========================================================================================================================--

----------------------------------------------------------------------------------------------------------------------------
--	PresentationText
----------------------------------------------------------------------------------------------------------------------------

-- Append CSC disclosures to customer buildings and unlock descriptions.
-- These updates affect presentation; the actual eligibility remains above.

UPDATE Buildings
SET Description = CASE
	WHEN Description IS NULL OR Description = '' THEN 'LOC_CSC_TAILORS_STAGE_2_EFFECT'
	ELSE '{' || Description || '}' || '[NEWLINE][NEWLINE]{LOC_CSC_TAILORS_STAGE_2_EFFECT}'
END
WHERE BuildingType = 'BUILDING_LIGHTHOUSE'
	OR BuildingType IN (SELECT CivUniqueBuildingType FROM BuildingReplaces WHERE ReplacesBuildingType = 'BUILDING_LIGHTHOUSE');

UPDATE Buildings
SET Description = CASE
	WHEN Description IS NULL OR Description = '' THEN 'LOC_CSC_TAILORS_STAGE_3_MARKET_EFFECT'
	ELSE '{' || Description || '}' || '{LOC_CSC_TAILORS_STAGE_3_MARKET_EFFECT_APPEND}'
END
WHERE BuildingType = 'BUILDING_MARKET'
	OR BuildingType IN (SELECT CivUniqueBuildingType FROM BuildingReplaces WHERE ReplacesBuildingType = 'BUILDING_MARKET');

UPDATE Buildings
SET Description = CASE
	WHEN Description IS NULL OR Description = '' THEN 'LOC_CSC_TAILORS_STAGE_3_TEMPLE_EFFECT'
	ELSE '{' || Description || '}' || '{LOC_CSC_TAILORS_STAGE_3_TEMPLE_EFFECT_APPEND}'
END
WHERE BuildingType = 'BUILDING_TEMPLE'
	OR BuildingType IN (SELECT CivUniqueBuildingType FROM BuildingReplaces WHERE ReplacesBuildingType = 'BUILDING_TEMPLE');

UPDATE Buildings
SET Description = CASE
	WHEN Description IS NULL OR Description = '' THEN 'LOC_CSC_TAILORS_STAGE_4_AMPHITHEATER_EFFECT'
	ELSE '{' || Description || '}' || '{LOC_CSC_TAILORS_STAGE_4_AMPHITHEATER_EFFECT_APPEND}'
END
WHERE BuildingType = 'BUILDING_AMPHITHEATER' OR BuildingType IN (SELECT CivUniqueBuildingType FROM BuildingReplaces WHERE ReplacesBuildingType = 'BUILDING_AMPHITHEATER');

UPDATE Buildings
SET Description = CASE
	WHEN Description IS NULL OR Description = '' THEN 'LOC_CSC_TAILORS_STAGE_4_BOLSHOI_EFFECT'
	ELSE '{' || Description || '}' || '{LOC_CSC_TAILORS_STAGE_4_BOLSHOI_EFFECT_APPEND}'
END
WHERE BuildingType = 'BUILDING_BOLSHOI_THEATRE';

UPDATE Buildings
SET Description = CASE
	WHEN Description IS NULL OR Description = '' THEN 'LOC_CSC_TAILORS_STAGE_4_BROADWAY_EFFECT'
	ELSE '{' || Description || '}' || '{LOC_CSC_TAILORS_STAGE_4_BROADWAY_EFFECT_APPEND}'
END
WHERE BuildingType = 'BUILDING_BROADWAY';

UPDATE Buildings
SET Description = CASE
	WHEN Description IS NULL OR Description = '' THEN 'LOC_CSC_TAILORS_STAGE_4_SYDNEY_EFFECT'
	ELSE '{' || Description || '}' || '{LOC_CSC_TAILORS_STAGE_4_SYDNEY_EFFECT_APPEND}'
END
WHERE BuildingType = 'BUILDING_SYDNEY_OPERA_HOUSE';

UPDATE Civics
SET Description = CASE
	WHEN Description IS NULL OR Description = '' THEN 'LOC_CSC_TAILORS_STAGE_4_CIVIC'
	ELSE '{' || Description || '}' || '{LOC_CSC_TAILORS_STAGE_4_CIVIC_APPEND}'
END
WHERE CivicType = 'CIVIC_OPERA_BALLET';

UPDATE Civics
SET Description = CASE
	WHEN Description IS NULL OR Description = '' THEN 'LOC_CSC_TAILORS_STAGE_2_CIVIC'
	ELSE '{' || Description || '}' || '{LOC_CSC_TAILORS_STAGE_2_CIVIC_APPEND}'
END
WHERE CivicType = 'CIVIC_NAVAL_TRADITION';

UPDATE Civics
SET Description = CASE
	WHEN Description IS NULL OR Description = '' THEN 'LOC_CSC_TAILORS_STAGE_3_CIVIC'
	ELSE '{' || Description || '}' || '{LOC_CSC_TAILORS_STAGE_3_CIVIC_APPEND}'
END
WHERE CivicType = 'CIVIC_DIVINE_RIGHT';

----------------------------------------------------------------------------------------------------------------------------
--	Notifications
----------------------------------------------------------------------------------------------------------------------------

-- Configure the notification identities registered in section 1. Shared Lua
-- observes active benefit wrappers below to report gains, losses and changes.

INSERT OR IGNORE INTO Notifications
        (   NotificationType,                              SeverityType,   ExpiresEndOfTurn,   AutoNotify   )
VALUES  (   'NOTIFICATION_CSC_TAILORS_EFFECT_NEW',         'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_INCREASED',   'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_DECREASED',   'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_REMOVED',     'HIGH',         0,                  0   );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_AbilityAttachModifiers
----------------------------------------------------------------------------------------------------------------------------

-- Observe active benefit wrappers rather than hidden Service grants. The shared
-- notification/MCUIS system counts live recipients. Wonder and era-specific
-- branches keep explicit native identities for accurate presentation.

INSERT INTO CSC_AbilityAttachModifiers
        (   ModifierId,                                                        AbilityIcon,                                   AbilityIconTarget,                        NotificationQuarter   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_2_DOCKMASTER_ATTACH_ANCIENT_NAVAL_MELEE',   'ICON_BUILDING_CSC_TAILORS_STAGE_2_SERVICE',   'BUILDING_CSC_TAILORS_STAGE_2_SERVICE',   'TAILORS'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH_ATTACH_HOLY_SITE',                'ICON_BUILDING_CSC_TAILORS_STAGE_3_SERVICE',   'BUILDING_CSC_TAILORS_STAGE_3_SERVICE',   'TAILORS'   );

INSERT OR IGNORE INTO CSC_AbilityAttachModifiers
        (   ModifierId,                                                AbilityIcon,                                            AbilityIconTarget,                                 NotificationQuarter   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BOLSHOI',    'ICON_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',    'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',    'TAILORS'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BROADWAY',   'ICON_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY',   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY',   'TAILORS'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_SYDNEY',     'ICON_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',     'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',     'TAILORS'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_CUSTOMER',   'ICON_BUILDING_CSC_TAILORS_STAGE_4_SERVICE',            'BUILDING_CSC_TAILORS_STAGE_4_SERVICE',            'TAILORS'   );

-- The gameplay reconciler grants each persistent Service on this exact Wonder
-- plot. The AI can resolve the same READY gate to a real completed recipient
-- when forecasting a nearby Fashion House, before the marker has been set.
INSERT INTO CSC_QuarterWonderServices
        (   HostType,                        ServiceType,                                       ActivationProperty   )
VALUES  (   'BUILDING_BOLSHOI_THEATRE',      'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',    'CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_READY'   ),
        (   'BUILDING_BROADWAY',             'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY',   'CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_READY'   ),
        (   'BUILDING_SYDNEY_OPERA_HOUSE',   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',     'CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_READY'   );

----------------------------------------------------------------------------------------------------------------------------
--	ModifierStrings
----------------------------------------------------------------------------------------------------------------------------

-- Associate benefit leaves with localized preview text. Terms and eligibility
-- stay in gameplay declarations and requirements, not in these strings.

INSERT INTO ModifierStrings
        (   ModifierId,                                                Context,     'Text'   )
VALUES  (   'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_ANCIENT_NAVAL_MELEE',   'Preview',   'LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION'   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_GRANT',                   'Preview',   'LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH',                         'Preview',   'LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION'   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_GRANT',                   'Preview',   'LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME'   );

INSERT OR IGNORE INTO ModifierStrings
        (   ModifierId,                                         Context,     Text   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM',            'Preview',   'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION'   ),
        (   'MOD_CSC_TAILORS_STAGE_4_SERVICE_GRANT',            'Preview',   'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BOLSHOI',    'Preview',   'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BOLSHOI'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BROADWAY',   'Preview',   'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BROADWAY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_SYDNEY',     'Preview',   'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_SYDNEY'   );

----------------------------------------------------------------------------------------------------------------------------
--	ArtProperties
----------------------------------------------------------------------------------------------------------------------------

-- Reuse the complete Service gate to write an art source property.
-- CSC_ArtProperties.lua mirrors that result into binary art-selection flags;
-- it does not implement another material/civic/customer eligibility calculation.

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                               ModifierType,                             OwnerRequirementSetId,                        SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_2_ART_PROPERTY',   'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',   'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',   NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_3_ART_PROPERTY',   'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',   'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',   NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_4_ART_PROPERTY',   'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',   'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',   NULL   );

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                               Name,       Value   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_2_ART_PROPERTY',   'Key',      'CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_STAGE_2_ART_PROPERTY',   'Amount',   1   ),
        (   'MOD_CSC_TAILORS_STAGE_3_ART_PROPERTY',   'Key',      'CSC_TAILORS_STAGE_3_EFFECT_FAITH'   ),
        (   'MOD_CSC_TAILORS_STAGE_3_ART_PROPERTY',   'Amount',   1   ),
        (   'MOD_CSC_TAILORS_STAGE_4_ART_PROPERTY',   'Key',      'CSC_TAILORS_STAGE_4_EFFECT_TOURISM'   ),
        (   'MOD_CSC_TAILORS_STAGE_4_ART_PROPERTY',   'Amount',   1   );

INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,                              ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_STAGE_2_ART_PROPERTY'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_STAGE_3_ART_PROPERTY'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',      'MOD_CSC_TAILORS_STAGE_4_ART_PROPERTY'   );
