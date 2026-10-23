-- CSC_Q_BAKERS
-- Author: Henno
-- DateCreated: 2025-07-13 14:34:41
--------------------------------------------------------------

-- Reading this Quarter
-- Materials -> Water/Wind Mill -> Bakery -> Cafe -> customer Services and sales.
-- Core SQL owns Food/Production/Culture, buildings and eligibility. *_GOLD.sql
-- adds the parallel Gold effects; *_MC_MODE.sql adds Industry/Corporation behavior.
--
-- Follow an effect through four places: its Building/Improvement/DistrictModifiers
-- attachment, the Modifiers row, its ModifierArguments, then its requirement sets.
-- ATTACH rows find eligible receivers; the attached child performs the actual effect.
-- Customer-population and trade-route amounts are calculated by the shared Lua
-- scripts and consumed here as city-center plot properties.
--===========================================================================================================================================================================--
/*	TYPES */
--===========================================================================================================================================================================--

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



--===========================================================================================================================================================================--
/*	RESOURCES */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Material and customer vocabularies
-- BASE/SPEC select the resources used by supply checks. SALES and the yield-specific
-- sales tags select customer district families for the shared adjacency processor.
-- ModSupport adds to these tags, so downstream rules need no hard-coded mod lists.
INSERT OR IGNORE INTO Tags
        (   Tag,                                Vocabulary   )
VALUES  (   'CLASS_CSC_BAKERS_BASE',            'RESOURCE_CLASS'   ),
        (   'CLASS_CSC_BAKERS_SPEC',            'RESOURCE_CLASS'   ),
        (   'CLASS_CSC_BAKERS_SALES',           'DISTRICT_CLASS'   ),
        (   'CLASS_CSC_BAKERS_SALES_FOOD',      'DISTRICT_CLASS'   ),
        (   'CLASS_CSC_BAKERS_SALES_CULTURE',   'DISTRICT_CLASS'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	TypeTags
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO TypeTags
        (   Type,                                     Tag   )
VALUES

--	Bakers' Quarter base materials
        (   'RESOURCE_BANANAS',                       'CLASS_CSC_BAKERS_BASE'   ),
        (   'RESOURCE_MAIZE',                         'CLASS_CSC_BAKERS_BASE'   ),
        (   'RESOURCE_RICE',                          'CLASS_CSC_BAKERS_BASE'   ),
        (   'RESOURCE_WHEAT',                         'CLASS_CSC_BAKERS_BASE'   ),

--	Bakers' Quarter specialty materials
        (   'RESOURCE_COCOA',                         'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_COFFEE',                        'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_WINE',                          'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_OLIVES',                        'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_SALT',                          'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_SPICES',                        'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_SUGAR',                         'CLASS_CSC_BAKERS_SPEC'   ),
        (   'RESOURCE_TEA',                           'CLASS_CSC_BAKERS_SPEC'   ),

--	Bakers' Quarter sales districts
        (   'DISTRICT_CITY_CENTER',                   'CLASS_CSC_BAKERS_SALES'   ),
        (   'DISTRICT_CITY_CENTER',                   'CLASS_CSC_BAKERS_SALES_FOOD'   ),
        (   'DISTRICT_COMMERCIAL_HUB',                'CLASS_CSC_BAKERS_SALES'   ),
        (   'DISTRICT_COMMERCIAL_HUB',                'CLASS_CSC_BAKERS_SALES_FOOD'   ),
        (   'DISTRICT_ENTERTAINMENT_COMPLEX',         'CLASS_CSC_BAKERS_SALES'   ),
        (   'DISTRICT_ENTERTAINMENT_COMPLEX',         'CLASS_CSC_BAKERS_SALES_CULTURE'   ),
        (   'DISTRICT_WATER_ENTERTAINMENT_COMPLEX',   'CLASS_CSC_BAKERS_SALES'   ),
        (   'DISTRICT_WATER_ENTERTAINMENT_COMPLEX',   'CLASS_CSC_BAKERS_SALES_CULTURE'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	CSC_QuarterMaterialAdjacencyConfig
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO CSC_QuarterMaterialAdjacencyConfig
        (   QuarterKey,   SourceTag,                 SourceFilter,   YieldType,            YieldChange,   AdjacencyType   )
VALUES
--  The bundled CSC processor matches these TypeTags; ModSupport resources inherit the same adjacency rules.
        (   'BAKERS',     'CLASS_CSC_BAKERS_BASE',   '',             'YIELD_PRODUCTION',   1,             'FROM_RINGS_TYPETAG_RESOURCE'   ),
        (   'BAKERS',     'CLASS_CSC_BAKERS_SPEC',   '',             'YIELD_PRODUCTION',   1,             'FROM_RINGS_TYPETAG_RESOURCE'   );

-- Commercial Hub adjacency cards also double its Food return from Bakers.
-- This registry doubles the customer district's reciprocal return under its
-- normal adjacency policy. It is separate from doubling the Quarter's own Gold;
-- the late CSC adjacency processor builds the policy-gated rules.
INSERT OR IGNORE INTO CSC_QuarterPolicyAdjacencyConfig
        (   QuarterKey,   DistrictType,                PolicyType   )
VALUES  (   'BAKERS',     'DISTRICT_COMMERCIAL_HUB',   'POLICY_TOWN_CHARTERS'   ),
        (   'BAKERS',     'DISTRICT_COMMERCIAL_HUB',   'POLICY_ECONOMIC_UNION'   );

-- Stage 3 Bakery -> Market population sale. Bakery Food is paid through the
-- shared Lua amount bridge because several Bakery cities can supply one Market.
-- Market sales: population belongs to the customer, not the Bakery's city.
-- The registry names the seller's population/Production-return properties and
-- the customer's Food property. CSC_CustomerPopulationReturns.lua accumulates
-- all qualifying seller/site pairs, including same-city and cross-city sales.
-- The 0.105 is a per-customer-citizen target, not an integer yield per Market.
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
        'CSC_BAKERS_BAKERY_MARKET',
        'DISTRICT_CSC_BAKERS_QUARTER',
        'BUILDING_CSC_BAKERS_BAKERY',
        'DISTRICT_COMMERCIAL_HUB',
        'BUILDING_MARKET',
        'CSC_BAKERS_STAGE_3_MARKET_CUSTOMER_POP',
        'CSC_BAKERS_STAGE_3_MARKET_RETURN_AMOUNT',
        'CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT',
        0.105
    );



--===========================================================================================================================================================================--
/*	STAGE 1 - MATERIALS IMPROVEMENTS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ImprovementModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Two-way material exchange, first direction: the improvement is the owner.
-- Its BASE or SPEC tag gates the wrapper, which finds adjacent owned Quarters
-- and attaches Food to their Mill or Cafe. The reverse Production/Gold benefit
-- is owned by the producer building and is registered under BuildingModifiers.
-- Keeping the directions separate lets several neighboring producers contribute.
INSERT INTO ImprovementModifiers
        (   ImprovementType,            ModifierId   )
VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

--  +1 Food to the Water Mill from adjacent improved base materials
        (   'IMPROVEMENT_FARM',         'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER'   ),
        (   'IMPROVEMENT_PLANTATION',   'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER'   ),
        (   'IMPROVEMENT_PASTURE',      'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER'   ),

--  +1 Food to the Wind Mill from adjacent improved base materials
        (   'IMPROVEMENT_FARM',         'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND'   ),
        (   'IMPROVEMENT_PLANTATION',   'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND'   ),
        (   'IMPROVEMENT_PASTURE',      'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND'   ),

-- 	CAFE --------------------------------------------------------------------------

--  +1 Food to the Café from each adjacent improved specialty materials
        (   'IMPROVEMENT_CAMP',         'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_MINE',         'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   ),
        (   'IMPROVEMENT_PLANTATION',   'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER'   );



--===============================================================================================================================================================================--
/*	BAKERS' QUARTER */
--===============================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Districts
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- The Quarter is a district container; mills and later production stages are
-- separate buildings. Shared material/sales adjacency rules are generated later,
-- after both this file and compatible resource/customer tags have loaded.
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
        /*  DistrictType,               */  'DISTRICT_CSC_BAKERS_QUARTER',
        /*  Name,                       */  'LOC_DISTRICT_CSC_BAKERS_QUARTER_NAME',
        /*  Description,                */  'LOC_DISTRICT_CSC_BAKERS_QUARTER_DESCRIPTION',
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
        /*  CityStrengthModifier        */  2,
        /*  AdvisorType                 */  'ADVISOR_GENERIC'
    );

/*
UPDATE Districts SET Description = '{LOC_DISTRICT_COMMERCIAL_HUB_EXPANSION1_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_3_SERVICE}' WHERE DistrictType='DISTRICT_COMMERCIAL_HUB';
UPDATE Districts SET Description = '{LOC_DISTRICT_ENTERTAINMENT_COMPLEX_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SERVICE_ENTER}' WHERE DistrictType='DISTRICT_ENTERTAINMENT_COMPLEX';
UPDATE Districts SET Description = '{LOC_DISTRICT_STREET_CARNIVAL_EXPANSION2_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SERVICE_ENTER}' WHERE DistrictType='DISTRICT_STREET_CARNIVAL';
UPDATE Districts SET Description = '{LOC_DISTRICT_HIPPODROME_EXPANSION2_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SERVICE_ENTER}' WHERE DistrictType='DISTRICT_HIPPODROME';
UPDATE Districts SET Description = '{LOC_DISTRICT_WATER_ENTERTAINMENT_COMPLEX_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SERVICE_WATER}' WHERE DistrictType='DISTRICT_WATER_ENTERTAINMENT_COMPLEX';
UPDATE Districts SET Description = '{LOC_DISTRICT_WATER_STREET_CARNIVAL_EXPANSION2_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_4_REQUIREMENT}' || '{LOC_CSC_BAKERS_STAGE_4_SERVICE_WATER}' WHERE DistrictType='DISTRICT_WATER_STREET_CARNIVAL';
*/

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	DistrictModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Stage 4 branch registry
-- Each branch identifies the building that receives Culture from Cafe sales.
-- The same branch keys appear in Lua's customer scan and property names below;
-- keep both sides in step when adding a new customer family.
DROP TABLE IF EXISTS CSC_BakersStage4CultureBuildings;

-- This temp table is the source of truth for Stage 4 culture-return branches.
-- Each branch pairs a customer/capstone building with the generated bit-stack
-- modifiers below, so LGD Conservatory support can use the same pipeline without
-- duplicating Zoo/Ferris rows by hand.
CREATE TEMPORARY TABLE CSC_BakersStage4CultureBuildings
		(	Branch TEXT NOT NULL,
			BuildingType TEXT NOT NULL,
			PRIMARY KEY (Branch, BuildingType)	);

INSERT OR IGNORE INTO CSC_BakersStage4CultureBuildings
        (   Branch,     BuildingType   )
VALUES  (   'ZOO',      'BUILDING_ZOO'   ),
        (   'FERRIS',   'BUILDING_FERRIS_WHEEL'   );

-- Do not expand Zoo/Ferris unique replacements here: BUILDING_YIELD_CHANGE
-- already applies through BuildingReplaces, and explicit rows double the yield.
INSERT OR IGNORE INTO CSC_BakersStage4CultureBuildings
        (   Branch,   BuildingType   )
SELECT	'CONSERVATORY',				'BUILDING_LEU_CONSERVATORY'
WHERE EXISTS (SELECT 1 FROM Buildings WHERE BuildingType = 'BUILDING_LEU_CONSERVATORY');

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,                    ModifierId   )
VALUES

--  Set flags for river access, used by Water Mill and Wind Mill variants
        (   'DISTRICT_CSC_BAKERS_QUARTER',   'MOD_CSC_BAKERS_RIVER_ACCESS_FLAG'   ),
        (   'DISTRICT_CSC_BAKERS_QUARTER',   'MOD_CSC_BAKERS_NO_RIVER_ACCESS_FLAG'   ),

--  Import/export route properties are set on city-center plots by Lua.
--  These city-center modifiers apply the resulting exact trade-route transaction effects.
        (   'DISTRICT_CITY_CENTER',          'MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD'   ),
        (   'DISTRICT_CITY_CENTER',          'MOD_CSC_BAKERS_IMPORT_CONSUMER_AMENITY'   ),
        (   'DISTRICT_CITY_CENTER',          'MOD_CSC_BAKERS_IMPORT_SPECIALTY_FOOD'   ),
        (   'DISTRICT_CITY_CENTER',          'MOD_CSC_BAKERS_IMPORT_SPECIALTY_AMENITY'   ),
        (   'DISTRICT_CITY_CENTER',          'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION'   ),
        (   'DISTRICT_CITY_CENTER',          'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION'   );

--  Customer-population return stacks. Lua sums adjacent Market city population
--  and writes scaled per-population amount bits on City Center plots. This
--  preserves +0.105 yield per customer citizen while paying the current city.
-- Why these effects attach to City Center instead of Bakery/Market
-- Lua already sums every eligible transaction. One property consumer per receiving
-- city pays that sum once; attaching it again for each seller would multiply it.
-- Stage 3 bits encode a scaled per-population rate; Stage 4 bits encode whole stacks.
INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_MARKET_RETURN_PROD_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

--  Stage 4 customer-population returns. Lua sums +1 per 5 Citizens in
--  adjacent Zoo/Ferris/Conservatory customer cities, then writes integer
--  stack bits on the receiving City Center plot.
INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_PRODUCTION_BIT_' || Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_' || BuildingType || '_BIT_' || Bit
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;

--  Extra export-return stacks. The base modifier handles the +1 bit; these generated
--  rows add +2, +4, +8, and +16 when Lua sets the matching route-count bit.
INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION_BIT_' || Bit
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO DistrictModifiers
        (   DistrictType,   ModifierId   )
SELECT	'DISTRICT_CITY_CENTER',						'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION_BIT_' || Bit
FROM CSC_RouteStackBits;



--===========================================================================================================================================================================--
/*	STAGES 2-4 - BUILDINGS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
/*	WATER MILL & PALGUM */
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Remove the standard game Water Mill
-- The CSC Water Mill replaces the vanilla building's role rather than using a
-- BuildingReplaces entry. Detach Palgum's old replacement link as part of removing
-- the vanilla Water Mill; Palgum otherwise remains its own building.
DELETE FROM Buildings WHERE BuildingType='BUILDING_WATER_MILL';

-- Palgum no longer replaces the Water Mill
DELETE FROM BuildingReplaces WHERE CivUniqueBuildingType='BUILDING_PALGUM';

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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
        /*  BuildingType,   */  'BUILDING_CSC_BAKERS_RIVER_ACCESS',
        /*  Name,           */  'LOC_BUILDING_CSC_BAKERS_RIVER_ACCESS_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_BAKERS_RIVER_ACCESS_DESCRIPTION',
        /*  PrereqTech,     */  NULL,
        /*  PrereqCivic,    */  NULL,
        /*  Cost,           */  0,
        /*  PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /*  PurchaseYield,  */  NULL,
        /*  Maintenance,    */  0,
        /*  CitizenSlots    */  0,
        /*  Entertainment   */  0,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',
        /*  Name,           */  'LOC_BUILDING_CSC_BAKERS_NO_RIVER_ACCESS_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_BAKERS_NO_RIVER_ACCESS_DESCRIPTION',
        /*  PrereqTech,     */  NULL,
        /*  PrereqCivic,    */  NULL,
        /*  Cost,           */  0,
        /*  PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /*  PurchaseYield,  */  NULL,
        /*  Maintenance,    */  0,
        /*  CitizenSlots    */  0,
        /*  Entertainment   */  0,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_BAKERS_WIND_MILL',
        /*  Name,           */  'LOC_BUILDING_CSC_BAKERS_WIND_MILL_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_BAKERS_WIND_MILL_DESCRIPTION',
        /*  PrereqTech,     */  'TECH_MACHINERY',
        /*  PrereqCivic,    */  NULL,
        /*  Cost,           */  80,
        /*  PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /*  PurchaseYield,  */  'YIELD_GOLD',
        /*  Maintenance,    */  2,
        /*  CitizenSlots    */  0,
        /*  Entertainment   */  0,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_BAKERS_WATER_MILL',
        /*  Name,           */  'LOC_BUILDING_CSC_BAKERS_WATER_MILL_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_BAKERS_WATER_MILL_DESCRIPTION',
        /*  PrereqTech,     */  'TECH_ENGINEERING',
        /*  PrereqCivic,    */  NULL,
        /*  Cost,           */  80,
        /*  PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /*  PurchaseYield,  */  'YIELD_GOLD',
        /*  Maintenance,    */  2,
        /*  CitizenSlots    */  0,
        /*  Entertainment   */  0,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_BAKERS_BAKERY',
        /*  Name,           */  'LOC_BUILDING_CSC_BAKERS_BAKERY_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_BAKERS_BAKERY_DESCRIPTION',
        /*  PrereqTech,     */  NULL,
        /*  PrereqCivic,    */  'CIVIC_GUILDS',
        /*  Cost,           */  160,
        /*  PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /*  PurchaseYield,  */  'YIELD_GOLD',
        /*  Maintenance,    */  2,
        /*  CitizenSlots    */  1,
        /*  Entertainment   */  1,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_BAKERS_CAFE',
        /*  Name,           */  'LOC_BUILDING_CSC_BAKERS_CAFE_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION',
        /*  PrereqTech,     */  NULL,
        /*  PrereqCivic,    */  'CIVIC_HUMANISM',
        /*  Cost,           */  250,
        /*  PrereqDistrict, */  'DISTRICT_CSC_BAKERS_QUARTER',
        /*  PurchaseYield,  */  'YIELD_GOLD',
        /*  Maintenance,    */  3,
        /*  CitizenSlots    */  1,
        /*  Entertainment   */  1,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',
        /*  Name,           */  'LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_DESCRIPTION',
        /*  PrereqTech,     */  NULL,
        /*  PrereqCivic,    */  NULL,
        /*  Cost,           */  0,
        /*  PrereqDistrict, */  'DISTRICT_CITY_CENTER',
        /*  PurchaseYield,  */  NULL,
        /*  Maintenance,    */  0,
        /*  CitizenSlots    */  1,
        /*  Entertainment   */  0,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',
        /*  Name,           */  'LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_DESCRIPTION',
        /*  PrereqTech,     */  NULL,
        /*  PrereqCivic,    */  NULL,
        /*  Cost,           */  0,
        /*  PrereqDistrict, */  'DISTRICT_COMMERCIAL_HUB',
        /*  PurchaseYield,  */  NULL,
        /*  Maintenance,    */  0,
        /*  CitizenSlots    */  1,
        /*  Entertainment   */  0,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',
        /*  Name,           */  'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_DESCRIPTION',
        /*  PrereqTech,     */  NULL,
        /*  PrereqCivic,    */  NULL,
        /*  Cost,           */  0,
        /*  PrereqDistrict, */  'DISTRICT_ENTERTAINMENT_COMPLEX',
        /*  PurchaseYield,  */  NULL,
        /*  Maintenance,    */  0,
        /*  CitizenSlots    */  1,
        /*  Entertainment   */  0,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    ),
    (
        /*  BuildingType,   */  'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',
        /*  Name,           */  'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME',
        /*  Description,    */  'LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_DESCRIPTION',
        /*  PrereqTech,     */  NULL,
        /*  PrereqCivic,    */  NULL,
        /*  Cost,           */  0,
        /*  PrereqDistrict, */  'DISTRICT_WATER_ENTERTAINMENT_COMPLEX',
        /*  PurchaseYield,  */  NULL,
        /*  Maintenance,    */  0,
        /*  CitizenSlots    */  1,
        /*  Entertainment   */  0,
        /*  AdvisorType     */  'ADVISOR_GENERIC'
    );

-- RegionalRange controls the Cafe's regional building effect. It does not extend
-- the one-hex material/customer adjacency used by the supply-chain transactions.
UPDATE Buildings SET RegionalRange=6 WHERE BuildingType='BUILDING_CSC_BAKERS_CAFE';

-- The river flags and Service buildings are internal grants, not production
-- choices. MustPurchase keeps them out of ordinary construction; SQL grants them.
-- River flag buildings are also hidden from Civilopedia below.
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

INSERT INTO CivilopediaPageExcludes
        (   SectionId,     PageId   )
VALUES  (   'BUILDINGS',   'BUILDING_CSC_BAKERS_RIVER_ACCESS'   ),
        (   'BUILDINGS',   'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'   );

-- Append the customer's CSC effect to its existing description, preserving the
-- original localization key. Include direct unique replacements because their
-- own description does not automatically inherit this text update.
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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Buildings_XP2
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO Buildings_XP2
        (   BuildingType,                                  Pillage   )
VALUES  (   'BUILDING_CSC_BAKERS_RIVER_ACCESS',            0   ),
        (   'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS',         0   ),
        (   'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',         0   ),
        (   'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',         0   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',   0   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',   0   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingPrereqs
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Either Mill is the upstream production stage for Bakery and Cafe. The river
-- flag enables the Water Mill, while MutuallyExclusiveBuildings prevents owning
-- both Mill variants. These building unlocks are distinct from Service civic gates.
INSERT OR IGNORE INTO BuildingPrereqs
        (   Building,                           PrereqBuilding   )
VALUES  (   'BUILDING_CSC_BAKERS_WATER_MILL',   'BUILDING_CSC_BAKERS_RIVER_ACCESS'   ),

        (   'BUILDING_CSC_BAKERS_BAKERY',       'BUILDING_CSC_BAKERS_WIND_MILL'   ),
        (   'BUILDING_CSC_BAKERS_BAKERY',       'BUILDING_CSC_BAKERS_WATER_MILL'   ),

        (   'BUILDING_CSC_BAKERS_CAFE',         'BUILDING_CSC_BAKERS_WIND_MILL'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'BUILDING_CSC_BAKERS_WATER_MILL'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	MutuallyExclusiveBuildings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT OR IGNORE INTO MutuallyExclusiveBuildings
        (   Building,                           MutuallyExclusiveBuilding   )
VALUES  (   'BUILDING_CSC_BAKERS_WATER_MILL',   'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'   ),
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'BUILDING_CSC_BAKERS_WIND_MILL'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'BUILDING_CSC_BAKERS_WATER_MILL'   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Building_CitizenYieldChanges
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- These are yields per assigned specialist, not passive building income.
-- Intrinsic specialist stats stay with the building definitions, including Gold;
-- the Gold companion isolates the additional economic modifier layer.
INSERT INTO Building_CitizenYieldChanges
        (   BuildingType,                                  YieldType,         YieldChange   )
VALUES  (   'BUILDING_CSC_BAKERS_BAKERY',                  'YIELD_FOOD',      2   ),

        (   'BUILDING_CSC_BAKERS_CAFE',                    'YIELD_FOOD',      1   ),
        (   'BUILDING_CSC_BAKERS_CAFE',                    'YIELD_CULTURE',   1   ),

        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',   'YIELD_CULTURE',   2   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',   'YIELD_GOLD',      2   ),

        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',   'YIELD_CULTURE',   2   ),
        (   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',   'YIELD_GOLD',      2   );

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Two-way exchanges and Services, second direction: buildings own the wrappers.
-- A local producer-to-producer effect uses BUILDING_YIELD_CHANGE directly.
-- A cross-district exchange first selects adjacent owned recipients with ATTACH.
-- Service grants, the active benefit and Great Person points are separate children
-- so each has one unambiguous ModifierId link and the same eligibility gates.
INSERT INTO BuildingModifiers
        (   BuildingType,                       ModifierId   )
VALUES

--	WIND / WATER MILL -------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent base materials improvements

--  +1 Production to adjacent base materials improvements
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE_PROD'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE_PROD'   ),

--  +1 Food to the Water/Wind Mill from each adjacent base materials improvement handled by ImprovementModifiers above

-- 	+1 Food to an adjacent Granary (+1 Production return here, +1 Gold return moved to CSC_Q_BAKERS_GOLD.sql)
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER'   ),
        (   'BUILDING_GRANARY',                 'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER_PROD'   ),
        (   'BUILDING_GRANARY',                 'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND_PROD'   ),


--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth, gains a Storekeeper service
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND'   ),
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY'   ),
--  +1 Great Engineer point
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_STAGE_2_GPP_ATTACH_CITY'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_STAGE_2_GPP_ATTACH_CITY'   ),

--	BAKERY ------------------------------------------------------------------------------

--  +1 Production to the local Flour Mill
        (   'BUILDING_CSC_BAKERS_BAKERY',       'MOD_CSC_BAKERS_PROD_TO_WATER_MILL'   ),
        (   'BUILDING_CSC_BAKERS_BAKERY',       'MOD_CSC_BAKERS_PROD_TO_WIND_MILL'   ),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to the Flour Mill in the Quarter

--  +1 Food from the local Flour Mill
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY'   ),

--  Cache supplied Bakery status for route exports
        (   'BUILDING_CSC_BAKERS_BAKERY',       'MOD_CSC_BAKERS_EXPORT_BAKERY_SUPPLIED_PROP'   ),


--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
-- 	Grant the Stage 3 Service to a Commercial Hub with a Market
        (   'BUILDING_CSC_BAKERS_BAKERY',       'MOD_CSC_BAKERS_STAGE_3_SERVICE_ATTACH_COMHUB'   ),
--  Each adjacent Bakery grants the Stage 3 Service +2 Housing
        (   'BUILDING_CSC_BAKERS_BAKERY',       'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB'   ),
--  +1 Great Merchant point
        (   'BUILDING_CSC_BAKERS_BAKERY',       'MOD_CSC_BAKERS_STAGE_3_GPP_ATTACH_COMHUB'   ),

--	CAFE --------------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent specialty materials improvements

--  +1 Production to adjacent specialty materials improvements
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC_PROD'   ),

--  +1 Production to the local Flour Mill
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_PROD_TO_WATER_MILL'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_PROD_TO_WIND_MILL'   ),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to the Flour Mill in the Quarter

--  +1 Food from the local Flour Mill
        (   'BUILDING_CSC_BAKERS_WATER_MILL',   'MOD_CSC_BAKERS_FOOD_TO_CAFE'   ),
        (   'BUILDING_CSC_BAKERS_WIND_MILL',    'MOD_CSC_BAKERS_FOOD_TO_CAFE'   ),

--  Population sales use the city-center consumers above: customer Culture and
--  Cafe Production (+Gold in the companion) scale with each customer city.

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2 Tourism to an Entertainment Complex, Water Park
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK'   ),


-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_ENTER'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_WATER'   ),

--  +1 Great Engineer point
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_ENTER'   ),
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_WATER'   ),

--  Cache supplied Cafe status for route exports
        (   'BUILDING_CSC_BAKERS_CAFE',         'MOD_CSC_BAKERS_EXPORT_CAFE_SUPPLIED_PROP'   );

INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,   ModifierId   )
SELECT	CivUniqueBuildingType,							'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER_PROD'
FROM BuildingReplaces
WHERE ReplacesBuildingType='BUILDING_GRANARY';

INSERT OR IGNORE INTO BuildingModifiers
        (   BuildingType,   ModifierId   )
SELECT	CivUniqueBuildingType,							'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND_PROD'
FROM BuildingReplaces
WHERE ReplacesBuildingType='BUILDING_GRANARY';

--===========================================================================================================================================================================--
/*	CIVICS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Civics
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

UPDATE Civics SET Description = '{LOC_CIVIC_FEUDALISM_DESCRIPTION}' || '{LOC_CSC_BAKERS_STAGE_2_CIVIC}' WHERE CivicType = 'CIVIC_FEUDALISM';
UPDATE Civics SET Description = '{LOC_CSC_BAKERS_STAGE_3_CIVIC}' WHERE CivicType = 'CIVIC_MEDIEVAL_FAIRES';
UPDATE Civics SET Description = '{LOC_CSC_BAKERS_STAGE_4_CIVIC}' WHERE CivicType = 'CIVIC_URBANIZATION';



--===========================================================================================================================================================================--
/*	MODIFIERS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- How to read the two requirement columns
-- OwnerRequirementSetId tests the source improvement/building. SubjectRequirementSetId
-- tests each candidate receiver in the modifier's collection. A NULL on a child
-- usually means its parent wrapper already selected and gated that recipient.
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,                                               ModifierType,                                              OwnerRequirementSetId,                             SubjectRequirementSetId   )
VALUES

--	FLOUR MILL --------------------------------------------------------------------------

--  Set flags for river access, used by Water Mill and Wind Mill variants
        (   'MOD_CSC_BAKERS_RIVER_ACCESS_FLAG',                       'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',      NULL,                                              'REQSET_CSC_PLOT_ADJ_TO_RIVER'   ),
        (   'MOD_CSC_BAKERS_NO_RIVER_ACCESS_FLAG',                    'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',      NULL,                                              'REQSET_CSC_PLOT_NOT_ADJ_TO_RIVER'   ),

--  +1 Food to the Water Mill from adjacent improved base materials
        (   'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER',   'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_BAKERS_PLOT_HAS_BASE',                 'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WATER_MILL',      'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              NULL   ),

--  +1 Food to the Wind Mill from adjacent improved base materials
        (   'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND',    'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_BAKERS_PLOT_HAS_BASE',                 'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WIND_MILL',       'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              NULL   ),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent base materials improvements

--  +1 Production to adjacent base materials improvements
        (   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE_PROD',     'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',        NULL,                                              'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE'   ),
        (   'MOD_CSC_ALL_PROD_TO_PLOT',                               'MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS',                 NULL,                                              NULL   ),

-- 	+1 Food to an adjacent Granary (+1 Production return here, +1 Gold return moved to CSC_Q_BAKERS_GOLD.sql)
        (   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER',           'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           NULL,                                              'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'   ),
        (   'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',          'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER_PROD',        'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           NULL,                                              'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',                      'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND_PROD',         'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           NULL,                                              'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',                       'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              NULL   ),
--  Art bridge: the source property uses the same complete gate as the Storekeeper service

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth, gains a Storekeeper service
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',        'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER',             'MODIFIER_SINGLE_CITY_ADJUST_CITY_GROWTH',                 NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',         'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND',              'MODIFIER_SINGLE_CITY_ADJUST_CITY_GROWTH',                 NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY',             'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT',                   'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',      NULL,                                              NULL   ),

--  +1 Great Engineer point
        (   'MOD_CSC_BAKERS_STAGE_2_GPP_ATTACH_CITY',                 'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'   ),
        (   'MOD_CSC_BAKERS_STAGE_2+4_GPP',                           'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',     NULL,                                              NULL   ),

--	BAKERY ------------------------------------------------------------------------------

--  +1 Food from the local Flour Mill
        (   'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',               'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              NULL   ),

--  +0.105 Food per Citizen to adjacent Market cities
-- Legacy direct Market-Food definitions are retained here, but this wrapper is
-- not attached in the current BuildingModifiers list. Active Market Food comes
-- from the customer-owned amount-bit consumers above; do not wire both paths.
        (   'MOD_CSC_BAKERS_BAKERY_ATTACH_COMMERCIAL_HUB',            'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           NULL,                                              'REQSET_CSC_ADJ_MARKET'   ),
        (   'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET',                   'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',   NULL,                                              NULL   ),

--  Cache supplied Bakery status for route exports
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_SUPPLIED_PROP',             'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                    'REQSET_CSC_BAKERS_EXPORT_BAKERY_SUPPLY_PREREQ',   NULL   ),
--  Art bridge: the source property uses the same complete gate as the Innkeeper service

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
-- 	Grant the Stage 3 Service to a Commercial Hub with a Market
        (   'MOD_CSC_BAKERS_STAGE_3_SERVICE_ATTACH_COMHUB',           'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                'REQSET_CSC_ADJ_MARKET'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_SERVICE_GRANT',                   'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',      NULL,                                              NULL   ),
--  An adjacent Stage 3 Service provides +2 Housing
        (   'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',            'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                'REQSET_CSC_ADJ_MARKET'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING',                  'MODIFIER_SINGLE_CITY_ADJUST_BUILDING_HOUSING',            NULL,                                              NULL   ),
--  +1 Great Merchant point
        (   'MOD_CSC_BAKERS_STAGE_3_GPP_ATTACH_COMHUB',               'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                'REQSET_CSC_ADJ_MARKET'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_GPP',                             'MODIFIER_PLAYER_DISTRICT_ADJUST_GREAT_PERSON_POINTS',     NULL,                                              NULL   ),

-- 	CAFE --------------------------------------------------------------------------

--  +1 Food to the Café from each adjacent improved specialty materials
        (   'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER',         'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',                 'REQSET_CSC_ADJ_BAKERS_QUARTER'   ),
        (   'MOD_CSC_BAKERS_FOOD_TO_CAFE',                            'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              NULL   ),

--  +1 Production to adjacent specialty materials improvements
        (   'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC_PROD',           'MODIFIER_CSC_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER',        NULL,                                              'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC'   ),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent specialty materials improvements

--  Legacy direct Cafe yield children below have no active building attachment.
--  Current customer Culture/Cafe Production are paid by the Stage 4 bit consumers.
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',                     'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',                  'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_PRODUCTION_TO_CAFE',                      'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              NULL   ),
--  Art bridge: the source property uses the same complete gate as the Stage 4 services

--  Cache supplied Cafe status for route exports
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_SUPPLIED_PROP',               'MODIFIER_SINGLE_CITY_ADJUST_PROPERTY',                    'REQSET_CSC_BAKERS_EXPORT_CAFE_SUPPLY_PREREQ',     NULL   ),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',     'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER',            'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',          NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',        'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_WATER_PARK_FERRIS'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER',            'MODIFIER_PLAYER_DISTRICT_ADJUST_TOURISM_CHANGE',          NULL,                                              NULL   ),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_ENTER',            'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER',             'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',      NULL,                                              NULL   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_WATER',            'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_WATER_PARK_FERRIS'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER',             'MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE',      NULL,                                              NULL   ),

--  +1 Great Engineer point
        (   'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_ENTER',                'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_WATER',                'MODIFIER_CSC_PLAYER_DISTRICTS_ATTACH_MODIFIER',           'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                'REQSET_CSC_ADJ_WATER_PARK_FERRIS'   ),

-- 	SHARED ------------------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to the Flour Mill in the Quarter

--  Import/export route effects. Lua sets the route properties on city-center plots.
        (   'MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD',                    'MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE',                NULL,                                              'REQSET_CSC_BAKERS_IMPORT_CONSUMER_ROUTE'   ),
        (   'MOD_CSC_BAKERS_IMPORT_CONSUMER_AMENITY',                 'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',          NULL,                                              'REQSET_CSC_BAKERS_IMPORT_CONSUMER_ROUTE'   ),
        (   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_FOOD',                   'MODIFIER_SINGLE_CITY_ADJUST_YIELD_CHANGE',                NULL,                                              'REQSET_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE'   ),
        (   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_AMENITY',                'MODIFIER_CSC_SINGLE_CITY_ADJUST_IMPORT_AMENITY',          NULL,                                              'REQSET_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE'   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION',                'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1'   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION',                  'MODIFIER_BUILDING_YIELD_CHANGE',                          NULL,                                              'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1'   );

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT	'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION_BIT_' || Bit,					'MODIFIER_BUILDING_YIELD_CHANGE',							NULL,					'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT	'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION_BIT_' || Bit,					'MODIFIER_BUILDING_YIELD_CHANGE',							NULL,					'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_' || Bit
FROM CSC_RouteStackBits;

-- Customer population returns are too granular for direct integer yield rows:
-- Lua calculates the target decimal amount, scales it by 10000, then writes
-- active bit properties. These generated modifiers turn those bit properties
-- back into per-population yield increments.
INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT	'MOD_CSC_BAKERS_MARKET_RETURN_PROD_AMOUNT_BIT_' || Bit,					'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',	NULL,					'REQSET_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO Modifiers
        (   ModifierId,   ModifierType,   OwnerRequirementSetId,   SubjectRequirementSetId   )
SELECT	'MOD_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,						'MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION',	NULL,					'REQSET_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

-- Stage 4 returns are whole-number stacks (+1 per 5 Citizens in each eligible
-- customer city). They use the same property-bit pattern, but BUILDING_YIELD_CHANGE
-- targets the Bakery/Cafe or the relevant customer building directly.
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



-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Arguments complete the modifier graph: ModifierId links a wrapper to its child;
-- BuildingType/YieldType/Amount describe that child's effect. A shared child can
-- be reused by several gated wrappers; putting several ModifierId arguments on
-- one wrapper would not create several independent attached effects.
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,                                               Name,                     Value   )
VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

--  Set flags for river access, used by Water Mill and Wind Mill variants
        (   'MOD_CSC_BAKERS_RIVER_ACCESS_FLAG',                       'BuildingType',           'BUILDING_CSC_BAKERS_RIVER_ACCESS'   ),
        (   'MOD_CSC_BAKERS_NO_RIVER_ACCESS_FLAG',                    'BuildingType',           'BUILDING_CSC_BAKERS_NO_RIVER_ACCESS'   ),

--  +1 Food to the Water Mill from adjacent improved base materials
        (   'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WATER',   'ModifierId',             'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WATER_MILL'   ),
        (   'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WATER_MILL',      'BuildingType',           'BUILDING_CSC_BAKERS_WATER_MILL'   ),
        (   'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WATER_MILL',      'YieldType',              'YIELD_FOOD'   ),
        (   'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WATER_MILL',      'Amount',                 1   ),

--  +1 Food to the Wind Mill from adjacent improved base materials
        (   'MOD_CSC_BAKERS_BASE_IMPROVEMENT_ATTACH_QUARTER_WIND',    'ModifierId',             'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WIND_MILL'   ),
        (   'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WIND_MILL',       'BuildingType',           'BUILDING_CSC_BAKERS_WIND_MILL'   ),
        (   'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WIND_MILL',       'YieldType',              'YIELD_FOOD'   ),
        (   'MOD_CSC_BAKERS_BASE_IMPROV_FOOD_TO_ADJ_WIND_MILL',       'Amount',                 1   ),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent base materials improvements

--  +1 Production to adjacent base materials improvements
        (   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_ADJ_IMP_BASE_PROD',     'ModifierId',             'MOD_CSC_ALL_PROD_TO_PLOT'   ),
        (   'MOD_CSC_ALL_PROD_TO_PLOT',                               'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_ALL_PROD_TO_PLOT',                               'Amount',                 1   ),

-- 	+1 Food to an adjacent Granary (+1 Production return here, +1 Gold return moved to CSC_Q_BAKERS_GOLD.sql)
        (   'MOD_CSC_BAKERS_FLOUR_MILL_ATTACH_CITY_CENTER',           'ModifierId',             'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY'   ),
        (   'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',          'BuildingType',           'BUILDING_GRANARY'   ),
        (   'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',          'YieldType',              'YIELD_FOOD'   ),
        (   'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_ADJ_GRANARY',          'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WATER_PROD',        'ModifierId',             'MOD_CSC_BAKERS_PROD_TO_WATER_MILL'   ),
        (   'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',                      'BuildingType',           'BUILDING_CSC_BAKERS_WATER_MILL'   ),
        (   'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',                      'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_BAKERS_PROD_TO_WATER_MILL',                      'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_GRANARY_ATTACH_BAKERS_WIND_PROD',         'ModifierId',             'MOD_CSC_BAKERS_PROD_TO_WIND_MILL'   ),
        (   'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',                       'BuildingType',           'BUILDING_CSC_BAKERS_WIND_MILL'   ),
        (   'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',                       'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_BAKERS_PROD_TO_WIND_MILL',                       'Amount',                 1   ),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth, gains a Storekeeper service
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',        'ModifierId',             'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER',             'Amount',                 10   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',         'ModifierId',             'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND',              'Amount',                 10   ),
        (   'MOD_CSC_BAKERS_STAGE_2_SERVICE_ATTACH_CITY',             'ModifierId',             'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_SERVICE_GRANT',                   'BuildingType',           'BUILDING_CSC_BAKERS_STAGE_2_SERVICE'   ),


--  +1 Great Engineer point
        (   'MOD_CSC_BAKERS_STAGE_2_GPP_ATTACH_CITY',                 'ModifierId',             'MOD_CSC_BAKERS_STAGE_2+4_GPP'   ),
        (   'MOD_CSC_BAKERS_STAGE_2+4_GPP',                           'GreatPersonClassType',   'GREAT_PERSON_CLASS_ENGINEER'   ),
        (   'MOD_CSC_BAKERS_STAGE_2+4_GPP',                           'Amount',                 '1'   ),

--	BAKERY ------------------------------------------------------------------------------

--  +1 Food from the local Flour Mill
        (   'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',               'BuildingType',           'BUILDING_CSC_BAKERS_BAKERY'   ),
        (   'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',               'YieldType',              'YIELD_FOOD'   ),
        (   'MOD_CSC_BAKERS_FLOUR_MILL_FOOD_TO_BAKERY',               'Amount',                 1   ),

--  +0.105 Food per Citizen to adjacent Market cities
        (   'MOD_CSC_BAKERS_BAKERY_ATTACH_COMMERCIAL_HUB',            'ModifierId',             'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET'   ),
        (   'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET',                   'YieldType',              'YIELD_FOOD'   ),
        (   'MOD_CSC_BAKERS_BAKERY_FOOD_TO_MARKET',                   'Amount',                 0.105   ),

--  Cache supplied Bakery status for route exports
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_SUPPLIED_PROP',             'Key',                    'CSC_BAKERS_BAKERY_SUPPLIED'   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_SUPPLIED_PROP',             'Amount',                 1   ),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
-- 	Grant the Stage 3 Service to a Commercial Hub with a Market
        (   'MOD_CSC_BAKERS_STAGE_3_SERVICE_ATTACH_COMHUB',           'ModifierId',             'MOD_CSC_BAKERS_STAGE_3_SERVICE_GRANT'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_SERVICE_GRANT',                   'BuildingType',           'BUILDING_CSC_BAKERS_STAGE_3_SERVICE'   ),
--  An adjacent Market provides +2 Housing
        (   'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',            'ModifierId',             'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_EFFECT_HOUSING',                  'Amount',                 2   ),
--  +1 Great Merchant point
        (   'MOD_CSC_BAKERS_STAGE_3_GPP_ATTACH_COMHUB',               'ModifierId',             'MOD_CSC_BAKERS_STAGE_3_GPP'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_GPP',                             'GreatPersonClassType',   'GREAT_PERSON_CLASS_MERCHANT'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_GPP',                             'Amount',                 '1'   ),

-- 	CAFE --------------------------------------------------------------------------

--  +1 Food to the Café from each adjacent improved specialty materials
        (   'MOD_CSC_BAKERS_SPEC_IMPROVEMENT_ATTACH_QUARTER',         'ModifierId',             'MOD_CSC_BAKERS_FOOD_TO_CAFE'   ),
        (   'MOD_CSC_BAKERS_FOOD_TO_CAFE',                            'BuildingType',           'BUILDING_CSC_BAKERS_CAFE'   ),
        (   'MOD_CSC_BAKERS_FOOD_TO_CAFE',                            'YieldType',              'YIELD_FOOD'   ),
        (   'MOD_CSC_BAKERS_FOOD_TO_CAFE',                            'Amount',                 1   ),

--  +1 Production to adjacent specialty materials improvements
        (   'MOD_CSC_BAKERS_CAFE_ATTACH_ADJ_IMP_SPEC_PROD',           'ModifierId',             'MOD_CSC_ALL_PROD_TO_PLOT'   ),

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to adjacent specialty materials improvements

--  +1 Culture for every 5 Citizens in the city for each adjacent Zoo or Ferris Wheel (+1 Gold moved to CSC_Q_BAKERS_GOLD.sql)
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',                     'BuildingType',           'BUILDING_ZOO'   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',                     'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_ZOO',                     'Amount',                 1   ),

        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',                  'BuildingType',           'BUILDING_FERRIS_WHEEL'   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',                  'YieldType',              'YIELD_CULTURE'   ),
        (   'MOD_CSC_BAKERS_CAFE_CULTURE_TO_FERRIS',                  'Amount',                 1   ),

        (   'MOD_CSC_BAKERS_PRODUCTION_TO_CAFE',                      'BuildingType',           'BUILDING_CSC_BAKERS_CAFE'   ),
        (   'MOD_CSC_BAKERS_PRODUCTION_TO_CAFE',                      'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_BAKERS_PRODUCTION_TO_CAFE',                      'Amount',                 1   ),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',     'ModifierId',             'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ENTER',            'Amount',                 2   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',        'ModifierId',             'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_TOURISM_WATER',            'Amount',                 2   ),

--  Cache supplied Cafe status for route exports
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_SUPPLIED_PROP',               'Key',                    'CSC_BAKERS_CAFE_SUPPLIED'   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_SUPPLIED_PROP',               'Amount',                 1   ),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_ENTER',            'ModifierId',             'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_ENTER',             'BuildingType',           'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_ATTACH_WATER',            'ModifierId',             'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_SERVICE_GRANT_WATER',             'BuildingType',           'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER'   ),

--  +1 Great Engineer point
        (   'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_ENTER',                'ModifierId',             'MOD_CSC_BAKERS_STAGE_2+4_GPP'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_GPP_ATTACH_WATER',                'ModifierId',             'MOD_CSC_BAKERS_STAGE_2+4_GPP'   ),

-- 	SHARED ------------------------------------------------------------------------------

-- Moved to CSC_Q_BAKERS_GOLD.sql: +1 Gold to the Flour Mill in the Quarter

--  Import/export route effects. Lua sets the route properties on city-center plots.
        (   'MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD',                    'YieldType',              'YIELD_FOOD'   ),
        (   'MOD_CSC_BAKERS_IMPORT_CONSUMER_FOOD',                    'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_IMPORT_CONSUMER_AMENITY',                 'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_FOOD',                   'YieldType',              'YIELD_FOOD'   ),
        (   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_FOOD',                   'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_IMPORT_SPECIALTY_AMENITY',                'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION',                'BuildingType',           'BUILDING_CSC_BAKERS_BAKERY'   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION',                'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_BAKERS_EXPORT_BAKERY_PRODUCTION',                'Amount',                 1   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION',                  'BuildingType',           'BUILDING_CSC_BAKERS_CAFE'   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION',                  'YieldType',              'YIELD_PRODUCTION'   ),
        (   'MOD_CSC_BAKERS_EXPORT_CAFE_PRODUCTION',                  'Amount',                 1   );

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

-- The Amount values below divide by AMOUNT_SCALE from
-- CSC_CustomerPopulationReturns.lua. For example, a stored bit of 256 becomes
-- 0.0256 yield per population when this modifier is active.
INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_MARKET_RETURN_PROD_AMOUNT_BIT_' || Bit,					'YieldType',				'YIELD_PRODUCTION'
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_MARKET_RETURN_PROD_AMOUNT_BIT_' || Bit,					'Amount',					Bit / 10000.0
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,							'YieldType',				'YIELD_FOOD'
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,							'Amount',					Bit / 10000.0
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_PRODUCTION_BIT_' || Bit,				'BuildingType',				'BUILDING_CSC_BAKERS_CAFE'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_PRODUCTION_BIT_' || Bit,				'YieldType',				'YIELD_PRODUCTION'
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_STAGE_4_CAFE_RETURN_PRODUCTION_BIT_' || Bit,				'Amount',					Bit
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_' || BuildingType || '_BIT_' || Bit,
		'BuildingType',
		BuildingType
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_' || BuildingType || '_BIT_' || Bit,
		'YieldType',
		'YIELD_CULTURE'
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;

INSERT OR IGNORE INTO ModifierArguments
        (   ModifierId,   Name,   Value   )
SELECT	'MOD_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_' || BuildingType || '_BIT_' || Bit,
		'Amount',
		Bit
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;



--===========================================================================================================================================================================--
/*	REQUIREMENTS */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSets
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Requirement sets are named gates, not effects by themselves.
-- TEST_ALL combines prerequisites with AND. The Stage 4 customer TEST_ANY set
-- combines alternative venues with OR, then sits inside the full producer gate.
-- The membership rows below supply the actual checks for these named sets.
INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,                                   RequirementSetType   )
VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

--  Set flags for river access, used by Water Mill and Wind Mill variants
        (   'REQSET_CSC_PLOT_ADJ_TO_RIVER',                     'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_PLOT_NOT_ADJ_TO_RIVER',                 'REQUIREMENTSET_TEST_ALL'   ),

-- 	+1 Production from each adjacent base materials improvement
        (   'REQSET_CSC_BAKERS_PLOT_HAS_BASE',                  'REQUIREMENTSET_TEST_ALL'   ),

--  Helper set for improved adjacent base materials prerequisite
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE',              'REQUIREMENTSET_TEST_ALL'   ),

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
        (   'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',               'REQUIREMENTSET_TEST_ALL'   ),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
--  Storekeeper belongs to the adjacent Granary; Market/Innkeeper is the Stage 3 branch.
        (   'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                 'REQUIREMENTSET_TEST_ALL'   ),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.105 Food per Citizen to adjacent Market cities
        (   'REQSET_CSC_ADJ_MARKET',                            'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_ADJ_BAKERY_STAGE_3_RETURN',             'REQUIREMENTSET_TEST_ALL'   ),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
--  An adjacent Market provides +2 Housing
        (   'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                 'REQUIREMENTSET_TEST_ALL'   ),

-- 	CAFE --------------------------------------------------------------------------

-- 	+1 Food to the Café from each adjacent specialty materials improvement
        (   'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',                  'REQUIREMENTSET_TEST_ALL'   ),

--  Helper set for adjacent specialty material improvement yields from the Café
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC',              'REQUIREMENTSET_TEST_ALL'   ),

--  Each eligible adjacent customer contributes floor(its population / 5) stacks.
--  Culture goes to the customer building; Production/Gold return to the Cafe.
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX',             'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK',                        'REQUIREMENTSET_TEST_ALL'   ),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
        (   'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                 'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY',   'REQUIREMENTSET_TEST_ANY'   ),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',         'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK_FERRIS',                 'REQUIREMENTSET_TEST_ALL'   ),

-- 	SHARED ------------------------------------------------------------------------------

--  Import/export route properties
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_SUPPLY_PREREQ',    'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_SUPPLY_PREREQ',      'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_IMPORT_CONSUMER_ROUTE',          'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',         'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE',            'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE',              'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1',      'REQUIREMENTSET_TEST_ALL'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1',        'REQUIREMENTSET_TEST_ALL'   ),

        (   'REQSET_CSC_ADJ_BAKERS_QUARTER',                    'REQUIREMENTSET_TEST_ALL'   );

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT	'REQSET_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit,		'REQUIREMENTSET_TEST_ALL'
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementSets
        (   RequirementSetId,   RequirementSetType   )
SELECT	'REQSET_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,			'REQUIREMENTSET_TEST_ALL'
FROM CSC_ScaledAmountBits;

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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementSetRequirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Service gates combine the civic, improved material supply and an adjacent
-- customer with its capstone building. An improvement collection establishes
-- that the material is improved; the nested plot set checks its tag and adjacency.
-- The same complete gates also drive the expanded-building art flags at the end.
INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,                                   RequirementId   )
VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

--  Set flags for river access, used by Water Mill and Wind Mill variants
        (   'REQSET_CSC_PLOT_ADJ_TO_RIVER',                     'REQ_CSC_PLOT_ADJ_TO_RIVER'   ),
        (   'REQSET_CSC_PLOT_NOT_ADJ_TO_RIVER',                 'REQ_CSC_PLOT_NOT_ADJ_TO_RIVER'   ),

-- 	+1 Production from each adjacent base materials improvement
        (   'REQSET_CSC_BAKERS_PLOT_HAS_BASE',                  'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'   ),

--  Helper set for improved adjacent base materials prerequisite
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE',              'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE',              'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE'   ),

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
        (   'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',               'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',               'REQ_CSC_DISTRICT_IS_CITY_CENTER'   ),
        (   'REQSET_CSC_ADJ_CITY_CENTER_GRANARY',               'REQ_CSC_CITY_HAS_GRANARY'   ),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
--  Storekeeper belongs to the adjacent Granary; Market/Innkeeper is the Stage 3 branch.
        (   'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                 'REQ_CSC_STAGE_2_EFFECT_TECH_OR_CIVIC'   ),
        (   'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_STAGE_2_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER'   ),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.105 Food to adjacent Market cities; +0.105 Production and +0.105 Gold returns to Bakery city per Citizen
        (   'REQSET_CSC_ADJ_MARKET',                            'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_ADJ_MARKET',                            'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB'   ),
        (   'REQSET_CSC_ADJ_MARKET',                            'REQ_CSC_CITY_HAS_MARKET'   ),

-- Shared with CSC_Q_BAKERS_GOLD.sql: inverse Market-to-Bakery adjacency requirements

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
--  An adjacent Market provides +2 Housing
        (   'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                 'REQ_CSC_STAGE_3_EFFECT_TECH_OR_CIVIC'   ),
        (   'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_STAGE_3_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER'   ),

        (   'REQSET_CSC_ADJ_BAKERY_STAGE_3_RETURN',             'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'   ),
        (   'REQSET_CSC_ADJ_BAKERY_STAGE_3_RETURN',             'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_ADJ_BAKERY_STAGE_3_RETURN',             'REQ_CSC_CITY_HAS_BAKERY'   ),

-- 	CAFE --------------------------------------------------------------------------

-- 	+1 Production from each adjacent specialty materials improvement
        (   'REQSET_CSC_BAKERS_PLOT_HAS_SPEC',                  'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'   ),

--  Helper set for improved adjacent specialty materials prerequisite
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC',              'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC',              'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC'   ),

--  Each eligible adjacent customer contributes floor(its population / 5) stacks.
--  Culture goes to the customer building; Production/Gold return to the Cafe.
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX',             'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX',             'REQ_CSC_DISTRICT_IS_ENTERTAINMENT_COMPLEX'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK',                        'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK',                        'REQ_CSC_DISTRICT_IS_WATER_PARK'   ),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
        (   'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                 'REQ_CSC_STAGE_4_EFFECT_TECH_OR_CIVIC'   ),
        (   'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC'   ),
        (   'REQSET_CSC_STAGE_4_EFFECT_PREREQ',                 'REQ_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY'   ),
        (   'REQSET_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY',   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_ENTER_CUSTOMER'   ),
        (   'REQSET_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY',   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_WATER_CUSTOMER'   ),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',         'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX'   ),
        (   'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO',         'REQ_CSC_CITY_HAS_ZOO'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK_FERRIS',                 'REQ_CSC_ADJ_WATER_PARK'   ),
        (   'REQSET_CSC_ADJ_WATER_PARK_FERRIS',                 'REQ_CSC_CITY_HAS_FERRIS'   ),

-- 	SHARED ------------------------------------------------------------------------------
-- Moved to CSC_Q_BAKERS_GOLD.sql: REQSET_CSC_BAKERS_ADJ_PLOT_HAS_MATERIAL_ANY, REQSET_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY requirements

--  Import/export route properties
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_SUPPLY_PREREQ',    'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_SUPPLY_PREREQ',      'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_SUPPLY_PREREQ',      'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC'   ),
        (   'REQSET_CSC_BAKERS_IMPORT_CONSUMER_ROUTE',          'REQ_CSC_BAKERS_IMPORT_CONSUMER_ROUTE'   ),
        (   'REQSET_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',         'REQ_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE',            'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE',              'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1',      'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1'   ),
        (   'REQSET_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1',        'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1'   ),

        (   'REQSET_CSC_ADJ_BAKERS_QUARTER',                    'REQ_CSC_PLOT_ADJ_TO_OWNER'   ),
        (   'REQSET_CSC_ADJ_BAKERS_QUARTER',                    'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER'   );

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
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementSetRequirements
        (   RequirementSetId,   RequirementId   )
SELECT	'REQSET_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,			'REQ_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

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

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Requirements
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Requirements declare each test's native type. RequirementArguments below
-- supply its resource tag, building/civic, nested set, distance or property name.
-- Collection-count tests mean at least one qualifying adjacent object, not a
-- request to add that many copies of the Service effect.
INSERT OR IGNORE INTO Requirements
        (   RequirementId,                                       RequirementType,                            Inverse   )
VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

--  Set flags for river access, used by Water Mill and Wind Mill variants
        (   'REQ_CSC_PLOT_ADJ_TO_RIVER',                         'REQUIREMENT_PLOT_ADJACENT_TO_RIVER',       0   ),
        (   'REQ_CSC_PLOT_NOT_ADJ_TO_RIVER',                     'REQUIREMENT_PLOT_ADJACENT_TO_RIVER',       1   ),

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
        (   'REQ_CSC_DISTRICT_IS_CITY_CENTER',                   'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_CITY_HAS_GRANARY',                          'REQUIREMENT_CITY_HAS_BUILDING',            0   ),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
        (   'REQ_CSC_STAGE_2_EFFECT_TECH_OR_CIVIC',              'REQUIREMENT_PLAYER_HAS_CIVIC',             0   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.105 Food to adjacent Market cities
        (   'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB',                'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_CITY_HAS_MARKET',                           'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_CITY_HAS_BAKERY',                           'REQUIREMENT_CITY_HAS_BUILDING',            0   ),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
--  An adjacent Market provides +2 Housing
-- 	+1 Citizen slot (Innkeeper) to a Commercial Hub with a Market
        (   'REQ_CSC_STAGE_3_EFFECT_TECH_OR_CIVIC',              'REQUIREMENT_PLAYER_HAS_CIVIC',             0   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),

-- 	CAFE --------------------------------------------------------------------------

--  Each eligible adjacent customer contributes floor(its population / 5) stacks.
--  Culture goes to the customer building; Production/Gold return to the Cafe.
        (   'REQ_CSC_DISTRICT_IS_ENTERTAINMENT_COMPLEX',         'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
        (   'REQ_CSC_DISTRICT_IS_WATER_PARK',                    'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
        (   'REQ_CSC_STAGE_4_EFFECT_TECH_OR_CIVIC',              'REQUIREMENT_PLAYER_HAS_CIVIC',             0   ),
        (   'REQ_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY',       'REQUIREMENT_REQUIREMENTSET_IS_MET',        0   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_ENTER_CUSTOMER',     'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_WATER_CUSTOMER',     'REQUIREMENT_COLLECTION_COUNT_ATLEAST',     0   ),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
        (   'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX',                 'REQUIREMENT_REQUIREMENTSET_IS_MET',        0   ),
        (   'REQ_CSC_CITY_HAS_ZOO',                              'REQUIREMENT_CITY_HAS_BUILDING',            0   ),
        (   'REQ_CSC_ADJ_WATER_PARK',                            'REQUIREMENT_REQUIREMENTSET_IS_MET',        0   ),
        (   'REQ_CSC_CITY_HAS_FERRIS',                           'REQUIREMENT_CITY_HAS_BUILDING',            0   ),

-- 	SHARED ------------------------------------------------------------------------------

--  Import/export route properties
        (   'REQ_CSC_BAKERS_IMPORT_CONSUMER_ROUTE',              'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',             'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE',                'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE',                  'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1',          'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1',            'REQUIREMENT_PLOT_PROPERTY_MATCHES',        0   ),

        (   'REQ_CSC_PLOT_ADJ_TO_OWNER',                         'REQUIREMENT_PLOT_ADJACENT_TO_OWNER',       0   ),
        (   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',             'REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES',    0   ),
        (   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC',             'REQUIREMENT_PLOT_RESOURCE_TAG_MATCHES',    0   ),
        (   'REQ_CSC_PLOT_HAS_ANY_IMPROVEMENT',                  'REQUIREMENT_PLOT_HAS_ANY_IMPROVEMENT',     0   ),
        (   'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',                'REQUIREMENT_PLOT_DISTRICT_TYPE_MATCHES',   0   ),
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
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT	'REQ_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,					'REQUIREMENT_PLOT_PROPERTY_MATCHES',			0
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT	'REQ_CSC_BAKERS_STAGE_4_CAFE_RETURN_BIT_' || Bit,					'REQUIREMENT_PLOT_PROPERTY_MATCHES',			0
FROM CSC_Stage4StackBits;

INSERT OR IGNORE INTO Requirements
        (   RequirementId,   RequirementType,   Inverse   )
SELECT	'REQ_CSC_BAKERS_STAGE_4_' || Branch || '_CULTURE_RETURN_BIT_' || Bit,	'REQUIREMENT_PLOT_PROPERTY_MATCHES',		0
FROM CSC_BakersStage4CultureBuildings
CROSS JOIN CSC_Stage4StackBits;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	RequirementArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Keep the owner/subject direction in mind for adjacency tests: "owner" is the
-- source of the current wrapper. Property tests in the generated return chains
-- read the receiving city-center plot written by Lua, not a resource plot.
INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,                                       Name,                  Value   )
VALUES

-- 	FLOUR MILL --------------------------------------------------------------------------

-- 	+1 Food to an adjacent Granary, and +1 Gold in return
        (   'REQ_CSC_DISTRICT_IS_CITY_CENTER',                   'DistrictType',        'DISTRICT_CITY_CENTER'   ),
        (   'REQ_CSC_CITY_HAS_GRANARY',                          'BuildingType',        'BUILDING_GRANARY'   ),
        (   'REQ_CSC_CITY_HAS_GRANARY',                          'MustBeFunctioning',   1   ),

--  At Feudalism, a Water Mill or Wind Mill adjacent to an improved base materials resource unlocks:
--  An adjacent Granary provides +10% growth in the city
        (   'REQ_CSC_STAGE_2_EFFECT_TECH_OR_CIVIC',              'CivicType',           'CIVIC_FEUDALISM'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'CollectionType',      'COLLECTION_PLAYER_DISTRICTS'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'Count',               1   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_2_SERVICE_CUSTOMER',   'RequirementSetId',    'REQSET_CSC_ADJ_CITY_CENTER_GRANARY'   ),

-- 	BAKERY ------------------------------------------------------------------------------

--  +0.105 Food to adjacent Market cities
        (   'REQ_CSC_DISTRICT_IS_COMMERCIAL_HUB',                'DistrictType',        'DISTRICT_COMMERCIAL_HUB'   ),
        (   'REQ_CSC_CITY_HAS_MARKET',                           'BuildingType',        'BUILDING_MARKET'   ),
        (   'REQ_CSC_CITY_HAS_BAKERY',                           'BuildingType',        'BUILDING_CSC_BAKERS_BAKERY'   ),

--  At Medieval Faires, a Bakery adjacent to an improved base materials resource unlocks:
--  An adjacent Market provides +2 Housing
--  Storekeeper belongs to the adjacent Granary; Market/Innkeeper is the Stage 3 branch.
        (   'REQ_CSC_STAGE_3_EFFECT_TECH_OR_CIVIC',              'CivicType',           'CIVIC_MEDIEVAL_FAIRES'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'CollectionType',      'COLLECTION_PLAYER_DISTRICTS'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'Count',               1   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_3_SERVICE_CUSTOMER',   'RequirementSetId',    'REQSET_CSC_ADJ_MARKET'   ),

-- 	CAFE --------------------------------------------------------------------------

--  Each eligible adjacent customer contributes floor(its population / 5) stacks.
--  Culture goes to the customer building; Production/Gold return to the Cafe.
        (   'REQ_CSC_DISTRICT_IS_ENTERTAINMENT_COMPLEX',         'DistrictType',        'DISTRICT_ENTERTAINMENT_COMPLEX'   ),
        (   'REQ_CSC_DISTRICT_IS_WATER_PARK',                    'DistrictType',        'DISTRICT_WATER_ENTERTAINMENT_COMPLEX'   ),

--  At Urbanization, a Café adjacent to improved base and speciality materials resources unlocks:
--  +2  Tourism to an Entertainment Complex, Water Park
        (   'REQ_CSC_STAGE_4_EFFECT_TECH_OR_CIVIC',              'CivicType',           'CIVIC_URBANIZATION'   ),
        (   'REQ_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY',       'RequirementSetId',    'REQSET_CSC_BAKERS_STAGE_4_SERVICE_CUSTOMER_ANY'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_ENTER_CUSTOMER',     'CollectionType',      'COLLECTION_PLAYER_DISTRICTS'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_ENTER_CUSTOMER',     'Count',               1   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_ENTER_CUSTOMER',     'RequirementSetId',    'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX_ZOO'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_WATER_CUSTOMER',     'CollectionType',      'COLLECTION_PLAYER_DISTRICTS'   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_WATER_CUSTOMER',     'Count',               1   ),
        (   'REQ_CSC_BAKERS_HAS_ADJ_STAGE_4_WATER_CUSTOMER',     'RequirementSetId',    'REQSET_CSC_ADJ_WATER_PARK_FERRIS'   ),

-- 	+1 Citizen slot from the relevant Stage 4 service: Groundskeeper for Zoo districts, Ride Technician for Ferris Wheel districts
        (   'REQ_CSC_ADJ_ENTERTAINMENT_COMPLEX',                 'RequirementSetId',    'REQSET_CSC_ADJ_ENTERTAINMENT_COMPLEX'   ),
        (   'REQ_CSC_CITY_HAS_ZOO',                              'BuildingType',        'BUILDING_ZOO'   ),
        (   'REQ_CSC_ADJ_WATER_PARK',                            'RequirementSetId',    'REQSET_CSC_ADJ_WATER_PARK'   ),
        (   'REQ_CSC_CITY_HAS_FERRIS',                           'BuildingType',        'BUILDING_FERRIS_WHEEL'   ),

-- 	SHARED ------------------------------------------------------------------------------

--  Import/export route properties
        (   'REQ_CSC_BAKERS_IMPORT_CONSUMER_ROUTE',              'PropertyName',        'CSC_BAKERS_IMPORT_CONSUMER_ROUTE'   ),
        (   'REQ_CSC_BAKERS_IMPORT_CONSUMER_ROUTE',              'PropertyMinimum',     1   ),
        (   'REQ_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',             'PropertyName',        'CSC_BAKERS_IMPORT_SPECIALTY_ROUTE'   ),
        (   'REQ_CSC_BAKERS_IMPORT_SPECIALTY_ROUTE',             'PropertyMinimum',     1   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE',                'PropertyName',        'CSC_BAKERS_EXPORT_BAKERY_ROUTE'   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE',                'PropertyMinimum',     1   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE',                  'PropertyName',        'CSC_BAKERS_EXPORT_CAFE_ROUTE'   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE',                  'PropertyMinimum',     1   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1',          'PropertyName',        'CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1'   ),
        (   'REQ_CSC_BAKERS_EXPORT_BAKERY_ROUTE_BIT_1',          'PropertyMinimum',     1   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1',            'PropertyName',        'CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1'   ),
        (   'REQ_CSC_BAKERS_EXPORT_CAFE_ROUTE_BIT_1',            'PropertyMinimum',     1   ),

-- Moved to CSC_Q_BAKERS_GOLD.sql: REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_ANY arg
        (   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_BASE',             'Tag',                 'CLASS_CSC_BAKERS_BASE'   ),
        (   'REQ_CSC_BAKERS_PLOT_HAS_MATERIAL_SPEC',             'Tag',                 'CLASS_CSC_BAKERS_SPEC'   ),
        (   'REQ_CSC_DISTRICT_IS_BAKERS_QUARTER',                'DistrictType',        'DISTRICT_CSC_BAKERS_QUARTER'   ),

        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',         'CollectionType',      'COLLECTION_PLAYER_IMPROVEMENTS'   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',         'Count',               1   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_BASE',         'RequirementSetId',    'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_BASE'   ),

        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'CollectionType',      'COLLECTION_PLAYER_IMPROVEMENTS'   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'Count',               1   ),
        (   'REQ_CSC_BAKERS_ADJ_PLOT_HAS_IMPROVED_SPEC',         'RequirementSetId',    'REQSET_CSC_BAKERS_ADJ_PLOT_HAS_SPEC'   );

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
SELECT	'REQ_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit,					'PropertyName',					'CSC_BAKERS_STAGE_3_MARKET_RETURN_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_MARKET_RETURN_AMOUNT_BIT_' || Bit,					'PropertyMinimum',				1
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,					'PropertyName',					'CSC_BAKERS_STAGE_3_MARKET_FOOD_AMOUNT_BIT_' || Bit
FROM CSC_ScaledAmountBits;

INSERT OR IGNORE INTO RequirementArguments
        (   RequirementId,   Name,   Value   )
SELECT	'REQ_CSC_BAKERS_MARKET_FOOD_AMOUNT_BIT_' || Bit,					'PropertyMinimum',				1
FROM CSC_ScaledAmountBits;

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


--===========================================================================================================================================================================--
/*	CAFE */
--===========================================================================================================================================================================--

--  Each eligible adjacent customer contributes floor(its population / 5) stacks.
--  Culture goes to the customer building; Production/Gold return to the Cafe.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	BuildingModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Stage 4 threshold transaction yields now come from the customer-population Lua bridge.

-- Gold handled in CSC_Q_BAKERS_GOLD.sql via the same Stage 4 Lua property bridge.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Modifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Replaced by MOD_CSC_BAKERS_STAGE_4_*_BIT city-center property consumers.

-- Gold handled in CSC_Q_BAKERS_GOLD.sql via the same Stage 4 Lua property bridge.

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierArguments
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

-- Replaced by MOD_CSC_BAKERS_STAGE_4_*_BIT city-center property consumers.

-- Gold handled in CSC_Q_BAKERS_GOLD.sql via the same Stage 4 Lua property bridge.



--===========================================================================================================================================================================--
/*	UI */
--===========================================================================================================================================================================--

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- Notifications
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO Types
        (   Type,                                         Kind   )
VALUES  (   'NOTIFICATION_CSC_BAKERS_EFFECT_NEW',         'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_INCREASED',   'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_DECREASED',   'KIND_NOTIFICATION'   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_REMOVED',     'KIND_NOTIFICATION'   );

INSERT INTO Notifications
        (   NotificationType,                             SeverityType,   ExpiresEndOfTurn,   AutoNotify   )
VALUES  (   'NOTIFICATION_CSC_BAKERS_EFFECT_NEW',         'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_INCREASED',   'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_DECREASED',   'HIGH',         0,                  0   ),
        (   'NOTIFICATION_CSC_BAKERS_EFFECT_REMOVED',     'HIGH',         0,                  0   );

-- UI observation registry
-- Register the active benefit wrapper, not the hidden Service grant. The shared
-- notification/MCUIS scripts count its live subjects to show gains/losses and
-- stack changes; these rows describe gameplay effects rather than grant them.
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
-- CSC_AbilityAttachModifiers
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

INSERT INTO CSC_AbilityAttachModifiers
        (   ModifierId,                                             AbilityIcon,                                        AbilityIconTarget,                             NotificationQuarter   )
VALUES  (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WATER',      'ICON_BUILDING_CSC_BAKERS_STAGE_2_SERVICE',         'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',         'BAKERS'   ),
        (   'MOD_CSC_BAKERS_STAGE_2_EFFECT_ATTACH_CITY_WIND',       'ICON_BUILDING_CSC_BAKERS_STAGE_2_SERVICE',         'BUILDING_CSC_BAKERS_STAGE_2_SERVICE',         'BAKERS'   ),
        (   'MOD_CSC_BAKERS_STAGE_3_EFFECT_ATTACH_COMHUB',          'ICON_BUILDING_CSC_BAKERS_STAGE_3_SERVICE',         'BUILDING_CSC_BAKERS_STAGE_3_SERVICE',         'BAKERS'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_ENTERTAINMENT',   'ICON_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER',   'BAKERS'   ),
        (   'MOD_CSC_BAKERS_STAGE_4_EFFECT_ATTACH_WATER_PARK',      'ICON_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',   'BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER',   'BAKERS'   );


-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	ModifierStrings
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------

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

-- Art is another reader of the complete Service gate. Source properties are
-- written by SQL here; CSC_ArtProperties.lua only converts their positive values
-- to binary art-selection flags. Material supply alone must not show Service art.
-- Expanded building art: source properties use the complete gameplay Service gates.
-- CSC_ArtProperties.lua mirrors these into binary CITYPROP selection flags.
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
