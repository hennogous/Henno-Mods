# Civ6 Modding Skill — Reference Mod Review

Systematic review of patterns in reference mods vs current skill coverage.

## Skill Ambition

**End goal:** The skill should be able to generate a complete, openable ModBuddy project — SQL, XML, Lua, modinfo, `.Art.xml`, folder structure, the lot. The modder opens it in ModBuddy, hooks up their art assets (textures, geometries), cooks, and ships. No hand-wiring boilerplate.

To get there, the review needs to capture:
- ModBuddy project structure conventions (folder layout, `.Art.xml` format, how modinfo maps to project)
- How artdefs, XLPs, BLPs, and textures are referenced from within the project
- What ModBuddy expects vs what can be generated externally
- The full pipeline from "Claude Code generates code" to "modder opens in ModBuddy and adds art"

## Mods to Review

- [x] C&P Domestic Trade Bonuses ✅ 2026-03-23
- [x] C&P Exchange of Ideas ✅ 2026-03-23
- [x] C&P Naval Trade Protection ✅ 2026-03-23
- [x] C&P Religious Pressure from Trade ✅ 2026-03-23
- [x] CH - Modular Adjacency Bonuses Core ✅ 2026-03-23
- [x] CH - Modular Adjacency Bonuses Example ✅ 2026-03-23
- [x] Cities and Towns Mode ✅ 2026-03-24
- [x] City Lights ✅ 2026-03-23
- [x] Detailed Appeal Lens (Envoy Quest List) ✅ 2026-03-23
- [x] EN - Modular Adjacency Bonuses Core ✅ 2026-03-23
- [x] EN - Modular Adjacency Bonuses Example ✅ 2026-03-23
- [~] JNR (in progress — All core UC district mods + Specialists + Wonder_Adjacency reviewed; remaining: Bonus_Resources, Builder_Boosted_Housing, Buildings_Light, City_State_Bonuses, District_Roads/Happiness/Themed_Recruits, Forest_Districts, Fresh_Water_Works, Regional_Range_Progression, Satellites, Specialist_Citizens, Sprawl, Diplomacy, Climate Balance, Civilization Tweaks, Project6T, Wonders, Empire, Improved_Improvements) ✅ partial 2026-03-23
- [x] Latin American Resources ✅ 2026-03-23
- [x] Leugi's Garden District ✅ 2026-03-23
- [x] More Lenses ✅ 2026-03-23
- [x] More Maritime Seaside Sectors ✅ 2026-03-23
- [x] Necropolis ✅ 2026-03-23
- [x] Preserve District Rework ✅ 2026-03-23
- [x] Project Metropolis ✅ 2026-03-24
- [x] Resourceful 2 ✅ 2026-03-23
- [x] Sukritact's Resources ✅ 2026-03-23 (no new patterns vs Latin American Resources)
- [x] Sukritact's Tourism Overview Screen ✅ 2026-03-24
- [x] Wetlands ✅ 2026-03-23

## Review Criteria

For each mod, capture:
1. **Patterns not in skill** — new SQL/XML/Lua techniques, modifier patterns, UI approaches
2. **Patterns that contradict skill** — things the skill says to do differently
3. **Quality patterns** — conventions used by high-quality modders that we should adopt
4. **Art patterns** — any art pipeline techniques not covered
5. **Compatibility patterns** — how mods handle compatibility with other mods, game modes, DLC

## Workshop Mods (additional)
- [x] Sukritact's Oson/Akan (`Steam\workshop\content\289070\2498423012`) ✅ 2026-03-24 — **GamePropertyRanges art variant pattern**
- [x] Sukritact's Oceans (`Steam\workshop\content\289070\2542898147`) ✅ 2026-03-25 — custom game mode, map generation Lua (JFA algorithm), features, resources, M&C integration
- [x] Sukritact's Urban Identities (`Steam\workshop\content\289070\3305272656`) ✅ 2026-03-25 — DBSCAN clustering, SQL triggers for UDQ, plot properties, runtime modifier attachment, custom Kinds/Tables
- [x] Detailed Map Tacks (`Steam\workshop\content\289070\2428969051`) ✅ 2026-03-25 — UI-only, GameEffects introspection API, ReplaceUIScript pattern, PlayerConfigurations data store, 31 new Lua API patterns
- [x] JNR UC — Bonus Resource Improvements (`Steam\workshop\content\289070\2497071692`) ✅ 2026-03-25 — Activator pattern, conditional INSERT from game state, 15 new patterns
- [x] JNR UC — Specialist Progression (`Steam\workshop\content\289070\2482700851`) ✅ 2026-03-25 — Permanent custom table as data driver, Building_CitizenYieldChanges
- [x] BD — Savannah (`Steam\workshop\content\289070\3263126211`) ✅ 2026-03-25 — New feature via SELECT clone, FeatureGenerator replacement, 10 new patterns
- [x] BD — Denser Vegetation (`Steam\workshop\content\289070\2115981252`) ✅ 2026-03-25 — art-only (.dep)
- [x] BD — Mixed Farms (`Steam\workshop\content\289070\3285307999`) ✅ 2026-03-25 — art-only (.dep)
- [x] JNR UC — Hammurabi Tweak (`Steam\workshop\content\289070\2292979207`) ✅ 2026-03-25 — dynamic modifier generation, TraitModifiers, BuildingPrereqs negative filter
- [x] JNR — Community Patch (`Steam\workshop\content\289070\1776020612`) ✅ 2026-03-25 — LeaderPlayable criteria, any="1" OR logic, COLLECTION_OWNER custom types

## Game File Reviews

Base path: `C:\Program Files (x86)\Steam\steamapps\common\Sid Meier's Civilization VI\Base\Assets`

Review key game files against their corresponding skill reference files:

### Schema & Core Tables
- [x] `Gameplay/Data/Schema/01_GameplaySchema.sql` ✅ 2026-03-25 → cross-checked 7 core tables (Buildings, Districts, Improvements, Modifiers, Requirements, Features, Projects, Resources, Adjacency_YieldChanges). Found 64 undocumented columns.
- [x] `Gameplay/Data/GameEffects.xml` ✅ 2026-03-25 → minimal file (just Kinds, Vocabularies, Tags). Real DynamicModifiers are in Modifiers.xml.
- [x] `Gameplay/Data/Modifiers.xml` ✅ 2026-03-25 → 463 DynamicModifier types, 20 CollectionTypes (all in skill), 369 EffectTypes (347 in skill, 22 missing). See findings below.
- [ ] `Gameplay/Data/Requirements.xml` → cross-check `references/collections-effects-requirements.md` and `references/modifier-system.md`

### Buildings & Districts
- [ ] `Gameplay/Data/Buildings.xml` + `Gameplay/Data/Districts.xml` → cross-check `references/sql-patterns.md` building/district sections — verify column coverage, flag defaults

### Civilizations & Leaders (civ creation patterns)
- [ ] `DLC/Australia/Data/Australia.xml` → cross-check `references/xml-data-patterns.md` civ/leader section — verify trait/modifier chain

### Expansions
- [ ] `Expansion1/Assets/Gameplay/Data/Expansion1.modinfo` → cross-check `references/modinfo-reference.md` — ActionCriteria, UI replacement, game mode patterns
- [ ] `Expansion1/Assets/Gameplay/Data/Expansion1_Governors.xml` → add governor system patterns to skill (relevant for CSC Commissioner)
- [ ] `Expansion1/Assets/Gameplay/Data/Schema/Expansion1_Schema.sql` → new tables: loyalty, governors, alliances — for Taxes & Politics reference

### Gathering Storm
- [ ] `Expansion2/Assets/Gameplay/Data/Schema/Expansion2_Schema.sql` → power system tables, climate tables

### Lua / UI
- [ ] `Base/Assets/UI/Gameplay/` — review `WorldInput.lua`, `CityBannerManager.lua` for UI hook patterns → cross-check `references/ui-modding-reference.md` and `references/lua-scripting-reference.md`
- [ ] `Base/Assets/UI/Choosers/` — review `TechCivicChooser.lua` for chooser UI pattern → cross-check `references/ui-modding-reference.md`

### Art Pipeline
- [ ] `Base/Assets/ArtDefs/Landmarks.artdef` — base game artdef structure → cross-check `references/art-pipeline.md`
- [ ] `Base/Assets/ArtDefs/Buildings.artdef` — building artdef structure → cross-check `references/art-pipeline.md`

## Findings

### JNR Urban Complexity — Industry + Suburbs (partial) ✅ 2026-03-23

Reviewed `DE_Industry` (Districts, Buildings, Requirements, Bonuses_Special, MODE_Corporations) and `DE_Suburbs` (PlotProperties Lua). JNR is a massive multi-mod collection — will continue in future heartbeats.

**Patterns not in skill:**
1. **`REQUIREMENT_CITY_HAS_HIGH_ADJACENCY_DISTRICT`** — Checks if a district has adjacency bonus >= threshold. Args: `DistrictType`, `YieldType`, `Amount`. Used for "IZ has 5+ production adjacency" gates. Not in skill.
2. **`REQUIREMENT_CITY_HAS_RESOURCE_TYPE_IMPROVED`** — Checks if a city has a specific resource type improved (harvested and within city bounds). Args: `ResourceType`. Different from `REQUIRES_PLOT_HAS_BONUS` (plot-level). This is city-level. Not in skill.
3. **`REQUIREMENT_PLOT_ADJACENT_DISTRICT_TYPE_MATCHES`** — Checks if a plot is adjacent to a specific district type. Args: `DistrictType`. Used for "adjacent to Aqueduct/Dam/Canal" checks. Not in skill.
4. **`REQUIREMENT_PLOT_HAS_ANY_IMPROVEMENT`** — Boolean check: does this plot have any improvement at all? No args needed. Not in skill.
5. **`CREATE TABLE IF NOT EXISTS` + `DROP TABLE` pattern for bulk generation** — `ProductReference` temp table with 36 alphanumeric values used as a loop to generate 36 copies of each great work type via `SELECT ... FROM ProductReference WHERE Copy > 0`. Table dropped after use. This is the canonical SQL-only loop pattern for generating N copies of something without Lua. Massively relevant to CSC's product/commission system.
6. **`MODIFIER_PLAYER_GRANT_RANDOM_RESOURCE_PRODUCT`** — M&C modifier type: grants a random Product great work of the specified resource type. Args: `ResourceType`. Used in `ProjectCompletionModifiers` — completing the project creates one product. This is how M&C's product system works at the SQL level.
7. **`GreatWork_YieldChanges` table** — Each great work can provide flat yield per turn. `GreatWorkType`, `YieldType`, `YieldChange`. Not in skill.
8. **`GreatWorkModifiers` table** — Each great work can have modifiers that fire while it's placed. Distinct from `BuildingModifiers` — these fire per great work instance. JNR uses this for product bonuses (e.g., Machines products give +1 production to improved tiles). Not in skill.
9. **`GreatWorks_ImprovementType` table** — Links great works to resource types for M&C industry/corporation mechanics. Not in skill.
10. **`ResourceIndustries` table** — M&C table linking resources to industry text descriptions. Not in skill.
11. **`ModifierStrings` table** — `ModifierId`, `Context` ('Summary'), `Text` — provides display text for modifier tooltips. Used for product bonus descriptions. Not in skill.
12. **`Project_ResourceCosts` table** — Projects can cost strategic resources. `ProjectType`, `ResourceType`, `StartProductionCost`. Not in skill.
13. **`EFFECT_ADJUST_ALL_PROJECTS_PRODUCTION`** — Percentage bonus to all project production in a city. Used for Kanban Logistics building. Not in skill.
14. **`EFFECT_ADJUST_CITY_SPY_BONUS`** — Adjusts spy bonus/penalty in a city. Used as a negative effect on Electronics products. Not in skill.
15. **`MODIFIER_SINGLE_CITY_ADJUST_TOURISM_LATE_ERAS`** — Tourism multiplier that only kicks in after a minimum era. Args: `MinimumEra`, `Modifier`. Not in skill.
16. **`MODIFIER_PLAYER_DISTRICT_ADJUST_DISTRICT_AMENITY`** — Adjusts amenity on districts player-wide. Not in skill (distinct from `MODIFIER_ADJUST_AMENITIES_IN_DISTRICT` which is per-district).
17. **`MODIFIER_CITY_DISTRICTS_ADJUST_DISTRICT_AMENITY`** — City-level version of district amenity adjustment. Not in skill.
18. **`MODIFIER_SINGLE_CITY_ADJUST_CITY_APPEAL`** — Adjusts the appeal of plots within a city. Used for pollution penalties. Not in skill.
19. **Tiered `REQUIREMENTSET_TEST_ANY` pattern** — JNR defines requirement sets like `BUILDING_IS_INDUSTRIAL_TIER1_JNR` (any of: Water Mill OR Wind Mill), `TIER2` (Workshop OR Manufactury), etc. Mutually exclusive buildings within a tier are captured as ANY. This is a clean architectural pattern for branching building trees. Very relevant to CSC's branching Quarter design.
20. **`Events.DistrictAddedToMap.Add()`** — Engine event for district placement on the map. Args: `PlayerID, districtID, cityID, iX, iY, districtType, percentComplete`. Used to set plot properties on district placement. Not in skill.
21. **`Map.GetPlot(iX, iY)`** — Gets plot object from coordinates. Basic but not documented in skill's Lua reference.

**Quality patterns:**
- JNR's `BuildingPrereqs` propagation via SELECT is excellent: `INSERT INTO BuildingPrereqs (Building, PrereqBuilding) SELECT Building, 'NEW_BUILDING' FROM BuildingPrereqs WHERE PrereqBuilding='OLD_BUILDING'` — automatically ensures anything that requires the old building also accepts the new alternative. Essential for branching building trees.
- `MutuallyExclusiveBuildings` with `DistrictReplaces` propagation for unique buildings.
- `DistrictReplaces` SELECT on adjacency bonuses, modifiers, and district-level effects — JNR consistently propagates to unique replacements everywhere.
- Temp table + DROP pattern for bulk SQL generation is cleaner than copy-paste of 36 identical rows.

### JNR Urban Complexity — Commerce + Campus + Entertainment + Religion ✅ 2026-03-23

Reviewed `DE_Commerce` (Districts, Buildings, TradeRoutes), `DE_Campus` (Districts), `DE_Entertainment` (Districts, AdjacencyBonusSupport.lua), `DE_Religion` (Buildings).

**Patterns not in skill:**
1. **Custom yield type as adjacency dummy** — `INSERT INTO Yields (YieldType, ...) VALUES ('YIELD_JNR_DUMMY_ADJACENCYTOURISM', ...)` — creates a dummy yield type with `DefaultValue = 0.25` that's used purely for adjacency display/tracking. The Entertainment district gets "tourism adjacency" via this fake yield, which is then converted to actual tourism via a modifier. The dummy yield never appears in the yield bar. This is the canonical workaround for giving a district an adjacency bonus in a yield type the adjacency system doesn't natively support (tourism). Not in skill at all — game-changing pattern.
2. **`Adjacency_YieldChanges` `OtherDistrictAdjacent` column** — Boolean flag: if 1, gives adjacency bonus from *any* other district type (generic). Used for the Entertainment Complex's "+1 tourism from each adjacent district." Distinct from `AdjacentDistrict` which specifies one type. Not in skill.
3. **`Adjacency_YieldChanges` `AdjacentWonder` column** — Boolean: adjacency bonus from adjacent wonders. `AdjacentWonder = 1` means any wonder. Not in skill.
4. **`Adjacency_YieldChanges` `AdjacentNaturalWonder` column** — Same pattern for natural wonders. Not in skill.
5. **`MODIFIER_CITY_DISTRICTS_ADJUST_TOURISM_ADJACENCY_YIELD_MOFIFIER`** (note: typo in game engine "MOFIFIER") — Converts a dummy adjacency yield to tourism at a percentage rate. Args: `Amount` (100 = 1:1), `YieldType` (the dummy yield). This is the second half of the dummy yield → tourism conversion. Not in skill.
6. **`REQUIREMENT_PLOT_ADJACENT_BUILDING_TYPE_MATCHES`** — Checks if a plot is adjacent to a specific building (e.g., Panama Canal wonder). Args: `BuildingType`, `MinRange`, `MaxRange`. Different from district adjacency — this checks buildings specifically. Not in skill.
7. **`EFFECT_ENABLE_SPECIFIC_BUILDING_FAITH_PURCHASE`** — Enables faith purchase of a specific building type in player cities. Args: `BuildingType`. Used for Valletta city-state suzerainty. Not in skill.
8. **`MustPurchase = 1`** on Buildings — Building can only be acquired through purchase (gold/faith), not production. Used for dummy/gate buildings. Not documented in skill.
9. **`EnabledByReligion = 1` filter in SQL queries** — Column on worship buildings. JNR uses it in SELECT to auto-detect all worship buildings: `SELECT BuildingType FROM Buildings WHERE EnabledByReligion=1`. Clever way to handle worship building prereqs without hardcoding each one.
10. **UI replacement for adjacency display** — `AdjacencyBonusSupport.lua` replaces the base game file to extend the yield range from `YIELD_FOOD..YIELD_FAITH` to include `YIELD_JNR_DUMMY_ADJACENCYTOURISM`. Without this UI mod, the dummy yield adjacency wouldn't show icons. This is the complete pattern: create dummy yield → use in adjacency → replace UI to display it → convert to real yield via modifier.
11. **Dynamic adjacency generation for unique districts via `DistrictReplaces` CROSS JOIN** — `SELECT a.CivUniqueDistrictType, b.YieldChangeId FROM DistrictReplaces a, District_Adjacencies b WHERE a.ReplacesDistrictType='DISTRICT_X' AND b.DistrictType='DISTRICT_X'` — automatically copies ALL adjacency bonuses from a base district to its unique replacement in a single query. No per-bonus enumeration. Not in skill.
12. **Dynamic adjacency ID generation via string concatenation** — `CivUniqueDistrictType || '_Tourism_JNR'` in INSERT statements to generate unique adjacency IDs per civ-unique district. Paired with `Description` field using localisation key concatenation: `'LOC_' || CivUniqueDistrictType || '_TOURISM_JNR_DESCRIPTION'`. Auto-generates adjacency definitions for all unique district replacements.
13. **Trade route modifier types:**
    - `MODIFIER_CITY_ADJUST_YIELD_FROM_FOREIGN_TRADE_ROUTES_PASSING_THROUGH` — yield from OTHER players' trade routes passing through your city
    - `MODIFIER_SINGLE_CITY_ADJUST_TRADE_ROUTE_YIELD_FROM_OTHERS` — yield on YOUR routes when they pass through foreign cities
    - `MODIFIER_SINGLE_CITY_ADJUST_TRADE_ROUTE_YIELD_TO_OTHERS` — yield bonus on routes that END at your city from other players
    - `MODIFIER_PLAYER_CITY_TRADE_ROUTE_YIELD_PER_LOCAL_BONUS_RESOURCE_FOR_INTERNATIONAL` — yield per bonus resource at destination for international routes
    - `EFFECT_ADJUST_CITY_TRADE_ROUTE_YIELD_PER_DESTINATION_STRATEGIC_RESOURCE_FOR_DOMESTIC` — yield per strategic resource at destination for domestic routes
    - `EFFECT_ADJUST_TRADE_ROUTE_YIELD_PER_SPECIALTY_DISTRICT_FOR_INTERNATIONAL` — yield per district at destination for international routes
    - `Domestic` arg on `MODIFIER_SINGLE_CITY_ADJUST_TRADE_ROUTE_YIELD_TO_OTHERS` (value 1 = domestic only)
    None of these documented in skill.
14. **`BuildingModifiers` propagation via `BuildingReplaces`** — `SELECT CivUniqueBuildingType, ModifierId FROM BuildingReplaces WHERE ReplacesBuildingType IN (SELECT BuildingType FROM BuildingModifiers WHERE ModifierId='...')` — auto-propagates modifier to all unique building replacements. JNR does this consistently.
15. **`StartingBuildings` cleanup** — `DELETE FROM StartingBuildings WHERE District='DISTRICT_COMMERCIAL_HUB'` — removes default starting buildings for a district. Required when restructuring the building tree (otherwise old defaults conflict with new prereq chains).

**Quality patterns:**
- JNR's adjacency propagation is the gold standard: one CROSS JOIN query copies all adjacencies from base to unique. CSC should adopt this pattern wholesale.
- String concatenation in SQL for dynamic type/modifier/localisation generation — eliminates copy-paste and auto-handles DLC civs.
- The dummy yield → UI replacement → modifier conversion pipeline for tourism adjacency is architecturally brilliant and could be adapted for CSC's custom yield needs.
- `EnabledByReligion` as a dynamic filter instead of hardcoded worship building lists.

### JNR Urban Complexity — Military + Theater + Government ✅ 2026-03-23

Reviewed `DE_Military` (Buildings, Bonuses_XP, Bonuses_Promotions), `DE_Theater` (Buildings), `DE_Government` (Districts).

**Patterns not in skill:**
1. **`Tags` table with `Vocabulary = 'ABILITY_CLASS'`** — Custom tags for unit ability class targeting. Tags are created with a specific vocabulary, then assigned to both abilities (via `TypeTags` on the ability) AND units (via `TypeTags` on the unit type). This creates a many-to-many mapping between unit classes and abilities. Not documented in skill.
2. **`MODIFIER_SINGLE_CITY_GRANT_ABILITY_FOR_TRAINED_UNITS`** — Grants a unit ability to all units trained in that city. Args: `AbilityType`. Combined with `Permanent = 1` on the modifier, the ability persists after the unit leaves. This is the standard pattern for "city building grants permanent bonus to trained units." Not in skill.
3. **`MODIFIER_PLAYER_UNIT_ADJUST_UNIT_EXPERIENCE_MODIFIER`** — Adjusts the XP gain multiplier for a unit. Args: `Amount` (percentage). Used inside `UnitAbilityModifiers` — the ability grants the XP bonus. Not in skill.
4. **`MODIFIER_CITY_TRAINED_UNITS_ADJUST_GRANT_EXPERIENCE`** — Adjusts the starting XP granted to units trained in a city. Args: `Amount` (can be negative = "start with one fewer promotion needed"). Used for the "trained units start with a free promotion" pattern. Not in skill.
5. **`REQUIREMENT_UNIT_PROMOTION_CLASS_MATCHES`** — Checks if a unit belongs to a specific promotion class. Args: `UnitPromotionClass`. Used to filter which unit types receive XP bonuses. Not in skill.
6. **Dynamic TypeTags via PromotionClass** — `INSERT INTO TypeTags (Type, Tag) SELECT UnitType, 'CLASS_XP_BONUS_MELEE_JNR' FROM Units WHERE PromotionClass='PROMOTION_CLASS_MELEE'` — auto-assigns tags to all units of a promotion class. Future-proofs against new units added by DLC/mods. JNR does this for all 8 promotion classes.
7. **`DELETE FROM TypeTags WHERE Type='...' AND Tag<>'...'`** — Selective tag deletion preserving civ-unique tags. Used for Basilikoi Paides and Ordu to remove generic class tags but keep their unique unit tags. Surgical tag management.
8. **`EFFECT_ADD_PLAYER_PROJECT_AVAILABILITY`** — Makes a project available to a player. Args: `ProjectType`. Used with `SubjectRequirementSetId` to conditionally unlock projects. Not in skill.
9. **`MODIFIER_PLAYER_ADJUST_CAPITAL`** — Moves the player's capital to the city where a project is completed. Args: `ProjectType`. Combined with `EFFECT_ADD_PLAYER_PROJECT_AVAILABILITY` to create a "Move Capital" project that only appears when conditions are met. Not in skill.
10. **`MODIFIER_PLAYER_ADD_CULTURE_BOMB_TRIGGER`** — Triggers a culture bomb (claiming adjacent tiles) when a specific district is placed. Args: `DistrictType`. Not in skill.
11. **`REQUIREMENT_PLOT_IS_OWNER_CAPITAL_CONTINENT`** — Checks if a plot is NOT on the player's capital continent. Used to gate "Move Capital" — only available for off-continent Government Plaza cities. Not in skill.
12. **`Projects_XP2` table: `UnlocksFromEffect` column** — When 1, the project is hidden by default and only appears when unlocked via `EFFECT_ADD_PLAYER_PROJECT_AVAILABILITY`. `MaxSimultaneousInstances` limits concurrent runs. Not in skill.
13. **`CostProgressionModel = 'COST_PROGRESSION_GAME_PROGRESS'`** on Projects — Same era-based cost scaling used for districts, applied to projects. `CostProgressionParam1 = 750` controls the scaling rate. Not documented for projects in skill.
14. **`BuildingReplaces` with multiple replacements** — A unique building can replace multiple base buildings: `('BUILDING_MARAE', 'BUILDING_JNR_ASSEMBLY'), ('BUILDING_MARAE', 'BUILDING_AMPHITHEATER')`. This makes the unique building available from EITHER prereq path. Not documented that multi-replace is valid.
15. **`Entertainment` column on Buildings** — Provides amenities. JNR adds `Entertainment = 1` to Amphitheater, Cabinet, Opera, Media Center. Distinct from the district's base amenity. Not clearly documented in skill.
16. **`MaxPlayerInstances` on Projects** — Limits how many times a player can complete a project total (not simultaneously). `MaxPlayerInstances = 1` = one-shot project. Not in skill.

**Quality patterns:**
- Military building tree: 3-way branch at tier 1 (Barracks/Stable/Target Range), 3-way at tier 2 (Armory/Cavalier/Depot), 3-way at tier 3 (Military Academy/Arsenal/Prison). Each branch serves different unit classes. Same structural pattern CSC uses for Quarter buildings.
- `EXISTS (SELECT * FROM Buildings WHERE BuildingType='...')` guard on DLC-dependent inserts — ensures the INSERT only runs if the DLC building exists.
- Theater tree: Museum of Art and Museum of Artifacts separated from the main building chain (`DELETE FROM BuildingPrereqs WHERE Building='BUILDING_MUSEUM_ART'`), made cheaper standalone buildings. Interesting design for "choose your specialization" without the full mutual exclusion pattern.

### JNR Urban Complexity — Aqueduct + Worship + Power ✅ 2026-03-23

Reviewed `DE_Aqueduct` (Districts, Buildings), `DE_Worship` (Buildings), `Power` (Tier_Table, Power_Load, Power_Yields).

**Patterns not in skill:**
1. **Custom config table as data-driven framework** — `CREATE TABLE IF NOT EXISTS Buildings_JNRUCPPC_PowerTierYields (BuildingType TEXT PRIMARY KEY, Tier INTEGER, Yield TEXT, GPP TEXT, IsFactory BOOLEAN)` — JNR creates a config table, populates it with all tier 2/3 buildings and their yield types, then uses it in all subsequent INSERT/UPDATE/SELECT statements. Every power modifier, yield bonus, and requirement is generated from this one table. Same pattern as Ruivo's `Ruivo_New_Adjacency` but for a completely different purpose. This is the gold standard for data-driven mod architecture.
2. **`MODIFIER_PLAYER_CITIES_ADJUST_YIELD_FROM_POWERED_BUILDINGS`** — Adjusts yield from powered buildings across all player cities. Args: `YieldType`, `Amount`. Used via `TraitModifiers` with era-gated `SubjectRequirementSetId` to layer additional yields as techs are researched. Not in skill.
3. **`MODIFIER_BUILDING_YIELD_CHANGE`** — Directly changes yield on a specific building. Args: `BuildingType`, `YieldType`, `Amount`. Combined with `PLAYER_HAS_ELECTRICITY_IN_POWERED_CITY_JNR` requirement set (tech researched AND city powered). This is distinct from `Building_YieldChanges` (static) — this modifier is conditional. Not in skill.
4. **`MODIFIER_SINGLE_CITY_ADJUST_REQUIRED_POWER`** — Increases power demand for a city. Args: `Amount`. Gated by tech requirements to ramp up power needs as the game progresses. Not in skill.
5. **`MODIFIER_PLAYER_CITIES_ADJUST_FREE_POWER`** — Grants free power to cities. Args: `Amount`, `SourceType` (`FREE_POWER_SOURCE_MISC`). Used to give AI players free power per era so they don't fall behind on powered building bonuses. `MINOR_CIV_DEFAULT_TRAIT` applies it to city-states too.
6. **`REQUIRES_PLAYER_IS_AI`** requirement — Built-in requirement checking if the player is AI-controlled. Used in combination with era requirements to create AI-only power subsidies. Not in skill.
7. **`MODIFIER_PLAYER_DISTRICT_ADJUST_YIELD_CHANGE`** — Adjusts yield on a district type for all of a player's cities. Args: `YieldType`, `Amount`. Used with `SubjectRequirementSetId` for conditional district yield. Not in skill.
8. **`District_TradeRouteYields` columns** — `YieldChangeAsDomesticDestination` and `YieldChangeAsInternationalDestination` — separate domestic vs international trade route yield bonuses from a district. Not in skill.
9. **`District.Maintenance` column** — Districts can have maintenance costs. JNR adds maintenance to Aqueducts. Not documented in skill.
10. **Cross-district building prereqs** — Aqueduct buildings require buildings from OTHER districts (Granary from City Center, Library from Campus, Workshop from IZ, etc.). `BuildingPrereqs` can reference buildings from any district, not just the building's own. The skill implies prereqs are within the same district chain.
11. **`EnabledByReligion` column** — Worship buildings use this flag. JNR creates 9 new worship buildings with `EnabledByReligion=1`, which means they only appear when a religion has selected them as a belief. Also used to disable other mod's worship buildings: `UPDATE Buildings SET InternalOnly=1, EnabledByReligion=0`.
12. **Dynamic modifier ID generation from config table** — `'JNR_POWER_' || Yield || '_ELECTRICITY_' || BuildingType` in INSERT statements generates unique modifier IDs per building per yield type. Combined with the config table, this produces dozens of modifiers from a single query template.

**Quality patterns:**
- The Power module's config table approach means adding a new building to the power system requires ONE row in `Buildings_JNRUCPPC_PowerTierYields`. All modifiers, yields, requirements, and power loads are auto-generated. Zero copy-paste. This is what CSC should aspire to.
- `MINOR_CIV_DEFAULT_TRAIT` used alongside `TRAIT_LEADER_MAJOR_CIV` to ensure city-states also get power bonuses — easy to miss this, and without it city-states would be permanently underpowered.
- Cross-district prereqs in Aqueduct create an interesting "infrastructure hub" pattern where the Aqueduct building you can construct depends on what other districts you've built.

### JNR Urban Complexity — Specialists + Wonder_Adjacency ✅ 2026-03-23

Reviewed `Specialists` (Slots, Yields, Buildings, Pedia), `Wonder_Adjacency` (Table, Bonuses, Text).

**Patterns not in skill:**
1. **`Building_CitizenYieldChanges` table** — Buildings provide yields to worked citizen slots. Distinct from `Building_YieldChanges` (base building yield) and `District_CitizenYieldChanges` (district citizen yield). Used to make specific buildings give extra science/culture/gold when a citizen is assigned to the district. Not documented in skill.
2. **`DELETE FROM District_CitizenYieldChanges WHERE DistrictType IS NOT NULL`** — Full table wipe before re-inserting. Aggressive but clean: ensures no base game values interfere with the mod's design. `IS NOT NULL` guard prevents deleting rows where DistrictType is null (safety). Pattern for total-replacement mods.
3. **`BuildingReplaces` propagation for citizen yields** — `INSERT OR REPLACE INTO Building_CitizenYieldChanges SELECT CivUniqueBuildingType, YieldType, YieldChange FROM BuildingReplaces, Building_CitizenYieldChanges WHERE ReplacesBuildingType = BuildingType` — auto-copies citizen yields to all unique building replacements. Same pattern as adjacency propagation.
4. **`DistrictReplaces` propagation for citizen yields** — Same pattern applied to `District_CitizenYieldChanges`. One-liner copies all base district citizen yields to unique districts.
5. **`REQUIREMENT_PLOT_ADJACENT_TO_OWNER`** — Checks if the subject plot is adjacent to the owner (modifier source). Used for wonder adjacency bonuses — the wonder gives a bonus to its adjacent district. Not in skill.
6. **`REQUIREMENT_DISTRICT_TYPE_MATCHES`** — Checks if the subject is a specific district type. Args: `DistrictType`. Combined with `ADJACENT_TO_OWNER` in a requirement set to create "bonus to adjacent [specific district] from this wonder." Not in skill.
7. **`SUBSTR(DistrictType, 10)`** — SQL string slicing to strip `DISTRICT_` prefix (9 chars + 1 for 1-based index) for generating readable modifier/requirement IDs. `DISTRICT_CAMPUS` → `CAMPUS`. Used throughout for dynamic ID generation. Clever SQL technique not in skill.
8. **`IsWonder = 1` column on Buildings** — Boolean for wonder identification. JNR seeds the config table with `SELECT BuildingType, AdjacentDistrict FROM Buildings WHERE IsWonder=1` to auto-discover all wonders, then overrides specific entries. Not documented in skill.
9. **Config table seeded from game data then overridden** — `Buildings_JNRUC_WonderAdjacencies` is first populated with ALL wonders via `SELECT ... WHERE IsWonder=1`, then specific entries are updated with `UPDATE ... WHERE BuildingType='BUILDING_X'`. This "auto-populate then hand-tune" pattern is excellent for mods that want a baseline from game data but need specific overrides.
10. **`Districts.CitizenSlots` column** — Districts themselves can have citizen slots (not just buildings). JNR adds citizen slots to Aerodrome district directly. Not documented in skill.

**Quality patterns:**
- Wonder_Adjacency uses the same config table → auto-generate pattern as Power, but seeds from game data instead of hardcoded values. Every requirement, modifier, and argument is generated from the config table. Adding wonder adjacency support for a new modded wonder = adding one UPDATE to the config table.
- `INSERT OR REPLACE` used throughout Specialists instead of `INSERT OR IGNORE` — overwrites existing values cleanly rather than skipping them.
- `SELECT FROM Districts WHERE BuildingType='...'` — DLC-safe insert: the query returns nothing if the DLC building doesn't exist, so the INSERT does nothing.

### Latin American Resources ✅ 2026-03-23

Standard resource mod with M&C Corporations mode compatibility. Leugi + p0kiehl collab.

**Patterns not in skill:**
1. **`Resource_ValidTerrains` table** — Specifies which terrain types a resource can appear on. `ResourceType`, `TerrainType`. Not documented in skill.
2. **`Resource_ValidFeatures` table** — Specifies which feature types a resource can appear on. `ResourceType`, `FeatureType`. Combined with valid terrains = full placement rules. Not in skill.
3. **`Resource_Harvests` table** — Defines what you get when harvesting (removing) a resource. `ResourceType`, `YieldType`, `Amount`, `PrereqTech`. Not in skill.
4. **`Resource_YieldChanges` table** — Base yields a resource provides on its tile. `ResourceType`, `YieldType`, `YieldChange`. Not in skill.
5. **`Improvement_ValidResources` table** — Links resources to improvements that can harvest them. `ImprovementType`, `ResourceType`, `MustRemoveFeature` (0/1). Not in skill.
6. **`Resources.RequiresRiver` column** — Resource can only spawn on river tiles. Capybaras and Yerba Mate use this.
7. **`Resources.Frequency` column** — Controls spawn frequency on map generation. Higher = more common. Bonus resources use 6, luxuries use 2.
8. **`REQUIREMENT_PLOT_RESOURCE_TYPE_MATCHES`** — Checks if a plot has a specific resource type. Args: `ResourceType`. Distinct from `REQUIRES_PLOT_HAS_BONUS` (resource class check). Not in skill.
9. **`GreatWorks.Tourism` column** — Great works (including products) can have base tourism. Products here have `Tourism = 1`. Not documented in skill.
10. **`MODIFIER_SINGLE_CITY_ADJUST_CITY_HOUSING_FROM_GREAT_WORKS`** — Adjusts housing from great works in a city. Args: `Amount`. M&C product bonus. Not in skill.
11. **`MODIFIER_SINGLE_CITY_ADJUST_UNIT_PRODUCTION`** — Adjusts production for specific unit types. Args: `YieldType` (comma-separated unit types!), `Amount`. Note: the `YieldType` arg actually takes unit type names, not yield types. Not in skill.
12. **`MODIFIER_SINGLE_CITY_ADJUST_MILITARY_UNITS_PRODUCTION`** — Military unit production bonus. Args: `StartEra`, `EndEra`, `Amount`. Era-gated variant. Not in skill.

**Contrast with JNR:** Latin American Resources creates products the old-fashioned way — 5 hardcoded copies per resource. JNR's temp table loop (`ProductReference` with 36 entries) is much cleaner. CSC should use the JNR approach.

### Leugi's Garden District ✅ 2026-03-23

Small custom district mod with an innovative "ongoing project effect" pattern.

**Patterns not in skill:**
1. **Ongoing project modifier via plot properties** — The key pattern: Lua sets a plot property to 1 when a project is being produced, and 0 when it stops. SQL uses `REQUIREMENT_PLOT_PROPERTY_MATCHES` to gate a modifier that only fires while the project is in production. Three events drive this: `Events.CityProductionChanged`, `Events.CityProjectCompleted`, `Events.CityProductionUpdated`. This is how you create "while producing this project, gain X" effects — no native support in SQL, so the Lua bridge is required.
2. **`MODIFIER_ALL_CITIES_ATTACH_MODIFIER`** — Game-level modifier (via `GameModifiers` table) that attaches a child modifier to all cities matching a requirement set. Different from `MODIFIER_PLAYER_CITIES_ATTACH_MODIFIER` (player-scoped) — this one is global. Not in skill.
3. **`Project_GreatPersonPoints` table** — Projects can grant GP points on completion. `ProjectType`, `GreatPersonClassType`, `Points`, `PointProgressionModel`, `PointProgressionParam1`. Scaled by game progress. Not documented in skill.
4. **`Events.CityProductionChanged`** — Fires when a city's production queue changes. Args: `playerID, cityID, eProductionType, eProductionObject`. Not in skill.
5. **`Events.CityProjectCompleted`** — Fires when a project finishes. Same args. Not in skill.
6. **`Events.CityProductionUpdated`** — Fires each turn when production progresses. Same args. Not in skill.
7. **`pCity:GetBuildQueue():CurrentlyBuilding()`** — Returns the type string of what's currently being produced. Used to check if the project is active. Not in skill.

**CSC relevance:** The ongoing project modifier pattern could be useful for CSC's Commissioner system (if the design uses projects for Quarter upgrades/commissions) — "while commissioning, the Quarter provides bonus X."

### Necropolis + More Maritime Seaside Sectors ✅ 2026-03-23

**Necropolis** — p0kiehl's civ-unique district + buildings for Egypt. Full SELECT-based district creation from base district.

**Patterns not in skill:**
1. **`INSERT INTO Districts ... SELECT ... FROM Districts WHERE DistrictType='DISTRICT_X'`** — Creates a new district by copying ALL columns from an existing one, overriding only the changed fields (name, description, cost, trait). This is the canonical pattern for civ-unique district creation. Far safer than specifying all 40+ columns manually — picks up any columns added by DLC/patches. Not in skill.
2. **Same pattern for Buildings** — `INSERT INTO Buildings ... SELECT ... FROM Buildings WHERE BuildingType='BUILDING_X'` — copies the full column set from a base building with specific overrides. Used for Obelisk (from Shrine), Nubian Shrine (from Temple), Temple of Amun (from Dar-e Mehr).
3. **`DELETE FROM CivilizationTraits WHERE TraitType='...' AND CivilizationType='...'`** — Removes an existing civ trait (Sphinx) before adding the replacement (Necropolis). Clean pattern for replacing a civ's unique.
4. **`Traits` + `CivilizationTraits` tables for civ-unique binding** — Each unique district/building gets its own trait type, then that trait is assigned to the civilization. Multiple traits per civ is valid (one per unique).
5. **`District_TradeRouteYields` propagation via SELECT** — Copies trade route yields from base district to unique replacement.
6. **`Building_GreatWorks` table** — Buildings provide great work slots. `BuildingType`, `GreatWorkSlotType`, `NumSlots`. Propagated from base building via SELECT.
7. **`Unit_BuildingPrereqs` table** — Religious units (Missionary, Apostle, Inquisitor, Guru, Warrior Monk) require specific buildings. `Unit`, `PrereqBuilding`, `NumSupported` (-1 = unlimited). Must add these for any building that replaces Shrine/Temple. Not in skill.
8. **`MomentIllustrations` table** — Timeline moment artwork for unique buildings/districts. `MomentIllustrationType`, `MomentDataType`, `GameDataType`, `Texture`. Cosmetic but polished mods include these.
9. **`MODIFIER_SINGLE_CITY_ADJUST_GREAT_PERSON_POINT`** — Single GP point adjustment in a city. Args: `GreatPersonClassType`, `Amount`. Gated by tech requirement. Not in skill (skill has the player-wide version but not city-specific).
10. **`Adjacency_YieldChanges.AdjacentRiver` column** — Boolean for river adjacency bonus. Necropolis gets +2 faith from river. Not in skill.
11. **`Adjacency_YieldChanges.AdjacentSeaResource` column** — Boolean for adjacent sea resource bonus. Waterfront uses this. Not in skill.
12. **`COST_PROGRESSION_NUM_UNDER_AVG_PLUS_TECH`** — Alternative cost progression model: cost scales with tech count below average. Used for Waterfront district. Distinct from `COST_PROGRESSION_GAME_PROGRESS`. Not in skill.
13. **`Districts.FreeEmbark` column** — District grants embarking ability to trained units. Waterfront uses this. Not in skill.

**Quality patterns:**
- SELECT-based district/building creation is vastly superior to manual column enumeration. If Firaxis adds a new column in a patch, the SELECT picks it up automatically. Manual enumeration breaks.
- `MutuallyExclusiveBuildings` generated via `SELECT FROM Buildings WHERE EnabledByReligion=1` — auto-excludes all worship buildings from the civ-unique replacements without hardcoding each one.
- Necropolis shows the complete "replace an existing civ unique" workflow: delete old trait → create new types → create trait → assign to civ → create district/buildings via SELECT → set up adjacencies → add building prereqs → add unit prereqs → add moments.

### Preserve District Rework + Resourceful 2 + Sukritact's Resources + Wetlands ✅ 2026-03-23

Batch of smaller mods. Preserve and Wetlands had the most new content.

**Patterns not in skill:**
1. **`Adjacent_AppealYieldChanges` table** — Buildings yield bonuses to adjacent tiles based on appeal tier. Columns: `BuildingType`, `Description`, `MinimumValue` (appeal threshold), `YieldType`, `YieldChange`, `Unimproved` (0/1). Preserve uses this for Grove/Sanctuary. Not in skill.
2. **`MODIFIER_GAME_ADJUST_PLOT_YIELD`** — Game-wide modifier that adjusts yield on plots matching a requirement set. Registered via `GameModifiers` (always-active). Used for the Preserve water tile bonus — can't use `Adjacent_AppealYieldChanges` for water tiles, so modifiers fill the gap. Not in skill.
3. **`REQUIRES_PLOT_HAS_COAST`** — Built-in requirement checking if a plot is a coast tile. No args needed. Not in skill.
4. **`Districts.NoAdjacentCity` column** — When 1, district cannot be placed adjacent to city center. `Districts.ZOC` — zone of control flag. Both modifiable via UPDATE. Not in skill.
5. **`Features` table for custom features** — Full feature creation: `FeatureType`, `RequiresRiver`, `DefenseModifier`, `MovementChange`, `SightThroughModifier`, `Appeal`, `AntiquityPriority`, `Removable`, `RemoveTech`, `Forest` (boolean, affects forest-related mechanics). Not in skill.
6. **`Features_XP2` table** — Expansion columns: `ValidWonderPlacement`, `ValidDistrictPlacement`, `ValidForReplacement`. Controls whether wonders/districts can be placed on the feature. Not in skill.
7. **`Feature_ValidTerrains` table** — Which terrain types a feature can spawn on. Same pattern as `Resource_ValidTerrains`.
8. **`Feature_Floodplains` table** — Registers a feature as a floodplain type (for flood mechanics in GS). Just `FeatureType`. Not in skill.
9. **`Feature_YieldChanges` table** — Base yields provided by a feature on its tile. Same pattern as `Resource_YieldChanges`.
10. **Map generation Lua (`FeatureGenerator.lua`)** — Wetlands includes a replacement for the feature generator that handles placement of custom features during map creation. Uses `AddFeaturesFromContinents` and custom placement logic. Not covered in skill at all — map generation scripting is a separate domain.

**No new patterns from:** Resourceful 2 (same resource tables as Latin American), Sukritact's Resources (same pattern, different resources).

---

**CSC relevance:** HIGH. The M&C product system (great works as products, projects creating them, `GreatWorkModifiers` for per-product bonuses) is exactly what CSC's specialty commissions could use. The temp table loop pattern is relevant for generating multiple product variants per Quarter. The tiered ANY requirement set pattern maps directly to CSC's branching building structure.

---

### EN - Modular Adjacency Bonuses Core + Example ✅ COMPLETE

EN is the English-translated version of the CH framework — same code, English comments. No new SQL/Lua patterns vs CH. The EN Example (`Another Example.sql`) adds several additional `AdjacencyType` values and one new effect type not covered in CH:

**Addenda to CH findings:**
1. **`EFFECT_ADJUST_CITY_YIELD_MODIFIER`** — Percentage modifier on a specific yield type for an entire city. Collection: `COLLECTION_OWNER_CITY`. Args: `YieldType`, `Amount` (percentage, e.g., 50 = +50%). Used in the EN Example for the "50% of faith converts to production" pattern. The CH mod registered this as `MODIFIER_OWNER_CITY_ADJUST_CITY_YIELD_MODIFIER_RUIVO` (since it requires Maya DLC). This is a general-purpose city-wide yield % multiplier.
2. **`MODIFIER_PLAYER_CITIES_ADJUST_GREEN_ENERGY_TOURISM_MODIFIER`** — Adjusts the tourism multiplier granted by clean/renewable power (GS). Args: `Amount`. Example: `Amount = 100` doubles the green energy tourism bonus. Not in skill.
3. **`AdjacencyType` vocabulary in the framework** (confirmed from EN examples): `FROM_RIVER_CROSSING`, `FROM_ADJACENT_WORKER`, `FROM_ADJACENT_LAKE`, `FROM_CITY_SURPLUS_FOOD`, `FROM_ADJACENT_ROUTE`, `FROM_ADJACENT_UNIT`, `FROM_CLIFF`, `FROM_CITY_POPULATION`, `FROM_CITY_TOTAL_HOUSING`, `FROM_CITY_SURPLUS_HOUSING`, `FROM_OUTGOING_ROUTES`, `FROM_CITY_SURPLUS_AMENITIES`, `FROM_SELF_WORKER`, `FROM_ADJACENT_DISTRICT`, `FROM_CITY_DISTRICTS_NUM`, `FROM_LATITUDE`, `FROM_POLE`, `FROM_SLOT_ECONOMIC/MILITARY/DIPLOMATIC/WILDCARD/GREAT_PERSON`, `FROM_RELIGION_FOREIGN_FOLLOWERS`, `FROM_RELIGION_TOTAL_FOLLOWERS`, `FROM_RELIGION_DOMESTIC_FOLLOWERS`, `FROM_RELIGION_FOREIGN_CITIES`, `FROM_RELIGION_FAITH_YIELD`, `FROM_RELIGION_CITIES_WITH_WONDER`, `FROM_RELIGION_BELIEFS_COUNT`, `FROM_SELF_YIELD_FAITH`, `FROM_CITY_SURPLUS_AMENITIES_OVER_HIGHEST_LEVEL_HAPPINESS`, `FROM_UI_ADJACENT_YIELD_*`. This is the most complete list of Ruivo adjacency type identifiers documented anywhere.

---

### Envoy Quest List (mislabelled as "Detailed Appeal Lens") ✅ COMPLETE

Pure UI mod — no SQL gameplay changes. Key patterns:

**Patterns not in skill:**
1. **`AffectsSavedGames = 0`** — Property declaring the mod does not affect saved games (safe to add/remove mid-playthrough). Not documented in skill modinfo section.
2. **`<File priority="1">` in `UpdateText`** — Priority on individual files within `UpdateText` actions. Higher priority = loaded first. Used when you have a primary translation file and a community-translation fallback. Not in skill (skill only covers priority on actions, not on individual file elements within an action).
3. **Multiple `<File>` entries in a single `AddUserInterfaces` action** — One `AddUserInterfaces` block can load multiple XML files (each implying its paired `.lua`). Not clearly stated in skill.
4. **`ImportFiles` for raw DDS textures** — `<ImportFiles>` used to register `.dds` texture files directly (not via BLP cook pipeline). For UI-only textures that don't need the 3D asset pipeline. Not documented in skill.
5. **`<Stability>Beta</Stability>` metadata field** — Cosmetic mod status indicator. No functional effect.

---

### More Lenses ✅ COMPLETE

**Patterns not in skill:**
1. **`<GameCoreInUse>` criteria** — `<Criteria id="expansion1"><GameCoreInUse>expansion1</GameCoreInUse></Criteria>` — detects if a specific game core (expansion) is loaded. Different from `<ModInUse>` (checks a mod UUID) — `GameCoreInUse` checks the expansion core itself. Used to load the correct expansion-specific UI replacement. Not in skill.
2. **`criteria="..."` inline attribute on action elements** — Actions can have a `criteria` attribute directly: `<ImportFiles id="..." criteria="expansion1">`. This is an alternative to `<DoNothing>/<Exclude>` for conditional loading. Simpler for single-action conditionals. Not documented in skill.
3. **`<Items>` wrapper in actions** — `<UpdateDatabase>`, `<ImportFiles>`, `<AddUserInterfaces>` can wrap files in `<Items>` instead of directly as `<File>` children. Functionally equivalent but different XML structure. Some modders use `<Items>`, others use bare `<File>`. Both are valid.
4. **`LocalizedText` action type** — Different from `UpdateText`. `<LocalizedText>` loads `.xml` text files using the Civ6 localization system directly. May have different behavior for language-specific loading vs `UpdateText`. Not documented in skill which only covers `UpdateText`.
5. **`ImportFiles` for Lua scripts (not just data)** — `ImportFiles` with `<Context>InGame</Context>` loads Lua scripts as context-specific imports. Used for lens support files that need to be available as `include()` targets. Distinct from `AddGameplayScripts` (which registers scripts with the gameplay context). Not documented.
6. **`ImportFiles` for replacing base game UI files** — Listing `Base/Assets/UI/minimappanel.lua` and `Base/Assets/UI/Panels/modallenspanel.lua` in `ImportFiles` replaces those base game files with the mod versions. This is the canonical pattern for UI file replacement — not using artdefs or any special XML, just `ImportFiles` with the full base-game-relative path. Skill mentions UI replacement is possible but doesn't show the actual path/mechanism.
7. **Expansion-specific UI replacement via `DLC/Expansion1/UI/Replacements/minimappanel.xml`** — Expansions have their own UI replacements in `DLC/Expansion1/UI/Replacements/`. A mod replacing the minimap panel needs separate replacements for base game, XP1, and XP2. Each is loaded conditionally via `GameCoreInUse` criteria.
8. **`Colors` table** — `INSERT INTO Colors (Type, Red, Green, Blue, Alpha) VALUES (...)` — registers named RGBA colors usable from Lua via `UI.GetColorValue()` or in XML stylesheets. Values are 0.0–1.0 floats. Alpha appears to have no visible effect (comment in file). Not documented in skill.
9. **Custom in-game settings table pattern** — `CREATE TABLE ML_Settings (Setting TEXT, Value INTEGER, PRIMARY KEY(Setting))` + `INSERT OR REPLACE INTO ML_Settings VALUES (...)` — a persistent per-game settings store using a custom SQLite table. Settings panel Lua reads/writes this table via `DB.ConfigurationQuery()` or similar. This is the standard pattern for mods with user-configurable in-game options. Not in skill.
10. **`include("Civ6Common.lua")` and `include("SupportFunctions")`** — Standard shared Lua libraries. `Civ6Common.lua` provides `GetCivilizationUniqueTraits`, `GetLeaderUniqueTraits`. `SupportFunctions` provides `Split`. These are base game UI includes, not gameplay context. Not documented in skill.
11. **`GlobalParameters.CITY_MIN_RANGE`** — Accessing game global parameters from Lua via `GlobalParameters` table. Returns the numeric value of any `GlobalParameters` entry. Not in skill.
12. **`Map.GetPlotDistance(x1, y1, x2, y2)`** — Hex grid distance between two plots. Basic map utility. Not in skill's Lua API coverage.
13. **`pPlot:GetWonderType()`** — Gets wonder type on a plot, returns -1 if none. Not in skill.
14. **`GameInfo.Features[featureType].NaturalWonder`** — Boolean property on feature info checking if it's a natural wonder. Not in skill.
15. **`pPlayer:GetTechs():HasTech(tech.Index)`** — Check if player has researched a tech. Takes the tech's `Index` (integer), not the type string. Not in skill.
16. **`:Members()` iterator on game collections** — `localPlayerCities:Members()` returns an iterable. Standard pattern for iterating all cities, units, etc. Not documented in skill.

**Quality patterns:**
- `ImportFiles` for core Lua libraries (LensSupport, BuilderLens_Support) separate from individual lens scripts — clean separation between framework and implementations.
- Separate `LoadOrder` values for schema (8), data (9), UI (10) to guarantee load order for dependent tables.
- All base UI files listed in lowercase in `<Files>` — comment says this is for Linux/macOS file system compatibility (case-sensitive).

---

### CH - Modular Adjacency Bonuses Core + Example ✅ COMPLETE

This is the most architecturally sophisticated mod in the set — a full data-driven framework for adjacency bonuses using custom SQLite tables, binary encoding, and Lua property injection. Reviewed as one unit.

**Patterns not in skill:**
1. **`CREATE TABLE` in mod SQL** — Mods can create their own SQLite tables at runtime. Here `Ruivo_New_Adjacency` and `Ruivo_BinaryList` are custom tables that act as configuration for a code-generation framework. These tables exist only during the active game session. Not documented in skill at all.
2. **Binary-encoded property pattern for arbitrary integer values** — The core technique: since `REQUIREMENT_PLOT_PROPERTY_MATCHES` only checks if a property equals/exceeds a value (not arbitrary arithmetic), Ruivo encodes any integer N as a set of 10 binary-weighted properties (`ID_1`, `ID_2`, `ID_4`, `ID_8`... `ID_512`). Each bit-property is either 0 or 1. Each has a corresponding modifier that fires only when that bit is 1. Sum of all firing modifiers = the original value N. Lua does the decomposition, SQL does the matching. This is the canonical pattern for "modifier scales with count of adjacent objects" — completely absent from skill.
3. **`EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE`** — Adjusts the base yield of a district (not the adjacency bonus, but the flat base). Applied via `COLLECTION_PLAYER_DISTRICTS`. Distinct from adjacency yield changes. Not in skill.
4. **`EFFECT_ADJUST_DISTRICT_YIELD_MODIFIER`** — Applies a % modifier to a district's adjacency yield (e.g., +100% doubles all adjacency bonuses). Collection: `COLLECTION_OWNER`. Not in skill.
5. **`EFFECT_ADJUST_DISTRICT_TOURISM_CHANGE`** — Adjusts tourism output of a specific district. Collection: `COLLECTION_OWNER`. Not in skill.
6. **`EFFECT_ADJUST_DISTRICT_HOUSING`** — Adjusts housing provided by a district. Collection: `COLLECTION_OWNER`. Not in skill.
7. **`EFFECT_ADJUST_CITY_IDENTITY_PER_TURN`** — Adjusts loyalty per turn (Rise & Fall). Collection: `COLLECTION_OWNER_CITY`. Inserted with `WHERE EXISTS (SELECT 1 FROM Types WHERE Type = 'EFFECT_...')` — DLC-safe conditional insert. Not in skill.
8. **`EFFECT_ADJUST_MODIFIED_FREE_POWER_IN_CITY`** — Adjusts clean power in a city (Gathering Storm). Similarly DLC-safe inserted. Not in skill.
9. **`MODIFIER_PLAYER_ADJUST_INFLUENCE_POINTS_PER_TURN`** — Adjusts Diplomatic Influence per turn (NFP/NF_3). Not in skill.
10. **`MODIFIER_PLAYER_ADJUST_EXTRA_FAVOR_PER_TURN`** — Adjusts World Congress Favor per turn (GS). Not in skill.
11. **`MODIFIER_PLAYER_ADJUST_GREAT_PERSON_POINTS`** — Direct Great Person point adjustment (not per-district). Args: `GreatPersonClassType`, `Amount`. Not in skill.
12. **`MODIFIER_PLAYER_ADJUST_GREAT_PERSON_POINTS_PERCENT`** — Percentage modifier on Great Person points. Not in skill.
13. **`EFFECT_ADJUST_SPACE_RACE_PROJECTS_PRODUCTION`** — Adjusts production toward space race projects. Collection: `COLLECTION_OWNER_CITY`. Not in skill.
14. **`DLC-safe conditional DynamicModifiers`** — `INSERT INTO DynamicModifiers ... SELECT ... WHERE EXISTS (SELECT 1 FROM Types WHERE Type = 'EFFECT_...')` — only creates the custom modifier type if the required expansion effect type exists. This is the canonical pattern for expansion-dependent custom modifier types.
15. **`DistrictReplaces` table** — Joins `DistrictReplaces` to propagate adjacency bonuses from vanilla districts to all civ-unique replacement districts. `DistrictReplaces (ReplacesDistrictType, CivUniqueDistrictType)`. Skill doesn't document this table at all. Essential for any mod touching districts that have civ-unique replacements.
16. **`SELECT-driven INSERT INTO Ruivo_New_Adjacency FROM GreatPersonClasses`** — Dynamically generates one adjacency bonus row per Great Person class using `SELECT ... FROM GreatPersonClasses`. Completely generalised — automatically handles new Great Person classes from any expansion.
17. **`INSERT OR IGNORE INTO`** — Safe idempotent insert (no error if row exists). Useful when combining compatibility patches with base content that may already have been inserted. Not documented in skill.
18. **`RequirementSets` with `MinDistance = N` AND `MaxDistance = N` (same value)** — For ring-specific targeting: only tiles at exactly distance N from the owner. Standard usage is `MinDistance = 0`, `MaxDistance = N` for "within N". The exact-ring variant is novel.
19. **`REQUIREMENT_REQUIREMENTSET_IS_MET` as a requirement** — A requirement whose `RequirementType` is itself `REQUIREMENT_REQUIREMENTSET_IS_MET`, pointing to another `RequirementSetId`. This enables nested requirement sets / composition. Used for "coast or ocean" combined condition.
20. **`CREATE TABLE Ruivo_RingList`** — Second custom table for ring-range iteration. Demonstrates that multiple custom tables can coexist in a mod's database context.

**Lua patterns:**
- `PlayerConfigurations[playerID]:GetCivilizationTypeName()` / `:GetLeaderTypeName()` — get civ/leader type names from config. Used to skip barbarians/free cities.
- `pPlayer:GetCities()` returns an iterable cities collection.
- Binary decomposition loop using a predefined `Ruivo_BinaryList` table — the Lua-side algorithm that decomposes integer N into bit-properties and calls `SetProperty` for each.

**Quality patterns:**
- Framework design: define data in `Ruivo_New_Adjacency` config table, let the SQL engine generate all modifiers/requirements via JOIN. Zero per-bonus boilerplate once the framework exists.
- DLC safety throughout: every expansion-dependent effect type is wrapped in an `EXISTS` guard.
- `DistrictReplaces` propagation: ensures vanilla-district bonuses automatically apply to all unique replacement districts, including future DLC civs.
- Comments in Chinese (author's native language) — no functional impact but demonstrates that SQL comment language doesn't matter.

---

### C&P Naval Trade Protection ✅ COMPLETE

**Patterns not in skill:**
1. **`TypeProperties` table with SELECT-based INSERT** — `INSERT INTO TypeProperties (Type, Name, Value, PropertyType) SELECT Type, 'CAN_TELEPORT_TO_CITY', 1, 'PROPERTYTYPE_IDENTITY' FROM TypeTags WHERE Tag LIKE 'CLASS_NAVAL_%' AND ...` — bulk-sets a named type property on all units matching a tag filter. `TypeProperties` is a generic key-value store on any `Type`. `PROPERTYTYPE_IDENTITY` means the property defines the object's identity/capability. Not documented in skill at all.
2. **`UnitAbilities` table** — Unit abilities are a distinct system from promotions. Key columns: `UnitAbilityType`, `Name`, `Description`, `Inactive` (1 = hidden from UI), `Permanent` (1 = can't be removed). Abilities grant modifiers via `UnitAbilityModifiers`. Classes are assigned via `TypeTags`. Skill documents unit promotions but not unit abilities.
3. **`UnitAbilityModifiers` table** — Links `UnitAbilityType` → `ModifierId`. The ability activating automatically fires these modifiers. Different from `UnitPromotionModifiers`.
4. **`EFFECT_CHANGE_UNIT_OPERATION_AVAILABILITY`** — Enables or disables a specific unit operation on units matching the collection. Args: `OperationType`, `Available` (0/1). Used to grant naval teleport (`UNITOPERATION_TELEPORT_TO_CITY`) via policy. Not in skill.
5. **`EFFECT_ADJUST_UNIT_TRADE_ROUTE_PLUNDER_IMMUNITY`** — Makes trade route units within range immune to plundering. Args: `DomainType`. Applied via `COLLECTION_PLAYER_UNITS` with a SubjectRequirementSet checking range and unit type. Not in skill.
6. **`COLLECTION_PLAYER_UNITS`** — Collection of all units owned by the player. Used with unit-level effects. Skill doesn't list this collection.
7. **`MODIFIER_PLAYER_UNITS_GRANT_ABILITY`** — Grants a `UnitAbilityType` to all player units (or filtered via SubjectRequirementSet). Args: `AbilityType`. Used via `PolicyModifiers` to conditionally grant the teleport ability. Not in skill.
8. **`AOE_REQUIRES_OWNER_ADJACENCY`** — Built-in pre-existing requirement checking that the subject unit is adjacent (within range) of the modifier's owner (the unit applying the effect). Used with `COLLECTION_PLAYER_UNITS` to create area-of-effect plunder immunity centered on each naval unit. This is the standard AOE pattern in Civ6 unit modifiers.
9. **`GovernorPromotionModifiers` table** — Links governor promotion types to modifiers. Pattern for overriding existing promotions: `DELETE FROM GovernorPromotionModifiers WHERE ModifierId = '...'` first, then `INSERT` replacements. Not documented in skill.
10. **`MODIFIER_SINGLE_CITY_ADJUST_IDENTITY_PER_TURN`** — Adjusts loyalty per turn on a city. Args: `Amount`. Used from governor promotions. Skill mentions loyalty briefly but not this modifier type.
11. **Stacked property-threshold pattern for scaling bonuses** — Instead of one modifier scaling with a property count, Leugi uses 5 separate modifiers each gated by a different property (`LEU_NUM_TRADING_POSTS_1`, `_2`, `_4`, `_8`, `_16`). Each property is a bit-flag set by Lua when trading post count crosses that threshold. This produces doubling bonuses (4, 8, 16, 32, 64 gold) while working around the lack of direct "multiply by property value" in SQL. A clever workaround for the absence of formula-based yields.
12. **`UPDATE Units SET BaseSightRange = BaseSightRange + 1 WHERE Domain = 'DOMAIN_SEA'`** — Bulk UPDATE with arithmetic on existing values. Skill shows UPDATE for single column replacement but not arithmetic modification. Also: `UPDATE Units SET ... WHERE Domain = '...'` for domain-wide unit tweaks.
13. **`INSERT INTO TypeTags SELECT UnitType, 'CLASS_LEU_WATER_HERO' FROM Units WHERE UnitType LIKE 'UNIT_HERO%' AND Domain = 'DOMAIN_SEA'`** — SELECT-based tag assignment matching a naming convention filter. Automatically future-proofs against new content.

**Quality patterns:**
- Two-state ability pattern: `ABILITY_X` (Inactive=1, used for effect) + `ABILITY_X_DISABLED` (Permanent=1, blocks operation when active) — clean toggle mechanism.
- `INSERT OR REPLACE INTO Requirements` when overriding base game requirement args — avoids collision errors on requirements that already exist.

---

### C&P Religious Pressure from Trade ✅ COMPLETE

**Patterns not in skill:**
1. **`<ModInUse>` criteria** — `<Criteria id="BetterTradeScreenMod"><ModInUse>8d4fa23a-ef43-440c-8422-2bec11f8f5d7</ModInUse></Criteria>` — fires only when a specific mod (by UUID) is active. Used to conditionally load compatibility patches. Completely undocumented in skill.
2. **`ImportFiles` action type** — `<ImportFiles>` with `<Criteria>` loads files only when the criteria is met. Here it replaces the Better Trade Screen mod's Lua files with C&P-patched versions. This is distinct from `AddUserInterfaces` (which always loads) — `ImportFiles` applies criteria-conditional file replacement. Not in skill.
3. **`<SpecialThanks>` in modinfo Properties** — cosmetic metadata field, no functional effect.
4. **`UpdateIcons` in FrontEndActions** — Icons can be registered in the FrontEnd context (not just InGame). Needed for icons that appear on the setup/lobby screen (e.g., policy icons visible during lobby configuration).
5. **`UpdateText` in FrontEndActions with LoadOrder** — Text strings referenced from FrontEnd SQL (like `Parameters` entries) need to be loaded via `UpdateText` in `FrontEndActions`. Order matters: text before database that references it.
6. **`GlobalParameters` table** — `UPDATE GlobalParameters SET Value = 1 WHERE Name = 'TRADE_ROUTE_TURN_DURATION_BASE'` — modifying global engine constants. These are single-value named parameters that control engine-level behaviour. Not documented in skill. Key trade-relevant parameters: `TRADE_ROUTE_TURN_DURATION_BASE`, `RELIGION_SPREAD_TRADE_ROUTE_PRESSURE_FOR_DESTINATION`, `RELIGION_SPREAD_TRADE_ROUTE_PRESSURE_FOR_ORIGIN`.
7. **`Eras_XP2` table** — `UPDATE Eras_XP2 SET TradeRouteMinimumEndTurnChange = 1` — expansion-specific era properties table. Not in skill.
8. **`MODIFIER_PLAYER_ADJUST_TRADE_ROUTE_RELIGIOUS_PRESSURE`** — Adjusts religious pressure spread via trade routes. Args: `Origin` (0/1), `Destination` (0/1), `Amount`. Can target origin city, destination city, or both independently. Confirmed against `DELETE FROM TraitModifiers WHERE ModifierId = 'TRAIT_ORIGIN_DESTINATION_RELIGIOUS_PRESSURE'` which removes the vanilla version first.
9. **`MODIFIER_ALL_PLAYERS_ATTACH_MODIFIER`** with `SubjectRequirementSetId = 'PLAYER_FOUNDED_RELIGION_REQUIREMENTS'`** — Attaches a modifier to all players who founded a religion. `PLAYER_FOUNDED_RELIGION_REQUIREMENTS` is a built-in requirement set — no need to define it. Used for belief modifiers that should apply across all players who adopt the belief and have a religion. Pattern for religion-wide modifier attachment.
10. **`BeliefModifiers` table** — Links `BeliefType` → `ModifierId`. Belief modifiers fire when the belief is active for a player's religion. Skill mentions beliefs but doesn't document `BeliefModifiers`.
11. **`Beliefs` table columns** — `BeliefClassType`: `BELIEF_CLASS_FOUNDER`, `BELIEF_CLASS_FOLLOWER`, `BELIEF_CLASS_ENHANCER`, `BELIEF_CLASS_WORSHIP`. Determines which slot in the religion this belief occupies.
12. **`INSERT OR REPLACE INTO TraitModifiers SELECT ... FROM Traits WHERE TraitType = '...'`** — Conditional trait modifier assignment: only inserts if the trait exists. Safe pattern when the target civilization may not be installed (DLC/expansion civs). Equivalent to an existence check without Lua.
13. **`Game:SetProperty(key, value)` / `Game:GetProperty(key)`** — Game-level (not player/city/unit/plot) properties. Used here to store religion names keyed by religion type index. Lua-side global state that persists across turns. Not documented in skill which only covers plot/city/player/unit properties.
14. **`pCity:GetBuildQueue():AddProgress(iReward)`** — Directly adds production progress to a city's build queue. No SQL equivalent. Used for the Chichen Itza "burst production when trader passes through" effect.
15. **`pPlayer:GetTechs():ChangeCurrentResearchProgress(amount)`** — Directly advances current tech research by a flat amount. Used for Arabia burst science. Not in skill.
16. **`pPlayer:GetReligion():ChangeFaithBalance(amount)`** — Directly adds faith to the player. Not in skill.
17. **`pPlayer:GetGreatPeoplePoints():ChangePointsTotal(classIndex, amount)`** — Directly adds Great Person points of a specific class. `classIndex` retrieved via `GameInfo.GreatPersonClasses["GREAT_PERSON_CLASS_..."].Index`. Not in skill.
18. **`pCity:GetReligion():AddReligiousPressure(playerID, religionType, amount, sourceType)`** — Directly applies religious pressure to a city from Lua. `sourceType = -1` uses default. This is the core mechanism for the "trader passes through = pressure burst" feature. Not in skill.
19. **`pCity:GetReligion():GetMajorityReligion()`** — Gets the majority religion index of a city. Returns -1 if none. Not in skill's Lua API coverage.
20. **`pPlayer:GetReligion():GetReligionInMajorityOfCities()`** — Gets the religion that is in the majority of the player's cities. Returns nil if none. Not in skill.
21. **`pPlayer:GetReligion():GetReligionTypeCreated()`** — Gets the religion type founded by this player. Returns -1 if no religion founded. Not in skill.
22. **`Game.AddWorldViewText(table)`** — Adds a floating text notification at a map position. Table fields: `MessageType = 0`, `MessageText` (localised string), `PlotX`, `PlotY`, `Visibility = RevealedState.VISIBLE`. Standard pattern for burst-effect feedback. Not in skill.
23. **`IconTextureAtlases` `Baseline` column** — `Baseline = 6` on a 22px icon atlas. Sets the vertical offset for font icon rendering (used for inline `[ICON_X]` tags in text). Required for custom font icons. Skill doesn't document this column.
24. **`[ICON_LEU_RELIGIOUS_PRESSURE]` inline icon pattern** — Custom font icons registered at 22px can be referenced inline in localisation strings and UI text. The atlas entry with `Baseline` controls vertical alignment. Full pattern: register 22px atlas with Baseline → define IconDefinition → reference as `[ICON_NAME]` in text strings.

**Quality patterns:**
- Granular Lua variable extraction at top of file (all tunable values as local vars) — easy to tweak without hunting through code.
- `iMod` game speed multiplier applied consistently to all burst rewards.
- Nil guards on every Lua function (`if pPlayer == nil then return end`) before accessing properties.

---

### C&P Exchange of Ideas ✅ COMPLETE

**Patterns not in skill:**
1. **`ObsoletePolicies` table** — Policies can obsolete other policies (`ObsoletePolicy` column) or require a Great Person class to still be available (`RequiresAvailableGreatPersonClass`). `POLICY_LEU_PERIPLUS` is replaced by `POLICY_LEU_MODERNIZATION` when that later civic unlocks. Several Great People burst policies become unavailable once that class is exhausted. Not documented in skill.
2. **`MODIFIER_PLAYER_ADJUST_PROPERTY`** — Sets a named player property to a value. Args: `Key` (property name), `Amount`. Used to flip a boolean flag on the player when a policy is active. Lua then reads `pPlayer:GetProperty("LEU_HAS_...")` to gate burst effects. This is the SQL-to-Lua bridge pattern: SQL sets a flag, Lua reads it each turn. Skill has no coverage of player properties at all.
3. **`MODIFIER_PLAYER_ADJUST_PROGRESS_DIFF_TRADE_BONUS`** — Built-in modifier for "catch-up tech/culture from trade routes to more advanced civs." Args: `TechCivicsPerYield` (techs/civics they're ahead = yield bonus multiplier). This is a specialised modifier type not documented in skill.
4. **`AllianceEffects` table + SELECT-based INSERT** — Registering modifier effects for specific alliance types at a minimum level via `AllianceEffects (LevelRequirement, AllianceType, ModifierID)`. Combined with a `SELECT ... FROM Buildings WHERE PrereqDistrict = ...` pattern to generate one modifier per building automatically — no manual enumeration needed. This SELECT-based bulk insert pattern is far more powerful than anything in the skill.
5. **`COLLECTION_ALLIANCE_PLAYERS`** — Collection type targeting all players you have an alliance with. Used in `DynamicModifiers` to attach modifiers to allied players' cities. Skill only documents player/city/district collections.
6. **`REQUIREMENT_PLAYER_LEADER_TYPE_MATCHES`** — Requirement checking specific leader identity. Args: `LeaderType`. Used to gate modifier to Peter the Great only. Skill doesn't document this.
7. **`DELETE FROM TraitModifiers WHERE ModifierId = '...'`** — Removes a specific modifier from a civ/leader trait. Here removes Peter's vanilla Grand Embassy bonus since it's being replaced. Pattern for cleanly overriding built-in leader abilities without leaving ghost effects.
8. **`Events.UnitMoved.Add()`** — Built-in engine event firing every time any unit moves. Args: `playerID, unitID, iX, iY`. Used to trigger effects when a Trader passes through a city tile. High-frequency event — needs `if pPlot:IsCity() == false then return end` guard. Not documented in skill.
9. **`pUnit:GetProperty()` / `pUnit:SetProperty()`** — Unit-level properties (distinct from player/plot properties). Used to store the trader's origin city ID on the unit itself. Pattern: set on dispatch, read on move. Not documented in skill.
10. **`pPlot:IsCity()`** — Checks if a plot contains a city center. Not documented in skill.
11. **`Cities.GetCityInPlot(iX, iY)`** — Gets city object from map coordinates. Distinct from `CityManager.GetCity(playerIndex, cityId)`. Not documented in skill.
12. **`pPlayer:GetProperty(key)`** — Player-level property read. Paired with `MODIFIER_PLAYER_ADJUST_PROPERTY` on the SQL side to detect active policy state in Lua. Skill doesn't document player properties.
13. **`pCity:ChangeLoyalty(amount)`** — Direct loyalty modification on a city. Used for the Structural Adjustment policy (traders reduce enemy city loyalty). Not documented in skill.
14. **`pPlayer:GetTechs():ChangeCurrentResearchProgress(amount)`** — Adds science points directly to current research. Used for burst science on trade route pass-through. Not documented in skill.
15. **`pPlayer:GetCulture():ChangeCurrentCulturalProgress(amount)`** — Adds culture points directly to current civic research. Not documented in skill.
16. **`pPlayer:GetReligion():ChangeFaithBalance(amount)`** — Adds faith directly to player's faith pool. Not documented in skill.
17. **`pPlayer:GetGreatPeoplePoints():ChangePointsTotal(classIndex, amount)`** — Adds great person points for a specific class. Index retrieved from `GameInfo.GreatPersonClasses["CLASS_NAME"].Index`. Not documented in skill.
18. **`pCity:GetYield(YieldTypes.SCIENCE)`** — Gets a city's current yield for a given type. Used for "burst yield equal to city output" effects. `YieldTypes` enum (SCIENCE, CULTURE, FAITH, etc.). Not documented in skill.
19. **`Game.AddWorldViewText(table)`** — Displays a floating text message on the map. Table fields: `MessageType`, `MessageText`, `PlotX`, `PlotY`, `Visibility`. Used for burst feedback text (e.g., "+15 [ICON_SCIENCE]"). Not documented in skill.
20. **`Locale.Lookup(string)`** — Translates a localisation key or formats a string with inline color/icon tags. Used to build display strings. Not documented in skill.
21. **`math.ceil(value * iMod)`** — Game speed scaling of Lua burst values. `iMod` from `CostMultiplier/100`. Standard pattern for any Lua values that should scale with game speed.
22. **Multiple files in a single action** — A single `<UpdateText>` action can list multiple `<File>` entries:
    ```xml
    <UpdateText id="PeterRework">
      <File>PeterRework/PeterRework_Texts.sql</File>
      <File>Policies/TradePolicies_Texts.sql</File>
    </UpdateText>
    ```
    Skill implies one file per action.

**Patterns that contradict skill:**
- None significant.

**Quality patterns:**
- `MODIFIER_PLAYER_ADJUST_PROPERTY` as SQL-to-Lua bridge is Leugi's standard pattern across all C&P mods. Clean: SQL owns the "is this policy active?" state, Lua just reads it.
- SELECT-based INSERT for `AllianceEffects` + `Modifiers` + `ModifierArguments` generates all building-specific modifiers automatically from a single query. Eliminates dozens of manual rows and auto-handles modded buildings that add to the district.
- `Events.UnitMoved` guard pattern: check unit type → check if plot is city → check if it's a foreign city → apply effect. Always guard high-frequency events.

### C&P Domestic Trade Bonuses ✅ COMPLETE

**Patterns not in skill:**
1. **`DoNothing` action type with `Exclude`** — `<DoNothing>` is an action type that does nothing on its own but can reference `<Exclude>` tags that disable other actions when criteria are met. Pattern: if config value = 0, disable the optional sub-feature actions. This is the canonical way to make mod features opt-out via Advanced Setup toggle. Skill doesn't document `DoNothing` or `Exclude` at all.
2. **`Parameters` table for Advanced Setup toggles** — `INSERT INTO Parameters` in FrontEnd SQL registers a game setup option in the Advanced Setup UI. Fields: `ParameterId`, `Name`, `Description`, `Domain` (bool/int), `DefaultValue`, `ConfigurationGroup`, `ConfigurationId`, `GroupId`, `SortIndex`. The `ConfigurationId` is the same key used in `ConfigurationValueMatches` criteria. This is the complete pattern for opt-in/opt-out mod features via lobby settings.
3. **`UpdateIcons` action type** — `<UpdateIcons>` in InGameActions for loading icon SQL. Distinct from `UpdateDatabase`. Skill only covers `UpdateDatabase` and `UpdateText`.
4. **`ImprovementModifiers` on base game improvements** — Attaching modifiers to game-default improvements (FARM, PLANTATION, PASTURE, etc.) to add trade yield bonuses when those improvements are present at the destination city. The modifier uses `OwnerRequirementSetId` (checks destination plot) and `SubjectRequirementSetId` (checks destination city buildings). The "owner" here is the improvement plot; the "subject" is the city receiving the trade route.
5. **Decimal values in ModifierArguments Amount** — `Amount = 0.5` for fractional yields (e.g., +0.5 food per bonus resource). Skill implies integer-only. Confirmed valid.
6. **`REQUIRES_PLOT_HAS_BONUS` / `REQUIRES_PLOT_HAS_STRATEGIC` / `REQUIRES_PLOT_HAS_VISIBLE_RESOURCE`** — Built-in requirement types for resource class checks. No RequirementArguments needed. Skill doesn't list these pre-built requirements.
7. **`REQUIREMENT_PLOT_RESOURCE_CLASS_TYPE_MATCHES`** — Requirement checking resource class type (e.g., `RESOURCECLASS_LUXURY`). Distinct from `REQUIRES_PLOT_HAS_BONUS`.
8. **`MODIFIER_PLAYER_CITIES_ADJUST_BUILDING_YIELD_CHANGE`** — Applies a yield change to all instances of a specific building across all player cities. Args: `BuildingType`, `YieldType`, `Amount`. Used for policy bonuses to buildings. Skill doesn't cover this modifier type.
9. **`MODIFIER_PLAYER_ADJUST_BUILDING_FAVOR`** — Grants World Congress Favor per turn from a specific building. Args: `BuildingType`, `Favor`. GS-only pattern.
10. **`MODIFIER_PLAYER_DISTRICTS_ADJUST_TOURISM_CHANGE`** — Adjusts tourism on districts matching a requirement set. Used with `SubjectRequirementSetId` to target city center districts that also have a specific building.
11. **`MODIFIER_PLAYER_CITIES_ATTACH_MODIFIER`** — Attaches a child modifier to all player cities that meet a `SubjectRequirementSetId`. Used to conditionally apply population/housing/amenity bonuses to cities with owned trading posts or active trade routes via the Angkor Wat rework. This is distinct from `MODIFIER_SINGLE_CITY_GRANT_BUILDING_IN_CITY_IGNORE` — it's a dynamic attach on the player-cities collection.
12. **`REQUIREMENT_PLOT_PROPERTY_MATCHES`** — Checks a custom plot property (set via Lua `pPlot:SetProperty()`). Args: `PropertyName`, `PropertyMinimum`. This is the SQL side of the Lua property pattern. Lets Lua-set data gate SQL modifier behaviour. Skill has no coverage of this bridge between Lua and SQL.
13. **`EFFECT_ADJUST_CITY_POPULATION`** — Direct population adjustment effect. Used in custom DynamicModifiers.
14. **`EFFECT_ADJUST_NATURAL_WONDER_AMENITY`** — Adjusts the amenity bonus granted by a natural wonder (or wonder building). Not a normal city amenity — specifically for wonder-type amenities.
15. **`MODIFIER_CITY_ENABLE_UNIT_FAITH_PURCHASE`** — Enables faith purchasing for a unit class in a city. Arg: `Tag` (unit class tag like `CLASS_TRADER`). Skill doesn't document this at all.
16. **`BuildingReplaces` table + SELECT-based INSERT for mutual exclusivity** — Using a `SELECT ... FROM BuildingReplaces` inside an `INSERT INTO MutuallyExclusiveBuildings` to automatically handle civ-unique building replacements (e.g., if a civ replaces Water Mill with a unique building, the new building is also made mutually exclusive with the River Port). This is the canonical pattern for modding buildings that have civ-unique replacements. Skill doesn't mention `BuildingReplaces` at all.
17. **`DELETE FROM BuildingModifiers WHERE ModifierId = '...'`** — Clean removal of specific modifier associations from existing buildings (here, Angkor Wat). More surgical than `UPDATE`. Skill only shows `INSERT` and `UPDATE`.
18. **Custom `GameEvents` with properties** — `GameEvents.Leu_LocalOwnedTradingPostProperty.Add(...)` and `pPlot:SetProperty("LeuHasOwnedTradePost", 1)` — Lua-side custom game events combined with plot properties to pass data between Lua scripts. Completely absent from skill's Lua section.
19. **`Events.WonderCompleted.Add()`** — Built-in engine event for wonder placement. Args: `locX, locY, buildingIndex, playerIndex, cityId, iPercentComplete, pillaged`. `iPercentComplete == 100` check ensures the wonder is actually complete (not mid-construction). Not documented in skill.
20. **`GameInfo.GameSpeeds[GameConfiguration.GetGameSpeedType()].CostMultiplier`** — Pattern for scaling Lua values to game speed. Standard modder practice, not documented.
21. **Icon sizes and atlases for UI buildings** — `IconTextureAtlases` requires multiple rows per atlas for different sizes (256, 128, 80, 50, 38, 32). Multiple `INSERT` rows with same `Name` but different `IconSize` values. Icons for policies use existing `ICON_ATLAS_POLICIES` with slot index 0 (Economic), 2 (Diplomatic). Skill mentions atlases but not the multi-size pattern or policy icon slots.
22. **`RequiresAdjacentRiver` column on Buildings** — Buildings that require river placement. City Center buildings can use this too (not just districts). Skill mentions the river tag on improvements but not this building column.
23. **`Building_YieldChangesBonusWithPower` on City Center buildings** — Power-dependent yield on a City Center building (Food Market). Not limited to district buildings.

**Patterns that contradict skill:**
- None significant.

**Quality patterns:**
- Dev comments in SQL explaining modifier intent ("as a personal note because trade modifiers are always friggin' confusing") — useful for maintainability, worth adopting.
- `BuildingReplaces` SELECT pattern for mutual exclusivity is essential whenever adding buildings that compete with replaceable vanilla buildings. Miss this and the mod breaks for any civ that has a replacement.
- Feature opt-in/opt-out via Parameters + ConfigurationValueMatches + DoNothing/Exclude is Leugi's standard pattern across all C&P mods.
- `RequiresAdjacentRiver = 1` on the River Port is pure design elegance — the building name tells you the placement rule.

**Lua patterns:**
- Plot properties as a Lua-to-SQL bridge: set via `pPlot:SetProperty(key, value)`, read in SQL via `REQUIREMENT_PLOT_PROPERTY_MATCHES`.
- `Events.WonderCompleted` for wonder-built triggers.
- Custom `GameEvents` for cross-script communication.
- `GameInfo.GameSpeeds[...].CostMultiplier` for game-speed-aware scaling.

### City Lights ✅ COMPLETE

**Patterns not in skill:**
1. **ConfigurationValueMatches criteria** — `<ConfigurationValueMatches>` in ActionCriteria to load SQL based on game settings (difficulty, integration level, SP/MP). Multiple `<Criteria>` tags = AND logic. `any="1"` = OR logic. Not in skill at all.
2. **LeaderPlayable criteria** — DLC detection by checking if specific leaders are playable (not DLC ID checks).
3. **Priority attribute on File elements** — `<File priority="25">` controls intra-action load order.
4. **Platform-specific BLPs** — `Platforms/MacOS/BLPs/` and `Platforms/Windows/BLPs/` with `SHARED_DATA/BLOB_` and `SHARED_DATA/TEXTURE_` prefixed files. Not covered in art pipeline reference.
5. **`<Dependencies>` block** — Hard mod dependencies in modinfo.
6. **`UpdateArt` action** — Loading `.dep` and artdef files via `<UpdateArt>` in InGameActions. Skill's art pipeline doesn't cover this action type.
7. **SQL for FrontEnd config** — `.sql` files (not XML) for FrontEnd config data.
8. **`COST_PROGRESSION_GAME_PROGRESS`** — Era-based district cost (confirmed). Districts use `CostProgressionParam1` = 500 or 1000 to tune scaling rate.
9. **`MutuallyExclusiveDistricts` table** — Blocks two district types from coexisting in a city. Skill doesn't mention this table.
10. **`AppealHousingChanges` table** — District housing modifiers based on appeal tier. Multiple rows per district for different appeal thresholds.
11. **`District_TradeRouteYields` table** — Districts providing trade route yields (origin, domestic, international) independently of buildings.
12. **`District_CitizenYieldChanges` table** — Districts adding directly to citizen (worked tile) yields.
13. **`DistrictModifiers` with `MODIFIER_CITY_PLOT_YIELDS_ADJUST_PLOT_YIELD`** — Districts applying improvement-specific plot yield bonuses via requirement sets.
14. **`GameModifiers` table** — Always-active game-wide modifiers (used for unit granting on district placement). Distinct from Building/DistrictModifiers.
15. **`Buildings_XP2` (RequiredPower)** — Separate table for GS power requirements on buildings.
16. **`Building_YieldChangesBonusWithPower`** — Additional yields when city is powered.
17. **`Projects_XP2` (UnlocksFromEffect, RequiredBuilding, CreateBuilding)** — Staged project chains: project consumes a building and creates the next tier building. The entire tiered upgrade loop is run through this pattern.
18. **`Project_BuildingCosts`** — Projects that consume buildings as a production cost.
19. **`ProjectCompletionModifiers`** — One-shot modifiers triggered on project completion.
20. **`CivilopediaPageExcludes`** — Explicitly hide internal/tracking buildings from Civilopedia.
21. **DISABLE_INTERNAL dummy building pattern** — An `InternalOnly = 1` building with `Cost = 9999` used as a prereq to permanently block player construction of internal tracking buildings (e.g. `BUILDING_COREX_TIER1_SCI_1`). The dummy prereq can never be built, so the tracking building is only constructible via modifier grants.
22. **`TraitType = 'TRAIT_CIVILIZATION_NO_PLAYER'`** on improvements — Blocks all player/AI construction of an improvement. City-level `MODIFIER_CITY_ADJUST_ALLOWED_IMPROVEMENT` then unlocks it per city when the right building is built. This is the canonical pattern for improvement gating.
23. **`MODIFIER_CITY_ADJUST_ALLOWED_IMPROVEMENT`** — Per-city improvement unlock. Each tier-2 district building unlocks a specific improvement type in that city only.
24. **Negative `YieldChange` in `Adjacency_YieldChanges`** — Penalty adjacencies. Rural Communities penalise adjacent specialized districts (e.g., `-1 science` when adjacent to Campus). This bidirectional adjacency pattern (mutual benefit + mutual penalty) not documented.
25. **`SubjectStackLimit` on Modifiers** — Caps how many times a modifier fires on a single subject. Used on the `COREX_TIER2_GOL_ATTACH_MODIFIER` to limit trade route adjacency bonus to 1 Commercial Hub.
26. **`OwnerRequirementSetId` and `OwnerStackLimit`** on Modifiers — Owner-side conditions and owner-side stacking limits. Distinct from SubjectRequirementSetId.
27. **`EFFECT_ADJUST_DISTRICT_YIELD_BASED_ON_ADJACENCY_BONUS`** — Mirrors one yield type as another (e.g., mirrors production adjacency bonus as gold). Uses `YieldTypeToGrant` / `YieldTypeToMirror` args. Skill doesn't cover this effect.
28. **Power system modifiers**: `MODIFIER_SINGLE_CITY_ADJUST_REQUIRED_POWER` and `MODIFIER_SINGLE_CITY_ADJUST_FREE_POWER` and `MODIFIER_PLAYER_CITIES_ADJUST_FREE_POWER` (with spatial req). None documented in skill.
29. **`MODIFIER_SINGLE_CITY_ADJUST_FREE_RESOURCE_EXTRACTION`** — Grants free strategic resource units to a city without owning the tile. Used for oil/aluminum extraction via Refinery.
30. **`REQUIREMENT_PLAYER_ERA_AT_LEAST`** — Era-based modifier gating. Used to give different bonuses once Industrial Era is reached.
31. **`REQUIREMENT_PLOT_ADJACENT_TERRAIN_TYPE_MATCHES` with `MaxRange`** — Checks if a terrain type exists within N tiles of the plot. Used for Research Base yields based on local terrain.
32. **Three scopes of plot yield modifiers**: `MODIFIER_SINGLE_PLOT_ADJUST_PLOT_YIELDS` (per-plot, from an improvement modifier), `MODIFIER_CITY_PLOT_YIELDS_ADJUST_PLOT_YIELD` (city-wide filtered by RequirementSet), `MODIFIER_PLAYER_ADJUST_PLOT_YIELD` (player-wide). Skill conflates these.
33. **`Adjacency_YieldChanges` with `AdjacentResourceClass`** — Adjacency bonus based on resource class (LUXURY, BONUS, STRATEGIC) rather than specific resources. Manufactory gets +2 production from any adjacent luxury/bonus resource.
34. **`MODIFIER_CITY_DISTRICTS_ADJUST_YIELD_MODIFIER`** — Percentage yield modifier on all districts (or filtered by req set). Used for +100% science on COREX districts.
35. **`Improvement_Tourism`** — Tourism from improvements after a tech unlock. `TOURISMSOURCE_` enum selects which yield drives tourism; `ScalingFactor` = multiplier ×100 (100 = 1:1). Skill doesn't document this table.
36. **`MODIFIER_ADJUST_AMENITIES_IN_DISTRICT`** — Grants amenity specifically to plots within a district (e.g., to tiles adjacent to a Wonder). Not the same as city-wide amenity.
37. **`MODIFIER_SINGLE_CITY_ADJUST_CITY_YIELD_PER_POPULATION`** — Per-population yield (e.g., 0.5 production per citizen). Arg is a decimal.
38. **`COLLECTION_PLAYER_PLOT_YIELDS`** — Collection type for player-wide plot yield attachment. Skill only documents common collections.
39. **`MODIFIER_SINGLE_CITY_ADJUST_CITY_GROWTH`** — Flat percentage growth boost on a city.
40. **`MODIFIER_SINGLE_CITY_ADJUST_TOURISM`** — Adjusts improvement-specific tourism multiplier (used for Artificial Reef tourism scaling ×4).
41. **`YieldFromAppeal` and `YieldFromAppealPercent`** columns on Improvements — Improvements can generate a yield proportional to plot appeal. `YieldFromAppeal = YIELD_GOLD` with `YieldFromAppealPercent = 200` = 2× appeal as gold. Documented in table but never in skill.
42. **`OwnerRequirementSetId` on Modifiers tied to power state** — `OwnerRequirementSetId = 'CITY_IS_POWERED'` used to make modifier conditional on city being powered. Standard pattern for GS power-dependent effects.

**Patterns that contradict skill:**
- Skill implies LoadOrder 1000+ for FrontEnd actions. City Lights uses 300 for text, no explicit LoadOrder on FrontEnd UpdateDatabase. Defaults work fine for most cases.

**Quality patterns:**
- Modular SQL per DLC level, per feature area, per difficulty. Config-driven via pre-game settings.
- `COREX_` prefix consistent throughout all types, modifiers, requirement sets.
- Internal tracking buildings hidden via `InternalOnly`, `CivilopediaPageExcludes`, and `DISABLE_INTERNAL` prereq pattern — none of this exposed to the player.
- Projects used as the "progress bar" mechanism to upgrade tracking buildings through a chain — not for resource rewards. Clean separation of concerns.

**Art patterns:**
- Platform BLPs in `Platforms/Windows/` and `Platforms/MacOS/` with identical `SHARED_DATA/` content. Both platforms needed.
- `.ast` asset files in `Assets/` (not in XLPs) — these are individual asset files referenced directly.

**Still to review (none — City Lights complete)**

**Patterns not in skill:**
1. **ConfigurationValueMatches criteria** — City Lights uses `<ConfigurationValueMatches>` in ActionCriteria to conditionally load SQL files based on pre-game settings (difficulty, civ integration level, singleplayer/multiplayer). The skill mentions ActionCriteria briefly but doesn't cover ConfigurationValueMatches at all. This is how CSC could implement optional M&C integration.
2. **Multiple Criteria on one action** — Multiple `<Criteria>` tags on a single `<UpdateDatabase>` act as AND logic (all must be true). The skill doesn't explain this.
3. **`any="1"` on Criteria** — `<Criteria id="XP1 or XP2" any="1">` makes child conditions OR instead of AND. Not in skill.
4. **LeaderPlayable criteria** — Detecting specific DLC by checking if leaders are playable, rather than checking DLC IDs directly. Elegant DLC detection pattern.
5. **Priority attribute on File elements** — `<File priority="25">` controls load order within an action. Skill mentions LoadOrder on actions but not priority on files.
6. **Platform-specific BLPs** — `Platforms/MacOS/BLPs/` and `Platforms/Windows/BLPs/` folders with pre-cooked platform-specific assets. Not covered in art pipeline reference.
7. **SHARED_DATA folder pattern** — BLPs reference a `SHARED_DATA` folder with `BLOB_` and `TEXTURE_` prefixed files. This is how cooked assets are shared between platforms.
8. **`<Dependencies>` block** — Declaring hard dependencies on specific mods (expansions). Skill doesn't cover this.
9. **UpdateArt action** — Loading `.dep` files and artdef files via `<UpdateArt>` in InGameActions. Skill's art pipeline reference doesn't explain this action type.
10. **SQL for FrontEnd config** — Using `.sql` files (not XML) for FrontEnd config data (`COREX_Civ_Config.sql`). Skill implies XML is standard for config.

**Patterns that contradict skill:**
- Skill says LoadOrder 1000+ for FrontEnd database actions. City Lights uses LoadOrder 300 for text and no explicit LoadOrder for its FrontEnd UpdateDatabase, suggesting defaults work fine for most cases.

**Quality patterns:**
- Modular file organization: separate SQL files per DLC compatibility, per feature area, per difficulty level
- Config-driven modularity: players choose integration depth pre-game, mod loads different SQL accordingly
- Consistent naming: `COREX_` prefix throughout

**Still to review:** Gameplay SQL patterns (COREX_Core.sql, improvements, governors, policies)

### Cities and Towns Mode ✅ 2026-03-24

Maple_Leaves & Phantagonist. Full custom game mode: towns as improvement-based mini-settlements with specialization, population, plot control, and transfer-to-city. GS dependency. Very relevant to CSC's settlement-expansion concepts.

**Patterns not in skill:**
1. **Custom `Kind` type registration** — `INSERT INTO Kinds (Kind) VALUES ('KIND_MAPLE_LEAVES_TOWN')` — mods can create entirely new Kinds beyond the game defaults. The custom Kind is then used in `Types` to register custom entities (town specializations). Combined with `CREATE TABLE MapleLeavesTowns_Mode` as a custom data table with FK to `Types(Type)`. This is the full pattern for creating a mod-defined entity system. Not documented in skill.
2. **`GameModeItems` table** — Registers a custom game mode in the Game Setup UI. Fields: `GameModeType`, `Name`, `Description`, `Portrait`, `Background`, `Icon`, `SortIndex`. This is how official game modes (Heroes & Legends, Secret Societies, etc.) are registered, and mods can use the same system. Not in skill at all.
3. **`ParameterDependencies` table** — Controls when a game mode parameter appears in setup UI. `Operator = 'Exists'` checks if a config value exists, `Operator = 'NotEquals'` checks inequality. Used to hide the game mode option when World Builder is active or when GS ruleset isn't loaded. Not in skill.
4. **`PlayerItemOverrideQueries` + `Queries` + `QueryCriteria` tables** — Advanced config system: registers SQL queries that run at game start to apply player-specific overrides. `QueryCriteria` gates when the query runs (only when the game mode is active). The query output feeds into `GameModePlayerItemOverrides`. This is the framework for per-leader/per-civ game mode bonuses. Not documented anywhere in skill.
5. **`COLLECTION_PLAYER_IMPROVEMENTS`** — Collection targeting all improvements owned by a player. Used in custom `DynamicModifiers` (`MODIFIER_PLAYER_IMPROVEMENTS_ATTACH_MODIFIER_CATM`) to attach modifiers to all of a player's town improvements. Not in skill.
6. **`EFFECT_ADJUST_UNIT_PROPERTY`** — Sets a named property on units via SQL modifier. Combined with `COLLECTION_PLAYER_UNITS` to bulk-set properties. Not in skill — skill covers plot properties but not unit property effects.
7. **`EFFECT_ADJUST_CITY_ALLOWED_IMPROVEMENT`** — City-scoped version of improvement unlock. Used via custom `MODIFIER_PLAYER_CITIES_ADJUST_ALLOWED_IMPROVEMENT_CATM`. Different from `MODIFIER_CITY_ADJUST_ALLOWED_IMPROVEMENT` (which is building-scoped). Not in skill.
8. **`COLLECTION_ALL_CITIES`** — Collection targeting ALL cities in the game (not just one player's). Used for game-wide loyalty adjustments. Not in skill.
9. **`GovernmentModifiers` table** — Attaches modifiers to government types. When a player adopts a government, its modifiers activate. Used for government-specific town bonuses (Autocracy gives +1 city limit, Republic gives GP points per science town, etc.). Not in skill.
10. **`MODIFIER_UNIT_ADJUST_BUILDER_CHARGES`** — Adjusts the number of builder charges (build actions) on a unit. Used via UnitAbilities to give Settlers a build charge for placing towns. Not in skill.
11. **`MODIFIER_UNIT_ADJUST_BASE_COMBAT_STRENGTH`** — Adjusts a unit's base combat strength. Used to give Settlers 1 combat strength for self-defense. Not in skill.
12. **`MODIFIER_UNIT_ADJUST_COMBAT_STRENGTH`** — Combat strength adjustment keyed by a property value (`Key` arg). The actual bonus comes from a Lua-set property, creating a dynamic scaling effect. Not in skill.
13. **`ModifierStrings` with `Context = 'Preview'`** — Combat preview text for modifiers. When `Context = 'Preview'`, the string shows in the combat prediction UI. Essential for combat-related modifiers. Not documented in skill.
14. **`REQUIREMENT_PLOT_ADJACENT_IMPROVEMENT_TYPE_MATCHES`** — Checks if a plot is adjacent to a specific improvement type. Args: `ImprovementType`, `MinRange`, `MaxRange`. Used to check proximity to town improvements. Not in skill.
15. **Dynamic project generation from custom table** — `INSERT INTO Projects SELECT 'PROJECT_'||TownType||'_CATM', ... FROM MapleLeavesTowns_Mode WHERE Disabled = 0` — generates one project per active town type directly from the custom data table. Combined with `UnlocksFromEffect = 1` so projects are hidden by default and unlocked via Lua/modifier. All `CivilopediaPageExcludes` also auto-generated.
16. **`Improvement_ValidFeatures` SELECT from `Features` table** — `SELECT FeatureType FROM Features WHERE Impassable = 0 AND NaturalWonder = 0 AND Settlement = 1` — dynamically populates valid features from game data properties. Future-proofs against new features added by DLC/mods.
17. **`Improvement_ValidResources` SELECT with resource class filter** — `SELECT ResourceType FROM Resources WHERE ResourceClassType IN (...) AND Frequency > 0` — auto-populates valid resources. No manual enumeration.
18. **`GrantFortification` column on Improvements** — Improvements can provide fortification to units standing on them. `DefenseModifier` provides flat defense bonus. Towns give +4 defense and 2 fortification.
19. **`Improvement_ValidBuildUnits` table** — Specifies which unit types can build an improvement. Towns are buildable by Settlers, Missionaries, Apostles, Inquisitors, and Gurus — an unusual mix that creates multiple paths to town placement. Not in skill.
20. **`OwnerRequirementSetId = 'REQSET_PLAYER_IS_HUMAN_HAS_CAPITAL_CATM'`** — Human-only modifier gating. AI gets separate modifier tracks with different bonuses, ensuring balanced gameplay. Pattern: human modifiers in one file, AI modifiers in `_MajorAI.sql`.
21. **`ImprovementBuilder.SetImprovementType(pPlot, -1, iPlayer)`** — Lua function to remove an improvement from a plot. `-1` = remove. Used when converting a town to a city.
22. **`pPlayer:GetCities():Create(x, y)`** — Creates a new city at coordinates from Lua. The core mechanic for town-to-city conversion. Not documented in skill.
23. **`WorldBuilder.CityManager():SetPlotOwner(x, y, playerID, cityID)`** — Changes plot ownership to a specific player/city. Used for transferring town territory to a city-state. This is a WorldBuilder API — available in gameplay scripts but originally intended for scenario editing.
24. **`pPlayer:GetInfluence():GiveFreeTokenToPlayer(csPlayerID)`** — Grants a free envoy to a city-state. Used as a reward for transferring a town.
25. **`include("CityAndTownMode_SupportFunctions")`** — Mod-provided shared Lua library loaded via `include()`. The file must be listed in `ImportFiles`. Pattern for splitting complex Lua logic across files.
26. **Plot property as serialized table** — `pPlot:GetProperty("..._PLOT_LIST_CATM")` returns a Lua table (stored as serialized data). Properties can store arrays/tables, not just numbers/strings. Not documented in skill.
27. **`DisasterResistant = 1`** in `Improvements_XP2` — GS-only: improvement survives natural disasters (floods, volcanoes, etc.).
28. **Separate Human vs AI modifier files** — `CityAndTownMode_Human.sql` and `CityAndTownMode_MajorAI.sql` with `REQUIRES_PLAYER_IS_AI` / `REQUIRES_PLAYER_IS_HUMAN` gating. Clean separation of balance for human vs AI.

**Quality patterns:**
- Custom schema table (`MapleLeavesTowns_Mode`) with proper FOREIGN KEY constraints back to game tables — professional database design, not just loose INSERT statements.
- `_CATM` suffix on all custom IDs — consistent namespacing prevents collisions with other mods.
- Game mode registration via `GameModeItems`/`Parameters`/`ParameterDependencies` — the official way to create opt-in game modes, matching Firaxis's own patterns.
- LoadOrder management: schema at -200, main data at 40000, post-processing at 400000. Ensures tables exist before data, and data exists before cross-references.
- Dynamic project generation from config table = zero per-town boilerplate. Adding a new town specialization = one row in `MapleLeavesTowns_Mode`.

**CSC relevance:** HIGH. The game mode registration pattern could be how CSC offers its feature as an optional mode. The custom Kind + custom data table architecture is directly applicable to Quarter types. The human-vs-AI balancing split is something CSC should adopt. The plot property as serialized table pattern opens up complex state storage on tiles.

### Project Metropolis ✅ 2026-03-24

Furion1986. **The closest existing mod to CSC** — adds 9 "Quarters" as minor districts that don't require population and allow multiples per city. Full custom art, 6 ArtDefs, custom unit commands (demolish via Builder/Military Engineer), custom strategic resource (Steel). Requires GS + R&F + 7 DLC packs. This is the reference implementation for CSC's core concept.

**Patterns not in skill:**
1. **`ReplaceUIScript` action type** — `<ReplaceUIScript>` in InGameActions with `<LuaContext>` and `<LuaReplace>` properties. Completely replaces a specific UI script context (here `UnitPanel`) with a modded version. Different from `ImportFiles` UI replacement (which replaces by filepath). `ReplaceUIScript` targets by context name. **Not documented in skill at all.** Critical for any mod that needs to modify unit panel, city panel, or other core UI.
2. **`RequiresPopulation="false"` on Districts** — Districts that don't consume a population slot for placement. This is the key flag that makes "minor districts" possible — they can be built without growing the city. Skill mentions `RequiresPopulation` but doesn't explain the `false` use case for minor/non-population districts.
3. **`OnePerCity="false"` on Districts** — Allows building multiple instances of the same district in one city. Combined with `RequiresPopulation="false"`, this creates stackable mini-districts. Default is `true` for specialty districts. Not documented as a design pattern in skill.
4. **`COST_PROGRESSION_PREVIOUS_COPIES`** cost model — District cost increases based on how many copies of THAT district already exist in the city. `CostProgressionParam1="2"` = doubles each copy. Different from `COST_PROGRESSION_GAME_PROGRESS` (era-based scaling). This is the canonical model for stackable districts. Not in skill.
5. **`District_CitizenGreatPersonPoints` table** — Districts provide Great Person points per citizen worked. `DistrictType`, `GreatPersonClassType`, `PointsPerTurn`. Author notes a bug: setting to 1 produces 2 in-game. Not documented in skill.
6. **`Coast="true"` on Districts** — District requires coastal placement. `AdjacentToLand="true"` further constrains to coast tiles adjacent to land. Combined with `FreeEmbark="true"`. These column interactions for coastal districts not documented together in skill.
7. **`HitPoints` on Districts** — Districts can have hit points (Garrison has 50), making them targetable/destroyable in combat. Not documented in skill.
8. **Sharing base-game adjacency IDs** — Quarters reuse existing adjacency IDs from base game districts (e.g., `Mine_Production`, `Quarry_Production`, `Mountain_Faith1`-`5`). This means Quarters inherit the exact same adjacency calculations as vanilla districts without redefining them. Saves massive boilerplate and ensures consistency. Not mentioned as a technique in skill.
9. **Quarters giving adjacency TO specialty districts** — `District_Adjacencies` entries on vanilla districts (Campus, Holy Site, etc.) referencing Quarter-specific adjacency IDs. This means specialty districts get bonuses from adjacent Quarters. Bidirectional adjacency: Quarters benefit from adjacency AND provide adjacency to others.
10. **Custom strategic resource with `Frequency="0"`** — Resource never spawns on the map naturally. Only obtainable through modifiers/buildings. Used for Steel as a late-game gate resource. Pattern for purely synthetic resources.
11. **`Resource_Consumption` table** — Defines resource stockpiling behavior: `Accumulate`, `BaseExtractionRate`, `ImprovedExtractionRate`, `StockpileCap`. Not in skill.
12. **Bulk UPDATE removing housing from improvements** — `UPDATE Improvements SET Housing = 0 WHERE ImprovementType = 'IMPROVEMENT_FARM'` etc. — rebalances the base game when Quarters now provide housing instead. Pattern for mod-wide rebalancing of base game values.
13. **`District_ValidTerrains` table** — Restricts which terrain types a district can be placed on. Farmers' Quarter limited to grass/plains/tundra/snow/desert (no water/mountain). Not documented in skill.
14. **Multiple `<Dependencies>` on specific DLC packs** — 14 hard dependencies listed individually by mod GUID. Most aggressive dependency list in the reference set. Pattern for mods that modify DLC-specific content (civ-unique buildings, units, etc.).
15. **`PH_GameCapabilities.xml`** — Separate file for game capability modifications. Distinct from main data files.

**Design patterns directly relevant to CSC:**
- **Quarter district flags:** `RequiresPopulation=false`, `OnePerCity=false`, `Cost=22`, `COST_PROGRESSION_PREVIOUS_COPIES` with param `2` — this is the exact configuration CSC Quarters should start from.
- **Adjacency bidirectionality:** Quarters both receive AND provide adjacency bonuses. Bakers' Quarter should give food adjacency to adjacent districts AND receive bonuses from adjacent resources/districts.
- **Trade route yields per Quarter:** Each Quarter type provides different domestic/international/origin yields via `District_TradeRouteYields`. Creates meaningful trade routing decisions.
- **Citizen yield per Quarter:** `District_CitizenYieldChanges` makes working Quarter tiles yield-specific. CSC should match this.
- **No custom Kinds needed:** Quarters are just regular `KIND_DISTRICT` with different flags. CSC doesn't need to invent a new entity system — standard districts with `RequiresPopulation=false` + `OnePerCity=false` is sufficient.
- **Rebalancing existing improvements:** Housing removed from farms/plantations because Quarters now provide it. CSC may need similar rebalancing depending on design goals.

**Art patterns:**
- 6 ArtDefs: Buildings, Civilizations, Cultures, Districts, Landmarks, StrategicView — comprehensive art coverage for new districts.
- Platform BLPs in both Windows and MacOS with mirrored SHARED_DATA directories.
- `.dep` file loaded via both FrontEnd `UpdateArt` and InGame `UpdateArt`.
- Texture naming: `TEXTURE_DIS_CTY_*` prefix for district city-culture variants. Multiple culture styles per district tilebase.
- Massive texture count (~200 SHARED_DATA textures per platform) — each district has full PBR maps (Albedo, Normal0, Normal1, Gloss, Metalness, Emissive, Opacity, DiffuseTint, FOW) across multiple culture variants.

**Quality patterns:**
- XML for all data (no SQL) — unusual for this scale of mod. Makes the data very readable but sacrifices dynamic generation (no SELECT-based inserts).
- Clear naming: `DISTRICT_FARMERS_QUARTER`, `DISTRICT_MAKERS_QUARTER`, etc. — matches CSC's naming convention.
- Game mode opt-in via `ConfigurationValueMatches` — same pattern as Cities and Towns Mode.

**CSC design divergence:**
- Project Metropolis uses XML for everything; CSC should use SQL for data-driven generation (JNR pattern).
- PM's Quarters have no building prerequisite chains; CSC's are the core mechanic (branching building trees).
- PM doesn't use M&C/product system; CSC does.
- PM has 9 Quarters covering all yield types; CSC has 8 specialized Quarters covering supply chain domains.
- PM's cost scaling (`COST_PROGRESSION_PREVIOUS_COPIES` ×2) may be too aggressive for CSC's design; CSC should test different `CostProgressionParam1` values.

### Sukritact's Oson (Akan) ✅ 2026-03-24

Sukritact. Full civilization mod with the **GamePropertyRanges → art variant** pattern — the key technique for dynamic visual changes based on game state. The Posuban (unique Encampment replacement) visually changes as great works are added to it.

**The GamePropertyRanges → SelectionRule pipeline (THE critical pattern for CSC art):**

The complete flow for dynamically selecting art assets based on game state:

1. **Lua sets a city property** (`Suk_Akan_Gameplay.Lua`):
   ```lua
   pCity:SetProperty("Suk_PosubanGreatWorks", numGreatWorks)
   -- Also sets plot property for binary encoding (Ruivo pattern)
   m_PlotPropertyHelper:SetProperty(pPlot, "Suk_PosubanGreatWorks", numGreatWorks)
   ```
   Triggered by a custom GameEvent (`GameEvents.Suk_Posuban_GreatWork`) fired from the UI context when great works change.

2. **GamePropertyRanges.artdef** defines a Classifier:
   - `Property Source`: `CITY` (reads from city properties, not plot)
   - `Property Name`: `Suk_PosubanGreatWorks` (matches the key used in `SetProperty`)
   - Intervals (named ranges):
     - `SUK_POSUBAN_00`: range [0, 1) — 0 great works
     - `SUK_POSUBAN_01`: range [1, 2) — 1 great work
     - `SUK_POSUBAN_02`: range [2, 3) — 2 great works
     - `SUK_POSUBAN_03`: range [3, 100) — 3+ great works
   - Classifier name: `Suk_PosubanClassifier`

3. **Landmarks.artdef** has multiple TileBase variants for the same building, with `SelectionRule`:
   - Default variant: `DIS_ENC_Suk_Posuban_00`, SelectionRule = `""` (empty = always matches), Priority = 0
   - Variant 1: `DIS_ENC_Suk_Posuban_01`, SelectionRule = `"[CITYPROP:SUK_POSUBAN_01]"`, Priority = 1
   - Variant 2: `DIS_ENC_Suk_Posuban_02`, SelectionRule = `"[CITYPROP:SUK_POSUBAN_02]"`, Priority = 2
   - Variant 3: `DIS_ENC_Suk_Posuban_03`, SelectionRule = `"[CITYPROP:SUK_POSUBAN_03]"`, Priority = 3

4. **Priority ordering**: Higher priority wins when multiple SelectionRules match. The default (Priority 0) is always a fallback. When the city property enters a new range, the matching variant takes over.

5. **SelectionRule syntax**: `[CITYPROP:INTERVAL_NAME]` where `INTERVAL_NAME` matches an interval defined in GamePropertyRanges.artdef. The `CITYPROP` prefix indicates it reads from city-level properties.

**How CSC should use this for the Joinery-near-Harbor example:**
```
-- Lua (gameplay script):
-- On district placement or adjacency change:
local bAdjacentHarbor = CheckAdjacentDistrict(pPlot, "DISTRICT_HARBOR")
pCity:SetProperty("CSC_Joinery_NearHarbor", bAdjacentHarbor and 1 or 0)

-- GamePropertyRanges.artdef:
-- Classifier "CSC_JoineryHarborClassifier"
--   Property Source: CITY
--   Property Name: CSC_Joinery_NearHarbor
--   Interval "CSC_JOINERY_DEFAULT": [0, 1)
--   Interval "CSC_JOINERY_HARBOR": [1, 100)

-- Landmarks.artdef:
-- Default tilebase: CSC_Joinery_Base (no boats), SelectionRule = ""
-- Harbor variant: CSC_Joinery_Harbor (with boats), SelectionRule = "[CITYPROP:CSC_JOINERY_HARBOR]", Priority = 1
```

**Other patterns not in skill:**
1. **`GameEvents.*.Add()` for custom events** — `GameEvents.Suk_Posuban_GreatWork.Add(handler)` — completely custom game events with arbitrary names. The event is *fired* from the UI context via `GameEvents.Suk_Posuban_GreatWork(playerID, data)` and *handled* in the gameplay context. This is the canonical UI→Gameplay bridge for events that can only be detected in UI (like great work slot changes). Not documented in skill.
2. **`Suk_PlotPropertyHelper`** — Reusable Lua library for managing plot properties with change tracking. Uses `include()` pattern. Handles the serialization details. Good example of shared mod infrastructure.
3. **`Suk_BinaryPropertyManager`** — Same Ruivo binary encoding pattern from CH adjacency mod, but packaged as a reusable Lua class. Parameterized with bit count (4 bits = 0-15 range).
4. **`Events.GovernorPromoted.Add()`** — Built-in event for governor promotion. Args: `playerID, governorIndex, promotionIndex`. Not in skill.
5. **`pPlayer:GetInfluence():ChangeTokensToGive(amount)`** — Adds free envoys to the player's pool. Different from `GiveFreeTokenToPlayer` (which targets a specific CS). Not in skill.
6. **`Events.UnitGreatPersonActivated.Add()`** — Fires when a Great Person uses their ability. Args: `playerID, unitID`. The unit is already "dead" (X < 0) by the time this fires. Not in skill.
7. **`pUnit:GetX()` returning -1** — Indicates the unit has been removed from the map (expended). Used as a check for Great Person activation.
8. **`pPlayer:GetTreasury():ChangeGoldBalance(amount)`** — Direct gold adjustment. Not in skill.
9. **`ReportingStatusTypes.DEFAULT`** — Constant for `Game.AddWorldViewText` message type. Not documented.
10. **Multiple ArtDef types in one mod** — 9 ArtDefs covering Buildings, Civilizations, Cultures, FallbackLeaders, GamePropertyRanges, Landmarks, Leaders, UnitBins, Units. Shows the full scope of ArtDefs a complete civ mod needs.

**CSC relevance:** CRITICAL. The GamePropertyRanges pattern is the missing link for contextual art variants. This is how Quarters can visually respond to adjacency, building state, or any other game condition. The Joinery-with-boats concept is directly implementable with this pattern.

### Sukritact's Tourism Overview Screen ? 2026-03-24

Sukritact. Custom UI panel showing tourism vs domestic culture progress for all civs. Adds a hotkey-triggered popup to the LaunchBar. Compact and well-structured � good reference for any custom overview screen.

**Patterns not in skill:**
1. **`InputCategories` + `InputActions` tables** � Registers a custom hotkey category and action in FrontEnd SQL. `CategoryId`, `Name`, `Visible`, `SortIndex` for category; `ActionId`, `CategoryId`, `Name`, `Description`, `ContextId` for action. `ContextId = 'World'` means available during gameplay. Not documented in skill at all. This is how you add configurable hotkeys to the options screen.
2. **`Input.GetActionId("ActionId")`** � Lua function to get the numeric ID for a registered input action. Used in conjunction with `Events.InputActionTriggered` to handle the hotkey. Pattern: `m_ToggleAction = Input.GetActionId("MyAction")` then check in handler. Not in skill.
3. **`Events.InputActionTriggered.Add(handler)`** � Fires when any registered input action is triggered. Handler receives action ID; compare with stored ID to filter. Not in skill.
4. **`UIManager:QueuePopup(ContextPtr, PopupPriority.Low, kParameters)`** � Adds a UI panel to the popup queue with a given priority. `PopupPriority.Low` for non-critical panels. Paired with `UIManager:DequeuePopup(ContextPtr)` to remove. `UIManager:IsInPopupQueue(ContextPtr)` to check. Not in skill.
5. **`LuaEvents.LaunchBar_Resize(sizeX)`** � Custom LuaEvent to notify the LaunchBar that its size has changed after adding a button. Required when adding buttons to the LaunchBar to reflow the layout. Not in skill.
6. **`ContextPtr:LookUpControl("/InGame/LaunchBar/ButtonStack")`** � Navigate from current context to any control in the UI tree by absolute path. Used to get references to LaunchBar controls from within a different context. Not in skill (skill only covers controls within the same context).
7. **`pPlayer:GetStats():GetTourism()`** � Gets the player's total tourism output per turn. Not documented in skill.
8. **`pPlayerCulture:GetTouristsTo()`** � Total foreign tourists visiting the local player. Not in skill.
9. **`pPlayerCulture:GetTouristsFrom(iPlayer)`** � Foreign tourists visiting local player from a specific civ. Not in skill.
10. **`pPlayerCulture:GetLifetimeCulture()`** � Player's total accumulated culture (all-time, not per turn). Not in skill.
11. **`pPlayerCulture:GetTouristsFromTooltip(iPlayer)`** � Returns the tooltip string explaining tourism bonuses from a specific civ. Suk parses this string with `ParseTooltip()` to extract numeric values rather than recalculating them from scratch. Clever � avoids reimplementing tourism formula.
12. **`pLocalPlayer:GetDiplomacy():HasOpenBordersFrom(iPlayer)`** � Checks if local player has open borders from a specific civ. Not in skill.
13. **`pCity:GetTrade():HasTradeRouteFrom(iPlayer)`** � Checks if a city has an active trade route from a given player. Not in skill.
14. **`GameInfo.Governments[iGovernment].OtherGovernmentIntolerance`** � The government's tourism penalty when civs have different governments. Used to calculate conflicting government tourism modifier. Not in skill.
15. **`Suk_InstanceManager` � InstanceManager subclass with settable Context** � Suk wraps InstanceManager to allow creating instances in a specific UI context (not just the current one). Pattern: copy all methods from InstanceManager, override `new` and `BuildInstance` to use a stored `m_Context`. Useful for panels that create instances across context boundaries.
16. **`GameInfo.GlobalParameters.TOURISM_TOURISM_TO_MOVE_CITIZEN.Value`** � Accessing tourism formula parameters from GlobalParameters table directly in Lua. Other useful tourism params: `TOURISM_CONFLICTING_GOVERNMENT_MULTIPLIER`, `TOURISM_OPEN_BORDERS_BONUS`, `TOURISM_TRADE_ROUTE_BONUS`. Not in skill.
17. **`PlayerManager.GetWasEverAliveMajorsCount()`** � Count of all major civs that have ever been alive (including eliminated). Used for tourism calculation scaling. Not in skill.
18. **`UI.DarkenLightenColor(color, amount, maxAlpha)`** � Darkens or lightens a color by an amount. Used to create lighter/darker variants of civ colors for UI elements. Not in skill.

**Quality patterns:**
- `ParseTooltip()` to extract numbers from engine tooltip strings rather than reimplementing game formula � future-proof against formula changes.
- `pPlayer:GetCulture():GetCurrentGovernment()` returns index, then `GameInfo.Governments[index].OtherGovernmentIntolerance` for the tourism penalty � good pattern for accessing per-government data in Lua.
- LaunchBar button added via `ContextPtr:LookUpControl` cross-context reference, then `LuaEvents.LaunchBar_Resize` to reflow.

### JNR Project6T � Unit_Expansion_Future ? 2026-03-24

JNR. Large unit expansion adding future-era units (melee, ranged, siege, cavalry, naval, air) plus matching policies that obsolete existing ones. Clean reference for unit registration, scaling maintenance relative to existing units, policy obsolescence chains, and era-gated unit production modifiers.

**Patterns not in skill:**
1. **Relative maintenance scaling** � `UPDATE Units SET Maintenance = N + (SELECT Maintenance FROM Units WHERE UnitType='EXISTING_UNIT')` � sets new unit maintenance as a fixed offset from an existing comparable unit. Future-proofs against balance patches: if vanilla maintenance changes, the new unit scales with it. Not documented in skill.
2. **`Units_XP2` with `ResourceCost` and `ResourceMaintenanceAmount`** � GS strategic resource requirements. `ResourceCost` = resources consumed on purchase; `ResourceMaintenanceAmount` = per-turn resource upkeep; `ResourceMaintenanceType` = the resource. Not in skill.
3. **`ObsoletePolicies` table** � `(PolicyType, ObsoletePolicy)` � when `ObsoletePolicy` is unlocked, `PolicyType` is no longer available. Used here to make vanilla policies obsolete when JNR's replacements unlock. Allows seamless policy succession without breaking existing saves. Not in skill.
4. **`UPDATE Policies SET Description='...'`** � Patching vanilla policy descriptions mid-mod to add context (here: adding "...no Future units" note to vanilla policies that now have JNR successors). Clean way to inform players of the relationship. Not documented.
5. **`PolicyModifiers` with SELECT copy from existing policy** � `INSERT INTO PolicyModifiers SELECT 'NEW_POLICY', ModifierId FROM PolicyModifiers WHERE PolicyType='VANILLA_POLICY'` � copies all modifiers from an existing policy to a new one. The new policy inherits all existing bonuses automatically, then you add new ones. Elegant for policy successors. Not in skill.
6. **`MODIFIER_PLAYER_CITIES_ADJUST_UNIT_TAG_ERA_PRODUCTION`** � Production bonus for units of a specific promotion class AND era. Args: `UnitPromotionClass`, `EraType`, `Amount`. Used to give production bonuses for Future-era units specifically. The `EraType` filter is the key pattern � only applies to units of that era, not all units of that promotion class. Not in skill.
7. **`ModifierArguments` with `Extra = -1`** � Some modifier types accept an `Extra` column in ModifierArguments. JNR sets it to `-1` for the era-gated production modifiers. Not documented in skill.
8. **`MODIFIER_PLAYER_ADD_CULTURE_BOMB_TRIGGER`** � Grants culture bomb effect when a specific improvement is built. Arg: `ImprovementType`. Used to give culture bomb on building the Seastead improvement. Not in skill.
9. **`MODIFIER_PLAYER_ADJUST_WAR_WEARINESS`** � Adjusts war weariness generation. Args: `Amount` (% change), `Domestic` (1 = applies to domestic weariness), `Overall` (1 = applies to all weariness). Positive = more weariness, negative = less. Not in skill.
10. **`MODIFIER_PLAYER_UNITS_GRANT_ABILITY`** � Grants a unit ability to ALL player units. Arg: `AbilityType`. Used to grant the forward observer / targeting assist ability to all ranged units when a policy is active. Not in skill.
11. **`CITY_HAS_GARRISON_UNIT_REQUIERMENT`** requirement set name � Note the typo (REQUIERMENT not REQUIREMENT) � this is in the vanilla game data. Using it as `SubjectRequirementSetId` on a city modifier to only apply to garrisoned cities. Worth noting the typo so CSC doesn't accidentally use the correctly-spelled version that doesn't exist.
12. **`WMDCapable = 1` on Units** � Nuclear/WMD capability flag. Air bomber with this set can use nuclear weapons. Not in skill.
13. **`Stackable = 1` on air units** � Allows multiple copies of the unit to occupy the same tile. Standard for air units. Not in skill.
14. **`AirSlots = N` UPDATE** � Sets carrier air slot count. Separate UPDATE after INSERT because the column isn't in the main INSERT template. Not in skill.
15. **`PseudoYieldType = 'PSEUDOYIELD_UNIT_NAVAL_COMBAT'`** � Naval/air units need this for the AI to value them correctly. Land units can be NULL. Not in skill.
16. **Conditional INSERT via `SELECT ... FROM Policies WHERE PolicyType='...'`** � `INSERT INTO PolicyModifiers (...) SELECT 'NEW_POLICY', 'NEW_MODIFIER' FROM Policies WHERE PolicyType='OPTIONAL_POLICY'` � inserts a modifier only if another policy exists in the DB. Used for optional dependency on JNR's own siege policy (only adds the modifier if Project6T's siege policy mod is also loaded). Not documented.

**Quality patterns:**
- Maintenance scaling via SELECT is the canonical JNR approach � all his unit expansion mods use it. Ensures new tiers stay balanced relative to vanilla regardless of any vanilla rebalancing.
- PolicyModifiers copy pattern (SELECT from existing) means the new future-era policy automatically inherits ALL bonuses the vanilla policy had, including any from other mods that extended the original policy.
- The `ObsoletePolicies` approach is cleaner than deleting/replacing the vanilla policy � saves are preserved, players can see the policy chain clearly.

### Sukritact's Oceans ✅ 2026-03-25

Sukritact. Major content mod adding a custom game mode with kelp forests, 7 new sea resources (continent-unique luxury distribution), Monopolies & Corporations integration, and a custom temperature lens UI. Uses gameplay scripts for map generation with a Jump Flood Algorithm for continent assignment and Gaussian convolution for temperature mapping.

**Patterns not in skill:**

#### Game Mode Registration (FrontEnd SQL)
1. **`Parameters` table for game mode toggle** — Registers a game mode checkbox in the advanced setup screen. Key columns: `ParameterId`, `Name` (LOC key), `Description` (LOC key), `Domain` ('bool'), `DefaultValue` (0/1), `ConfigurationGroup` ('Game'), `ConfigurationId` ('GAMEMODE_*'), `GroupId` ('GameModes'). Not in skill.
2. **`ParameterCriteria` table** — Conditions that hide/show the game mode parameter. Here used to hide the Oceans toggle when Random game mode is active: `Operator = 'NotEquals'`, `ConfigurationValue = '1'`. Not in skill.
3. **`ParameterDependencies` table** — Dependencies that enable/disable the parameter. `Operator = 'Exists'`, `ConfigurationValue = 'RULESET_EXPANSION_1,RULESET_EXPANSION_2'` — only shows if R&F or GS rulesets are available. Not in skill.
4. **`GameModeItems` table** — Registers the game mode with icon, portrait, background, and sort index. `GameModeType` must match the `ConfigurationId` from Parameters. Not in skill.
5. **`ConfigurationValueMatches` in ActionCriteria** — Modinfo pattern to gate InGameActions behind a game mode being enabled. `Group = 'Game'`, `ConfigurationId = 'GAMEMODE_*'`, `Value = '1'`. Not in skill (skill covers `RuleSet` criteria but not game mode criteria).
6. **Compound ActionCriteria** — Multiple `ConfigurationValueMatches` blocks within one `Criteria` element require ALL conditions to be true (AND logic). Suk uses this for "Oceans mode ON + Monopolies mode ON" compound criteria. Not documented.

#### Map Generation (Gameplay Scripts)
7. **`AddGameplayScripts` modinfo action** — Runs Lua scripts during map generation, after terrain/features but before game start. Scripts execute in load order. Different from `AddUserInterfaces` (UI context) or `ReplaceUIScript` (replaces existing). Not in skill.
8. **`include "ModuleName"` for script dependencies** — Gameplay scripts use `include` to load other Lua modules. Works because `ImportFiles` makes the files available to the Lua loader. The pattern: `ImportFiles` lists utility modules, `AddGameplayScripts` lists the entry point that `include`s them. Not documented.
9. **`Game:SetProperty(key, value)` / `Game:GetProperty(key)`** — Persistent game-level properties that survive save/load. Used as a "run once" guard: `if Game:GetProperty("Suk_Kelp_Spawned") then return end`. Also used to pass data between gameplay scripts and UI contexts via `ExposedMembers`. Not in skill.
10. **`ExposedMembers` table** — Global table shared between gameplay scripts and UI contexts. `ExposedMembers.SukTemperature = tTemperatureMap` makes the temperature data available to the UI lens. Not in skill.
11. **`TerrainBuilder.SetFeatureType(pPlot, featureIndex)`** — Places a feature on a plot during map generation. Not in skill.
12. **`TerrainBuilder.GetAdjacentFeatureCount(pPlot, featureIndex)`** — Counts adjacent tiles with a specific feature. Used for clustering control (kelp likes 1-2 neighbors but not 4+). Not in skill.
13. **`TerrainBuilder.GetRandomNumber(max, reason)`** — Map generation random number generator. `reason` string is for debug logging. Not in skill.
14. **`ResourceBuilder.CanHaveResource(pPlot, resourceIndex)` / `ResourceBuilder.SetResourceType(pPlot, resourceIndex, count)`** — Resource placement during map gen. Not in skill.
15. **`MapConfiguration.GetValue(key)`** — Reads game setup configuration values. `"rainfall"` returns the rainfall slider value; `"resources"` returns resource abundance setting. Used to scale kelp and resource density. Not in skill.
16. **`Map.GetGridSize()`** — Returns `width, height` of the map grid. Not in skill.
17. **`Map.IsWrapX()` / `Map.IsWrapY()`** — Whether map wraps on each axis. Not in skill.
18. **`Map.GetPlotByIndex(index)`** — Gets plot object from 1D index (row-major: `y * width + x`). Not in skill.
19. **`pPlot:GetContinentType()`** — Returns continent index (-1 for ocean). Not in skill.
20. **`GetShuffledCopyOfTable(table)`** — Built-in utility that returns a shuffled copy. Used to randomize kelp placement order. Not in skill.

#### Jump Flood Algorithm (Continent Assignment for Ocean Tiles)
21. **Jump Flood Algorithm (JFA) for Voronoi on hex grid** — `Suk_ContinentJumpFlood.lua` implements JFA to assign every ocean tile to its nearest continent. This creates continent-based ocean zones for unique luxury distribution. Algorithm: iterative passes with decreasing step sizes (powers of 2), each pass propagates nearest-seed information. Hex coordinates converted to pixel space using `sqrt(3)` scaling. O(n log n) vs O(n^2) for brute force. Could be useful for any distance-field problem on the hex grid.

#### Gaussian Convolution (Temperature Mapping)
22. **`Suk_MapConvolution` class** — Reusable 2D convolution system on the hex grid with wrap-aware boundary handling and configurable Gaussian kernels (3x3, 5x5, 7x7). Used to blur terrain type values into a smooth temperature gradient across the map. Pattern: seed grid with values per terrain type -> convolve multiple times -> normalize to [0,1]. Highly reusable for any smooth gradient across the map.
23. **Multi-pass convolution for smooth gradients** — Suk applies convolution 3 times (5x5, 5x5, 7x7) for increasingly smooth results. Progressive kernel sizes act like a cascade of increasingly wide blurs. Not in skill.

#### Custom Lens UI
24. **`UILens.GetOverlay(overlayName)`** — Gets a lens overlay defined in `Lenses.artdef`. Not in skill.
25. **`UILens.CreateLensLayerHash(layerName)` / `UILens.ToggleLayerOn/Off(hash)` / `UILens.SetActive(lensName)`** — Full lens activation chain. Not in skill.
26. **`overlay:SetHighlightColor(bucket, color)` / `overlay:SetPlotChannel(plots, bucket)`** — Assigns colors to plot groups on the overlay. Color created via `UI.GetColorValue(r, g, b, a)`. Used to create a temperature heat map visualization. Not in skill.
27. **Lens button re-parenting** — `Controls.Button:ChangeParent(pLensToggleStack)` moves a button into the MinimapPanel's LensToggleStack. Same pattern as Tourism Overview's LaunchBar button. Not in skill.

#### Feature Registration
28. **`Feature_AdjacentTerrains` generated via SELECT** — `INSERT INTO Feature_AdjacentTerrains SELECT 'FEATURE_SUK_KELP', TerrainType FROM Terrains WHERE Mountain = 0 AND Water = 0` — data-driven, future-proof against new terrains. Not in skill.
29. **`Feature_Removes` table** — Yield received when the feature is removed (harvested). `FeatureType`, `YieldType`, `Yield`. Not in skill.
30. **`Feature_NotNearFeatures` table** — Prevents features from spawning near other features. `FeatureType`, `FeatureTypeAvoid`. Not in skill.
31. **`Resources.SeaFrequency` column** — Controls spawning frequency for sea resources. Separate from land `Frequency`. Not in skill.

#### Monopolies & Corporations Integration (M&C Temp Table Pattern)
32. **`CROSS JOIN` with numbered temp table for bulk great work generation** — `Suk_Resources CROSS JOIN Suk_Resources_GreatWorks` generates 5 great works per resource in one INSERT. Cleaner than JNR's 36-alphanumeric approach.
33. **`Projects_MODE` table** — Links projects to resources for M&C mode. `ProjectType`, `ResourceType`. Not in skill.
34. **`ResourceCorporations` table** — Corporation-tier bonuses per resource. `ResourceType`, `ResourceEffect`, `ResourceEffectText`. Not in skill.
35. **UPDATE RequirementArguments with string concatenation** — `UPDATE RequirementArguments SET Value = Value || ', ' || (SELECT GROUP_CONCAT(...))` — appends new resource types to existing comma-separated requirement values. Additive modification of existing M&C requirement argument values. **Compatibility gold.**

#### Nested Requirement Sets (REQUIREMENT_REQUIREMENTSET_IS_MET)
36. **`REQUIREMENT_REQUIREMENTSET_IS_MET` for OR-of-ANDs** — Creates a requirement that checks if ANOTHER RequirementSet is met. Enables nesting: outer `REQUIREMENTSET_TEST_ANY` contains multiple `REQUIREMENT_REQUIREMENTSET_IS_MET` requirements, each pointing to an inner `REQUIREMENTSET_TEST_ALL`. **Canonical pattern for OR-of-ANDs requirement logic.** Partially in skill but the nested application pattern isn't documented.

#### Custom DynamicModifiers
37. **`MODIFIER_SUK_PLAYER_PLOTS_ATTACH_MODIFIER`** — Custom DynamicModifier: `COLLECTION_PLAYER_PLOT_YIELDS` + `EFFECT_ATTACH_MODIFIER`. Iterates over all plots with yields owned by a player and attaches a child modifier. `COLLECTION_PLAYER_PLOT_YIELDS` not documented in skill.

**Quality patterns:**
- Run-once guard via `Game:SetProperty` prevents duplicate execution on save/load. Essential for gameplay scripts.
- Temperature-based kelp placement creates organic, climate-aware distribution instead of uniform random.
- `GROUP_CONCAT` + string concatenation for additive M&C integration — never overwrites vanilla data, only appends.
- Gaussian convolution library (`Suk_MapConvolution`) is fully reusable for any mod needing smooth gradients.
- JFA for ocean-to-continent assignment is O(n log n) and wrap-aware.
- Adjacent kelp clustering score with diminishing returns (1 neighbor: +175, 2: +100, 3: 0, 4: -100, 5+: -150) creates natural-looking clusters.

**Art patterns:**
- Feature artdefs: `Features.artdef` registers the feature visual; `Clutter.artdef` adds decoration objects; `Overlay.artdef` handles terrain overlay blending.
- Multiple BLP sets (Windows + MacOS) in `Platforms/` directory — required for cross-platform Steam mods.
- `StrategicView.artdef` — strategic view icon definition for the feature.
- `Lenses.artdef` — registers custom lens overlays used by the temperature lens UI.

**Compatibility patterns:**
- `INSERT OR IGNORE INTO Improvement_ValidFeatures` — adds kelp as valid feature for Fishery and Feitoria without breaking if the improvement doesn't exist (e.g., Feitoria only exists with Portugal DLC).
- `DELETE FROM BuildingModifiers WHERE ModifierId IN (...)` before re-inserting — cleanly replaces vanilla building modifiers.
- `UPDATE Improvement_ValidResources SET MustRemoveFeature = 0` — changes vanilla behavior without deleting/re-inserting the row.

### Sukritact's Urban Identities ✅ 2026-03-25

Sukritact, Leugi, CaptainLime, Pouakai. Major game mode adding map "regions" (clusters of terrain/feature types) detected via DBSCAN clustering, each with unique "identities" (city traits with gameplay modifiers). Cities claim regions by being the first to settle in them. Uses custom tables, plot properties, SQL triggers, DBSCAN algorithm, and runtime modifier attachment.

**Patterns not in skill:**

#### Custom Kinds and Tables
1. **`INSERT INTO Kinds (Kind)`** — Registers entirely new Kinds (`KIND_SUK_REGION`, `KIND_SUK_URBANIDENTITY`). These aren't just custom types using existing kinds — they create NEW kind categories. Used for the Types table foreign key relationship. Not in skill.
2. **`CREATE TABLE` (non-temporary, gameplay database)** — Creates permanent gameplay tables (`Suk_Regions`, `Suk_UrbanIdentities`, `Suk_UrbanIdentity_Regions`, `Suk_UrbanIdentity_Modifiers`, `Suk_UrbanIdentity_PlotProperties`). These persist in the game's database and can be queried from Lua via `DB.Query()`. Not in skill (skill only covers INSERT into existing tables and temp tables).
3. **Foreign key constraints with CASCADE** — Custom tables use `FOREIGN KEY ... REFERENCES Types(Type) ON DELETE CASCADE ON UPDATE CASCADE`. If the Type is removed (e.g., by another mod), dependent rows auto-delete. Clean relational design. Not in skill.

#### SQL Triggers for Automatic Compatibility
4. **`CREATE TRIGGER ... AFTER INSERT ON DistrictReplaces`** — SQL triggers that fire when other mods add unique district replacements. Automatically generates adjacency requirements for the replacement district. This means if a civ mod adds a unique district that replaces one Suk references, the adjacency checks automatically support it — **zero manual compatibility work needed**. Creates Requirements, RequirementArguments, and RequirementSetRequirements entries for the new district. Not in skill — this is an extremely powerful pattern.
5. **`WHEN NEW.ReplacesDistrictType IN (SELECT DistrictType FROM ...)`** — Trigger condition that only fires when the new district replacement is relevant to the mod's data. Prevents unnecessary processing. Not in skill.

#### Plot Properties System
6. **`pPlot:SetProperty(key, value)` / `pPlot:GetProperty(key)`** — Per-plot persistent properties (survive save/load). Used to store region membership, identity type, and custom effect state on individual tiles. Different from `Game:SetProperty` (game-level) — this is tile-level storage. Not in skill.
7. **`REQUIREMENT_PLOT_PROPERTY_MATCHES`** — Requirement type that checks if a plot has a specific property value. Args: `PropertyName`, `PropertyMinimum` (or `PropertyValue`). Used to gate modifiers on whether a plot belongs to a specific region/identity. Not in skill.

#### Runtime Modifier Attachment
8. **`pCity:AttachModifierByID(modifierId)`** — Attaches a modifier to a city at runtime via Lua, without needing a BuildingModifiers/CityModifiers SQL row. Modifiers must still be defined in SQL but are dynamically applied by gameplay scripts. Used when cities claim regions — the identity's modifiers are attached to the city. Not in skill.

#### Cross-Context Communication
9. **`ReportingEvents.SendLuaEvent(eventName, data)`** — Sends a custom event from gameplay scripts to UI contexts. Paired with `LuaEvents[eventName](data)` for local dispatch. The dual-send pattern ensures both gameplay and UI listeners receive the event. Not in skill.

#### DBSCAN Clustering Algorithm
10. **`Suk_DBSCAN_Clustering` class** — Full DBSCAN (Density-Based Spatial Clustering of Applications with Noise) implementation for hex grids. Parameters: `MinSamples` (min neighbors for core point), `Epsilon` (max distance for neighbors), `MinSize` (min cluster size), `Dilate` (grow clusters by N tiles). Used to identify natural regions (forests, mountains, etc.) on the generated map. Includes cluster dilation, passability filtering, size-based culling (4-18 tiles), center calculation, and weighted random selection. Not in skill.
11. **Cluster overlap resolution** — After DBSCAN, overlapping clusters are resolved via weighted random selection: rarer region types get priority (frequency^4 weighting), smaller clusters preferred within type. Selected cluster invalidates all overlapping clusters. Not in skill.
12. **Map coverage culling** — After selection, regions covering too much of the map are culled via a weighted scoring function considering region type frequency, local density, and size. Not in skill.

#### Weighted Random Identity Assignment
13. **Frequency-decrement random selection** — Each identity starts with frequency 10. When assigned, frequency decrements by 2. Chance follows `3^(frequency-10) * 3500` curve — first assignments have high chance, subsequent picks of the same identity become exponentially rarer. Ensures diversity. Not in skill.

#### Modinfo Patterns
14. **Empty `<Criteria id="NeverMet" />`** — A criteria with no conditions that is NEVER met. Can be used to include files that should never load as actions but need to be in the Files list. Seen but not used in the current version. Not in skill.
15. **`<References>` for optional dependencies** — `<Mod id="..." title="Sukritact's Oceans" />` in `<References>` means: if this mod is present, load it first so our data can extend it. Different from `<Dependencies>` (required) — references are optional. The mod checks for Oceans' KELP regions and adds KELP-based identities if present. Not in skill.
16. **`priority` attribute on `<File>` elements** — `<File priority="1">...` and `<File priority="2">...` within the same `<UpdateDatabase>` action controls load order. Lower priority loads first. Used to ensure `_AdjacencySetup.sql` (creates temp table and triggers) runs before `_RegionIdentities.sql` (uses them). Not in skill.

#### Custom DynamicModifiers (10 new types)
17. **`COLLECTION_CITY_DISTRICTS`** — Collection type iterating over all districts in a city. Used with various effects: `EFFECT_ATTACH_MODIFIER`, `EFFECT_ADJUST_DISTRICT_BASE_YIELD_CHANGE`, `EFFECT_ADJUST_DISTRICT_YIELD_BASED_ON_ADJACENCY_BONUS`, `EFFECT_ADJUST_DISTRICT_YIELD_CHANGE`, `EFFECT_ADJUST_TRADE_ROUTE_CAPACITY`. Not in skill.
18. **`COLLECTION_OWNER`** — Collection type targeting the city owner. Used with `EFFECT_DISTRICT_ADJACENCY`, `EFFECT_TERRAIN_ADJACENCY`, `EFFECT_ADJUST_IMPROVEMENT_VALID_TERRAIN`, `EFFECT_ADJUST_BUILDING_PRODUCTION`, `EFFECT_ADJUST_DISTRICT_PRODUCTION`. Not in skill.

#### Gameplay Events
19. **`Events.ImprovementAddedToMap.Add(handler)`** — Fires when an improvement is built. Handler receives `(iX, iY, iImprovement, iOwner)`. Used for "Rich Soil" identity: 33% chance to spawn a random resource when a farm is built on a plot with this identity. Not in skill.
20. **`GameEvents.CityBuilt.Add(handler)`** — Fires when a city is founded. Handler receives `(iPlayer, iCity, iX, iY)`. Not in skill.
21. **`Events.CityRemovedFromMap.Add(handler)`** — Fires when a city is destroyed or captured. Handler receives `(iPlayer, iCity)`. Not in skill.
22. **`Game.GetRandNum(max, reason)`** — Gameplay random number generator (different from `TerrainBuilder.GetRandomNumber` which is map-gen only). Not in skill.

#### SQL Patterns
23. **`CROSS JOIN Yields` with `CROSS JOIN Eras` for bulk modifier generation** — Generates yield-per-era scaling entries programmatically via temp table and cross join. One identity definition generates modifiers for every yield type × every era combination. Not in skill.
24. **Comma-separated multi-values in ModifierArguments** — `YieldType = 'YIELD_PRODUCTION,YIELD_GOLD'`, `Amount = '2,1'` — some modifier types accept comma-separated lists. Each yield type maps to the corresponding amount by position. Not documented in skill.

**Quality patterns:**
- SQL triggers for DistrictReplaces compatibility = automatic UDQ support without hardcoding. Any mod adding a unique district is automatically handled.
- Plot properties as a per-tile data store enables complex spatial game mechanics without new tables.
- DBSCAN with configurable parameters per region type lets each terrain feature cluster naturally at different scales (forests cluster tightly, mountains loosely).
- Region identity assignment uses exponential frequency decay to ensure each game generates diverse identities.
- `pCity:AttachModifierByID` for runtime modifier application means the SQL defines WHAT happens, Lua decides WHEN.

**Compatibility patterns:**
- `<References>` to Sukritact's Oceans — if present, kelp/reef regions are created; if absent, those regions simply don't exist. Zero crash risk.
- SQL triggers on `DistrictReplaces` automatically support civ mods adding unique districts.
- `INSERT OR IGNORE INTO Types` for DynamicModifiers — safe if another mod already registered the same modifier type.
- `include("Suk_RegionDefinitions_", true)` — the `true` parameter loads ALL files matching the prefix, allowing other mods to add region definitions by including a file with the right naming convention.

### JNR 6T Grand Eras ✅ 2026-03-25

JNR. Adds a new "Post-Classical" era between Classical and Medieval, plus many new techs and civics. Massive SQL complexity — the cache-delete-reinsert pattern for era injection is the most sophisticated SQL technique in any reviewed mod. Includes complete UI replacement of tech/civic trees, extensive mod compatibility system, and granular LoadOrder control.

**Patterns not in skill:**

#### Era Injection (Cache-Delete-Reinsert Pattern)
1. **Full table cache + delete + ordered reinsert for index integrity** — The Eras table uses internal row ordering (via ChronologyIndex) that matters for the game engine. To INSERT a new era in the correct position: (a) CREATE cache tables mirroring every table that references Eras, (b) INSERT all data into caches, (c) DELETE from original tables, (d) INSERT the new era, (e) re-INSERT cached data in correct ChronologyIndex order, (f) DROP cache tables. This preserves foreign key relationships while ensuring the new era's position in the internal index is correct. **The canonical pattern for inserting into ordered game tables.** Not in skill.
2. **REINDEX after DELETE** — `DELETE FROM Eras WHERE ChronologyIndex<>1; REINDEX Eras;` — rebuilds the table index after bulk deletion to ensure clean sequential ordering for subsequent inserts. Not in skill.
3. **Multi-column foreign key cache table (`Eras_ForeignKeyCache`)** — Instead of creating a separate cache per table, JNR creates ONE cache table with `ObjectType`, `TableName`, `EraType`, `EraType_B`, `EraType_C` columns. Tables with one era reference use `EraType`; tables with two (e.g., MinimumGameEra/MaximumGameEra) use `EraType` + `EraType_B`; tables with three use all three. Then batch-restores per era per table. Elegant normalization of the cache pattern. Not in skill.
4. **UPDATE to ERA_ANCIENT as temp placeholder** — Before caching, all era references are SET to `ERA_ANCIENT` (which is never deleted). This prevents foreign key violations during the restructuring. After restructuring, cached original values are restored. Not in skill.
5. **`Eras_XP1` / `Eras_XP2` tables** — Expansion-specific era data tables. `Eras_XP1` has `GameEraMinimumTurns`, `GameEraMaximumTurns`, `LiberatedEnvoys`. `Eras_XP2` has `GrievanceDecayRate`, `TensionDecayRate`, `TradeRouteMinimumEndTurnChange`, `EraScoreThresholdShift`. Not in skill.
6. **`INSERT OR IGNORE ... SELECT ... FROM existing_era WHERE EraType='reference_era'`** — Copies expansion-specific era data from an existing era to use as a starting template for the new era, then tweaks values. Pattern: clone the most similar existing era's data, then adjust. Not in skill.
7. **`MomentIllustrations` table** — Maps moment illustrations to eras. `MomentIllustrationType`, `MomentDataType`, `GameDataType` (the era type), `Texture`. Required when adding a new era so moments display correctly. Not in skill.

#### Custom Tables for UI Support
8. **`CREATE TABLE IF NOT EXISTS EraRolloverFrames`** — Custom permanent table for UI data (tech/civic tree era frame textures). Created by the gameplay database, read by the UI replacement Lua. Pattern: use a custom DB table as a contract between SQL data and UI replacement scripts. Not in skill.

#### Modinfo Patterns
9. **`<ModInUse inverse="1">` in ActionCriteria** — Inverted mod presence check: "this criteria is met ONLY IF this mod is NOT loaded". Used for exclusive unit packs — if Steel & Thunder is loaded, use S&T units; if Warfare Expanded is loaded, use WE units; if NEITHER is loaded, use vanilla units. Not in skill.
10. **Complex multi-mod exclusive criteria** — `<ModInUse>mod_A</ModInUse><ModInUse inverse="1">mod_B</ModInUse>` means "mod A is present AND mod B is NOT present". Used for priority chains where multiple mods might provide the same content. Not in skill.
11. **Extreme LoadOrder range (1 to 10000005)** — JNR uses LoadOrder values spanning 7 orders of magnitude to ensure precise execution order. Era data at 1-2, unlocks at 13000, diplomacy at 33000, late-load at 10000005. The late-load ensures wonders are re-assigned AFTER all other mods have added their content. Not in skill (skill mentions LoadOrder but not this extreme range pattern).
12. **Separate FrontEnd and InGame update paths** — StartEras config runs in FrontEnd only, while gameplay data runs InGame only. The separation ensures the game setup screen shows correct era options while gameplay gets the full restructured tree. Not in skill.

#### GlobalParameters Modification
13. **`UPDATE GlobalParameters SET Value = Value+N`** — Relative adjustment of global game parameters. `CITY_GROWTH_MULTIPLIER` increased by 2, `CITY_GROWTH_EXPONENT` by 0.1 to account for the extended game length from the extra era. Additive rather than absolute — compatible with other mods adjusting the same parameters. Not in skill.

#### StartEras System
14. **StartEras tables** — `StartEras`, `MajorStartingUnits`, `BonusMinorStartingUnits`, `StartingBoostedCivics`, `StartingBoostedTechnologies`, `StartingBuildings`, `StartingCivics`, `StartingGovernments` — all the tables that define what players start with when beginning in a later era. Complete set not documented in skill.

**Quality patterns:**
- The cache-delete-reinsert is the ONLY safe way to add a new era. Direct INSERT fails because the internal index ordering matters, and there's no way to specify position.
- `ModInUse inverse` chains create a clean priority system for exclusive content packs without requiring the mods to know about each other.
- ForeignKeyCache consolidating multiple tables into one cache is brilliant engineering — reduces the number of temp tables from ~15 to ~1 for the era reference problem.
- LoadOrder 10000005 for wonder reassignment ensures this mod runs after ALL other mods, even ones with high LoadOrder values. Future-proof.

**Compatibility patterns:**
- Exclusive criteria chains (`ModInUse` + `inverse`) handle multiple unit expansion mods gracefully.
- `INSERT OR IGNORE` throughout ensures no crashes if referenced content doesn't exist.
- StartEra config in FrontEnd, gameplay in InGame — clean separation prevents setup screen issues.
- Cache-based restructuring preserves all data from other mods that may have modified the same tables earlier in the load order.

### Detailed Map Tacks ✅ 2026-03-25

UI-only mod (no gameplay SQL). Shows yields/adjacency bonuses on map pins. Architecture: multi-file Lua module system with yield calculator, modifier calculator, requirement checker, serialization, and map pin subject manager. Pure `ReplaceUIScript` + `AddUserInterfaces` approach.

**Patterns not in skill:**
1. **`ReplaceUIScript` action type** — Replaces a specific Lua context's script. `<LuaContext>MapPinManager</LuaContext><LuaReplace>mappinmanager_dmt.lua</LuaReplace>`. Different from `ImportFiles` (which adds). This REPLACES the base game script for that context. Not in skill.
2. **`InputCategories` / `InputActions` / `InputActionDefaultGestures` tables** — Custom keybind registration in config XML loaded via FrontEnd. `InsertOrIgnore` elements define categories, actions, and default key bindings. `Input.GetActionId("ActionName")` in Lua retrieves the bound key. Not in skill.
3. **`GameEffects.GetModifiers()` API** — Returns all active modifier object IDs in the game. The modifier calculator iterates ALL modifiers, checks ownership, collection type, effect type, and caches relevant ones per district type. This is the canonical way to read the live modifier state from UI Lua. Not in skill.
4. **`GameEffects.GetModifierActive(objId)`** — Checks if a modifier is currently active (conditions met). Not in skill.
5. **`GameEffects.GetModifierOwner(objId)`** — Gets the owner object ID of a modifier. Not in skill.
6. **`GameEffects.GetModifierDefinition(objId)`** — Returns the modifier definition including `.Id` and `.Arguments` table. Not in skill.
7. **`GameEffects.GetModifierSubjects(objId)`** — Returns the subjects (target objects) of a modifier. Not in skill.
8. **`GameEffects.GetObjectName(objId)` / `GetObjectType(objId)` / `GetObjectString(objId)` / `GetObjectsPlayerId(objId)`** — Object introspection API for the GameEffects system. `GetObjectType` returns `LOC_MODIFIER_OBJECT_CITY`, `LOC_MODIFIER_OBJECT_DISTRICT`, etc. Not in skill.
9. **`GameEffects.GetModifierOwnerRequirementSet(objId)` / `GetRequirementSetState(rsId)`** — Checks if the owner requirement set of a modifier is "Met". Used to filter modifiers whose owner conditions aren't satisfied. Not in skill.
10. **`PlayerConfigurations[playerID]:SetValue(key, serializedTable)` / `:GetValue(key)`** — Player configuration as a key-value store for custom mod data that persists with the save game and syncs in multiplayer via `Network.BroadcastPlayerInfo()`. Not in skill.
11. **`Network.BroadcastPlayerInfo()`** — Broadcasts player configuration changes to all clients in multiplayer. Used after updating map pin data to sync yield displays. Not in skill.
12. **`PlayersVisibility[playerID]:IsRevealed(plotIndex)`** — Checks if a specific plot is revealed to a player. Used to hide information about unexplored tiles. Not in skill.
13. **`pPlayer:GetResources():IsResourceVisible(resourceHash)`** — Checks if a resource type is visible to the player (has the tech to reveal it). Uses the `Hash` field from `GameInfo.Resources`. Not in skill.
14. **`Cities.GetPlotPurchaseCity(x, y)`** — Gets the city that owns a specific plot. Used to check religion beliefs for the city at a pin location. Not in skill.
15. **`RiverManager` API** — `RiverManager.GetNumRivers()`, `.GetRiverByIndex(i, "edges")`, `.GetRiverForFloodplain(x,y)`, `.GetFloodplainPlots(riverTypeId)`, `.GetRiverNameByType(typeId)`, `.GetRiverName(plot)`, `.CanBeFlooded(plot)`. Comprehensive river system API for dam placement validation. Not in skill.
16. **`Events.LoadGameViewStateDone.Add(handler)`** — Engine event that fires when the game view is fully loaded. `LocalPlayerTurnBegin` doesn't fire on initial load, so this is needed for first-load initialization. Not in skill.
17. **`Events.BuildingAddedToMap.Add(handler)`** — Fires when a building (wonder) is placed on the map. Args: `(plotX, plotY, buildingIndex, playerID)`. Not in skill.
18. **`Events.FeatureRemovedFromMap.Add(handler)`** — Fires when a terrain feature is removed. Args: `(posX, posY)`. Not in skill.
19. **`Events.ImprovementChanged.Add(handler)` / `ImprovementAddedToMap` / `ImprovementRemovedFromMap`** — Improvement lifecycle events. Not in skill.
20. **`Events.PlotVisibilityChanged.Add(handler)`** — Fires when a plot's visibility changes for the local player. Args: `(posX, posY, visibilityType)`. Not in skill.
21. **`Events.DistrictPillaged.Add(handler)` / `DistrictRemovedFromMap`** — District damage/removal events. Not in skill.
22. **`LuaEvents` for cross-context communication** — `LuaEvents.DMT_UpdatePinYields.Add(handler)`, `LuaEvents.DMT_MapPinAdded.Add(handler)`. Custom named events for inter-Lua-context messaging. The yield calculator context fires events that the map pin manager context listens to. Not clearly documented in skill.
23. **`ExcludedAdjacencies` table** — Game table that excludes specific adjacency bonuses for certain civs/leaders based on traits. DMT reads this to correctly filter adjacency calculations. Not in skill.
24. **`Features_XP2` table** — Expansion 2 feature extensions: `ValidWonderPlacement`, `ValidDistrictPlacement` columns. Used for floodplains/volcanic soil placement validation. Not in skill.
25. **`Automation.GetTime()`** — Returns current time (used for double-click detection in UI). Not in skill.
26. **`UIManager:GetControlUnderMouse(context)`** — Gets the UI control currently under the mouse cursor within a context. Used for double-click detection. Not in skill.
27. **Metalua serialization library** — Full table serialization/deserialization for storing complex data structures in PlayerConfigurations (which only accept strings). The `serialize()` function generates loadable Lua source code strings, `deserialize()` evaluates them. Handles shared references and nested tables. Not in skill.
28. **`BASE_*` function caching for script replacement** — `BASE_MapPinFlag_Refresh = MapPinFlag.Refresh` before overriding. The replacement script includes the original via `include("mappinmanager.lua")`, caches key functions, then overrides them with enhanced versions that call the base. Clean extension pattern. Not clearly documented in skill.
29. **Compatibility chain via `include` fallback** — `local files = {"mappinmanager_cqui.lua", "mappinmanager.lua"}; for _, file in ipairs(files) do include(file); if Initialize then break end end` — tries to load CQUI's version first, falls back to base. Handles mod compatibility by preferring enhanced versions. Not in skill.
30. **`Map.GetAdjacentPlot(x, y, direction)`** — Gets a specific adjacent plot by direction index (0–5). Different from `Map.GetAdjacentPlots(x,y)` which returns all. Not in skill.
31. **`Map.GetPlotXYWithRangeCheck(x, y, dx, dy, range)`** — Gets plot at offset with range validation. Used for "plots within N tiles" calculations. Not in skill.

**Quality patterns:**
- Complete UI module architecture: separate files for yield calc, modifier calc, requirement checking, serialization, and subject management. Clean separation of concerns.
- Multiplayer-safe via PlayerConfigurations + BroadcastPlayerInfo — all clients see the same data.
- Feature/terrain/improvement caching on init for fast adjacency lookups during gameplay.
- The `BASE_*` caching + include pattern is the gold standard for UI script replacement that preserves compatibility with other mods.
- `AffectsSavedGames = 0` — correctly marked since it's UI-only.

**Compatibility patterns:**
- `LoadOrder = 12345` (higher than Map Tacks mod's 12000) ensures DMT loads after base Map Tacks.
- Include fallback chain for CQUI compatibility.
- `InsertOrIgnore` for input config — won't crash if another mod registered the same actions.

### JNR UC — Bonus Resource Improvements ✅ 2026-03-25

Adds unique bonuses per bonus resource. 5 new improvements, extensive mod compatibility via activator system.

**Patterns not in skill:**
1. **`EFFECT_ADJUST_CITY_ALLOWED_IMPROVEMENT`** — Makes a specific improvement type buildable in a city. Args: `ImprovementType`. Used with `COLLECTION_PLAYER_CITIES` and a city-level requirement (city has resource). This gates improvements to specific cities rather than globally. Not in skill.
2. **`MODIFIER_PLAYER_CITIES_ADJUST_IMPROVEMENT_VALID_TERRAIN`** — Adds terrain validity for an improvement, scoped to player cities. Args: `ImprovementType`, `TerrainType`. Used to let Potatoes unlock farms on tundra. Not in skill.
3. **`MODIFIER_PLAYER_ADJUST_FREE_RESOURCE_IMPORT_EXTRACTION`** — Grants free strategic resource extraction (like +1 Iron/Coal) without requiring an improvement. Args: `ResourceType`, `Amount`. Used for Peat bonus. Not in skill.
4. **`MODIFIER_PLAYER_CITIES_ADJUST_UNIT_PRODUCTION_MODIFIER`** — Adjusts unit production percentage in cities. Args: `Amount`. Not in skill.
5. **`MODIFIER_PLAYER_CITIES_ADJUST_BUILDING_PRODUCTION_MODIFIER`** — Adjusts building production percentage in cities. Args: `Amount`. Not in skill.
6. **`MODIFIER_CITY_PLOT_YIELDS_ADJUST_PLOT_YIELD`** — Adjusts yield on specific plots within a city. Args: `YieldType`, `Amount`. Used with complex requirements to target specific terrain+feature+improvement combinations. Not in skill.
7. **`OwnerRequirementSetId` on Modifiers** — The `Modifiers` table has BOTH `SubjectRequirementSetId` (requirements on the target) AND `OwnerRequirementSetId` (requirements on the modifier's owner/source). JNR uses this to gate Peat's coal bonus on having an Industrial Zone: the OWNER (city) must have IZ, the SUBJECT (player) gets free coal. Not in skill.
8. **Activator pattern** — JNR separates improvement/modifier DEFINITIONS from ACTIVATION into separate SQL files. Base definitions create improvements with `TraitType='TRAIT_CIVILIZATION_NO_PLAYER'` (no one can build), then activator files UPDATE the trait to NULL and add resource validity. This allows conditional activation via modinfo criteria — if Wetlands mod isn't loaded, wetlands-specific activators never run. Very clean extensibility pattern. Not in skill.
9. **`REQUIREMENT_PLOT_ADJACENT_IMPROVEMENT_TYPE_MATCHES`** — Checks if a plot is adjacent to a specific improvement. Args: `ImprovementType`. Used for "farm adjacent to pasture" bonus. Not in skill.
10. **`Requirements.Inverse = 1`** — Inverts a requirement check. `REQUIRES_PLOT_HAS_NO_FEATURE_JNR` uses `REQUIREMENT_PLOT_HAS_ANY_FEATURE` with `Inverse=1` to check "plot has NO feature". The Inverse column on Requirements is not documented in skill.
11. **Conditional INSERT from game state** — `INSERT OR IGNORE INTO Modifiers ... SELECT ... FROM Districts WHERE DistrictType IN ('DISTRICT_PRESERVE', 'DISTRICT_LEU_GARDEN')` — only creates the modifier if Preserve or Garden district exists. If neither mod is loaded, the SELECT returns 0 rows and nothing is inserted. Zero crash risk. Brilliant compatibility pattern. Not in skill at this granularity.
12. **`ConfigurationValueMatches` in ActionCriteria** — For game mode detection: checks if a game setup option equals a specific value. Used for Sukritact's Oceans game mode. Different from `ModInUse` (which checks mod UUID). Not in skill.
13. **`UpdateIcons` action type** — Separate action type for icon SQL files. Distinct from `UpdateDatabase` and `UpdateText`. Icons get their own load context. Not documented as a separate action in skill.
14. **`Feature_Floodplains` table** — Game table listing all floodplain feature types. JNR uses `SELECT FROM Feature_Floodplains` to auto-support all floodplain types. Not in skill.
15. **`Feature_Removes` table** — Yield returned when a feature is chopped. JNR clones forest/jungle removal yields for Savannah. Not in skill.

**Quality patterns:**
- The activator/definition separation is architecturally superb: base file creates everything but leaves it locked, per-mod activators unlock and configure. Adding support for a new resource mod = one small activator SQL file + one modinfo criteria block.
- Conditional inserts from game state (`SELECT FROM Districts WHERE DistrictType IN (...)`) provide zero-crash compatibility without any criteria or flag checking.
- `TRAIT_CIVILIZATION_NO_PLAYER` as an initial lock on improvements, then `UPDATE ... SET TraitType=NULL` to unlock. Prevents orphaned improvements if the enabling condition isn't met.

### JNR UC — Specialist Progression ✅ 2026-03-25

Enhances specialist (citizen) yields per building tier. Uses custom permanent table + data-driven yield updates.

**Patterns not in skill:**
1. **`CREATE TABLE IF NOT EXISTS` for permanent custom tables** — `Buildings_JNRUC_SpecialistTiers` table with `BuildingType` and `Yield` columns. Used as a mapping table that drives all subsequent SQL operations. Unlike temp tables (CREATE+DROP), this persists in the gameplay database. Different from the temp-table-for-loops pattern. Not clearly distinguished in skill.
2. **`Building_CitizenYieldChanges` table** — Controls specialist (citizen slot) yield bonuses per building. `BuildingType`, `YieldType`, `YieldChange`. JNR uses UPDATE to increase existing values and INSERT OR IGNORE to add new ones. This is the core table for citizen/specialist yields. Not in skill.
3. **Data-driven bulk UPDATE via subquery** — `UPDATE Building_CitizenYieldChanges SET YieldChange=YieldChange+1 WHERE YieldType='YIELD_PRODUCTION' AND BuildingType IN (SELECT BuildingType FROM Buildings_JNRUC_SpecialistTiers WHERE Yield='YIELD_PRODUCTION')` — one statement updates ALL production-specialist buildings. The custom mapping table drives everything. Not in skill.
4. **Conditional DELETE for mod compatibility** — `DELETE FROM Buildings_JNRUC_SpecialistTiers WHERE BuildingType='BUILDING_FACTORY' AND EXISTS (SELECT * FROM Buildings WHERE BuildingType='BUILDING_JNR_CHEMICAL')` — if JNR's Chemical building exists (from Industry mod), remove Factory from the specialist tier table so it doesn't get double-boosted. Clean deduplication between related mods.
5. **`INSERT OR IGNORE INTO ... SELECT` from custom table** — Uses the custom tier table as a source: `INSERT OR IGNORE INTO Building_CitizenYieldChanges (BuildingType, YieldType, YieldChange) SELECT BuildingType, Yield, 1 FROM Buildings_JNRUC_SpecialistTiers WHERE Yield<>'YIELD_GOLD'`. Creates missing rows from the mapping table. Not documented as a pattern in skill.

**Quality patterns:**
- The permanent custom table as a "driver" for all subsequent operations is cleaner than hardcoding building lists in each UPDATE. New buildings need only one INSERT into the driver table.
- Conditional DELETEs for cross-mod deduplication prevent double-stacking when multiple JNR mods modify the same buildings.
- The `PrereqDistrict` column on Buildings used as a dynamic filter: `WHERE BuildingType IN (SELECT BuildingType FROM Buildings WHERE PrereqDistrict='DISTRICT_AERODROME')`. Auto-includes all aerodrome buildings without hardcoding.

### BD — Savannah ✅ 2026-03-25

Adds a new terrain feature (Savannah) on flat desert. Comprehensive feature creation mod with FeatureGenerator replacement, artdefs, and extensive mod compatibility.

**Patterns not in skill:**
1. **`Features` table INSERT via SELECT clone** — `INSERT INTO Features (...columns...) SELECT 'FEATURE_JNR_SAVANNAH', ..., [columns from FEATURE_FOREST]` — creates a new feature by cloning an existing one's properties and overriding specific values. Ensures the new feature inherits all base properties (movement, defense, sight, appeal, etc.) without manually specifying each. Not in skill.
2. **`FeatureGenerator.lua` replacement** — Map generation script replacement via `<ImportFiles>` for each map type (Base, XP1, XP2, DetailedWorlds, ShufflePlusPlus). The savannah spawning logic is injected into the feature generation phase. Each map script variant gets its own modified copy. Not in skill.
3. **`Feature_ValidTerrains` table** — Restricts which terrains a feature can appear on. `FEATURE_JNR_SAVANNAH` limited to `TERRAIN_DESERT`. Not in skill.
4. **`Feature_Removes` cloning** — `INSERT INTO Feature_Removes SELECT 'FEATURE_JNR_SAVANNAH', YieldType, Yield FROM Feature_Removes WHERE FeatureType='FEATURE_JUNGLE'` — copies chopping yields from jungle to savannah. Not in skill.
5. **`District_RequiredFeatures` table** — Which features a district requires. Used to allow Mbanza on Savannah (since Mbanza requires forest/jungle). Not in skill.
6. **`Improvement_ValidFeatures` for barbarian/goody huts** — `IMPROVEMENT_BARBARIAN_CAMP` and `IMPROVEMENT_GOODY_HUT` need explicit feature validity. Without this, barbarians and goody huts wouldn't spawn on the new feature. Easy to miss. Not in skill.
7. **`Suk_RegionDefinitions_*.lua` integration** — Provides region definitions for Sukritact's Urban Identities when that game mode is active. Uses the naming convention `Suk_RegionDefinitions_[suffix].lua` with `include("Suk_RegionDefinitions_", true)` in the parent mod. Not in skill.
8. **`GAMEMODE_*` ConfigurationValueMatches for game mode detection** — `GAMEMODE_BARBARIAN_CLANS`, `GAMEMODE_APOCALYPSE`, `GAMEMODE_SUK_URBANIDENTITIES` as config IDs. These are checked in ActionCriteria to conditionally load compatibility files. Not in skill.
9. **`RuleSetInUse` criteria** — `RULESET_EXPANSION_1` or `RULESET_EXPANSION_2` as criteria for expansion-specific content. Different from `ModInUse`. Not in skill.
10. **`Feature.Forest = 1` column** — Boolean flag on Features that marks a feature as "forest-like" (affected by lumber mills, Teddy's ability, etc.). Savannah inherits this from FEATURE_FOREST. Not in skill.

**Quality patterns:**
- Feature creation via SELECT clone from an existing feature ensures no properties are accidentally missing.
- Separate FeatureGenerator scripts per map type is the only reliable way to inject new features into map generation.
- Barbarian camp + goody hut feature validity is easy to forget — JNR does it correctly.

**Compatibility patterns:**
- `RuleSetInUse` + `ModInUse` + `ConfigurationValueMatches` combined criteria for expansion-specific game mode content.
- Region definitions file following Suk's naming convention for automatic Urban Identities integration.
- Per-map-script replacement files to handle all common map type variants.

### BD — Denser Vegetation ✅ 2026-03-25 (art-only)
### BD — Mixed Farms ✅ 2026-03-25 (art-only)

Art-only mods (`.dep` files). No new SQL/Lua patterns. Notable: Denser Vegetation uses `ModInUse inverse="1"` criteria to skip loading if the Civ V Skin mod is present (exclusive visual mods).

### JNR UC — Hammurabi Tweak ✅ 2026-03-25

Reworks Hammurabi's leader ability to scale with modded districts. Entirely data-driven via dynamic SQL generation.

**Patterns not in skill:**
1. **`MODIFIER_PLAYER_DISTRICT_ADJUST_SPECIFIC_DISTRICT_GRANT_ENVOYS`** — Grants envoys when a specific district is built. Args: `DistrictType`, `Amount`. Used per-district with dynamic ID generation. Not in skill.
2. **`MODIFIER_PLAYER_CITIES_ADJUST_BUILDING_PRODUCTION`** — Adjusts production of a specific building. Args: `BuildingType`, `Amount`. Not in skill.
3. **`TraitModifiers` table** — Links modifiers to leader/civ traits. `TraitType`, `ModifierId`. JNR DELETEs the base game entries and INSERTs dynamically generated ones. Not documented as insertable in skill.
4. **`BuildingPrereqs` used as negative filter** — `BuildingType NOT IN (SELECT Building FROM BuildingPrereqs)` — selects only tier-1 buildings (those with NO prerequisites). Clean way to identify the first building in each district's chain. Not in skill.
5. **Dynamic modifier generation per-district** — One SELECT generates modifiers for ALL non-city-center, non-wonder, non-unique districts: `'TRAIT_HAMMURABI_FREE_ENVOY_WHEN_' || DistrictType || '_MADE_JNR'`. Combined with the same SELECT for ModifierArguments and TraitModifiers, three SELECTs completely wire up the ability for all districts including modded ones.

**Quality patterns:**
- DELETE base game modifiers + dynamic INSERT is the canonical pattern for reworking leader abilities to support modded content. The base game hardcodes specific districts; JNR's approach auto-includes everything.
- `RequiresPopulation=1` as a filter for specialty districts (distinct from `CityCenter`, `Wonder`, etc.)

### JNR — Community Patch ✅ 2026-03-25

Bug fix compilation. Various exploit patches.

**Patterns not in skill:**
1. **`LeaderPlayable` criteria** — `<LeaderPlayable>Players:Expansion2_Players::LEADER_KRISTINA</LeaderPlayable>` checks if a specific leader is playable in the current configuration. Used to conditionally load fixes only if the affected leader/civ is present. Not in skill.
2. **`any="1"` on Criteria** — `<Criteria id="Sweden" any="1">` means the criteria is met if ANY of the child conditions are met (OR logic). Without `any`, all conditions must be met (AND logic). This is the criteria-level OR equivalent. Not in skill.
3. **`EFFECT_GRANT_UNIT_OF_CLASS_AND_APPLY_ABILITY`** — Grants a unit of a specific class AND applies a unit ability modifier to it. Combined effect type. Not in skill.
4. **`COLLECTION_OWNER` with custom DynamicModifiers** — The patch creates a new `MODIFIER_PLAYER_GRANT_UNIT_OF_ABILITY_WITH_MODIFIER` type using `COLLECTION_OWNER`. Not in skill.
5. **Commented-out `<InGameActions>` sections** — XML comments `<!-- -->` can disable entire action blocks without removing them. Useful for temporarily disabling fixes. Pattern noted but trivial.

---

## Game File Reviews

### Schema: 01_GameplaySchema.sql ✅ 2026-03-25

Cross-checked all major table definitions against `references/sql-patterns.md`. Findings below are columns/tables NOT documented or INCORRECTLY documented in the skill.

#### Modifiers Table — Missing Columns
1. **`Repeatable`** — `BOOLEAN DEFAULT 0`. When 1, the modifier can fire multiple times even if `RunOnce` is set. Not in skill.
2. **`OwnerStackLimit`** / **`SubjectStackLimit`** — `INTEGER`. Limits how many times a modifier can stack on the same owner/subject. Not in skill.
3. **`Permanent`** — In skill but not clearly documented: when 1, the modifier's effects persist even after the modifier source is removed (e.g., unit keeps ability after leaving city).
4. **`NewOnly`** — When 1, modifier only applies to newly created subjects, not existing ones. Not in skill.

#### Requirements Table — Missing Columns
5. **`Inverse`** — `BOOLEAN DEFAULT 0`. Inverts the requirement check (NOT condition). Found in JNR's `REQUIRES_PLOT_HAS_NO_FEATURE_JNR`. In skill but not prominently documented.
6. **`Reverse`** — `BOOLEAN DEFAULT 0`. Different from `Inverse`. Reverses the directionality of a two-entity requirement (swaps subject and context). Not in skill at all.
7. **`Persistent`** — `BOOLEAN DEFAULT 0`. When 1, the requirement result is cached and doesn't re-evaluate dynamically. Not in skill.
8. **`Triggered`** — `BOOLEAN DEFAULT 0`. When 1, the requirement only evaluates in response to a specific event, not continuously. Not in skill.
9. **`Likeliness`** / **`Impact`** — `INTEGER DEFAULT 0`. AI weighting hints for requirements. Not critical for gameplay modding but exist in schema.
10. **`ProgressWeight`** — `INTEGER DEFAULT 1`. Weight for progress tracking on requirements. Not in skill.

#### Buildings Table — Missing Columns
11. **`Entertainment`** — `INTEGER DEFAULT 0`. Direct amenity provision (distinct from Building modifiers). JNR uses this. Not documented in skill's building patterns.
12. **`CitizenSlots`** — `INTEGER` (nullable). Number of specialist citizen slots. Not in skill.
13. **`MustPurchase`** — `BOOLEAN DEFAULT 0`. Building can only be purchased, not produced. Used by JNR for gate buildings. In SKILL-REVIEW but not in skill reference.
14. **`RegionalRange`** — `INTEGER DEFAULT 0`. Range at which building effects spread to nearby cities (Factory, Zoo range). Not in skill.
15. **`GrantFortification`** — `INTEGER DEFAULT 0`. Fortification points granted by the building (walls). Not in skill.
16. **`DefenseModifier`** — `INTEGER DEFAULT 0`. City defense bonus from building. Not in skill.
17. **`AdjacentCapital`** — `BOOLEAN DEFAULT 0`. Wonder must be adjacent to capital. Not in skill.
18. **`AdjacentImprovement`** — `TEXT`. Wonder must be adjacent to specific improvement. Not in skill.
19. **`CityAdjacentTerrain`** — `TEXT`. City must have adjacent terrain of this type. Not in skill.
20. **`GovernmentTierRequirement`** — `TEXT`. Building requires government of specific tier. Not in skill.
21. **`UnlocksGovernmentPolicy`** — `BOOLEAN`. Building unlocks a government policy slot. Not in skill.
22. **`InternalOnly`** — `BOOLEAN DEFAULT 0`. Building is internal/hidden (not shown in UI). Not in skill.
23. **`Capital`** — `BOOLEAN DEFAULT 0`. Building is a capital building (e.g., Palace). Not in skill.

#### Districts Table — Missing Columns
24. **`MaxPerPlayer`** — `REAL DEFAULT -1`. Maximum instances per player (-1 = unlimited). Note: REAL type, not INTEGER. Not in skill.
25. **`TravelTime`** — `INTEGER DEFAULT -1`. Trade route travel time through this district. Not in skill.
26. **`CityStrengthModifier`** — `INTEGER DEFAULT 0`. Bonus to city combat strength from this district. Not in skill.
27. **`AdjacentToLand`** — `BOOLEAN DEFAULT 0`. District must be adjacent to land (Harbor). Not documented as a column in skill.
28. **`CanAttack`** — `BOOLEAN DEFAULT 0`. District can perform ranged attacks (Encampment). Not in skill.
29. **`CaptureRemovesDistrict`** — `BOOLEAN DEFAULT 0`. Capturing the city removes this district entirely. Not in skill.
30. **`FreeEmbark`** — `BOOLEAN DEFAULT 0`. Units in this district get free embarkation. Not in skill.
31. **`TradeEmbark`** — `BOOLEAN DEFAULT 0`. Trade routes through this district embark. Not in skill.

#### Improvements Table — Missing Columns
32. **`OnePerCity`** — `BOOLEAN DEFAULT 0`. Only one of this improvement per city. JNR uses this for Brewery/Clothier. Not in skill.
33. **`AdjacentSeaResource`** — `BOOLEAN DEFAULT 0`. Must be adjacent to a sea resource. Used for Fishery. Not in skill.
34. **`Workable`** — `BOOLEAN DEFAULT 1`. If 0, the improvement tile cannot be worked by citizens. Unusual but exists. Not in skill.
35. **`Domain`** — `TEXT DEFAULT "DOMAIN_LAND"`. Land or sea domain for the improvement. Not in skill.
36. **`NoAdjacentSpecialtyDistrict`** — `BOOLEAN DEFAULT 0`. Cannot be built adjacent to a specialty district. Not in skill.
37. **`RequiresAdjacentLuxury`** — `BOOLEAN DEFAULT 0`. Must be adjacent to a luxury resource. Not in skill.
38. **`RequiresAdjacentBonusOrLuxury`** — `BOOLEAN DEFAULT 0`. Must be adjacent to bonus or luxury. Not in skill.
39. **`Removable`** — `BOOLEAN DEFAULT 1`. If 0, improvement cannot be removed. Not in skill.
40. **`Capturable`** — `BOOLEAN DEFAULT 1`. If 0, improvement cannot be captured. Not in skill.
41. **`ImprovementOnRemove`** — `TEXT`. Improvement that replaces this one when removed. Not in skill.

#### Adjacency_YieldChanges Table — Complete Schema
42. **`Self`** — `BOOLEAN DEFAULT 0`. Adjacency bonus is self-referential (district gives bonus to itself, e.g., Seowon). Not in skill.
43. **`AdjacentSeaResource`** — `BOOLEAN DEFAULT 0`. Adjacency from sea resources specifically. Not in skill.
44. **`AdjacentResourceClass`** — `TEXT DEFAULT "NO_RESOURCECLASS"`. Adjacency from a specific resource class (bonus, luxury, strategic). Not in skill.
45. **`ObsoleteCivic` / `ObsoleteTech`** — Adjacency bonus expires when civic/tech is researched. Not in skill.

#### Features Table — Missing Columns
46. **`Forest`** — `BOOLEAN DEFAULT 0`. Feature counts as "forest-like" (lumber mills, abilities). BD-Savannah uses this. Not in skill.
47. **`AntiquityPriority`** — `INTEGER DEFAULT 0`. Priority for antiquity site generation on this feature. Not in skill.
48. **`Settlement`** — `BOOLEAN DEFAULT 1`. Whether cities can be settled on this feature. Not in skill.
49. **`DangerValue`** — `INTEGER DEFAULT 0`. AI danger assessment for this feature. Not in skill.
50. **`CustomPlacement`** — `TEXT`. Custom placement function name for map generation. Not in skill.

#### Projects Table — Missing Columns
51. **`MaxPlayerInstances`** — `INTEGER` (nullable). Maximum completions per player. JNR uses this for one-shot projects. Not in skill.
52. **`UnlocksFromEffect`** — `BOOLEAN DEFAULT 0`. Project hidden until unlocked by `EFFECT_ADD_PLAYER_PROJECT_AVAILABILITY`. JNR uses this. Not in skill.
53. **`AmenitiesWhileActive`** — `INTEGER`. Amenity bonus/penalty while project is being built. Not in skill.
54. **`PrereqResource`** — `TEXT`. Strategic resource required to start the project. Not in skill.
55. **`WMD`** — `BOOLEAN DEFAULT 0`. Project produces a weapon of mass destruction. Not in skill.
56. **`RequiredBuilding`** — `TEXT`. Building required in the city to start the project. Not in skill.
57. **`VisualBuildingType`** — `TEXT`. Building type whose visual is shown during construction. Not in skill.
58. **`SpaceRace`** — `BOOLEAN DEFAULT 0`. Project is a space race project (science victory). Not in skill.

#### Resources Table — Missing Columns
59. **`Happiness`** — `INTEGER DEFAULT 0`. Amenity provided by luxury resources (default 4 for luxury). Not in skill.
60. **`Clumped`** — `BOOLEAN DEFAULT 0`. Resource spawns in clusters on the map. Not in skill.
61. **`PeakEra`** — `TEXT DEFAULT "NO_ERA"`. Era when this resource is most valuable (strategic resource obsolescence). Not in skill.
62. **`RevealedEra`** — `INTEGER DEFAULT 1`. Era when the resource becomes visible on the map. Not in skill.
63. **`LakeEligible`** — `BOOLEAN DEFAULT 1`. Whether resource can spawn on lake tiles. Not in skill.
64. **`SeaFrequency`** — `INTEGER DEFAULT 0`. Spawn frequency on sea tiles (separate from land Frequency). Not in skill.

### Modifiers.xml — DynamicModifiers Coverage ✅ 2026-03-25

Base game Modifiers.xml contains 463 DynamicModifier types mapping ModifierType → CollectionType + EffectType.

**Coverage:** 347/369 EffectTypes in skill (94%). All 20 CollectionTypes in skill.

**22 Missing EffectTypes (CSC-relevant marked with ⭐):**
- ⭐ `EFFECT_ADJUST_CITY_PROPERTY` — Sets a property on a city. SQL→Lua bridge. Critical for CSC supply chain state tracking.
- ⭐ `EFFECT_ADJUST_PLAYER_PROPERTY` — Sets a property on a player. SQL→Lua bridge. Used by Suk's Urban Identities.
- ⭐ `EFFECT_ADJUST_UNIT_PROPERTY` — Sets a property on a unit. SQL→Lua bridge.
- ⭐ `EFFECT_ADJUST_DISTRICT_TOURISM_ADJACENCY_YIELD_MOFIFIER` — Converts dummy yield adjacency to tourism. The JNR pattern for tourism adjacency. (Note: typo "MOFIFIER" is in the engine.)
- ⭐ `EFFECT_CITY_GRANT_RANDOM_RESOURCE_PRODUCT` — M&C product generation. JNR uses this for corporations.
- ⭐ `EFFECT_ADJUST_PLAYER_VALID_BUILDING` — Makes a building type available to a player. Could gate CSC Quarter buildings.
- `EFFECT_ADJUST_ACTIVE_BUILDING_PRODUCTION` — Production bonus only while building is being actively constructed.
- `EFFECT_ADJUST_CITY_HOUSING_FROM_GREAT_WORKS` — Housing from great works.
- `EFFECT_ADJUST_CITY_STATE_TRADE_ROUTE_FLAT_YIELD` — Flat yield from city-state trade routes.
- `EFFECT_ADJUST_CITY_UNIT_MAX_LEVEL` — Max promotion level for units in a city.
- `EFFECT_ADJUST_FREE_CIVIC_BOOST_WONDER_ERA` / `EFFECT_ADJUST_FREE_TECH_BOOST_WONDER_ERA` — Free boosts from wonders by era.
- `EFFECT_ADJUST_PLAYER_GOLD_INTEREST_PERCENT` — Treasury interest rate.
- `EFFECT_ADJUST_PLAYER_TARGET_CITY_SPY_YIELD_PERCENT` — Spy yield targeting.
- `EFFECT_ADJUST_PLAYER_TOKEN_ON_TRADE_ROUTE_STARTED` — Influence token on trade route creation.
- `EFFECT_ADJUST_PLAYER_TRADE_ROUTE_DESTINATION_YIELD_FOR_SUZERAIN_ROUTE` / `..._ORIGIN_YIELD_FOR_SUZERAIN_ROUTE` — Suzerain trade route yields.
- `EFFECT_ADJUST_TRADE_ROUTE_WATER_RANGE` — Trade route water range extension.
- `EFFECT_ADJUST_UNIT_ERA_STRENGTH_MODIFIER` — Unit strength scaling per era.
- `EFFECT_ADJUST_UNIT_MILITARY_POLICIES_COMBAT_MODIFIER` — Combat bonus from military policies.
- `EFFECT_CITY_REMOVE_OTHER_RELIGIONS` — Removes non-dominant religions from a city.
- `EFFECT_DIPLOMACY_AGENDA_MAGNIFICENCES` — Diplomacy agenda effect.

**Impact assessment:** The skill's sql-patterns.md documents the most commonly used columns but is missing ~60% of the available columns across these core tables. Most critical gaps for CSC:
- **Modifiers.OwnerRequirementSetId** (already used by JNR, critical for CSC supply chain gates)
- **Requirements.Inverse/Reverse** (needed for "NOT" conditions in CSC)
- **Buildings.Entertainment/CitizenSlots/RegionalRange** (CSC buildings will need these)
- **Districts.MaxPerPlayer** (REAL type — could be used for Quarter limits)
- **Improvements.OnePerCity** (CSC Quarter-specific improvements)
- **Adjacency_YieldChanges.Self/ObsoleteTech** (CSC custom adjacency could evolve with techs)
- **Projects.UnlocksFromEffect/MaxPlayerInstances** (CSC supply chain projects)
