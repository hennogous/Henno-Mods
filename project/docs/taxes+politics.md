Got it. Below is a corrected and consolidated design overview, rewritten to incorporate your clarifications precisely and to tighten terminology. This version assumes the reader is a Civ VI modder and is explicit about rules, yields, prerequisites, and intent, not narrative.

---

# **Comprehensive Design Overview (Revised)**

## **Spatial Supply Chains, Taxation, and Political Loyalty**

---

## **1\. Core Design Intent**

This mod replaces Civ VI’s largely additive, state-owned economic model with a spatial supply-demand economy that:

* Generates non-Gold yields automatically through adjacency-based Transactions

* Generates Gold only through player-chosen taxation

* Uses Loyalty as the primary balancing mechanism

* Creates persistent tension between:

  * Guilds (urban production)

  * Landed Elite (territorial control)

  * Church (landscape & legitimacy)

  * Monarchy (extraction and arbitration)

The system is designed to:

* Be legible via tiles and adjacencies

* Minimize hidden capacity math

* Integrate into Civ VI’s placement-first gameplay

---

## **2\. Terminology**

### **Transaction**

A Transaction exists when:

* A Seller building and a specified Buyer building are adjacent (or in the same Quarter), and

* Required material improvements are adjacent

Transactions:

* Always produce yields

* Produce Gold only if taxed

* Are never disabled by politics

### **Supply and Demand (Directional Yields)**

* Supply (forward):

   \+Yield flowing from Seller → Buyer

* Demand (backward):

   \+Production flowing from Buyer → Seller

Taxation extracts Gold from the Seller, i.e. from Demand.

---

## **3\. Guilds (Quarters)**

### **3.1 Representation**

* New Quarter Districts, each representing an industry (Bakers, Tailors, etc.)

* Each Quarter may contain:

  * Tier 1: Intermediary Goods building

  * Tier 2: Consumer Goods building

  * Tier 3: Specialty Goods building

* Tier 1 is a prerequisite for Tier 2 and Tier 3

* One instance of each building per Quarter

---

### **3.2 Quarter Placement (Front-Loaded, Non-Taxable)**

These effects apply immediately upon district placement.

#### **Favorable Inputs**

* \+1 Production to the Quarter for each adjacent improved resource mapped to that Quarter’s supply chain

* \+1 Production if adjacent to a River

#### **Charter Payments**

* \+1 Gold to the Quarter for each adjacent district that can later host a Buyer building

Charter Gold:

* Is not taxed

* Represents permission to operate

* Exists solely to guide placement

---

### **3.3 Quarter Buildings and Supply**

Quarter buildings have no intrinsic yields.

All yields arise from Transactions.

#### **Tier 1 (Intermediary Goods)**

* \+1 main yield per adjacent improved base material

* Enables downstream Transactions

* Provides Supply to Buyers and Demand to Sellers

#### **Tier 2 (Consumer Goods)**

* Requires Tier 1

* Generates Supply only via Transactions

* Scales “for the many”

#### **Tier 3 (Specialty Goods)**

* Requires Tier 1

* Requires adjacent improved specialty material

* Generates Supply only via Transactions

* Unlocks Elite commissions

* Scales “for the few”

---

### **3.4 Buyer Specification**

Each Quarter building has explicit Buyer buildings, for example:

* Wind Mill → Granary

* Textile Workshop → Shipyard

* Bakery → Market

* Tailor → Consulate

* Fashion House → Opera House

Transactions occur only with valid Buyers.

---

### **3.5 Transaction Yields**

#### **Tier 1 → Buyer**

* Seller (Tier 1): \+1 Production (Demand)

* Buyer: \+1 appropriate yield (Supply)

#### **Tier 2 → Buyer**

* Seller (Tier 2): \+X Production

* Buyer: \+X yield

   Where X \= 0.2 × city population

#### **Tier 3 → Buyer**

* Seller (Tier 3): \+Y Production

* Buyer: \+Y yield

   Where Y \= \+1 per 5 city population

---

### **3.6 Guild Taxation**

#### **External Guild Tax**

Applies to Transactions between Quarter buildings and Buyers in other districts.

* \+1 Gold per Transaction

* −1 Loyalty per Transaction (to the Quarter)

#### **Internal Guild Tax**

Applies to internal Quarter Transactions (Tier 1 → Tier 2 → Tier 3).

* \+1 Gold per internal Transaction

* −1 Loyalty flat to the Quarter

Internal tax is always “medium”.

Applying both internal and external taxation represents “high” pressure.

Guilds:

* Prefer Governors

* Having a Governor in the city offsets −1 Loyalty from Guild taxation

---

## **4\. Landed Elite (Estates)**

### **4.1 Representation**

* Estate District

* Build conditions:

  * A Governor is present

  * A Land Grants policy is active

* Construction triggers a culture bomb

* Manor House is part of the base district (not a building)

---

### **4.2 Area of Influence**

* 3-tile radius

* Effects are spatial, not city-wide

---

### **4.3 Baseline Loyalty Effects (Within Radius)**

* \+1 Loyalty per improved tile

* −5 Loyalty per Urban District

Urban Districts:

* City Center

* Commercial Hub

* Entertainment Complex

* Quarter Districts

Excluded:

* Holy Sites

* Encampments

* City Lights Rural Communities

---

### **4.4 Elite Taxation**

#### **External Elite Tax (Land-Based)**

* \+1 Gold per improved tile within radius

* −1 Loyalty per tile

#### **Internal Elite Tax (Commissions)**

Triggered by Tier 3 Specialty Goods commissioned by the Estate.

* \+1 Gold per active commission

* −1 Loyalty per commission

Elite dislike:

* Services

* Urban density

* Governors

Each Service in the city:

* Increases Estate Loyalty penalties by \+1

---

## **5\. Church (Holy Sites)**

### **5.1 Representation**

* Standard Holy Sites

* Unified global actor (no local differentiation)

---

### **5.2 Area of Influence**

* 2-tile radius

Within radius:

* \+1 Loyalty per unimproved tile with Charming+ Appeal

* −5 Loyalty per Estate within 3 tiles

---

### **5.3 City-Wide Legitimacy**

* If city follows the player’s founded religion:

  * \+City Loyalty (scales by era)

* Otherwise:

  * No bonus

---

### **5.4 Church Taxation**

#### **External Church Tax (Land-Based)**

* \+1 Gold per unimproved tile within Holy Site radius

* −1 Loyalty per tile

#### **Internal Church Tax (Doctrine-Based)**

* \+1 Gold per active belief effect in the city

* −1 Loyalty flat to the city

The Church dislikes:

* Specialty Goods buildings

* Elite commissions

* Excess Services

---

## **6\. Services and Urban Growth**

* Services are granted when:

  * A valid Transaction adjacency exists

  * Required materials are adjacent

  * Relevant tech/civic is unlocked

Effects:

* Improve yields and growth

* Represent urbanization

Political impact:

* −1 Loyalty from Estates per Service

* −1 Loyalty from Church per Service (after specific civics)

---

## **7\. State-Owned Economy (Baseline Civ VI)**

* Gold from:

  * Improvements outside Estate/Holy Site influence

  * Districts not engaged in Transactions

* Is considered state-run

* Is not taxed

* Provides a stable economic floor

---

## **8\. Monarchy (Player Role)**

The player:

* Does not generate Gold automatically from supply chains

* Extracts Gold via taxation policies

* Balances:

  * Loyalty

  * Urban growth

  * Political pressure

Governors:

* Stabilize Loyalty

* Are disliked by Elite and Church

* Preferred by Guilds

---

## **9\. Loyalty Difficulty Settings (Pre-Game)**

Global scalar on Loyalty penalties:

* Low: ×0.5

* Standard: ×1.0

* High: ×1.5–2.0

Rules unchanged; magnitudes only.

---

## **10\. Summary**

* Adjacency creates Supply and Demand

* Demand produces Production

* Taxation converts Production into Gold

* Gold extraction destabilizes cities

* Terrain and placement define city identity

* No dominant strategy; map-responsive gameplay

This system is database-driven, modular, and designed to feel like an integrated extension of Civ VI rather than a parallel economy.

Below is a clean reminder of the major, sharp loyalty levers for each political bloc, framed the way you asked earlier: few, legible, high-impact. I’m deliberately not listing secondary or “nice to have” effects — only the levers that meaningfully move loyalty and therefore drive player decisions.

---

## **1\. Monarchy (Player)**

Core loyalty posture

* Neutral by default.

* Loyalty is not generated directly, but converted into:

  * Gold (via taxation)

  * Diplomatic Favor / Mandate (optional system you mentioned)

Major loyalty interactions

* Taxation policies are the Monarchy’s primary loyalty sink.

* Governors provide baseline stabilization, but are disliked by all blocs.

Pressure role

* The Monarchy is the arbiter:

  * Who gets taxed

  * Where unrest is tolerated

  * When loyalty is “spent” for cash or war prep

---

## **2\. Guilds (Quarters)**

What they like

* Urban density

* Buyers (district adjacencies)

* Governors in the city

* Trade routes (local or foreign)

Major loyalty levers

* \+ Loyalty:

  * Quarters adjacent to City Center / urban districts

  * Presence of Governor

* – Loyalty:

  * Guild taxation

     (external sales tax and internal quarter tax are the primary levers)

  * Competition with other Quarters (soft cap via adjacency limits)

Design intent

* Guild loyalty is transaction-sensitive, not land-sensitive.

* They tolerate import/export, but hate being squeezed internally.

Sharp rule

Every taxable Guild transaction risks urban unrest.

---

## **3\. Landed Elite (Estates)**

What they like

* Control over improved land

* Low district density nearby

* Weak urbanization

* Access to luxury commissions

Major loyalty levers

* \+ Loyalty:

  * Each improved tile within Estate influence

* – Loyalty:

  * Any District (except City Lights Rural Communities, if you choose) within influence

  * Services established in the city (proxy for urban growth)

  * Elite land taxation

Design intent

* Estates are powerful but brittle.

* They give strong passive loyalty but react violently to:

  * Urban encroachment

  * Administrative extraction

Sharp rule

Estates buy stability with land, and lose it with cities.

---

## **4\. Church (Holy Sites)**

What they like

* Open land

* Moral authority

* Religious dominance

* Limited excess and luxury

Major loyalty levers

* \+ Loyalty:

  * Unimproved or high-Appeal tiles

  * City follows the Player’s founded religion

* – Loyalty:

  * Elite proximity (competition for land authority)

  * Excessive luxury / specialty production (Tier 3 pressure)

  * Church land taxation

  * Competing religions (if enabled)

Design intent

* The Church is empire-wide and uniform, unlike Estates.

* It stabilizes low-development cities but resists indulgence and concentration of wealth.

Sharp rule

The Church tolerates poverty, fears excess, and rivals land power.

---

## **5\. Cross-Bloc Tensions (the important ones)**

These are the few interactions worth modeling:

* Elite ↔ Guilds

  * Elite dislike urban Services

  * Elite crave commissions from Guild specialty goods

* Elite ↔ Church

  * Direct rivalry over land authority

  * Strong mutual loyalty penalties in proximity

* Church ↔ Guilds

  * Dislikes luxury and excess

  * Tolerates basic provisioning

* All blocs ↔ Governor

  * Mild loyalty penalty (central authority)

  * Guilds tolerate it best

---

## **6\. What you wisely chose** 

## **not**

##  **to model**

This is important for restraint:

* No fine-grained class satisfaction

* No per-building micro loyalty

* No constant trickle penalties

* No ideological sliders

Loyalty moves only when the player makes structural choices:

* Place districts

* Enable taxes

* Push urbanization

* Centralize authority

---

## **One-line summary**

* Guild loyalty responds to transactions and taxation

* Elite loyalty responds to land and urban intrusion

* Church loyalty responds to land purity, religion, and excess

* Monarchy loyalty is the budget you spend on power

That’s the backbone. Everything else is decoration.

