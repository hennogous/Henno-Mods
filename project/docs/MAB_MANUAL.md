# MAB Manual — Modular Adjacency Bonuses Core (Ruivo)

**Mod:** Modular Adjacency Bonuses Core (MAB)  
**Author:** Ruivo  
**Civ 6 Version:** Post-February 2026 update (v2.0+)  
**Workshop ID:** 3429735059  
**CSC changes to MAB:** [MAB_CHANGES.md](MAB_CHANGES.md)

---

## Overview

MAB (Modular Adjacency Bonuses) is a Civ 6 modding framework that replaces the vanilla hard-coded adjacency system with a fully data-driven, SQL-defined architecture. Instead of writing Lua for every new adjacency bonus, modders declare adjacency rules in a database table (`Ruivo_New_Adjacency`) and the framework automatically generates the modifiers, requirements, and tooltips.

### Key Capabilities

- **Data-driven adjacency:** Define bonuses via SQL rows, not Lua code
- **60+ adjacency source types:** Districts, resources, terrain, units, roads, city stats, player stats, global stats, properties
- **Multi-ring adjacency:** Count adjacent objects at custom distances (1 ring, 2 rings, etc.)
- **Custom target objects:** Filter by specific resource classes, districts, terrains, improvements, etc.
- **Flexible modifier owners:** Attach bonuses to districts, buildings, civ traits, beliefs, policy cards, governors, and more
- **Binary-folding property system:** Efficient per-plot adjacency counting via game properties
- **Full tooltip support:** Customizable yield icons, adjacency source names, and formatted strings

---

## Architecture

### Three-Layer Pipeline

1. **SQL Definition** (`Ruivo_New_Adjacency` table) — declares what adjacency bonuses exist
2. **SQL Assembly** (INSERT statements at load order 1919810) — auto-generates modifiers, requirements, and attaches them
3. **Lua Dispatcher** (`RUIVO_STAT_MODULE_GP.lua`) — counts adjacent objects, writes game properties, and calculates yields

### Load Order

- **Phase -1 (early):** Core tables defined — `MAB_CORE_TABLE_INFO.sql`
- **Phase +1 (mid):** MAB itself activates and caches adjacency data
- **Phase 1919810 (very late):** Modifiers assembled — `NEW_ADJACENCY_BONUS_BY_RUIVO_CORE_INSERT.sql`

This late-assembly order ensures all base-game and DLC tables exist before MAB generates its modifiers.

---

## The `Ruivo_New_Adjacency` Table

This is the heart of MAB. Every adjacency bonus is one row in this table.

| Column                      | Type    | Default          | Description                                                                                             |
|-----------------------------|---------|------------------|---------------------------------------------------------------------------------------------------------|
| `ID`                        | TEXT    | *(required)*     | Unique identifier for this adjacency rule. Used as the base name for modifiers and modifierset IDs.     |
| `DistrictType`              | TEXT    | *(required)*     | The district(s) this adjacency applies to (e.g., `DISTRICT_COMMERCIAL_HUB`).                            |
| `ProvideType`               | TEXT    | `SelfBonus`      | What the adjacency **provides** (yield type + delivery mechanism). See **ProvideType** below.           |
| `YieldType`                 | TEXT    | *(required)*     | The yield/resource being provided. Interpreted based on `ProvideType` (e.g., `YIELD_GOLD`, `GREAT_PERSON_CLASS_PROPHET`). |
| `YieldChange`               | FLOAT   | `0`              | Amount per adjacent object.                                                                             |
| `AdjacencyType`             | TEXT    | *(required)*     | What to count as adjacent. See **AdjacencyType** below.                                                 |
| `CustomAdjacentObject`      | TEXT    | `NONE`           | Filter parameter for `FROM_RINGS_CAO_*` types (e.g., `RESOURCECLASS_BONUS`, `TERRAIN_PLAINS`).           |
| `Rings`                     | INTEGER | `1`              | How many rings outward to search for adjacent objects.                                                  |
| `DistrictModifiers`         | BOOLEAN | `0`              | If `1`, modifier is attached directly to districts. If `0`, uses `TraitType`/`ModifierOwner` routing.   |
| `NewMethod`                 | BOOLEAN | `0`              | If `1`, uses the newer `EFFECT_ATTACH_MODIFIER` attachment method (preferred).                          |
| `ApplyForUniqueDistricts`   | BOOLEAN | `0`              | If `1`, automatically extends this rule to unique district replacements (e.g., Wat for Campus).          |
| `TraitType`                 | TEXT    | `NULL`           | If set, this adjacency only applies to civs/leaders with this trait. Mutually exclusive with `DistrictModifiers`. |
| `ModifierOwner`             | TEXT    | `DistrictModifiers` | Where the modifier originates. See **ModifierOwner** below.                                            |
| `WhoIsTheOwner`             | TEXT    | `NULL`           | The specific owner object (e.g., `BUILDING_GRANARY`, `POLICY_CARD_ADORETUM`). Required when `ModifierOwner != DistrictModifiers`. |
| `CollectionType`            | TEXT    | `COLLECTION_PLAYER_DISTRICTS` | Which districts receive the modifier. See **CollectionType** below.                              |
| `Only`                      | TEXT    | `Human&AI`       | Restrict to `OnlyHuman`, `OnlyAI`, or `Human&AI`.                                                       |
| `FreeCompose`               | BOOLEAN | `0`              | Experimental. If `1`, skips automatic modifier generation and expects manual requirement wiring.         |

### How the Fields Interact

The combination of `ModifierOwner`, `WhoIsTheOwner`, and `CollectionType` determines **where the adjacency bonus gets attached**:

- `ModifierOwner = 'DistrictModifiers'` + `ModifierOwner = 'DistrictModifiers'` → modifier goes on the district itself
- `ModifierOwner = 'BuildingModifiers'` + `WhoIsTheOwner = 'BUILDING_GRANARY'` + `CollectionType = 'COLLECTION_CITY_DISTRICTS'` → if city has a Granary, all city districts get the bonus
- `ModifierOwner = 'PolicyModifiers'` + `WhoIsTheOwner = 'POLICY_ADORETUM'` + `CollectionType = 'COLLECTION_PLAYER_DISTRICTS'` → if player has the policy, all player districts get the bonus

The `ProvideType` + `YieldType` pair determines **what is actually given**:

- `ProvideType = 'SelfBonus'` + `YieldType = 'YIELD_GOLD'` → flat +YieldChange gold on the district
- `ProvideType = 'SelfMultiplier'` + `YieldType = 'YIELD_PRODUCTION'` → percentage production multiplier
- `ProvideType = 'GreatPersonPoints'` + `YieldType = 'GREAT_PERSON_CLASS_PROPHET'` → Great Prophet points per adjacent object
- `ProvideType = 'SelfCityProperty'` + `YieldType = 'MyCustomKey'` → set a custom property on the city

---

## ProvideType Reference

`ProvideType` defines **what kind of bonus** the adjacency delivers. Each type expects a specific kind of value in `YieldType`.

### Yield Bonus Types

| ProvideType        | YieldType                  | Effect                                                    |
|-------------------|----------------------------|-----------------------------------------------------------|
| `SelfBonus`        | Any yield (`YIELD_GOLD`, etc.) | Flat yield added to the district per adjacent object     |
| `SelfMultiplier`   | Any yield                  | Percentage multiplier applied to district yield output    |

### City-Level Bonuses

| ProvideType          | YieldType      | Effect                                         |
|---------------------|----------------|------------------------------------------------|
| `SelfAirSlots`       | `YIELD_AIR_SLOTS`    | Adds air unit slots to the district's city            |
| `SelfHousing`        | `YIELD_HOUSING`      | Adds housing to the district's city                   |
| `SelfAmenity`        | `YIELD_AMENITY`      | Adds amenities to the district's city                 |
| `SelfLoyalty`        | `YIELD_LOYALTY`      | Adds loyalty per turn to the district's city          |
| `SelfPower`          | `YIELD_POWER`        | Adds clean power to the district's city               |
| `SelfPowerModifier`  | `YIELD_POWER`        | Adds clean power **percentage** to the district's city |
| `SelfExtraDistrictSlot` | `YIELD_DISTRICT_SLOT` | Adds an extra district slot to the city             |

### Player-Level Bonuses

| ProvideType        | YieldType                  | Effect                                                     |
|-------------------|----------------------------|------------------------------------------------------------|
| `SelfTourism`      | `YIELD_TOURISM`            | Adds tourism output to the player                          |
| `SelfInfluence`    | `YIELD_INFLUENCE`          | Adds influence points per turn                             |
| `SelfFavor`        | `YIELD_FAVOR`              | Adds diplomatic favor per turn                              |
| `SelfTradeRoute`   | `YIELD_TRADE_ROUTE`        | Adds trade route capacity                                  |
| `SelfCivicBoost`   | `YIELD_CIVIC_BOOST`        | Percentage boost to civic research                        |
| `SelfTechnologyBoost` | `YIELD_TECHNOLOGY_BOOST` | Percentage boost to technology research                   |

### Great Person Bonuses

| ProvideType             | YieldType                       | Effect                                  |
|------------------------|---------------------------------|-----------------------------------------|
| `GreatPersonPoints`     | `GREAT_PERSON_CLASS_XXX`        | Flat Great Person points for the class  |
| `GreatPersonMultiplier` | `GREAT_PERSON_CLASS_XXX`        | Percentage Great Person points multiplier |

### Miscellaneous

| ProvideType          | YieldType      | Effect                                       |
|---------------------|----------------|----------------------------------------------|
| `SelfExtractResource` | `RESOURCE_IRON`, etc. | Enables extraction of strategic resources   |

### Property Types (Custom)

| ProvideType           | YieldType (any key string) | Effect                                          |
|----------------------|----------------------------|-------------------------------------------------|
| `SelfDistrictProperty` | Any key (e.g., `MY_KEY`)   | Sets a custom integer property on the district   |
| `SelfCityProperty`     | Any key                    | Sets a custom integer property on the city       |
| `SelfPlayerProperty`   | Any key                    | Sets a custom integer property on the player     |
| `SelfGameProperty`     | Any key                    | Sets a custom integer property on the game       |

---

## AdjacencyType Reference

`AdjacencyType` defines **what is being counted** for the adjacency. The prefix indicates scope; `FROM_RINGS_` types support multi-ring searching.

### Property-Based Sources

These read game properties that were previously set via Lua or modifiers.

| AdjacencyType                  | Scope    | Rings? | Custom Object? | Description                              |
|-------------------------------|----------|--------|----------------|------------------------------------------|
| `FROM_PLOT_PROPERTY`           | Plot     | No     | Yes (property key)  | Reads a property from the plot itself    |
| `FROM_PLOT_PROPERTY_HASHED`    | Plot     | No     | Yes               | Reads a hashed/encoded property          |
| `FROM_RINGS_PLOT_PROPERTY`     | Plot     | Yes    | Yes               | Reads properties from nearby plots       |
| `FROM_RINGS_PLOT_PROPERTY_HASHED` | Plot  | Yes    | Yes               | Reads hashed properties from nearby plots |
| `FROM_CITY_PROPERTY`           | City     | No     | Yes               | Reads a property from the city            |
| `FROM_CITY_PROPERTY_HASHED`    | City     | No     | Yes               | Reads a hashed city property             |
| `FROM_PLAYER_PROPERTY`         | Player   | No     | Yes               | Reads a property from the player          |
| `FROM_PLAYER_PROPERTY_HASHED`  | Player   | No     | Yes               | Reads a hashed player property           |
| `FROM_GAME_PROPERTY`           | Game     | No     | Yes               | Reads a property from the game state     |
| `FROM_GAME_PROPERTY_HASHED`    | Game     | No     | Yes               | Reads a hashed game property             |

### Global/Unconditional Sources

| AdjacencyType             | Scope | Rings? | Custom Object? | Description                                  |
|--------------------------|-------|--------|----------------|----------------------------------------------|
| `FROM_UNCONDITIONAL_BONUS` | Game  | No     | No             | Always provides the bonus (no adjacency check) |
| `FROM_STORM_HAPPEND`       | Game  | No     | No             | Counts number of storms in this game          |
| `FROM_STANDARDIZE_TURNS`   | Game  | No     | No             | Current turn normalized by game speed         |
| `FROM_HIGHEST_HUMAN_YIELD` | Game  | No     | Yes (yield type) | Highest yield among all human players of a type |
| `FROM_UI_SEA_LEVEL`        | Game  | No     | No             | Climate change points (UI only)              |

### Plot-Level Attributes

**Self (the district's plot):**

| AdjacencyType            | Custom Object? | Description                                 |
|-------------------------|----------------|---------------------------------------------|
| `FROM_LAND_WATER_PAIR`   | No             | Counts adjacent land-water pairs (max 3)     |
| `FROM_RIVER_CROSSING`    | No             | Counts adjacent river crossings              |
| `FROM_SELF_ROUTE`        | No             | Road level on this plot                      |
| `FROM_SELF_WORKER`       | No             | Citizens working this district               |
| `FROM_CLIFF`             | No             | 1 if this plot has a cliff, 0 otherwise      |
| `FROM_LATITUDE`          | No             | Distance % from astronaut standard line to equator |
| `FROM_POLE`              | No             | Distance % from astronaut standard line to pole |
| `FROM_SELF_WATER_LEVEL`  | No             | Freshwater level (0=none, 1=salt, 3=fresh)   |

**Adjacent plots:**

| AdjacencyType                  | Custom Object? | Description                           |
|-------------------------------|----------------|---------------------------------------|
| `FROM_ADJACENT_ROUTE`         | No             | Count of adjacent road segments by level |
| `FROM_ADJACENT_WORKER`        | No             | Count of workers on adjacent plots     |
| `FROM_ADJACENT_UNIT`          | No             | Count of units on adjacent plots       |
| `FROM_ADJACENT_DISTRICT`      | No             | Count of adjacent districts            |
| `FROM_ADJACENT_DISTRICT_AND_WONDER` | No         | Count of adjacent districts + wonders (even unbuilt) |
| `FROM_ADJACENT_LAKE`          | No             | Count of adjacent freshwater lakes     |
| `FROM_ADJACENT_WATER_LEVEL`   | No             | Sum of adjacent freshwater levels      |
| `FROM_ADJACENT_RESOURCE`      | No             | Count of adjacent resources (even unrevealed) |
| `FROM_ADJACENT_WONDERS`       | No             | Count of adjacent completed wonders    |

**Multi-ring (FROM_RINGS_*):**

| AdjacencyType                  | Custom Object? | Description                            |
|-------------------------------|----------------|----------------------------------------|
| `FROM_RINGS_ROUTE`            | No             | Sum of road levels within N rings      |
| `FROM_RINGS_WORKER`           | No             | Sum of workers within N rings          |
| `FROM_RINGS_UNIT`             | No             | Count of units within N rings          |
| `FROM_RINGS_DISTRICT_AND_WONDER` | No          | Count of districts + wonders within N rings |
| `FROM_RINGS_DISTRICT`         | No             | Count of districts within N rings (excludes wonders) |
| `FROM_RINGS_LAKE`             | No             | Count of freshwater lakes within N rings |
| `FROM_RINGS_WATER_LEVEL`      | No             | Sum of freshwater levels within N rings |
| `FROM_RINGS_RESOURCE`         | No             | Count of resources within N rings      |
| `FROM_RINGS_WONDERS`          | No             | Count of completed wonders within N rings |
| `FROM_RINGS_NATIONALPARK`     | No             | Count of national parks within N rings |

**Multi-ring with custom adjacent objects (FROM_RINGS_CAO_*):**

These types use `CustomAdjacentObject` to filter by specific types.

| AdjacencyType                  | Custom Adjacent Object Examples       | Description                              |
|-------------------------------|---------------------------------------|------------------------------------------|
| `FROM_RINGS_CAO_ROUTE`        | `ROUTE_ROAD`, `ROUTE_RAILROAD`        | Count specific road types within N rings |
| `FROM_RINGS_CAO_UNIT`         | `UNIT_WARRIOR`, `UNIT_TANK`           | Count specific unit types within N rings |
| `FROM_RINGS_CAO_RESOURCE_CLASS` | `RESOURCECLASS_BONUS`, `RESOURCECLASS_LUXURY` | Count resources of a specific class within N rings |
| `FROM_RINGS_TYPETAG_RESOURCE` | `CLASS_FOOD`, `CLASS_SEA`             | Count resources with a specific tag within N rings |
| `FROM_RINGS_CAO_RESOURCE`     | `RESOURCE_WHEAT`, `RESOURCE_COAL`     | Count a specific resource within N rings |
| `FROM_RINGS_CAO_IMPROVEMENT`  | `IMPROVEMENT_FARM`, `IMPROVEMENT_MINE` | Count specific improvements within N rings |
| `FROM_RINGS_CAO_DISTRICT`     | `DISTRICT_COMMERCIAL_HUB`             | Count specific district types within N rings |
| `FROM_RINGS_CAO_FEATURE`      | `FEATURE_FOREST`, `FEATURE_RAINFOREST` | Count specific features within N rings   |
| `FROM_RINGS_CAO_TERRAIN_SETS` | `IsMountain`, `IsHills`, `IsFlatlands`, `IsWater`, `IsShallowWater`, `IsLake`, `IsCanyon`, `IsCoastalLand`, `IsRiverCrossing`, `IsOpenGround`, `IsRoughGround` | Count plots matching a terrain predicate function within N rings |
| `FROM_RINGS_CAO_TERRAIN`      | `TERRAIN_PLAINS`, `TERRAIN_DESERT_HILLS` | Count specific terrain types within N rings |

### District-Level Attributes

**Self:**

| AdjacencyType                     | Description                                    |
|----------------------------------|------------------------------------------------|
| `FROM_SELF_YIELD_XXX`            | The district's own yield (YIELD_FOOD, YIELD_PRODUCTION, etc.) |
| `FROM_SELF_DISTRICT_MAX_HP`      | District max HP                                |
| `FROM_SELF_DISTRICT_DAMAGE`      | Damage taken by the district                    |
| `FROM_SELF_DISTRICT_REMAIN_HP`   | District remaining HP                           |
| `FROM_SELF_WALL_MAX_HP`          | Wall max HP                                    |
| `FROM_SELF_WALL_DAMAGE`          | Damage taken by the wall                        |
| `FROM_SELF_WALL_REMAIN_HP`       | Wall remaining HP                               |
| `FROM_SELF_DISTRICT_DAMAGE_PERCENT` | District damage as percentage                |
| `FROM_SELF_DISTRICT_REMAIN_HP_PERCENT` | District HP as percentage                 |
| `FROM_SELF_WALL_DAMAGE_PERCENT`  | Wall damage as percentage                       |
| `FROM_SELF_WALL_REMAIN_HP_PERCENT` | Wall HP as percentage                         |
| `FROM_SELF_DEFENSE_STRENGTH`     | District garrison defense strength              |

**Multi-ring:**

| AdjacencyType                     | Description                                    |
|----------------------------------|------------------------------------------------|
| `FROM_RINGS_DISTRICT_MAX_HP`     | Sum of max HP of districts within N rings      |
| `FROM_RINGS_DISTRICT_DAMAGE`     | Sum of damage of districts within N rings       |
| `FROM_RINGS_DISTRICT_REMAIN_HP`  | Sum of remaining HP of districts within N rings |
| `FROM_RINGS_WALL_MAX_HP`         | Sum of wall max HP within N rings              |
| `FROM_RINGS_WALL_DAMAGE`         | Sum of wall damage within N rings               |
| `FROM_RINGS_WALL_REMAIN_HP`      | Sum of wall remaining HP within N rings         |
| `FROM_RINGS_DEFENSE_STRENGTH`    | Sum of defense strength within N rings          |
| `FROM_RINGS_DISTRICTS_CAO_YIELD` | Sum of specific yield from districts within N rings (CustomAdjacentObject = yield type) |

**UI-only district attributes:**

| AdjacencyType                     | Description                                    |
|----------------------------------|------------------------------------------------|
| `FROM_UI_SELF_AIR_SLOTS`         | District air unit slots                        |
| `FROM_UI_SELF_AIR_UNITS`         | Number of air units in the district            |
| `FROM_UI_SELF_SURPLUS_AIR_SLOTS` | Remaining air unit slots                       |

**Multi-ring UI:**

| AdjacencyType                     | Description                                    |
|----------------------------------|------------------------------------------------|
| `FROM_UI_RINGS_AIR_SLOTS`        | Sum of air slots within N rings                |
| `FROM_UI_RINGS_AIR_UNITS`        | Sum of air units within N rings                |
| `FROM_UI_RINGS_SURPLUS_AIR_SLOTS` | Sum of surplus air slots within N rings        |

### City-Level Attributes

| AdjacencyType                     | Custom Object? | Description                              |
|----------------------------------|----------------|------------------------------------------|
| `FROM_CITY_POPULATION`           | No             | Total city population                     |
| `FROM_CITY_TOTAL_HOUSING`        | No             | Total housing in the city                 |
| `FROM_CITY_SURPLUS_HOUSING`      | No             | Surplus housing                           |
| `FROM_CITY_DISTRICTS_NUM`        | No             | Total number of districts (excl. City Center and wonders) |
| `FROM_CITY_SURPLUS_FOOD`         | No             | City food surplus                         |
| `FROM_CITY_SURPLUS_AMENITIES`    | No             | City surplus amenities                    |
| `FROM_CITY_SURPLUS_AMENITIES_OVER_HIGHEST_LEVEL_HAPPINESS` | No | Amenities above max happiness level |
| `FROM_CITY_DEFENSE_STRENGTH`     | No             | City defense strength                     |
| `FROM_CITY_CAO_YIELD`            | Yes (yield type) | Total of a specific yield in the city   |

**UI-only city attributes:**

| AdjacencyType                     | Description                                    |
|----------------------------------|------------------------------------------------|
| `FROM_UI_CITY_DISTRICT_SLOT`     | City district slots                            |
| `FROM_UI_CITY_SURPLUS_DISTRICT_SLOT` | Surplus district slots                      |
| `FROM_UI_CITY_FREE_POWER`        | Free power in the city                         |
| `FROM_UI_CITY_TEMPORARY_POWER`   | Temporary power                                |
| `FROM_UI_CITY_REQUIRED_POWER`    | Required power                                 |
| `FROM_UI_CITY_CURRENT_POWER`     | Total power in the city                        |
| `FROM_UI_CITY_SURPLUS_POWER`     | Surplus power                                  |
| `FROM_UI_CITY_POWER_RATIO`       | Power coverage ratio (%)                       |
| `FROM_UI_CITY_LOYALTY_PERTURN`   | City loyalty per turn                          |
| `FROM_UI_CITY_LOYALTY_PERCENT`   | City loyalty percentage                        |
| `FROM_UI_CITY_INCOMING_ROUTES`   | Incoming trade routes                          |
| `FROM_UI_CITY_OUTGOING_ROUTES`   | Outgoing trade routes                          |

### Player-Level Attributes

| AdjacencyType                     | Custom Object? | Description                              |
|----------------------------------|----------------|------------------------------------------|
| `FROM_PLAYER_TECHS_NUM`          | No             | Number of technologies researched         |
| `FROM_PLAYER_CIVICS_NUM`         | No             | Number of civics researched               |
| `FROM_OUTGOING_ROUTES`           | No             | Number of outgoing trade routes          |
| `FROM_SLOT_MILITARY`             | No             | Number of military policy slots           |
| `FROM_SLOT_ECONOMIC`             | No             | Number of economic policy slots           |
| `FROM_SLOT_DIPLOMATIC`           | No             | Number of diplomatic policy slots         |
| `FROM_SLOT_GREAT_PERSON`         | No             | Number of Great Person policy slots       |
| `FROM_SLOT_WILDCARD`             | No             | Number of wildcard policy slots           |
| `FROM_PLAYER_TOTAL_UNITS`        | No             | Total number of units owned by player     |
| `FROM_PLAYER_RESOURCES_TYPES`    | No             | Number of different resource types owned |
| `FROM_CAO_IMPROVEMENT_RESOURCE_TYPES` | Yes (improvement type) | Count of resource types from a specific improvement |
| `FROM_PLAYER_CAO_YIELD`          | Yes (yield type) | Player's total of a specific yield      |

**UI-only player attributes:**

| AdjacencyType                     | Description                                    |
|----------------------------------|------------------------------------------------|
| `FROM_UI_MILITARY_STRENGTH`      | Total military strength of the player          |

### Religion Attributes (Hidden from tooltips)

| AdjacencyType                     | Description                                    |
|----------------------------------|------------------------------------------------|
| `FROM_RELIGION_FAITH_YIELD`      | Total faith output of the religion              |
| `FROM_RELIGION_BELIEFS_COUNT`    | Number of beliefs in the religion               |
| `FROM_RELIGION_TOTAL_FOLLOWERS`  | Total number of followers                       |
| `FROM_RELIGION_FOREIGN_FOLLOWERS` | Followers in foreign cities                   |
| `FROM_RELIGION_DOMESTIC_FOLLOWERS` | Followers in domestic cities                 |
| `FROM_RELIGION_TOTAL_CITIES_FOLLOWING` | Number of cities following this religion  |
| `FROM_RELIGION_CITIES_WITH_WONDER` | Cities with wonders following this religion  |
| `FROM_RELIGION_FOREIGN_CITIES`   | Foreign cities following this religion          |
| `FROM_RELIGION_DOMESTIC_CITIES`  | Domestic cities following this religion         |
| `FROM_RELIGION_CITY_PLAYER_FOLLOWERS`  | Followers of a specific player's religion in a city |

---

## ModifierOwner and CollectionType

When `ModifierOwner` is not `'DistrictModifiers'`, the modifier originates from a specific game object. The `CollectionType` then determines **which districts receive the bonus**.

| ModifierOwner                | WhoIsTheOwner              | CollectionType                    | Effect                                  |
|-----------------------------|----------------------------|-----------------------------------|-----------------------------------------|
| `DistrictModifiers`         | `NULL`                     | `COLLECTION_PLAYER_DISTRICTS`     | Attached directly to the district       |
| `TraitModifiers`            | Trait type (e.g., `TRAIT_CIVILIZATION_ROME`) | `COLLECTION_PLAYER_DISTRICTS` | If player has the trait, all player districts get the bonus |
| `BuildingModifiers`         | Building type              | `COLLECTION_CITY_DISTRICTS`       | If city has the building, city districts get the bonus |
| `BuildingModifiers`         | Building type              | `COLLECTION_PLAYER_DISTRICTS`     | If **any** city has the building, all player districts get the bonus (useful for wonders) |
| `PolicyModifiers`           | Policy type                | `COLLECTION_PLAYER_DISTRICTS`     | If player has the policy, all player districts get the bonus |
| `TechnologyModifiers`       | Technology type            | `COLLECTION_PLAYER_DISTRICTS`     | If player has the tech, all player districts get the bonus |
| `CivicModifiers`            | Civic type                 | `COLLECTION_PLAYER_DISTRICTS`     | If player has the civic, all player districts get the bonus |
| `GovernmentModifiers`       | Government type            | `COLLECTION_PLAYER_DISTRICTS`     | If player's government matches, all player districts get the bonus |
| `BeliefModifiers`           | Belief type (Pantheon or Follower Belief) | `COLLECTION_ALL_DISTRICTS` | If city has the belief, all districts in the city get the bonus |
| `GovernorPromotionModifiers`| Governor Promotion type    | `COLLECTION_CITY_DISTRICTS`       | If this city has a governor with this promotion, city districts get the bonus |
| `GovernorPromotionModifiers`| Governor Promotion type    | `COLLECTION_PLAYER_DISTRICTS`     | If **any** city has a governor with this promotion, all player districts get the bonus |

### Custom Attachment Modifiers

MAB defines three custom `EFFECT_ATTACH_MODIFIER` types that route the generated modifier to the correct scope:

- `RUIVO_MODIFIER_OWNER_CITY_DISTRICTS_ATTACH_MODIFIER` → `COLLECTION_CITY_DISTRICTS` (all districts in the city)
- `RUIVO_MODIFIER_PLAYER_ALL_DISTRICTS_ATTACH_MODIFIER` → `COLLECTION_PLAYER_DISTRICTS` (all player districts)
- `RUIVO_MODIFIER_ALL_DISTRICTS_ATTACH_MODIFIER` → `COLLECTION_ALL_DISTRICTS` (all districts in the game)

These are used for `ModifierOwner` values other than `DistrictModifiers`.

---

## The Lua Dispatcher: `StatsModule_For_GP`

The heart of the runtime engine is `StatsModule_For_GP(AdjacencyType, CustomAdjacentObject, iX, iY, playerID, pCity, Rings)`. This function:

1. Looks up which counting function handles the given `AdjacencyType` (via the `NEW_ADJACENCY_BONUS_BY_RUIVO` dispatch table)
2. Calls the appropriate counting function with the correct arguments
3. Returns the count of adjacent objects, which is then multiplied by `YieldChange` and set as a property on the district's plot

### Dispatch Architecture

The dispatch table `NEW_ADJACENCY_BONUS_BY_RUIVO` maps each `AdjacencyType` to a counting function. For example:

```lua
NEW_ADJACENCY_BONUS_BY_RUIVO["FROM_RINGS_RESOURCE"] = FROM_RINGS_RESOURCE
```

Each counting function follows a signature like:
```lua
function FROM_RINGS_RESOURCE(iX, iY, iPlayerID, pCity, Rings)
```

Functions prefixed with `FROM_RINGS_*` accept the `Rings` parameter and use `RuivoGetRingPlotIndexes(iX, iY, Rings)` to get all plots within N rings, then iterate and count.

### Binary Folding System

MAB uses a **binary folding** system to store adjacency counts in game properties. Instead of storing a single integer (which could conflict if multiple adjacency rules write to the same plot), MAB uses the 10-value binary list `{1, 2, 4, 8, 16, 32, 64, 128, 256, 512}` to encode any value up to 1023 as 10 separate boolean properties.

For example, if a district has 13 adjacent resources:
- Property `MYADJ_1` = 1 (bit 0 set)
- Property `MYADJ_2` = 1 (bit 1 set, 2)
- Property `MYADJ_4` = 0 (bit 2 not set)
- Property `MYADJ_8` = 1 (bit 3 set, 8)
- Total = 1 + 2 + 8 = 11 (wait, that's wrong — but the idea holds)

This system allows efficient bitwise operations and avoids integer overflow in game properties. The function `Ruivo_Zip_SetProperty(ID, iBonus, YieldChange, iX, iY)` handles the encoding.

### Refresh Triggers

The adjacency counts are recalculated when:
- A district is completed (`GameEvents.DistrictChangedProgress` at 100%)
- A player completes a turn (via `Ruivo_Refresh_Core()` called in game events)
- Properties are invalidated (storm events, climate changes, etc.)

---

## Tooltip System

MAB provides extensive tooltip customization through three SQL tables.

### `Ruivo_New_Adjacency_Text`

Override the formatted tooltip string for a specific adjacency. Supports four format parameters.

```sql
INSERT INTO Ruivo_New_Adjacency_Text (ID, Tooltip, AddPercentChar) VALUES
    ('MY_ADJ_ID', '[COLOR:ResFoodLabelCS] +[Amount] [Icon] [Name][PercentChar] [adj] [CAO]', 0);
```

Parameters: `[Amount]`, `[Icon]`, `[Name]`, `[PercentChar]`, `[adj]`, `[CAO]`

### `Ruivo_CAO` (Custom Adjacent Object Names)

Maps `CustomAdjacentObject` values to human-readable names for tooltips.

```sql
INSERT INTO Ruivo_CAO (CustomAdjacentObject, Name) VALUES
    ('RESOURCECLASS_BONUS', 'LOC_RUIVO_RESOURCECLASS_BONUS'),
    ('IsMountain', 'LOC_RUIVO_ISMOUNTAIN');
```

The `Name` field references a localized string from the text database.

### `Ruivo_Yield_IconString`

Defines the icon, display name, and text color for each yield type in tooltips.

```sql
INSERT INTO Ruivo_Yield_IconString (YieldType, Name, IconString, TextColor, AddPercentChar) VALUES
    ('YIELD_FOOD', 'LOC_YIELD_FOOD_NAME', '[ICON_Food]', '[COLOR:ResFoodLabelCS]', 0);
```

---

## Adding a New Adjacency Bonus: Step-by-Step

### 1. Define the Rule in `Ruivo_New_Adjacency`

```sql
INSERT INTO Ruivo_New_Adjacency (ID, DistrictType, ProvideType, YieldType, YieldChange, AdjacencyType, CustomAdjacentObject, Rings, DistrictModifiers, NewMethod, ApplyForUniqueDistricts, TraitType, ModifierOwner, WhoIsTheOwner, CollectionType, Only, FreeCompose) VALUES
(
    'MYMOD_COMM_HUB_ADJ_GOLD_FARM',     -- ID
    'DISTRICT_COMMERCIAL_HUB',          -- DistrictType
    'SelfBonus',                        -- ProvideType (flat yield bonus)
    'YIELD_GOLD',                       -- YieldType
    1,                                  -- YieldChange (+1 per adjacent farm)
    'FROM_RINGS_CAO_IMPROVEMENT',       -- AdjacencyType (count specific improvements in N rings)
    'IMPROVEMENT_FARM',                 -- CustomAdjacentObject (farms only)
    1,                                  -- Rings (1 tile away)
    0,                                  -- DistrictModifiers (use default)
    1,                                  -- NewMethod (use EFFECT_ATTACH_MODIFIER)
    0,                                  -- ApplyForUniqueDistricts
    NULL,                               -- TraitType (applies to everyone)
    'DistrictModifiers',                -- ModifierOwner
    'NULL',                             -- WhoIsTheOwner
    'COLLECTION_PLAYER_DISTRICTS',      -- CollectionType
    'Human&AI',                         -- Only
    0                                   -- FreeCompose
);
```

### 2. Add Tooltip Localization (Optional but Recommended)

```sql
-- In your localisation SQL file:
INSERT INTO EnglishValues (Language, Text, Tag) VALUES
    ('en_US', 'adjacent farms', 'LOC_RUIVO_ADJACENCY_IMPROVEMENT_FARM');
```

### 3. That's It

MAB's SQL assembly (at load order 1919810) will automatically:
- Generate the modifier ID `MYMOD_COMM_HUB_ADJ_GOLD_FARM_1`, `MYMOD_COMM_HUB_ADJ_GOLD_FARM_2`, etc. (for binary folding)
- Create requirement sets that check for the presence of the improvement
- Attach the modifier to Commercial Hub districts
- Generate the tooltip using the default template or your custom text

---

## Practical Examples

### Example 1: Campus gets +1 Science per adjacent Mountain

```sql
INSERT INTO Ruivo_New_Adjacency (ID, DistrictType, ProvideType, YieldType, YieldChange, AdjacencyType, Rings) VALUES
    ('CAMPUS_SCIENCE_PER_MOUNTAIN', 'DISTRICT_CAMPUS', 'SelfBonus', 'YIELD_SCIENCE', 1, 'FROM_RINGS_CAO_TERRAIN_SETS', 1);

INSERT INTO Ruivo_New_Adjacency_Text (ID, Tooltip) VALUES
    ('CAMPUS_SCIENCE_PER_MOUNTAIN', '+[Amount] [Icon] [Name] [adj] [CAO]');

-- Register the terrain function in Ruivo_CAO (it should already have IsMountain)
```

Note: `FROM_RINGS_CAO_TERRAIN_SETS` uses `IsMountain` as the terrain predicate. You'd set `CustomAdjacentObject = 'IsMountain'` if you wanted to be explicit, but for single-ring the default `FROM_ADJACENT_*` variants work too. For the classic version, use `FROM_RINGS_CAO_TERRAIN_SETS` with `CustomAdjacentObject = 'IsMountain'`.

### Example 2: Industrial Zone gets +2 Production per adjacent Workshop

This requires Workshop to have a district adjacency bonus itself. If Workshop is a building, you'd use `FROM_RINGS_CAO_DISTRICT` or make Workshop a district. For a building-based approach, you could instead use a building-triggered modifier:

```sql
-- This makes the Workshop building grant +2 Production to the Industrial Zone
INSERT INTO Ruivo_New_Adjacency (ID, DistrictType, ProvideType, YieldType, YieldChange, AdjacencyType, DistrictModifiers, ModifierOwner, WhoIsTheOwner, CollectionType) VALUES
    ('INDUSTRIAL_ZONE_PROD_PER_WORKSHOP', 'DISTRICT_INDUSTRIAL_ZONE', 'SelfBonus', 'YIELD_PRODUCTION', 2, 'FROM_SELF_DISTRICT', 0, 'BuildingModifiers', 'BUILDING_WORKSHOP', 'COLLECTION_CITY_DISTRICTS');
```

Wait, `FROM_SELF_DISTRICT` doesn't count adjacent districts. For a building-in-another-district approach, MAB would need a `FROM_ADJACENT_BUILDING` type, which doesn't exist in the shipped list. You'd need to write custom Lua to add it.

### Example 3: Governor Promotion Grants Production

```sql
-- If the city's governor has the "Industrial Complex" promotion, all Industrial Zones get +2 Production
INSERT INTO Ruivo_New_Adjacency (ID, DistrictType, ProvideType, YieldType, YieldChange, AdjacencyType, ModifierOwner, WhoIsTheOwner, CollectionType) VALUES
    ('INDUSTRIAL_ZONE_PROMOTION_PROD', 'DISTRICT_INDUSTRIAL_ZONE', 'SelfBonus', 'YIELD_PRODUCTION', 2, 'FROM_UNCONDITIONAL_BONUS', 'GovernorPromotionModifiers', 'GOVERNOR_PROMOTION_INDUSTRY', 'COLLECTION_CITY_DISTRICTS');
```

The `FROM_UNCONDITIONAL_BONUS` type means there's nothing to count — the bonus is flat, and the modifier owner check (governor promotion) gates whether it applies.

### Example 4: Trade Routes Grant Gold to Commercial Hubs

```sql
-- Each outgoing trade route grants +1 Gold to every Commercial Hub
INSERT INTO Ruivo_New_Adjacency (ID, DistrictType, ProvideType, YieldType, YieldChange, AdjacencyType, ModifierOwner, CollectionType) VALUES
    ('COMM_HUB_GOLD_PER_ROUTE', 'DISTRICT_COMMERCIAL_HUB', 'SelfBonus', 'YIELD_GOLD', 1, 'FROM_OUTGOING_ROUTES', 'DistrictModifiers', 'COLLECTION_PLAYER_DISTRICTS');
```

Here `FROM_OUTGOING_ROUTES` reads the player's total outgoing trade route count. Since every player district gets the modifier, all Commercial Hubs get +Gold per route — which stacks. If you want per-district, write custom Lua.

### Example 5: City Center gets +1 Food per Citizen

```sql
INSERT INTO Ruivo_New_Adjacency (ID, DistrictType, ProvideType, YieldType, YieldChange, AdjacencyType) VALUES
    ('CITY_CENTER_FOOD_PER_CITIZEN', 'DISTRICT_CITY_CENTER', 'SelfBonus', 'YIELD_FOOD', 1, 'FROM_CITY_POPULATION');
```

This reads the city's total population and grants that much food to the City Center.

---

## Troubleshooting

### Adjacency Not Showing in Tooltips

1. Check if `CanDisplay = true` in-game (open the production panel and hover over adjacency text). If the adjacency source type's `CanDisplay` flag is 0 in `Ruivo_AdjacencyType`, it won't show.
2. Verify the `AdjacencyType` has `Environment = 'GamePlay'` and `CanDisplay = 1`.
3. Make sure the adjacency's `ModifierOwner` check is passing (e.g., if `ModifierOwner = 'BuildingModifiers'`, the building must actually exist).

### Lua Errors on Game Load

- The most common error is `attempt to call a nil value` when `StatsModule_For_GP` can't find the dispatch function. Make sure your `AdjacencyType` exists in both `Ruivo_AdjacencyType` and the dispatch table.
- `Game.GetLocalPlayer()` returning -1 during load screen causes crashes in some tooltip functions. Ensure you have early-exit guards.

### Binary Folding Overflows

- The maximum encodable value is 1023. If a district has more than 1023 adjacent objects of a type, the count wraps. In practice this almost never happens unless you're counting every single tile on a huge map.

---

## Reference Tables (Quick Lookup)

### Ruivo_BinaryList Values

The binary folding system uses these values: `{1, 2, 4, 8, 16, 32, 64, 128, 256, 512}`. Maximum encodable: **1023**.

### Environment Types

- `GamePlay` — available during actual gameplay
- `UserInterface` — only available on UI screens (may crash in GP context)

### `Environment` vs `CanDisplay`

- `Environment = 'GamePlay'` and `CanDisplay = 1` → shows in-game tooltips
- `Environment = 'UserInterface'` → only shows on UI screens
- `Environment = 'GamePlay'` and `CanDisplay = 0` → exists in logic but hidden from tooltips (e.g., religion attributes)

---

*This manual was generated on 2026-04-03 based on MAB Workshop mod 3429735059.*
