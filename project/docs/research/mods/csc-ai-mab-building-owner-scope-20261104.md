# Where the Mill's player-wide scope came from

4 November 2026. Read-only provenance review before implementing Henno's newly
confirmed **local Quarter Mill bonus**. This answers whether the prior scope
was an MAB defect or CSC's use of its configuration. No reference-mod file,
native target, installed package or game state was changed by this review.

## Answer

**CSC inherited MAB's generic player-wide default by omitting the per-rule
CollectionType.** MAB supports local building effects explicitly. Its compiler
and eligibility helper consistently honour either choice; the local tutorial
documents both. The prior remote-city behavior was therefore a CSC integration
and design mismatch, not evidence that MAB ignored an authored local scope.

That gameplay-scope mismatch is separate from the native AI's phantom encoding
forecast. Merely changing PLAYER_DISTRICTS to CITY_DISTRICTS can fix where an
actual attachment is applied, but it still gives the hypothetical interpreter
an actual district context for all omitted-gate encoding bits.

## Source identities

- Read-only local reference repository:
  `Documents/My Games/Sid Meier's Civilization VI/Mods/NEW_ADJACENCY_BONUS_BY_RUIVO`.
  Working branch `test/all-features`, clean, HEAD
  `d852b8466cf7152f4fd76cacec5fa8c2084d7c0a`.
- Its existing upstream-tracking `origin/main` is
  `ab4fe6803ac02d051635d29bb2ef756f37168e52`, remote
  `https://github.com/revoltl/NEW_ADJACENCY_BONUS_BY_RUIVO.git`.
  No fetch or reference change was made. This is a pinned upstream snapshot,
  not a claim about the remote's latest head. Web retrieval returned cache
  misses; the conclusions use the local Git objects and source instead.
- Pre-fix CSC source inspected at
  `94d97a119a49c8ed28731358884b36b91dd2d32a`.
  Later implementation changes must not be read back into this provenance.

## 1. The generic schema default is player-wide

Both pinned MAB versions define:

```sql
CollectionType TEXT NOT NULL DEFAULT 'COLLECTION_PLAYER_DISTRICTS'
```

The same row also defaults ModifierOwner to DistrictModifiers. The schema does
not dynamically switch CollectionType to CITY_DISTRICTS merely because an
author sets ModifierOwner to BuildingModifiers.

Here "default" means an omitted column. An explicit NULL violates NOT NULL;
an explicit empty string is not the default and does not select MAB's CITY,
PLAYER or ALL wrapper branch. The CSC Mill rows omitted the column entirely.

Source: `NEW_ADJACENCY_BONUS_BY_RUIVO_CORE_TABLE.sql`; local lines51–55,
upstream-tracking lines45–49. Git blobs for that file are
`e9da10468b0f8edce8a7f96ae1df94768945dbbc` (local integration) and
`4c7fd0651a9fda8517297a4647eedaffcc689a3d` (upstream-tracking).
The local exact-byte SHA-256 is
`012029adfc026bf8afec88e29bd251116f109074e6835ca8f82547d867eafa01`.

## 2. Local and global building scopes are deliberate supported options

In `NEW_ADJACENCY_BONUS_BY_RUIVO_CORE_INSERT.sql`, the non-district-source
wrapper generator selects:

| Authored CollectionType | Generated wrapper's collection |
| --- | --- |
| COLLECTION_CITY_DISTRICTS | Districts belonging to the source city |
| COLLECTION_PLAYER_DISTRICTS | All districts belonging to the player |
| COLLECTION_ALL_DISTRICTS | All districts in the game |

It separately attaches that wrapper through BuildingModifiers when the source
is a building. There is no fallback from a requested CITY collection to PLAYER.
The local compiler's exact-byte SHA-256 is
`4e943cfefcab59279211b8c9152f1c892637bf44a287d764d354cc81d95e0f16`.

The corresponding `RUIVO_STAT_MODULE_GP.lua` eligibility helper agrees:
BuildingModifiers with CITY checks the recipient city for the building;
PLAYER checks whether the player has that building in any city. Both the
local integration and pinned upstream-tracking helper have these branches.
The local helper's exact-byte SHA-256 is
`c511125805f34867e479bb874ba0379321cbcd5e9564c19bf5f6013ee17ad141`.

The local English tutorial's ModifierOwner table explicitly gives both building
forms: CITY for the building's city, PLAYER for all player districts, with
Wonders as a global example. That is consistent with the code. It does not
describe all building rules as inherently local.

## 3. CSC omitted the override for both Mills

The historical, now-unregistered
`Civ Supply Chains/Lua_UI/Ruivo_Adjacencies/CSC_Ruivo_AdjacencyProcessor.sql`
inserts both
`CSC_BAKERS_WIND_MILL_PRODUCTION_FROM_HILLS` and
`CSC_BAKERS_WATER_MILL_PRODUCTION_FROM_RIVER` with
ModifierOwner=`BuildingModifiers` and the appropriate WhoIsTheOwner.
**Neither INSERT includes CollectionType.** Both consequently take the
schema's player-wide default.

CSC's independent bundled implementation preserved the same default in
`CSC_AdjacencySchema.sql` and omitted the same override in its generated Mill
rows. Its compiler selects the player-wide attach wrapper for that value, and
its shared Lua `IsEligible` scans the player's cities for the building.
Those layers agreed; changing only one would leave the matcher, previews and
actual application with different scope contracts.

The [bundled adjacency implementation record](../../integrations/csc-adjacencies.md)
explicitly retained the authored collection and previously tested remote-city
Water Mill activation/removal. That was parity with the inherited configuration,
not validation against Henno's newly clarified local intention.

## 4. Consequences for the local repair

The repair should explicitly encode that a Quarter's own city has the matching
Mill, and keep gameplay evaluation, previews and planned-Mill evaluation aligned.
A missing local Mill must not be satisfied by a Mill in another city. The test
needs a positive local control and a remote-only negative control.

The selected repair keeps BuildingModifiers ownership and explicitly selects
CITY collection for both Mill rules. Its Lua eligibility must agree with that
local scope. A planned-Mill evaluation may intentionally substitute the local
future Mill; ordinary actual-state evaluation must not.

The new one-step Wind/three-step Water representation also needs gameplay
parity checks for activation/removal, city transfer or other refresh events,
and multiple local/remote Mills. Player-wide stacking from repeated building
instances is not part of the newly confirmed local bonus contract.

The native forecast correction has its own measurement: confirm that the Mill
building vector no longer owns the old ten-bit generated roots and that its
former 1023-capacity contribution is replaced by one Wind or three Water unit
steps. The unsupported property gate can still be omitted by native analysis;
this representation bounds that omission rather than adding exact site
foresight. A lower forecast alone does not prove local gameplay correctness or
improved AI choices. Native validation of the changed representation remains
pending; the current task is offline only.

## 5. Gameplay and UI district lifecycle checks use different interfaces

The gameplay path can enumerate actual district objects, check lifecycle and
verify the building's stored plot index against this city's Quarter. The UI
path must also work without those indexed APIs or GetBuildingLocation.
City-level building presence is sufficient to identify the OnePerCity
prerequisite, but is not sufficient to establish that the Quarter is complete
and unpillaged.

The shipped Base UI `Panels/ProductionPanel.lua` calls
`cityDistricts:IsPillaged(row.Index)` at line 1996 and
`cityDistricts:IsComplete(row.Index)` at line 2002. `row` is a district
definition. `ToolTips/PlotToolTip.lua` lines 758 and 761 use the same district
type plus an optional plot index. ProductionPanel's exact-byte SHA-256 is
`1527d2fd8b2c82d38c228ba2dd75153b3c0bf721c934d1f7cc9cc9ddf98d337f`;
PlotToolTip's is
`fd73dda3ef4e98c69ab75bffe57e17610c226814c97fa98d103cac27a392f1c4`.

Read-only decompilation of the unchanged XP2 reference binary
`324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`
confirms Cache Lua ICityDistricts `lIsPillaged` at RVA `0x68eea0` and
`lIsComplete` at `0x68ed50`: both read the district type from Lua argument 2,
accept an optional numeric plot index from argument 3 (default -1), and return
a Boolean. The manager-only UI test must omit indexed district methods and
building-location methods so it cannot accidentally test only the gameplay
branch.

The first focused test adapter still exposed indexed gameplay district objects
when labelled UI, which concealed this branch. An independent manager-only Lua
fixture reproduced eligibility on a pillaged Quarter. The corrected source now
checks the two supported lifecycle methods in its manager fallback; the revised
UI fixture omits indexed methods and all location APIs. Independent rerun of
all nine focused SQL/Lua 5.1 tests against the immutable MAB database passed,
including pillage, incompleteness, repair, exact gameplay locations, and numeric
versus HavokScript integer tags. Reviewed Core SHA-256:
`5f193144b308c3d01f52d992b710336cfe3d5050ccf8143f38af14d11e2a7eed`;
focused test SHA-256:
`de4a81ce3bfa07a98c3ea2c1d66b81335d517eb3a074532faf50cba1b15f3639`.
These are offline source checks, not a live engine or saved-game result.

## Evidence preservation

The pinned sources, scope excerpts and a file manifest are retained under
`Desktop/Codex/csc-mab-owner-scope-20261104/`. Reference source remains read-only.
The review did not launch, load, attach, edit the MAB repository, fetch remotes,
or change native CE code. The independent fix and its focused validation are
reported separately when complete.
