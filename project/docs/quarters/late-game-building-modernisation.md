# Late-game Quarter building modernisation

Research, 24 November 2026. The Apothecary and Pharmacy are the worked example. The unlock, costs and gameplay benefits remain design choices.

## A Pharmacy for every eligible city

Use a second real Stage 3 building and let a permanent player unlock switch the building type. Firaxis uses this pattern when the Owls of Minerva gain the Gilded Vault. The important part is the player modifier that supplies **both** building types. The installed Gathering Storm engine visits existing cities when the player's effective replacement changes.

| Firaxis declaration | Proposed CSC equivalent |
| --- | --- |
| Bank → Gilded Vault in `BuildingReplaces` | Apothecary → Pharmacy. Put Pharmacy in `CivUniqueBuildingType` and Apothecary in `ReplacesBuildingType`. |
| Gilded Vault in `BuildingConditions` with `UnlocksFromEffect=true` | Gate Pharmacy and give it the same Quarter and Herbalist prerequisite as the Apothecary. |
| Governor promotion owns `MODIFIER_PLAYER_ADJUST_VALID_BUILDING` | Attach an instance through `TechnologyModifiers` or `CivicModifiers` to the chosen unlock. |
| `BuildingType=BUILDING_GILDED_VAULT`, `BuildingTypeToReplace=BUILDING_BANK` | Supply the Pharmacy and Apothecary types respectively. |

On the installed Steam XP2 core, the effect records a player-level replacement pair and rebuilds the effective building mapping. When the effective type changes, it checks each owned city for the old building. Where the building exists, native code removes it and creates the replacement. It also has explicit handling for extra Great Work slots and for relocating works. A city without the old building takes a different branch that removes matching old build-queue entries. The inspected branch contains no transfer of investment to a queued Pharmacy. This is a reason to test a nearly finished Apothecary when selecting the unlock.

The intended result is an existing Apothecary becoming a Pharmacy without spending city production, while an eligible city building Stage 3 later receives the Pharmacy as its normal build or purchase choice. Verify fresh production and purchase lists with the CSC rows, including a second player who has yet to reach the unlock. The building, condition and modifier machinery exists in the base schema/data and the XP2 core. Secret Societies supplies the worked example. CSC can author its own rows and test with that mode off.

## A city chooses to refit

Gathering Storm's power-plant conversions provide an ordinary production project. Give the project the chosen tech or civic, the Apothecaries' Quarter as `PrereqDistrict`, and a production cost. In `Projects_XP2`, set `CreateBuilding` to the Pharmacy. In `Project_BuildingCosts`, list only the Apothecary as `ConsumedBuildingType`. The schema requires at least one listed source to start and consumes **every** listed source present on completion. The Apothecary therefore remains in place while the city is working on the project. The completion code iterates the project's building costs, removes the buildings found, then calls the queue's building-creation routine for the destination.

This gives **Modernise the Apothecary** a familiar home in city production. Use it when spending production now for a local benefit is an interesting decision. A city which has never built Stage 3 needs a separate construction rule. A reasonable design is to allow direct Pharmacy construction after the unlock and set mutual exclusions in both directions, as Firaxis does for power plants. Specify whether an empty Quarter can still choose the cheaper historical building. An automatic player-wide replacement on this same unlock would consume the proposed project's source. AI interest in an optional CSC project needs a playtest.

## Keeping one building ID

A contextual label can retain every gameplay attachment. The stock plot tooltip already reads `city:GetBuildings():GetBuildingNameOverride(index)`. The historical native symbol map names a setter and the reference disassembly traces its callers to Heroes & Legends. The shipped Lua and API catalogue inspected here expose the getter. We found no corresponding public Lua setter. Stock production, repairs, city details, general building tooltips, map search and the Civilopedia also contain independent reads of the static building or page name.

For a presentation-only change, a shared CSC UI function can choose a localization key using the **owner** of the building or production preview. Describe both phases on the Civilopedia page, which has no single owning city. Unmodified screens and other UI mods can still display the historical name. An even smaller design is to keep the historic building name and surface the modern activity in a named Service or description.

Gameplay Lua can also remove a building and create another on an explicit host plot. CSC already uses `city:GetBuildings():RemoveBuilding(index)` and `city:GetBuildQueue():CreateBuilding(index, hostPlot)` to reconcile hidden Wonder Services. That code is a fallback for custom city-specific triggers. It demonstrates placement of a proxy building and leaves the continuity of a paid, occupied or pillaged building to separate verification. [Wonder Service reconciler](../../../Civ%20Supply%20Chains/Lua_UI/WonderServices/CSC_WonderServicePlacement.lua) · [Gameplay QA](../workflows/gameplay-qa.md)

## Where it fits in the Apothecaries' Quarter

Prefer the player-wide replacement for a change of profession that follows a discovery across the empire. A distinct Pharmacy gives stock screens, icons, search and Civilopedia an ordinary building record to resolve. Use a local project if cities should decide when to pay for new equipment. For buildings that keep the same name, existing era art and gated effects can carry the entire change.

The Apothecary is the Guilds Stage 3 building. A Pharmacy would inherit its Herbalist exchange, specialist, amenity, Market and Armory transactions, Surgeon eligibility and route role. At Chemistry the **Alchemist** already unlocks the University Pharmacologist. Keep those two jobs distinct. The Quarter's current SQL is parked and has no authored building rows. The common stage registry already allows multiple building types at one stage. Register both IDs and share the authored Stage 3 economics, then check exact-type readers for Services, adjacency, art, notifications and AI. [Quarter design](../../../docs/content/quarters/apothecaries.md) · [Stage registry](../../../Civ%20Supply%20Chains/Data/CSC_Q_ALL_Schema.sql) · [Bakers' two Stage 2 registrations](../../../Civ%20Supply%20Chains/Data/CSC_Q_BAKERS.sql)

For the first playable prototype, advance the unlock normally with one supplied and staffed Apothecary serving an Armory, a second city partway through building one, and a third eligible Quarter with an empty Stage 3. Record both types, host plot, production progress, repair state, assignments and actual effects before and after. The existing city should have exactly one Stage 3 and one set of benefits. Check a pillaged building for an unintended free repair, then check capture by a player on the other side of the unlock and save/reload. CSC gameplay and these player-visible transitions were not exercised in this investigation.

## Source and evidence ledger

Firaxis paths below are relative to the installed Civilization VI game root.

| Question | Evidence and scope |
| --- | --- |
| How does Firaxis declare a player-wide successor? | `DLC/Ethiopia/Data/Ethiopia_SecretSocieties_MODE.xml` lines 466–487, 721–724 and 1042–1051. The example declares the unlock condition, prerequisites, replacement row and two modifier arguments. Base `Assets/Gameplay/Data/Modifiers.xml` lines 1189–1193 declares the owner-scoped effect. Base `Technologies.xml` line 646 and `Civics.xml` line 504 show the unlock attachment tables. All base paths begin with `Base/`. |
| Can Firaxis projects consume ordinary building types? | `DLC/Expansion2/Data/Expansion2_Schema.sql` lines 622–629 and 646–658, `Expansion2_Projects.xml` lines 29–31, 64–66 and 82–91, and `Expansion2_Buildings.xml` lines 445–450. REA found the source and destination rows in the local gameplay DB, SHA-256 `baa9fc982abda0225240a944d6b0a049e77a948cffbc19dd7ff3d7d5560a7d42`. Evidence `ev_cf4f951f5a608e2a2b99da43224f12928e5e87352f50bce7d5971d9026261f0a` and `ev_2b7c7fe4d473f2bb82ab65e10ae75d8e3916bc13d47f4cef8e785564030f83d5`. |
| Which screens read an override? | `Base/Assets/UI/ToolTips/PlotToolTip.lua:774` checks the getter. Compare `Base/Assets/UI/Panels/ProductionPanel.lua:2069`, `Base/Assets/UI/ToolTipHelper.lua:143`, `Base/Assets/UI/Popups/MapSearchPanel.lua:632`, `DLC/Expansion2/UI/Replacements/CitySupport.lua:741`, `DLC/Expansion2/UI/Civilopedia/CivilopediaPage_Building.lua:12` and CSC's `Lua_UI/Lenses/CSC_QuarterTooltip.lua:529`. Coverage is limited to the inspected paths. |
| Where do the native names come from? | The [historical linker map and pinned reference](../research/mods/csc-ai-gamecore-symbol-resource-20261029.md) identify `AddBuildingReplacementOverride`, `ReplaceBuilding`, `PostCreateProject` and the Heroes Manager setter callers. The installed November Steam core has a different digest. Use the installed-build addresses below for the traced behaviour. |

### Native trace on the installed Gathering Storm core

Target `DLC/Expansion2/Binaries/Win64/GameCore_XP2_FinalRelease.dll`, SHA-256 `4de40abf7c739f53c1f3f825863ace84dc220e5a42d87620e56fceaf3fbd4dc8`. All addresses in the table are RVAs in hexadecimal. The labels describe behaviours identified against the named reference. Findings come from static code and data.

| Entry | What the inspected path does |
| --- | --- |
| Valid-building effect initialiser `86fe30`, apply `870820` | The initialiser references `BuildingTypeToReplace`. The virtual apply method forwards the pair to `2640f0`. The reference effect table and the two building arguments distinguish this from other player-validity modifiers. |
| Add player building replacement `2640f0` | After updating the mapping, a change of effective type enters the city loop. At `26421c` it tests old-type ownership, at `2642c8` it calls `ReplaceBuilding`, and at `2642f5` it calls the routine identified as relocating gathered Great Works. The alternate branch at `26432d` calls queue removal. |
| Replace city building `10d670` | Requires the effective mapping to agree, stages extra Great Work slot records, removes the old building at `10d7ae`, calls normal building creation at `10d7f6` and reapplies extra slots. The call uses default placement. Give both types the same host district and verify the result in the city. |
| Remove queued old type `103610` → `0ffc20` | The queue helper removes matching entries and clears the old type's accumulated production field at `0ffea9`. The building progress updater at `1049b0` reads and writes this same indexed array. No credit to the successor appears in this path. |
| Complete city project `101de0` | The building-cost loop calls `HasBuilding` at `101f3d` and removal at `101f5e`. The XP2 destination then goes to `CreateBuilding` at `101fc7`. A separate visual-building mechanism runs in the same function. Use the XP2 destination for the permanent Pharmacy. |
| Name override | The setter at `10e730` matches the named reference body after accounting for relocated operands. Its direct call sites at `634675` and `635dee` correspond to the Heroes Manager's hero-creation and building-override callbacks. The installed core contains the literal Lua getter. A bounded search found neither the setter's Lua literal nor a public `ReplaceBuilding` literal. |

| REA observation on the installed DLL | Evidence IDs |
| --- | --- |
| Initialise and apply | `ev_60eedcbdd754ef3e91eec5382e47301dd9d3fece3f9fd40f1c1925645793df29` and `ev_b5b8fc0fd51e40f7991618e4b1bb2c5a43239c799834c56b895ae9458c0e0935` |
| Visit cities and replace a completed building | `ev_437313408182c017aca4fc241623c60ed2e355d72b42a49e9bf2941ee24791a5` and `ev_73fafd3e68c09c3ad357e3c7fbfb8ef1a0f90f1de365048219bb3dbc62f5d014` |
| Remove old construction and update production | `ev_2bdc956676164fee5e6934a1c37dcaf003e7a83bcab1c55572cf2a94d8ef6198` and `ev_120d254b817336fc3d2c401cb9917b9d8938d380745cda7aaa22bbbbbaa0fbe8` |
| Complete the conversion project | `ev_3f6285004f6a33af1a5d6c6fb78030490df9820b81041a2e6dcd8309661be2a0` |
| Current name-setter references | `ev_68445297170f009230460d79c11d7a32d1ff633fefde0ceab1c45d73830994ec` |

The native Evidence bundle is archived on Shadow under `Desktop/Codex/csc-building-modernisation-20261124-evidence.json`. The source rows, addresses and build digest above permit independent inspection.
