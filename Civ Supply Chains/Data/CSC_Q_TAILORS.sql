-- CSC_Q_TAILORS
-- Author: Henno
-- DateCreated: 2026-08-23
--------------------------------------------------------------

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
        (   'MODIFIER_CSC_TAILORS_SINGLE_CITY_ADJUST_UNIT_TAG_ERA_PRODUCTION',   'KIND_MODIFIER'   );

INSERT OR IGNORE INTO DynamicModifiers
        (   ModifierType,                                                        CollectionType,       EffectType   )
VALUES  (   'MODIFIER_CSC_TAILORS_SINGLE_CITY_ADJUST_UNIT_TAG_ERA_PRODUCTION',   'COLLECTION_OWNER',   'EFFECT_ADJUST_UNIT_TAG_ERA_PRODUCTION'   );


--===========================================================================================================================================================================--
/*	RESOURCES */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

INSERT OR IGNORE INTO CSC_QuarterMaterialAdjacencyConfig
        (   QuarterKey,   SourceTag,                  SourceFilter,   YieldType,            YieldChange,   AdjacencyType   )
VALUES  (   'TAILORS',    'CLASS_CSC_TAILORS_BASE',   '',             'YIELD_PRODUCTION',   1,             'FROM_RINGS_TYPETAG_RESOURCE'   ),
        (   'TAILORS',    'CLASS_CSC_TAILORS_SPEC',   '',             'YIELD_PRODUCTION',   1,             'FROM_RINGS_TYPETAG_RESOURCE'   );


--===========================================================================================================================================================================--
/*	STAGE 1 - MATERIALS IMPROVEMENTS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ImprovementModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
		( DistrictType, Name, Description, PrereqTech, PrereqCivic, Cost, CostProgressionModel, CostProgressionParam1, MilitaryDomain, RequiresPlacement, Coast, RequiresPopulation, Aqueduct, InternalOnly, NoAdjacentCity, PlunderType, PlunderAmount, Appeal, OnePerCity, CaptureRemovesBuildings, CaptureRemovesCityDefenses, Maintenance, CityStrengthModifier, AdvisorType )
VALUES	(
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

-- District material, customer, return, and river adjacencies are generated by CSC_Ruivo_AdjacencyProcessor.sql.

-- Stage 3 population and domestic trade returns are driven by city-center plot
-- properties maintained by the shared gameplay bridges.
INSERT INTO DistrictModifiers
        (   DistrictType,             ModifierId   )
VALUES  (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_1'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_IMPORT_TAILOR_AMENITY'   ),
        (   'DISTRICT_CITY_CENTER',   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION'   );

INSERT INTO DistrictModifiers
        (   DistrictType,            ModifierId   )
SELECT  'DISTRICT_CITY_CENTER',       'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits
WHERE Bit > 1;

INSERT INTO DistrictModifiers
        (   DistrictType,            ModifierId   )
SELECT  'DISTRICT_CITY_CENTER',       'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;


--===========================================================================================================================================================================--
/*	STAGES 2-4 - BUILDINGS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Buildings
		( BuildingType, Name, Description, PrereqTech, PrereqCivic, Cost, PrereqDistrict, PurchaseYield, Maintenance, CitizenSlots, Entertainment, AdvisorType )
VALUES	(
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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings_XP2
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Buildings_XP2
        (   BuildingType,                             Pillage   )
VALUES  (   'BUILDING_CSC_TAILORS_STAGE_2_SERVICE',   0   ),
        (   'BUILDING_CSC_TAILORS_STAGE_3_SERVICE',   0   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingPrereqs
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO BuildingPrereqs
        (   Building,                        PrereqBuilding   )
VALUES  (   'BUILDING_CSC_TAILORS_TAILOR',   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Building_CitizenYieldChanges
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO Building_CitizenYieldChanges
        (   BuildingType,                    YieldType,         YieldChange   )
VALUES  (   'BUILDING_CSC_TAILORS_TAILOR',   'YIELD_CULTURE',   2   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',   'YIELD_GOLD',      1   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO BuildingModifiers
        (   BuildingType,                              ModifierId   )
VALUES  (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_PROD'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_HARBOR_LIGHTHOUSE'   ),
        (   'BUILDING_LIGHTHOUSE',                     'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_PROD'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_STAGE_2_ART_PROPERTY'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_STAGE_2_SERVICE_ATTACH_HARBOR'   ),
        (   'BUILDING_CSC_TAILORS_TEXTILE_WORKSHOP',   'MOD_CSC_TAILORS_DOCKMASTER_GPP_ATTACH_HARBOR'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_TAILOR_ATTACH_MARKET'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_TAILOR_ATTACH_TEMPLE'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_STAGE_3_ART_PROPERTY'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_TAILOR_SUPPLIED_PROPERTY'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_STAGE_3_SERVICE_ATTACH_HOLY_SITE'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_SACRISTAN_FAITH_ATTACH_HOLY_SITE'   ),
        (   'BUILDING_CSC_TAILORS_TAILOR',             'MOD_CSC_TAILORS_SACRISTAN_GPP_ATTACH_HOLY_SITE'   );

INSERT OR IGNORE INTO BuildingModifiers
		( BuildingType, ModifierId )
SELECT CivUniqueBuildingType, 'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_PROD'
FROM BuildingReplaces
WHERE ReplacesBuildingType = 'BUILDING_LIGHTHOUSE';

INSERT INTO BuildingModifiers
		( BuildingType, ModifierId )
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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                            ModifierType,                                              OwnerRequirementSetId,                         SubjectRequirementSetId   )
VALUES  (   'MOD_CSC_TAILORS_BASE_IMPROVEMENT_ATTACH_QUARTER',     'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_TAILORS_PLOT_HAS_BASE',            'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'MOD_CSC_TAILORS_BASE_IMPROV_CULTURE_TO_WORKSHOP',     'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_ADJ_IMP_BASE_PROD',   'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',        NULL,                                          'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE'   ),
        (   'MOD_CSC_TAILORS_PROD_TO_ADJ_BASE',                    'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',                 NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_ATTACH_HARBOR_LIGHTHOUSE',   'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           NULL,                                          'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE'   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_PROD_TO_LIGHTHOUSE',         'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_ATTACH_QUARTER_PROD',      'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           NULL,                                          'REQSET_CSC_ADJ_TAILORS_QUARTER'   ),
        (   'MOD_CSC_TAILORS_LIGHTHOUSE_PROD_TO_WORKSHOP',         'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_2_ART_PROPERTY',                'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                    'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',    NULL   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_TAILOR',          'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_WORKSHOP_CULTURE_TO_FASHION_HOUSE',   'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_TAILOR_PROD_TO_WORKSHOP',             'MODIFIER_BUILDING_YIELD_CHANGE',                          'REQSET_CSC_TAILORS_CITY_HAS_TAILOR',          NULL   ),
        (   'MOD_CSC_TAILORS_FASHION_HOUSE_PROD_TO_WORKSHOP',      'MODIFIER_BUILDING_YIELD_CHANGE',                          'REQSET_CSC_TAILORS_CITY_HAS_FASHION_HOUSE',   NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_ATTACH_HARBOR',       'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',    'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE'   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_GRANT',               'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',      NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP_ATTACH_HARBOR',        'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',    'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE'   ),
        (   'MOD_CSC_TAILORS_DOCKMASTER_GPP',                      'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',     NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_TAILOR_ATTACH_MARKET',                'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           NULL,                                          'REQSET_CSC_TAILORS_ADJ_MARKET'   ),
        (   'MOD_CSC_TAILORS_TAILOR_ATTACH_TEMPLE',                'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           NULL,                                          'REQSET_CSC_TAILORS_ADJ_TEMPLE'   ),
        (   'MOD_CSC_TAILORS_CUSTOMER_CULTURE',                    'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',   NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_3_ART_PROPERTY',                'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                    'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',    NULL   ),
        (   'MOD_CSC_TAILORS_TAILOR_SUPPLIED_PROPERTY',            'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                    'REQSET_CSC_TAILORS_STAGE_3_SUPPLY_PREREQ',    NULL   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_ATTACH_HOLY_SITE',    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',    'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE'   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_GRANT',               'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',      NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH_ATTACH_HOLY_SITE',    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',    'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH',                     'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_MODIFIER',         NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP_ATTACH_HOLY_SITE',      'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',    'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_GPP',                       'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',     NULL,                                          NULL   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_CULTURE',               'MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE',                NULL,                                          'REQSET_CSC_TAILORS_IMPORT_TAILOR_ROUTE'   ),
        (   'MOD_CSC_TAILORS_IMPORT_TAILOR_AMENITY',               'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',          NULL,                                          'REQSET_CSC_TAILORS_IMPORT_TAILOR_ROUTE'   ),
        (   'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION',            'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                          'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1'   );

INSERT OR IGNORE INTO Modifiers
		( ModifierId, ModifierType, OwnerRequirementSetId, SubjectRequirementSetId )
SELECT 'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_' || Bit,
	'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION', NULL,
	'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO Modifiers
		( ModifierId, ModifierType, OwnerRequirementSetId, SubjectRequirementSetId )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION_BIT_' || Bit,
	'MODIFIER_BUILDING_YIELD_CHANGE', NULL,
	'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO Modifiers
		( ModifierId, ModifierType, OwnerRequirementSetId, SubjectRequirementSetId )
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
		( ModifierId, ModifierType, OwnerRequirementSetId, SubjectRequirementSetId )
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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
        (   'MOD_CSC_TAILORS_STAGE_2_ART_PROPERTY',                'Key',                    'CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION'   ),
        (   'MOD_CSC_TAILORS_STAGE_2_ART_PROPERTY',                'Amount',                 1   ),
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
        (   'MOD_CSC_TAILORS_TAILOR_ATTACH_MARKET',                'ModifierId',             'MOD_CSC_TAILORS_CUSTOMER_CULTURE'   ),
        (   'MOD_CSC_TAILORS_TAILOR_ATTACH_TEMPLE',                'ModifierId',             'MOD_CSC_TAILORS_CUSTOMER_CULTURE'   ),
        (   'MOD_CSC_TAILORS_CUSTOMER_CULTURE',                    'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_TAILORS_CUSTOMER_CULTURE',                    'Amount',                 0.105   ),
        (   'MOD_CSC_TAILORS_STAGE_3_ART_PROPERTY',                'Key',                    'CSC_TAILORS_STAGE_3_CUSTOMERS'   ),
        (   'MOD_CSC_TAILORS_STAGE_3_ART_PROPERTY',                'Amount',                 1   ),
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
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_' || Bit, 'YieldType', 'YIELD_PRODUCTION'
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_CUSTOMER_RETURN_PROD_AMOUNT_BIT_' || Bit, 'Amount', Bit / 10000.0
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION_BIT_' || Bit, 'BuildingType', 'BUILDING_CSC_TAILORS_TAILOR'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION_BIT_' || Bit, 'YieldType', 'YIELD_PRODUCTION'
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_EXPORT_TAILOR_PRODUCTION_BIT_' || Bit, 'Amount', Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
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
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_' || REPLACE(EraType, 'ERA_', '') || '_' || REPLACE(PromotionClass, 'PROMOTION_CLASS_', ''), 'UnitPromotionClass', PromotionClass
FROM (
SELECT 'ERA_ANCIENT' AS EraType UNION ALL SELECT 'ERA_CLASSICAL' UNION ALL SELECT 'ERA_MEDIEVAL' UNION ALL SELECT 'ERA_RENAISSANCE'
)
CROSS JOIN (
SELECT 'PROMOTION_CLASS_NAVAL_MELEE' AS PromotionClass UNION ALL SELECT 'PROMOTION_CLASS_NAVAL_RANGED' UNION ALL SELECT 'PROMOTION_CLASS_NAVAL_RAIDER'
);

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
SELECT 'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_' || REPLACE(EraType, 'ERA_', '') || '_' || REPLACE(PromotionClass, 'PROMOTION_CLASS_', ''), 'EraType', EraType
FROM (
SELECT 'ERA_ANCIENT' AS EraType UNION ALL SELECT 'ERA_CLASSICAL' UNION ALL SELECT 'ERA_MEDIEVAL' UNION ALL SELECT 'ERA_RENAISSANCE'
)
CROSS JOIN (
SELECT 'PROMOTION_CLASS_NAVAL_MELEE' AS PromotionClass UNION ALL SELECT 'PROMOTION_CLASS_NAVAL_RANGED' UNION ALL SELECT 'PROMOTION_CLASS_NAVAL_RAIDER'
);

INSERT OR IGNORE INTO ModifierArguments
		( ModifierId, Name, Value )
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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,                                 RequirementSetType   )
VALUES  (   'REQSET_CSC_TAILORS_PLOT_HAS_BASE',               'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_PLOT_HAS_BASE',           'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_ADJ_TAILORS_QUARTER',                 'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HARBOR_LIGHTHOUSE',       'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ',       'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_CITY_HAS_TAILOR',             'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_CITY_HAS_FASHION_HOUSE',      'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_MARKET',                  'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_TEMPLE',                  'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_SUPPLY_PREREQ',       'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_STAGE_3_EFFECT_PREREQ',       'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_ADJ_HOLY_SITE_TEMPLE',        'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_IMPORT_TAILOR_ROUTE',         'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1',   'REQUIREMENTSET_TEST_ALL'   );

INSERT OR IGNORE INTO RequirementSets
		( RequirementSetId, RequirementSetType )
SELECT 'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementSets
		( RequirementSetId, RequirementSetType )
SELECT 'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit, 'REQUIREMENTSET_TEST_ALL'
FROM CSC_RouteStackBits
WHERE Bit > 1;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
        (   'REQSET_CSC_TAILORS_CITY_HAS_TAILOR',             'REQ_CSC_TAILORS_CITY_HAS_TAILOR'   ),
        (   'REQSET_CSC_TAILORS_CITY_HAS_FASHION_HOUSE',      'REQ_CSC_TAILORS_CITY_HAS_FASHION_HOUSE'   ),
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
		( RequirementSetId, RequirementId )
SELECT 'REQSET_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit,
	'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementSetRequirements
		( RequirementSetId, RequirementId )
SELECT 'REQSET_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit,
	'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
        (   'REQ_CSC_TAILORS_CITY_HAS_TAILOR',                    'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_FASHION_HOUSE',             'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_COMMERCIAL_HUB',         'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_TAILORS_DISTRICT_IS_HOLY_SITE',              'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_MARKET',                    'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_TEMPLE',                    'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_TAILORS_PLAYER_HAS_DIVINE_RIGHT',            'REQUIREMENT_PLAYER_HAS_CIVIC',             0   ),
        (   'REQ_CSC_TAILORS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_TAILORS_IMPORT_TAILOR_ROUTE',                'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_1',          'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   );

INSERT OR IGNORE INTO Requirements
		( RequirementId, RequirementType, Inverse )
SELECT 'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO Requirements
		( RequirementId, RequirementType, Inverse )
SELECT 'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit, 'REQUIREMENT_PLOT_PROPERTY_MATCHES', 0
FROM CSC_RouteStackBits
WHERE Bit > 1;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
        (   'REQ_CSC_TAILORS_CITY_HAS_TAILOR',                    'BuildingType',        'BUILDING_CSC_TAILORS_TAILOR'   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_TAILOR',                    'MustBeFunctioning',   1   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_FASHION_HOUSE',             'BuildingType',        'BUILDING_CSC_TAILORS_FASHION_HOUSE'   ),
        (   'REQ_CSC_TAILORS_CITY_HAS_FASHION_HOUSE',             'MustBeFunctioning',   1   ),
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
		( RequirementId, Name, Value )
SELECT 'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'PropertyName',
	'CSC_TAILORS_STAGE_3_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementArguments
		( RequirementId, Name, Value )
SELECT 'REQ_CSC_TAILORS_CUSTOMER_RETURN_AMOUNT_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementArguments
		( RequirementId, Name, Value )
SELECT 'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit, 'PropertyName',
	'CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits
WHERE Bit > 1;

INSERT OR IGNORE INTO RequirementArguments
		( RequirementId, Name, Value )
SELECT 'REQ_CSC_TAILORS_EXPORT_TAILOR_ROUTE_BIT_' || Bit, 'PropertyMinimum', 1
FROM CSC_RouteStackBits
WHERE Bit > 1;


--===========================================================================================================================================================================--
/*	UI */
--===========================================================================================================================================================================--

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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierStrings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO ModifierStrings
        (   ModifierId,                                                Context,     'Text'   )
VALUES  (   'MOD_CSC_TAILORS_DOCKMASTER_EFFECT_ANCIENT_NAVAL_MELEE',   'Preview',   'LOC_CSC_TAILORS_STAGE_2_EFFECT_DESCRIPTION'   ),
        (   'MOD_CSC_TAILORS_STAGE_2_SERVICE_GRANT',                   'Preview',   'LOC_BUILDING_CSC_TAILORS_STAGE_2_SERVICE_NAME'   ),
        (   'MOD_CSC_TAILORS_SACRISTAN_FAITH',                         'Preview',   'LOC_CSC_TAILORS_STAGE_3_EFFECT_DESCRIPTION'   ),
        (   'MOD_CSC_TAILORS_STAGE_3_SERVICE_GRANT',                   'Preview',   'LOC_BUILDING_CSC_TAILORS_STAGE_3_SERVICE_NAME'   );
