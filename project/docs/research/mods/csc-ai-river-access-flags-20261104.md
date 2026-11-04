# River Access flags: gameplay purpose and indirect AI effects

4 November 2026. Offline source/database audit plus fresh read-only Ghidra review.
No gameplay implementation, installed package, FireTuner, game or native process
was changed. Henno asked to recover the flags' purpose and determine whether the
AI ignores them. [AI-C057]

> Follow-up: Henno confirmed **Water only on rivers; Wind allowed anywhere**.
> The [native gate/UI investigation](csc-ai-watermill-native-river-check-20261104.md)
> explains why both markers serve a purpose: the vanilla flag tests the City
> Center, while positive prerequisite and complementary exclusion separate
> constructibility from hiding. Gameplay code remains unchanged.

## Gameplay logic

The two hidden buildings are implementation markers for the **Bakers Quarter's
river access**, not productive investments. This is SQL-driven; no CSC Lua river
flag grant routine was found in the active source search.

| Mechanism | Current rule |
| --- | --- |
| Automatic grant | The Quarter owns two COLLECTION_OWNER / EFFECT_GRANT_BUILDING_IN_CITY_IGNORE modifiers |
| River marker | Subject requirement REQUIREMENT_PLOT_ADJACENT_TO_RIVER |
| No-river marker | The same requirement with Inverse=1 |
| Water Mill | Engineering, the Bakers Quarter and RIVER_ACCESS prerequisite; excludes NO_RIVER_ACCESS and Wind Mill |
| Wind Mill | Machinery and the Bakers Quarter; excludes Water Mill; **no no-river prerequisite or River Access exclusion** |
| Bakery and Café | Each lists the two Mills as alternative prerequisites; Café does not require Bakery |

Consequently, the declared building relationships allow either Mill at a river
Quarter once the relevant technology is available, but only Wind at a non-river
Quarter. Water also becomes unavailable once Wind is built, and vice versa.
The public description presents Wind as the non-river alternative; it should not
be read as proof that the current SQL forbids Wind on river sites. No restriction
was added during this audit.

The markers have Cost0, Maintenance0, CitizenSlots0, Entertainment0,
MustPurchase1 and no PurchaseYield. They are excluded from Civilopedia and have
XP2 Pillage0. They own no BuildingModifiers and have no Building_YieldChanges in
the frozen loaded database. **Internal implementation marker** describes their
role: their actual Buildings.InternalOnly field is0, not1. MustPurchase and the
missing purchase currency keep them out of ordinary player construction/purchase.

Source anchors in `Civ Supply Chains/Data/CSC_Q_BAKERS.sql`: DistrictModifiers
around312; marker definitions414–443; MustPurchase549; Civilopedia564; XP2 flags611;
BuildingPrereqs627; mutually exclusive rows641; modifier definitions811;
building arguments985; requirement sets1242/1351 and inverse requirements1487.
The frozen optional-mod database independently agrees with these relationships.
These are definition-level checks, not a new native grant/legality experiment.

## They have no direct score in our capture, but are not invisible

The existing [archived component observation](csc-ai-bakers-forecast-components-20261104.md)
measured River Access and No River Access at **0 Q8 in both Delhi and Majapahit**.
CalculateDistrictValues also excludes their own district contribution through
the MustPurchase flag. Neither should be counted as extra economic income.

There are two indirect effects:

1. **River Access is a real prerequisite edge in native definitions.** Fresh
   BuildingValue at RVA52b900, lines439–454, follows the first non-null prerequisite
   chain and multiplies an early subtotal by `1+2*depth`. That loop has no test for
   MustPurchase, zero cost or whether the prerequisite is already present. A
   loaded Water→River Access edge therefore participates in that structural
   heuristic rather than being identified as a free implementation marker.
   With that one-edge chain, the corresponding depth factor is3 versus1 for a
   prerequisite-free Wind. This does **not** multiply the later modifier sum or
   establish a nonzero numerical uplift: the affected early subtotal may be zero.
   The earlier native readiness paths can also inspect missing prerequisites;
   the marker's exact contribution to any measured ETA remains unitemised.
2. **No River Access is in Water's mutual-exclusion list.** Fresh
   CalculateDistrictValues at RVA3dfee0, lines65–78, rejects a building's ordinary
   district contribution if an excluded building is present **or has a lower
   definition index**. In the captured mapping NoRiver138 and Wind139 both precede
   Water140. Either lower-index relationship suffices to exclude Water from that
   district sum even if the excluded building is absent. Wind already supplies
   a separate exclusion, so removing NoRiver alone would not make Water enter
   this pass. This is not a claim that ordinary Water construction is impossible.

The direct-zero results and these indirect paths answer different questions.
Hiding a building, making it free or setting its own value to zero does not make
all references to it disappear from native planning.

## What follows for the next forecast ledger

Keep the gameplay gating intact while attributing the remaining Mill forecast.
Treat the markers as zero-cost implementation state in a CSC economic model;
retain the resulting Water/Wind availability. Inspect the native early subtotal
and mutually exclusive representative separately from genuine Mill benefits.

No gameplay deletion or native filter is implemented here. A correction that
skips markers for economic prerequisite depth must not accidentally bypass the
Water Mill's actual river legality. Changing definition order or deleting only
NoRiver is not a demonstrated complete forecast repair. Henno subsequently confirmed that Wind is allowed anywhere; its existing
availability therefore requires no extra non-river restriction.

## Evidence identity and limits

- Current source reviewed after source commit02145d6 and documentation3c5b9f1.
- Read-only frozen database:
  `Desktop/Codex/csc-adjacencies/mab-DebugGameplay.sqlite`, SHA-256
  `f089f40e721fadc8cb58105d3d7cdf8d4c48db1a0fd9c2788274e640b0d1cd59`.
  Its marker/prerequisite/exclusion rows were checked against current source;
  this is not a claim that it contains the later unit-step Mill compiler.
- Fresh Ghidra target GameCore_XP2_FinalRelease.dll, image base180000000,
  SHA-256 `324c51e9ea3531758842e16c69e6cddbefbb226c5b675c3d6e60111646c2e98c`.
  Numbered native excerpts and identity retained at
  `Desktop/Codex/csc-river-access-audit-20261104/native-excerpts.json`.
- Prior captured marker values and native definition indices remain evidence
  from that archived world. No new live score, candidate-specific hidden-marker
  grant, prerequisite pointer observation, ETA attribution or decision was measured.
