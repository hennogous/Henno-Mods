# Specialty Products / Product GreatWorks Notes

Last updated: 2026-06-14

## Current project boundary

Specialty Products are **not active CSC functionality**. The prototype has been moved out of **Civ Supply Chains** and parked in the sibling ModBuddy project **Taxes And Politics** under the local solution workspace:

```text
C:\Users\Shadow\Documents\Firaxis ModBuddy\Civilization VI\Henno Mods
├─ Civ Supply Chains/
└─ TaxesPolitics/
```

CSC should retain only its Monopolies & Corporations support for:

- Industry / Corporation improvements acting as stronger material providers to Quarters.
- Settings/options that remove passive M&C city bonuses.

Taxes And Politics owns the parked Specialty Products slice:

- Setting/action that removes vanilla M&C Product projects when T&P's commissioning projects are used.
- Product GreatWork substrate/shims.
- Bakers Specialty Product resource/GreatWorks/project rows.
- Aristocrat hidden building / Product slots / grant script.
- Product GreatWorks UI handlers.
- Product/Aristocrat icon definitions, textures, and localization.

## Parked files

The June 2026 split parked the implementation as:

- `TaxesPolitics/Data/TAP_PRODUCT_SUBSTRATE.sql`
- `TaxesPolitics/Data/TAP_ARISTOCRAT.sql`
- `TaxesPolitics/Data/TAP_BAKERS_SPECIALTY_PRODUCTS.sql`
- `TaxesPolitics/Text/TAP_SPECIALTY_PRODUCTS_TEXT.sql`
- `TaxesPolitics/Icons/TAP_SPECIALTY_PRODUCTS_ICONS.sql`
- `TaxesPolitics/Lua_UI/GreatWorks/GreatWorksOverview_CSC_Products.lua`
- `TaxesPolitics/Lua_UI/GreatWorks/GreatWorkShowcase_CSC_Products.lua`
- `TaxesPolitics/Lua_UI/Aristocrat/CSC_Aristocrat.lua`
- `TaxesPolitics/Textures/Aristocrat_*`
- `TaxesPolitics/Textures/CSC_GreatWorks_*`

The active CSC project should not contain Product/Aristocrat identifiers such as:

- `GREATWORKOBJECT_PRODUCT` / `GREATWORKSLOT_PRODUCT` when used only for Specialty Products.
- `GREATWORK_PRODUCT_CSC_*`.
- `PROJECT_CREATE_PRODUCT_CSC_*`.
- `BUILDING_CSC_ARISTOCRAT`.
- `NOTIFICATION_CSC_NEW_ARISTOCRAT`.

## Historical test result

A 2026-06-12 probe confirmed that a lean Product path can work without enabling the full Monopolies & Corporations game mode:

- The mod defined the minimal Product object/slot substrate itself.
- Bakers Specialty Products used `GREATWORKOBJECT_PRODUCT`.
- The Aristocrat building provided `GREATWORKSLOT_PRODUCT` slots.
- A Community Extension probe created and assigned a Bakers Specialty Product.
- The Great Works screen opened.
- The granted Product appeared in the Aristocrat building in the capital.
- The Product counted in the Great Works/display-space summary.
- No crash package was produced after placement.

This remains useful evidence for the future Taxes And Politics implementation, not a reason to reintroduce the feature into CSC.

## Product identity finding

Use Civ VI's vanilla Product Great Work identity if this feature is revisited:

- `GREATWORKOBJECT_PRODUCT`
- `GREATWORKSLOT_PRODUCT`

Do **not** use custom Product-like identities such as:

- `GREATWORKOBJECT_CSC_SPECIALTY_PRODUCT`
- `GREATWORKSLOT_CSC_SPECIALTY_PRODUCT`

The custom rows can be valid SQL and could be created through Community Extension probes, but they crashed or behaved unsafely during later game/UI processing. Firaxis Product handling expects the vanilla Product identity.

## Naming convention finding

Firaxis Product UI logic derives resource/icon names from the Product GreatWork pattern:

```text
GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_1
→ RESOURCE_CSC_BAKERS_SPECIALTY
→ ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_BAKERS_SPECIALTY
```

Keep that pattern in mind if Taxes And Politics resumes this implementation.
