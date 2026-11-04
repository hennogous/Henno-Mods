# Why vanilla Water Mill river gating does not replace CSC's Quarter flags

4 November 2026. Read-only native analysis of the pinned XP2 GameCore DLL,
SHA-256 `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`,
image base `0x180000000`. No game execution, FireTuner request, attachment,
installation or gameplay source change formed part of this investigation.

**The ordinary building `RequiresAdjacentRiver` field checks the City Center
plot, not the building's prerequisite district plot.** It is therefore not a
drop-in replacement for CSC's intended Water Mill restriction: a river beside
the Bakers Quarter. The intended Wind Mill remains allowed on river and inland
Quarters; the two real Mills remain mutually exclusive.

## Native field and plot identity

The shipped `Base/Assets/Gameplay/Data/Buildings.xml` line 105 defines vanilla
`BUILDING_WATER_MILL` with `PrereqDistrict="DISTRICT_CITY_CENTER"` and
`RequiresAdjacentRiver="true"`. Its own City Center prerequisite makes the
native check look like building-location gating in vanilla.

The loader at RVA `0x755340` selects both river columns. The definition builder
at `0x7b5eb0` reads zero-based column 41 (`RequiresAdjacentRiver`) and stores it
as Building definition byte `+0x159`, bit `0x08`. Column 44 (`RequiresRiver`)
is a separate bit `0x40` in the same byte.

The normal building status producer at `0x0f61c0`, called by
`City::BuildQueue::CanConstruct` (`0x0f7100`), contains this branch:

```text
if building.RequiresAdjacentRiver:
    plot = City::IInstance::GetPlot(thisCity)
    if plot.IsRiver == false:
        status[1] = 1
        return false
```

Instruction addresses in the pinned binary:

| RVA | Operation |
| --- | --- |
| `0x0f6b34` | Test Building `+0x159` bit `0x08` |
| `0x0f6b3e` | Load the owning city pointer from BuildQueue `+0x1e8` |
| `0x0f6b45` | Call `City::IInstance::GetPlot`, RVA `0x043d80` |
| `0x0f6b4a` | Compare that plot's signed byte `+0x37` with zero |
| `0x0f6b50` | Set hard exclusion status byte `[1]` to one |

`City::IInstance::GetPlot` resolves the city's `+0xc0/+0xc4` coordinates through
the map. `Lua::IMapPlot::lIsRiver` (`0x01e5e0`) tests the same plot byte `+0x37`
greater than zero, independently confirming the river predicate.

The status producer resolves prerequisite districts elsewhere, but this river
branch calls the city plot getter directly. Changing `PrereqDistrict` to the
Bakers Quarter does not redirect it.

| World arrangement | `RequiresAdjacentRiver` alone | Intended CSC Water availability |
| --- | --- | --- |
| City Center riverside; Quarter inland | River check passes | Forbidden |
| City Center inland; Quarter riverside | River check fails | Allowed |
| Both riverside | River check passes | Allowed |
| Both inland | River check fails | Forbidden |

Other technology, prerequisite, exclusion and construction checks still apply.
These are code-derived outcomes, not observed in-game test cases.

## Why a positive flag and a complementary negative flag serve different roles

The native building-status producer makes a concrete distinction:

| Condition | Produced status | Visibility query | Full construction query |
| --- | --- | --- | --- |
| Missing prerequisite building | Populate `+4/+8/+0xc`; clear status `[0]` | Can remain visible | Fails |
| Present mutually exclusive building | Set status `[1]` | Fails | Fails |
| Failed native `RequiresAdjacentRiver` | Set status `[1]` | Fails | Fails |

The prerequisite collection is Building definition `+0x1f8`, loaded from
`BuildingPrereqs` by `0x77a780`. The exclusion collection is `+0x1e0`, loaded
from `MutuallyExclusiveBuildings` by `0x77bfb0`. On finding an owned exclusion,
the status producer jumps to `0x0f6b50`, the same hard exclusion destination.

`CanConstruct` at `0x0f7100` tests status `[1]` **before** its visibility-query
branch. A true visibility parameter then skips the later missing-prerequisite
check; the full query performs that check. Both base Build operation
`CanStart` (`0x6831e0`) and XP2 `CanStart` (`0x74fb00`) forward this parameter
to `CanConstruct` unchanged.

The UI route corroborates the interpretation. Shipped
`Base/Assets/UI/Panels/ProductionPanel.lua` line 2026 obtains
`CanProduce(row.Hash, true)` for list admission; line 2038 calls
`CanProduce(row.Hash, false, true)` for startability and reasons. The Lua
wrapper (`0x68b9e0`), cache forwarding (`0x06afb0`) and game CanProduce
(`0x0f84a0`) preserve the Boolean into the Build operation.
The purchase UI also separates admission from a full check at lines 1730–1732;
this investigation did not reconstruct every purchase-specific gate.

This explains the current two-flag architecture: a River prerequisite enforces
positive availability, while a present NoRiver exclusion can remove an inland
Water Mill from the production list instead of merely leaving it disabled.
The native consumers support that explanation; they do not establish the
original author's intent or prove that every saved flag is synchronized.

Removing only the positive prerequisite does not remove the NoRiver exclusion.
Removing both flag buildings **and all their prerequisite/exclusion links**
also removes this Quarter-river gate unless a replacement native construction
condition is supplied. A UI-only hiding rule does not enforce gameplay, AI
construction or purchase legality.

## The other river field is not an established ordinary-building substitute

`RequiresRiver` is separately consumed by
`Map::Improvement::Builder::CanHaveWonder` (`0x25bad0`), which checks bit `0x40`
against the supplied placement plot's `+0x37` byte. That is a placed-wonder
location route. The inspected ordinary-building status path does not apply
this field to its prerequisite district. This is a bounded finding about the
identified consumers, not a claim that no other consumer exists anywhere.

Neither an arbitrary building RequirementSet replacement nor a native option
to redirect `RequiresAdjacentRiver` to `PrereqDistrict` was established here.
Do not remove the existing gameplay gate on the strength of the vanilla field.
An alternative would need both a supported gameplay gate and a small decisive
live comparison before being treated as equivalent.

## Evidence receipt

Fourteen full function exports are preserved under
`Desktop/Codex/csc-vanilla-watermill-river-20261104/`. Each export filename
starts with its absolute address; `source-manifest.json` records their exact
byte digests and target identity. Manifest SHA-256:
`418c724aa12b3c76c9308bb18dc86fb827664d428220f30331c8954c1b56aca4`.

Shipped source exact-byte SHA-256:

- `Buildings.xml`: `7a540dbe244253788a48e5496bed2fe6afd819fe1ed21a14a9e097241ceb4a13`.
- `ProductionPanel.lua`: `1527d2fd8b2c82d38c228ba2dd75153b3c0bf721c934d1f7cc9cc9ddf98d337f`.

The current source-field and hidden-flag configuration is reviewed separately
by the owning CSC investigation. This report establishes static native
consumers and their control flow; it does not measure gameplay transitions,
saved-game migration, AI forecast changes or a replacement implementation.
