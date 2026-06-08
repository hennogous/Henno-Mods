---
title: Supply Chain Framework
---

# Supply Chain Framework

Each industry supply chain follows a structured progression with 5 distinct stages:

1. Materials extraction
2. Intermediate goods processing
3. Consumer goods production
4. Specialty goods production
5. Goods sales

Don't panic.

Everything you see in this picture will make sense in a while, and this structure is the basis for understanding the mechanics of the entire mod. While there are some thematic variations in how this framework is implemented, it's about 80% consistent across the 8 Quarters.

![Supply Chain Framework](../images/Civ%20Modding%20Projects%20-%20Supply%20Chain%20Framework.jpg)

## High-level gameplay design

* In order to simplify gameplay with this mod later on, especially for the AI, a lot of strategic decisions have been frontloaded into the placement of Quarters. This is the main reason for the extensive use of adjacencies to guide players to place their Quarter adjacent to resources that feed the supply chain (stage 1), as well as the districts with which each Quarter later interacts.
   * Adjacencies from specific resources employ a custom adjacency system that allows for more granular control of adjacencies.
* This adjacency-driven configuration then sets up the more detailed transactions (more on these below) between supply chain actors that unfold as the player progresses through the build trees of the respective districts, as well as the tech / civic trees. Decisions in the middle part of the gameplay of the mod (stages 2-4) are therefore mostly driven by opportunity cost, prioritisation of further investment in Quarters, along with specialist management, rather than detailed micro-management of transactions for each Quarter in a potentially wide empire.
* Once specialty products are produced through elective projects and placed into cities across the empire (stage 5), a new phase of strategic complexity enters the gameplay.
   * Specialty products replace the single-resource Products from M&C (optional via a setting, but recommended to avoid bloated gameplay with two types of Products), and leverages the in-game mechanics around Great Works in the same way. It's therefore strongly recommended to enable the M&C game mode when playing with this mod.

## Transactions

The mod introduces the concept of a transaction as an atomic pattern for the yields provided by an interaction between adjacent actors in a supply chain, and is an abstract modelling of the concepts of Supply, Demand and Payment.

* A Seller is a building or improvement that produces and sells goods or materials.
* A Buyer is a building that purchases goods or materials, either as an end-consumer or to process the goods and materials further before in turn acting as a Seller of the output.
* Demand is driven by the Buyer in the transaction, and flows backward in the supply chain. Demand is therefore always implemented as a {{production}} Production yield bonus to the Seller in the transaction, representing increased effort to meet goods demand.
* Supply is the output of the Seller's response to the demand, i.e. the goods produced through that increased production, and flows forward in the supply chain. Supply is always implemented as a yield bonus to the Buyer, representing the value created by the supplied goods. This yield is mostly the main yield of the Quarter (see below), but in some cases a more appropriate yield is used.
* Payment for provided Supply is implemented as a {{gold}} Gold yield bonus to the Seller.
   * When playing with the Taxes & Politics mod, this automatic payment element of the transactional model is replaced by a player-driven Taxation concept.
* The ratio between Demand, Supply and Payment is used to represent some economic principles, e.g. the relative value of consumer goods vs specialty goods.

## Services

Services are the capstone form of a successful supply chain transaction. They are not a separate sixth stage, and they are not simply extra text or effects attached to the destination building. A Service is an invisible building granted in the adjacent customer district once the appropriate supplier, customer, era unlock, and material-supply requirements are all met.

The customer building defines the destination and theme of the Service, while the supplied Quarter defines the industry that makes it viable. For example, a supplied Café can support:

* a Groundskeeper in an adjacent Entertainment district with a Zoo;
* a Ride Technician in an adjacent Water Park with a Ferris Wheel;
* a Horticulturist in an adjacent Garden with a Conservatory.

In each case the Zoo, Ferris Wheel, or Conservatory is the capstone destination for that branch of the chain. The ongoing effect belongs to the Service profession created by the completed relationship, not to the capstone building as if it had independently acquired a Bakers' Quarter bonus.

Gameplay-wise, Services normally grant a Citizen slot in the host district and apply the value created by the completed supply chain: growth, housing, tourism, or another thematic effect. This keeps the chain readable: goods create recurring customers, recurring customers create local occupations, and those occupations expand the city's specialist capacity.

## Stage 1: Materials extraction

* Stage 1 of supply chains consist of standard game improvements (e.g. Wheat Farms, Cotton Plantations and Lumber Mills) that extract materials from resources or features on the map, and sell them as inputs to stage 2 and 4 buildings.
* Materials mapped to supply chains are classified as either Base materials or Specialty materials.
* Standard game bonus resources in scope have mostly been classified as Base materials, while standard game luxury resources can be either a Base material or a Specialty material, depending on their role in the specific supply chain (see the Materials table for a mapping of resources to industries later on).
   * Some resources may be a Base material in one supply chain, and a Specialty material in another.
   * Standard game luxuries retain their standard {{amenity}} Amenity effects, with Quarters offering supplementary local / regional amenities to provide further happiness management options.
* Resources no longer provide city-wide bonuses from Industry and Corporations improvements, as these bonuses are replaced by the effects of the Quarters.
   * This means that only resources that are used by Quarters now result in city-wide effects.
   * {{tourism}} Tourism from resource Monopolies remains unchanged by this mod, regardless of whether the resource is used by a Quarter or not.
* While Industries and Corporations improvements on resources no longer provide city-wide effects or unlock Product projects, they now serve as highly productive and profitable sources of base and specialty materials to Quarters instead.
* Some effects of this mod have a requirement for an adjacent source of materials, which means an adjacent improved copy of a resource that has been mapped to the required type of materials.

* Demand for Base materials result in a +1 {{production}} Production and +1 {{gold}} Gold bonus from each adjacent stage 2 building to Base materials improvements
   * M&C: +2 {{production}} Production and +2 {{gold}} Gold to an Industry, and +3 {{production}} Production and +3 {{gold}} Gold to a Corporation
* Demand for Specialty materials result in a +1 {{production}} Production and +1 {{gold}} Gold bonus from each adjacent stage 4 building to Specialty materials improvements
   * M&C: +2 {{production}} Production and +2 {{gold}} Gold to an Industry, and +3 {{production}} Production and +3 {{gold}} Gold to a Corporation

![Stage 1](../images/Civ%20Modding%20Projects%20-%20Stage%201.jpg)

## Stage 2-4: Quarters

* Stages 2, 3 and 4 of supply chains are implemented as buildings inside of each of 8 new districts called Quarters, each dedicated to the goods supply chain of a specific industry, e.g. Baking or Textiles.
* All Quarters unlock at Craftsmanship.
* Each Quarter can only be constructed once per city, and count toward district slots.

* While all Quarters gain {{production}} Production and {{gold}} Gold yields from their activities, each Quarter has a main yield focus, e.g. {{food}} Food for the Bakers' Quarter.
   * Buildings in the Quarter will provide this yield type as their main value proposition, although there is some thematic variance representing a part of the industry's evolution through the ages.
   * Specialists provide the base yield of the Quarter, as well as a thematic yield.

* Quarters interact with upstream and downstream links in their supply chain in two steps:

1. Adjacency bonuses are initially used to abstractly represent the interaction between the Quarter and other game elements that are adjacent to it.
   * The flat yields from these adjacencies are particularly helpful to small cities, and represents the production and commercial potential of the Quarter.
   * District adjacencies are bi-directional in order to guide the placement of both the Quarter and other districts, as adjacent districts are key to productive Quarters once the later stages of the supply chain are constructed.

   * +1 {{production}} Production to Quarters from each adjacent base materials and specialty materials resource (stage 1) in their supply chain.
      * This adjacency is from both unimproved and improved resources, mostly to help the AI evaluate placement decisions.
   * +1 {{gold}} Gold from each adjacent Commercial Hub and any other districts (or their unique replacers) where the Quarter's products will later be sold (stage 5), in exchange for +1 of the main yield of the Quarter in return.
      * An exception to this is the district where intermediary goods will later be sold, which receives a more thematic yield in return, as intermediary goods often have a different secondary use and narrative from how they are used by later stages in the Quarter supply chain.
      * For players using Albro's excellent City Lights mod, the supply chain system integrates with the urban vs. rural mechanics, as follows:
      * Rural Communities provide a +1 {{production}} Production adjacency bonus to Quarters instead of +1 {{gold}} Gold in exchange for +1 of the main yield of the Quarter, representing availability of a rural workforce.
      * Urban Boroughs are treated as a point of sale (stage 5) for all Quarters, and hence provide an adjacency bonus of +1 {{gold}} Gold, in exchange for +1 of the main yield of the Quarter in return.
   * +1 {{production}} Production from an adjacent Quarter that produces goods that are required by the industry in the Quarter, in exchange for a +1 {{gold}} Gold adjacency bonus in return.
   * +1 {{production}} Production bonus from every 2 adjacent river segments, representing improved logistics.

2. Transactions between actors (suppliers, processors and customers) in the supply chain are then used as the basis for more detailed relationships, and are generally implemented as yields on adjacent buildings that are part of the transaction.

* Each Quarter constructed in a city is more expensive than the previous one, but Quarter construction costs do not scale by game era.
   * This ensures Quarters are accessible for developing new settlements throughout the game, supporting diverse playstyles.

### Stage 2 – Intermediary goods building

Procures various Base materials from stage 1 suppliers and processes those into intermediary goods (e.g. flour, textiles) to sell to customers. These customers could be both downstream actors in its supply chain for further processing (stages 3 and 4), as well as consumers for direct use.

* Stage 2 buildings unlock with appropriate technologies or civics
* Low construction and maintenance cost
* Provide flat yields from transactions with other supply chain actors, and are designed to support smaller cities by exploiting resources on the map, benefiting wide play.

![Stage 2](../images/Civ%20Modding%20Projects%20-%20Stage%202.jpg)

* Procures Base materials that belong to its supply chain as an input, by adding +1 {{production}} Production (demand) and +1 {{gold}} Gold (payment) to each adjacent Base materials improvement.
   * M&C: Increased to +2 {{production}} Production and +2 {{gold}} Gold to an Industry improvement, and +3 {{production}} Production and +3 {{gold}} Gold to a Corporation.

* Processes the procured Base materials into intermediary goods by generating +1 main yield of the Quarter (supply) for each adjacent Base materials improvement, with a fixed maintenance cost of -2 {{gold}} Gold.

* Sales transactions of intermediary goods are represented by:
   * +1 {{production}} Production (demand) and +1 {{gold}} Gold (payment) to the stage 2 building, in return for +1 main yield of the Quarter (supply) to the local stage 3 and stage 4 buildings in the Quarter.
   * +1 {{production}} Production (demand) and +1 {{gold}} Gold (payment) to the stage 2 building, in return for +1 of a thematic yield (supply) to an adjacent building (or its unique replacers) that has a relationship with the industry's intermediary goods during that era.
      * With an appropriate Medieval Era (or later) technology / civic, this transaction enables the establishment of a Service building in the adjacent customer district, if the Quarter has an adjacent source of Base materials.
      * This Service is the capstone of that intermediary-goods relationship. It grants a Citizen slot in the customer district and applies an appropriate local or city-wide effect representing the value created by the supplied goods.

### Stage 3 – Consumer goods building

Procures intermediary goods from a stage 2 supplier in the Quarter, and processes those into consumer goods (e.g. Bakery, Tailor, Carpenter) ready for sale to the general city population.

* Most stage 3 buildings unlock at Guilds, with some thematic variation.
* Requires a stage 2 (intermediary goods) building in the Quarter.
* Medium construction and maintenance cost.
* These buildings provide the dual benefit of a minor flat yield, as well as a yield that scales with each Citizen in the city, good for growing cities.

![Stage 3](../images/Civ%20Modding%20Projects%20-%20Stage%203.jpg)

* Purchases intermediary goods from its supply chain as an input, by adding +1 {{production}} Production (demand) and +1 {{gold}} Gold (payment) to the local stage 2 building in the Quarter.

* Processes intermediary goods into consumer goods in two ways:
   * Generating +1 main yield of the Quarter (supply), at a maintenance cost of -2 {{gold}} Gold.
   * Adding +1 Citizen slot, and granting +2 of the main yield of the Quarter (supply) to Citizens in the Quarter.

* Sales transactions of consumer goods to the city population is represented by:
   * A scaling yield of +0.1 {{production}} Production (demand) and +0.1 {{gold}} Gold (payment) per Citizen in the City to the stage 3 building, in return for +0.1 of the main yield of the Quarter (supply) to an adjacent Market.
      * Whenever there is a scaling yield based on city population from a transaction between adjacent buildings from different cities, it is the customer's city population that is used as the multiplier, since that determines the market size and hence the value of the transaction.
      * At the moment, both the main yield and the {{gold}} Gold yield will be given to the customer city, but in the future I want to change this to use the customer's city population to give {{gold}} Gold back to the seller's city.
   * A scaling yield of +0.1 {{production}} Production (demand) and +0.1 {{gold}} Gold (payment) per Citizen in the City to the stage 3 building, in return for +0.1 of the main yield of the Quarter (supply) to an adjacent building (or its unique replacers) that has a relationship with the industry's consumer goods during that era.
      * With an appropriate Renaissance Era (or later) technology / civic, this transaction enables the establishment of a Service building in the adjacent district, if the Quarter has an adjacent source of Base materials.
      * This Service is the capstone of that consumer-goods relationship. It grants a Citizen slot in the customer district and applies an appropriate effect representing the value created by recurring sales to that destination.
   * +1 bonus of the main yield of the Quarter to trade routes with the City as destination, and +1 {{gold}} Gold to the City in return, if the Quarter has an adjacent source of Base materials and the origin City does not have a similar Quarter.
      * This ensures that there is always a way to sell the Quarter's consumer goods, even if it's not located adjacent to a Market or other customer building.
      * Access to consumer goods provides +1 {{amenity}} Amenity in the city.

### Stage 4 - Specialty goods building

Procures intermediary goods from a stage 2 supplier in the Quarter and various Specialty materials from stage 1 suppliers, and transforms them into specialty goods (e.g. Café, Fashion House, Luthier) for sale to select customers.

* Most stage 4 buildings unlock at Humanism, with some unlocking at more appropriate Renaissance techs or civics.
* Requires a stage 2 (intermediary goods) building in the Quarter.
* This means that there is a fork in the progression tree for supply chain stages, with a stage 3 building not being required for a stage 4 building.
* Scaling yields that support tall play and large cities.
* High construction and maintenance cost.
* Single-resource Products from M&C are optionally completely removed from the game, and replaced by specialty products produced in specialty goods buildings.

![Stage 4](../images/Civ%20Modding%20Projects%20-%20Stage%204.jpg)

* Purchases inputs from two sources:
   * Purchases intermediary goods from its supply chain as an input, by adding +1 {{production}} Production (demand) and +1 {{gold}} Gold (payment) to the local stage 2 building in the Quarter.
   * Procures Specialty materials that belong to its supply chain as an input, by adding +1 {{production}} Production (demand) and +1 {{gold}} Gold (payment) to each adjacent Specialty materials improvement.
      * M&C: Increased to +2 {{production}} Production and +2 {{gold}} Gold to an Industry improvement, and +3 {{production}} Production and +3 {{gold}} Gold to a Corporation.

* Processes intermediary goods and Specialty materials into Specialty goods by:
   * Generating +1 main yield of the Quarter (supply), at a maintenance cost of -3 {{gold}} Gold.
   * Adding +1 Citizen slot, and granting +1 of the main yield of the Quarter and +1 of another thematic yield (supply) to Citizens in the Quarter.

* Sales transactions of Specialty goods to select customers is represented by:
   * A scaling yield of +1 {{production}} Production (demand) and +1 {{gold}} Gold (payment) for every 5 Citizens in the City, in return for +1 of the main yield of the Quarter (supply) to an adjacent customer building (or its unique replacers) that has a relationship with the industry's Specialty goods during that era.
      * Whenever there is a scaling yield based on city population from a transaction between adjacent buildings from different cities, it is the customer's city population that is used as the multiplier, since that determines the market size and hence the value of the transaction.
      * At the moment, both the main yield and the {{gold}} Gold yield will be given to the customer city, but in the future I want to change this to use the customer's city population to give {{gold}} Gold back to the seller's city.
      * With an appropriate Industrial Era (or later) technology / civic, this transaction enables the establishment of a Service building in the adjacent customer district, if the Quarter has adjacent sources of both Base and Specialty materials.
      * This Service is the capstone of that specialty-goods relationship. It grants a Citizen slot in the customer district and applies the final value created by the completed chain, such as tourism from leisure destinations served by a supplied Café.
   * +1 bonus of the main yield of the Quarter to trade routes with the City as destination, and +1 {{gold}} Gold to the City in return, if the Quarter has adjacent sources of both Base and Specialty materials and the origin City does not have a similar Quarter.
      * This ensures that there is always a way to sell the Quarter's specialty goods, even if it's not located adjacent to a Market or other customer building.
      * Access to specialty goods for the upper class provides +1 {{amenity}} Amenity in all cities within 6 tiles.

## Stage 5: Goods sales

For the most part, sales of different types of goods to buyers (stage 5) were described in the sections above along with the building that produced the goods. There is however one additional exclusive customer and a related new type of governor: The Aristocrat and The Commissioner.

* The Aristocrat: Acts as a local investor and patron for Quarters in the city, commissioning and displaying specialty goods in its private collection.

   * Once a specialty goods building (stage 4) has been constructed in the Quarter, a suitable technology / civic enables a Commissioner governor (see below) with a Local Lords promotion to grant an Aristocrat in the city.
   * Aristocrats are implemented as buildings in the city center, but don't appear on the map(???).
   * Provide loyalty equal to double the {{amenity}} Amenity surplus / deficit of the city, representing the role that local nobility played in the unity or fragmentation of empires.
   * Increase the combat strength of the city, representing the military burden of Aristocrats and the resources they command.

   * Each local Aristocrat gives the city access to a Commission New Specialty Item project in the city, which can be completed twice.
   * This project produces a Specialty Item fitting the Quarter.
   * Aristocrats have 3 slots to display commissioned specialty items in their private collections.
      * Commissioned specialty goods have local effects and can be traded between Aristocrats, as well as other players.
      * Private collections have theming bonuses for specialty goods from the same Quarter, but different civilizations.

   * In the future, having a certain number of Aristocrats will grant additional governor titles, representing the ascension of an Aristocrat into central government.

* The Commissioner: A new governor, with a promotion tree focused on Quarters, Burghers and Aristocrats.
* Might add one or two titles along the civic tree to make it easier to appoint / promote a governor

* Base ability:
   * Master of Guilds (base ability): +20% {{production}} Production towards Quarters in the city

* Promotions:
   * Guardian of the Peasants: +10% growth in the city
   * Middle Class Hero: Grant specialist slots to districts adjacent to Quarters that don't already have them
   * Local Lords: Grant Aristocrats to Quarters with specialty goods buildings.
   * Land Ownership: {{culture}} Culture bomb tiles around Quarters in cities with Aristocrats.
   * Patronage: +100% Great Person Points from specialists in the city

---

Incorporating all of the details from the 5 supply chain stages as well as the 5 social classes, leads to a supply chain framework that looks like this. While there are some thematic variations in how this framework is implemented, it's about 80% consistent across the 8 Quarters.

![Supply Chain Framework details](../images/Civ%20Modding%20Projects%20-%20Supply%20Chain%20Framework%20details.jpg)
