-- CSC_Q_TAILORS
-- Author: Henno
-- DateCreated: 2026-08-23
--------------------------------------------------------------

-- Reading this Quarter
-- Materials -> Textile Workshop -> Tailor -> Fashion House -> customer Services.
-- Core owns Production/Culture and Services. *_GOLD.sql adds parallel Gold returns;
-- *_MC_MODE.sql adds Industry/Corporation exchanges.
--
-- ATTACH modifiers select recipients; child modifiers deliver the effect. Trace
-- an attachment through Modifiers, ModifierArguments and its requirement sets.
-- Shared Lua calculates population/route amounts, and SQL property consumers pay
-- them. Wonder-hosted Services additionally need Lua for exact-plot placement.
--===========================================================================================================================================================================--
/*	TYPES */
--===========================================================================================================================================================================--

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
        (   'MODIFIER_CSC_TAILORS_SINGLE_CITY_ADJUST_UNIT_TAG_ERA_PRODUCTION',   'KIND_MODIFIER'   );

-- Register the Dockmaster's custom modifier type against the native effect.
-- Types supplies KIND_MODIFIER; DynamicModifiers supplies collection and effect.
-- The per-era/per-unit-family instances are generated below.
INSERT OR IGNORE INTO DynamicModifiers
        (   ModifierType,                                                        CollectionType,       EffectType   )
VALUES  (   'MODIFIER_CSC_TAILORS_SINGLE_CITY_ADJUST_UNIT_TAG_ERA_PRODUCTION',   'COLLECTION_OWNER',   'EFFECT_ADJUST_UNIT_TAG_ERA_PRODUCTION'   );


--===========================================================================================================================================================================--
/*	RESOURCES */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Resource tags are the live BASE/SPEC material mappings, including ModSupport.
-- SALES tags describe customer district families and the yield each receives.
-- These classifications feed adjacency, supply and map/lens readers; they do not
-- by themselves grant a producer building or Service.
INSERT OR IGNORE INTO Tags
        (   Tag,                                    Vocabulary   )
VALUES  (   'CLASS_CSC_TAILORS_BASE',               'RESOURCE_CLASS'   ),
        (   'CLASS_CSC_TAILORS_SPEC',               'RESOURCE_CLASS'   ),
        (   'CLASS_CSC_TAILORS_SALES',              'DISTRICT_CLASS'   ),
        (   'CLASS_CSC_TAILORS_SALES_PRODUCTION',   'DISTRICT_CLASS'   ),
        (   'CLASS_CSC_TAILORS_SALES_CULTURE',      'DISTRICT_CLASS'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC_QuarterMaterialAdjacencyConfig
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- The bundled processor turns these tag rows into Quarter adjacency rules.
-- An empty SourceFilter accepts every resource added to the class; discovery
-- and ownership are evaluated by the shared engine.
INSERT OR IGNORE INTO CSC_QuarterMaterialAdjacencyConfig
        (   QuarterKey,   SourceTag,                  SourceFilter,   YieldType,            YieldChange,   AdjacencyType   )
VALUES  (   'TAILORS',    'CLASS_CSC_TAILORS_BASE',   '',             'YIELD_PRODUCTION',   1,             'FROM_RINGS_TYPETAG_RESOURCE'   ),
        (   'TAILORS',    'CLASS_CSC_TAILORS_SPEC',   '',             'YIELD_PRODUCTION',   1,             'FROM_RINGS_TYPETAG_RESOURCE'   );

-- District adjacency cards double the actual Production/Culture return.
-- These cards double the customer's reciprocal Production/Culture adjacency.
-- The processor handles direct unique districts and gates each extra rule by
-- its actual policy, keeping gameplay and placement previews aligned.
INSERT OR IGNORE INTO CSC_QuarterPolicyAdjacencyConfig
        (   QuarterKey,   DistrictType,                PolicyType   )
VALUES  (   'TAILORS',    'DISTRICT_HARBOR',           'POLICY_NAVAL_INFRASTRUCTURE'   ),
        (   'TAILORS',    'DISTRICT_HARBOR',           'POLICY_ECONOMIC_UNION'   ),
        (   'TAILORS',    'DISTRICT_COMMERCIAL_HUB',   'POLICY_TOWN_CHARTERS'   ),
        (   'TAILORS',    'DISTRICT_COMMERCIAL_HUB',   'POLICY_ECONOMIC_UNION'   ),
        (   'TAILORS',    'DISTRICT_HOLY_SITE',        'POLICY_SCRIPTURE'   ),
        (   'TAILORS',    'DISTRICT_THEATER',          'POLICY_AESTHETICS'   ),
        (   'TAILORS',    'DISTRICT_THEATER',          'POLICY_SPORTS_MEDIA'   );

-- Wonder customers hosted by the Fashion House's Stage 4 Services. Both map
-- planning views highlight their completed Wonder plots as points of sale.
INSERT OR IGNORE INTO CSC_QuarterWonderSales
        (   QuarterKey,   BuildingType   )
VALUES  (   'TAILORS',    'BUILDING_BOLSHOI_THEATRE'   ),
        (   'TAILORS',    'BUILDING_BROADWAY'   ),
        (   'TAILORS',    'BUILDING_SYDNEY_OPERA_HOUSE'   );

-- Each Stage 3 customer family is a separate sale, even when its Market and
-- Temple belong to the same city. Customer-owned property modifiers pay Culture.
-- Stage 3 transaction registry
-- Market and Temple are independent customer sites, including in one city.
-- Lua computes their population-based targets and the Tailor city's combined
-- returns; customer-owned Culture consumers are defined at the end of this file.
-- Keep property names identical between this registry and the generated bit tests.
INSERT OR IGNORE INTO CSC_Stage3CustomerTransactions
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
VALUES
    (
        'CSC_TAILORS_TAILOR_MARKET',
        'DISTRICT_CSC_TAILORS_QUARTER',
        'BUILDING_CSC_TAILORS_TAILOR',
        'DISTRICT_COMMERCIAL_HUB',
        'BUILDING_MARKET',
        'CSC_TAILORS_STAGE_3_CUSTOMER_POP',
        'CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT',
        'CSC_TAILORS_STAGE_3_MARKET_CULTURE_AMOUNT',
        0.105
    ),
    (
        'CSC_TAILORS_TAILOR_TEMPLE',
        'DISTRICT_CSC_TAILORS_QUARTER',
        'BUILDING_CSC_TAILORS_TAILOR',
        'DISTRICT_HOLY_SITE',
        'BUILDING_TEMPLE',
        'CSC_TAILORS_STAGE_3_CUSTOMER_POP',
        'CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT',
        'CSC_TAILORS_STAGE_3_TEMPLE_CULTURE_AMOUNT',
        0.105
    );


--===========================================================================================================================================================================--
/*	STAGE 1 - MATERIALS IMPROVEMENTS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ImprovementModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO ImprovementModifiers
        (   ImprovementType,            ModifierId   )
VALUES  (   'IMPROVEMENT_PLANTATION',   'MOD_CSC_TAILORS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_MINE',         'MOD_CSC_TAILORS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   );

-- Material exchange begins at the improvement: Base materials send Culture to
-- adjacent Workshops. Reciprocal Production/Gold are producer-owned wrappers;
-- material-to-producer and producer-to-material are separate modifier chains.
INSERT INTO ImprovementModifiers
        (   ImprovementType,            ModifierId   )
VALUES  (   'IMPROVEMENT_FARM',         'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_PLANTATION',   'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_PASTURE',      'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER'   );


--===========================================================================================================================================================================--
/*	TAILORS' QUARTER */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Districts
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
        /*  DistrictType,               */  'DISTRICT_CSC_TAILORS_QUARTER',
        /*  Name,                       */  'LOC_DISTRICT_CSC_TAILORS_QUARTER_NAME',
        /*  Description,                */  'LOC_DISTRICT_CSC_TAILORS_QUARTER_DESCRIPTION',
        /*  PrereqTech,                 */  NULL,
        /*  PrereqCivic,                */  'CIVIC_CRAFTSMANSHIP',
        /*  Cost,                       */  60,
        /*  CostProgressionModel,       */  'COST_PROGRESSION_PREVIOUS_COPIES',
        /*  CostProgressionParam1,      */  10,
        /*  MilitaryDomain,             */  'NO_DOMAIN',
        /*  RequiresPlacement,          */  1,
        /*  Coast,                      */  0,
        /*  RequiresPopulation,         */  0,
        /*  Aqueduct,                   */  0,
        /*  InternalOnly,               */  0,
        /*  NoAdjacentCity,             */  0,
        /*  PlunderType,                */  'PLUNDER_HEAL',
        /*  PlunderAmount,              */  50,
        /*  Appeal,                     */  1,
        /*  OnePerCity,                 */  1,
        /*  CaptureRemovesBuildings,    */  0,
        /*  CaptureRemovesCityDefenses, */  0,
        /*  Maintenance,                */  1,
        /*  CityStrengthModifier,       */  2,
        /*  AdvisorType                 */  'ADVISOR_GENERIC'
    );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	DistrictModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- District material, customer, return, and river adjacencies are generated by the bundled CSC_AdjacencyProcessor.sql.

-- Stage 3 population and domestic trade returns are driven by city-center plot
-- properties maintained by the shared gameplay bridges.
-- City-center attachments consume city-wide totals calculated by shared Lua.
-- They exist once per receiving city, independently of how many producers or
-- neighboring customer sites contributed to the total.
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
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION'   );

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT  'DISTRICT_CITY_CENTER',       'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT INTO DistrictModifiers
        (   DistrictType,             ModifierId   )
VALUES  (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_1'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_IMPORT_TAILOR_AMENITY'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION'   );

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT  'DISTRICT_CITY_CENTER',       'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits
WHERE Bit > 1;

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT  'DISTRICT_CITY_CENTER',       'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;


--===========================================================================================================================================================================--
/*	STAGES 2-4 - BUILDINGS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- The Workshop is the common upstream prerequisite. Tailor and Fashion House
-- are separate downstream stages, not upgrades that remove the Workshop.
-- Hidden Service buildings carry slots/presentation; active bonuses have their
-- own gated modifiers rather than unconditional hidden-building effects.
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
    (
        /*  BuildingType,   */  'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',
        /*  Name,           */  'LOC_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP_DESCRIPTION',
        /*  PrereqTech,     */  'TECH_CONSTRUCTION',
        /*  PrereqCivic,    */  NULL,
        /*  Cost,           */  80,
        /*  PrereqDistrict, */  'DISTRICT_CSC_TAILORS_QUARTER',
        /*  PurchaseYield,  */  'YIELD_GOLD',
        /*  Maintenance,    */  2,
        /*  CitizenSlots,   */  0,
        /*  Entertainment,  */  0,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_TAILORS_TAILOR',
        /*  Name,           */  'LOC_BUILDING_CSC_TAILORS_TAILOR_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_TAILORS_TAILOR_DESCRIPTION',
        /*  PrereqTech,     */  NULL,
        /*  PrereqCivic,    */  'CIVIC_GUILDS',
        /*  Cost,           */  160,
        /*  PrereqDistrict, */  'DISTRICT_CSC_TAILORS_QUARTER',
        /*  PurchaseYield,  */  'YIELD_GOLD',
        /*  Maintenance,    */  2,
        /*  CitizenSlots,   */  1,
        /*  Entertainment,  */  1,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_TAILORS_STAGE_2_SERVICE',
        /*  Name,           */  'LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_DESCRIPTION',
        /*  PrereqTech,     */  NULL,
        /*  PrereqCivic,    */  NULL,
        /*  Cost,           */  0,
        /*  PrereqDistrict, */  'DISTRICT_HARBOR',
        /*  PurchaseYield,  */  NULL,
        /*  Maintenance,    */  0,
        /*  CitizenSlots,   */  1,
        /*  Entertainment,  */  0,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_TAILORS_STAGE_3_SERVICE',
        /*  Name,           */  'LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_DESCRIPTION',
        /*  PrereqTech,     */  NULL,
        /*  PrereqCivic,    */  NULL,
        /*  Cost,           */  0,
        /*  PrereqDistrict, */  'DISTRICT_HOLY_SITE',
        /*  PurchaseYield,  */  NULL,
        /*  Maintenance,    */  0,
        /*  CitizenSlots,   */  1,
        /*  Entertainment,  */  0,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    );

UPDATE Buildings
SET MustPurchase = 1
WHERE BuildingType IN (
	'BUILDING_CSC_TAILORS_STAGE_2_SERVICE',
	'BUILDING_CSC_TAILORS_STAGE_3_SERVICE'
);

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
    (
        'BUILDING_CSC_TAILORS_FASHION_HOUSE',
        'LOC_BUILDING_CSC_TAILORS_FASHION_HOUSE_NAME',
        'LOC_BUILDING_CSC_TAILORS_FASHION_HOUSE_DESCRIPTION',
        'CIVIC_HUMANISM',
        250,
        'DISTRICT_CSC_TAILORS_QUARTER',
        'YIELD_GOLD',
        3,
        1,
        1,
        6,
        0,
        'ADVISOR_CULTURE'
    ),
    (
        'BUILDING_CSC_TAILORS_STAGE_4_SERVICE',
        'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME',
        'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_DESCRIPTION',
        NULL,
        0,
        'DISTRICT_THEATER',
        NULL,
        0,
        1,
        0,
        0,
        1,
        'ADVISOR_CULTURE'
    ),
    (
        'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',
        'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_NAME',
        'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI_DESCRIPTION',
        NULL,
        0,
        'DISTRICT_WONDER',
        NULL,
        0,
        0,
        0,
        0,
        1,
        'ADVISOR_CULTURE'
    ),
    (
        'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY',
        'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_NAME',
        'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY_DESCRIPTION',
        NULL,
        0,
        'DISTRICT_WONDER',
        NULL,
        0,
        0,
        0,
        0,
        1,
        'ADVISOR_CULTURE'
    ),
    (
        'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',
        'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_NAME',
        'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY_DESCRIPTION',
        NULL,
        0,
        'DISTRICT_WONDER',
        NULL,
        0,
        0,
        0,
        0,
        1,
        'ADVISOR_CULTURE'
    );

-- Append the recipient's CSC relationship while preserving its original text.
-- Amphitheater includes direct uniques; each Wonder keeps a separate branch
-- so several venues in one city remain distinct customers.
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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings_XP2
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Pillage=0 keeps hidden Service buildings out of ordinary building pillage.
-- Producer/customer eligibility still controls their associated active benefits;
-- a persistent Service slot and a currently supplied Service are different states.
INSERT OR IGNORE INTO Buildings_XP2
        (   BuildingType,                             Pillage   )
VALUES  (   'BUILDING_CSC_TAILORS_STAGE_2_SERVICE',   0   ),
        (   'BUILDING_CSC_TAILORS_STAGE_3_SERVICE',   0   );

INSERT OR IGNORE INTO Buildings_XP2
        (   BuildingType,                                      Pillage   )
VALUES  (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE',            0   ),
        (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',    0   ),
        (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY',   0   ),
        (   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',     0   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingPrereqs
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Both downstream producers require the Workshop. Fashion House does not
-- require a Tailor row here; the branches share their upstream production stage.
INSERT OR IGNORE INTO BuildingPrereqs
        (   Building,                        PrereqBuilding   )
VALUES  (   'BUILDING_CSC_TAILORS_TAILOR',   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   );

INSERT OR IGNORE INTO BuildingPrereqs
        (   Building,                               PrereqBuilding   )
VALUES  (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Building_CitizenYieldChanges
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- These are yields from an assigned specialist, separate from passive sales,
-- trade-route returns and the customer-population transaction amounts.
INSERT INTO Building_CitizenYieldChanges
        (   BuildingType,                    YieldType,         YieldChange   )
VALUES  (   'BUILDING_CSC_TAILORS_TAILOR',   'YIELD_CULTURE',   2   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',   'YIELD_GOLD',      1   );

INSERT OR IGNORE INTO Building_CitizenYieldChanges
        (   BuildingType,                           YieldType,         YieldChange   )
VALUES  (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'YIELD_CULTURE',   1   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'YIELD_GOLD',      2   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Fashion House has separate state readers: SUPPLIED enables goods exports;
-- SERVICE_ELIGIBLE adds civic/producer prerequisites used by Wonder placement.
-- SQL grants the ordinary Theater Square Service. CSC_WonderServicePlacement.lua
-- grants the three Wonder variants on their actual host plots.
INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,                           ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_FASHION_HOUSE_SUPPLIED_PROPERTY'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE_PROPERTY'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_4_SERVICE_ATTACH_THEATER'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_CUSTOMER'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_CUSTOMER'   );

-- Workshop/Lighthouse and downstream exchanges
-- Workshop sends Production to adjacent Lighthouses and Culture to its local
-- Tailor/Fashion House. Lighthouse and downstream producers attach the reciprocal
-- Workshop return. Dockmaster/Sacristan grants and benefits use separate wrappers.
INSERT INTO BuildingModifiers
        (   BuildingType,                              ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_PROD'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_HARBOR_LIGHTHOUSE'   ),
        (   'BUILDING_LIGHTHOUSE',                     'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_PROD'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_STAGE_2_SERVICE_ATTACH_HARBOR'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_DOCKMASTER_GPP_ATTACH_HARBOR'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_TAILOR_SUPPLIED_PROPERTY'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_STAGE_3_SERVICE_ATTACH_HOLY_SITE'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_SACRISTAN_FAITH_ATTACH_HOLY_SITE'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_SACRISTAN_GPP_ATTACH_HOLY_SITE'   );

-- Emit this attachment only if the Fashion House building exists in the loaded content.
INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,   ModifierId   )
SELECT BuildingType, 'MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP'
FROM Buildings
WHERE BuildingType = 'BUILDING_CSC_TAILORS_FASHION_HOUSE';

INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,   ModifierId   )
SELECT CivUniqueBuildingType, 'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_PROD'
FROM BuildingReplaces
WHERE ReplacesBuildingType = 'BUILDING_LIGHTHOUSE';

-- Dockmaster expands an explicit era x naval-family matrix: Ancient through
-- Renaissance, for naval melee/ranged/raider classes. Match each generated key
-- across attachment, child modifier and arguments. This does not implicitly
-- include later eras or non-naval unit families.
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


--===========================================================================================================================================================================--
/*	MODIFIERS */
--===========================================================================================================================================================================--

INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,                           ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BOLSHOI'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BOLSHOI'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BROADWAY'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BROADWAY'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_SYDNEY'   ),
        (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_SYDNEY'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Read ATTACH chains from source to receiver. OwnerRequirementSetId checks the
-- producer/improvement; SubjectRequirementSetId filters the target collection.
-- A child with NULL requirements can intentionally rely on its wrapper's gate.
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                                  ModifierType,                                            OwnerRequirementSetId,                          SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_SPEC_CULTURE_TO_FASHION_HOUSE',             'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_SPEC_IMPROVEMENT_ATTACH_QUARTER',           'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_PLOT_HAS_SPEC',             'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_SUPPLIED_PROPERTY',           'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                  'REQSET_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ',     NULL   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE_PROPERTY',   'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                  'REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ',   NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_4_SERVICE_GRANT',                     'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_4_SERVICE_ATTACH_THEATER',            'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM',                     'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',        NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_CUSTOMER',     'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP',                         'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',   NULL,                                           NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_CUSTOMER',         'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',     'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER'   );

-- Stage 4 uses whole stacks: floor(customer population / 5) for each seller,
-- site and venue branch, then sums them. These bits are counts, unlike Stage 3's
-- scaled rates. Gold mirrors these stacks in its companion; each venue's Culture
-- uses that venue's building branch.
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

-- Trade is a separate channel from population sales. Import flags mean at
-- least one eligible route; export bits encode route counts. UI scans active
-- routes, then the synchronized gameplay receiver writes the city/plot properties.
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                          ModifierType,                                       OwnerRequirementSetId,   SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_CULTURE',      'MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE',         NULL,                    'REQSET_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE'   ),
        (   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_AMENITY',      'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',   NULL,                    'REQSET_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE'   ),
        (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION',   'MODIFIER_BUILDING_YIELD_CHANGE',                   NULL,                    'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1'   );

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION_BIT_' || Bit,
	'MODIFIER_BUILDING_YIELD_CHANGE', NULL,
	'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

-- Base input -> Workshop, Workshop -> improved Base plot, then local exchanges.
-- The single-plot Production child can also serve the Fashion House's Specialty
-- wrapper because the parent, not the child, supplies the resource-class gate.
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                            ModifierType,                                            OwnerRequirementSetId,                        SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER',     'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_PLOT_HAS_BASE',           'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'MOD_CSC_TAILORS_BASE_IMPROV_CULTURE_TO_WORKSHOP',     'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_PROD',   'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',      NULL,                                         'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE'   ),
        (   'MOD_CSC_TAILORS_PROD_TO_ADJ_BASE',                    'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',               NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_HARBOR_LIGHTHOUSE',   'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         NULL,                                         'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE'   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_PROD_TO_LIGHTHOUSE',         'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_PROD',      'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         NULL,                                         'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_PROD_TO_WORKSHOP',         'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR',          'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE',   'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP',             'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP',      'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_ATTACH_HARBOR',       'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',   'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE'   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_GRANT',               'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP_ATTACH_HARBOR',        'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',   'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE'   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP',                      'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',   NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_TAILOR_SUPPLIED_PROPERTY',            'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                  'REQSET_CSC_TAILORS_STAGE_3_SUPPLY_PREREQ',   NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_ATTACH_HOLY_SITE',    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE'   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_GRANT',               'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',    NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH_ATTACH_HOLY_SITE',    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH',                     'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_MODIFIER',       NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP_ATTACH_HOLY_SITE',      'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',         'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP',                       'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',   NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE',               'MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE',              NULL,                                         'REQSET_CSC_TAILORS_IMPORT_TAILOR_ROUTE'   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_AMENITY',               'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',        NULL,                                         'REQSET_CSC_TAILORS_IMPORT_TAILOR_ROUTE'   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION',            'MODIFIER_BUILDING_YIELD_CHANGE',                        NULL,                                         'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1'   );

-- Stage 3 bits encode a rate scaled by 10,000. Lua divides a target city-total
-- yield by the receiving city's population; the native per-population effect
-- multiplies it back. Bit / 10000.0 must stay floating point so fractional returns
-- survive SQL division.
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_' || Bit,
	'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION', NULL,
	'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

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

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                                ModifierType,                                       OwnerRequirementSetId,                        SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BOLSHOI',           'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',   NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BOLSHOI',    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',    'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BOLSHOI'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BOLSHOI',        'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',    'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BOLSHOI'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BROADWAY',          'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',   NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BROADWAY',   'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',    'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BROADWAY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BROADWAY',       'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',    'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BROADWAY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_SYDNEY',            'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',   NULL,                                         NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_SYDNEY',     'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',    'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',   'REQSET_CSC_TAILORS_ADJ_STAGE_4_SYDNEY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_SYDNEY',         'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',    'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',   'REQSET_CSC_TAILORS_ADJ_STAGE_4_SYDNEY'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- ModifierId links wrapper to child; BuildingType/YieldType/Amount describe
-- that child's action. Key/Amount on state modifiers instead publish city
-- properties for trade, art or Wonder placement; those properties are not yields.
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                                                  Name,                     Value   )
VALUES  (   'MOD_CSC_TAILORS_SPEC_CULTURE_TO_FASHION_HOUSE',             'BuildingType',           'BUILDING_CSC_TAILORS_FASHION_HOUSE'   ),
        (   'MOD_CSC_TAILORS_SPEC_CULTURE_TO_FASHION_HOUSE',             'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_TAILORS_SPEC_CULTURE_TO_FASHION_HOUSE',             'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_SPEC_IMPROVEMENT_ATTACH_QUARTER',           'ModifierId',             'MOD_CSC_TAILORS_SPEC_CULTURE_TO_FASHION_HOUSE'   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_SUPPLIED_PROPERTY',           'Key',                    'CSC_TAILORS_FASHION_HOUSE_SUPPLIED'   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_SUPPLIED_PROPERTY',           'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE_PROPERTY',   'Key',                    'CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE'   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_SERVICE_ELIGIBLE_PROPERTY',   'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_STAGE_4_SERVICE_GRANT',                     'BuildingType',           'BUILDING_CSC_TAILORS_STAGE_4_SERVICE'   ),
        (   'MOD_CSC_TAILORS_STAGE_4_SERVICE_ATTACH_THEATER',            'ModifierId',             'MOD_CSC_TAILORS_STAGE_4_SERVICE_GRANT'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM',                     'Amount',                 2   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_CUSTOMER',     'ModifierId',             'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP',                         'GreatPersonClassType',   'GREAT_PERSON_CLASS_ARTIST'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP',                         'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_CUSTOMER',         'ModifierId',             'MOD_CSC_TAILORS_STAGE_MANAGER_GPP'   );

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_' || Bit, 'BuildingType', 'BUILDING_CSC_TAILORS_FASHION_HOUSE'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_' || Bit, 'YieldType', 'YIELD_PRODUCTION'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_FASHION_HOUSE_RETURN_PRODUCTION_BIT_' || Bit, 'Amount', Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'BuildingType', 'BUILDING_AMPHITHEATER'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'YieldType', 'YIELD_CULTURE'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_AMPHITHEATER_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'Amount', Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'BuildingType', 'BUILDING_BOLSHOI_THEATRE'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'YieldType', 'YIELD_CULTURE'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_BOLSHOI_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'Amount', Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'BuildingType', 'BUILDING_BROADWAY'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'YieldType', 'YIELD_CULTURE'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_BROADWAY_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'Amount', Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'BuildingType', 'BUILDING_SYDNEY_OPERA_HOUSE'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'YieldType', 'YIELD_CULTURE'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_STAGE_4_SYDNEY_CULTURE_RETURN_CULTURE_BIT_' || Bit, 'Amount', Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                                          Name,             Value   )
VALUES  (   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_CULTURE',      'YieldType',      'YIELD_CULTURE'   ),
        (   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_CULTURE',      'Amount',         1   ),
        (   'MOD_CSC_TAILORS_IMPORT_FASHION_HOUSE_AMENITY',      'Amount',         1   ),
        (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION',   'BuildingType',   'BUILDING_CSC_TAILORS_FASHION_HOUSE'   ),
        (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION',   'YieldType',      'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_EXPORT_FASHION_HOUSE_PRODUCTION',   'Amount',         1   );

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
        (   ModifierId,                                            Name,                     Value   )
VALUES  (   'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER',     'ModifierId',             'MOD_CSC_TAILORS_BASE_IMPROV_CULTURE_TO_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_BASE_IMPROV_CULTURE_TO_WORKSHOP',     'BuildingType',           'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_BASE_IMPROV_CULTURE_TO_WORKSHOP',     'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_TAILORS_BASE_IMPROV_CULTURE_TO_WORKSHOP',     'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_PROD',   'ModifierId',             'MOD_CSC_TAILORS_PROD_TO_ADJ_BASE'   ),
        (   'MOD_CSC_TAILORS_PROD_TO_ADJ_BASE',                    'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_PROD_TO_ADJ_BASE',                    'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_HARBOR_LIGHTHOUSE',   'ModifierId',             'MOD_CSC_TAILORS_WORKSHOP_PROD_TO_LIGHTHOUSE'   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_PROD_TO_LIGHTHOUSE',         'BuildingType',           'BUILDING_LIGHTHOUSE'   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_PROD_TO_LIGHTHOUSE',         'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_PROD_TO_LIGHTHOUSE',         'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_PROD',      'ModifierId',             'MOD_CSC_TAILORS_LIGHTHOUSE_PROD_TO_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_PROD_TO_WORKSHOP',         'BuildingType',           'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_PROD_TO_WORKSHOP',         'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_PROD_TO_WORKSHOP',         'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR',          'BuildingType',           'BUILDING_CSC_TAILORS_TAILOR'   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR',          'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR',          'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE',   'BuildingType',           'BUILDING_CSC_TAILORS_FASHION_HOUSE'   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE',   'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE',   'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP',             'BuildingType',           'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP',             'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP',             'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP',      'BuildingType',           'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP',      'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP',      'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_ATTACH_HARBOR',       'ModifierId',             'MOD_CSC_TAILORS_STAGE_2_SERVICE_GRANT'   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_GRANT',               'BuildingType',           'BUILDING_CSC_TAILORS_STAGE_2_SERVICE'   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP_ATTACH_HARBOR',        'ModifierId',             'MOD_CSC_TAILORS_DOCKMASTER_GPP'   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP',                      'GreatPersonClassType',   'GREAT_PERSON_CLASS_ADMIRAL'   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP',                      'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_TAILOR_SUPPLIED_PROPERTY',            'Key',                    'CSC_TAILORS_TAILOR_SUPPLIED'   ),
        (   'MOD_CSC_TAILORS_TAILOR_SUPPLIED_PROPERTY',            'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_ATTACH_HOLY_SITE',    'ModifierId',             'MOD_CSC_TAILORS_STAGE_3_SERVICE_GRANT'   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_GRANT',               'BuildingType',           'BUILDING_CSC_TAILORS_STAGE_3_SERVICE'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH_ATTACH_HOLY_SITE',    'ModifierId',             'MOD_CSC_TAILORS_SACRISTAN_FAITH'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH',                     'YieldType',              'YIELD_FAITH'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH',                     'Amount',                 10   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP_ATTACH_HOLY_SITE',      'ModifierId',             'MOD_CSC_TAILORS_SACRISTAN_GPP'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP',                       'GreatPersonClassType',   'GREAT_PERSON_CLASS_PROPHET'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP',                       'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE',               'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE',               'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_AMENITY',               'Amount',                 1   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION',            'BuildingType',           'BUILDING_CSC_TAILORS_TAILOR'   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION',            'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION',            'Amount',                 1   );

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_' || Bit, 'YieldType', 'YIELD_PRODUCTION'
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_' || Bit, 'Amount', Bit / 10000.0
FROM CSC_ScaledAmountBits;

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


--===========================================================================================================================================================================--
/*	REQUIREMENTS */
--===========================================================================================================================================================================--

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                                                Name,           Value   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BOLSHOI',           'Amount',       2   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BOLSHOI',    'ModifierId',   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BOLSHOI'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BOLSHOI',        'ModifierId',   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BROADWAY',          'Amount',       2   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BROADWAY',   'ModifierId',   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BROADWAY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_BROADWAY',       'ModifierId',   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_SYDNEY',            'Amount',       2   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_SYDNEY',     'ModifierId',   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_SYDNEY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP_ATTACH_SYDNEY',         'ModifierId',   'MOD_CSC_TAILORS_STAGE_MANAGER_GPP'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Supply, producer readiness and full Service eligibility are different gates.
-- SUPPLY checks improved materials; PRODUCER adds the civic; EFFECT additionally
-- requires an eligible adjacent customer. Trade can export supplied goods without
-- borrowing the Service's customer requirement. TEST_ANY combines alternative
-- Stage 4 venues, while each individual venue uses its own TEST_ALL checks.
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,                                RequirementSetType   )
VALUES  (   'REQSET_CSC_TAILORS_PLOT_HAS_SPEC',              'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC',          'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ',      'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ',    'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER',   'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',       'REQUIREMENTSET_TEST_ANY'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_CUSTOMER',       'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',      'REQUIREMENTSET_TEST_ALL'   );

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
        (   RequirementSetId,                                        RequirementSetType   )
VALUES  (   'REQSET_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE',         'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1',   'REQUIREMENTSET_TEST_ALL'   );

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,                                 RequirementSetType   )
VALUES  (   'REQSET_CSC_TAILORS_PLOT_HAS_BASE',               'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',           'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_ADJ_TAILORS_QUARTER',                 'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE',       'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',       'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_MARKET',                  'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_TEMPLE',                  'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_SUPPLY_PREREQ',       'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',       'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE',        'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_IMPORT_TAILOR_ROUTE',         'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1',   'REQUIREMENTSET_TEST_ALL'   );

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,                            RequirementSetType   )
VALUES  (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BOLSHOI',    'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BROADWAY',   'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_SYDNEY',     'REQUIREMENTSET_TEST_ALL'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Membership rows provide the actual AND/OR logic of the named sets above.
-- Art and Service wrappers share a complete gate; omitting its customer check
-- would let civic and material supply activate a Service by themselves.
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,                                RequirementId   )
VALUES  (   'REQSET_CSC_TAILORS_PLOT_HAS_SPEC',              'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC',          'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC',          'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ',      'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ',      'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_SPEC'   ),
        (   'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER',   'REQ_CSC_TAILORS_DISTRICT_IS_THEATER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_THEATER_AMPHITHEATER',   'REQ_CSC_TAILORS_CITY_HAS_AMPHITHEATER'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',       'REQ_CSC_TAILORS_STAGE_4_THEATER_CUSTOMER'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',       'REQ_CSC_TAILORS_STAGE_4_BOLSHOI_READY'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',       'REQ_CSC_TAILORS_STAGE_4_BROADWAY_READY'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_CUSTOMER_ANY',       'REQ_CSC_TAILORS_STAGE_4_SYDNEY_READY'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_CUSTOMER',       'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_CUSTOMER',       'REQ_CSC_TAILORS_STAGE_4_CUSTOMER_ANY'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ',    'REQ_CSC_TAILORS_STAGE_4_SUPPLY_PREREQ'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ',    'REQ_CSC_TAILORS_PLAYER_HAS_OPERA_BALLET'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',      'REQ_CSC_TAILORS_STAGE_4_PRODUCER_PREREQ'   ),
        (   'REQSET_CSC_TAILORS_STAGE_4_EFFECT_PREREQ',      'REQ_CSC_TAILORS_HAS_ADJ_STAGE_4_SERVICE_CUSTOMER'   );

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
        (   RequirementSetId,                                        RequirementId   )
VALUES  (   'REQSET_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE',         'REQ_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE'   ),
        (   'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1',   'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1'   );

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit,
	'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,                                 RequirementId   )
VALUES  (   'REQSET_CSC_TAILORS_PLOT_HAS_BASE',               'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',           'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',           'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE'   ),
        (   'REQSET_CSC_ADJ_TAILORS_QUARTER',                 'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_ADJ_TAILORS_QUARTER',                 'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE',       'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE',       'REQ_CSC_TAILORS_DISTRICT_IS_HARBOR'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE',       'REQ_CSC_TAILORS_CITY_HAS_LIGHTHOUSE'   ),
        (   'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',       'REQ_CSC_TAILORS_PLAYER_HAS_NAVAL_TRADITION'   ),
        (   'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',       'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',       'REQ_CSC_TAILORS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_MARKET',                  'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_MARKET',                  'REQ_CSC_TAILORS_DISTRICT_IS_COMMERCIAL_HUB'   ),
        (   'REQSET_CSC_TAILORS_ADJ_MARKET',                  'REQ_CSC_TAILORS_CITY_HAS_MARKET'   ),
        (   'REQSET_CSC_TAILORS_ADJ_TEMPLE',                  'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_TEMPLE',                  'REQ_CSC_TAILORS_DISTRICT_IS_HOLY_SITE'   ),
        (   'REQSET_CSC_TAILORS_ADJ_TEMPLE',                  'REQ_CSC_TAILORS_CITY_HAS_TEMPLE'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_SUPPLY_PREREQ',       'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',       'REQ_CSC_TAILORS_PLAYER_HAS_DIVINE_RIGHT'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',       'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',       'REQ_CSC_TAILORS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE',        'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE',        'REQ_CSC_TAILORS_DISTRICT_IS_HOLY_SITE'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE',        'REQ_CSC_TAILORS_CITY_HAS_TEMPLE'   ),
        (   'REQSET_CSC_TAILORS_IMPORT_TAILOR_ROUTE',         'REQ_CSC_TAILORS_IMPORT_TAILOR_ROUTE'   ),
        (   'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1',   'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1'   );

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit,
	'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit,
	'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,                            RequirementId   )
VALUES  (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BOLSHOI',    'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BOLSHOI',    'REQ_CSC_TAILORS_STAGE_4_BOLSHOI_READY'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BROADWAY',   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_BROADWAY',   'REQ_CSC_TAILORS_STAGE_4_BROADWAY_READY'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_SYDNEY',     'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_TAILORS_ADJ_STAGE_4_SYDNEY',     'REQ_CSC_TAILORS_STAGE_4_SYDNEY_READY'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Individual requirements declare reusable native predicate types. Collection
-- counts ask whether an adjacent owned capstone exists; nested sets keep each
-- venue's district/building/plot checks together.
INSERT OR IGNORE INTO Requirements
        (   RequirementId,                                        RequirementType,                            Inverse   )
VALUES  (   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',             'REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES',    0   ),
        (   'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
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
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_4_SERVICE_CUSTOMER',   'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   );

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
        (   RequirementId,                                        RequirementType,                       Inverse   )
VALUES  (   'REQ_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE',         'REQUIREMENT_PLOT_PROPERTY_MATCHES',   0   ),
        (   'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1',   'REQUIREMENT_PLOT_PROPERTY_MATCHES',   0   );

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT 'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,                                        RequirementType,                            Inverse   )
VALUES  (   'REQ_CSC_TAILORS_PLOT_ADJ_TO_OWNER',                  'REQUIREMENT_PLOT_ADJACENT_TO_OWNER',       0   ),
        (   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',             'REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES',    0   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',                'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_HARBOR',                 'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_LIGHTHOUSE',                'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
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
SELECT 'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT 'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_RouteStackBits
WHERE Bit > 1;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Bind each predicate to its tag, capstone, civic, distance or property name.
-- Wonder checks use actual buildings/plots: DISTRICT_WONDER alone cannot tell
-- several Wonders in one city apart.
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,                                        Name,                  Value   )
VALUES  (   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_SPEC',             'Tag',                 'CLASS_CSC_TAILORS_SPEC'   ),
        (   'REQ_CSC_TAILORS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'CollectionType',      'COLLECTION_PLAYER_IMPROVEMENTS'   ),
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
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_4_SERVICE_CUSTOMER',   'RequirementSetId',    'REQSET_CSC_TAILORS_ADJ_STAGE_4_CUSTOMER'   );

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
        (   RequirementId,                                        Name,                Value   )
VALUES  (   'REQ_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE',         'PropertyName',      'CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE'   ),
        (   'REQ_CSC_TAILORS_IMPORT_FASHION_HOUSE_ROUTE',         'PropertyMinimum',   1   ),
        (   'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1',   'PropertyName',      'CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1'   ),
        (   'REQ_CSC_TAILORS_EXPORT_FASHION_HOUSE_ROUTE_BIT_1',   'PropertyMinimum',   1   );

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
        (   RequirementId,                                        Name,                  Value   )
VALUES  (   'REQ_CSC_TAILORS_PLOT_HAS_MATERIAL_BASE',             'Tag',                 'CLASS_CSC_TAILORS_BASE'   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_QUARTER',                'DistrictType',        'DISTRICT_CSC_TAILORS_QUARTER'   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_HARBOR',                 'DistrictType',        'DISTRICT_HARBOR'   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_LIGHTHOUSE',                'BuildingType',        'BUILDING_LIGHTHOUSE'   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_LIGHTHOUSE',                'MustBeFunctioning',   1   ),
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
SELECT 'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'PropertyName',
	'CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_ScaledAmountBits;

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


--===========================================================================================================================================================================--
/*	UI */
--===========================================================================================================================================================================--

-- Presentation observes gameplay rather than deciding eligibility. These types
-- provide gain/increase/decrease/removal channels; the ability registry below
-- chooses the active modifier chains counted by MCUIS and notifications.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Notifications
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Types
        (   Type,                                          Kind   )
VALUES  (   'NOTIFICATION_CSC_TAILORS_EFFECT_NEW',         'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_INCREASED',   'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_DECREASED',   'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_REMOVED',     'KIND_NOTIFICATION'   );

INSERT OR IGNORE INTO Notifications
        (   NotificationType,                              SeverityType,   ExpiresEndOfTurn,   AutoNotify   )
VALUES  (   'NOTIFICATION_CSC_TAILORS_EFFECT_NEW',         'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_INCREASED',   'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_DECREASED',   'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_TAILORS_EFFECT_REMOVED',     'HIGH',         0,                  0   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- CSC_AbilityAttachModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO CSC_AbilityAttachModifiers
        (   ModifierId,                                                        AbilityIcon,                                   AbilityIconTarget,                        NotificationQuarter   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_2_DOCKMASTER_ATTACH_ANCIENT_NAVAL_MELEE',   'ICON_BUILDING_CSC_TAILORS_STAGE_2_SERVICE',   'BUILDING_CSC_TAILORS_STAGE_2_SERVICE',   'TAILORS'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH_ATTACH_HOLY_SITE',                'ICON_BUILDING_CSC_TAILORS_STAGE_3_SERVICE',   'BUILDING_CSC_TAILORS_STAGE_3_SERVICE',   'TAILORS'   );

-- Stage Manager keeps a separate Tourism anchor for each venue. Great Artist
-- point siblings use the same gates; UI observes only the chosen anchor so a
-- single Service benefit does not produce duplicate icons or notifications.
INSERT OR IGNORE INTO CSC_AbilityAttachModifiers
        (   ModifierId,                                                AbilityIcon,                                            AbilityIconTarget,                                 NotificationQuarter   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BOLSHOI',    'ICON_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',    'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BOLSHOI',    'TAILORS'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_BROADWAY',   'ICON_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY',   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_BROADWAY',   'TAILORS'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_SYDNEY',     'ICON_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',     'BUILDING_CSC_TAILORS_STAGE_4_SERVICE_SYDNEY',     'TAILORS'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierStrings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO ModifierStrings
        (   ModifierId,                                                Context,     'Text'   )
VALUES  (   'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_ANCIENT_NAVAL_MELEE',   'Preview',   'LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION'   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_GRANT',                   'Preview',   'LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH',                         'Preview',   'LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION'   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_GRANT',                   'Preview',   'LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME'   );

INSERT OR IGNORE INTO CSC_AbilityAttachModifiers
        (   ModifierId,                                                AbilityIcon,                                   AbilityIconTarget,                        NotificationQuarter   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_ATTACH_CUSTOMER',   'ICON_BUILDING_CSC_TAILORS_STAGE_4_SERVICE',   'BUILDING_CSC_TAILORS_STAGE_4_SERVICE',   'TAILORS'   );

INSERT OR IGNORE INTO ModifierStrings
        (   ModifierId,                                Context,     Text   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM',   'Preview',   'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION'   ),
        (   'MOD_CSC_TAILORS_STAGE_4_SERVICE_GRANT',   'Preview',   'LOC_BUILDING_CSC_TAILORS_STAGE_4_SERVICE_NAME'   );


INSERT OR IGNORE INTO ModifierStrings
        (   ModifierId,                                         Context,     Text   )
VALUES  (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BOLSHOI',    'Preview',   'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BOLSHOI'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_BROADWAY',   'Preview',   'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_BROADWAY'   ),
        (   'MOD_CSC_TAILORS_STAGE_MANAGER_TOURISM_SYDNEY',     'Preview',   'LOC_CSC_TAILORS_STAGE_4_EFFECT_DESCRIPTION_SYDNEY'   );

-- Art uses the complete Service gate, including a live customer. SQL writes a
-- source property; CSC_ArtProperties.lua only converts it into a binary art flag.
-- Do not give that Lua mirror its own material/civic/venue eligibility algorithm.
-- Expanded building art: source properties use the complete gameplay Service gates.
-- CSC_ArtProperties.lua mirrors these into binary CITYPROP selection flags.
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

-- Stage 3 Culture lives on the customer city, avoiding a seller-owned wrapper
-- whose subjects could retain a stale amount. Separate Market/Temple channels
-- read Lua's summed property; several sellers contribute to one consumer, and
-- clearing that property removes the previous Culture.
-- Customer-owned property modifiers invalidate Culture immediately when a seller changes.

INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_ScaledAmountBits;
INSERT INTO Modifiers
        (   ModifierId,   ModifierType,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION', 'REQSET_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_ScaledAmountBits;
INSERT INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'YieldType', 'YIELD_CULTURE' FROM CSC_ScaledAmountBits;
INSERT INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'Amount', Bit / 10000.0 FROM CSC_ScaledAmountBits;
INSERT INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL' FROM CSC_ScaledAmountBits;
INSERT INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'REQ_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_ScaledAmountBits;
INSERT INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT 'REQ_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES' FROM CSC_ScaledAmountBits;
INSERT INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'PropertyName', 'CSC_TAILORS_STAGE_3_MARKET_CULTURE_AMOUNT_BIT_' || Bit FROM CSC_ScaledAmountBits;
INSERT INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_MARKET_CUSTOMER_CULTURE_BIT_' || Bit, 'PropertyMinimum', 1 FROM CSC_ScaledAmountBits;

-- Temple has its own property family even when its city also has a Market.
-- Lua counts those sites independently. Both channels can pay into one Culture
-- total without overwriting one another's saved bit properties.
INSERT INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT 'DISTRICT_CITY_CENTER', 'MOD_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_ScaledAmountBits;
INSERT INTO Modifiers
        (   ModifierId,   ModifierType,   SubjectRequirementSetId   )
SELECT 'MOD_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION', 'REQSET_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_ScaledAmountBits;
INSERT INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'YieldType', 'YIELD_CULTURE' FROM CSC_ScaledAmountBits;
INSERT INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT 'MOD_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'Amount', Bit / 10000.0 FROM CSC_ScaledAmountBits;
INSERT INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT 'REQSET_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL' FROM CSC_ScaledAmountBits;
INSERT INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT 'REQSET_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'REQ_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit FROM CSC_ScaledAmountBits;
INSERT INTO Requirements
        (   RequirementId,   RequirementType   )
SELECT 'REQ_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES' FROM CSC_ScaledAmountBits;
INSERT INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'PropertyName', 'CSC_TAILORS_STAGE_3_TEMPLE_CULTURE_AMOUNT_BIT_' || Bit FROM CSC_ScaledAmountBits;
INSERT INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT 'REQ_CSC_TAILORS_TEMPLE_CUSTOMER_CULTURE_BIT_' || Bit, 'PropertyMinimum', 1 FROM CSC_ScaledAmountBits;


-- Specialty producers receive the same bilateral return as Base producers.
INSERT INTO BuildingModifiers
        (   BuildingType,                           ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_FASHION_HOUSE',   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IMP_SPEC_PROD'   );
INSERT INTO Modifiers
        (   ModifierId,                                                 ModifierType,                                         SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IMP_SPEC_PROD',   'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_SPEC'   );
INSERT INTO ModifierArguments
        (   ModifierId,                                                 Name,           Value   )
VALUES  (   'MOD_CSC_TAILORS_FASHION_HOUSE_ATTACH_ADJ_IMP_SPEC_PROD',   'ModifierId',   'MOD_CSC_TAILORS_PROD_TO_ADJ_BASE'   );
