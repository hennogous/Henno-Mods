# CSC Specialty Products Implementation Notes

Last updated: 2026-06-12

## Current decision

CSC Specialty Products should use Civ VI's vanilla Product Great Work identity instead of custom Product-like object/slot types.

Use:

- `GREATWORKOBJECT_PRODUCT`
- `GREATWORKSLOT_PRODUCT`

Do **not** use custom Product identities such as:

- `GREATWORKOBJECT_CSC_SPECIALTY_PRODUCT`
- `GREATWORKSLOT_CSC_SPECIALTY_PRODUCT`

The custom rows can be valid SQL and can even be created through Community Extension probes, but they crashed or behaved unsafely during later game/UI processing. The vanilla Product identity is what Firaxis's Product handling expects.

## Design ownership

Specialty Products are technically viable in CSC, but the fuller version of this functionality probably belongs in the future Taxes & Politics mod rather than in Civ Supply Chains.

Reasoning:

- The Aristocrat is a proto-version of the Landed Elite concept.
- Taxes & Politics introduces the Landed Elite and their Estate district, which is a stronger thematic and mechanical home for elite-owned specialty goods.
- CSC can still keep the current implementation as a working prototype or compatibility bridge.
- If migrated later, CSC should likely remain focused on industry/material flows while Taxes & Politics owns the political/economic elite layer around estates, prestige goods, and Product storage/commissioning.

## Confirmed test result

A 2026-06-12 probe confirmed the lean CSC Product path works without enabling the full Monopolies & Corporations game mode:

- CSC defines the minimal Product object/slot substrate itself.
- Bakers Specialty Products use `GREATWORKOBJECT_PRODUCT`.
- The Aristocrat building provides `GREATWORKSLOT_PRODUCT` slots.
- A CE probe created and assigned a Bakers Specialty Product.
- The Great Works screen opened.
- The granted Product appeared in the Aristocrat building in the capital.
- The Product counted in the Great Works/display-space summary.
- No crash package was produced after placement.

## Database substrate

`Data/CSC_Q_SETUP.sql` provides the minimal Product substrate with `INSERT OR IGNORE` so it coexists with M&C if present:

- `PSEUDOYIELD_GREATWORK_PRODUCT`
- `GREATWORKOBJECT_PRODUCT`
- `GREATWORKSLOT_PRODUCT`
- `GreatWork_ValidSubTypes` mapping from `GREATWORKSLOT_PRODUCT` to `GREATWORKOBJECT_PRODUCT`

`Data/CSC_Q_BAKERS_SPECIALTY_PRODUCTS.sql` defines the Bakers Specialty Product GreatWorks using:

```sql
GreatWorkObjectType = 'GREATWORKOBJECT_PRODUCT'
```

The naming convention matters:

```text
GREATWORK_PRODUCT_CSC_BAKERS_SPECIALTY_1
→ RESOURCE_CSC_BAKERS_SPECIALTY
→ ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_BAKERS_SPECIALTY
```

Firaxis Product UI logic derives resource/icon names from this pattern.

## UI substrate

When the M&C game mode is off, Firaxis does not import its Product-specific Great Works UI handlers. CSC therefore imports its own wildcard handlers:

- `Lua_UI/GreatWorks/GreatWorksOverview_CSC_Products.lua`
- `Lua_UI/GreatWorks/GreatWorkShowcase_CSC_Products.lua`

These are loaded via the base game wildcard includes:

```lua
include("GreatWorksOverview_", true)
include("GreatWorkShowcase_", true)
```

Project wiring:

```xml
<ImportFiles id="CSC_Product_GreatWorks_UI">
  <Properties><LoadOrder>500</LoadOrder></Properties>
  <File>Lua_UI/GreatWorks/GreatWorksOverview_CSC_Products.lua</File>
  <File>Lua_UI/GreatWorks/GreatWorkShowcase_CSC_Products.lua</File>
</ImportFiles>
```

## Icons

`Icons/CSC_BAKERS_ICONS.sql` must provide Product/resource aliases used by the UI:

- `ICON_MONOPOLIES_AND_CORPS_RESOURCE_CSC_BAKERS_SPECIALTY`
- `ICON_RESOURCE_CSC_BAKERS_SPECIALTY`
- `RESOURCE_CSC_BAKERS_SPECIALTY`
- `ICON_GREATWORKOBJECT_PRODUCT` fallback

The fallback avoids relying on M&C icon data when the game mode is disabled.

## Compatibility stance

If a player runs CSC and M&C together, CSC Products may also be movable to vanilla Product slots such as Stock Exchanges and Seaports. This is acceptable. The recommendation remains that CSC does not require M&C and is not balanced around running both systems together.
