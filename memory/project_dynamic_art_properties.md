# Dynamic Art Properties

## Bakers Stage 2 Granary Growth

Added May 22, 2026: Bakers' Stage 2 Granary growth now has a SQL-side source property and a Lua-set art property for art selection.

- Source property key: `CSC_BAKERS_STAGE_2_GRANARY_GROWTH`
- Lua/art property key: `CSC_BAKERS_STAGE_2_GRANARY_GROWTH_ART`
- Active interval: `CSC_BAKERS_STAGE_2_GRANARY_GROWTH_ACTIVE`
- SelectionRule syntax: `[CITYPROP:CSC_BAKERS_STAGE_2_GRANARY_GROWTH_ACTIVE]`
- Source: parallel `MODIFIER_SINGLE_CITY_ADJUST_PROPERTY` modifiers attached with the same owner/subject gates as `MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WATER` and `MOD_CSC_BAKERS_STAGE_2_EFFECT_GROWTH_WIND`
- ArtDef file: `Civ Supply Chains/ArtDefs/CSC_GamePropertyRanges.artdef`

The SQL modifier property remains the source of truth, but `Lua_UI/ArtProperties/CSC_ArtProperties.lua` mirrors it into a direct `pCity:SetProperty(...)` value for `GamePropertyRanges`. This matches Sukritact's Posuban art-facing pattern while preserving SQL-driven gameplay logic.

The Lua bridge must be present in both `Civ Supply Chains.modinfo` and the ModBuddy `InGameActionData` inside `Civ Supply Chains/Civ Supply Chains.civ6proj`; otherwise ModBuddy builds can omit the gameplay script even if the file is listed as content.

To avoid art only updating on the next turn, the bridge refreshes on immediate hooks for every moving part in `REQSET_CSC_STAGE_2_EFFECT_PREREQ` + `REQSET_CSC_ADJ_CITY_CENTER_GRANARY`: building changes/removal/construction, city production completion/update, district add/remove/pillage, improvement add/change/remove/pillage, resource add/change/remove, city tile ownership, city transfer/add/remove, civic completion, and unit operation completion/deactivation/clearing for builder repairs. Plot/building/improvement/resource events refresh all cities for the affected player because the affected Bakers' Quarter can be adjacent to the city or plot that changed.

Session learning was added to the `civ6-modding` skill's `references/art-pipeline.md`: raw numeric art mirror property vs. GamePropertyRanges interval name, hybrid SQL-authoritative/Lua-visible bridge, and reusable event fan-out for future dynamic art properties.

Additional Bakers alternate assets:

- `CSC_BAKERS_Wind_Mill_2` and `CSC_BAKERS_Water_Mill_2` use `CSC_BAKERS_STAGE_2_GRANARY_GROWTH_ACTIVE`, derived from source property `CSC_BAKERS_STAGE_2_GRANARY_GROWTH`.
- `CSC_BAKERS_Bakery_2` uses `CSC_BAKERS_STAGE_3_EFFECT_HOUSING_ACTIVE`, derived from source property `CSC_BAKERS_STAGE_3_EFFECT_HOUSING`.
- `CSC_BAKERS_Cafe_2` uses `CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ACTIVE`, derived from source property `CSC_BAKERS_STAGE_4_EFFECT_TOURISM`.

The new Water Mill/Bakery/Cafe assets were already present in `XLPs/CSC_Tilebases.xlp`; `ArtDefs/CSC_Landmarks.artdef` adds matching priority-1 `BaseVariants` for the corresponding `BUILDING_CSC_BAKERS_*` entries.

LGD Conservatory support lives in the criteria-gated `Civ Supply Chains/ModSupport/ModSupport_LGD.sql` file, not core Bakers SQL. The art bridge mirrors the LGD Garden/Conservatory Stage 4 tourism branch with `MOD_CSC_BAKERS_STAGE_4_PROP_ATTACH_GARDEN` -> `MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_GARDEN`, setting the existing source property `CSC_BAKERS_STAGE_4_EFFECT_TOURISM`. This lets `CSC_BAKERS_Cafe_2` activate from the Conservatory path without introducing core references to LGD objects.

Lua event callback parameters in `CSC_ArtProperties.lua` should stay untyped. `Events.ImprovementChanged` can send payloads that trip Civ VI's Lua runtime type checker when callback arguments are annotated as `:boolean`, even though the documented shape lists booleans for the final parameters. Keep typed annotations on internal helpers if useful, but leave broad event fan-out handlers plain.

For art properties that must light up the Quarter owner's city, avoid attaching the SQL source property from the Quarter building to an adjacent subject district if cross-city adjacency is valid. That pattern sets `MODIFIER_SINGLE_CITY_ADJUST_PROPERTY` on the subject district's city. Use inverse receiver-to-Quarter attach modifiers instead:

- Stage 2 Mill art: `BUILDING_GRANARY` owns `MOD_CSC_BAKERS_STAGE_2_PROP_ATTACH_BAKERS_WATER` / `_WIND`; no owner tech/civic prereq; subject reqsets find adjacent Bakers' Quarters with Water/Wind Mill.
- Stage 3 Bakery art: `BUILDING_MARKET`/`BUILDING_SUKIENNICE` own `MOD_CSC_BAKERS_STAGE_3_PROP_ATTACH_BAKERS_QUARTER`; no owner tech/civic prereq; `REQSET_CSC_ADJ_BAKERY_STAGE_3_ART` finds adjacent Bakers' Quarters with a Bakery.
- Stage 4 Cafe art: `BUILDING_ZOO`, `BUILDING_FERRIS_WHEEL`, and LGD's `BUILDING_LEU_CONSERVATORY` own the art attach modifiers; no owner tech/civic prereq; `REQSET_CSC_ADJ_CAFE_STAGE_4_ART` finds adjacent Bakers' Quarters with a Cafe.

As of May 28, 2026, the art bridge follows the base transactions, not the later unlocked effects. Alternate assets should appear as soon as the adjacent Granary/Market/Zoo/Ferris Wheel/Conservatory transaction exists, even before the stage effect civic and improved-material gates are satisfied.
