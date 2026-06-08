# Dynamic Art Properties

CSC uses SQL-driven city properties plus Lua mirroring to drive `GamePropertyRanges` art variants.

## Current Bakers property bridge

Bakers' dynamic building variants use SQL-side source properties mirrored into city-visible Lua/art properties for ArtDef selection.

| Art branch | Source property | Active interval / selection target |
|---|---|---|
| Stage 2 Water/Wind Mill transaction | `CSC_BAKERS_STAGE_2_GRANARY_GROWTH` | `CSC_BAKERS_STAGE_2_GRANARY_GROWTH_ACTIVE` |
| Stage 3 Bakery transaction | `CSC_BAKERS_STAGE_3_EFFECT_HOUSING` | `CSC_BAKERS_STAGE_3_EFFECT_HOUSING_ACTIVE` |
| Stage 4 Café transaction | `CSC_BAKERS_STAGE_4_EFFECT_TOURISM` | `CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ACTIVE` |

SelectionRule syntax:

```text
[CITYPROP:CSC_BAKERS_STAGE_2_GRANARY_GROWTH_ACTIVE]
```

The relevant ArtDef file is:

```text
Civ Supply Chains/ArtDefs/CSC_GamePropertyRanges.artdef
```

The corresponding landmark variants live in:

```text
Civ Supply Chains/ArtDefs/CSC_Landmarks.artdef
```

## SQL remains authoritative

The SQL modifier property is the gameplay source of truth. `Lua_UI/ArtProperties/CSC_ArtProperties.lua` mirrors the SQL-driven value into a direct `pCity:SetProperty(...)` value that `GamePropertyRanges` can read.

This follows Sukritact's Posuban-style art-facing property pattern while preserving SQL-driven gameplay logic.

## ModBuddy action requirement

The Lua bridge must be present in the ModBuddy `InGameActionData` inside:

```text
Civ Supply Chains/Civ Supply Chains.civ6proj
```

Do not maintain a tracked root `.modinfo`; the real `.modinfo` is generated into the built mod output and is not versioned here.

## Refresh events

To avoid art only updating on the next turn, `CSC_ArtProperties.lua` refreshes on immediate hooks for every moving part in the relevant transaction requirements:

- building changes/removal/construction;
- city production completion/update;
- district add/remove/pillage;
- improvement add/change/remove/pillage;
- resource add/change/remove;
- city tile ownership;
- city transfer/add/remove;
- civic completion;
- builder unit operation completion/deactivation/clearing for repairs.

Plot/building/improvement/resource events refresh all cities for the affected player because the affected Bakers' Quarter can be adjacent to the city or plot that changed.

## Variant ownership rule

For art properties that must light up the Quarter owner's city, avoid attaching the SQL source property from the Quarter building to an adjacent subject district if cross-city adjacency is valid. That pattern sets `MODIFIER_SINGLE_CITY_ADJUST_PROPERTY` on the subject district's city.

Use inverse receiver-to-Quarter attach modifiers instead:

- Stage 2 Mill art: `BUILDING_GRANARY` owns `MOD_CSC_BAKERS_STAGE_2_PROP_ATTACH_BAKERS_WATER` / `_WIND`; subject reqsets find adjacent Bakers' Quarters with Water/Wind Mill.
- Stage 3 Bakery art: `BUILDING_MARKET` / `BUILDING_SUKIENNICE` own `MOD_CSC_BAKERS_STAGE_3_PROP_ATTACH_BAKERS_QUARTER`; `REQSET_CSC_ADJ_BAKERY_STAGE_3_ART` finds adjacent Bakers' Quarters with a Bakery.
- Stage 4 Café art: `BUILDING_ZOO`, `BUILDING_FERRIS_WHEEL`, and LGD's `BUILDING_LEU_CONSERVATORY` own the art attach modifiers; `REQSET_CSC_ADJ_CAFE_STAGE_4_ART` finds adjacent Bakers' Quarters with a Café.

## Timing rule

The art bridge follows the base transactions, not the later unlocked effects. Alternate assets should appear as soon as the adjacent Granary/Market/Zoo/Ferris Wheel/Conservatory transaction exists, even before the stage effect civic and improved-material gates are satisfied.

## Lua callback pitfall

Lua event callback parameters in `CSC_ArtProperties.lua` should stay untyped. `Events.ImprovementChanged` can send payloads that trip Civ VI's Lua runtime type checker when callback arguments are annotated as `:boolean`, even though documented shapes list booleans for final parameters. Keep typed annotations on internal helpers if useful, but leave broad event fan-out handlers plain.

## LGD support

LGD Conservatory support lives in the criteria-gated file:

```text
Civ Supply Chains/ModSupport/ModSupport_LGD.sql
```

The art bridge mirrors the LGD Garden/Conservatory Stage 4 tourism branch with:

```text
MOD_CSC_BAKERS_STAGE_4_PROP_ATTACH_GARDEN
  -> MOD_CSC_BAKERS_STAGE_4_PROP_TOURISM_GARDEN
```

This sets the existing source property `CSC_BAKERS_STAGE_4_EFFECT_TOURISM`, letting `CSC_BAKERS_Cafe_2` activate from the Conservatory path without introducing core references to LGD objects.
