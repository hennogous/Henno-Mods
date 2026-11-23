-- CSC_Q_BAKERS
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
        (   Type,                                          Kind   )
VALUES  (   'DISTRICT_CSC_BAKERS_QUARTER',                 'KIND_DISTRICT'   ),
        (   'BUILDING_CSC_BAKERS_RIVER_ACCESS',            'KIND_BUILDING'   ),
        (   'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',         'KIND_BUILDING'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',               'KIND_BUILDING'   ),
        (   'BUILDING_CSC_BAKERS_WATER_MILL',              'KIND_BUILDING'   ),
        (   'BUILDING_CSC_BAKERS_BAKERY',                  'KIND_BUILDING'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',                    'KIND_BUILDING'   ),
        (   'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',         'KIND_BUILDING'   ),
        (   'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',         'KIND_BUILDING'   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',   'KIND_BUILDING'   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',   'KIND_BUILDING'   );

INSERT INTO Types
        (   Type,                                         Kind   )
VALUES  (   'NOTIFICATION_CSC_BAKERS_EFFECT_NEW',         'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_INCREASED',   'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_DECREASED',   'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_REMOVED',     'KIND_NOTIFICATION'   );



--========================================================================================================================--
/*	2. RESOURCES */
--========================================================================================================================--

----------------------------------------------------------------------------------------------------------------------------
--	Tags
----------------------------------------------------------------------------------------------------------------------------

-- BASE and SPEC are material classes. District-class tags identify customer
-- and sales relationships; optional resource/mod mappings are added by ModSupport.

INSERT OR IGNORE INTO Tags
        (   Tag,                                Vocabulary   )
VALUES  (   'CLASS_CSC_BAKERS_BASE',            'RESOURCE_CLASS'   ),
        (   'CLASS_CSC_BAKERS_SPEC',            'RESOURCE_CLASS'   ),
        (   'CLASS_CSC_BAKERS_SALES',           'DISTRICT_CLASS'   ),
        (   'CLASS_CSC_BAKERS_SALES_FOOD',      'DISTRICT_CLASS'   ),
        (   'CLASS_CSC_BAKERS_SALES_CULTURE',   'DISTRICT_CLASS'   );

----------------------------------------------------------------------------------------------------------------------------
--	TypeTags
----------------------------------------------------------------------------------------------------------------------------

-- Map core resources and native districts into those classes. The other sections
-- consume the classes rather than maintaining another resource or district list.

INSERT OR IGNORE INTO TypeTags
        (   Type,                                     Tag   )
VALUES  (   'RESOURCE_BANANAS',                       'CLASS_CSC_BAKERS_BASE'   ),
        (   'RESOURCE_MAIZE',                         'CLASS_CSC_BAKERS_BASE'   ),
        (   'RESOURCE_RICE',                          'CLASS_CSC_BAKERS_BASE'   ),
        (   'RESOURCE_WHEAT',                         'CLASS_CSC_BAKERS_BASE'   ),
        (   'RESOURCE_COCOA',                         'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_COFFEE',                        'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_WINE',                          'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_OLIVES',                        'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_SALT',                          'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_SPICES',                        'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_SUGAR',                         'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_TEA',                           'CLASS_CSC_BAKERS_SPEC'   ),
        (   'DISTRICT_CITY_CENTER',                   'CLASS_CSC_BAKERS_SALES'   ),
        (   'DISTRICT_CITY_CENTER',                   'CLASS_CSC_BAKERS_SALES_FOOD'   ),
        (   'DISTRICT_COMMERCIAL_HUB',                'CLASS_CSC_BAKERS_SALES'   ),
        (   'DISTRICT_COMMERCIAL_HUB',                'CLASS_CSC_BAKERS_SALES_FOOD'   ),
        (   'DISTRICT_ENTERTAINMENT_COMPLEX',         'CLASS_CSC_BAKERS_SALES'   ),
        (   'DISTRICT_ENTERTAINMENT_COMPLEX',         'CLASS_CSC_BAKERS_SALES_CULTURE'   ),
        (   'DISTRICT_WATER_ENTERTAINMENT_COMPLEX',   'CLASS_CSC_BAKERS_SALES'   ),
        (   'DISTRICT_WATER_ENTERTAINMENT_COMPLEX',   'CLASS_CSC_BAKERS_SALES_CULTURE'   );



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

INSERT INTO ImprovementModifiers
        (   ImprovementType,            ModifierId   )
VALUES  (   'IMPROVEMENT_FARM',         'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER'   ),
        (   'IMPROVEMENT_PLANTATION',   'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER'   ),
        (   'IMPROVEMENT_PASTURE',      'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER'   ),
        (   'IMPROVEMENT_FARM',         'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND'   ),
        (   'IMPROVEMENT_PLANTATION',   'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND'   ),
        (   'IMPROVEMENT_PASTURE',      'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND'   ),
        (   'IMPROVEMENT_CAMP',         'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_MINE',         'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_PLANTATION',   'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   );



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
        /* DistrictType,               */  'DISTRICT_CSC_BAKERS_QUARTER',
        /* Name,                       */  'LOC_DISTRICT_CSC_BAKERS_QUARTER_NAME',
        /* Description,                */  'LOC_DISTRICT_CSC_BAKERS_QUARTER_DESCRIPTION',
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
        (   QuarterKey,   SourceTag,                 SourceFilter,   YieldType,            YieldChange,   AdjacencyType   )
VALUES  (   'BAKERS',     'CLASS_CSC_BAKERS_BASE',   '',             'YIELD_PRODUCTION',   1,             'FROM_RINGS_TYPETAG_RESOURCE'   ),
        (   'BAKERS',     'CLASS_CSC_BAKERS_SPEC',   '',             'YIELD_PRODUCTION',   1,             'FROM_RINGS_TYPETAG_RESOURCE'   );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_QuarterPolicyAdjacencyConfig
----------------------------------------------------------------------------------------------------------------------------

-- Tell the shared adjacency processor which native policy doubles a customer
-- district's reciprocal adjacency return. This is separate from Quarter Gold.

INSERT OR IGNORE INTO CSC_QuarterPolicyAdjacencyConfig
        (   QuarterKey,   DistrictType,                PolicyType   )
VALUES  (   'BAKERS',     'DISTRICT_COMMERCIAL_HUB',   'POLICY_TOWN_CHARTERS'   ),
        (   'BAKERS',     'DISTRICT_COMMERCIAL_HUB',   'POLICY_ECONOMIC_UNION'   );

----------------------------------------------------------------------------------------------------------------------------
--	DistrictModifiers
----------------------------------------------------------------------------------------------------------------------------

-- Attach the Quarter's river-state helpers. They grant internal flags used by
-- Water Mill eligibility; the flag and requirement implementations are in section 6.

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,                    ModifierId   )
VALUES  (   'DISTRICT_CSC_BAKERS_QUARTER',   'MOD_CSC_BAKERS_RIVER_ACCESS_FLAG'   ),
        (   'DISTRICT_CSC_BAKERS_QUARTER',   'MOD_CSC_BAKERS_NO_RIVER_ACCESS_FLAG'   );



--========================================================================================================================--
/*	5. STAGES 2-4 - BUILDINGS AND SERVICES */
--========================================================================================================================--

-- Stage 2: Water/Wind Mill, Base purchases and Granary exchanges; Storekeeper.
-- Stage 3: Bakery, local Mill exchange and population sales to Markets; Innkeeper.
-- Stage 4: Cafe, Spec purchases, Mill exchange and stepped venue sales;
--          Groundskeeper/Ride Technician. Garden integration adds its venue.
-- Ordinary exchanges work independently of the additional Service unlocks.

----------------------------------------------------------------------------------------------------------------------------
--	VanillaBuildingReplacement
----------------------------------------------------------------------------------------------------------------------------

-- Replace the vanilla City Center Water Mill with Quarter-specific producers.
-- Remove the Palgum replacement link as part of the same existing substitution.

DELETE FROM Buildings WHERE BuildingType='BUILDING_WATER_MILL';

DELETE FROM BuildingReplaces WHERE CivUniqueBuildingType='BUILDING_PALGUM';

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
-- Internal eligibility flags
    (
        /* BuildingType,   */  'BUILDING_CSC_BAKERS_RIVER_ACCESS',
        /* Name,           */  'LOC_BUILDING_CSC_BAKERS_RIVER_ACCESS_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_BAKERS_RIVER_ACCESS_DESCRIPTION',
        /* PrereqTech,     */  NULL,
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  0,
        /* Entertainment,  */  0,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',
        /* Name,           */  'LOC_BUILDING_CSC_BAKERS_NO_RIVER_ACCESS_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_BAKERS_NO_RIVER_ACCESS_DESCRIPTION',
        /* PrereqTech,     */  NULL,
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  0,
        /* Entertainment,  */  0,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
-- Stage 2
    (
        /* BuildingType,   */  'BUILDING_CSC_BAKERS_WIND_MILL',
        /* Name,           */  'LOC_BUILDING_CSC_BAKERS_WIND_MILL_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_BAKERS_WIND_MILL_DESCRIPTION',
        /* PrereqTech,     */  'TECH_MACHINERY',
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  80,
        /* PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /* PurchaseYield,  */  'YIELD_GOLD',
        /* Maintenance,    */  2,
        /* CitizenSlots,   */  0,
        /* Entertainment,  */  0,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_BAKERS_WATER_MILL',
        /* Name,           */  'LOC_BUILDING_CSC_BAKERS_WATER_MILL_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_BAKERS_WATER_MILL_DESCRIPTION',
        /* PrereqTech,     */  'TECH_ENGINEERING',
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  80,
        /* PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /* PurchaseYield,  */  'YIELD_GOLD',
        /* Maintenance,    */  2,
        /* CitizenSlots,   */  0,
        /* Entertainment,  */  0,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',
        /* Name,           */  'LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_DESCRIPTION',
        /* PrereqTech,     */  NULL,
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_CITY_CENTER',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  0,
        /* Entertainment,  */  0,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
-- Stage 3
    (
        /* BuildingType,   */  'BUILDING_CSC_BAKERS_BAKERY',
        /* Name,           */  'LOC_BUILDING_CSC_BAKERS_BAKERY_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_BAKERS_BAKERY_DESCRIPTION',
        /* PrereqTech,     */  NULL,
        /* PrereqCivic,    */  'CIVIC_GUILDS',
        /* Cost,           */  160,
        /* PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /* PurchaseYield,  */  'YIELD_GOLD',
        /* Maintenance,    */  2,
        /* CitizenSlots,   */  1,
        /* Entertainment,  */  1,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',
        /* Name,           */  'LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_DESCRIPTION',
        /* PrereqTech,     */  NULL,
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_COMMERCIAL_HUB',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  1,
        /* Entertainment,  */  0,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
-- Stage 4
    (
        /* BuildingType,   */  'BUILDING_CSC_BAKERS_CAFE',
        /* Name,           */  'LOC_BUILDING_CSC_BAKERS_CAFE_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION',
        /* PrereqTech,     */  NULL,
        /* PrereqCivic,    */  'CIVIC_HUMANISM',
        /* Cost,           */  250,
        /* PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /* PurchaseYield,  */  'YIELD_GOLD',
        /* Maintenance,    */  3,
        /* CitizenSlots,   */  1,
        /* Entertainment,  */  1,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',
        /* Name,           */  'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_DESCRIPTION',
        /* PrereqTech,     */  NULL,
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_ENTERTAINMENT_COMPLEX',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  1,
        /* Entertainment,  */  0,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    ),
    (
        /* BuildingType,   */  'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',
        /* Name,           */  'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME',
        /* Description,    */  'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_DESCRIPTION',
        /* PrereqTech,     */  NULL,
        /* PrereqCivic,    */  NULL,
        /* Cost,           */  0,
        /* PrereqDistrict, */  'DISTRICT_WATER_ENTERTAINMENT_COMPLEX',
        /* PurchaseYield,  */  NULL,
        /* Maintenance,    */  0,
        /* CitizenSlots,   */  1,
        /* Entertainment,  */  0,
        /* AdvisorType,    */  'ADVISOR_GENERIC'
    );

----------------------------------------------------------------------------------------------------------------------------
--	BuildingAvailability
----------------------------------------------------------------------------------------------------------------------------

-- MustPurchase keeps internally granted Service records out of ordinary
-- production. Their state is maintained by native grants or exact-plot Lua.
-- River-state flags are internal too. The Cafe retains RegionalRange=6.

UPDATE Buildings SET RegionalRange=6 WHERE BuildingType='BUILDING_CSC_BAKERS_CAFE';

UPDATE Buildings
SET MustPurchase = 1
WHERE BuildingType IN (
    'BUILDING_CSC_BAKERS_RIVER_ACCESS',
    'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',
    'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',
    'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',
    'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',
    'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER'
);

----------------------------------------------------------------------------------------------------------------------------
--	Buildings_XP2
----------------------------------------------------------------------------------------------------------------------------

-- Hidden flags and Service grant records cannot be pillaged. Their active
-- benefits still depend on the functioning chain through the Service gates.

INSERT OR IGNORE INTO Buildings_XP2
        (   BuildingType,                                  Pillage   )
VALUES  (   'BUILDING_CSC_BAKERS_RIVER_ACCESS',            0   ),
        (   'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',         0   ),
        (   'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',         0   ),
        (   'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',         0   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',   0   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',   0   );

----------------------------------------------------------------------------------------------------------------------------
--	BuildingPrereqs
----------------------------------------------------------------------------------------------------------------------------

-- Keep the authored producer ladder and local prerequisites together.
-- The Water Mill additionally needs the local river-access flag.

INSERT OR IGNORE INTO BuildingPrereqs
        (   Building,                           PrereqBuilding   )
VALUES  (   'BUILDING_CSC_BAKERS_WATER_MILL',   'BUILDING_CSC_BAKERS_RIVER_ACCESS'   ),
        (   'BUILDING_CSC_BAKERS_BAKERY',       'BUILDING_CSC_BAKERS_WIND_MILL'   ),
        (   'BUILDING_CSC_BAKERS_BAKERY',       'BUILDING_CSC_BAKERS_WATER_MILL'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'BUILDING_CSC_BAKERS_WIND_MILL'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'BUILDING_CSC_BAKERS_WATER_MILL'   );

----------------------------------------------------------------------------------------------------------------------------
--	MutuallyExclusiveBuildings
----------------------------------------------------------------------------------------------------------------------------

-- Water and Wind Mills are alternatives: building one excludes the other.
-- River/no-river flags select Water Mill eligibility independently of that choice.

INSERT OR IGNORE INTO MutuallyExclusiveBuildings
        (   Building,                           MutuallyExclusiveBuilding   )
VALUES  (   'BUILDING_CSC_BAKERS_WATER_MILL',   'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'   ),
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'BUILDING_CSC_BAKERS_WIND_MILL'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'BUILDING_CSC_BAKERS_WATER_MILL'   );

----------------------------------------------------------------------------------------------------------------------------
--	Building_CitizenYieldChanges
----------------------------------------------------------------------------------------------------------------------------

-- These are real yields from assigned Quarter specialists. They are separate
-- from material purchases, customer sales and conditional Service effects.

INSERT INTO Building_CitizenYieldChanges
        (   BuildingType,                                  YieldType,         YieldChange   )
VALUES  (   'BUILDING_CSC_BAKERS_BAKERY',                  'YIELD_FOOD',      2   ),
        (   'BUILDING_CSC_BAKERS_CAFE',                    'YIELD_FOOD',      1   ),
        (   'BUILDING_CSC_BAKERS_CAFE',                    'YIELD_CULTURE',   1   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',   'YIELD_CULTURE',   2   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',   'YIELD_GOLD',      2   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',   'YIELD_CULTURE',   2   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',   'YIELD_GOLD',      2   );

----------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
----------------------------------------------------------------------------------------------------------------------------

-- Attach supplied-state properties and active Service wrappers to producers.
-- Ordinary exchange attachments are generated from the declarations below.
-- A Service has its own material/civic/customer gates in section 6; those gates
-- do not restrict an ordinary building sale unless its declaration says so.
-- Stage 2: Storekeeper growth at Granaries; Stage 3: Innkeeper Housing at Markets.
-- Stage 4: Tourism, a specialist slot and Great Engineer points at supplied venues.

INSERT INTO BuildingModifiers
        (   BuildingType,                       ModifierId   )
VALUES  (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND'   ),
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY'   ),
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_STAGE_2_GPP_ATTACH_CITY'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_STAGE_2_GPP_ATTACH_CITY'   ),
        (   'BUILDING_CSC_BAKERS_BAKERY',       'MOD_CSC_BAKERS_EXPORT_BAKERY_SUPPLIED_PROP'   ),
        (   'BUILDING_CSC_BAKERS_BAKERY',       'MOD_CSC_BAKERS_STAGE_3_SERVICE_ATTACH_COMHUB'   ),
        (   'BUILDING_CSC_BAKERS_BAKERY',       'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB'   ),
        (   'BUILDING_CSC_BAKERS_BAKERY',       'MOD_CSC_BAKERS_STAGE_3_GPP_ATTACH_COMHUB'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_ENTER'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_WATER'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_ENTER'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_WATER'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_EXPORT_CAFE_SUPPLIED_PROP'   );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_QuarterFlowBuildings
----------------------------------------------------------------------------------------------------------------------------

-- Declare the exact building for each producer stage. Gameplay-derived readers,
-- AI and flow presentation reuse these stage identities.

INSERT OR IGNORE INTO CSC_QuarterFlowBuildings
        (   QuarterKey,   Stage,   BuildingType   )
VALUES  (   'BAKERS',     2,       'BUILDING_CSC_BAKERS_WATER_MILL'   ),
        (   'BAKERS',     2,       'BUILDING_CSC_BAKERS_WIND_MILL'   ),
        (   'BAKERS',     3,       'BUILDING_CSC_BAKERS_BAKERY'   ),
        (   'BAKERS',     4,       'BUILDING_CSC_BAKERS_CAFE'   );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_MaterialTransactions
----------------------------------------------------------------------------------------------------------------------------

-- Identify the producer and the Base/Spec class it purchases. Stage 2 buys Base;
-- Stage 4 buys Spec. Payout legs below state the direction and yield explicitly.

INSERT INTO CSC_MaterialTransactions
        (   TransactionId,                  QuarterKey,   ProducerBuildingType,               MaterialClass   )
VALUES
-- Stage 2
        (   'CSC_BAKERS_WATER_MILL_BASE',   'BAKERS',     'BUILDING_CSC_BAKERS_WATER_MILL',   'CLASS_CSC_BAKERS_BASE'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'BAKERS',     'BUILDING_CSC_BAKERS_WIND_MILL',    'CLASS_CSC_BAKERS_BASE'   ),
-- Stage 4
        (   'CSC_BAKERS_CAFE_SPEC',         'BAKERS',     'BUILDING_CSC_BAKERS_CAFE',         'CLASS_CSC_BAKERS_SPEC'   );

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
        'CSC_BAKERS_WATER_MILL_BASE',
        'INPUT_ORDINARY',
        'PRODUCER',
        'YIELD_FOOD',
        1,
        'REGISTERED_INPUT',
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_BASE',
        'RETURN_PRODUCTION_ORDINARY',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        1,
        'ANY_PLAYER_IMPROVEMENT',
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_BASE',
        'INPUT_ORDINARY',
        'PRODUCER',
        'YIELD_FOOD',
        1,
        'REGISTERED_INPUT',
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_BASE',
        'RETURN_PRODUCTION_ORDINARY',
        'IMPROVEMENT',
        'YIELD_PRODUCTION',
        1,
        'ANY_PLAYER_IMPROVEMENT',
        NULL
    ),
-- Stage 4
    (
        'CSC_BAKERS_CAFE_SPEC',
        'INPUT_ORDINARY',
        'PRODUCER',
        'YIELD_FOOD',
        1,
        'REGISTERED_INPUT',
        NULL
    ),
    (
        'CSC_BAKERS_CAFE_SPEC',
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
        'CSC_BAKERS_WATER_MILL_GRANARY',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WATER_MILL',
        'BUILDING_GRANARY',
        'ADJACENT_OWNED',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_GRANARY',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WIND_MILL',
        'BUILDING_GRANARY',
        'ADJACENT_OWNED',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
-- Stage 3
    (
        'CSC_BAKERS_BAKERY_MARKET',
        'BAKERS',
        'BUILDING_CSC_BAKERS_BAKERY',
        'BUILDING_MARKET',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION',
        0.101,
        NULL,
        0,
        'CSC_BAKERS_STAGE_3_MARKET_CUSTOMER_POP'
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_BAKERY',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WATER_MILL',
        'BUILDING_CSC_BAKERS_BAKERY',
        'SAME_CITY',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_BAKERY',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WIND_MILL',
        'BUILDING_CSC_BAKERS_BAKERY',
        'SAME_CITY',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
-- Stage 4
    (
        'CSC_BAKERS_CAFE_ZOO',
        'BAKERS',
        'BUILDING_CSC_BAKERS_CAFE',
        'BUILDING_ZOO',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        0,
        NULL
    ),
    (
        'CSC_BAKERS_CAFE_FERRIS_WHEEL',
        'BAKERS',
        'BUILDING_CSC_BAKERS_CAFE',
        'BUILDING_FERRIS_WHEEL',
        'ADJACENT_OWNED',
        'PARTNER_POPULATION_STEPS',
        1,
        5,
        0,
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_CAFE',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WATER_MILL',
        'BUILDING_CSC_BAKERS_CAFE',
        'SAME_CITY',
        'FIXED',
        1,
        NULL,
        0,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_CAFE',
        'BAKERS',
        'BUILDING_CSC_BAKERS_WIND_MILL',
        'BUILDING_CSC_BAKERS_CAFE',
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
        (   TransactionId,                               LegKey,                Recipient,   YieldType,            AmountPerUnit,   AmountProperty   )
VALUES
-- Stage 2
        (   'CSC_BAKERS_WATER_MILL_GRANARY',             'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WATER_MILL_GRANARY',             'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_GRANARY',              'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_GRANARY',              'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
-- Stage 3
        (   'CSC_BAKERS_BAKERY_MARKET',                  'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_BAKERS_STAGE_3_MARKET_RETURN_AMOUNT_Q8'   ),
        (   'CSC_BAKERS_BAKERY_MARKET',                  'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               'CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT_Q8'   ),
        (   'CSC_BAKERS_WATER_MILL_CSC_BAKERS_BAKERY',   'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WATER_MILL_CSC_BAKERS_BAKERY',   'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_CSC_BAKERS_BAKERY',    'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_CSC_BAKERS_BAKERY',    'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
-- Stage 4
        (   'CSC_BAKERS_CAFE_ZOO',                       'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_BAKERS_STAGE_4_CAFE_RETURN'   ),
        (   'CSC_BAKERS_CAFE_ZOO',                       'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_BAKERS_STAGE_4_ZOO_CULTURE_RETURN'   ),
        (   'CSC_BAKERS_CAFE_FERRIS_WHEEL',              'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               'CSC_BAKERS_STAGE_4_CAFE_RETURN'   ),
        (   'CSC_BAKERS_CAFE_FERRIS_WHEEL',              'PARTNER_RETURN',      'PARTNER',   'YIELD_CULTURE',      1,               'CSC_BAKERS_STAGE_4_FERRIS_CULTURE_RETURN'   ),
        (   'CSC_BAKERS_WATER_MILL_CSC_BAKERS_CAFE',     'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WATER_MILL_CSC_BAKERS_CAFE',     'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_CSC_BAKERS_CAFE',      'PARTNER_RETURN',      'PARTNER',   'YIELD_FOOD',         1,               NULL   ),
        (   'CSC_BAKERS_WIND_MILL_CSC_BAKERS_CAFE',      'SOURCE_PRODUCTION',   'SOURCE',    'YIELD_PRODUCTION',   1,               NULL   );

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
        'BAKERS_BAKERY',
        'BAKERS',
        'BUILDING_CSC_BAKERS_BAKERY',
        'MOD_CSC_BAKERS_EXPORT_BAKERY_SUPPLIED_PROP',
        0,
        'ImportConsumerRoute',
        'ExportBakeryRoute',
        'CSC_BAKERS_IMPORT_CONSUMER_ROUTE',
        'CSC_BAKERS_EXPORT_BAKERY_ROUTE'
    ),
    (
        'BAKERS_CAFE',
        'BAKERS',
        'BUILDING_CSC_BAKERS_CAFE',
        'MOD_CSC_BAKERS_EXPORT_CAFE_SUPPLIED_PROP',
        0,
        'ImportSpecialtyRoute',
        'ExportCafeRoute',
        'CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',
        'CSC_BAKERS_EXPORT_CAFE_ROUTE'
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
        (   TransactionId,                    LegKey,                ModifierPrefix,                                                              RequirementSetPrefix,                                     BindingKind   )
VALUES  (   'CSC_BAKERS_BAKERY_MARKET',       'SOURCE_PRODUCTION',   'MOD_CSC_BAKERS_MARKET_RETURN_PROD_AMOUNT_BIT_',                             'REQSET_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_',            'CITY_RATE_BITS'   ),
        (   'CSC_BAKERS_BAKERY_MARKET',       'PARTNER_RETURN',      'MOD_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_',                                    'REQSET_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_',              'CITY_RATE_BITS'   ),
        (   'CSC_BAKERS_CAFE_ZOO',            'SOURCE_PRODUCTION',   'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_PRODUCTION_BIT_',                        'REQSET_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_',             'BUILDING_STACK_BITS'   ),
        (   'CSC_BAKERS_CAFE_ZOO',            'PARTNER_RETURN',      'MOD_CSC_BAKERS_STAGE_4_ZOO_CULTURE_RETURN_BUILDING_ZOO_BIT_',               'REQSET_CSC_BAKERS_STAGE_4_ZOO_CULTURE_RETURN_BIT_',      'BUILDING_STACK_BITS'   ),
        (   'CSC_BAKERS_CAFE_FERRIS_WHEEL',   'SOURCE_PRODUCTION',   'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_PRODUCTION_BIT_',                        'REQSET_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_',             'BUILDING_STACK_BITS'   ),
        (   'CSC_BAKERS_CAFE_FERRIS_WHEEL',   'PARTNER_RETURN',      'MOD_CSC_BAKERS_STAGE_4_FERRIS_CULTURE_RETURN_BUILDING_FERRIS_WHEEL_BIT_',   'REQSET_CSC_BAKERS_STAGE_4_FERRIS_CULTURE_RETURN_BIT_',   'BUILDING_STACK_BITS'   );

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
        'CSC_BAKERS_WATER_MILL_GRANARY',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',
        'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',
        'REQ_CSC_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_DISTRICT_IS_CITY_CENTER',
        'REQ_CSC_CITY_HAS_GRANARY'
    ),
    (
        'CSC_BAKERS_WATER_MILL_GRANARY',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER_PROD',
        'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
        'REQSET_CSC_ADJ_BAKERS_QUARTER',
        'REQ_CSC_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_BAKERY',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_BAKERY',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
        'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_CAFE',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FOOD_TO_CAFE',
        'MOD_CSC_BAKERS_FOOD_TO_CAFE',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WATER_MILL_CSC_BAKERS_CAFE',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
        'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_GRANARY',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',
        'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',
        'REQ_CSC_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_DISTRICT_IS_CITY_CENTER',
        'REQ_CSC_CITY_HAS_GRANARY'
    ),
    (
        'CSC_BAKERS_WIND_MILL_GRANARY',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND_PROD',
        'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',
        'REQSET_CSC_ADJ_BAKERS_QUARTER',
        'REQ_CSC_PLOT_ADJ_TO_OWNER',
        'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_BAKERY',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',
        'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_BAKERY',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',
        'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_CAFE',
        'PARTNER_RETURN',
        'SOURCE',
        'MOD_CSC_BAKERS_FOOD_TO_CAFE',
        'MOD_CSC_BAKERS_FOOD_TO_CAFE',
        NULL,
        NULL,
        NULL,
        NULL
    ),
    (
        'CSC_BAKERS_WIND_MILL_CSC_BAKERS_CAFE',
        'SOURCE_PRODUCTION',
        'PARTNER',
        'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',
        'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',
        NULL,
        NULL,
        NULL,
        NULL
    );

INSERT INTO CSC_MaterialTransactionBindings
        (   TransactionId,                  LegKey,                         RootModifierId,                                           ChildModifierId,                                       OwnerRequirementSetId,               SubjectRequirementSetId   )
VALUES  (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_ORDINARY',               'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER',   'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WATER_MILL',   'REQSET_CSC_BAKERS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'RETURN_PRODUCTION_ORDINARY',   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE_PROD',     'MOD_CSC_ALL_PROD_TO_PLOT',                            NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_ORDINARY',               'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND',    'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WIND_MILL',    'REQSET_CSC_BAKERS_PLOT_HAS_BASE',   'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'RETURN_PRODUCTION_ORDINARY',   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE_PROD',     'MOD_CSC_ALL_PROD_TO_PLOT',                            NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_ORDINARY',               'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER',         'MOD_CSC_BAKERS_FOOD_TO_CAFE',                         'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',   'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'RETURN_PRODUCTION_ORDINARY',   'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC_PROD',           'MOD_CSC_ALL_PROD_TO_PLOT',                            NULL,                                'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC'   );

INSERT INTO CSC_MaterialTransactionGateBindings
        (   TransactionId,                  LegKey,                         RequirementSetId,                        RequirementId,                             GateRole   )
VALUES  (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_ORDINARY',               'REQSET_CSC_BAKERS_PLOT_HAS_BASE',       'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_ORDINARY',               'REQSET_CSC_ADJ_BAKERS_QUARTER',         'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'INPUT_ORDINARY',               'REQSET_CSC_ADJ_BAKERS_QUARTER',         'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WATER_MILL_BASE',   'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_ORDINARY',               'REQSET_CSC_BAKERS_PLOT_HAS_BASE',       'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_ORDINARY',               'REQSET_CSC_ADJ_BAKERS_QUARTER',         'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'INPUT_ORDINARY',               'REQSET_CSC_ADJ_BAKERS_QUARTER',         'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_WIND_MILL_BASE',    'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE',   'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_ORDINARY',               'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',       'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_ORDINARY',               'REQSET_CSC_ADJ_BAKERS_QUARTER',         'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',      'QUARTER_TYPE'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'INPUT_ORDINARY',               'REQSET_CSC_ADJ_BAKERS_QUARTER',         'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC',   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC',   'MATERIAL_TAG'   ),
        (   'CSC_BAKERS_CAFE_SPEC',         'RETURN_PRODUCTION_ORDINARY',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC',   'REQ_CSC_PLOT_ADJ_TO_OWNER',               'ADJACENCY'   );

INSERT INTO CSC_TradeRoutePayoutBindings
        (   ChannelId,         LegKey,                Recipient,       ModifierId   )
VALUES  (   'BAKERS_BAKERY',   'IMPORT_YIELD',        'ORIGIN',        'MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD'   ),
        (   'BAKERS_BAKERY',   'IMPORT_AMENITY',      'ORIGIN',        'MOD_CSC_BAKERS_IMPORT_CONSUMER_AMENITY'   ),
        (   'BAKERS_BAKERY',   'EXPORT_PRODUCTION',   'DESTINATION',   'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION'   ),
        (   'BAKERS_CAFE',     'IMPORT_YIELD',        'ORIGIN',        'MOD_CSC_BAKERS_IMPORT_SPECIALTY_FOOD'   ),
        (   'BAKERS_CAFE',     'IMPORT_AMENITY',      'ORIGIN',        'MOD_CSC_BAKERS_IMPORT_SPECIALTY_AMENITY'   ),
        (   'BAKERS_CAFE',     'EXPORT_PRODUCTION',   'DESTINATION',   'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION'   );

----------------------------------------------------------------------------------------------------------------------------
--	LegacyVenueIdentities
----------------------------------------------------------------------------------------------------------------------------

-- Retain Cafe property-consumer branch names used by native effects below.
-- This helper supplies identities only; section 5 owns actual venues and rates.
-- Do not expand unique buildings here: native BUILDING_YIELD_CHANGE inheritance
-- already handles them and extra consumers would pay twice.

DROP TABLE IF EXISTS CSC_BakersStage4CultureBuildings;

CREATE TEMPORARY TABLE CSC_BakersStage4CultureBuildings
		(	Branch TEXT NOT NULL,
			BuildingType TEXT NOT NULL,
			PRIMARY KEY (Branch, BuildingType)	);

INSERT OR IGNORE INTO CSC_BakersStage4CultureBuildings
        (   Branch,     BuildingType   )
VALUES  (   'ZOO',      'BUILDING_ZOO'   ),
        (   'FERRIS',   'BUILDING_FERRIS_WHEEL'   );

INSERT OR IGNORE INTO CSC_BakersStage4CultureBuildings
        (   Branch,   BuildingType   )
SELECT	'CONSERVATORY',				'BUILDING_LEU_CONSERVATORY'
WHERE EXISTS (SELECT 1 FROM Buildings WHERE BuildingType = 'BUILDING_LEU_CONSERVATORY');

----------------------------------------------------------------------------------------------------------------------------
--	DistrictModifiers
----------------------------------------------------------------------------------------------------------------------------

-- Lua aggregates ordinary sales and routes before publishing city-center bits.
-- Attach each aggregate consumer once per receiving city, so multiple producers
-- do not multiply an already summed payment. Route bits use whole counts; Stage 3
-- amounts use Q8 rates, while Stage 4 uses whole per-customer population stacks.

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,             ModifierId   )
VALUES  (   'DISTRICT_CITY_CENTER',   'MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_BAKERS_IMPORT_CONSUMER_AMENITY'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_FOOD'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_AMENITY'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION'   );

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_MARKET_RETURN_PROD_AMOUNT_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_PRODUCTION_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_' || BuildingType || '_BIT_' || Bit
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION_BIT_' || Bit
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION_BIT_' || Bit
FROM CSC_RouteStackBits;

----------------------------------------------------------------------------------------------------------------------------
--	Modifiers
----------------------------------------------------------------------------------------------------------------------------

-- Wrappers choose eligible recipients; leaves deliver the effect. Service
-- grants, active benefits, supplied properties and ordinary amount consumers keep
-- their separate identities. Generated ordinary exchange roots/leaves come from
-- the shared compiler and the bindings above.

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                             ModifierType,                                            OwnerRequirementSetId,                             SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_BAKERS_RIVER_ACCESS_FLAG',                     'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                              'REQSET_CSC_PLOT_ADJ_TO_RIVER'   ),
        (   'MOD_CSC_BAKERS_NO_RIVER_ACCESS_FLAG',                  'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                              'REQSET_CSC_PLOT_NOT_ADJ_TO_RIVER'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',      'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER',           'MODIFIER_SINGLE_CITY_ADJUST_CITY_GROWTH',               NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',       'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND',            'MODIFIER_SINGLE_CITY_ADJUST_CITY_GROWTH',               NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY',           'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT',                 'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_2_GPP_ATTACH_CITY',               'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'   ),
        (   'MOD_CSC_BAKERS_STAGE_2+4_GPP',                         'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',   NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_SUPPLIED_PROP',           'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                  'REQSET_CSC_BAKERS_EXPORT_BAKERY_SUPPLY_PREREQ',   NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_3_SERVICE_ATTACH_COMHUB',         'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                'REQSET_CSC_ADJ_MARKET'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_SERVICE_GRANT',                 'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',          'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                'REQSET_CSC_ADJ_MARKET'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING',                'MODIFIER_SINGLE_CITY_ADJUST_BUILDING_HOUSING',          NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_3_GPP_ATTACH_COMHUB',             'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                'REQSET_CSC_ADJ_MARKET'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_GPP',                           'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',   NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',                   'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',                'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_PRODUCTION_TO_CAFE',                    'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_SUPPLIED_PROP',             'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                  'REQSET_CSC_BAKERS_EXPORT_CAFE_SUPPLY_PREREQ',     NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',   'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER',          'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',        NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',      'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_WATER_PARK_FERRIS'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER',          'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',        NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_ENTER',          'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER',           'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_WATER',          'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_WATER_PARK_FERRIS'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER',           'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_ENTER',              'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_WATER',              'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_WATER_PARK_FERRIS'   ),
        (   'MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD',                  'MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE',              NULL,                                              'REQSET_CSC_BAKERS_IMPORT_CONSUMER_ROUTE_BIT_1'   ),
        (   'MOD_CSC_BAKERS_IMPORT_CONSUMER_AMENITY',               'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',        NULL,                                              'REQSET_CSC_BAKERS_IMPORT_CONSUMER_ROUTE_BIT_1'   ),
        (   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_FOOD',                 'MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE',              NULL,                                              'REQSET_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE_BIT_1'   ),
        (   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_AMENITY',              'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',        NULL,                                              'REQSET_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE_BIT_1'   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION',              'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                              'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1'   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION',                'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                              'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1'   );

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT	'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION_BIT_' || Bit,					'MODIFIER_BUILDING_YIELD_CHANGE',							NULL,					'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT	'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION_BIT_' || Bit,					'MODIFIER_BUILDING_YIELD_CHANGE',							NULL,					'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT	'MOD_CSC_BAKERS_MARKET_RETURN_PROD_AMOUNT_BIT_' || Bit,					'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',	NULL,					'REQSET_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT	'MOD_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,						'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',	NULL,					'REQSET_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT	'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_PRODUCTION_BIT_' || Bit,			'MODIFIER_BUILDING_YIELD_CHANGE',							NULL,					'REQSET_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT	'MOD_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_' || BuildingType || '_BIT_' || Bit,
		'MODIFIER_BUILDING_YIELD_CHANGE',
		NULL,
		'REQSET_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_BIT_' || Bit
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;

----------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
----------------------------------------------------------------------------------------------------------------------------

-- Connect wrappers to leaves and supply yield, property or benefit parameters.
-- The shared compiler refreshes ordinary transaction amounts from section 5;
-- the bit consumers below implement the encoded amount.

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                                             Name,                     Value   )
VALUES  (   'MOD_CSC_BAKERS_RIVER_ACCESS_FLAG',                     'BuildingType',           'BUILDING_CSC_BAKERS_RIVER_ACCESS'   ),
        (   'MOD_CSC_BAKERS_NO_RIVER_ACCESS_FLAG',                  'BuildingType',           'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',      'ModifierId',             'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER',           'Amount',                 10   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',       'ModifierId',             'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND',            'Amount',                 10   ),
        (   'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY',           'ModifierId',             'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT',                 'BuildingType',           'BUILDING_CSC_BAKERS_STAGE_2_SERVICE'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_GPP_ATTACH_CITY',               'ModifierId',             'MOD_CSC_BAKERS_STAGE_2+4_GPP'   ),
        (   'MOD_CSC_BAKERS_STAGE_2+4_GPP',                         'GreatPersonClassType',   'GREAT_PERSON_CLASS_ENGINEER'   ),
        (   'MOD_CSC_BAKERS_STAGE_2+4_GPP',                         'Amount',                 '1'   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_SUPPLIED_PROP',           'Key',                    'CSC_BAKERS_BAKERY_SUPPLIED'   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_SUPPLIED_PROP',           'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_STAGE_3_SERVICE_ATTACH_COMHUB',         'ModifierId',             'MOD_CSC_BAKERS_STAGE_3_SERVICE_GRANT'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_SERVICE_GRANT',                 'BuildingType',           'BUILDING_CSC_BAKERS_STAGE_3_SERVICE'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',          'ModifierId',             'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING',                'Amount',                 2   ),
        (   'MOD_CSC_BAKERS_STAGE_3_GPP_ATTACH_COMHUB',             'ModifierId',             'MOD_CSC_BAKERS_STAGE_3_GPP'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_GPP',                           'GreatPersonClassType',   'GREAT_PERSON_CLASS_MERCHANT'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_GPP',                           'Amount',                 '1'   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',                   'BuildingType',           'BUILDING_ZOO'   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',                   'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',                   'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',                'BuildingType',           'BUILDING_FERRIS_WHEEL'   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',                'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',                'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_PRODUCTION_TO_CAFE',                    'BuildingType',           'BUILDING_CSC_BAKERS_CAFE'   ),
        (   'MOD_CSC_BAKERS_PRODUCTION_TO_CAFE',                    'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_BAKERS_PRODUCTION_TO_CAFE',                    'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',   'ModifierId',             'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER',          'Amount',                 2   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',      'ModifierId',             'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER',          'Amount',                 2   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_SUPPLIED_PROP',             'Key',                    'CSC_BAKERS_CAFE_SUPPLIED'   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_SUPPLIED_PROP',             'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_ENTER',          'ModifierId',             'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER',           'BuildingType',           'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_WATER',          'ModifierId',             'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER',           'BuildingType',           'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_ENTER',              'ModifierId',             'MOD_CSC_BAKERS_STAGE_2+4_GPP'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_WATER',              'ModifierId',             'MOD_CSC_BAKERS_STAGE_2+4_GPP'   ),
        (   'MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD',                  'YieldType',              'YIELD_FOOD'   ),
        (   'MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD',                  'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_IMPORT_CONSUMER_AMENITY',               'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_FOOD',                 'YieldType',              'YIELD_FOOD'   ),
        (   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_FOOD',                 'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_AMENITY',              'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION',              'BuildingType',           'BUILDING_CSC_BAKERS_BAKERY'   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION',              'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION',              'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION',                'BuildingType',           'BUILDING_CSC_BAKERS_CAFE'   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION',                'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION',                'Amount',                 1   );

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION_BIT_' || Bit,					'BuildingType',				'BUILDING_CSC_BAKERS_BAKERY'
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION_BIT_' || Bit,					'YieldType',				'YIELD_PRODUCTION'
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION_BIT_' || Bit,					'Amount',					Bit
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION_BIT_' || Bit,					'BuildingType',				'BUILDING_CSC_BAKERS_CAFE'
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION_BIT_' || Bit,					'YieldType',				'YIELD_PRODUCTION'
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION_BIT_' || Bit,					'Amount',					Bit
FROM CSC_RouteStackBits;

----------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
----------------------------------------------------------------------------------------------------------------------------

-- Name the AND/OR gates referenced by native effects. Service gates combine
-- their unlock, functioning supplier/producer and appropriate customer conditions.
-- Ordinary transaction eligibility remains distinct from Service prerequisites.

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,                                   RequirementSetType   )
VALUES  (   'REQSET_CSC_PLOT_ADJ_TO_RIVER',                     'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_PLOT_NOT_ADJ_TO_RIVER',                 'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                 'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_ADJ_MARKET',                            'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_ADJ_BAKERY_STAGE_3_RETURN',             'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                 'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX',             'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK',                        'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                 'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY',   'REQUIREMENTSET_TEST_ANY'   ),
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',         'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK_FERRIS',                 'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_SUPPLY_PREREQ',    'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_SUPPLY_PREREQ',      'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_IMPORT_CONSUMER_ROUTE',          'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',         'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE',            'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE',              'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1',      'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1',        'REQUIREMENTSET_TEST_ALL'   );

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT	'REQSET_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit,		'REQUIREMENTSET_TEST_ALL'
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT	'REQSET_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,			'REQUIREMENTSET_TEST_ALL'
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT	'REQSET_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_' || Bit,		'REQUIREMENTSET_TEST_ALL'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT	'REQSET_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_BIT_' || Bit,	'REQUIREMENTSET_TEST_ALL'
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT	'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_' || Bit,		'REQUIREMENTSET_TEST_ALL'
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT	'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_' || Bit,			'REQUIREMENTSET_TEST_ALL'
FROM CSC_RouteStackBits;

----------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
----------------------------------------------------------------------------------------------------------------------------

-- Compose each named gate from its requirement IDs. Bit gates select one
-- published amount bit; Service gates preserve full gameplay eligibility.

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,                                   RequirementId   )
VALUES  (   'REQSET_CSC_PLOT_ADJ_TO_RIVER',                     'REQ_CSC_PLOT_ADJ_TO_RIVER'   ),
        (   'REQSET_CSC_PLOT_NOT_ADJ_TO_RIVER',                 'REQ_CSC_PLOT_NOT_ADJ_TO_RIVER'   ),
        (   'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                 'REQ_CSC_STAGE_2_EFFECT_TECH_OR_CIVIC'   ),
        (   'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER'   ),
        (   'REQSET_CSC_ADJ_MARKET',                            'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_ADJ_MARKET',                            'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB'   ),
        (   'REQSET_CSC_ADJ_MARKET',                            'REQ_CSC_CITY_HAS_MARKET'   ),
        (   'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                 'REQ_CSC_STAGE_3_EFFECT_TECH_OR_CIVIC'   ),
        (   'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER'   ),
        (   'REQSET_CSC_ADJ_BAKERY_STAGE_3_RETURN',             'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'   ),
        (   'REQSET_CSC_ADJ_BAKERY_STAGE_3_RETURN',             'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_ADJ_BAKERY_STAGE_3_RETURN',             'REQ_CSC_CITY_HAS_BAKERY'   ),
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX',             'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX',             'REQ_CSC_DISTRICT_IS_ENTERTAINMENT_COMPLEX'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK',                        'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK',                        'REQ_CSC_DISTRICT_IS_WATER_PARK'   ),
        (   'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                 'REQ_CSC_STAGE_4_EFFECT_TECH_OR_CIVIC'   ),
        (   'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC'   ),
        (   'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY'   ),
        (   'REQSET_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY',   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_ENTER_CUSTOMER'   ),
        (   'REQSET_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY',   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_WATER_CUSTOMER'   ),
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',         'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX'   ),
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',         'REQ_CSC_CITY_HAS_ZOO'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK_FERRIS',                 'REQ_CSC_ADJ_WATER_PARK'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK_FERRIS',                 'REQ_CSC_CITY_HAS_FERRIS'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_SUPPLY_PREREQ',    'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_SUPPLY_PREREQ',      'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_SUPPLY_PREREQ',      'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC'   ),
        (   'REQSET_CSC_BAKERS_IMPORT_CONSUMER_ROUTE',          'REQ_CSC_BAKERS_IMPORT_CONSUMER_ROUTE'   ),
        (   'REQSET_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',         'REQ_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE',            'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE',              'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1',      'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1',        'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1'   );

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT	'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_' || Bit,		'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT	'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_' || Bit,			'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT	'REQSET_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit,		'REQ_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT	'REQSET_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,			'REQ_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT	'REQSET_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_' || Bit,		'REQ_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT	'REQSET_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_BIT_' || Bit,
		'REQ_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_BIT_' || Bit
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;

----------------------------------------------------------------------------------------------------------------------------
--	Requirements
----------------------------------------------------------------------------------------------------------------------------

-- Declare the native test and inversion for each condition. Ownership,
-- adjacency, building, supply and unlock tests are parameterized below.

INSERT OR IGNORE INTO Requirements
        (   RequirementId,                                       RequirementType,                            Inverse   )
VALUES  (   'REQ_CSC_PLOT_ADJ_TO_RIVER',                         'REQUIREMENT_PLOT_ADJACENT_TO_RIVER',       0   ),
        (   'REQ_CSC_PLOT_NOT_ADJ_TO_RIVER',                     'REQUIREMENT_PLOT_ADJACENT_TO_RIVER',       1   ),
        (   'REQ_CSC_STAGE_2_EFFECT_TECH_OR_CIVIC',              'REQUIREMENT_PLAYER_HAS_CIVIC',             0   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB',                'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_CITY_HAS_MARKET',                           'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_CITY_HAS_BAKERY',                           'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_STAGE_3_EFFECT_TECH_OR_CIVIC',              'REQUIREMENT_PLAYER_HAS_CIVIC',             0   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_DISTRICT_IS_ENTERTAINMENT_COMPLEX',         'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_DISTRICT_IS_WATER_PARK',                    'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_STAGE_4_EFFECT_TECH_OR_CIVIC',              'REQUIREMENT_PLAYER_HAS_CIVIC',             0   ),
        (   'REQ_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY',       'REQUIREMENT_REQUIREMENTSET_IS_MET',        0   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_ENTER_CUSTOMER',     'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_WATER_CUSTOMER',     'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX',                 'REQUIREMENT_REQUIREMENTSET_IS_MET',        0   ),
        (   'REQ_CSC_CITY_HAS_ZOO',                              'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_ADJ_WATER_PARK',                            'REQUIREMENT_REQUIREMENTSET_IS_MET',        0   ),
        (   'REQ_CSC_CITY_HAS_FERRIS',                           'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_BAKERS_IMPORT_CONSUMER_ROUTE',              'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',             'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE',                'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE',                  'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1',          'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1',            'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_PLOT_HAS_ANY_IMPROVEMENT',                  'REQUIREMENT_PLOT_HAS_ANY_IMPROVEMENT',     0   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',         'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   );

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT	'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_' || Bit,					'REQUIREMENT_PLOT_PROPERTY_MATCHES',			0
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT	'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_' || Bit,						'REQUIREMENT_PLOT_PROPERTY_MATCHES',			0
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT	'REQ_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit,					'REQUIREMENT_PLOT_PROPERTY_MATCHES',			0
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT	'REQ_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,					'REQUIREMENT_PLOT_PROPERTY_MATCHES',			0
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT	'REQ_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_' || Bit,					'REQUIREMENT_PLOT_PROPERTY_MATCHES',			0
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT	'REQ_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_BIT_' || Bit,	'REQUIREMENT_PLOT_PROPERTY_MATCHES',		0
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;

----------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
----------------------------------------------------------------------------------------------------------------------------

-- Supply exact classes, building/district types, technologies/civics and property
-- thresholds for the tests above. This is the detailed wiring behind the readable
-- building/transaction declarations, not another source of economic terms.

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,                                       Name,                 Value   )
VALUES  (   'REQ_CSC_STAGE_2_EFFECT_TECH_OR_CIVIC',              'CivicType',          'CIVIC_FEUDALISM'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'CollectionType',     'COLLECTION_PLAYER_DISTRICTS'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'Count',              1   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'RequirementSetId',   'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'   ),
        (   'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB',                'DistrictType',       'DISTRICT_COMMERCIAL_HUB'   ),
        (   'REQ_CSC_CITY_HAS_MARKET',                           'BuildingType',       'BUILDING_MARKET'   ),
        (   'REQ_CSC_CITY_HAS_BAKERY',                           'BuildingType',       'BUILDING_CSC_BAKERS_BAKERY'   ),
        (   'REQ_CSC_STAGE_3_EFFECT_TECH_OR_CIVIC',              'CivicType',          'CIVIC_MEDIEVAL_FAIRES'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'CollectionType',     'COLLECTION_PLAYER_DISTRICTS'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'Count',              1   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'RequirementSetId',   'REQSET_CSC_ADJ_MARKET'   ),
        (   'REQ_CSC_DISTRICT_IS_ENTERTAINMENT_COMPLEX',         'DistrictType',       'DISTRICT_ENTERTAINMENT_COMPLEX'   ),
        (   'REQ_CSC_DISTRICT_IS_WATER_PARK',                    'DistrictType',       'DISTRICT_WATER_ENTERTAINMENT_COMPLEX'   ),
        (   'REQ_CSC_STAGE_4_EFFECT_TECH_OR_CIVIC',              'CivicType',          'CIVIC_URBANIZATION'   ),
        (   'REQ_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY',       'RequirementSetId',   'REQSET_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_ENTER_CUSTOMER',     'CollectionType',     'COLLECTION_PLAYER_DISTRICTS'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_ENTER_CUSTOMER',     'Count',              1   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_ENTER_CUSTOMER',     'RequirementSetId',   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_WATER_CUSTOMER',     'CollectionType',     'COLLECTION_PLAYER_DISTRICTS'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_WATER_CUSTOMER',     'Count',              1   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_WATER_CUSTOMER',     'RequirementSetId',   'REQSET_CSC_ADJ_WATER_PARK_FERRIS'   ),
        (   'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX',                 'RequirementSetId',   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX'   ),
        (   'REQ_CSC_CITY_HAS_ZOO',                              'BuildingType',       'BUILDING_ZOO'   ),
        (   'REQ_CSC_ADJ_WATER_PARK',                            'RequirementSetId',   'REQSET_CSC_ADJ_WATER_PARK'   ),
        (   'REQ_CSC_CITY_HAS_FERRIS',                           'BuildingType',       'BUILDING_FERRIS_WHEEL'   ),
        (   'REQ_CSC_BAKERS_IMPORT_CONSUMER_ROUTE',              'PropertyName',       'CSC_BAKERS_IMPORT_CONSUMER_ROUTE'   ),
        (   'REQ_CSC_BAKERS_IMPORT_CONSUMER_ROUTE',              'PropertyMinimum',    1   ),
        (   'REQ_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',             'PropertyName',       'CSC_BAKERS_IMPORT_SPECIALTY_ROUTE'   ),
        (   'REQ_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',             'PropertyMinimum',    1   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE',                'PropertyName',       'CSC_BAKERS_EXPORT_BAKERY_ROUTE'   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE',                'PropertyMinimum',    1   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE',                  'PropertyName',       'CSC_BAKERS_EXPORT_CAFE_ROUTE'   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE',                  'PropertyMinimum',    1   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1',          'PropertyName',       'CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1'   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1',          'PropertyMinimum',    1   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1',            'PropertyName',       'CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1'   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1',            'PropertyMinimum',    1   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',         'CollectionType',     'COLLECTION_PLAYER_IMPROVEMENTS'   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',         'Count',              1   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',         'RequirementSetId',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE'   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'CollectionType',     'COLLECTION_PLAYER_IMPROVEMENTS'   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'Count',              1   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'RequirementSetId',   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC'   );

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_' || Bit,					'PropertyName',					'CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_' || Bit,					'PropertyMinimum',				1
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_' || Bit,						'PropertyName',					'CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_' || Bit,						'PropertyMinimum',				1
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit,					'PropertyName',					'CSC_BAKERS_STAGE_3_MARKET_RETURN_AMOUNT_Q8_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit,					'PropertyMinimum',				1
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,					'PropertyName',					'CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT_Q8_BIT_' || Bit
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,					'PropertyMinimum',				1
FROM CSC_Stage3RateBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_' || Bit,					'PropertyName',					'CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_' || Bit,					'PropertyMinimum',				1
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_BIT_' || Bit,
		'PropertyName',
		'CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_BIT_' || Bit
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_BIT_' || Bit,
		'PropertyMinimum',
		1
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;

----------------------------------------------------------------------------------------------------------------------------
--	RouteImports
----------------------------------------------------------------------------------------------------------------------------

-- Expand the existing origin-side consumers for whole route counts. The route
-- scanner publishes bits; base +1 consumers and these 2/4/8/16 consumers pay the
-- same total without multiplying by producer count. Keep temporary channel/effect
-- setup, all dependent SELECTs and teardown together.

CREATE TEMP TABLE CSC_BakersImportChannels (Channel TEXT PRIMARY KEY);

INSERT INTO CSC_BakersImportChannels
        (   Channel   )
VALUES  (   'CONSUMER'   ),
        (   'SPECIALTY'   );

CREATE TEMP TABLE CSC_BakersImportEffects (Effect TEXT PRIMARY KEY, ModifierType TEXT);

INSERT INTO CSC_BakersImportEffects
        (   Effect,      ModifierType   )
VALUES  (   'FOOD',      'MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE'   ),
        (   'AMENITY',   'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY'   );

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_BAKERS_IMPORT_' || Channel || '_' || Effect || '_BIT_' || Bit
FROM CSC_BakersImportChannels CROSS JOIN CSC_BakersImportEffects CROSS JOIN CSC_RouteStackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_BAKERS_IMPORT_' || Channel || '_' || Effect || '_BIT_' || Bit,
       ModifierType, 'REQSET_CSC_BAKERS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit
FROM CSC_BakersImportChannels CROSS JOIN CSC_BakersImportEffects CROSS JOIN CSC_RouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_BAKERS_IMPORT_' || Channel || '_' || Effect || '_BIT_' || Bit, 'Amount', Bit
FROM CSC_BakersImportChannels CROSS JOIN CSC_BakersImportEffects CROSS JOIN CSC_RouteStackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_BAKERS_IMPORT_' || Channel || '_FOOD_BIT_' || Bit, 'YieldType', 'YIELD_FOOD'
FROM CSC_BakersImportChannels CROSS JOIN CSC_RouteStackBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT 'REQ_CSC_BAKERS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES'
FROM CSC_BakersImportChannels CROSS JOIN (SELECT 1 AS Bit UNION ALL SELECT Bit FROM CSC_RouteStackBits);

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_BAKERS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_BakersImportChannels CROSS JOIN (SELECT 1 AS Bit UNION ALL SELECT Bit FROM CSC_RouteStackBits);

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_BAKERS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit,
       'REQ_CSC_BAKERS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit
FROM CSC_BakersImportChannels CROSS JOIN (SELECT 1 AS Bit UNION ALL SELECT Bit FROM CSC_RouteStackBits);

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_BAKERS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit,
       'PropertyName', 'CSC_BAKERS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit
FROM CSC_BakersImportChannels CROSS JOIN (SELECT 1 AS Bit UNION ALL SELECT Bit FROM CSC_RouteStackBits);

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_BAKERS_IMPORT_' || Channel || '_ROUTE_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_BakersImportChannels CROSS JOIN (SELECT 1 AS Bit UNION ALL SELECT Bit FROM CSC_RouteStackBits);

DROP TABLE CSC_BakersImportEffects;

DROP TABLE CSC_BakersImportChannels;



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
	WHEN Description IS NULL OR Description='' THEN 'LOC_CSC_BAKERS_STAGE_2_EFFECT'
	ELSE '{' || Description || '}' || '[NEWLINE][NEWLINE]{LOC_CSC_BAKERS_STAGE_2_EFFECT}'
END
WHERE BuildingType='BUILDING_GRANARY'
OR BuildingType IN (SELECT CivUniqueBuildingType FROM BuildingReplaces WHERE ReplacesBuildingType='BUILDING_GRANARY');

UPDATE Buildings
SET Description = CASE
	WHEN Description IS NULL OR Description='' THEN 'LOC_CSC_BAKERS_STAGE_3_EFFECT'
	ELSE '{' || Description || '}' || '{LOC_CSC_BAKERS_STAGE_3_EFFECT}'
END
WHERE BuildingType='BUILDING_MARKET'
OR BuildingType IN (SELECT CivUniqueBuildingType FROM BuildingReplaces WHERE ReplacesBuildingType='BUILDING_MARKET');

UPDATE Buildings
SET Description = CASE
	WHEN Description IS NULL OR Description='' THEN 'LOC_CSC_BAKERS_STAGE_4_EFFECT_ENTER'
	ELSE '{' || Description || '}' || '{LOC_CSC_BAKERS_STAGE_4_EFFECT_ENTER}'
END
WHERE BuildingType='BUILDING_ZOO'
OR BuildingType IN (SELECT CivUniqueBuildingType FROM BuildingReplaces WHERE ReplacesBuildingType='BUILDING_ZOO');

UPDATE Buildings
SET Description = CASE
	WHEN Description IS NULL OR Description='' THEN 'LOC_CSC_BAKERS_STAGE_4_EFFECT_WATER'
	ELSE '{' || Description || '}' || '{LOC_CSC_BAKERS_STAGE_4_EFFECT_WATER}'
END
WHERE BuildingType='BUILDING_FERRIS_WHEEL'
OR BuildingType IN (SELECT CivUniqueBuildingType FROM BuildingReplaces WHERE ReplacesBuildingType='BUILDING_FERRIS_WHEEL');

UPDATE Civics SET Description = '{LOC_CIVIC_FEUDALISM_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_2_CIVIC}' WHERE CivicType = 'CIVIC_FEUDALISM';

UPDATE Civics SET Description = '{LOC_CSC_BAKERS_STAGE_3_CIVIC}' WHERE CivicType = 'CIVIC_MEDIEVAL_FAIRES';

UPDATE Civics SET Description = '{LOC_CSC_BAKERS_STAGE_4_CIVIC}' WHERE CivicType = 'CIVIC_URBANIZATION';

----------------------------------------------------------------------------------------------------------------------------
--	CivilopediaPageExcludes
----------------------------------------------------------------------------------------------------------------------------

-- Hide internal river-state flags from the Civilopedia. Their gameplay use is
-- Water Mill eligibility; they are not purchasable player-facing buildings.

INSERT INTO CivilopediaPageExcludes
        (   SectionId,     PageId   )
VALUES  (   'BUILDINGS',   'BUILDING_CSC_BAKERS_RIVER_ACCESS'   ),
        (   'BUILDINGS',   'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'   );

----------------------------------------------------------------------------------------------------------------------------
--	Notifications
----------------------------------------------------------------------------------------------------------------------------

-- Configure the notification identities registered in section 1. Shared Lua
-- observes active benefit wrappers below to report gains, losses and changes.

INSERT INTO Notifications
        (   NotificationType,                             SeverityType,   ExpiresEndOfTurn,   AutoNotify   )
VALUES  (   'NOTIFICATION_CSC_BAKERS_EFFECT_NEW',         'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_INCREASED',   'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_DECREASED',   'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_REMOVED',     'HIGH',         0,                  0   );

----------------------------------------------------------------------------------------------------------------------------
--	CSC_AbilityAttachModifiers
----------------------------------------------------------------------------------------------------------------------------

-- Observe active benefit wrappers rather than hidden Service grants. The shared
-- notification/MCUIS system counts live recipients. Wonder and era-specific
-- branches keep explicit native identities for accurate presentation.

INSERT INTO CSC_AbilityAttachModifiers
        (   ModifierId,                                             AbilityIcon,                                        AbilityIconTarget,                             NotificationQuarter   )
VALUES  (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',      'ICON_BUILDING_CSC_BAKERS_STAGE_2_SERVICE',         'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',         'BAKERS'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',       'ICON_BUILDING_CSC_BAKERS_STAGE_2_SERVICE',         'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',         'BAKERS'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',          'ICON_BUILDING_CSC_BAKERS_STAGE_3_SERVICE',         'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',         'BAKERS'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',   'ICON_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',   'BAKERS'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',      'ICON_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',   'BAKERS'   );

----------------------------------------------------------------------------------------------------------------------------
--	ModifierStrings
----------------------------------------------------------------------------------------------------------------------------

-- Associate benefit leaves with localized preview text. Terms and eligibility
-- stay in gameplay declarations and requirements, not in these strings.

INSERT INTO ModifierStrings
        (   ModifierId,                                      Context,     'Text'   )
VALUES  (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER',    'Preview',   'LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WATER'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND',     'Preview',   'LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WIND'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING',         'Preview',   'LOC_CSC_BAKERS_STAGE_3_EFFECT_DESCRIPTION'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER',   'Preview',   'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_ENTER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER',   'Preview',   'LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_WATER'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT',          'Preview',   'LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_SERVICE_GRANT',          'Preview',   'LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER',    'Preview',   'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER',    'Preview',   'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME'   );

----------------------------------------------------------------------------------------------------------------------------
--	ArtProperties
----------------------------------------------------------------------------------------------------------------------------

-- Reuse the complete Service gate to write an art source property.
-- CSC_ArtProperties.lua mirrors that result into binary art-selection flags;
-- it does not implement another material/civic/customer eligibility calculation.

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                              ModifierType,                             OwnerRequirementSetId,                SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_BAKERS_STAGE_2_PROP',           'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',   'REQSET_CSC_STAGE_2_EFFECT_PREREQ',   NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_3_PROP_HOUSING',   'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',   'REQSET_CSC_STAGE_3_EFFECT_PREREQ',   NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM',   'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',   'REQSET_CSC_STAGE_4_EFFECT_PREREQ',   NULL   );

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                              Name,       Value   )
VALUES  (   'MOD_CSC_BAKERS_STAGE_2_PROP',           'Key',      'CSC_BAKERS_STAGE_2_EFFECT_GROWTH'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_PROP',           'Amount',   1   ),
        (   'MOD_CSC_BAKERS_STAGE_3_PROP_HOUSING',   'Key',      'CSC_BAKERS_STAGE_3_EFFECT_HOUSING'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_PROP_HOUSING',   'Amount',   1   ),
        (   'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM',   'Key',      'CSC_BAKERS_STAGE_4_EFFECT_TOURISM'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM',   'Amount',   1   );

INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,                       ModifierId   )
VALUES  (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_STAGE_2_PROP'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_STAGE_2_PROP'   ),
        (   'BUILDING_CSC_BAKERS_BAKERY',       'MOD_CSC_BAKERS_STAGE_3_PROP_HOUSING'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM'   );
