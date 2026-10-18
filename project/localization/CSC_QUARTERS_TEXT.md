# CSC_QUARTERS_TEXT
output: Civ Supply Chains/Text/CSC_QUARTERS_TEXT.sql
language: en_US

<!--
First Pedia draft, 14 October 2026.
Sources: docs/content/index.md, docs/content/design/supply-chain-framework.md,
and docs/content/design/transactions.md. The fuller framework transaction definitions
are retained; Customer (Buyer) reconciles the two source terms.

Editorial changes: removed images, image-dependent prose, web navigation,
Taxes & Politics and the closing social-classes/image reference. Moved trade-route
sales and the shared population rule to Stage 5; retained stage-specific adjacent
sales and Service unlocks with their producing building. Added native Pedia
chapter headings, bullets and existing text icons. Other wording is kept faithful.

Review before release: this is a design-source draft, not a fresh gameplay audit.
The source contains two historical cross-city Gold notes, reproduced here for
review rather than presented as current gameplay limitations:
* *At the moment, both the main yield (supply) and the {{gold}} Gold yield (payment) will be given to the customer city, but in the future I want to change this to use the customer's city population to give {{gold}} Gold back to the seller's city so that it follows the standard transaction pattern of payment belonging to the seller.*
* *At the moment, both the main yield and the {{gold}} Gold yield will be given to the customer city, but in the future I want to change this to use the customer's city population to give {{gold}} Gold back to the seller's city.*
Current customer-population return logic already implements seller-city returns.
Trade-route material gates, Production/Gold returns, Amenity promises, generic
river bonuses and upkeep values also need reconciliation with each Quarter.
-->

## LOC_PEDIA_CONCEPTS_PAGEGROUP_CSC_SUPPLY_CHAINS_NAME
Civ Supply Chains

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTRODUCTION_CHAPTER_CONTENT_TITLE
Introduction

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTRODUCTION_CHAPTER_CONTENT_PARA_1
Sid Meier's Civilization VI has always been good at plotting out the overall arc of an empire's history, from Antiquity to the Information Age. But, to me, it's sometimes fallen short in telling the smaller stories that add all the immersive flavour along the way. For instance: improving a wheat resource on a tile gives all of the benefits of that decision at once, with the effect only visible as growth in the city. There are very few tools for the player to tell the story of what happens to the crops produced on that wheat farm, the effect on the local economy, until it ultimately leads to growth in the city. This is where games like the Anno series have a more complex, and in my opinion stronger, economic gameplay.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTRODUCTION_CHAPTER_CONTENT_PARA_2
In this mod, I'm trying to create the version of Civ that I've always wanted to play: all of the just-one-more-turn feeling of Civ, expanded with a toolbox for telling many more small stories. A local forest turning into ships for exploring the globe, and even string instruments in the Bolshoi Theater. Or a cotton plantation and some gold thread driving a thriving textiles industry leading to some very well-dressed and influential diplomats!

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTRODUCTION_CHAPTER_CONTENT_PARA_3
In a sense, the mod is inspired by the Industry and Corporations concept in the Monopolies & Corporations (M&C) game mode, which is optional but recommended when playing with this mod. The mod however reworks some concepts and goes to a deeper level of complexity by introducing structured supply chains in Quarter districts for 8 industries:
- [ICON_Bullet] Baking
- [ICON_Bullet] Textiles
- [ICON_Bullet] Medicine
- [ICON_Bullet] Masonry
- [ICON_Bullet] Woodworking
- [ICON_Bullet] Metalworking
- [ICON_Bullet] Jewelry
- [ICON_Bullet] Brewing

## LOC_PEDIA_CONCEPTS_PAGE_CSC_FRAMEWORK_CHAPTER_CONTENT_TITLE
Supply Chain Framework

## LOC_PEDIA_CONCEPTS_PAGE_CSC_FRAMEWORK_CHAPTER_CONTENT_PARA_1
Each industry supply chain follows a structured progression with 5 distinct stages:

## LOC_PEDIA_CONCEPTS_PAGE_CSC_FRAMEWORK_CHAPTER_CONTENT_PARA_2
- 1. Materials extraction
- 2. Intermediate goods processing
- 3. Consumer goods production
- 4. Specialty goods production
- 5. Goods sales

## LOC_PEDIA_CONCEPTS_PAGE_CSC_FRAMEWORK_CHAPTER_CONTENT_PARA_3
Don't panic.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_FRAMEWORK_CHAPTER_CONTENT_PARA_4
This structure is the basis for understanding the mechanics of the entire mod. While there are some thematic variations in how this framework is implemented, it's about 80% consistent across the 8 Quarters.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_FRAMEWORK_CHAPTER_STRATEGY_TITLE
High-level gameplay design

## LOC_PEDIA_CONCEPTS_PAGE_CSC_FRAMEWORK_CHAPTER_STRATEGY_PARA_1
- [ICON_Bullet] In order to simplify gameplay with this mod later on, especially for the AI, a lot of strategic decisions have been frontloaded into the placement of Quarters. This is the main reason for the extensive use of adjacencies to guide players to place their Quarters adjacent to resources that feed the supply chain (stage 1), as well as the districts with which each Quarter later interacts.
- [ICON_Bullet] Adjacencies from specific resources employ a custom adjacency system that allows for more granular control of adjacencies.
- [ICON_Bullet] This adjacency-driven configuration then sets up the more detailed transactions between supply chain actors that unfold as the player progresses through the build trees of the respective districts, as well as the tech / civic trees. Decisions in the middle part of the gameplay of the mod (stages 2-5) are therefore mostly driven by opportunity cost, prioritisation of further investment in Quarters, along with specialist management, rather than detailed micro-management of transactions for each Quarter in a potentially wide empire.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_CONTENT_TITLE
Transactions

## LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_CONTENT_PARA_1
The mod introduces the concept of a transaction as an atomic pattern for the yields provided by an interaction between adjacent actors in a supply chain, and is an abstract modelling of the concepts of Supply, Demand and Payment.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_ACTORS_TITLE
Sellers and customers

## LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_ACTORS_PARA_1
Seller — A building or improvement that produces and sells goods or Materials.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_ACTORS_PARA_2
Customer (Buyer) — A building that purchases goods or Materials, either as an end-consumer or to process them further before acting as a Seller of its output.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_YIELDS_TITLE
Demand, Supply and Payment

## LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_YIELDS_PARA_1
Demand is driven by the Customer, and flows backward in the supply chain. Implemented as a [ICON_Production] Production yield bonus to the Seller, representing increased effort to meet demand.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_YIELDS_PARA_2
Supply is the output of the Seller's response to demand, i.e. the goods produced through that increased production, flowing forward in the supply chain. Implemented as a yield bonus to the Customer — mostly the Quarter's main yield, representing the value created by the supplied goods, but sometimes a more appropriate thematic yield.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_YIELDS_PARA_3
Payment for provided Supply is implemented as a [ICON_Gold] Gold yield bonus to the Seller.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_BALANCE_TITLE
The value of a transaction

## LOC_PEDIA_CONCEPTS_PAGE_CSC_TRANSACTIONS_CHAPTER_BALANCE_PARA_1
The ratio between Demand, Supply and Payment is used to represent some economic principles, e.g. the relative value of consumer goods vs specialty goods.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_CONTENT_TITLE
Stage 1: Materials extraction

## LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_CONTENT_PARA_1
- [ICON_Bullet] Stage 1 of supply chains consist of standard game improvements (e.g. Wheat Farms, Cotton Plantations and Lumber Mills) that extract Materials from resources or features on the map, and sell them as inputs to stage 2 and 4 buildings.
- [ICON_Bullet] Materials mapped to supply chains are classified as either [ICON_CSC_BASE] Base Materials or [ICON_CSC_SPEC] Specialty Materials.
- [ICON_Bullet] Standard game bonus resources in scope have mostly been classified as [ICON_CSC_BASE] Base Materials, while standard game luxury resources can be either a [ICON_CSC_BASE] Base Material or a [ICON_CSC_SPEC] Specialty Material, depending on their role in the specific supply chain.
- [ICON_Bullet] Some resources may be a [ICON_CSC_BASE] Base Material in one supply chain, and a [ICON_CSC_SPEC] Specialty Material in another.
- [ICON_Bullet] Standard game luxuries retain their standard [ICON_Amenities] Amenity effects, with Quarters offering supplementary local / regional amenities to provide further happiness management options.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_SUPPLIED_TITLE
What does supplied mean?

## LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_SUPPLIED_PARA_1
- [ICON_Bullet] Some effects of this mod have a requirement for a building in a Quarter to be "supplied", which means having an adjacent improved copy of a resource that has been mapped to the required type of Materials for the Quarter.
- [ICON_Bullet] E.g. a "supplied Bakery" is a Bakery that has an improved Wheat Farm adjacent to it. Since the Water Mill / Wind Mill is a prerequisite for constructing the Bakery, this will result in a fully functioning chain from Wheat Farm, to Mill, to Bakery.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_DEMAND_TITLE
Demand for Materials

## LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_DEMAND_PARA_1
- [ICON_Bullet] Demand for [ICON_CSC_BASE] Base Materials result in a +1 [ICON_Production] Production and +1 [ICON_Gold] Gold bonus from each adjacent stage 2 building to [ICON_CSC_BASE] Base Materials improvements
- [ICON_Bullet] M&C: +2 [ICON_Production] Production and +2 [ICON_Gold] Gold to an Industry, and +3 [ICON_Production] Production and +3 [ICON_Gold] Gold to a Corporation
- [ICON_Bullet] Demand for [ICON_CSC_SPEC] Specialty Materials result in a +1 [ICON_Production] Production and +1 [ICON_Gold] Gold bonus from each adjacent stage 4 building to [ICON_CSC_SPEC] Specialty Materials improvements
- [ICON_Bullet] M&C: +2 [ICON_Production] Production and +2 [ICON_Gold] Gold to an Industry, and +3 [ICON_Production] Production and +3 [ICON_Gold] Gold to a Corporation

## LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_MONOPOLIES_TITLE
Monopolies & Corporations

## LOC_PEDIA_CONCEPTS_PAGE_CSC_MATERIALS_CHAPTER_MONOPOLIES_PARA_1
- [ICON_Bullet] When the Monopolies & Corporations game mode is enabled, a mod setting becomes available that removes city-wide bonuses from Industry and Corporations improvements, as these bonuses are replaced by the effects of the Quarters.
- [ICON_Bullet] With this setting enabled, Industries and Corporations now serve as highly productive and profitable sources of [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials to Quarters instead.
- [ICON_Bullet] [ICON_Tourism] Tourism from resource Monopolies remains unchanged by this mod, regardless of whether the resource is used by a Quarter or not.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_CONTENT_TITLE
Quarters

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_CONTENT_PARA_1
- [ICON_Bullet] Stages 2, 3 and 4 of supply chains are implemented as buildings inside of 8 new districts called Quarters, each dedicated to the goods supply chain of a specific industry, e.g. Baking or Textiles.
- [ICON_Bullet] All Quarters unlock at Craftsmanship and have a maintenance cost of 1 [ICON_Gold] Gold.
- [ICON_Bullet] Each Quarter can only be constructed once per city, and count toward district slots.
- [ICON_Bullet] Each Quarter constructed in a city is more expensive than the previous one, but Quarter construction costs do not scale by game era.
- [ICON_Bullet] This ensures Quarters are accessible for developing new settlements throughout the game, supporting diverse playstyles.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_YIELDS_TITLE
Quarter yields and specialists

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_YIELDS_PARA_1
- [ICON_Bullet] While all Quarters gain [ICON_Production] Production and [ICON_Gold] Gold yields from their activities, each Quarter has a main yield focus, e.g. [ICON_Food] Food for the Bakers' Quarter.
- [ICON_Bullet] Buildings in the Quarter will provide this yield type as their main value proposition, although there is some thematic variance representing a part of the industry's evolution through the ages.
- [ICON_Bullet] Specialists provide the base yield of the Quarter, as well as a thematic yield.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_PLACEMENT_TITLE
Planning a Quarter

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_PLACEMENT_PARA_1
Quarters interact with upstream and downstream links in their supply chain in two steps:


## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_PLACEMENT_PARA_2
Adjacency bonuses are initially used to abstractly represent the interaction between the Quarter and other game elements that are adjacent to it.
- [ICON_Bullet] The flat yields from these adjacencies are particularly helpful to small cities, and represents the production and commercial potential of the Quarter.
- [ICON_Bullet] District adjacencies are bi-directional in order to guide the placement of both the Quarter and other districts, as adjacent districts are key to productive Quarters once the later stages of the supply chain are constructed.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_ADJACENCIES_TITLE
Adjacency bonuses

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_ADJACENCIES_PARA_1
- [ICON_Bullet] +1 [ICON_Production] Production to Quarters from each adjacent [ICON_CSC_BASE] Base Materials and [ICON_CSC_SPEC] Specialty Materials resource (stage 1) in their supply chain.
- [ICON_Bullet] This adjacency is from both unimproved and improved resources, mostly to help the AI evaluate placement decisions.
- [ICON_Bullet] +1 [ICON_Gold] Gold from each adjacent [ICON_CSC_SALES] Commercial Hub and any other districts (or their unique replacers) where the Quarter's products will later be sold (stage 5), representing the charter fees that Guilds historically paid to establish their presence in a city. Each of these adjacent districts receive +1 of the main yield of the Quarter in return, represents the provisions received from having such an established source of goods nearby.
- [ICON_Bullet] An exception to this is the district where intermediary goods will later be sold, which receives a more thematic yield in return, as intermediary goods often have a different secondary use and narrative from how they are used by later stages in the Quarter supply chain.
- [ICON_Bullet] The Commercial Hub provides an adjacency to all Quarters, as the Market is a valid customer for all stage 3 buildings, regardless of the Quarter's industry.
- [ICON_Bullet] For players using Albro's excellent City Lights mod, the supply chain system integrates with the urban vs. rural mechanics, as follows:
- [ICON_Bullet] [ICON_CSC_GOODS] Rural Communities provide a +1 [ICON_Production] Production adjacency bonus to Quarters instead of +1 [ICON_Gold] Gold in exchange for +1 of the main yield of the Quarter, representing availability of a rural workforce.
- [ICON_Bullet] [ICON_CSC_SALES] Urban Boroughs are treated as a point of sale (stage 5) for all Quarters, and hence provide an adjacency bonus of +1 [ICON_Gold] Gold, in exchange for +1 of the main yield of the Quarter in return.
- [ICON_Bullet] +1 [ICON_Production] Production from an adjacent Quarter that produces goods that are required by the industry in the Quarter, in exchange for a +1 [ICON_Gold] Gold adjacency bonus in return.
- [ICON_Bullet] +1 [ICON_Production] Production bonus from every 2 adjacent river segments, representing improved logistics.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_RELATIONSHIPS_TITLE
Building transactions

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_RELATIONSHIPS_PARA_1
Transactions between actors (suppliers, processors and customers) in the supply chain are then used as the basis for more detailed relationships, and are generally implemented as yields on adjacent buildings that are part of the transaction.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_QUARTERS_CHAPTER_RELATIONSHIPS_PARA_2
Transactions between adjacent buildings do not depend on whether the Quarter currently has adjacent improved Material resources. The adjacency and the required functioning supplier/customer buildings establish the sale itself. The exception is a Stage 2 transaction with a Material supplier, where the adjacent improved resource is one of the actors in the transaction.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_CONTENT_TITLE
Stage 2: Intermediary goods

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_CONTENT_PARA_1
Procures various [ICON_CSC_BASE] Base Materials from stage 1 suppliers and processes those into intermediary goods (e.g. flour, textiles) to sell to customers. These customers could be both downstream actors in its supply chain for further processing (stages 3 and 4), as well as consumers for direct use.
- [ICON_Bullet] Stage 2 buildings unlock with appropriate technologies or civics
- [ICON_Bullet] Low construction and maintenance cost
- [ICON_Bullet] Provide flat yields from transactions with other supply chain actors, and are designed to support smaller cities by exploiting resources on the map, benefiting wide play.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_INPUTS_TITLE
Material inputs

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_INPUTS_PARA_1
- [ICON_Bullet] Procures [ICON_CSC_BASE] Base Materials that belong to its supply chain as an input, by adding +1 [ICON_Production] Production (demand) and +1 [ICON_Gold] Gold (payment) to each adjacent [ICON_CSC_BASE] Base Materials improvement.
- [ICON_Bullet] M&C: Increased to +2 [ICON_Production] Production and +2 [ICON_Gold] Gold to an Industry improvement, and +3 [ICON_Production] Production and +3 [ICON_Gold] Gold to a Corporation.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_PROCESSING_TITLE
Processing and yields

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_PROCESSING_PARA_1
- [ICON_Bullet] Processes the procured [ICON_CSC_BASE] Base Materials into intermediary goods by generating +1 main yield of the Quarter (supply) for each adjacent [ICON_CSC_BASE] Base Materials improvement, with a fixed maintenance cost of -2 [ICON_Gold] Gold.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_SALES_TITLE
Customers and Services

## LOC_PEDIA_CONCEPTS_PAGE_CSC_INTERMEDIARY_CHAPTER_SALES_PARA_1
Sales transactions of intermediary goods are represented by:

- [ICON_Bullet] +1 [ICON_Production] Production (demand) and +1 [ICON_Gold] Gold (payment) to the stage 2 building, in return for +1 main yield of the Quarter (supply) to the local stage 3 and stage 4 buildings in the Quarter.
- [ICON_Bullet] +1 [ICON_Production] Production (demand) and +1 [ICON_Gold] Gold (payment) to the stage 2 building, in return for +1 of a thematic yield (supply) to an adjacent building (or its unique replacers) that has a relationship with the industry's intermediary goods during that era.
- [ICON_Bullet] With an appropriate Medieval Era (or later) technology / civic, this transaction enables the establishment of a Service building in the adjacent customer district, if the Quarter has an adjacent source of [ICON_CSC_BASE] Base Materials.
- [ICON_Bullet] The Service grants a [ICON_Citizen] Citizen slot in the customer district and applies an appropriate local or city-wide effect representing the value created by the supplied goods.
- [ICON_Bullet] The Service also provides +1 of an appropriate Great Person point per turn.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_CONTENT_TITLE
Stage 3: Consumer goods

## LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_CONTENT_PARA_1
Procures intermediary goods from a stage 2 supplier in the Quarter, and processes those into consumer goods (e.g. Bakery, Tailor, Carpenter) ready for sale to the general city population.
- [ICON_Bullet] Most stage 3 buildings unlock at Guilds, with some thematic variation.
- [ICON_Bullet] Requires a stage 2 (intermediary goods) building in the Quarter.
- [ICON_Bullet] Medium construction and maintenance cost.
- [ICON_Bullet] These buildings provide the dual benefit of a minor flat yield, as well as a yield that scales with each [ICON_Citizen] Citizen in the city, good for growing cities.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_INPUTS_TITLE
Intermediary goods inputs

## LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_INPUTS_PARA_1
- [ICON_Bullet] Purchases intermediary goods from its supply chain as an input, by adding +1 [ICON_Production] Production (demand) and +1 [ICON_Gold] Gold (payment) to the local stage 2 building in the Quarter.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_PROCESSING_TITLE
Processing and specialists

## LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_PROCESSING_PARA_1
Processes intermediary goods into consumer goods in two ways:

- [ICON_Bullet] Generating +1 main yield of the Quarter (supply), at a maintenance cost of -2 [ICON_Gold] Gold.
- [ICON_Bullet] Adding +1 [ICON_Citizen] Citizen slot, and granting +2 of the main yield of the Quarter (supply) to [ICON_Citizen] Citizens in the Quarter.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_SALES_TITLE
Customers and Services

## LOC_PEDIA_CONCEPTS_PAGE_CSC_CONSUMER_CHAPTER_SALES_PARA_1
Sales transactions of consumer goods to the city population is represented by:

- [ICON_Bullet] A scaling yield of +0.1 [ICON_Production] Production (demand) and +0.1 [ICON_Gold] Gold (payment) per [ICON_Citizen] Citizen in the City to the stage 3 building, in return for +0.1 of the main yield of the Quarter (supply) to an adjacent Market.
- [ICON_Bullet] The Market is always a valid customer for any stage 3 building, regardless of which Quarter they belong to, and hence this transaction is relevant to all Quarters.
- [ICON_Bullet] A scaling yield of +0.1 [ICON_Production] Production (demand) and +0.1 [ICON_Gold] Gold (payment) per [ICON_Citizen] Citizen in the City to the stage 3 building, in return for +0.1 of the main yield of the Quarter (supply) to an adjacent building (or its unique replacers) that has a relationship with the industry's consumer goods during that era.
- [ICON_Bullet] As each Quarter has their own specific set of customer districts and building over and above the Commercial Hub, this transaction is different for each stage 3 building, depending on the Quarter.
- [ICON_Bullet] With an appropriate Renaissance Era (or later) technology / civic, this transaction enables the establishment of a Service building in the adjacent district, if the Quarter has an adjacent improved source of [ICON_CSC_BASE] Base Materials.
- [ICON_Bullet] The Service grants a [ICON_Citizen] Citizen slot in the customer district and applies an appropriate effect representing the value created by recurring sales to that destination.
- [ICON_Bullet] The Service also provides +1 of an appropriate Great Person point per turn.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_CONTENT_TITLE
Stage 4: Specialty goods

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_CONTENT_PARA_1
Procures intermediary goods from a stage 2 supplier in the Quarter and various [ICON_CSC_SPEC] Specialty Materials from stage 1 suppliers, and transforms them into specialty goods (e.g. Café, Fashion House, Luthier) for sale to select customers.
- [ICON_Bullet] Most stage 4 buildings unlock at Humanism, with some unlocking at more appropriate Renaissance techs or civics.
- [ICON_Bullet] Requires a stage 2 (intermediary goods) building in the Quarter.
- [ICON_Bullet] This means that there is a fork in the progression tree for supply chain stages, with a stage 3 building not being required for a stage 4 building.
- [ICON_Bullet] Scaling yields that support tall play and large cities.
- [ICON_Bullet] High construction and maintenance cost.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_INPUTS_TITLE
Intermediary goods and Specialty Materials

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_INPUTS_PARA_1
Purchases inputs from two sources:

- [ICON_Bullet] Purchases intermediary goods from its supply chain as an input, by adding +1 [ICON_Production] Production (demand) and +1 [ICON_Gold] Gold (payment) to the local stage 2 building in the Quarter.
- [ICON_Bullet] Procures [ICON_CSC_SPEC] Specialty Materials that belong to its supply chain as an input, by adding +1 [ICON_Production] Production (demand) and +1 [ICON_Gold] Gold (payment) to each adjacent [ICON_CSC_SPEC] Specialty Materials improvement.
- [ICON_Bullet] M&C: Increased to +2 [ICON_Production] Production and +2 [ICON_Gold] Gold to an Industry improvement, and +3 [ICON_Production] Production and +3 [ICON_Gold] Gold to a Corporation.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_PROCESSING_TITLE
Processing and specialists

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_PROCESSING_PARA_1
Processes intermediary goods and [ICON_CSC_SPEC] Specialty Materials into Specialty goods by:

- [ICON_Bullet] Generating +1 main yield of the Quarter (supply) for each adjacent [ICON_CSC_SPEC] Specialty Materials improvement, with a fixed maintenance cost of -3 [ICON_Gold] Gold.
- [ICON_Bullet] Adding +1 [ICON_Citizen] Citizen slot, and granting +1 of the main yield of the Quarter and +1 of another thematic yield (supply) to [ICON_Citizen] Citizens in the Quarter.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_SALES_TITLE
Customers and Services

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SPECIALTY_CHAPTER_SALES_PARA_1
Sales transactions of Specialty goods to select customers are represented by:

- [ICON_Bullet] A scaling yield of +1 [ICON_Production] Production (demand) and +1 [ICON_Gold] Gold (payment) for every 5 [ICON_Citizen] Citizens in the City, in return for +1 of the main yield of the Quarter or an appropriate thematic yield (supply) to an adjacent customer building (or its unique replacers) that has a relationship with the industry's Specialty goods during that era.
- [ICON_Bullet] With an appropriate Industrial Era (or later) technology / civic, this transaction enables the establishment of a Service building in the adjacent customer district, if the Quarter has adjacent sources of both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials.
- [ICON_Bullet] The service grants a [ICON_Citizen] Citizen slot in the customer district and applies the final value created by the completed chain, such as tourism from leisure destinations served by a supplied Café.
- [ICON_Bullet] The Service also provides +1 of an appropriate Great Person point per turn.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_CONTENT_TITLE
Stage 5: Goods sales

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_CONTENT_PARA_1
Goods sales are stage 5 of the supply chain: intermediary goods, consumer goods and specialty goods reach their customers. A customer may use the goods directly or process them further before acting as a Seller of its own output.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_CONTENT_PARA_2
The Commercial Hub provides an adjacency to all Quarters, as the Market is a valid customer for all stage 3 buildings, regardless of the Quarter's industry. Each Quarter also has its own set of customer districts and buildings with a thematic relationship to its goods.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_CONTENT_PARA_3
Transactions between adjacent buildings do not depend on whether the Quarter currently has adjacent improved Material resources. The adjacency and the required functioning supplier/customer buildings establish the sale itself. The exception is a Stage 2 transaction with a Material supplier, where the adjacent improved resource is one of the actors in the transaction.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_POPULATION_TITLE
Population and market size

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_POPULATION_PARA_1
Whenever there is a scaling yield based on city population from a transaction between adjacent buildings from different cities, it is the customer's city population that is used as the multiplier, since that determines the market size and hence the value of the transaction.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_CONSUMERTRADE_TITLE
Trade routes: Consumer goods

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_CONSUMERTRADE_PARA_1
- [ICON_Bullet] +1 bonus of the main yield of the Quarter (supply) to [ICON_TradeRoute] Trade Routes with the City as destination. +1 [ICON_Production] Production and +1 [ICON_Gold] Gold to the Quarter in return, if the Quarter has an adjacent source of [ICON_CSC_BASE] Base Materials and the origin City does not have a similar Quarter.
- [ICON_Bullet] This ensures that there is always a way to sell the Quarter's consumer goods, even if it's not located adjacent to a Market or other customer building.
- [ICON_Bullet] This acquired access to consumer goods provides +1 [ICON_Amenities] Amenity in the origin city.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_SPECIALTYTRADE_TITLE
Trade routes: Specialty goods

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SALES_CHAPTER_SPECIALTYTRADE_PARA_1
- [ICON_Bullet] +1 bonus of the main yield of the Quarter (supply) to [ICON_TradeRoute] Trade Routes with the City as destination. +1 [ICON_Production] Production and +1 [ICON_Gold] Gold to the Quarter in return, if the Quarter has adjacent sources of both [ICON_CSC_BASE] Base and [ICON_CSC_SPEC] Specialty Materials and the origin City does not have a similar Quarter.
- [ICON_Bullet] This ensures that there is always a way to sell the Quarter's specialty goods, even if it's not located adjacent to a Market or other customer building.
- [ICON_Bullet] This acquired access to specialty goods for the upper class provides +1 [ICON_Amenities] Amenity in all cities within 6 tiles of the origin city.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SERVICES_CHAPTER_CONTENT_TITLE
Services

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SERVICES_CHAPTER_CONTENT_PARA_1
Services are the capstones of well-planned supply chains and represent how a stable goods economy enables a service economy. Services are implemented as an invisible building granted in the adjacent customer district once the appropriate supplier, customer, era unlock, and material-supply requirements are all met.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SERVICES_CHAPTER_EXAMPLES_TITLE
Customers and occupations

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SERVICES_CHAPTER_EXAMPLES_PARA_1
The customer building defines the destination and theme of the Service, while the supplied Quarter defines the industry that makes it viable. For example, a supplied Café can support:
- [ICON_Bullet] a Groundskeeper in an adjacent Entertainment district with a Zoo;
- [ICON_Bullet] a Ride Technician in an adjacent Water Park with a Ferris Wheel;
- [ICON_Bullet] a Horticulturist in an adjacent Garden with a Conservatory.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SERVICES_CHAPTER_EFFECTS_TITLE
Service effects

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SERVICES_CHAPTER_EFFECTS_PARA_1
Gameplay-wise, Services normally grant a [ICON_Citizen] Citizen slot in specialist-capable host districts and apply the value created by the completed supply chain: growth, housing, tourism, or another thematic effect. This keeps the chain readable: goods create recurring customers, recurring customers create local occupations, and those occupations expand the city's specialist capacity where the game supports it.

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SERVICES_CHAPTER_ART_TITLE
The visible impact of Services

## LOC_PEDIA_CONCEPTS_PAGE_CSC_SERVICES_CHAPTER_ART_PARA_1
Alternate Quarter-building art follows the same activation conditions as the related Service: the appropriate era unlock, the required adjacent improved Material supply, and an eligible adjacent customer. It illustrates the visible impact of the industry that enabled the Service, or the changed activity around the Quarter once that Service relationship is in place; it is not a visual indicator for every ordinary adjacent-building transaction.
