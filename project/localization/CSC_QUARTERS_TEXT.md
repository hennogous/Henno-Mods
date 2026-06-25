# CSC_QUARTERS_TEXT
output: Civ Supply Chains/Text/CSC_QUARTERS_TEXT.sql
language: en_US

### Shared Class Names

## LOC_CLASS_CSC_BASE_NAME
Base Materials

## LOC_CLASS_CSC_SPEC_NAME
Specialty Materials

## LOC_CLASS_CSC_SALES_NAME
Sales

### Bakers' Quarter

## LOC_DISTRICT_CSC_BAKERS_QUARTER_NAME
Bakers' Quarter

## LOC_DISTRICT_CSC_BAKERS_QUARTER_DESCRIPTION
A district in your city specializing in baking.

<!--
Buildings in this Quarter create supply-chain transactions with adjacent material improvements, local Quarter buildings, customer districts, and Trade Routes.

Base Materials support Water Mills and Wind Mills; Specialty Materials support Cafés. Bakers buildings send [ICON_Food] Food through the chain while receiving [ICON_Production] Production and [ICON_Gold] Gold payments where implemented.

At Feudalism, Medieval Faires, and Urbanization, supplied Bakers buildings can establish Storekeeper, Innkeeper, Groundskeeper, and Ride Technician services in adjacent customer districts.
-->
+1 [ICON_Production] Production from every 2 adjacent river segments once the Water Mill is built, or +1 [ICON_Production] Production if built on Hills terrain once the Wind Mill is built.

## LOC_RESOURCE_WINE_NAME
Grapes

### Bakers' Adjacencies

## LOC_CSC_CITY_CENTER_GOLD_TO_BAKERS
+{1_num} [ICON_Gold] from the adjacent City Center.

## LOC_CSC_COMMERCIAL_HUB_GOLD_TO_BAKERS
+{1_num} [ICON_Gold] from the adjacent Commercial {1_num : plural 1?Hub; other?Hubs;}.

## LOC_CSC_SUGUBA_GOLD_TO_BAKERS
+{1_num} [ICON_Gold] from the adjacent Suguba {1_num : plural 1?district; other?districts;}.

## LOC_CSC_ENTERTAINMENT_GOLD_TO_BAKERS
+{1_num} [ICON_Gold] from the adjacent Entertainment {1_num : plural 1?Complex; other?Complexes;}.

## LOC_CSC_STREET_CARNIVAL_GOLD_TO_BAKERS
+{1_num} [ICON_Gold] from the adjacent Street {1_num : plural 1?Carnival; other?Carnivals;}.

## LOC_CSC_HIPPODROME_GOLD_TO_BAKERS
+{1_num} [ICON_Gold] from the adjacent Hippodrome {1_num : plural 1?district; other?districts;}.

## LOC_CSC_WATER_PARK_GOLD_TO_BAKERS
+{1_num} [ICON_Gold] from the adjacent Water {1_num : plural 1?Park; other?Parks;}.

## LOC_CSC_WATER_STREET_CARNIVAL_GOLD_TO_BAKERS
+{1_num} [ICON_Gold] from the adjacent Copacabana {1_num : plural 1?district; other?districts;}.

## LOC_CSC_REPLACER_GOLD_TO_BAKERS_FRONT
+{1_num} [ICON_Gold] from the adjacent

## LOC_CSC_REPLACER_GOLD_TO_BAKERS_BACK
{1_num : plural 1?district; other?districts;}.

## LOC_CSC_BREWERS_PRODUCTION_TO_BAKERS
+{1_num} [ICON_Production] Production from the adjacent Brewers' {1_num : plural 1?Quarter; other?Quarters;}.

## LOC_CSC_BAKERS_GOLD_TO_BREWERS
+{1_num} [ICON_Gold] Gold from the adjacent Bakers' {1_num : plural 1?Quarter; other?Quarters;}.

## LOC_BUILDING_CSC_BAKERS_RIVER_ACCESS_NAME
River access

## LOC_BUILDING_CSC_BAKERS_RIVER_ACCESS_DESCRIPTION
This quarter is adjacent to a river.

## LOC_BUILDING_CSC_BAKERS_NO_RIVER_ACCESS_NAME
No river access

## LOC_BUILDING_CSC_BAKERS_NO_RIVER_ACCESS_DESCRIPTION
This quarter is not adjacent to a river.

## LOC_BUILDING_CSC_BAKERS_WATER_MILL_NAME
Water Mill

## LOC_BUILDING_CSC_BAKERS_WATER_MILL_DESCRIPTION
- +1 [ICON_Food] Food from each adjacent Base Materials improvement, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.
- +1 [ICON_Production] Production and +1 [ICON_Gold] Gold from the local Bakery and Café, in exchange for +1 [ICON_Food] Food.
- +1 [ICON_Production] Production and +1 [ICON_Gold] Gold from an adjacent Granary, in exchange for +1 [ICON_Food] Food.

At Feudalism, a supplied Water Mill establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service in an adjacent City Center with a Granary.

## LOC_BUILDING_CSC_BAKERS_WIND_MILL_NAME
Wind Mill

## LOC_BUILDING_CSC_BAKERS_WIND_MILL_DESCRIPTION
- +1 [ICON_Food] Food from each adjacent Base Materials improvement, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.
- +1 [ICON_Production] Production and +1 [ICON_Gold] Gold from the local Bakery and Café, in exchange for +1 [ICON_Food] Food.
- +1 [ICON_Production] Production and +1 [ICON_Gold] Gold from an adjacent Granary, in exchange for +1 [ICON_Food] Food.

At Feudalism, a supplied Wind Mill establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service in an adjacent City Center with a Granary.

## LOC_BUILDING_CSC_BAKERS_BAKERY_NAME
Bakery

## LOC_BUILDING_CSC_BAKERS_BAKERY_DESCRIPTION
- +1 [ICON_Food] Food from the local Water Mill or Wind Mill, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.
- +0.1 [ICON_Production] Production and +0.1 [ICON_Gold] Gold per [ICON_Citizen] Citizen from each adjacent Market, in exchange for +0.1 [ICON_Food] Food per [ICON_Citizen] Citizen to the Market city.
- +1 [ICON_Production] Production and +1 [ICON_Gold] Gold from each incoming [ICON_TradeRoute] Trade Route, in exchange for a +1 [ICON_Food] Food bonus to the [ICON_TradeRoute] Trade Route, if the origin city itself does not have a Bakers' Quarter.

At Medieval Faires, a supplied Bakery establishes an {LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service in an adjacent Commercial Hub with a Market.

## LOC_BUILDING_CSC_BAKERS_CAFE_NAME
Café

## LOC_BUILDING_CSC_BAKERS_CAFE_DESCRIPTION
- +1 [ICON_Food] Food from the local Water Mill or Wind Mill, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold.
- +1 [ICON_Food] Food from each adjacent Specialty Materials improvement, in exchange for +1 [ICON_Production] Production.
- +1 [ICON_Production] Production and +1 [ICON_Gold] Gold for every 5 [ICON_Citizen] Citizens in the city from each adjacent Zoo and Ferris Wheel, in exchange for +1 [ICON_Culture] Culture.
- +1 [ICON_Food] Food bonus to [ICON_TradeRoute] Trade Routes to the city, in exchange for +2 [ICON_Gold] Gold to the Quarter, if the origin city does not have a Bakers' Quarter.

At Urbanization, a supplied Café can establish services in adjacent Entertainment Complexes with Zoos and Water Parks with Ferris Wheels.

## LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME
Storekeeper

## LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_DESCRIPTION
A Service established in the City Center at Feudalism when a supplied Water Mill or Wind Mill supports an adjacent Granary.

+10% growth and +1 [ICON_GreatEngineer] Great Engineer point.

## LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME
Innkeeper

## LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_DESCRIPTION
A Service established in the Commercial Hub at Medieval Faires when a supplied Bakery serves an adjacent Market.

+2 [ICON_Housing] Housing and +1 [ICON_GreatMerchant] Great Merchant point.

## LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME
Groundskeeper

## LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_DESCRIPTION
A Service established in the Entertainment Complex at Urbanization when a supplied Café serves an adjacent Zoo.

+2 [ICON_Tourism] Tourism and +1 [ICON_GreatEngineer] Great Engineer point.

## LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME
Ride Technician

## LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_DESCRIPTION
A Service established in the Water Park at Urbanization when a supplied Café serves an adjacent Ferris Wheel.

+2 [ICON_Tourism] Tourism and +1 [ICON_GreatEngineer] Great Engineer point.

## LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WATER
- {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME}: {1_TotalAmount}% growth and {2_TotalStack} [ICON_GreatEngineer] Great Engineer {3_TotalStackCount : plural 1?point; other?points;}.
- Supply Chain: supplied Water Mill [ICON_ARROW] adjacent Granary.

## LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WATER_NEW
a new {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service: {1_NewAmount}% growth and {2_NewStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WATER_INCREASED
{LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service: {1_IncreaseAmount}% growth and {2_IncreasedStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WATER_DECREASED
{LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service: {1_DecreaseAmount}% growth and {2_DecreasedStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WATER_REMOVED
{LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service: {1_LostAmount}% growth and {2_LostStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WIND
- {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME}: {1_TotalAmount}% growth and {2_TotalStack} [ICON_GreatEngineer] Great Engineer {3_TotalStackCount : plural 1?point; other?points;}.
- Supply Chain: supplied Wind Mill [ICON_ARROW] adjacent Granary.

## LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WIND_NEW
a new {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service: {1_NewAmount}% growth and {2_NewStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WIND_INCREASED
{LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service: {1_IncreaseAmount}% growth and {2_IncreasedStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WIND_DECREASED
{LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service: {1_DecreaseAmount}% growth and {2_DecreasedStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_2_EFFECT_DESCRIPTION_WIND_REMOVED
{LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service: {1_LostAmount}% growth and {2_LostStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_2_EFFECT
+1 [ICON_Food] Food from an adjacent Water Mill or Wind Mill, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold to the Water Mill or Wind Mill.

At Feudalism, a Granary adjacent to a supplied Water Mill or Wind Mill establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service: +10% growth and +1 [ICON_GreatEngineer] Great Engineer point from each adjacent supplied mill.

## LOC_CSC_BAKERS_STAGE_2_CIVIC
text-prefix: [NEWLINE][NEWLINE]

- A Granary adjacent to a supplied Water Mill or Wind Mill establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service: +10% growth and +1 [ICON_GreatEngineer] Great Engineer point from an adjacent supplied mill.

## LOC_CSC_BAKERS_STAGE_3_EFFECT_DESCRIPTION
- {LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME}: {1_TotalAmount} [ICON_Housing] Housing and {2_TotalStack} [ICON_GreatMerchant] Great Merchant {3_TotalStackCount : plural 1?point; other?points;}.
- Supply Chain: {3_TotalStackCount} supplied {3_TotalStackCount : plural 1?Bakery; other?Bakeries;} [ICON_ARROW] adjacent Market.

## LOC_CSC_BAKERS_STAGE_3_EFFECT_DESCRIPTION_NEW
a new {LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service: {1_NewAmount} [ICON_Housing] Housing, {2_NewStack} [ICON_GreatMerchant] Great Merchant {3_StackCount : plural 1?point; other?points;} and +1 [ICON_Citizen] Citizen slot in the Commercial Hub

## LOC_CSC_BAKERS_STAGE_3_EFFECT_DESCRIPTION_INCREASED
{LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service: {1_IncreaseAmount} [ICON_Housing] Housing and {2_IncreasedStack} [ICON_GreatMerchant] Great Merchant {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_3_EFFECT_DESCRIPTION_DECREASED
{LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service: {1_DecreaseAmount} [ICON_Housing] Housing and {2_DecreasedStack} [ICON_GreatMerchant] Great Merchant {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_3_EFFECT_DESCRIPTION_REMOVED
{LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service: {1_LostAmount} [ICON_Housing] Housing and {2_LostStack} [ICON_GreatMerchant] Great Merchant {3_StackCount : plural 1?point; other?points;}

<!--
## LOC_CSC_BAKERS_STAGE_3_SERVICE
text-prefix: [NEWLINE][NEWLINE]

At Medieval Faires, a Market adjacent to a supplied Bakery establishes an {LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service: +2 [ICON_Housing] Housing and +1 [ICON_GreatMerchant] Great Merchant point from each adjacent supplied Bakery, and +1 [ICON_Citizen] Citizen slot in the Commercial Hub.
-->

## LOC_CSC_BAKERS_STAGE_3_EFFECT
text-prefix: [NEWLINE][NEWLINE]

+0.1 [ICON_Food] Food per [ICON_Citizen] Citizen to the city from each adjacent Bakery, in exchange for +0.1 [ICON_Production] Production and +0.1 [ICON_Gold] Gold per [ICON_Citizen] Citizen to the Bakery city.

At Medieval Faires, a Market adjacent to a supplied Bakery establishes an {LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service: +2 [ICON_Housing] Housing and +1 [ICON_GreatMerchant] Great Merchant point from each adjacent supplied Bakery, and +1 [ICON_Citizen] Citizen slot in the Commercial Hub.

## LOC_CSC_BAKERS_STAGE_3_CIVIC
- A Market adjacent to a supplied Bakery establishes an {LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service:
- +2 [ICON_Housing] Housing and +1 [ICON_GreatMerchant] Great Merchant point from each adjacent supplied Bakery, and +1 [ICON_Citizen] Citizen slot in the Commercial Hub.

## LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_ENTER
- {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME}: {1_TotalAmount} [ICON_Tourism] Tourism and {2_TotalStack} [ICON_GreatEngineer] Great Engineer {3_TotalStackCount : plural 1?point; other?points;}.
- Supply Chain: {3_TotalStackCount} supplied {3_TotalStackCount : plural 1?Café; other?Cafés;} [ICON_ARROW] adjacent Zoo.

## LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_ENTER_NEW
a new {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service: {1_NewAmount} [ICON_Tourism] Tourism, {2_NewStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;} and +1 [ICON_Citizen] Citizen slot in the Entertainment Complex

## LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_ENTER_INCREASED
{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service: {1_IncreaseAmount} [ICON_Tourism] Tourism and {2_IncreasedStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_ENTER_DECREASED
{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service: {1_DecreaseAmount} [ICON_Tourism] Tourism and {2_DecreasedStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_ENTER_REMOVED
{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service: {1_LostAmount} [ICON_Tourism] Tourism and {2_LostStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_WATER
- {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME}: {1_TotalAmount} [ICON_Tourism] Tourism and {2_TotalStack} [ICON_GreatEngineer] Great Engineer {3_TotalStackCount : plural 1?point; other?points;}.
- Supply Chain: {3_TotalStackCount} supplied {3_TotalStackCount : plural 1?Café; other?Cafés;} [ICON_ARROW] adjacent Ferris Wheel.

## LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_WATER_NEW
a new {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service: {1_NewAmount} [ICON_Tourism] Tourism, {2_NewStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;} and +1 [ICON_Citizen] Citizen slot in the Water Park

## LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_WATER_INCREASED
{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service: {1_IncreaseAmount} [ICON_Tourism] Tourism and {2_IncreasedStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_WATER_DECREASED
{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service: {1_DecreaseAmount} [ICON_Tourism] Tourism and {2_DecreasedStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_4_EFFECT_DESCRIPTION_WATER_REMOVED
{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service: {1_LostAmount} [ICON_Tourism] Tourism and {2_LostStack} [ICON_GreatEngineer] Great Engineer {3_StackCount : plural 1?point; other?points;}

## LOC_CSC_BAKERS_STAGE_4_EFFECT_ENTER
text-prefix: [NEWLINE][NEWLINE]

+1 [ICON_Culture] Culture for every 5 [ICON_Citizen] Citizens in the city from each adjacent Café, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold to the Café.

At Urbanization, a Zoo adjacent to a supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service: +2 [ICON_Tourism] Tourism and +1 [ICON_GreatEngineer] Great Engineer point from each adjacent supplied Café, and +1 [ICON_Citizen] Citizen slot in the Entertainment Complex.

## LOC_CSC_BAKERS_STAGE_4_EFFECT_WATER
+1 [ICON_Culture] Culture for every 5 [ICON_Citizen] Citizens in the city from each adjacent Café, in exchange for +1 [ICON_Production] Production and +1 [ICON_Gold] Gold to the Café.

At Urbanization, a Ferris Wheel adjacent to a supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service: +2 [ICON_Tourism] Tourism and +1 [ICON_GreatEngineer] Great Engineer point from each adjacent supplied Café, and +1 [ICON_Citizen] Citizen slot in the Water Park.

<!--
## LOC_CSC_BAKERS_STAGE_4_SERVICE_ENTER
text-prefix: [NEWLINE]

{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service: +2 [ICON_Tourism] Tourism and +1 [ICON_GreatEngineer] Great Engineer point from each adjacent supplied Café, and +1 [ICON_Citizen] Citizen slot if the district has a Zoo.

## LOC_CSC_BAKERS_STAGE_4_SERVICE_WATER
text-prefix: [NEWLINE]

{LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service: +2 [ICON_Tourism] Tourism and +1 [ICON_GreatEngineer] Great Engineer point from each adjacent supplied Café, and +1 [ICON_Citizen] Citizen slot if the district has a Ferris Wheel.
-->

## LOC_CSC_BAKERS_STAGE_4_CIVIC
- A Zoo adjacent to a supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service, and a Ferris Wheel adjacent to a supplied Café establishes a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service:
- +2 [ICON_Tourism] Tourism and +1 [ICON_GreatEngineer] Great Engineer point from each adjacent supplied Café, and +1 [ICON_Citizen] Citizen slot in the district.

<!--
## LOC_CSC_BAKERS_STAGE_4_REQUIREMENT
text-prefix: [NEWLINE][NEWLINE]

At Urbanization, a district adjacent to a supplied Café establishes a local service:
-->

## LOC_PEDIA_CONCEPTS_PAGEGROUP_CSC_SUPPLY_CHAINS_NAME
Supply Chains

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTRODUCTION_CHAPTER_CONTENT_TITLE
Introduction

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTRODUCTION_CHAPTER_CONTENT_PARA_1
Introduction text...

## LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_CONTENT_TITLE
Stage 1: Materials extraction

## LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_CONTENT_PARA_1
- - Stage 1 of supply chains consist of standard game improvements (e.g. wheat farms, cotton plantations and lumber mills) that extract materials from resources on the map, and sell them as inputs to stage 2 and 4 buildings.
- - Materials mapped to supply chains are classified as either Base Materials or Specialty Materials.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_CONTENT_TITLE
Quarters

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_CONTENT_PARA_1
- - Stages 2, 3 and 4 of supply chains are implemented as 3 buildings inside of 8 new districts called Quarters, each dedicated to the goods supply chain of a specific industry, e.g. Baking or Textiles.
- - All Quarters unlock at Craftsmanship.
- - Each Quarter can only be constructed once per city, and count toward district slots.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_CONTENT_TITLE
Stage 2: Intermediary goods

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_CONTENT_PARA_1
Intermediary goods buildings purchase various Base Materials from stage 1 suppliers and processes those into intermediary goods (e.g. flour, textiles) to sell to customers. These customers could be both downstream actors in its supply chain for further processing, as well as outside of the supply chain for direct use.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_CONTENT_TITLE
Stage 3: Consumer goods

## LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_CONTENT_PARA_1
Consumer goods buildings procure intermediary goods from a stage 2 supplier in the Quarter, and processes those into consumer goods (e.g. bakery, tailor, joinery) ready for sale to the general city population.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_CONTENT_TITLE
Stage 4: Specialty goods

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_CONTENT_PARA_1
Specialty goods buildings procure intermediary goods from a stage 2 supplier in the Quarter and various Specialty Materials from stage 1 suppliers, and transforms them into specialty goods (e.g. Café, Fashion House, Sculptor) for sale to select customers.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_CONTENT_TITLE
Stage 5: Goods sales

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_CONTENT_PARA_1
For the most part, sales of different types of goods to buyers (stage 5) were described in the sections above along with the building that produced the goods.

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCBASE_TITLE
Base Materials

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCSPEC_TITLE
Specialty Materials

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCGOODS_TITLE
Goods Providers

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCSALES_TITLE
Sales Districts

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_HISTORY_TITLE
Historical Context

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_HISTORY_PARA_1
Baking is one of the oldest urban trades, emerging wherever grain cultivation, milling, and settled life made reliable bread possible. In many cities, bakers became more than individual craftsmen: they formed guilds, worked under civic regulation, and supplied a food so essential that its weight, price, and quality were often matters of public concern. A Bakers' Quarter represents this clustered institution of mills, ovens, stores, and sellers, where the practical work of turning harvests into daily nourishment became part of the city's basic stability.

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_HISTORY_PARA_2
Over time, the same trade reached beyond subsistence. Bread and pastries moved from granaries and market stalls into inns, fairs, coffee houses, gardens, and places of public amusement, following the growth of urban hospitality and leisure. The baker's craft could feed a city, welcome travelers, sweeten public gatherings, and support the cafés where conversation, fashion, and culture gathered around a table. In that progression, the Bakers' Quarter becomes not only a safeguard against hunger, but a quiet measure of civic life becoming more social, comfortable, and expressive.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_WATER_MILL_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_WATER_MILL_CHAPTER_CSCHAIN_PARA_1
By the flowing river, the Water Mill stands as a testament to the harnessing of natural power. Its massive wheel turns with an insistent groan, transforming the raw harvests of nearby Wheat, Rice, and other Farms into the finely ground flour that is the lifeblood of your city. This essential step in the Bakers' Quarter's supply chain delivers its milled bounty to the Bakery and Café, as well as to an adjacent Granary, helping to fill the city's stores.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_WATER_MILL_CHAPTER_HISTORY_TITLE
Historical Context

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_WATER_MILL_CHAPTER_HISTORY_PARA_1
Water Mills were a significant technological innovation, building on earlier inventions like the wheel, which was fundamental to harnessing mechanical energy. They have a long and ancient history, with some of the earliest known examples dating back to ancient Persia and the Hellenistic world. Unlike windmills, they were tied to specific geographic locations, relying on the power of rivers and streams, and their use made them focal points for communities and settlements throughout history.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_WATER_MILL_CHAPTER_HISTORY_PARA_2
The interaction between a water mill and a granary was central to the agrarian economy and became particularly significant during the feudal era. While the water mill itself was a powerful tool for processing grain, its value was tied directly to the ability to store the resulting product. The granary served as the secure, central repository for the milled grain, making it a critical component for managing food supplies. In many societies, this pairing of a powered mill and a central granary became a foundation of economic power, as it allowed landowners or authorities to control the processing, storage, and distribution of a community's most essential commodity.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_WIND_MILL_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_WIND_MILL_CHAPTER_CSCHAIN_PARA_1
Perched on a hill or an open plain, the Wind Mill stands ready to capture the invisible force of the air itself. With its great sails turning against the sky, it grinds raw materials from nearby Wheat, Rice, and other Farms into flour. This essential step in the Bakers' Quarter's supply chain provides flour to the Bakery and Café, and also stocks any adjacent Granary.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_WIND_MILL_CHAPTER_HISTORY_TITLE
Historical Context

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_WIND_MILL_CHAPTER_HISTORY_PARA_1
Windmills were a significant technological innovation with a long and ancient history, building upon earlier inventions like the wheel, which was fundamental to harnessing mechanical energy. While they played a pivotal role in medieval Europe, their origins are believed to be much older, with evidence suggesting that the earliest designs were developed in Persia (modern-day Iran and Afghanistan) as early as the 9th century. These early windmills were primarily used for tasks like grinding grain and pumping water, and their use meant that communities were no longer solely reliant on rivers and streams for a power source, allowing them to establish mills in a wider range of locations.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_WIND_MILL_CHAPTER_HISTORY_PARA_2
The interaction between a windmill and a granary reflects a self-contained system of production and storage that was vital for agricultural societies across different cultures and eras. During the feudal era, this relationship was particularly significant. The windmill, regardless of its specific design or origin, provided a new source of power to process crops, while the granary served as the central hub for storing the milled grain. This pairing was fundamental to economic and social structures, enabling communities to manage food supplies more efficiently and consolidating the control of resources in the hands of a ruling class. This combination of a powered mill and a central storage facility represents a timeless agricultural advancement, independent of any single region's history.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_GRANARY_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_GRANARY_CHAPTER_CSCHAIN_PARA_1
The Granary stands as the final stop for flour before it reaches the city's bakers. A bustling storehouse of grain and flour, it purchases the milled output from an adjacent Water Mill or Wind Mill, ensuring a constant supply of the raw materials needed to feed your populace.

At Feudalism, an adjacent supplied Water Mill or Wind Mill can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} service here. See the {LOC_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_NAME} Civilopedia page for full requirements and effects.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_BAKERY_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_BAKERY_CHAPTER_CSCHAIN_PARA_1
The Bakery is where the smell of freshly baked bread fills the air from early in the morning. Taking the finely milled flour from the local Water Mill or Wind Mill, this building transforms it into a variety of baked goods available at the Market, providing nourishment to the general population.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_BAKERY_CHAPTER_HISTORY_TITLE
Historical Context

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_BAKERY_CHAPTER_HISTORY_PARA_1
The Bakery is an institution with a rich history, deeply tied to the rise of urban centers and the specialization of labor. The professional baker emerged with the advent of guilds, which regulated the trade and ensured the quality of products. A baker's work was fundamentally dependent on the existence of a local Wind Mill or Water Mill, as these structures provided the milled flour essential for their craft. This relationship highlights a key supply chain, where the output of one industry—the milling of grain—becomes the primary input for another, the baking of bread. The presence of these mills allowed a baker to produce a consistent and reliable supply of bread, which was a dietary staple for a city's growing population.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_BAKERY_CHAPTER_HISTORY_PARA_2
With the advent of the Market, the role of the Bakery expanded beyond simple production. The Market provided a dedicated space for commerce, allowing bakers to sell their goods directly to the public rather than just to their immediate neighbors. This commercial link became even more pronounced with the development of Medieval Faires, which were large, periodic gatherings that attracted merchants and customers from a wide area. For the baker, a fair was a prime opportunity to sell a variety of breads and other baked goods, and to engage in larger-scale trade. This connection between the Bakery and the Market, particularly during special events like fairs, demonstrates how specialized crafts integrated into and helped to fuel the broader medieval economy.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_MARKET_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_MARKET_CHAPTER_CSCHAIN_PARA_1
The Market is where the general population can purchase freshly baked goods from the Bakery every day, ensuring that the economic chain is completed and your citizens are well-fed.

At Medieval Faires, an adjacent supplied Bakery can establish an {LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} service here. See the {LOC_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_NAME} Civilopedia page for full requirements and effects.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_CAFE_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_CAFE_CHAPTER_CSCHAIN_PARA_1
The Café is the final, exclusive step in the Bakers' Quarter supply chain. It procures its flour from the local Water Mill or Wind Mill, but its true distinction comes from its use of rare Specialty Materials like coffee, sugar, cocoa, and spices. These are sourced from adjacent improvements and transformed into fine baked goods and rich drinks for the select customers who also frequent an adjacent Entertainment Complex or Water Park.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_CAFE_CHAPTER_HISTORY_TITLE
Historical Context

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_CAFE_CHAPTER_HISTORY_PARA_1
The Café is an establishment that reflects the rise of a new kind of social and intellectual life, particularly with the advent of the Enlightenment. Its roots can be traced to the coffee houses that emerged in the Ottoman Empire and spread throughout Europe via trade routes. Its reliance on a local mill is a nod to a key supply chain, as it needs finely milled ingredients for its pastries and beverages. As society became more urbanized, cafes became vibrant social spaces, a departure from the traditional tavern or alehouse. They also had a crucial dependency on Specialty Materials like coffee, tea, and cocoa, which were increasingly imported as a result of global trade networks.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_CAFE_CHAPTER_HISTORY_PARA_2
During the Enlightenment, cafés evolved from simple establishments into crucial centers for the exchange of ideas. They became known as "penny universities" because for the price of a cup of coffee, anyone could sit, read the daily papers, and engage in conversation with others. They were a more accessible alternative to official salons or universities, and because they were not subject to the same strict censorship as printed materials, they became hotbeds for intellectual discourse. Thinkers such as Voltaire, Rousseau, and Diderot were known to frequent these establishments, and it was in this atmosphere of open debate that many of their revolutionary ideas were refined and disseminated.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_CAFE_CHAPTER_HISTORY_PARA_3
The sales interaction of a Café with the local Zoo or Ferris Wheel is a reflection of the rise of leisure culture and the "day out." As cities grew and the middle class expanded, public entertainment venues became popular destinations. A café adjacent to these attractions would have been a natural fit, offering a place for people to relax and socialize as part of their visit. This connection demonstrates how the Café was not just a place for intellectual discussion, but a vital part of a burgeoning urban entertainment industry, catering to a public seeking new forms of recreation and social engagement.

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_ENTERTAINMENT_COMPLEX_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_ENTERTAINMENT_COMPLEX_CHAPTER_CSCHAIN_PARA_1
Some visitors to the Entertainment Complex also enjoy refreshments from the adjacent Café.

At Urbanization, an adjacent supplied Café can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service if this district has a Zoo. See the {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} Civilopedia page for full requirements and effects.

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_STREET_CARNIVAL_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_STREET_CARNIVAL_CHAPTER_CSCHAIN_PARA_1
Some visitors to the Street Carnival also enjoy refreshments from the adjacent Café.

At Urbanization, an adjacent supplied Café can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service if this district has a Zoo. See the {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} Civilopedia page for full requirements and effects.

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_HIPPODROME_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_HIPPODROME_CHAPTER_CSCHAIN_PARA_1
Some visitors to the Hippodrome also enjoy refreshments from the adjacent Café.

At Urbanization, an adjacent supplied Café can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service if this district has a Zoo. See the {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} Civilopedia page for full requirements and effects.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_ZOO_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_ZOO_CHAPTER_CSCHAIN_PARA_1
Some visitors to the Zoo also enjoy refreshments from the adjacent Café.

At Urbanization, an adjacent supplied Café can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} service in this district. See the {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_NAME} Civilopedia page for full requirements and effects.

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_WATER_ENTERTAINMENT_COMPLEX_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_WATER_ENTERTAINMENT_COMPLEX_CHAPTER_CSCHAIN_PARA_1
Some visitors to the Water Park also enjoy refreshments from the adjacent Café.

At Urbanization, an adjacent supplied Café can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service if this district has a Ferris Wheel. See the {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} Civilopedia page for full requirements and effects.

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_WATER_STREET_CARNIVAL_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_WATER_STREET_CARNIVAL_CHAPTER_CSCHAIN_PARA_1
Some visitors to the Copacabana also enjoy refreshments from the adjacent Café.

At Urbanization, an adjacent supplied Café can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service if this district has a Ferris Wheel. See the {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} Civilopedia page for full requirements and effects.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_FERRIS_WHEEL_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_FERRIS_WHEEL_CHAPTER_CSCHAIN_PARA_1
Some visitors to the Ferris Wheel also enjoy refreshments from the adjacent Café.

At Urbanization, an adjacent supplied Café can establish a {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} service in this district. See the {LOC_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_NAME} Civilopedia page for full requirements and effects.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_CHAPTER_CSCHAIN_PARA_1
The Water Mill or Wind Mill draws on improved Bakers' Base Materials nearby, turns them into dependable flour, and transports that steady flow to the city's Granary.

This establishes a Storekeeper service in the City Center, ensuring that hard-earned food stores are managed for the good of the growing population.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_CHAPTER_HISTORY_TITLE
Historical Context

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_2_SERVICE_CHAPTER_HISTORY_PARA_1
As milling and storage became regular institutions rather than seasonal improvisations, cities needed people to measure, record, preserve, and distribute grain and flour. Storekeepers rarely changed history by themselves, but their quiet competence made larger populations possible: fewer spoiled stores, fewer missing sacks, and fewer hungry days between harvests. In that sense, the growth of the city was not only a matter of producing more food, but of making food dependable enough that more people could plan their lives around it.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_CHAPTER_CSCHAIN_PARA_1
The Bakery draws on dependable flour from the local Water Mill or Wind Mill, turns it into bread and baked goods, and offers that steady flow of goods to the growing number of visitors to the adjacent Market.

This gives a Citizen the opportunity to take up employment as an Innkeeper in the Commercial Hub, turning traffic to the Market into lodging, meals, and shelter for merchants and travelers passing through the city.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_CHAPTER_HISTORY_TITLE
Historical Context

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_3_SERVICE_CHAPTER_HISTORY_PARA_1
Markets and fairs did more than exchange goods; they concentrated people. Merchants, teamsters, pilgrims, laborers, and customers all needed food, lodging, animals tended, and disputes settled before the road called again. Bread was a humble anchor for that world because it made daily crowds possible. Where food supply became steady, towns could host strangers as well as residents, and hospitality became a profession rather than an occasional courtesy.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_CHAPTER_CSCHAIN_PARA_1
The Café draws on dependable flour from the local Water Mill or Wind Mill and improved Bakers' Specialty Materials nearby, turns them into pastries and drinks, and offers that steady flow of refreshments to the growing numbers of visitors to the adjacent Zoo.

This gives a Citizen the opportunity to take up employment as a Groundskeeper in the Entertainment Complex, keeping paths, enclosures, and gathering places ready for visitors who now have reason to linger.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_CHAPTER_HISTORY_TITLE
Historical Context

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_ENTER_CHAPTER_HISTORY_PARA_1
Public attractions became more complex as cities became larger, wealthier, and more accustomed to leisure outside the home. Cafés, refreshment stalls, and nearby bakeries helped extend a visit from a brief spectacle into a day out, which in turn meant more paths to sweep, benches to mend, cages to tend, crowds to guide, and small disasters to prevent. The groundskeeper is the unglamorous consequence of a city large enough to feed itself and then ask what it might do after lunch.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_CHAPTER_CSCHAIN_TITLE
Supply Chains

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_CHAPTER_CSCHAIN_PARA_1
The Café draws on dependable flour from the local Water Mill or Wind Mill and improved Bakers' Specialty Materials nearby, turns them into pastries and drinks, and offers that steady flow of refreshments to the growing numbers of visitors to the adjacent Ferris Wheel.

This gives a Citizen the opportunity to take up employment as a Ride Technician in the Water Park, keeping the machinery, queues, and waterfront crowds moving safely through a longer day out.

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_CHAPTER_HISTORY_TITLE
Historical Context

## LOC_PEDIA_BUILDINGS_PAGE_BUILDING_CSC_BAKERS_STAGE_4_SERVICE_WATER_CHAPTER_HISTORY_PARA_1
Mechanical rides and waterfront amusements turned leisure into infrastructure. They needed operators, inspectors, repair crews, ticket sellers, and a nearby flow of food and drink to keep crowds lingering. Such services followed population growth in the most literal way: once enough people could be fed reliably, cities could sustain places where those same people gathered simply to enjoy themselves. The ride technician is what happens when bread, sugar, machinery, and free time all arrive in the same neighborhood.

## Raw SQL 1
mode: raw

```sql
-- PEDIA: RESOURCES

CREATE TEMP TABLE BAKERS_RESOURCES (
    ResourceName TEXT,
    ResourceCategory TEXT
);

CREATE TEMP TABLE BAKERS_SALES_DISTRICTS (
    DistrictType TEXT,
    NameTag TEXT,
    SortIndex INTEGER
);

INSERT INTO BAKERS_RESOURCES (ResourceName, ResourceCategory) VALUES

--	Bakers' Quarter Base Materials
		(	'RESOURCE_BANANAS',		'CLASS_CSC_BAKERS_BASE'		),
		(	'RESOURCE_MAIZE',		'CLASS_CSC_BAKERS_BASE'		),
		(	'RESOURCE_RICE',		'CLASS_CSC_BAKERS_BASE'		),
		(	'RESOURCE_WHEAT',		'CLASS_CSC_BAKERS_BASE'		),
        (   'RESOURCE_CSC_FLAX',    'CLASS_CSC_BAKERS_BASE'     ),

--	Bakers' Quarter Specialty Materials
		(	'RESOURCE_COCOA',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_COFFEE',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_WINE',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_OLIVES',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_SALT',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_SPICES',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_SUGAR',		'CLASS_CSC_BAKERS_SPEC'		),
		(	'RESOURCE_TEA',			'CLASS_CSC_BAKERS_SPEC'		);

INSERT INTO BAKERS_SALES_DISTRICTS (DistrictType, NameTag, SortIndex) VALUES
		(	'DISTRICT_CITY_CENTER',					'LOC_DISTRICT_CITY_CENTER_NAME',					10	),
		(	'DISTRICT_COMMERCIAL_HUB',				'LOC_DISTRICT_COMMERCIAL_HUB_NAME',				20	),
		(	'DISTRICT_ENTERTAINMENT_COMPLEX',		'LOC_DISTRICT_ENTERTAINMENT_COMPLEX_NAME',		30	),
		(	'DISTRICT_WATER_ENTERTAINMENT_COMPLEX',	'LOC_DISTRICT_WATER_ENTERTAINMENT_COMPLEX_NAME',	40	);
```

## Raw SQL 2
mode: raw

```sql
INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT
    'en_US',
    CASE
        WHEN ResourceCategory = 'CLASS_CSC_BAKERS_BASE' THEN 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCBASE_PARA_1'
        WHEN ResourceCategory = 'CLASS_CSC_BAKERS_SPEC' THEN 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCSPEC_PARA_1'
    END,
    '[ICON_BULLET]' || GROUP_CONCAT('[ICON_' || ResourceName || '] ' ||
        CASE ResourceName
            WHEN 'RESOURCE_CSC_FLAX' THEN 'Flax'
            WHEN 'RESOURCE_WINE' THEN 'Grapes'
            ELSE
                UPPER(SUBSTR(ResourceName, INSTR(ResourceName, '_') + 1, 1)) ||
                LOWER(SUBSTR(ResourceName, INSTR(ResourceName, '_') + 2))
        END, ' [NEWLINE][ICON_BULLET]')
FROM
    BAKERS_RESOURCES
GROUP BY
    ResourceCategory;
```

## Raw SQL 3
mode: raw

```sql
INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
VALUES ('en_US', 'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCGOODS_PARA_1', '');
```

## Raw SQL 4
mode: raw

```sql
INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT
    'en_US',
    'LOC_PEDIA_DISTRICTS_PAGE_DISTRICT_CSC_BAKERS_QUARTER_CHAPTER_CSCSALES_PARA_1',
    '[ICON_BULLET]' || GROUP_CONCAT('[ICON_' || DistrictType || '] {' || NameTag || '}', ' [NEWLINE][ICON_BULLET]')
FROM (
    SELECT DistrictType, NameTag
    FROM BAKERS_SALES_DISTRICTS
    ORDER BY SortIndex
);
```

## Raw SQL 5
mode: raw

```sql
INSERT OR REPLACE INTO LocalizedText (Language, Tag, Text)
SELECT 'en_US', 'LOC_PEDIA_RESOURCES_PAGE_' || ResourceName || '_CHAPTER_CSCQUAR_TITLE', 'Supply Chains'
FROM BAKERS_RESOURCES
UNION ALL
SELECT
    'en_US',
    'LOC_PEDIA_RESOURCES_PAGE_' || ResourceName || '_CHAPTER_CSCQUAR_PARA_1',
    CASE
        WHEN ResourceCategory = 'CLASS_CSC_BAKERS_BASE' THEN 'Base material: [ICON_BAKERS] Bakers'' Quarter'
        WHEN ResourceCategory = 'CLASS_CSC_BAKERS_SPEC' THEN 'Specialty material: [ICON_BAKERS] Bakers'' Quarter'
    END
FROM BAKERS_RESOURCES;
```

## Raw SQL 6
mode: raw

```sql
DROP TABLE BAKERS_RESOURCES;
DROP TABLE BAKERS_SALES_DISTRICTS;

-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Tailors' Quarter
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## LOC_DISTRICT_CSC_TAILORS_QUARTER_NAME
Tailors' Quarter

## LOC_DISTRICT_CSC_TAILORS_QUARTER_DESCRIPTION
A district in your city specializing in textiles.

## Raw SQL 7
mode: raw

```sql
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Apothecaries' Quarter
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## LOC_DISTRICT_CSC_APOTHECARIES_QUARTER_NAME
Apothecaries' Quarter

## LOC_DISTRICT_CSC_APOTHECARIES_QUARTER_DESCRIPTION
A district in your city specializing in medicine.

## Raw SQL 8
mode: raw

```sql
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Stonemasons' Quarter
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## LOC_DISTRICT_CSC_STONEMASONS_QUARTER_NAME
Stonemasons' Quarter

## LOC_DISTRICT_CSC_STONEMASONS_QUARTER_DESCRIPTION
A district in your city specializing in stoneworking.

## Raw SQL 9
mode: raw

```sql
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Carpenters' Quarter
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## LOC_DISTRICT_CSC_CARPENTERS_QUARTER_NAME
Carpenters' Quarter

## LOC_DISTRICT_CSC_CARPENTERS_QUARTER_DESCRIPTION
A district in your city specializing in woodworking.

## LOC_BUILDING_CSC_CARPENTERS_JOINERY_NAME
Joinery

## LOC_BUILDING_CSC_CARPENTERS_JOINERY_DESCRIPTION
## LOC_BOOST_TRIGGER_CONSTRUCTION_CSC
Build a Joinery.

## LOC_BOOST_TRIGGER_LONGDESC_CONSTRUCTION_CSC
Work in the Joinery has taught your workers much about construction practices.

## Raw SQL 10
mode: raw

```sql
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Blacksmiths' Quarter
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## LOC_DISTRICT_CSC_BLACKSMITHS_QUARTER_NAME
Blacksmiths' Quarter

## LOC_DISTRICT_CSC_BLACKSMITHS_QUARTER_DESCRIPTION
A district in your city specializing in metalworking.

## Raw SQL 11
mode: raw

```sql
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Goldsmiths' Quarter
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## LOC_DISTRICT_CSC_GOLDSMITHS_QUARTER_NAME
Goldsmiths' Quarter

## LOC_DISTRICT_CSC_GOLDSMITHS_QUARTER_DESCRIPTION
A district in your city specializing in jewelry.

## Raw SQL 12
mode: raw

```sql
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
--	Brewers' Quarter
-------------------------------------------------------------------------------------------------------------------------------------------------------------------------------
```

## LOC_DISTRICT_CSC_BREWERS_QUARTER_NAME
Brewers' Quarter

## LOC_DISTRICT_CSC_BREWERS_QUARTER_DESCRIPTION
A district in your city specializing in fermentation.
