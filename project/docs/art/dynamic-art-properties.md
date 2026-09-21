# Dynamic Art Properties

The optional CSC Art Pack uses SQL-driven city properties plus Lua mirroring to drive `GamePropertyRanges` art variants. CSC supplies the gameplay requirement sets; the Art Pack owns all alternate-art bridge files and models. See [the Art Pack split](optional-art-pack-test.md).

## Current timing and local verification

The alternate-art fix was pulled on 12 September 2026 at Henno-Mods `11595de`.
Expanded art follows the full Service activation gate: unlock, required improved
material supply and an eligible adjacent same-owner Service customer. Quarter
buildings own the source-property modifiers, reusing their Service/effect owner
requirement sets. The earlier reverse customer attaches and partial art-only gates
were removed. This was verified by source inspection, not a fresh in-game test.
See the [building art plan](quarter-building-art-plan.md#expanded-art).

## Current Bakers property bridge

Bakers' dynamic building variants use SQL-side source properties mirrored into city-visible Lua/art properties for ArtDef selection.

| Art branch | Source property | Active interval / selection target |
|---|---|---|
| Stage 2 Water/Wind Mill transaction | `CSC_BAKERS_STAGE_2_EFFECT_GROWTH` | `CSC_BAKERS_STAGE_2_EFFECT_GROWTH_ACTIVE` |
| Stage 3 Bakery transaction | `CSC_BAKERS_STAGE_3_EFFECT_HOUSING` | `CSC_BAKERS_STAGE_3_EFFECT_HOUSING_ACTIVE` |
| Stage 4 Café transaction | `CSC_BAKERS_STAGE_4_EFFECT_TOURISM` | `CSC_BAKERS_STAGE_4_EFFECT_TOURISM_ACTIVE` |

SelectionRule syntax:

```text
[CITYPROP:CSC_BAKERS_STAGE_2_EFFECT_GROWTH_ACTIVE]
```

The relevant ArtDef file is:

```text
CSC Art Pack/ArtDefs/CSC_GamePropertyRanges.artdef
```

The corresponding landmark variants live in:

```text
CSC Art Pack/ArtDefs/CSC_ArtPack_Landmarks.artdef
```

## Tailors' Stage 2 bridge

The Tailors' Stage 2 bridge is complete: Art Pack SQL, the shared Lua mirror,
`GamePropertyRanges`, and the Textile Workshop landmark variant are wired
together.

| Source property | Mirrored art property | Active interval / selection property | Active physical state |
|---|---|---|---|
| `CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION` | `CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION_ART` | `CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION_ACTIVE` | Naval Tradition is unlocked; a same-owner adjacent Harbor has a functioning Lighthouse (or supported replacement), the Quarter contains a functioning Textile Workshop, and the Quarter is adjacent to an improved Base Material. |

Art-facing names follow
`CSC_<QUARTER>_STAGE_<NUMBER>_EFFECT_<EFFECT_CONTENT>_<ART_OR_ACTIVE>`.
`<EFFECT_CONTENT>` is the second-to-last word; here it is `PRODUCTION`.
The completed Tailors wire-up selects `CSC_TAILORS_Textile_Workshop_2` over
the baseline `CSC_TAILORS_Textile_Workshop` when
`[CITYPROP:CSC_TAILORS_STAGE_2_EFFECT_PRODUCTION_ACTIVE]` is true.

The property modifier is attached directly to the Textile Workshop and uses
`REQSET_CSC_TAILORS_STAGE_2_EFFECT_PREREQ`, shared with the Dockmaster effects.
That gate includes `CIVIC_NAVAL_TRADITION`, improved Base Material supply and a
collection-count check for an eligible adjacent Harbor/Lighthouse customer.
The old Tailors contract still points at CSC-owned bridge files and requires a separate rebaseline before future contract-driven bridge work.

## SQL remains authoritative

The Art Pack SQL modifier property is the art-state source of truth. `CSC Art Pack/Lua_UI/ArtProperties/CSC_ArtProperties.lua` mirrors the SQL-driven value into a direct `pCity:SetProperty(...)` value that `GamePropertyRanges` can read.

This follows Sukritact's Posuban-style art-facing property pattern while preserving SQL-driven gameplay logic.

## ModBuddy action requirement

The Lua bridge must be present in the ModBuddy `InGameActionData` inside:

```text
CSC Art Pack/CSC Art Pack.civ6proj
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

## Variant ownership and timing

Attach the source-property modifier directly to the Quarter building so the property
belongs to the Quarter owner's city. Reuse the Service/effect `OwnerRequirementSetId`
and prove an eligible adjacent customer exists through its collection-count gate.
Do not restore inverse customer-building art attaches or parallel art-only gates.
Ordinary adjacent-building transactions retain their own independent timing.

## Lua callback pitfall

Lua event callback parameters in `CSC_ArtProperties.lua` should stay untyped. `Events.ImprovementChanged` can send payloads that trip Civ VI's Lua runtime type checker when callback arguments are annotated as `:boolean`, even though documented shapes list booleans for final parameters. Keep typed annotations on internal helpers if useful, but leave broad event fan-out handlers plain.

## LGD support

LGD Conservatory support lives in the criteria-gated file:

```text
Civ Supply Chains/ModSupport/ModSupport_LGD.sql
```

The LGD Service customer path contributes through the current shared Service gate.
Inspect `ModSupport_LGD.sql` with the core Stage 4 prerequisites when changing it;
do not restore the removed Garden-owned reverse property attachment.
